import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import redis

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.job_queue = "log_analysis_jobs"
        
    async def initialize(self):
        """Initialize job manager"""
        logger.info("Initializing job manager")
        
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up job manager")
        
    def create_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new job"""
        job_id = job_data["job_id"]
        
        string_data = {k: str(v) for k, v in job_data.items()}
        for key, value in string_data.items():
            self.redis_client.hset(f"job:{job_id}", key, value)
        
        self.redis_client.lpush(self.job_queue, job_id)
        
        logger.info(f"Created job {job_id}")
        return job_id
        
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data"""
        job_data = self.redis_client.hgetall(f"job:{job_id}")
        
        if not job_data:
            return None
            
        return {k.decode(): v.decode() for k, v in job_data.items()}
        
    def update_job_status(self, job_id: str, status: str, progress: Optional[int] = None, error: Optional[str] = None):
        """Update job status"""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if progress is not None:
            updates["progress"] = str(progress)
            
        if error:
            updates["error"] = error
            
        for key, value in updates.items():
            self.redis_client.hset(f"job:{job_id}", key, value)
        logger.info(f"Updated job {job_id} status to {status}")
        
    def store_results(self, job_id: str, results: Dict[str, Any]):
        """Store job results"""
        self.redis_client.set(f"results:{job_id}", json.dumps(results))
        logger.info(f"Stored results for job {job_id}")
        
    def get_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job results"""
        results_data = self.redis_client.get(f"results:{job_id}")
        
        if not results_data:
            return None
            
        return json.loads(results_data.decode())
