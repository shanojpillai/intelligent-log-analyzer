# System Diagram - Intelligent Log Analyzer

## High-Level Architecture Diagram

```mermaid
graph TB
    %% User Interface Layer
    subgraph "Frontend Layer"
        UI[Streamlit Web Interface]
        UP[Upload Page]
        DB[Dashboard]
        KB[Knowledge Base]
        ST[Settings]
    end

    %% API Gateway
    subgraph "API Layer"
        API[FastAPI Backend]
        AUTH[Authentication]
        ROUTER[API Router]
    end

    %% Microservices Layer
    subgraph "Processing Services"
        LE[Log Extractor Service]
        EE[Embedding Engine]
        RE[Retrieval Engine]
        AI[AI Analyzer - Ollama]
        NLP[NLU Processor - spaCy]
        EX[Export Service]
    end

    %% Data Storage Layer
    subgraph "Data Layer"
        PG[(PostgreSQL Database)]
        RD[(Redis Queue/Cache)]
        WV[(Weaviate Vector DB)]
        MO[(MinIO Object Storage)]
    end

    %% External Services
    subgraph "External"
        LLM[Ollama LLM Models]
        NGINX[Nginx Reverse Proxy]
    end

    %% User Flow
    USER[Support Engineer] --> UI
    UI --> UP
    UI --> DB
    UI --> KB
    UI --> ST

    %% API Connections
    UP --> API
    DB --> API
    KB --> API
    ST --> API

    %% API to Services
    API --> AUTH
    API --> ROUTER
    ROUTER --> LE
    ROUTER --> EE
    ROUTER --> RE
    ROUTER --> AI
    ROUTER --> NLP
    ROUTER --> EX

    %% Service Interactions
    LE --> MO
    LE --> PG
    EE --> WV
    EE --> RD
    RE --> WV
    RE --> PG
    AI --> LLM
    AI --> PG
    NLP --> PG
    EX --> PG
    EX --> MO

    %% Data Flow
    MO --> LE
    PG --> RE
    WV --> RE
    RD --> EE
    RD --> AI

    %% External Access
    NGINX --> API
    AI --> LLM

    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec

    class UI,UP,DB,KB,ST frontend
    class API,AUTH,ROUTER api
    class LE,EE,RE,AI,NLP,EX service
    class PG,RD,WV,MO data
    class LLM,NGINX external
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as Support Engineer
    participant UI as Streamlit UI
    participant API as FastAPI Backend
    participant LE as Log Extractor
    participant EE as Embedding Engine
    participant RE as Retrieval Engine
    participant AI as AI Analyzer
    participant NLP as NLU Processor
    participant DB as PostgreSQL
    participant VDB as Weaviate
    participant Cache as Redis
    participant Storage as MinIO

    User->>UI: Upload ZIP file
    UI->>API: POST /api/upload
    API->>Storage: Store ZIP file
    API->>DB: Create job record
    API->>Cache: Queue processing job
    API-->>UI: Return job_id

    Cache->>LE: Process job
    LE->>Storage: Download ZIP file
    LE->>LE: Extract log files
    LE->>DB: Update job status
    LE->>EE: Send extracted logs

    EE->>EE: Generate embeddings
    EE->>VDB: Store vector embeddings
    EE->>RE: Trigger similarity search

    RE->>VDB: Query similar cases
    RE->>DB: Fetch historical solutions
    RE->>AI: Send context + logs

    AI->>AI: Analyze with LLM
    AI->>NLP: Extract entities
    NLP->>DB: Store NLU results
    AI->>DB: Store analysis results

    DB-->>UI: Job completion notification
    User->>UI: View results
    UI->>API: GET /api/jobs/{id}/results
    API->>DB: Fetch analysis results
    API-->>UI: Return formatted results
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Upload Flow"
        A[ZIP Upload] --> B[File Validation]
        B --> C[Storage in MinIO]
        C --> D[Job Creation]
        D --> E[Queue in Redis]
    end

    subgraph "Processing Pipeline"
        E --> F[Log Extraction]
        F --> G[Content Analysis]
        G --> H[Vector Embedding]
        H --> I[Similarity Search]
        I --> J[AI Analysis]
        J --> K[NLU Processing]
        K --> L[Result Storage]
    end

    subgraph "Results & Export"
        L --> M[Dashboard Display]
        M --> N[Export Generation]
        N --> O[PDF/Word Reports]
    end

    %% Data Stores
    C -.-> MinIO[(MinIO)]
    D -.-> PG[(PostgreSQL)]
    E -.-> Redis[(Redis)]
    H -.-> Weaviate[(Weaviate)]
    L -.-> PG

    %% External Services
    J -.-> Ollama[Ollama LLM]
    K -.-> spaCy[spaCy NLP]
```

