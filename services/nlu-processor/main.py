import os
import redis
import json
import logging
import time
import spacy
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLUProcessor:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
        self.nlp = spacy.load("en_core_web_sm")
        
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using spaCy"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 0.9  # spaCy doesn't provide confidence scores by default
            })
            
        return entities
        
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        doc = self.nlp(text)
        keywords = []
        
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
                
        return list(set(keywords))
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis"""
        doc = self.nlp(text)
        
        negative_words = ['error', 'failed', 'timeout', 'exception', 'critical', 'fatal', 'crash']
        positive_words = ['success', 'completed', 'ok', 'normal', 'healthy']
        
        text_lower = text.lower()
        negative_count = sum(1 for word in negative_words if word in text_lower)
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
            score = -0.5
        elif positive_count > negative_count:
            sentiment = "positive"
            score = 0.5
        else:
            sentiment = "neutral"
            score = 0.0
            
        return {
            "sentiment": sentiment,
            "score": score,
            "negative_indicators": negative_count,
            "positive_indicators": positive_count
        }
        
    def process_log_content(self, ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI analysis content with NLU"""
        try:
            text_content = ""
            text_content += ai_analysis.get("root_cause", "") + " "
            text_content += " ".join(ai_analysis.get("recommendations", [])) + " "
            text_content += " ".join(ai_analysis.get("key_findings", []))
            
            entities = self.extract_entities(text_content)
            
            keywords = self.extract_keywords(text_content)
            
            sentiment = self.analyze_sentiment(text_content)
            
            log_patterns = self.identify_log_patterns(text_content)
            
            nlu_results = {
                "entities": entities,
                "keywords": keywords[:20],  # Top 20 keywords
                "sentiment": sentiment,
                "log_patterns": log_patterns,
                "processed_text_length": len(text_content),
                "entity_count": len(entities),
                "keyword_count": len(keywords)
            }
            
            return nlu_results
            
        except Exception as e:
            logger.error(f"Error in NLU processing: {e}")
            return {
                "entities": [],
                "keywords": [],
                "sentiment": {"sentiment": "neutral", "score": 0.0},
                "log_patterns": [],
                "error": str(e)
            }
            
    def identify_log_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Identify common log patterns"""
        patterns = []
        
        if any(word in text.lower() for word in ['database', 'connection', 'timeout', 'pool']):
            patterns.append({
                "type": "DATABASE_ISSUE",
                "confidence": 0.8,
                "description": "Database connectivity or performance issue detected"
            })
            
        if any(word in text.lower() for word in ['memory', 'heap', 'oom', 'garbage']):
            patterns.append({
                "type": "MEMORY_ISSUE",
                "confidence": 0.7,
                "description": "Memory-related issue detected"
            })
            
        if any(word in text.lower() for word in ['api', 'rate', 'limit', 'throttle']):
            patterns.append({
                "type": "API_ISSUE",
                "confidence": 0.75,
                "description": "API-related issue detected"
            })
            
        if any(word in text.lower() for word in ['slow', 'performance', 'latency', 'response']):
            patterns.append({
                "type": "PERFORMANCE_ISSUE",
                "confidence": 0.6,
                "description": "Performance degradation detected"
            })
            
        return patterns
        
    def process_jobs(self):
        """Process NLU jobs from Redis queue"""
        logger.info("Starting NLU processor service")
        
        while True:
            try:
                job_data = self.redis_client.brpop("nlu_queue", timeout=5)
                
                if job_data:
                    job_id = job_data[1].decode()
                    logger.info(f"Processing NLU job: {job_id}")
                    
                    ai_analysis_data = self.redis_client.get(f"ai_analysis:{job_id}")
                    if not ai_analysis_data:
                        logger.error(f"No AI analysis data found for job {job_id}")
                        continue
                        
                    ai_analysis = json.loads(ai_analysis_data.decode())
                    
                    self.redis_client.hset(f"job:{job_id}", "status", "nlu_processing")
                    
                    nlu_results = self.process_log_content(ai_analysis)
                    
                    self.redis_client.set(f"nlu:{job_id}", json.dumps(nlu_results))
                    
                    self.redis_client.lpush("compilation_queue", job_id)
                    logger.info(f"Queued job {job_id} for final compilation")
                    
            except Exception as e:
                logger.error(f"Error processing jobs: {e}")
                time.sleep(1)

if __name__ == "__main__":
    processor = NLUProcessor()
    processor.process_jobs()
