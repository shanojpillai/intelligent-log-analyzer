#!/bin/bash

echo "🚀 Starting Intelligent Log Analyzer System Tests"
echo "=================================================="

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Please install Python 3."
    exit 1
fi

echo "📦 Installing test dependencies..."
pip3 install requests

echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking service status..."
docker-compose ps

echo "🧪 Running functionality tests..."
python3 test_system.py

echo "📋 Recent logs from backend service:"
docker-compose logs --tail=20 backend

echo "🏁 Test run completed!"
