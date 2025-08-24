"""
Knowledge base models for the Intelligent Log Analyzer backend.

This module contains models for the knowledge base and similar cases.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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
