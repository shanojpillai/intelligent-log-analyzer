#!/bin/bash


set -e

echo "🔍 Setting up Intelligent Log Analyzer..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "📁 Creating directories..."
mkdir -p data/{uploads,extracted,embeddings,knowledge-base,exports}
mkdir -p logs
mkdir -p config/ssl

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before starting the system."
fi

echo "🔐 Setting permissions..."
chmod +x scripts/*.sh
chmod 755 data/
chmod 755 logs/

echo "🐳 Pulling Docker images..."
docker-compose pull

echo "🔨 Building custom images..."
docker-compose build

echo "🤖 Initializing AI model..."
docker-compose up -d ollama
sleep 10
docker-compose exec ollama ollama pull llama2 || echo "⚠️  Ollama model pull failed - will retry on first use"

echo "✅ Setup completed!"
echo ""
echo "🚀 To start the system:"
echo "   docker-compose up -d"
echo ""
echo "🌐 Access points:"
echo "   Frontend UI: http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Monitoring:"
echo "   MinIO Console: http://localhost:9001"
echo "   Weaviate: http://localhost:8080"
echo ""
echo "🔧 To view logs:"
echo "   docker-compose logs -f [service-name]"
echo ""
echo "🛑 To stop the system:"
echo "   docker-compose down"
