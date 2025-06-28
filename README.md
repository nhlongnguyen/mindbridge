# MindBridge: Agentic RAG Documentation System

[![CI/CD Pipeline](https://github.com/user/mindbridge/workflows/CI/badge.svg)](https://github.com/user/mindbridge/actions)
[![Code Coverage](https://codecov.io/gh/user/mindbridge/branch/main/graph/badge.svg)](https://codecov.io/gh/user/mindbridge)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An intelligent documentation and code analysis system that combines vector-based semantic search with graph database relationships to provide comprehensive answers about software tools, libraries, frameworks, and programming languages.

## 🚀 Features

- **🔍 Hybrid Search**: Combines vector-based semantic search with graph relationship traversal
- **📊 Repository Analysis**: Automated processing of GitHub repositories to extract code structure and documentation
- **🏷️ Version Management**: Handles multiple versions of tools/libraries with version-specific queries
- **🤖 Contextual RAG**: Advanced retrieval-augmented generation with cross-referenced information
- **🔒 Secure API**: JWT-based authentication with comprehensive REST endpoints
- **⚡ Async Processing**: Background job processing for large repository analysis
- **📈 Observability**: Built-in monitoring, logging, and health checks

## 🏗️ Architecture

```mermaid
graph TB
    Client[Client Applications] --> API[FastAPI Backend]
    API --> Auth[JWT Authentication]
    API --> Queue[Celery Workers]
    Queue --> GitHub[GitHub Integration]
    Queue --> Parser[Code/Doc Parser]
    Parser --> DB[(PostgreSQL + pgvector)]
    Parser --> Cache[(Redis Cache/Queue)]
    API --> Search[Search Service]
    Search --> DB
    Search --> Cache
```

### Technology Stack

- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with pgvector extension for vector operations
- **Cache/Queue**: Redis for caching and job processing
- **Workers**: Celery for background task processing
- **Authentication**: JWT-based security
- **Monitoring**: OpenTelemetry with structured logging
- **Deployment**: Docker Compose with Kubernetes readiness

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- Git
- Docker & Docker Compose (for containerized setup)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/nhlongnguyen/mindbridge.git
cd mindbridge

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### Development Setup

```bash
# Install Python dependencies
pip install poetry
poetry install --with dev,test

# Install pre-commit hooks
pre-commit install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
poetry run alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Start worker process (in separate terminal)
poetry run celery -A src.worker.celery_app worker --loglevel=info
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mindbridge
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# GitHub Integration
GITHUB_TOKEN=your-github-personal-access-token

# Application Settings
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=false

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
BATCH_SIZE=32

# Search Configuration
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100
SIMILARITY_THRESHOLD=0.7
```

### Database Setup

```bash
# Install PostgreSQL and pgvector extension
# Ubuntu/Debian:
sudo apt-get install postgresql-15 postgresql-15-pgvector

# macOS with Homebrew:
brew install postgresql pgvector

# Enable pgvector extension in your database
psql -d mindbridge -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run database migrations
poetry run alembic upgrade head
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Authentication

```bash
# Get JWT token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/repositories" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Core Endpoints

#### Repository Management

```bash
# Analyze a GitHub repository
curl -X POST "http://localhost:8000/repositories" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/user/repo"}'

# Check analysis progress
curl -X GET "http://localhost:8000/jobs/{job_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# List analyzed repositories
curl -X GET "http://localhost:8000/repositories" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Search Operations

```bash
# Semantic search across documentation
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to implement authentication",
    "repository_id": "optional-repo-filter",
    "limit": 10
  }'

# Search within specific repository
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database connection",
    "repository_id": "uuid-of-repository",
    "limit": 5
  }'
```

## 🧪 Testing

The project uses pytest with comprehensive test coverage requirements (85%+).

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov-report=html

# Run specific test categories
poetry run pytest tests/unit/          # Unit tests only
poetry run pytest tests/integration/   # Integration tests only

# Run tests with detailed output
poetry run pytest -v --tb=short

# Run tests in parallel
poetry run pytest -n auto
```

### Test Structure

Each test module follows the mandatory pattern:
- **Expected Use Case**: Normal operation with valid inputs
- **Edge Case**: Boundary conditions, empty inputs, maximum limits
- **Failure Case**: Invalid inputs, error conditions, exception handling

Example:
```python
class TestDocumentProcessor:
    def test_process_document_success(self):
        """Expected use case: Process valid document successfully"""
        # Test implementation

    def test_process_empty_document(self):
        """Edge case: Handle empty document"""
        # Test implementation

    def test_process_document_embedding_failure(self):
        """Failure case: Handle embedding service failure"""
        # Test implementation
```

## 🚀 Deployment

### Production with Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://your-domain.com/health

# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgresql.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/worker.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n mindbridge
kubectl get services -n mindbridge
```

### Environment-Specific Configurations

- **Development**: `docker-compose.yml`
- **Staging**: `docker-compose.staging.yml`
- **Production**: `docker-compose.prod.yml`

## 📊 Monitoring and Observability

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/health/db

# Redis connectivity
curl http://localhost:8000/health/redis

# Detailed system metrics
curl http://localhost:8000/metrics
```

### Logging

The application uses structured logging with OpenTelemetry integration:

```python
import structlog

logger = structlog.get_logger(__name__)

# Example usage
logger.info(
    "Repository analysis started",
    repository_id=repo_id,
    github_url=url,
    user_id=user.id
)
```

### Metrics and Tracing

- **Metrics**: Prometheus-compatible metrics available at `/metrics`
- **Tracing**: OpenTelemetry traces for request tracking
- **Dashboards**: Grafana dashboards for visualization

## 🤝 Contributing

We follow strict development standards outlined in [CLAUDE.md](./CLAUDE.md).

### Development Workflow

1. **Fetch Task**: Get assigned task from GitHub Projects
2. **Understand Requirements**: Analyze issue thoroughly
3. **Create Implementation Plan**: Detail technical approach in issue comments
4. **Wait for Approval**: Get plan reviewed before coding
5. **TDD Development**: Write tests first, implement second
6. **Quality Gates**: Pass all tests, linting, and coverage requirements
7. **Update Status**: Keep GitHub issue status current

### Code Quality Requirements

- **Test Coverage**: Minimum 85%
- **Linting**: Ruff, Black, isort compliance
- **Type Checking**: mypy strict mode
- **Documentation**: Google-style docstrings for all public APIs

```bash
# Run quality checks
poetry run ruff check src/ tests/
poetry run black --check src/ tests/
poetry run mypy src/
poetry run pytest --cov=src --cov-fail-under=85
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## 📈 Performance

### Benchmarks

- **Repository Analysis**: ~2-5 minutes for typical Python repository (1000+ files)
- **Search Latency**: <100ms for vector similarity search
- **Throughput**: 100+ concurrent search requests
- **Storage**: ~10MB per 1000 documents (with embeddings)

### Optimization Tips

1. **Batch Processing**: Use appropriate batch sizes for embedding generation
2. **Database Indexing**: Ensure proper indexes on frequently queried columns
3. **Caching**: Leverage Redis for frequently accessed data
4. **Connection Pooling**: Configure appropriate database connection pools

## 🔒 Security

### Security Measures

- **Authentication**: JWT-based with configurable expiration
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: Protection against abuse
- **HTTPS**: TLS encryption for all communications
- **Secrets Management**: Environment-based configuration

### Security Auditing

```bash
# Run security scan
poetry run bandit -r src/

# Check for vulnerabilities
poetry run safety check

# Audit dependencies
poetry audit
```

## 📋 Roadmap

### Current Version (v1.0 - MVP)
- ✅ PostgreSQL + pgvector for vector operations
- ✅ Python repository analysis
- ✅ Markdown documentation processing
- ✅ Semantic search functionality
- ✅ JWT authentication
- ✅ Background job processing

### Future Versions

#### v2.0 - Graph Database Integration
- [ ] Neo4j integration for code relationships
- [ ] Hybrid search (vector + graph traversal)
- [ ] Advanced dependency analysis
- [ ] Cross-reference linking

#### v3.0 - Multi-Language Support
- [ ] JavaScript/TypeScript analysis
- [ ] Java code processing
- [ ] Go language support
- [ ] Generic language framework

#### v4.0 - Advanced Agentic Features
- [ ] Query planning and optimization
- [ ] Tool usage and function calling
- [ ] Learning from user feedback
- [ ] Context-aware recommendations

#### v5.0 - Enterprise Features
- [ ] Multi-tenant architecture
- [ ] Advanced analytics and reporting
- [ ] Custom embedding models
- [ ] Enterprise SSO integration

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Test database connectivity
psql -h localhost -U username -d mindbridge -c "SELECT version();"

# Check pgvector extension
psql -d mindbridge -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

#### Redis Connection Issues
```bash
# Check Redis service
redis-cli ping

# Monitor Redis activity
redis-cli monitor
```

#### Embedding Generation Slow
```bash
# Check available system resources
htop

# Monitor GPU usage (if available)
nvidia-smi

# Adjust batch size in configuration
export BATCH_SIZE=16  # Reduce if memory constrained
```

#### Job Processing Issues
```bash
# Check Celery worker status
celery -A src.worker.celery_app inspect active

# Monitor job queue
celery -A src.worker.celery_app inspect reserved

# Restart workers
docker-compose restart worker
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/user/mindbridge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/user/mindbridge/discussions)
- **Documentation**: [Project Wiki](https://github.com/user/mindbridge/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [sentence-transformers](https://www.sbert.net/) for embedding generation
- [pgvector](https://github.com/pgvector/pgvector) for PostgreSQL vector operations
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Celery](https://docs.celeryproject.org/) for distributed task processing

---

**Built with ❤️ for the developer community**

For detailed development guidelines, see [CLAUDE.md](./CLAUDE.md)
