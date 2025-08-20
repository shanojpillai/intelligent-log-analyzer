from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:secure_password_123@postgres:5432/log_analyzer"
    
    REDIS_URL: str = "redis://:redis_password_123@redis:6379"
    
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET_NAME: str = "log-files"
    
    WEAVIATE_URL: str = "http://weaviate:8080"
    
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama2"
    
    MAX_FILE_SIZE_MB: int = 100
    MAX_CONCURRENT_JOBS: int = 5
    JOB_TIMEOUT_MINUTES: int = 30
    
    SECRET_KEY: str = "your_super_secret_key_here"
    JWT_SECRET: str = "your_jwt_secret_key_here"
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
