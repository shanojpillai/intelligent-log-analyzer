from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_path = Column(String)
    status = Column(String, default="queued")
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    file_size = Column(Integer)
    error_message = Column(Text, nullable=True)

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

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    solution = Column(Text)
    category = Column(String)
    severity = Column(String)
    success_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SimilarCase(Base):
    __tablename__ = "similar_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    case_id = Column(String)
    similarity_score = Column(Float)
    matched_at = Column(DateTime, default=datetime.utcnow)
