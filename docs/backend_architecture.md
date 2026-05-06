# Backend Architecture Documentation

## Overview

This backend follows **Clean Architecture** principles with a feature-based modular design. The architecture enforces separation of concerns, dependency inversion, and SOLID principles to ensure maintainability, testability, and scalability.

## Architecture Layers

### 1. **Router Layer** (`router.py`)
- **Responsibility**: HTTP endpoint definitions and routing
- **Dependencies**: Controller layer only
- **No business logic**: Purely handles HTTP concerns
- **Location**: `modules/<module_name>/router.py`

### 2. **Controller Layer** (`controller.py`)
- **Responsibility**: Request validation, response formatting, dependency injection
- **Dependencies**: Service layer, core dependencies
- **No business logic**: Orchestrates service calls
- **Location**: `modules/<module_name>/controller.py`

### 3. **Service Layer** (`service.py`)
- **Responsibility**: Business logic, orchestration, external service integration
- **Dependencies**: Repository layer, core services (OpenAI, S3, Redis)
- **No database access**: Uses repositories for data access
- **Location**: `modules/<module_name>/service.py`

### 4. **Repository Layer** (`repository.py`)
- **Responsibility**: Database operations, data access
- **Dependencies**: Database models only
- **No business logic**: Pure CRUD operations
- **Location**: `modules/<module_name>/repository.py`

### 5. **Model Layer** (`models.py`)
- **Responsibility**: Database schema definitions (SQLAlchemy models)
- **Dependencies**: Database Base
- **No business logic**: Pure data structures
- **Location**: `modules/<module_name>/models.py`

### 6. **Schema Layer** (`schemas.py`)
- **Responsibility**: Pydantic models for request/response validation
- **Dependencies**: None (or models for type hints)
- **No business logic**: Pure validation
- **Location**: `modules/<module_name>/schemas.py`

## Dependency Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        HTTP Request                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Router Layer (router.py)                                   │
│  - Route definitions                                        │
│  - HTTP methods                                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Controller Layer (controller.py)                            │
│  - Request validation                                       │
│  - Response formatting                                      │
│  - Dependency injection                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Service Layer (service.py)                                 │
│  - Business logic                                           │
│  - Orchestration                                            │
│  - External service integration                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Repository Layer (repository.py)                            │
│  - Database operations                                      │
│  - CRUD operations                                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL)                                       │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

Each module follows this standardized structure:

```
modules/
├── auth/
│   ├── __init__.py
│   ├── controller.py
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── models.py
│   ├── schemas.py
│   └── tests/
│       ├── __init__.py
│       ├── test_router.py
│       ├── test_service.py
│       └── test_repository.py
├── document/
│   └── (same structure)
├── chatbot/
│   └── (same structure)
├── media/
│   └── (same structure)
├── summarization/
│   └── (same structure)
├── playback/
│   └── (same structure)
└── vector_search/
    └── (same structure)
```

## Core Infrastructure

The `core/` directory contains shared infrastructure:

```
core/
├── __init__.py
├── config.py          # Application settings (via config/settings.py)
├── security.py        # JWT, password hashing
├── dependencies.py    # Shared dependency injection
├── exceptions.py      # Custom exception classes
├── logging.py         # Logging configuration
├── openai_client.py   # OpenAI API integration
├── redis_client.py    # Redis integration
├── s3_client.py       # AWS S3 integration
└── rate_limiting.py   # Rate limiting logic
```

## Database Layer

The `database/` directory contains database infrastructure:

```
database/
├── __init__.py
├── base.py            # SQLAlchemy Base
├── session.py         # Database session management
└── init_db.py         # Database initialization
```

## Key Architectural Principles

### 1. **Dependency Inversion**
- High-level modules (controllers, services) don't depend on low-level modules (repositories)
- Both depend on abstractions (interfaces, where defined)
- Dependencies flow inward, not outward

### 2. **Single Responsibility**
- Each layer has a single, well-defined responsibility
- No business logic in routers or controllers
- No database access in services

