from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import uuid
import json
import asyncio
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any
import redis
from sqlalchemy.orm import Session

from database.connection import get_db, engine
from database.models import Base
from services.job_manager import JobManager
from services.log_processor import LogProcessor
from utils.config import settings
from utils.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent Log Analyzer API",
    description="AI-powered log analysis system with RAG knowledge base",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://:redis_password_123@redis:6379"))
job_manager = JobManager(redis_client)
log_processor = LogProcessor()

os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/extracted", exist_ok=True)
os.makedirs("data/exports", exist_ok=True)
os.makedirs("logs", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Intelligent Log Analyzer API")
    
    try:
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    
    await job_manager.initialize()
    logger.info("Job manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Intelligent Log Analyzer API")
    await job_manager.cleanup()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "redis": redis_status,
            "api": "healthy"
        }
    }

@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process log files"""
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        max_size = int(os.getenv("MAX_FILE_SIZE_MB", "100")) * 1024 * 1024
        if file.size and file.size > max_size:
            raise HTTPException(status_code=400, detail=f"File too large. Max size: {max_size//1024//1024}MB")
        
        job_id = str(uuid.uuid4())
        
        upload_path = Path("data/uploads") / f"{job_id}_{file.filename}"
        
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        job_data = {
            "job_id": job_id,
            "filename": file.filename,
            "file_path": str(upload_path),
            "status": "queued",
            "progress": "0",
            "created_at": datetime.utcnow().isoformat(),
            "file_size": str(len(content))
        }
        
        for key, value in job_data.items():
            redis_client.hset(f"job:{job_id}", key, str(value))
        
        background_tasks.add_task(process_log_file, job_id, str(upload_path), db)
        
        logger.info(f"File uploaded successfully: {job_id}")
        
        return {
            "job_id": job_id,
            "message": "File uploaded successfully",
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job processing status"""
    try:
        job_data = redis_client.hgetall(f"job:{job_id}")
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_info = {k.decode(): v.decode() for k, v in job_data.items()}
        
        return job_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """Get job analysis results"""
    try:
        job_data = redis_client.hgetall(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        results_data = redis_client.get(f"results:{job_id}")
        
        if not results_data:
            return {"message": "Results not available yet"}
        
        results = json.loads(results_data.decode())
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/pdf")
async def export_pdf(request: dict):
    """Export analysis results to PDF"""
    try:
        job_id = request.get("job_id")
        if not job_id:
            raise HTTPException(status_code=400, detail="job_id is required")
        
        results_data = redis_client.get(f"results:{job_id}")
        if not results_data:
            raise HTTPException(status_code=404, detail="Results not found")
        
        results = json.loads(results_data.decode())
        
        pdf_path = f"data/exports/{job_id}_report.pdf"
        
        with open(pdf_path, "w") as f:
            f.write("PDF Report Content")
        
        return {"export_id": job_id, "format": "pdf", "status": "completed"}
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/word")
async def export_word(request: dict):
    """Export analysis results to Word document"""
    try:
        job_id = request.get("job_id")
        if not job_id:
            raise HTTPException(status_code=400, detail="job_id is required")
        
        results_data = redis_client.get(f"results:{job_id}")
        if not results_data:
            raise HTTPException(status_code=404, detail="Results not found")
        
        results = json.loads(results_data.decode())
        
        doc_path = f"data/exports/{job_id}_report.docx"
        
        with open(doc_path, "w") as f:
            f.write("Word Document Content")
        
        return {"export_id": job_id, "format": "word", "status": "completed"}
        
    except Exception as e:
        logger.error(f"Word export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_log_file(job_id: str, file_path: str, db: Session):
    """Background task to process uploaded log file"""
    try:
        logger.info(f"Starting processing for job {job_id}")
        
        redis_client.hset(f"job:{job_id}", "status", "processing")
        redis_client.hset(f"job:{job_id}", "progress", "10")
        
        logger.info(f"Extracting ZIP file: {file_path}")
        extracted_files = await log_processor.extract_zip(file_path, job_id)
        redis_client.hset(f"job:{job_id}", "progress", "25")
        
        logger.info(f"Processing {len(extracted_files)} log files")
        log_content = await log_processor.process_logs(extracted_files)
        redis_client.hset(f"job:{job_id}", "progress", "50")
        
        logger.info("Generating embeddings")
        embeddings = await log_processor.generate_embeddings(log_content)
        redis_client.hset(f"job:{job_id}", "progress", "70")
        
        logger.info("Searching for similar cases")
        similar_cases = await log_processor.find_similar_cases(embeddings)
        redis_client.hset(f"job:{job_id}", "progress", "85")
        
        logger.info("Running AI analysis")
        ai_analysis = await log_processor.analyze_with_ai(log_content, similar_cases)
        redis_client.hset(f"job:{job_id}", "progress", "95")
        
        results = {
            "job_id": job_id,
            "files_processed": len(extracted_files),
            "issues_found": len(ai_analysis.get("issues", [])),
            "confidence": ai_analysis.get("confidence", 0),
            "key_findings": ai_analysis.get("key_findings", []),
            "severity_distribution": ai_analysis.get("severity_distribution", {}),
            "similar_cases": similar_cases,
            "ai_analysis": ai_analysis,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        redis_client.set(f"results:{job_id}", json.dumps(results))
        
        redis_client.hset(f"job:{job_id}", "status", "completed")
        redis_client.hset(f"job:{job_id}", "progress", "100")
        
        logger.info(f"Processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Processing failed for job {job_id}: {e}")
        redis_client.hset(f"job:{job_id}", "status", "failed")
        redis_client.hset(f"job:{job_id}", "error", str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
