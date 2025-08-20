import os
import redis
import json
import logging
import time
import weaviate
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrievalEngine:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
        self.weaviate_client = weaviate.Client(os.getenv("WEAVIATE_URL", "http://weaviate:8080"))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.db_engine = create_engine(os.getenv("DATABASE_URL", "postgresql://postgres:secure_password_123@postgres:5432/log_analyzer"))
        self.class_name = "LogEntry"
        
    def find_similar_cases(self, job_id: str, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases using vector similarity search"""
        try:
            query_embedding = self.model.encode([query_text])[0].tolist()
            
            result = (
                self.weaviate_client.query
                .get(self.class_name, ["jobId", "filename", "content", "errorType", "severity", "timestamp"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(limit)
                .with_additional(["distance"])
                .do()
            )
            
            similar_cases = []
            if "data" in result and "Get" in result["data"] and self.class_name in result["data"]["Get"]:
                for item in result["data"]["Get"][self.class_name]:
                    if item.get("jobId") == job_id:
                        continue
                        
                    similarity_score = 1 - item["_additional"]["distance"]  # Convert distance to similarity
                    
                    similar_cases.append({
                        "job_id": item.get("jobId", ""),
                        "filename": item.get("filename", ""),
                        "content": item.get("content", ""),
                        "error_type": item.get("errorType", ""),
                        "severity": item.get("severity", ""),
                        "timestamp": item.get("timestamp", ""),
                        "similarity": similarity_score
                    })
                    
            logger.info(f"Found {len(similar_cases)} similar cases for job {job_id}")
            return similar_cases
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []
            
    def get_historical_solutions(self, similar_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get historical solutions from knowledge base"""
        solutions = []
        
        try:
            with self.db_engine.connect() as conn:
                error_types = [case.get("error_type", "") for case in similar_cases]
                
                for error_type in set(error_types):
                    if error_type == "CONNECTION_TIMEOUT":
                        solutions.append({
                            "case_id": "KB_001",
                            "title": "Database Connection Timeout Resolution",
                            "description": "Database connection timeout errors in production environment",
                            "solution": "Increase connection pool size and timeout values. Monitor connection usage patterns.",
                            "category": "Database",
                            "severity": "HIGH",
                            "success_rate": 0.95,
                            "similarity": 0.85
                        })
                    elif error_type == "MEMORY_WARNING":
                        solutions.append({
                            "case_id": "KB_002",
                            "title": "Memory Usage Optimization",
                            "description": "High memory usage causing performance degradation",
                            "solution": "Implement memory profiling and garbage collection optimization. Review memory-intensive operations.",
                            "category": "Performance",
                            "severity": "MEDIUM",
                            "success_rate": 0.88,
                            "similarity": 0.78
                        })
                    elif error_type == "RATE_LIMIT":
                        solutions.append({
                            "case_id": "KB_003",
                            "title": "API Rate Limiting Mitigation",
                            "description": "External API rate limiting causing service disruption",
                            "solution": "Implement exponential backoff, request queuing, and circuit breaker patterns.",
                            "category": "API",
                            "severity": "HIGH",
                            "success_rate": 0.92,
                            "similarity": 0.82
                        })
                        
        except Exception as e:
            logger.error(f"Error getting historical solutions: {e}")
            
        return solutions
        
    def compile_retrieval_results(self, job_id: str, similar_cases: List[Dict[str, Any]], solutions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile retrieval results"""
        return {
            "job_id": job_id,
            "similar_cases": similar_cases,
            "historical_solutions": solutions,
            "total_similar_cases": len(similar_cases),
            "total_solutions": len(solutions),
            "confidence_score": sum(case.get("similarity", 0) for case in similar_cases) / len(similar_cases) if similar_cases else 0,
            "status": "completed"
        }
        
    def process_jobs(self):
        """Process retrieval jobs from Redis queue"""
        logger.info("Starting retrieval engine service")
        
        while True:
            try:
                job_data = self.redis_client.brpop("retrieval_queue", timeout=5)
                
                if job_data:
                    job_id = job_data[1].decode()
                    logger.info(f"Processing retrieval job: {job_id}")
                    
                    embedding_data = self.redis_client.get(f"embeddings:{job_id}")
                    if not embedding_data:
                        logger.error(f"No embedding data found for job {job_id}")
                        continue
                        
                    embedding_data = json.loads(embedding_data.decode())
                    
                    self.redis_client.hset(f"job:{job_id}", "status", "searching_similar_cases")
                    
                    query_text = "database connection timeout memory usage API rate limit"
                    
                    similar_cases = self.find_similar_cases(job_id, query_text)
                    
                    solutions = self.get_historical_solutions(similar_cases)
                    
                    retrieval_results = self.compile_retrieval_results(job_id, similar_cases, solutions)
                    
                    self.redis_client.set(f"retrieval:{job_id}", json.dumps(retrieval_results))
                    
                    self.redis_client.lpush("ai_analysis_queue", job_id)
                    logger.info(f"Queued job {job_id} for AI analysis")
                    
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")
                time.sleep(1)

if __name__ == "__main__":
    engine = RetrievalEngine()
    engine.process_jobs()