### 3. **Open/Closed Principle**
- Modules are open for extension (new modules can be added)
- Closed for modification (existing modules don't need changes)
- Plugin-style architecture for new features

### 4. **Interface Segregation**
- Services implement specific interfaces (where defined)
- No forced dependencies on unused methods
- Clean contracts between layers

### 5. **Dependency Injection**
- All dependencies injected via FastAPI's `Depends`
- Centralized in `core/dependencies.py`
- Easy to mock for testing

## Cross-Module Communication

Modules communicate through:
1. **Repository imports**: Services can import repositories from other modules (e.g., chatbot service imports document repository)
2. **Model imports**: For type hints and database relationships
3. **No direct service-to-service calls**: Services should not directly call other services (use repositories instead)

## Anti-Patterns to Avoid

### ❌ **Forbidden Patterns**
- Business logic in routers
- Database access in controllers
- Direct database access in services (use repositories)
- Circular imports between modules
- Global state (use dependency injection)
- Tight coupling between modules

### ✅ **Correct Patterns**
- Controllers orchestrate service calls
- Services use repositories for data access
- Repositories perform database operations
- All dependencies injected
- Modules communicate through well-defined interfaces

## Scalability Considerations

### Horizontal Scaling
- Stateless services (FastAPI)
- Session management via Redis
- Database connection pooling
- S3 for file storage

### Vertical Scaling
- Async operations for I/O-bound tasks
- Background tasks for long-running operations
- Caching via Redis
- Vector search with FAISS

### Future Extensibility
- Easy to add new modules
- Plugin-style architecture
- Interface-driven design enables swapping implementations
- Microservice-ready (modules can be extracted)

## Testing Strategy

### Unit Tests
- Test each layer in isolation
- Mock dependencies
- Located in `modules/<module>/tests/`

### Integration Tests
- Test module interactions
- Use test database
- Test API endpoints

### Test Coverage Target
- ≥95% coverage for production code
- Critical paths: 100% coverage

## Configuration Management

- Environment-based configuration via `.env`
- Centralized in `config/settings.py`
- Type-safe with Pydantic
- No hardcoded secrets

## Security Considerations

- JWT-based authentication
- Password hashing with bcrypt
- User isolation in repositories
- Input validation via Pydantic schemas
- Rate limiting enabled by default

## Performance Optimizations

- Database connection pooling
- Redis caching for frequently accessed data
- Async I/O for external API calls
- Vector search with FAISS
- Batch operations for bulk data

## Monitoring and Logging

- Structured logging via `core/logging.py`
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error tracking with context

## Deployment Considerations

- Docker-ready (Dockerfile included)
- Environment variable configuration
- Health check endpoint (`/health`)
- Graceful shutdown handling
- Database migrations via Alembic

## Module-Specific Notes

### Auth Module
- Handles user registration, login, JWT tokens
- Password hashing with bcrypt
- User isolation enforced

### Document Module
- File upload handling (PDF, audio, video)
- S3 integration for storage
- PDF text extraction and chunking
- Document status tracking

### Chatbot Module
- RAG (Retrieval-Augmented Generation)
- Streaming responses
- Chat history management
- Vector search integration

### Media Module
- Audio/video transcription via OpenAI Whisper
- Transcript segmentation
- Timestamp management
- Playback support

### Summarization Module
- Document summarization
- Caching for performance
- Auto vs on-demand summaries
- Content aggregation

### Playback Module
- Media playback with timestamps
- Transcript synchronization
- S3 presigned URLs
- Playback session tracking

### Vector Search Module
- FAISS-based vector search
- OpenAI embeddings
- Chunk indexing
- Similarity search

## Conclusion

This architecture provides a solid foundation for:
- **Maintainability**: Clear separation of concerns
- **Testability**: Each layer can be tested independently
- **Scalability**: Stateless services, horizontal scaling ready
- **Extensibility**: Easy to add new modules and features
- **Reliability**: Type-safe, validated, well-structured code

The clean architecture ensures the codebase remains manageable as it grows, while following industry best practices for FastAPI applications.
