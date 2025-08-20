#!/bin/bash


set -e

echo "🌱 Seeding sample data..."

echo "⏳ Waiting for services to start..."
sleep 30

echo "📦 Creating sample log files..."
mkdir -p /tmp/sample-logs

cat > /tmp/sample-logs/application.log << 'EOF'
2024-01-20 10:30:00 INFO  [main] Application starting up
2024-01-20 10:30:01 INFO  [main] Database connection pool initialized
2024-01-20 10:30:15 WARN  [pool-1] Database connection timeout after 30 seconds
2024-01-20 10:30:16 ERROR [pool-1] Failed to connect to database: Connection timeout
2024-01-20 10:30:30 ERROR [main] java.sql.SQLException: Connection pool exhausted
2024-01-20 10:31:00 WARN  [gc] Memory usage: 85% of heap space used
2024-01-20 10:31:15 ERROR [api] Rate limit exceeded for external service call
2024-01-20 10:31:30 INFO  [main] Attempting database reconnection
2024-01-20 10:31:45 INFO  [main] Database connection restored
2024-01-20 10:32:00 INFO  [main] Application running normally
EOF

cat > /tmp/sample-logs/error.log << 'EOF'
2024-01-20 10:30:16 ERROR Database connection failed
2024-01-20 10:30:30 FATAL Connection pool exhausted - no available connections
2024-01-20 10:31:15 ERROR API rate limit exceeded: 429 Too Many Requests
2024-01-20 10:31:20 ERROR Failed to process request: timeout after 30000ms
2024-01-20 10:31:25 ERROR OutOfMemoryError: Java heap space
EOF

cat > /tmp/sample-logs/system.log << 'EOF'
2024-01-20 10:29:00 INFO System startup initiated
2024-01-20 10:29:30 INFO Loading configuration files
2024-01-20 10:30:00 INFO Services initialization complete
2024-01-20 10:30:15 WARN High CPU usage detected: 90%
2024-01-20 10:30:30 WARN Disk space low: 15% remaining
2024-01-20 10:31:00 ERROR Service health check failed
2024-01-20 10:31:30 INFO Service recovery initiated
2024-01-20 10:32:00 INFO All services healthy
EOF

cd /tmp
zip -r sample-logs.zip sample-logs/
echo "✅ Sample ZIP file created: /tmp/sample-logs.zip"

rm -rf /tmp/sample-logs

echo "🎯 Sample data ready for testing!"
echo "📁 Upload /tmp/sample-logs.zip through the web interface to test the system"