## Network Architecture

```mermaid
graph TB
    subgraph "External Network"
        Internet[Internet]
        User[Support Engineers]
    end

    subgraph "DMZ"
        LB[Load Balancer]
        Proxy[Nginx Reverse Proxy]
    end

    subgraph "Application Network"
        subgraph "Frontend Tier"
            FE1[Streamlit Instance 1]
            FE2[Streamlit Instance 2]
        end

        subgraph "API Tier"
            API1[FastAPI Instance 1]
            API2[FastAPI Instance 2]
        end

        subgraph "Service Tier"
            MS1[Log Extractor]
            MS2[Embedding Engine]
            MS3[Retrieval Engine]
            MS4[AI Analyzer]
            MS5[NLU Processor]
            MS6[Export Service]
        end
    end

    subgraph "Data Network"
        subgraph "Databases"
            PG[PostgreSQL Primary]
            PGR[PostgreSQL Replica]
            Redis[Redis Cluster]
            Weaviate[Weaviate Cluster]
        end

        subgraph "Storage"
            MinIO[MinIO Cluster]
        end
    end

    subgraph "AI Network"
        Ollama[Ollama GPU Cluster]
    end

    %% Connections
    User --> Internet
    Internet --> LB
    LB --> Proxy
    Proxy --> FE1
    Proxy --> FE2
    FE1 --> API1
    FE2 --> API2
    API1 --> MS1
    API1 --> MS2
    API2 --> MS3
    API2 --> MS4
    MS1 --> PG
    MS2 --> Weaviate
    MS3 --> Redis
    MS4 --> Ollama
    MS5 --> PG
    MS6 --> MinIO
```

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            FW[Firewall]
            WAF[Web Application Firewall]
            VPN[VPN Gateway]
        end

        subgraph "Application Security"
            JWT[JWT Authentication]
            RBAC[Role-Based Access Control]
            API_KEY[API Key Management]
        end

        subgraph "Data Security"
            ENC[Encryption at Rest]
            TLS[TLS in Transit]
            VAULT[Secret Management]
        end

        subgraph "Infrastructure Security"
            SCAN[Container Scanning]
            MONITOR[Security Monitoring]
            AUDIT[Audit Logging]
        end
    end

    subgraph "Application Components"
        UI[Streamlit UI]
        API[FastAPI Backend]
        SERVICES[Microservices]
        DATA[Data Stores]
    end

    %% Security Flow
    FW --> WAF
    WAF --> UI
    UI --> JWT
    JWT --> RBAC
    RBAC --> API
    API --> API_KEY
    API_KEY --> SERVICES
    SERVICES --> ENC
    ENC --> DATA

    %% Monitoring
    MONITOR --> UI
    MONITOR --> API
    MONITOR --> SERVICES
    AUDIT --> DATA
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Docker Compose]
        DEV_DB[(Local Databases)]
        DEV_STORAGE[(Local Storage)]
    end

    subgraph "Staging Environment"
        STAGE_K8S[Kubernetes Cluster]
        STAGE_DB[(Staging Databases)]
        STAGE_STORAGE[(Staging Storage)]
    end

    subgraph "Production Environment"
        subgraph "Kubernetes Production"
            PROD_FE[Frontend Pods]
            PROD_API[API Pods]
            PROD_SERVICES[Service Pods]
        end

        subgraph "Managed Services"
            RDS[(AWS RDS PostgreSQL)]
            ELASTICACHE[(AWS ElastiCache Redis)]
            S3[(AWS S3 Storage)]
        end

        subgraph "AI Infrastructure"
            GPU_NODES[GPU Node Pool]
            OLLAMA_PODS[Ollama Pods]
        end
    end

    subgraph "CI/CD Pipeline"
        GIT[Git Repository]
        BUILD[Build Pipeline]
        TEST[Test Pipeline]
        DEPLOY[Deployment Pipeline]
    end

    %% Flow
    GIT --> BUILD
    BUILD --> TEST
    TEST --> DEV
    DEV --> STAGE_K8S
    STAGE_K8S --> DEPLOY
    DEPLOY --> PROD_FE
    DEPLOY --> PROD_API
    DEPLOY --> PROD_SERVICES
