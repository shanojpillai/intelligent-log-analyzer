# API Documentation

## Overview

The Intelligent Log Analyzer provides a comprehensive REST API built with FastAPI. The API enables programmatic access to all system functionality including file uploads, job management, analysis results, and report generation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com/api`

## Authentication

The API uses JWT-based authentication for secure access.

### Authentication Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## API Endpoints

### Health Check

#### GET /health
Check the health status of the API and connected services.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-24T15:30:00Z",
  "services": {
    "redis": "healthy",
    "postgres": "healthy",
    "weaviate": "healthy",
    "ollama": "healthy"
  }
}
```

### File Upload & Job Management

#### POST /api/upload
Upload a ZIP file containing log data for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: ZIP file (max 100MB)

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully",
  "status": "queued",
  "filename": "application_logs.zip",
  "file_size": "15728640"
}
```

**Error Responses:**
- `400`: Invalid file format or size
- `413`: File too large
- `500`: Server error

#### GET /api/jobs/{job_id}
Get the current status of a processing job.

**Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": "75",
  "filename": "application_logs.zip",
  "created_at": "2024-08-24T15:30:00Z",
  "updated_at": "2024-08-24T15:35:00Z",
  "current_stage": "ai_analysis"
}
```

**Status Values:**
- `queued`: Job is waiting to be processed
- `extracting`: ZIP file extraction in progress
- `embedding`: Vector embedding generation
- `retrieving`: Searching for similar cases
- `ai_analysis`: AI analysis in progress
- `nlu_processing`: NLU entity extraction
- `completed`: Analysis finished successfully
- `failed`: Processing failed

#### GET /api/jobs
List all jobs for the authenticated user.

**Query Parameters:**
- `status` (optional): Filter by job status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "filename": "app_logs.zip",
      "created_at": "2024-08-24T15:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Analysis Results

#### GET /api/jobs/{job_id}/results
Retrieve analysis results for a completed job.

**Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_processed": 15,
  "issues_found": 8,
  "confidence": 92,
  "key_findings": [
    "Database connection timeouts during peak hours",
    "Memory usage exceeding safe thresholds",
    "API rate limiting affecting service availability"
  ],
  "severity_distribution": {
    "HIGH": 3,
    "MEDIUM": 4,
    "LOW": 1
  },
  "similar_cases": [
    {
      "case_id": "case_001",
      "similarity": 0.89,
      "description": "Database timeout issues",
      "solution": "Increase connection pool size"
    }
  ],
  "ai_analysis": {
    "root_cause": "Multiple system issues detected...",
    "severity": "HIGH",
    "recommendations": [
      "Increase database connection pool size",
      "Implement connection timeout monitoring"
    ]
  },
  "processed_at": "2024-08-24T15:40:00Z"
}
```

#### POST /api/analyze
Trigger manual analysis of previously uploaded logs.

**Request Body:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "analysis_type": "full",
  "include_historical": true
}
```

**Response:**
```json
{
  "message": "Analysis triggered successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

### Knowledge Base & Search

#### GET /api/search/similar
Search for similar historical cases based on log patterns.

**Query Parameters:**
- `query` (string): Search query or log pattern
- `limit` (optional): Number of results (default: 10)
- `threshold` (optional): Similarity threshold (default: 0.7)

**Response:**
```json
{
  "similar_cases": [
    {
      "case_id": "case_001",
      "similarity": 0.89,
      "error_type": "DATABASE_TIMEOUT",
      "description": "Connection timeout during peak load",
      "solution": "Increase connection pool size to 50",
      "success_rate": 0.95
    }
  ],
  "total_found": 5,
  "search_time_ms": 45
}
```

#### GET /api/knowledge-base/solutions
Get proven solutions from the knowledge base.

**Query Parameters:**
- `category` (optional): Solution category
- `success_rate_min` (optional): Minimum success rate (default: 0.8)

**Response:**
```json
{
  "solutions": [
    {
      "solution_id": "sol_001",
      "title": "Database Connection Pool Optimization",
      "description": "Increase connection pool size for high-load scenarios",
      "category": "DATABASE",
      "success_rate": 0.95,
      "implementation_steps": [
        "Update database configuration",
        "Restart application services",
        "Monitor connection metrics"
      ]
    }
  ]
}
```

### Export & Reports

#### POST /api/export/pdf
Generate a PDF report of analysis results.

**Request Body:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "include_sections": ["summary", "findings", "recommendations"],
  "template": "standard"
}
```

**Response:**
```json
{
  "export_id": "exp_001",
  "format": "pdf",
  "status": "generating",
  "estimated_completion": "2024-08-24T15:45:00Z"
}
```

#### POST /api/export/word
Generate a Word document report of analysis results.

**Request Body:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "include_sections": ["summary", "findings", "recommendations"],
  "template": "detailed"
}
```

**Response:**
```json
{
  "export_id": "exp_002",
  "format": "word",
  "status": "generating",
  "estimated_completion": "2024-08-24T15:45:00Z"
}
```

#### GET /api/export/{export_id}
Check export status and download completed reports.

**Parameters:**
- `export_id` (string): Export job identifier

**Response (In Progress):**
```json
{
  "export_id": "exp_001",
  "status": "generating",
  "progress": 75,
  "estimated_completion": "2024-08-24T15:45:00Z"
}
```

**Response (Completed):**
```json
{
  "export_id": "exp_001",
  "status": "completed",
  "download_url": "/api/export/exp_001/download",
  "file_size": "2048576",
  "expires_at": "2024-08-25T15:45:00Z"
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format. Only ZIP files are supported.",
    "details": {
      "field": "file",
      "received_type": "text/plain"
    }
  },
  "timestamp": "2024-08-24T15:30:00Z",
  "request_id": "req_12345"
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Upload endpoints**: 10 requests per minute
- **Analysis endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1692889800
```

## WebSocket Events

For real-time job status updates:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/{job_id}');
```

### Events
```json
{
  "event": "status_update",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ai_analysis",
  "progress": 75,
  "timestamp": "2024-08-24T15:35:00Z"
}
```

## SDK Examples

### Python
```python
import requests

# Upload file
with open('logs.zip', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': f},
        headers={'Authorization': 'Bearer <token>'}
    )
    job_id = response.json()['job_id']

# Check status
status = requests.get(
    f'http://localhost:8000/api/jobs/{job_id}',
    headers={'Authorization': 'Bearer <token>'}
).json()

# Get results
results = requests.get(
    f'http://localhost:8000/api/jobs/{job_id}/results',
    headers={'Authorization': 'Bearer <token>'}
).json()
```

### JavaScript
```javascript
// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/api/upload', {
  method: 'POST',
  body: formData,
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { job_id } = await uploadResponse.json();

// Poll for results
const pollResults = async () => {
  const response = await fetch(`/api/jobs/${job_id}/results`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

## OpenAPI Specification

The complete OpenAPI specification is available at:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **JSON Schema**: `http://localhost:8000/openapi.json`
