# AI Teddy v5 - Architecture Documentation

## Layer Structure:
- **Domain**: Business logic, entities, value objects
- **Application**: Use cases, services, DTOs
- **Infrastructure**: External services, persistence, security
- **Presentation**: API endpoints, websockets

## Key Principles:
- Domain layer has no external dependencies
- Application orchestrates domain logic
- Infrastructure implements interfaces
- Presentation handles HTTP/WebSocket concerns

## Module Organization:
- Each service has clear responsibility
- No circular dependencies between layers
- Interfaces defined in higher layers
- Implementation in lower layers

