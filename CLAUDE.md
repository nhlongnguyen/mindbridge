# Mindbridge - Agentic RAG Documentation System

## Project Overview

An intelligent documentation and code analysis system that combines vector-based semantic search with graph database relationships to provide comprehensive answers about software tools, libraries, frameworks, and programming languages. The system processes GitHub repositories, extracts code structure and documentation, and enables hybrid search capabilities through both vector similarity and graph traversal.

### Core Features
- **Repository Analysis**: Automated processing of GitHub repositories to extract code structure and documentation
- **Hybrid Search**: Combines vector-based semantic search with graph relationship traversal
- **Version Management**: Handles multiple versions of tools/libraries with version-specific queries
- **Contextual RAG**: Advanced retrieval-augmented generation with cross-referenced information
- **REST API**: Complete API for repository management and search operations

### Technology Stack
- **Database**: PostgreSQL with pgvector extension
- **Cache/Queue**: Redis for caching and job processing
- **Backend**: FastAPI with Celery workers
- **Authentication**: JWT-based security
- **Monitoring**: OpenTelemetry with structured logging
- **Deployment**: Docker Compose with Kubernetes readiness

---

## Coding Standards and Architecture

### Object-Oriented Programming (OOP) Principles

**Mandatory Requirements:**
- All business logic must be encapsulated in classes with clear responsibilities
- Use composition over inheritance whenever possible
- Implement proper encapsulation with private/protected members where appropriate
- Follow the principle of "Tell, Don't Ask" - objects should expose behavior, not internal state

**Class Design Rules:**
```python
# Good: Proper encapsulation and behavior exposure
class DocumentProcessor:
    def __init__(self, embedding_service: EmbeddingService):
        self._embedding_service = embedding_service
        self._processed_count = 0

    def process_document(self, document: Document) -> ProcessedDocument:
        # Implementation here
        pass

    @property
    def processed_count(self) -> int:
        return self._processed_count

# Avoid: Exposing internal state directly
class BadDocumentProcessor:
    def __init__(self):
        self.embedding_service = None  # Public attribute
        self.documents = []            # Mutable public state
```

### SOLID Principles (Strictly Enforced)

**Single Responsibility Principle (SRP):**
- Each class must have exactly one reason to change
- Separate data access, business logic, and presentation concerns
- Use service classes for business operations, repository classes for data access

**Open/Closed Principle (OCP):**
- Design for extension without modification
- Use abstract base classes and interfaces
- Implement strategy pattern for varying algorithms

**Liskov Substitution Principle (LSP):**
- Derived classes must be substitutable for their base classes
- Maintain behavioral contracts in inheritance hierarchies

**Interface Segregation Principle (ISP):**
- Create specific interfaces rather than general-purpose ones
- Clients should not depend on interfaces they don't use

**Dependency Inversion Principle (DIP):**
- Depend on abstractions, not concretions
- Use dependency injection for all external dependencies

```python
# Example of SOLID implementation
from abc import ABC, abstractmethod
from typing import Protocol

class EmbeddingService(Protocol):
    def generate_embedding(self, text: str) -> List[float]: ...

class VectorStore(ABC):
    @abstractmethod
    def store_vector(self, vector: List[float], metadata: Dict) -> str: ...

    @abstractmethod
    def search_similar(self, vector: List[float], limit: int) -> List[SearchResult]: ...

class DocumentIndexer:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore):
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def index_document(self, document: Document) -> IndexResult:
        embedding = self._embedding_service.generate_embedding(document.content)
        vector_id = self._vector_store.store_vector(embedding, document.metadata)
        return IndexResult(vector_id=vector_id, status="indexed")
```

### Clean Code Principles

**Naming Conventions:**
- Use descriptive, intention-revealing names
- Avoid abbreviations and cryptic naming
- Use verbs for functions, nouns for classes and variables
- Boolean variables should start with `is_`, `has_`, `can_`, `should_`

**Function Design:**
- Keep functions small (max 20 lines)
- Functions should do one thing well
- Use pure functions where possible (no side effects)
- Maximum 3 parameters; use data classes for more complex parameter sets

**Code Organization:**
- Group related functionality in modules
- Use package structure to reflect domain boundaries
- Keep import statements organized (standard library, third-party, local)

---

## Testing Standards

### Testing Framework
- **Primary**: pytest for all testing
- **Additional**: pytest-asyncio for async code testing
- **Mocking**: pytest-mock and unittest.mock
- **Coverage**: pytest-cov with minimum 85% coverage requirement

### Test Types and Requirements

