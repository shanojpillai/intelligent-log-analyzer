import asyncio
import zipfile
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class LogProcessor:
    def __init__(self):
        self.supported_extensions = ['.log', '.txt', '.out', '.err']
        
    async def extract_zip(self, zip_path: str, job_id: str) -> List[str]:
        """Extract ZIP file and return list of log files"""
        extracted_files = []
        extract_dir = Path(f"data/extracted/{job_id}")
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
                            
                            extracted_files.append(str(extracted_path))
                            logger.info(f"Extracted log file: {file_path.name}")
                        
            logger.info(f"Extracted {len(extracted_files)} log files from {zip_path}")
            return extracted_files
            
        except Exception as e:
            logger.error(f"Error extracting ZIP file {zip_path}: {e}")
            raise
            
    async def process_logs(self, log_files: List[str]) -> Dict[str, Any]:
        """Process extracted log files"""
        log_content = {
            "files": [],
            "total_lines": 0,
            "error_patterns": [],
            "warning_patterns": [],
            "timestamps": []
        }
        
        error_patterns = [
            r'ERROR',
            r'FATAL',
            r'Exception',
            r'failed',
            r'timeout',
            r'connection.*refused',
            r'out of memory',
            r'stack trace'
        ]
        
        warning_patterns = [
            r'WARN',
            r'WARNING',
            r'deprecated',
            r'retry',
            r'slow'
        ]
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                file_info = {
                    "filename": Path(log_file).name,
                    "path": log_file,
                    "line_count": len(lines),
                    "errors": [],
                    "warnings": [],
                    "sample_content": lines[:10] if lines else []
                }
                
                for i, line in enumerate(lines):
                    for pattern in error_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            file_info["errors"].append({
                                "line_number": i + 1,
                                "content": line.strip(),
                                "pattern": pattern
                            })
                            
                    for pattern in warning_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            file_info["warnings"].append({
                                "line_number": i + 1,
                                "content": line.strip(),
                                "pattern": pattern
                            })
                            
                    timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}[\s\T]\d{2}:\d{2}:\d{2}', line)
                    if timestamp_match:
                        log_content["timestamps"].append(timestamp_match.group())
                
                log_content["files"].append(file_info)
                log_content["total_lines"] += len(lines)
                
                logger.info(f"Processed log file: {file_info['filename']} ({len(lines)} lines)")
                
            except Exception as e:
                logger.error(f"Error processing log file {log_file}: {e}")
                
        return log_content
        
    async def generate_embeddings(self, log_content: Dict[str, Any]) -> List[float]:
        """Generate embeddings for log content (mock implementation)"""
        
        text_content = ""
        for file_info in log_content["files"]:
            for error in file_info["errors"]:
                text_content += error["content"] + " "
            for warning in file_info["warnings"]:
                text_content += warning["content"] + " "
                
        embedding = [0.1] * 384  # Typical sentence-transformer dimension
        
        logger.info("Generated embeddings for log content")
        return embedding
        
    async def find_similar_cases(self, embeddings: List[float]) -> List[Dict[str, Any]]:
        """Find similar historical cases (mock implementation)"""
        
        similar_cases = [
            {
                "case_id": "case_001",
                "similarity": 0.85,
                "description": "Database connection timeout in production environment",
                "solution": "Increase connection pool size and timeout values",
                "date": "2024-01-15",
                "category": "Database"
            },
            {
                "case_id": "case_002", 
                "similarity": 0.78,
                "description": "Memory leak causing application crashes",
                "solution": "Implement proper resource cleanup and garbage collection",
                "date": "2024-01-10",
                "category": "Memory"
            },
            {
                "case_id": "case_003",
                "similarity": 0.72,
                "description": "API rate limiting errors from external service",
                "solution": "Implement exponential backoff and request queuing",
                "date": "2024-01-08",
                "category": "API"
            }
        ]
        
        logger.info(f"Found {len(similar_cases)} similar cases")
        return similar_cases
        
    async def analyze_with_ai(self, log_content: Dict[str, Any], similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logs with AI (mock implementation)"""
        
        total_errors = sum(len(file_info["errors"]) for file_info in log_content["files"])
        total_warnings = sum(len(file_info["warnings"]) for file_info in log_content["files"])
        
        analysis = {
            "root_cause": "Multiple database connection timeouts detected in application logs. This appears to be related to increased load during peak hours.",
            "confidence": 85.5,
            "issues": [
                {
                    "type": "Database Connection",
                    "severity": "High",
                    "count": total_errors,
                    "description": "Connection timeout errors detected"
                },
                {
                    "type": "Performance",
                    "severity": "Medium", 
                    "count": total_warnings,
                    "description": "Slow query warnings found"
                }
            ],
            "key_findings": [
                "Database connection pool exhaustion during peak hours",
                "Slow queries causing connection backlog",
                "Similar pattern observed in historical case #001"
            ],
            "recommendations": [
                "Increase database connection pool size from 10 to 25",
                "Implement connection timeout of 30 seconds",
                "Add database connection monitoring and alerting",
                "Optimize slow queries identified in logs"
            ],
            "severity_distribution": {
                "High": total_errors,
                "Medium": total_warnings,
                "Low": 0
            },
            "entities": [
                {
                    "text": "database",
                    "label": "SYSTEM",
                    "confidence": 0.95
                },
                {
                    "text": "connection timeout",
                    "label": "ERROR_TYPE",
                    "confidence": 0.92
                },
                {
                    "text": "production",
                    "label": "ENVIRONMENT",
                    "confidence": 0.88
                }
            ]
        }
        
        logger.info("Completed AI analysis of log content")
        return analysis
