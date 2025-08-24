"""
Analysis result model for the Intelligent Log Analyzer backend.

This module contains the AnalysisResult model for storing analysis results.
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    files_processed = Column(Integer)
    issues_found = Column(Integer)
    confidence = Column(Float)
    key_findings = Column(JSON)
    severity_distribution = Column(JSON)
    ai_analysis = Column(JSON)
    processed_at = Column(DateTime, default=datetime.utcnow)