**Unit Tests (Mandatory for all classes and functions):**
- Test individual components in isolation
- Mock all external dependencies
- File naming: `test_<module_name>.py`
- Class naming: `Test<ClassName>`

**Integration Tests (Required for all API endpoints and database operations):**
- Test component interactions
- Use test database and external service mocks
- File naming: `test_integration_<feature_name>.py`

**Test Case Requirements (Every test function must include):**

1. **Expected Use Case**: Normal operation with valid inputs
2. **Edge Case**: Boundary conditions, empty inputs, maximum limits
3. **Failure Case**: Invalid inputs, error conditions, exception handling

```python
# Example test structure
class TestDocumentProcessor:

    def test_process_document_success(self, mock_embedding_service, sample_document):
        """Expected use case: Process valid document successfully"""
        processor = DocumentProcessor(mock_embedding_service)
        result = processor.process_document(sample_document)

        assert result.status == ProcessingStatus.SUCCESS
        assert result.chunks_count > 0
        mock_embedding_service.generate_embedding.assert_called()

    def test_process_empty_document(self, mock_embedding_service):
        """Edge case: Handle empty document"""
        processor = DocumentProcessor(mock_embedding_service)
        empty_doc = Document(content="", metadata={})
        result = processor.process_document(empty_doc)

        assert result.status == ProcessingStatus.SKIPPED
        assert result.chunks_count == 0

    def test_process_document_embedding_failure(self, mock_embedding_service, sample_document):
        """Failure case: Handle embedding service failure"""
        mock_embedding_service.generate_embedding.side_effect = EmbeddingError("Service unavailable")
        processor = DocumentProcessor(mock_embedding_service)

        with pytest.raises(DocumentProcessingError):
            processor.process_document(sample_document)
```

### Test Data Management
- Use factories (factory_boy) for test data creation
- Store test fixtures in `tests/fixtures/` directory
- Use temporary databases for integration tests
- Clean up resources in test teardown

### Testing Anti-Patterns to Avoid

**Framework Anti-Patterns:**
- **Avoid**: Using multiple testing frameworks simultaneously (pytest + unittest + nose)
- **Avoid**: Mixing assertion styles (assert vs self.assertEqual vs expect)
- **Avoid**: Custom test runners without clear justification
- **Avoid**: Testing framework-specific features that reduce portability

**Test Structure Anti-Patterns:**
- **Avoid**: Mega tests that test multiple unrelated behaviors
- **Avoid**: Tests that depend on execution order (use proper isolation)
- **Avoid**: Tests that rely on external state or services without proper mocking
- **Avoid**: Tests with unclear or misleading names (test_1, test_stuff, test_everything)

**Mocking Anti-Patterns:**
- **Avoid**: Over-mocking internal implementation details
- **Avoid**: Mocking the system under test itself
- **Avoid**: Tests that mock everything and test nothing
- **Avoid**: Shared mocks across unrelated test cases

**Data Management Anti-Patterns:**
- **Avoid**: Tests that create permanent data or side effects
- **Avoid**: Hard-coded test data that becomes brittle over time
- **Avoid**: Tests that share mutable test data without proper cleanup
- **Avoid**: Database tests that don't use transactions or proper isolation

**Performance Anti-Patterns:**
- **Avoid**: Tests that make real network calls without necessity
- **Avoid**: Tests that sleep or use arbitrary timeouts
- **Avoid**: Tests that test performance characteristics without proper benchmarking setup
- **Avoid**: Integration tests that could be unit tests (over-testing)

**Encapsulation Anti-Patterns:**
- **Avoid**: Testing private methods directly (test through public interface instead)
- **Avoid**: Accessing private attributes in tests (use public properties/methods)
- **Avoid**: Testing implementation details rather than behavior contracts
- **Avoid**: Tests that break when internal refactoring occurs

