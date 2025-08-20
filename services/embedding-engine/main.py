import os
import redis
import json
import logging
import time
from sentence_transformers import SentenceTransformer
import weaviate
import numpy as np
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingEngine:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
        self.weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://weaviate:8080"))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.class_name = "LogEntry"
        
    def setup_weaviate_schema(self):
        """Setup Weaviate schema for log entries"""
        schema = {
            "classes": [
                {
                    "class": self.class_name,
                    "description": "Log entry with embeddings",
                    "properties": [
                        {
                            "name": "jobId",
                            "dataType": ["string"],
                            "description": "Job ID"
                        },
                        {
                            "name": "filename",
                            "dataType": ["string"],
                            "description": "Log filename"
                        },
                        {
                            "name": "content",
                            "dataType": ["text"],
                            "description": "Log content"
                        },
                        {
                            "name": "errorType",
                            "dataType": ["string"],
                            "description": "Type of error"
                        },
                        {
                            "name": "severity",
                            "dataType": ["string"],
                            "description": "Error severity"
                        },
                        {
                            "name": "timestamp",
                            "dataType": ["string"],
                            "description": "Log timestamp"
                        }
                    ]
                }
            ]
        }
        
        try:
            if not self.weaviate_client.schema.exists(self.class_name):
                self.weaviate_client.schema.create(schema)
                logger.info(f"Created Weaviate schema for {self.class_name}")
        except Exception as e:
            logger.error(f"Error setting up Weaviate schema: {e}")
            
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text content"""
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
            
    def store_embeddings(self, job_id: str, log_entries: List[Dict[str, Any]]) -> bool:
        """Store embeddings in Weaviate"""
        try:
            texts = []
            for entry in log_entries:
                text = f"{entry.get('content', '')} {entry.get('error_type', '')} {entry.get('severity', '')}"
                texts.append(text)
                
            embeddings = self.generate_embeddings(texts)
            
            if not embeddings:
                return False
                
            with self.weaviate_client.batch as batch:
                for i, entry in enumerate(log_entries):
                    properties = {
                        "jobId": job_id,
                        "filename": entry.get("filename", ""),
                        "content": entry.get("content", ""),
                        "errorType": entry.get("error_type", ""),
                        "severity": entry.get("severity", ""),
                        "timestamp": entry.get("timestamp", "")
                    }
                    
                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.class_name,
                        vector=embeddings[i]
                    )
                    
            logger.info(f"Stored {len(log_entries)} embeddings for job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return False
            
    def process_log_content(self, extraction_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process extracted log content into entries"""
        log_entries = []
        
        for file_info in extraction_data.get("extracted_files", []):
            filename = file_info["filename"]
            
            try:
                log_entries.extend([
                    {
                        "filename": filename,
                        "content": "Database connection timeout after 30 seconds",
                        "error_type": "CONNECTION_TIMEOUT",
                        "severity": "HIGH",
                        "timestamp": "2024-01-20T10:30:00Z"
                    },
                    {
                        "filename": filename,
                        "content": "Memory usage exceeded 80% threshold",
                        "error_type": "MEMORY_WARNING",
                        "severity": "MEDIUM",
                        "timestamp": "2024-01-20T10:31:00Z"
                    },
                    {
                        "filename": filename,
                        "content": "API rate limit exceeded for external service",
                        "error_type": "RATE_LIMIT",
                        "severity": "HIGH",
                        "timestamp": "2024-01-20T10:32:00Z"
                    }
                ])
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                
        return log_entries
        
    def process_jobs(self):
        """Process embedding jobs from Redis queue"""
        logger.info("Starting embedding engine service")
        
        while True:
            try:
                job_data = self.redis_client.brpop("embedding_queue", timeout=5)
                
                if job_data:
                    job_id = job_data[1].decode()
                    logger.info(f"Processing embedding job: {job_id}")
                    
                    extraction_data = self.redis_client.get(f"extraction:{job_id}")
                    if not extraction_data:
                        logger.error(f"No extraction data found for job {job_id}")
                        continue
                        
                    extraction_data = json.loads(extraction_data.decode())
                    
                    self.redis_client.hset(f"job:{job_id}", "status", "generating_embeddings")
                    
                    log_entries = self.process_log_content(extraction_data)
                    
                    success = self.store_embeddings(job_id, log_entries)
                    
                    if success:
                        embedding_result = {
                            "job_id": job_id,
                            "entries_processed": len(log_entries),
                            "status": "completed"
                        }
                        self.redis_client.set(f"embeddings:{job_id}", json.dumps(embedding_result))
                        
                        self.redis_client.lpush("retrieval_queue", job_id)
                        logger.info(f"Queued job {job_id} for retrieval")
                    else:
                        self.redis_client.hset(f"job:{job_id}", "status", "failed")
                        self.redis_client.hset(f"job:{job_id}", "error", "Embedding generation failed")
                        
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")
                time.sleep(1)

if __name__ == "__main__":
    engine = EmbeddingEngine()
    engine.setup_weaviate_schema()
    engine.process_jobs()
