#!/bin/bash
set -e

echo "🚀 Setting up Mindbridge Docker environment..."

# Change to project directory
cd "$(dirname "$0")/.."

# Check if .env.docker exists
if [ ! -f .env.docker ]; then
    echo "❌ .env.docker file not found!"
    exit 1
fi

echo "📦 Building Docker images..."
docker-compose --env-file .env.docker build --no-cache app

echo "🗄️ Starting database and Redis services..."
docker-compose --env-file .env.docker up -d postgres redis

echo "⏳ Waiting for services to be healthy..."
echo "Waiting for PostgreSQL..."
until docker-compose --env-file .env.docker exec postgres pg_isready -U mindbridge >/dev/null 2>&1; do
  echo "  PostgreSQL not ready yet..."
  sleep 3
done
echo "✅ PostgreSQL is ready!"

echo "Waiting for Redis..."
until docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 ping >/dev/null 2>&1; do
  echo "  Redis not ready yet..."
  sleep 3
done
echo "✅ Redis is ready!"

echo "🔄 Running database migrations..."
docker-compose --env-file .env.docker run --rm -e PYTHONPATH=/app app alembic upgrade head

echo "🎯 Starting full application stack..."
docker-compose --env-file .env.docker up -d

echo "⏳ Waiting for application to be ready..."
sleep 15

echo "🩺 Running health checks..."
for i in {1..30}; do
  if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Application is healthy!"
    break
  fi
  echo "  Waiting for application... ($i/30)"
  sleep 3
done

echo ""
echo "📊 Final stack status:"
docker-compose --env-file .env.docker ps

echo ""
echo "🎉 Mindbridge is now running!"
echo "📍 Application: http://localhost:8000"
echo "📍 Health check: http://localhost:8000/health"
echo "📍 API docs: http://localhost:8000/docs"
echo "📍 Metrics: http://localhost:8000/metrics"
echo "📍 Redis Insight: http://localhost:8001"
echo ""
echo "📋 Useful commands:"
echo "  • View app logs: docker-compose --env-file .env.docker logs -f app"
echo "  • View all logs: docker-compose --env-file .env.docker logs -f"
echo "  • Stop stack: docker-compose --env-file .env.docker down"
echo "  • Reset database: docker-compose --env-file .env.docker down -v"
echo "  • Run migrations: docker-compose --env-file .env.docker run --rm app alembic upgrade head"