```

## Technology Stack Diagram

```mermaid
mindmap
  root((Intelligent Log Analyzer))
    Frontend
      Streamlit
      Python
      Plotly
      Pandas
    Backend
      FastAPI
      Python
      Pydantic
      SQLAlchemy
    AI/ML
      Ollama
      spaCy
      Transformers
      Weaviate
    Data Storage
      PostgreSQL
      Redis
      MinIO
      Weaviate
    Infrastructure
      Docker
      Kubernetes
      Nginx
      Prometheus
    Security
      JWT
      TLS/SSL
      RBAC
      Vault
```

## Performance & Monitoring

```mermaid
graph TB
    subgraph "Monitoring Stack"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
        JAEGER[Jaeger Tracing]
    end

    subgraph "Application Metrics"
        APP_METRICS[Application Metrics]
        BUSINESS_METRICS[Business Metrics]
        PERFORMANCE_METRICS[Performance Metrics]
    end

    subgraph "Infrastructure Metrics"
        NODE_METRICS[Node Metrics]
        CONTAINER_METRICS[Container Metrics]
        NETWORK_METRICS[Network Metrics]
    end

    subgraph "Log Aggregation"
        FLUENTD[Fluentd]
        ELASTIC[Elasticsearch]
        KIBANA[Kibana]
    end

    %% Data Flow
    APP_METRICS --> PROM
    BUSINESS_METRICS --> PROM
    PERFORMANCE_METRICS --> PROM
    NODE_METRICS --> PROM
    CONTAINER_METRICS --> PROM
    NETWORK_METRICS --> PROM

    PROM --> GRAF
    PROM --> ALERT
    JAEGER --> GRAF

    FLUENTD --> ELASTIC
    ELASTIC --> KIBANA
```

## Key Features

### 🏗️ **Microservices Architecture**
- **Scalable Design**: Independent services for different processing stages
- **Fault Tolerance**: Service isolation prevents cascade failures
- **Technology Diversity**: Each service optimized for its specific task

### 🔄 **Asynchronous Processing**
- **Queue-Based**: Redis queues for job management
- **Real-time Updates**: WebSocket connections for live progress
- **Parallel Processing**: Multiple workers for concurrent analysis

### 🤖 **AI-Powered Analysis**
- **Vector Similarity**: Weaviate for semantic search
- **LLM Integration**: Ollama for advanced reasoning
- **NLP Processing**: spaCy for entity extraction

### 📊 **Comprehensive Monitoring**
- **Health Checks**: Service availability monitoring
- **Performance Metrics**: Response times and throughput
- **Business Metrics**: Analysis success rates and user engagement

### 🔒 **Security First**
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Data Protection**: Encryption at rest and in transit
- **Audit Trail**: Comprehensive logging for compliance

This system diagram provides a complete visual representation of the Intelligent Log Analyzer's architecture, showing how all components interact to deliver AI-powered log analysis capabilities.
