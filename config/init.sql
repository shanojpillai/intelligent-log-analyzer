
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(255),
    file_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255),
    files_processed INTEGER,
    issues_found INTEGER,
    confidence FLOAT,
    key_findings JSONB,
    severity_distribution JSONB,
    ai_analysis JSONB,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    description TEXT,
    solution TEXT,
    category VARCHAR(100),
    severity VARCHAR(50),
    success_rate FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS similar_cases (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255),
    case_id VARCHAR(255),
    similarity_score FLOAT,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO knowledge_base (case_id, title, description, solution, category, severity, success_rate) VALUES
('KB_001', 'Database Connection Timeout Resolution', 'Database connection timeout errors in production environment', 'Increase connection pool size and timeout values. Monitor connection usage patterns.', 'Database', 'HIGH', 0.95),
('KB_002', 'Memory Usage Optimization', 'High memory usage causing performance degradation', 'Implement memory profiling and garbage collection optimization. Review memory-intensive operations.', 'Performance', 'MEDIUM', 0.88),
('KB_003', 'API Rate Limiting Mitigation', 'External API rate limiting causing service disruption', 'Implement exponential backoff, request queuing, and circuit breaker patterns.', 'API', 'HIGH', 0.92),
('KB_004', 'Disk Space Management', 'Disk space exhaustion causing application failures', 'Implement log rotation, cleanup old files, and monitor disk usage with alerts.', 'Storage', 'HIGH', 0.90),
('KB_005', 'Network Connectivity Issues', 'Intermittent network connectivity problems', 'Check network configuration, implement retry mechanisms, and monitor network health.', 'Network', 'MEDIUM', 0.85)
ON CONFLICT (case_id) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id ON analysis_results(job_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_severity ON knowledge_base(severity);
CREATE INDEX IF NOT EXISTS idx_similar_cases_job_id ON similar_cases(job_id);
