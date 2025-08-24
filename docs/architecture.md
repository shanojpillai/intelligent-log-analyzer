# Architecture Documentation

## System Overview

The Intelligent Log Analyzer implements a comprehensive microservices architecture designed for scalable, AI-powered log analysis. The system processes uploaded ZIP files containing log data through a sophisticated pipeline that combines vector similarity search, historical knowledge retrieval, and large language model analysis.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Support       │    │   Upload        │    │   Log           │
│   Engineer      │───▶│   Portal        │───▶│   Extractor     │
│                 │    │   (Streamlit)   │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Results       │    │   AI Analyzer   │    │   Embedding     │
│   Dashboard     │◀───│   (Ollama)      │◀───│   Engine        │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Export        │    │   NLU           │    │   Vector        │
│   Service       │    │   Processor     │    │   Database      │
│   (PDF/Word)    │    │   (spaCy)       │    │   (Weaviate)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                              ┌─────────────────┐    ┌─────────────────┐
                              │   Retrieval     │    │   Knowledge     │
                              │   Engine        │───▶│   Base          │
                              │                 │    │   (PostgreSQL)  │
                              └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Frontend Layer
- **Upload Portal**: Streamlit-based web interface for file uploads
- **Results Dashboard**: Interactive visualization of analysis results
- **Export Interface**: PDF/Word report generation controls

### 2. Backend Services
- **FastAPI Backend**: Main orchestration service with REST API
- **Job Manager**: Asynchronous job processing and status tracking
- **Log Processor**: Core business logic for log analysis workflow

### 3. Microservices Layer
- **Log Extractor**: ZIP file processing and log content extraction
- **Embedding Engine**: Vector representation generation using transformers
- **Retrieval Engine**: Similarity search against historical cases
- **AI Analyzer**: LLM-powered analysis using Ollama
- **NLU Processor**: Named entity recognition and information extraction
- **Export Service**: Report generation in multiple formats

### 4. Data Layer
- **PostgreSQL**: Structured data storage for jobs, results, and knowledge base
- **Redis**: Message queuing and caching
- **Weaviate**: Vector database for similarity search
- **MinIO**: Object storage for uploaded files and exports

## Data Flow

### 1. Upload Phase
1. User uploads ZIP file through Streamlit interface
2. File stored in MinIO object storage
3. Job created in PostgreSQL with unique ID
4. Job queued in Redis for processing

### 2. Processing Pipeline
1. **Extraction**: Log Extractor service processes ZIP file
2. **Embedding**: Embedding Engine generates vector representations
3. **Retrieval**: Retrieval Engine finds similar historical cases
4. **Analysis**: AI Analyzer performs LLM-based analysis
5. **NLU**: NLU Processor extracts entities and key information
6. **Storage**: Results stored in PostgreSQL and Redis

### 3. Results Phase
1. User views results in dashboard
2. Similar cases and recommendations displayed
3. Export service generates reports on demand

## Technology Stack

### Core Technologies
- **Python 3.9+**: Primary development language
- **FastAPI**: High-performance web framework
- **Streamlit**: Interactive web interface
- **Docker**: Containerization and deployment

### AI/ML Stack
- **Ollama**: Open-source LLM inference
- **Weaviate**: Vector database
- **spaCy**: Natural language processing
- **Transformers**: Embedding generation

### Infrastructure
- **PostgreSQL**: Primary database
- **Redis**: Message queue and cache
- **MinIO**: Object storage
- **Nginx**: Reverse proxy and load balancing

## Security Considerations

### Authentication & Authorization
- JWT-based authentication for API access
- Role-based access control for different user types
- Secure token management and rotation

### Data Protection
- Encryption at rest for sensitive log data
- TLS encryption for all network communication
- Secure file upload validation and sanitization

### Infrastructure Security
- Container isolation and security scanning
- Network segmentation between services
- Regular security updates and vulnerability management

## Scalability Design

### Horizontal Scaling
- Stateless microservices for easy scaling
- Load balancing across service instances
- Database connection pooling and optimization

### Performance Optimization
- Redis caching for frequently accessed data
- Asynchronous processing for long-running tasks
- Vector database optimization for similarity search

### Monitoring & Observability
- Comprehensive logging across all services
- Health checks and service monitoring
- Performance metrics and alerting

## Deployment Architecture

### Development Environment
- Docker Compose for local development
- Hot reloading for rapid iteration
- Integrated testing and debugging tools

### Production Environment
- Kubernetes orchestration for production
- Auto-scaling based on load metrics
- High availability and disaster recovery

## Future Enhancements

### Planned Features
- Multi-tenant support for enterprise deployment
- Advanced analytics and reporting dashboard
- Integration with popular monitoring tools
- Machine learning model fine-tuning capabilities

### Scalability Improvements
- Distributed processing for large log files
- Advanced caching strategies
- Real-time streaming log analysis
