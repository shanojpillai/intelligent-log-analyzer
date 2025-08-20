import os
import redis
import json
import zipfile
import logging
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import tempfile
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogExtractor:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
        self.minio_client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"),
            access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin123"),
            secure=False
        )
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "log-files")
        self.supported_extensions = ['.log', '.txt', '.out', '.err', '.trace']
        
    def ensure_bucket_exists(self):
        """Ensure MinIO bucket exists"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error creating bucket: {e}")
            
    def extract_zip_file(self, job_id: str, zip_path: str) -> dict:
        """Extract ZIP file and identify log files"""
        extracted_files = []
        extract_dir = Path(f"/tmp/extracted/{job_id}")
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if not file_info.is_dir():
                        file_path = Path(file_info.filename)
                        
                        if any(file_path.name.lower().endswith(ext) for ext in self.supported_extensions):
                            extracted_path = extract_dir / file_path.name
                            with zip_ref.open(file_info) as source, open(extracted_path, 'wb') as target:
                                target.write(source.read())
                            
                            object_name = f"{job_id}/{file_path.name}"
                            self.minio_client.fput_object(
                                self.bucket_name,
                                object_name,
                                str(extracted_path)
                            )
                            
                            extracted_files.append({
                                "filename": file_path.name,
                                "path": str(extracted_path),
                                "object_name": object_name,
                                "size": extracted_path.stat().st_size
                            })
                            
                            logger.info(f"Extracted and uploaded: {file_path.name}")
                        
            return {
                "job_id": job_id,
                "extracted_files": extracted_files,
                "total_files": len(extracted_files),
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error extracting ZIP file {zip_path}: {e}")
            return {
                "job_id": job_id,
                "error": str(e),
                "status": "failed"
            }
            
    def process_jobs(self):
        """Process extraction jobs from Redis queue"""
        logger.info("Starting log extractor service")
        
        while True:
            try:
                job_data = self.redis_client.brpop("extraction_queue", timeout=5)
                
                if job_data:
                    job_id = job_data[1].decode()
                    logger.info(f"Processing extraction job: {job_id}")
                    
                    job_info = self.redis_client.hgetall(f"job:{job_id}")
                    if not job_info:
                        logger.error(f"Job {job_id} not found")
                        continue
                        
                    zip_path = job_info[b'file_path'].decode()
                    
                    self.redis_client.hset(f"job:{job_id}", "status", "extracting")
                    
                    result = self.extract_zip_file(job_id, zip_path)
                    
                    self.redis_client.set(f"extraction:{job_id}", json.dumps(result))
                    
                    if result["status"] == "completed":
                        self.redis_client.lpush("embedding_queue", job_id)
                        logger.info(f"Queued job {job_id} for embedding generation")
                    else:
                        self.redis_client.hset(f"job:{job_id}", "status", "failed")
                        self.redis_client.hset(f"job:{job_id}", "error", result.get("error", "Unknown error"))
                        
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")
                time.sleep(1)

if __name__ == "__main__":
    extractor = LogExtractor()
    extractor.ensure_bucket_exists()
    extractor.process_jobs()