**Assertion Anti-Patterns:**
- **Avoid**: Tests with no assertions (they don't verify anything)
- **Avoid**: Too many assertions in a single test (violates single responsibility)
- **Avoid**: Assertions that don't relate to the test name or purpose
- **Avoid**: Vague assertions that don't provide meaningful failure messages

**Test Organization Anti-Patterns:**
- **Avoid**: Tests that don't follow AAA (Arrange, Act, Assert) pattern
- **Avoid**: Business logic tests mixed with presentation layer tests
- **Avoid**: Duplicate test setup code without proper abstraction (use fixtures/factories)
- **Avoid**: Tests placed in incorrect test categories (unit tests that are actually integration tests)

**Coverage Anti-Patterns:**
- **Avoid**: Writing tests solely to increase coverage metrics without testing behavior
- **Avoid**: Focusing only on line coverage while ignoring branch coverage
- **Avoid**: Gaming coverage metrics with meaningless tests
- **Avoid**: Using coverage as the only quality metric for test suites

**Async/Concurrency Anti-Patterns:**
- **Avoid**: Testing async code synchronously (missing async/await patterns)
- **Avoid**: Tests with race conditions or timing dependencies
- **Avoid**: Blocking async tests that defeat the purpose of async code
- **Avoid**: Not testing concurrent access patterns for shared resources

---

## Code Style and Linting

### Community Standards (Strictly Enforced)
- **Code Formatter**: Black with line length 88
- **Import Sorter**: isort with Black compatibility
- **Linter**: Ruff (replaces flake8, pylint, isort, and more)
- **Type Checker**: mypy with strict mode enabled
- **File Format**: All files must end with a single newline character

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml (must be used)
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Type Annotations (Mandatory)
- All function parameters and return types must be annotated
- Use `typing` module for complex types
- Use `Protocol` for structural typing
- Enable strict mypy checking

```python
from typing import List, Dict, Optional, Union, Protocol
from dataclasses import dataclass

@dataclass
class SearchResult:
    content: str
    score: float
    metadata: Dict[str, Union[str, int, float]]

class SearchService(Protocol):
    def search(self, query: str, limit: int = 10) -> List[SearchResult]: ...

def process_search_results(
    results: List[SearchResult],
    minimum_score: float = 0.7
) -> Optional[List[SearchResult]]:
    if not results:
        return None
    return [r for r in results if r.score >= minimum_score]
```

---

## Documentation Standards

### Documentation Requirements (Proactive Updates Mandatory)

**Code Documentation:**
- All public classes and functions must have docstrings
- Use Google-style docstrings consistently
- Include type information, parameter descriptions, and return values
- Document exceptions that may be raised

```python
def analyze_repository(
    github_url: str,
    branch: str = "main",
    include_tests: bool = False
) -> RepositoryAnalysis:
    """Analyze a GitHub repository and extract code structure.

    Args:
        github_url: The GitHub repository URL to analyze
        branch: The git branch to analyze (defaults to "main")
        include_tests: Whether to include test files in analysis

    Returns:
        RepositoryAnalysis containing extracted code structure and metadata

    Raises:
        RepositoryNotFoundError: If the repository cannot be accessed
        AnalysisError: If the analysis process fails

    Example:
        >>> analysis = analyze_repository("https://github.com/user/repo")
        >>> print(f"Found {len(analysis.classes)} classes")
    """
```

**API Documentation:**
- Use FastAPI automatic documentation features
- Include example requests and responses
- Document all error codes and their meanings
- Maintain OpenAPI specification accuracy

**Architecture Documentation:**
- Update README.md for any architectural changes
- Maintain ADR (Architecture Decision Records) in `docs/adr/`
- Update deployment documentation for infrastructure changes
- Keep database schema documentation current

**Documentation Update Rules:**
1. **Before Feature Implementation**: Update design documents
2. **During Implementation**: Update code docstrings and comments
3. **After Feature Completion**: Update user-facing documentation
4. **On API Changes**: Update OpenAPI specs and examples

### Context7 Documentation Search (Mandatory)

**Rule**: Always use the Context7 MCP server to search for documentation before implementing any feature involving external libraries or frameworks.

**Usage Examples:**
```python
# Before implementing Weaviate integration:
# Use: mcp__context7__resolve-library-id with "weaviate"
# Then: mcp__context7__get-library-docs with resolved library ID

# Before implementing FastAPI features:
# Use: mcp__context7__resolve-library-id with "fastapi"
# Then: mcp__context7__get-library-docs with topic-specific queries
```

**Required Documentation Sources:**
- Library/framework official documentation
- Best practices and patterns
- Security considerations
- Performance optimization guidelines

---

## Project Management and GitHub Integration

### GitHub Project Configuration

**Project Details:**
- **Project ID**: `PVT_kwHOAEZ9Ks4A8mS8`
- **Project Number**: `1`
- **Project Name**: "Mindbrige development"
- **Owner**: nhlongnguyen
- **Status Field ID**: `PVTSSF_lAHOAEZ9Ks4A8mS8zgwjNKs`

**Status Options:**
- **Backlog** (ID: `f75ad846`) - This item hasn't been started
- **Ready** (ID: `e18bf179`) - This is ready to be picked up
- **In progress** (ID: `47fc9ee4`) - This is actively being worked on
- **In review** (ID: `aba860b9`) - This item is in review
- **Done** (ID: `98236657`) - This has been completed

### Task Management Rules (Strictly Enforced)

**GitHub Project Integration:**
- All development work must be tracked in GitHub Projects
- Tasks must be created as GitHub Issues with proper labels
- Use project board columns: Backlog, Ready, In Progress, In Review, Done
- Link all commits and PRs to their respective issues

**Task Workflow (Mandatory Process):**

1. **Fetch Task**: Retrieve task from GitHub Projects board
2. **Understand Requirements**: Analyze issue description, acceptance criteria, and dependencies
3. **Create Implementation Plan**: Provide detailed technical plan in issue comments
4. **Plan Review**: Wait for plan approval before starting implementation
5. **Create Feature Branch**: Create and switch to a new feature branch using format `feature/R-XXX-description`
6. **Update Task Status to "In Progress"**: Mark GitHub project task as "in progress" using GitHub CLI
7. **TDD Implementation**: Write tests first, then implement functionality
8. **Quality Gates**: Ensure all tests pass and linting rules are satisfied
9. **Commit Changes**: Stage and commit all changes with descriptive commit message
10. **Post Subtask Completion**: After completing each individual subtask listed in the issue description, post a comment to the GitHub issue with completion summary
11. **Create Pull Request**: Push branch and create PR with detailed description linking to issue
12. **Update Task Status to "In Review"**: Mark GitHub project task as "in review" using GitHub CLI
13. **Status Updates**: Update GitHub issue status throughout development

### GitHub Project Status Management Commands

**Update Task Status to "In Progress" (Before Implementation):**
```bash
# Get the task item ID from GitHub project (replace TASK_NUMBER with actual issue number)
TASK_ITEM_ID=$(gh project item-list 1 --owner nhlongnguyen | grep "R-XXX:" | awk '{print $NF}')

# Update status to "In Progress"
gh project item-edit \
  --id $TASK_ITEM_ID \
  --field-id PVTSSF_lAHOAEZ9Ks4A8mS8zgwjNKs \
  --single-select-option-id 47fc9ee4 \
  --project-id PVT_kwHOAEZ9Ks4A8mS8

# Alternative: Direct command with known item ID
gh project item-edit \
  --id PVTI_lAHOAEZ9Ks4A8mS8zgcBQO[X] \
  --field-id PVTSSF_lAHOAEZ9Ks4A8mS8zgwjNKs \
  --single-select-option-id 47fc9ee4 \
  --project-id PVT_kwHOAEZ9Ks4A8mS8
```

**Update Task Status to "In Review" (After Creating PR):**
```bash
# Get the task item ID from GitHub project (replace TASK_NUMBER with actual issue number)
TASK_ITEM_ID=$(gh project item-list 1 --owner nhlongnguyen | grep "R-XXX:" | awk '{print $NF}')

# Update status to "In Review"
gh project item-edit \
  --id $TASK_ITEM_ID \
  --field-id PVTSSF_lAHOAEZ9Ks4A8mS8zgwjNKs \
  --single-select-option-id aba860b9 \
  --project-id PVT_kwHOAEZ9Ks4A8mS8

# Alternative: Direct command with known item ID
gh project item-edit \
  --id PVTI_lAHOAEZ9Ks4A8mS8zgcBQO[X] \
  --field-id PVTSSF_lAHOAEZ9Ks4A8mS8zgwjNKs \
  --single-select-option-id aba860b9 \
  --project-id PVT_kwHOAEZ9Ks4A8mS8
```

**Status Quick Reference:**
- **Backlog**: `f75ad846`
- **Ready**: `e18bf179`
- **In Progress**: `47fc9ee4`
- **In Review**: `aba860b9`
- **Done**: `98236657`

### Subtask Completion Tracking Commands

**Post Subtask Completion Comment (After Each Individual Subtask):**
```bash
# Post completion comment for a specific subtask
gh issue comment ISSUE_NUMBER --body "## ✅ Subtask Completed: [Subtask Name]

### Summary
Brief description of what was implemented for this subtask.

### Changes Made
- List of specific changes
- Files modified/created
- Tests added/updated

### Next Steps
- Reference to next subtask (if any)
- Any dependencies or blockers identified

---
*Subtask checkpoint posted automatically via Claude Code workflow*"

# Example usage:
gh issue comment 42 --body "## ✅ Subtask Completed: Database Schema Setup

### Summary
Implemented PostgreSQL database schema with pgvector extension for vector storage.

### Changes Made
- Created database models in src/mindbridge/database/models.py
- Added Alembic migration files
- Updated database configuration in src/mindbridge/config.py
- Added unit tests for model validation

### Next Steps
- Proceeding to Redis cache implementation
- No blockers identified

---
*Subtask checkpoint posted automatically via Claude Code workflow*"
```

### Implementation Workflow

**Workflow Diagram:**

```mermaid
flowchart TD
    A[Fetch Task from GitHub Projects] --> B[Understand Requirements]
    B --> C[Create Implementation Plan]
    C --> D[Plan Review & Approval]
    D --> E[Create Feature Branch]
    E --> F[Update Project Status to 'In Progress']
    F --> G[TDD: Write Failing Tests]
    G --> H[Implement Code to Pass Tests]
    H --> I[Run Test Suite]

    I --> J{All Tests Pass?}
    J -->|No| K[Fix Failing Tests]
    K --> I
    J -->|Yes| L[Run Pre-commit Checks]

    L --> M{Pre-commit Checks Pass?}
    M -->|No| N[Fix Linting/Type/Format Issues]
    N --> L
    M -->|Yes| O[Stage & Commit Changes]

    O --> P[Post Subtask Completion Comment]
    P --> Q{More Subtasks?}
    Q -->|Yes| G
    Q -->|No| R[Push Branch]
    R --> S[Create Pull Request]
    S --> T[Update Project Status to 'In Review']
    T --> U[Update GitHub Issue Status]

    style I fill:#e1f5fe
    style J fill:#fff3e0
    style K fill:#ffebee
    style L fill:#e8f5e8
    style M fill:#fff3e0
    style N fill:#ffebee
    style O fill:#e8f5e8
    style P fill:#e8f5e8
    style Q fill:#fff3e0
    style F fill:#fff8dc
    style T fill:#f0e68c

    subgraph "Quality Gates Loop"
        I
        J
        K
        L
        M
        N
    end

    subgraph "Subtask Loop"
        G
        H
        I
        J
        K
        L
        M
        N
        O
        P
        Q
    end

    subgraph "Test Commands"
        T1["python3 -m poetry run pytest tests/ --cov=src --cov-report=html"]
    end

    subgraph "Pre-commit Commands"
        P1["python3 -m poetry run pre-commit run --all-files"]
    end

    subgraph "GitHub Commands"
        F1["gh project item-edit --id TASK_ID --field-id STATUS_FIELD --single-select-option-id IN_PROGRESS"]
        T1_CMD["gh project item-edit --id TASK_ID --field-id STATUS_FIELD --single-select-option-id IN_REVIEW"]
        P1_CMD["gh issue comment ISSUE_NUMBER --body 'Subtask completed: [summary]'"]
    end

    I -.-> T1
    L -.-> P1
    F -.-> F1
    T -.-> T1_CMD
    P -.-> P1_CMD
```

**Phase 1: Task Analysis and Planning**
```markdown
## Implementation Plan Template (Required in GitHub Issues)

### Requirements Analysis
- [ ] Functional requirements understood
- [ ] Non-functional requirements identified
- [ ] Dependencies mapped
- [ ] Acceptance criteria clarified

### Technical Design
- [ ] Architecture approach defined
- [ ] Database schema changes identified
- [ ] API contract specified
- [ ] Error handling strategy planned

### Test Strategy
- [ ] Unit test cases identified
- [ ] Integration test scenarios planned
- [ ] Edge cases documented
- [ ] Failure scenarios considered

### Implementation Steps
1. Step 1: [Detailed description]
2. Step 2: [Detailed description]
3. Step 3: [Detailed description]

### Definition of Done
- [ ] All tests pass (unit + integration)
- [ ] Code coverage >= 85%
- [ ] Linting rules pass (ruff, black, mypy)
- [ ] Documentation updated
- [ ] API documentation current
- [ ] Manual testing completed
```

**Phase 2: Test-Driven Development**
```python
# Required TDD cycle for every feature:

# 1. Red: Write failing test
def test_new_feature_success():
    # Arrange
    service = MyService()

    # Act & Assert
    with pytest.raises(NotImplementedError):
        service.new_feature()

# 2. Green: Implement minimal code to pass
def new_feature(self):
    raise NotImplementedError("To be implemented")

# 3. Refactor: Improve code while keeping tests green
def new_feature(self):
    # Actual implementation
    return expected_result
```

**Phase 3: Quality Assurance and Delivery**
- Run full test suite: `python3 -m poetry run pytest tests/ --cov=src --cov-report=html`
- Run pre-commit checks: `python3 -m poetry run pre-commit run --all-files`
- Update documentation as needed

**Phase 4: Commit and Pull Request**
```bash
# Stage and commit changes
git add .
git commit -m "feat: R-XXX Implementation description

- Detailed bullet points of changes
- Reference to acceptance criteria met
- Any breaking changes noted

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push branch and create PR
git push -u origin feature/R-XXX-description
gh pr create --title "R-XXX: Implementation Title" --body "
## Summary
Brief description of implementation

## Changes
- [ ] Feature/change 1
- [ ] Feature/change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed

## Quality Gates
- [ ] All tests passing
- [ ] Code coverage >= 85%
- [ ] Linting rules pass
- [ ] Type checking clean

Closes #XXX
"
```

### GitHub Labels and Templates

**Required Issue Labels:**
- `type:feature` - New functionality
- `type:bug` - Bug fixes
- `type:docs` - Documentation updates
- `type:refactor` - Code improvements
- `priority:high` - Critical issues
- `priority:medium` - Standard issues
- `priority:low` - Nice-to-have improvements
- `status:planned` - In planning phase
- `status:in-progress` - Currently being worked on
- `status:review` - Ready for code review
- `size:small` - < 4 hours work
- `size:medium` - 4-16 hours work
- `size:large` - > 16 hours work

---

## Development Environment Setup

### Required Tools
```bash
# Python environment (Python 3.12+ required)
# Poetry is already installed via pip

# One-time setup: Install all dependencies
python3 -m poetry install

# Optional: Install pre-commit hooks
python3 -m poetry run pre-commit install

# IDE configuration
# - Configure Black, Ruff, and mypy integration
# - Set up pytest runner
# - Enable type checking in editor
```

### Development Commands (Use These for This Project)

**Code Quality & Linting:**
```bash
# Run all pre-commit hooks (recommended)
python3 -m poetry run pre-commit run --all-files

# Individual commands (if needed)
python3 -m poetry run ruff check src/ tests/ --fix
python3 -m poetry run black src/ tests/
python3 -m poetry run mypy src/
```

**Testing:**
```bash
# Run all tests (with required environment variable)
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/ -v

# Run tests with coverage
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/ --cov=src --cov-report=html

# Run specific test file
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/database/test_models.py -v

# Run tests matching pattern
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/ -k "test_vector" -v

# Start development services for integration testing
docker-compose -f docker-compose.dev.yml up -d
```

**Application Commands:**
```bash
# Start development server
python3 -m poetry run uvicorn src.mindbridge.main:app --reload

# Start with custom host/port
python3 -m poetry run uvicorn src.mindbridge.main:app --host 0.0.0.0 --port 8080 --reload

# Run database migrations (when available)
python3 -m poetry run alembic upgrade head

# Generate new migration
python3 -m poetry run alembic revision --autogenerate -m "Description"
```

**Dependency Management:**
```bash
# Add new dependency
python3 -m poetry add package-name

# Add development dependency
python3 -m poetry add --group dev package-name

# Update dependencies
python3 -m poetry update

# Show dependency tree
python3 -m poetry show --tree
```

**Quality Gates (Run Before Commits):**
```bash
# Complete quality check pipeline
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/ --cov=src --cov-fail-under=85 && \
python3 -m poetry run pre-commit run --all-files
```

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost:5432/mindbridge
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
GITHUB_TOKEN=your-github-token
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
LOG_LEVEL=INFO
```

---

## Docker Deployment and Containerization

### Complete Docker Setup

The project includes a production-ready Docker Compose configuration with all services integrated and optimized for performance.

#### 🚀 **Automated Setup Script (Recommended)**

```bash
# One-command complete setup
./scripts/docker-setup.sh
```

This automated script performs:
- Builds all Docker images with optimized caching
- Starts PostgreSQL and Redis services with health checks
- Runs database migrations with all enhancements (pgvector, HNSW indexes, constraints)
- Starts the full application stack
- Verifies all services are healthy and operational

#### 🐳 **Manual Docker Setup Process**

```bash
# 1. Build and start database services first
docker-compose --env-file .env.docker up -d postgres redis

# 2. Wait for services to be healthy (check logs)
docker-compose --env-file .env.docker logs postgres
docker-compose --env-file .env.docker logs redis

# 3. Run database migrations (includes all performance optimizations)
docker-compose --env-file .env.docker run --rm -e PYTHONPATH=/app/src app alembic upgrade head

# 4. Start the complete application stack
docker-compose --env-file .env.docker up -d

# 5. Verify all services are running and healthy
docker-compose --env-file .env.docker ps
curl http://localhost:8000/health
```

#### 📊 **Docker Services Architecture**

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **API Application** | 8000 | FastAPI server with async processing | `/health` endpoint |
| **PostgreSQL + pgvector** | 5432 | Database with vector operations | `pg_isready` |
| **Redis** | 6379 | Cache and job queue | `PING` command |
| **Redis Insight** | 8001 | Redis management interface | Web UI |
| **Celery Worker** | - | Background job processing | Process monitoring |
| **Celery Beat** | - | Scheduled task management | Process monitoring |

#### 🔧 **Docker Environment Configuration**

The Docker setup uses `.env.docker` for environment-specific configuration:

```bash
# Database Configuration
POSTGRES_DB=mindbridge
POSTGRES_USER=mindbridge
POSTGRES_PASSWORD=docker-dev-password-123

# Redis Configuration
REDIS_PASSWORD=docker-redis-password-123

# Application Configuration
JWT_SECRET_KEY=docker-development-secret-key-256-bits-long
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8000
ENVIRONMENT=development
LOG_LEVEL=INFO

# Celery Configuration
CELERY_BROKER_URL=redis://:docker-redis-password-123@redis:6379/0
CELERY_RESULT_BACKEND=redis://:docker-redis-password-123@redis:6379/1
```

#### 🗄️ **Enhanced Database Features in Docker**

The containerized setup includes all production-ready database optimizations:

✅ **PostgreSQL 15 with pgvector Extension** - Vector similarity search capability
✅ **HNSW Vector Indexing** - 100-1000x faster vector similarity queries
✅ **Composite Database Indexes** - Optimized query performance for common patterns
✅ **Database-Level CHECK Constraints** - Data validation and integrity
✅ **Cascade Foreign Key Relationships** - Automatic cleanup and data consistency
✅ **Proper Enum Types** - Type safety and validation
✅ **Connection Pooling** - Efficient database connection management

#### 🔍 **Docker Management Commands**

**Service Management:**
```bash
# View service status and health
docker-compose --env-file .env.docker ps

# View real-time logs for specific services
docker-compose --env-file .env.docker logs -f app
docker-compose --env-file .env.docker logs -f postgres
docker-compose --env-file .env.docker logs -f redis
docker-compose --env-file .env.docker logs -f worker

# Stop all services
docker-compose --env-file .env.docker down

# Stop services and remove volumes (CAUTION: This removes all data)
docker-compose --env-file .env.docker down -v

# Restart specific service
docker-compose --env-file .env.docker restart app
```

**Database Operations:**
```bash
# Run database migrations manually
docker-compose --env-file .env.docker run --rm app alembic upgrade head

# Access PostgreSQL database directly
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge

# Check database schema and indexes
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge -c "
SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'public';
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'vector_documents';
"

# Backup database
docker-compose --env-file .env.docker exec postgres pg_dump -U mindbridge -d mindbridge > backup.sql
```

**Redis Operations:**
```bash
# Check Redis connectivity and performance
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 ping
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 info memory

# Monitor Redis operations
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 monitor

# Check connected clients and slow queries
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 client list
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 slowlog get 10

# Clear Redis cache (use with caution in development)
docker-compose --env-file .env.docker exec redis redis-cli -a docker-redis-password-123 flushdb
```

#### 🧪 **Docker Testing and Validation**

**API Testing:**
```bash
# Test all API endpoints
curl http://localhost:8000/health        # Health check
curl http://localhost:8000/docs          # Interactive API documentation
curl http://localhost:8000/redoc         # Alternative API documentation
curl http://localhost:8000/metrics       # Prometheus metrics

# Test with verbose output
curl -v http://localhost:8000/health
```

**Database Testing:**
```bash
# Validate vector operations in Docker
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge -c "
-- Insert test vector document
INSERT INTO vector_documents (content, title, embedding)
VALUES ('Docker test content for vector operations', 'Docker Vector Test',
        ARRAY(SELECT random() FROM generate_series(1, 1536))::vector);

-- Verify vector dimensions and operations
SELECT id, title, vector_dims(embedding) as dimensions
FROM vector_documents WHERE title = 'Docker Vector Test';

-- Test vector similarity search
SELECT id, title, 1 - (embedding <=> (SELECT embedding FROM vector_documents LIMIT 1)) as similarity
FROM vector_documents
ORDER BY embedding <=> (SELECT embedding FROM vector_documents LIMIT 1)
LIMIT 5;
"

# Clean up test data
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge -c "
DELETE FROM vector_documents WHERE title = 'Docker Vector Test';
"
```

**Performance Testing:**
```bash
# Load test API endpoints
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/health

# Monitor resource usage
docker stats --no-stream
docker-compose --env-file .env.docker exec postgres pg_stat_activity
```

#### 🔧 **Docker Troubleshooting**

**Common Issues and Solutions:**

**Issue: Services fail to start**
```bash
# Check service logs for errors
docker-compose --env-file .env.docker logs postgres
docker-compose --env-file .env.docker logs redis
docker-compose --env-file .env.docker logs app

# Restart problematic services
docker-compose --env-file .env.docker restart postgres redis
```

**Issue: Database connection errors**
```bash
# Verify database is healthy
docker-compose --env-file .env.docker exec postgres pg_isready -U mindbridge -d mindbridge

# Check connection from app container
docker-compose --env-file .env.docker exec app python -c "
import asyncpg
import asyncio
async def test_db():
    conn = await asyncpg.connect('postgresql://mindbridge:docker-dev-password-123@postgres:5432/mindbridge')
    result = await conn.fetchval('SELECT version();')
    print('Database connection successful:', result)
    await conn.close()
asyncio.run(test_db())
"
```

**Issue: Redis connection errors**
```bash
# Test Redis connectivity from app container
docker-compose --env-file .env.docker exec app python -c "
import redis
r = redis.Redis(host='redis', port=6379, password='docker-redis-password-123', decode_responses=True)
print('Redis PING response:', r.ping())
print('Redis info:', r.info('server')['redis_version'])
"
```

**Issue: Migration failures**
```bash
# Check migration status
docker-compose --env-file .env.docker run --rm app alembic current
docker-compose --env-file .env.docker run --rm app alembic history

# Reset and rerun migrations (CAUTION: Removes all data)
docker-compose --env-file .env.docker down -v
docker-compose --env-file .env.docker up -d postgres redis
docker-compose --env-file .env.docker run --rm app alembic upgrade head
```

#### 🚀 **Production Deployment Considerations**

**For Production Use:**
1. **Security**: Update all passwords and secrets in `.env.docker`
2. **Persistence**: Ensure proper volume mounting for data persistence
3. **Monitoring**: Set up log aggregation and metrics collection
4. **Backup**: Implement automated database backup strategies
5. **Resource Limits**: Configure appropriate CPU and memory limits
6. **Health Checks**: Monitor all service health endpoints
7. **TLS/SSL**: Configure HTTPS for production endpoints

**Performance Optimization:**
```bash
# Tune PostgreSQL for production
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
"

# Monitor query performance
docker-compose --env-file .env.docker exec postgres psql -U mindbridge -d mindbridge -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 10;
"
```

---

## Continuous Integration Requirements

### GitHub Actions Workflow
- All pushes and pull requests trigger CI pipeline
- CI must run: pre-commit hooks, tests
- All code quality checks (linting, type checking, formatting) are handled by pre-commit hooks
- Security scanning is handled by pre-commit hooks (bandit)
- PR requirements: CI passing, code review approval, no merge conflicts
- Automated deployment to staging on main branch pushes only

### Quality Gates
- Test coverage must be >= 85%
- All linting rules must pass
- No high-severity security vulnerabilities
- Documentation must be up-to-date
- All GitHub issue acceptance criteria must be met

### Recent CI/CD Improvements

**✅ Fixed Critical Issues:**
- Added missing `ALLOWED_ORIGINS` environment variable to CI workflow
- Fixed health check test mocking for async context managers
- Resolved tracing configuration test isolation issues
- Updated environment variable naming consistency (.env.example)

**✅ Local Development Infrastructure:**
- Created `docker-compose.dev.yml` for local PostgreSQL and Redis services
- Added working `.env` file template with correct variable names
- Fixed database initialization script to avoid referencing non-existent tables

**✅ Test Suite Status:**
- All 167 tests now pass consistently ✅
- Test coverage improved to 70%
- Fixed 8 previously failing tests
- Proper async mocking for database and Redis health checks

**✅ Developer Experience:**
```bash
# Quick local setup
docker-compose -f docker-compose.dev.yml up -d
ALLOWED_ORIGINS="http://localhost:3000,http://localhost:8080" \
python3 -m poetry run pytest tests/ -v
# All tests pass! 🎉
```

---

This CLAUDE.md file serves as the definitive guide for all development activities on the Agentic RAG Documentation System project. All team members must adhere to these standards without exception.
