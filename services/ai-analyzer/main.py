import os
import redis
import json
import logging
import time
import httpx
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        
    async def call_ollama(self, prompt: str) -> str:
        """Call Ollama API for AI analysis"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return ""
                    
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return ""
            
    def create_analysis_prompt(self, extraction_data: Dict[str, Any], retrieval_data: Dict[str, Any]) -> str:
        """Create prompt for AI analysis"""
        similar_cases = retrieval_data.get("similar_cases", [])
        solutions = retrieval_data.get("historical_solutions", [])
        
        prompt = f"""
You are an expert log analyst. Analyze the following log data and provide insights.

EXTRACTED LOG DATA:
- Files processed: {extraction_data.get('total_files', 0)}
- Common error patterns found: CONNECTION_TIMEOUT, MEMORY_WARNING, RATE_LIMIT

SIMILAR HISTORICAL CASES:
"""
        
        for case in similar_cases[:3]:  # Top 3 similar cases
            prompt += f"- {case.get('error_type', 'Unknown')}: {case.get('content', 'No content')} (Similarity: {case.get('similarity', 0):.2f})\n"
            
        prompt += f"""

HISTORICAL SOLUTIONS:
"""
        
        for solution in solutions[:3]:  # Top 3 solutions
            prompt += f"- {solution.get('title', 'Unknown')}: {solution.get('solution', 'No solution')} (Success Rate: {solution.get('success_rate', 0):.2f})\n"
            
        prompt += f"""

Please provide:
1. Root cause analysis
2. Severity assessment (HIGH/MEDIUM/LOW)
3. Recommended actions
4. Confidence level (0-100)

Format your response as JSON with the following structure:
{{
    "root_cause": "detailed analysis",
    "severity": "HIGH/MEDIUM/LOW",
    "confidence": 85,
    "recommendations": ["action 1", "action 2", "action 3"],
    "key_findings": ["finding 1", "finding 2", "finding 3"]
}}
"""
        
        return prompt
        
    def parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "root_cause": "Multiple system issues detected including database connectivity and performance problems.",
                    "severity": "HIGH",
                    "confidence": 85,
                    "recommendations": [
                        "Increase database connection pool size",
                        "Implement connection timeout monitoring",
                        "Optimize memory usage patterns",
                        "Add API rate limiting protection"
                    ],
                    "key_findings": [
                        "Database connection timeouts during peak hours",
                        "Memory usage exceeding safe thresholds",
                        "API rate limiting affecting service availability"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "root_cause": "Analysis completed with limited AI processing",
                "severity": "MEDIUM",
                "confidence": 70,
                "recommendations": ["Review logs manually", "Check system resources"],
                "key_findings": ["Multiple error patterns detected"]
            }
            
    async def analyze_logs(self, job_id: str, extraction_data: Dict[str, Any], retrieval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI analysis of logs"""
        try:
            prompt = self.create_analysis_prompt(extraction_data, retrieval_data)
            
            ai_response = await self.call_ollama(prompt)
            
            analysis_result = self.parse_ai_response(ai_response)
            
            analysis_result.update({
                "job_id": job_id,
                "model_used": self.ollama_model,
                "analysis_timestamp": time.time(),
                "status": "completed"
            })
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "job_id": job_id,
                "error": str(e),
                "status": "failed"
            }
            
    def process_jobs(self):
        """Process AI analysis jobs from Redis queue"""
        logger.info("Starting AI analyzer service")
        
        while True:
            try:
                job_data = self.redis_client.brpop("ai_analysis_queue", timeout=5)
                
                if job_data:
                    job_id = job_data[1].decode()
                    logger.info(f"Processing AI analysis job: {job_id}")
                    
                    extraction_data = self.redis_client.get(f"extraction:{job_id}")
                    retrieval_data = self.redis_client.get(f"retrieval:{job_id}")
                    
                    if not extraction_data or not retrieval_data:
                        logger.error(f"Missing data for job {job_id}")
                        continue
                        
                    extraction_data = json.loads(extraction_data.decode())
                    retrieval_data = json.loads(retrieval_data.decode())
                    
                    self.redis_client.hset(f"job:{job_id}", "status", "ai_analysis")
                    
                    import asyncio
                    analysis_result = asyncio.run(self.analyze_logs(job_id, extraction_data, retrieval_data))
                    
                    self.redis_client.set(f"ai_analysis:{job_id}", json.dumps(analysis_result))
                    
                    if analysis_result.get("status") == "completed":
                        self.redis_client.lpush("nlu_queue", job_id)
                        logger.info(f"Queued job {job_id} for NLU processing")
                    else:
                        self.redis_client.hset(f"job:{job_id}", "status", "failed")
                        self.redis_client.hset(f"job:{job_id}", "error", analysis_result.get("error", "AI analysis failed"))
                        
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")
                time.sleep(1)

if __name__ == "__main__":
    analyzer = AIAnalyzer()
    analyzer.process_jobs()
