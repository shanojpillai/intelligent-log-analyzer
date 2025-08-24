# Intelligent Log Analyzer

An AI-powered log analysis system that helps support engineers quickly identify and resolve issues by leveraging historical knowledge and pattern matching.

## Architecture Overview

This system implements a comprehensive 14-component architecture for intelligent log analysis:

```
Upload → Extract → Search Past → Get Context → AI Analyze → Show Results → Export
```

<img width="1320" height="1622" alt="image" src="https://github.com/user-attachments/assets/b6c67e60-cb3b-419f-a5cc-30750f478c24" />


## System Components

### Core Processing Pipeline
1. **Support Engineer** - Person who uses the system
2. **Upload Portal** - Web interface for dropping ZIP files (Streamlit UI)
3. **Log Extractor** - ZIP file processing and log content extraction
4. **Embedding Engine** - Converts log text into searchable vector patterns
5. **Vector Database** - Stores mathematical patterns of past problems (Weaviate)
6. **Retrieval Engine** - Finds similar historical incidents using pattern matching
7. **Knowledge Base** - Library of proven solutions from past cases
8. **AI Analyzer** - Open source LLM for log analysis with historical context (Ollama/Llama)
9. **Redis Queue** - Job management and processing queue
10. **NLU Processor** - Extracts important entities and details from logs (spaCy)
11. **PostgreSQL** - Database for storing analysis results
12. **Results Dashboard** - Interface showing insights and solutions
13. **Support Engineer** - Reviews AI recommendations
14. **Export Service** - Creates PDF/Word reports for documentation

### Storage Components
- **Object Storage** - Secure storage for original ZIP files (MinIO)
- **RAG Knowledge Layer** - Smart memory system combining vector database, retrieval engine, and knowledge base

## Project Structure

```
intelligent-log-analyzer/
├── docker-compose.yml              # Multi-service orchestration
├── .env.example                    # Environment variables template
├── README.md                       # This file
├── docs/                          # Documentation
│   ├── architecture.md           # Detailed architecture
│   ├── api.md                    # API documentation
│   └── deployment.md             # Deployment guide
├── frontend/                      # Streamlit UI
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                    # Main Streamlit application
│   ├── pages/                    # Multi-page app structure
│   ├── components/               # Reusable UI components
│   └── utils/                    # Frontend utilities
├── backend/                       # FastAPI backend services
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                   # FastAPI main application
│   ├── api/                      # API endpoints
│   ├── services/                 # Business logic services
│   ├── models/                   # Data models
│   ├── database/                 # Database configurations
│   └── utils/                    # Backend utilities
├── services/                      # Microservices
│   ├── log-extractor/            # ZIP processing service
│   ├── embedding-engine/         # Vector embedding service
│   ├── retrieval-engine/         # Similarity search service
│   ├── ai-analyzer/              # Open source LLM integration
│   ├── nlu-processor/            # spaCy NLU service
│   └── export-service/           # Report generation service
├── data/                         # Data storage
│   ├── uploads/                  # Uploaded ZIP files
│   ├── extracted/                # Extracted log files
│   ├── embeddings/               # Vector embeddings cache
│   └── knowledge-base/           # Historical solutions
├── config/                       # Configuration files
│   ├── redis.conf               # Redis configuration
│   ├── postgres.conf            # PostgreSQL configuration
│   └── nginx.conf               # Reverse proxy configuration
└── scripts/                      # Utility scripts
    ├── setup.sh                 # Environment setup
    ├── seed-data.sh             # Sample data seeding
    └── backup.sh                # Data backup utilities
```

## Features

### 🚀 Core Capabilities
- **Drag & Drop Upload**: Simple ZIP file upload interface
- **Intelligent Extraction**: Automatic log file detection and parsing
- **Vector Search**: Semantic similarity matching against historical issues
- **AI Analysis**: Open source LLM powered log analysis
- **Entity Extraction**: spaCy for identifying key information
- **Solution Recommendations**: Historical knowledge-based suggestions
- **Export Reports**: PDF/Word documentation generation

### 🔧 Technical Features
- **Containerized Architecture**: Full Docker deployment
- **Microservices Design**: Scalable, maintainable components
- **Queue Management**: Redis-based job processing
- **Vector Database**: Efficient similarity search with Weaviate
- **RESTful APIs**: Clean service interfaces
- **Real-time Updates**: Live processing status
- **Responsive UI**: Modern Streamlit interface

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/shanojpillai/intelligent-log-analyzer.git
cd intelligent-log-analyzer
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configurations
```

3. **Start the system**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Environment Variables

```bash
# AI Services
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama2

# Vector Database
WEAVIATE_URL=http://weaviate:8080

# Database
POSTGRES_DB=log_analyzer
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_URL=redis://redis:6379

# Storage
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

## Usage

### 1. Upload Logs
- Navigate to the Upload Portal
- Drag and drop ZIP files containing log files
- System automatically queues processing jobs

### 2. Processing Pipeline
- **Extraction**: ZIP files are processed and logs extracted
- **Embedding**: Log content converted to vector representations
- **Retrieval**: Similar historical issues identified
- **Analysis**: AI analyzes logs with historical context
- **NLU**: Key entities and information extracted

### 3. Review Results
- View analysis results in the dashboard
- Review AI recommendations and similar cases
- Export findings to PDF/Word reports

## API Endpoints

### Upload & Processing
- `POST /api/upload` - Upload ZIP files
- `GET /api/jobs/{job_id}` - Check processing status
- `GET /api/jobs/{job_id}/results` - Get analysis results

### Analysis & Search
- `POST /api/analyze` - Trigger log analysis
- `GET /api/search/similar` - Find similar historical cases
- `GET /api/knowledge-base/solutions` - Get solution recommendations

### Export & Reports
- `POST /api/export/pdf` - Generate PDF report
- `POST /api/export/word` - Generate Word document
- `GET /api/export/{export_id}` - Download generated report

## Development

### Local Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend development
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling Services
```bash
# Scale processing services
docker-compose up -d --scale log-extractor=3 --scale embedding-engine=2
```

## Contributing

1. Fork the repository from [https://github.com/shanojpillai/intelligent-log-analyzer](https://github.com/shanojpillai/intelligent-log-analyzer)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request to the `main` branch

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue in the [GitHub repository](https://github.com/shanojpillai/intelligent-log-analyzer/issues)
- Check the documentation in the `docs/` directory
- For security issues, please email directly instead of creating a public issue

---

**Built with ❤️ for intelligent log analysis and faster issue resolution**
