# Frontend Service Conventions

## Interface Naming: snake_case vs camelCase

This project uses a deliberate split:

- **API interfaces** (request/response types): Use `snake_case` property names to match the Python backend JSON exactly. No transformation layer is needed -- interfaces map 1:1 to API payloads.

- **Internal UI models** (e.g., `TableColumn`, `TableAction`): Use standard TypeScript `camelCase`.

This means `Employee.badge_number` is snake_case (API field), while `TableColumn.sortable` is camelCase (UI-only).

### Why not convert to camelCase?

Adding an HTTP interceptor or mapper to auto-convert between snake_case and camelCase was considered and rejected:

- Adds runtime overhead and an abstraction layer for no functional benefit
- The 1:1 mapping makes API debugging straightforward (interface fields match network payloads)
- Internal models already use camelCase where appropriate
