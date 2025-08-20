#!/bin/bash


set -e

BACKUP_DIR="/tmp/log-analyzer-backup-$(date +%Y%m%d_%H%M%S)"
echo "💾 Creating backup in $BACKUP_DIR..."

mkdir -p "$BACKUP_DIR"

echo "🗄️  Backing up PostgreSQL database..."
docker-compose exec -T postgres pg_dump -U postgres log_analyzer > "$BACKUP_DIR/database.sql"

echo "📊 Backing up Redis data..."
docker-compose exec -T redis redis-cli --rdb - > "$BACKUP_DIR/redis.rdb"

echo "🗃️  Backing up MinIO data..."
docker-compose exec -T minio mc mirror /data "$BACKUP_DIR/minio" || echo "⚠️  MinIO backup failed"

echo "🔍 Backing up Weaviate data..."
mkdir -p "$BACKUP_DIR/weaviate"
docker cp $(docker-compose ps -q weaviate):/var/lib/weaviate "$BACKUP_DIR/weaviate/" || echo "⚠️  Weaviate backup failed"

echo "📁 Backing up uploaded files..."
cp -r data/ "$BACKUP_DIR/data/" 2>/dev/null || echo "⚠️  No data directory found"

echo "⚙️  Backing up configuration..."
cp .env "$BACKUP_DIR/.env" 2>/dev/null || echo "⚠️  No .env file found"
cp -r config/ "$BACKUP_DIR/config/" 2>/dev/null || echo "⚠️  No config directory found"

echo "🗜️  Compressing backup..."
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"

rm -rf "$BACKUP_DIR"

echo "✅ Backup completed: $BACKUP_DIR.tar.gz"
echo "📏 Backup size: $(du -h "$BACKUP_DIR.tar.gz" | cut -f1)"
