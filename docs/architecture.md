# 🏗️ System Architecture

## High-Level Architecture

The system follows a **3-tier architecture** with a caching layer:

```mermaid
graph TB
    subgraph Client Layer
        A["🌐 Browser"]
    end

    subgraph Frontend
        B["⚛️ React App<br/>Vite Dev Server :5173"]
    end

    subgraph Backend
        C["⚡ FastAPI<br/>Application :8000"]
    end

    subgraph Data Layer
        D["🔴 Valkey Cache<br/>:6379"]
        E["🐘 PostgreSQL<br/>:5432"]
    end

    A -->|"HTTP"| B
    B -->|"REST API"| C
    C -->|"Cache-Aside"| D
    C -->|"Async SQLAlchemy"| E
```

## Request Flow

### Write Path (Create Short URL)

When a user shortens a URL, the request flows through the system like this:

```mermaid
sequenceDiagram
    participant U as User
    participant R as React Frontend
    participant F as FastAPI Backend
    participant P as PostgreSQL
    participant V as Valkey Cache

    U->>R: Paste long URL & click "Shorten"
    R->>F: POST /api/shorten {"url": "https://..."}
    F->>F: generate_short_code() → "kX9mBzQ"
    F->>P: SELECT id FROM urls WHERE short_code='kX9mBzQ'
    P-->>F: null (no collision)
    F->>P: INSERT INTO urls (original_url, short_code='kX9mBzQ')
    F->>V: SET url:kX9mBzQ = "https://..." (TTL: 1hr)
    F-->>R: {"short_url": "http://localhost:8000/kX9mBzQ"}
    R-->>U: Display short URL with copy button
```

### Read Path (Redirect)

When someone visits a short URL, the system uses the **cache-aside pattern**:

```mermaid
sequenceDiagram
    participant U as User
    participant F as FastAPI Backend
    participant V as Valkey Cache
    participant P as PostgreSQL

    U->>F: GET /kX9mBzQ

    F->>V: GET url:kX9mBzQ
    
    alt Cache Hit ⚡ (~1ms)
        V-->>F: "https://original-url.com"
    else Cache Miss 🐢 (~5-10ms)
        V-->>F: null
        F->>P: SELECT * FROM urls WHERE short_code = "kX9mBzQ"
        P-->>F: URL record
        F->>V: SET url:kX9mBzQ = "https://..." (repopulate cache)
    end

    F->>P: UPDATE urls SET clicks = clicks + 1
    F-->>U: 307 Redirect → https://original-url.com
```

## Component Responsibilities

| Component | Responsibility | Why This Choice? |
|---|---|---|
| **React + Vite** | UI for URL shortening and history | Fast HMR, modern DX, simple SPA |
| **FastAPI** | REST API, business logic, routing | Async-native, automatic OpenAPI docs, fast |
| **PostgreSQL** | Persistent URL storage, click tracking | ACID compliance, reliable, great indexing |
| **Valkey** | Cache hot URLs, reduce DB load | Redis-compatible, sub-millisecond lookups |
| **Docker Compose** | Orchestrate all services | One command to start everything |

## Communication Patterns

### Frontend ↔ Backend
- **Protocol:** HTTP/REST
- **Format:** JSON
- **CORS:** Enabled for `localhost:5173`

### Backend ↔ Cache (Valkey)
- **Pattern:** Cache-Aside (Lazy Loading)
- **Protocol:** Redis protocol (RESP)
- **Connection:** Async via `valkey-py`
- **TTL:** 1 hour per entry

### Backend ↔ Database (PostgreSQL)
- **ORM:** SQLAlchemy 2.0 (async)
- **Driver:** asyncpg (fastest PostgreSQL driver for Python)
- **Connection Pool:** Managed by SQLAlchemy engine

## Docker Compose Network

All services communicate over a shared Docker bridge network:

```mermaid
graph LR
    subgraph Docker Network
        FE["frontend :5173"]
        BE["backend :8000"]
        DB["postgres :5432"]
        CA["valkey :6379"]
        DO["docs :8001"]
    end

    FE -->|"API calls"| BE
    BE -->|"queries"| DB
    BE -->|"cache ops"| CA

    style FE fill:#818cf8,color:#fff
    style BE fill:#34d399,color:#fff
    style DB fill:#60a5fa,color:#fff
    style CA fill:#f87171,color:#fff
    style DO fill:#fbbf24,color:#000
```

!!! info "Service Dependencies"
    The backend waits for PostgreSQL and Valkey to be healthy before starting, ensuring database tables are created before serving requests.
