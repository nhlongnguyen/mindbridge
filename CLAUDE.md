# Midnbridge - Agentic RAG Documentation System

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

---

## Code Style and Linting

### Community Standards (Strictly Enforced)
- **Code Formatter**: Black with line length 88
- **Import Sorter**: isort with Black compatibility
- **Linter**: Ruff (replaces flake8, pylint, isort, and more)
- **Type Checker**: mypy with strict mode enabled

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml (must be used)
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

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

### Task Management Rules (Strictly Enforced)

**GitHub Project Integration:**
- All development work must be tracked in GitHub Projects
- Tasks must be created as GitHub Issues with proper labels
- Use project board columns: Backlog, In Progress, Review, Done
- Link all commits and PRs to their respective issues

**Task Workflow (Mandatory Process):**

1. **Fetch Task**: Retrieve task from GitHub Projects board
2. **Understand Requirements**: Analyze issue description, acceptance criteria, and dependencies
3. **Create Implementation Plan**: Provide detailed technical plan in issue comments
4. **Plan Review**: Wait for plan approval before starting implementation
5. **Create Feature Branch**: Create and switch to a new feature branch using format `feature/R-XXX-description`
6. **Update Task Status**: Mark GitHub issue as "in progress" using GitHub CLI
7. **TDD Implementation**: Write tests first, then implement functionality
8. **Quality Gates**: Ensure all tests pass and linting rules are satisfied
9. **Commit Changes**: Stage and commit all changes with descriptive commit message
10. **Create Pull Request**: Push branch and create PR with detailed description linking to issue
11. **Status Updates**: Update GitHub issue status throughout development

### Implementation Workflow

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
- Check linting: `python3 -m poetry run ruff check src/ tests/ --fix`
- Format code: `python3 -m poetry run black src/ tests/`
- Type checking: `python3 -m poetry run mypy src/`
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
# Lint and auto-fix issues
python3 -m poetry run ruff check src/ --fix
python3 -m poetry run ruff check tests/ --fix

# Format code
python3 -m poetry run black src/ tests/

# Type checking
python3 -m poetry run mypy src/

# Run all quality checks
python3 -m poetry run ruff check src/ --fix && \
python3 -m poetry run black src/ tests/ && \
python3 -m poetry run mypy src/
```

**Testing:**
```bash
# Run all tests
python3 -m poetry run pytest tests/ -v

# Run tests with coverage
python3 -m poetry run pytest tests/ --cov=src --cov-report=html

# Run specific test file
python3 -m poetry run pytest tests/database/test_models.py -v

# Run tests matching pattern
python3 -m poetry run pytest tests/ -k "test_vector" -v
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
python3 -m poetry run ruff check src/ tests/ --fix && \
python3 -m poetry run black src/ tests/ && \
python3 -m poetry run mypy src/ && \
python3 -m poetry run pytest tests/ --cov=src --cov-fail-under=85
```

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost:5432/mindbridge
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
GITHUB_TOKEN=your-github-token
LOG_LEVEL=INFO
```

---

## Continuous Integration Requirements

### GitHub Actions Workflow
- All pushes must trigger CI pipeline
- CI must run: tests, linting, type checking, security scanning
- PR requirements: CI passing, code review approval, no merge conflicts
- Automated deployment to staging on main branch updates

### Quality Gates
- Test coverage must be >= 85%
- All linting rules must pass
- No high-severity security vulnerabilities
- Documentation must be up-to-date
- All GitHub issue acceptance criteria must be met

---

This CLAUDE.md file serves as the definitive guide for all development activities on the Agentic RAG Documentation System project. All team members must adhere to these standards without exception.
