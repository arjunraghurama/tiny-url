# 🔗 TinyURL — System Design Learning Project

A full-stack URL shortener built to learn **system design** concepts: caching, database design, API design, horizontal scaling, and trade-offs.

📖 **[Read the Documentation →](https://arjunraghurama.github.io/tiny-url)**

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | Single-page URL shortening UI |
| Backend | FastAPI (Python) | Async REST API |
| Cache | Valkey | Redis-compatible in-memory cache |
| Database | PostgreSQL | Persistent URL storage |
| Docs | Zensical | Documentation site (GitHub Pages) |

## Architecture

```
Browser → React (:5173) → FastAPI (:8000) → Valkey (:6379)
                                           → PostgreSQL (:5432)
```

- **Write path:** Generate random alphanumeric code → insert into DB → cache in Valkey
- **Read path:** Check Valkey cache (~1ms) → fallback to PostgreSQL (~5-10ms) → 307 redirect

## Quick Start

```bash
# Start all services
docker compose up --build -d

# Access
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000/docs  (Swagger UI)
```

## Project Structure

```
tiny-url/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py          # App entrypoint, lifespan, CORS
│   │   ├── routes.py        # API endpoints
│   │   ├── services.py      # URL shortening logic
│   │   ├── models.py        # SQLAlchemy models (User, URL)
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── cache.py         # Valkey cache client
│   │   ├── config.py        # App settings
│   │   └── database.py      # Async SQLAlchemy engine
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js           # Backend API client
│   │   ├── index.css        # Premium dark-mode styles
│   │   └── components/
│   │       ├── ShortenForm.jsx
│   │       ├── URLCard.jsx
│   │       └── RecentURLs.jsx
│   └── Dockerfile
├── docs/                    # Documentation (Zensical → GitHub Pages)
│   ├── index.md
│   ├── architecture.md
│   ├── database-design.md
│   ├── caching-strategy.md
│   ├── api-design.md
│   ├── scaling.md
│   └── tradeoffs.md
├── docker-compose.yml
├── zensical.toml            # Docs site config
└── .github/workflows/docs.yml
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/shorten` | Create a short URL |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/api/urls/{short_code}/stats` | Get click statistics |
| `GET` | `/api/urls/recent` | List recent URLs |

## System Design Concepts Covered

- **Random code generation** — cryptographically random alphanumeric codes (prevents enumeration)
- **Cache-aside pattern** — Valkey cache with TTL, graceful fallback to DB
- **Database indexing** — unique index on `short_code` for O(log n) lookups
- **Async I/O** — FastAPI + asyncpg for high concurrency
- **Horizontal scaling** — stateless backend, read replicas, sharding strategies
- **Design trade-offs** — SQL vs NoSQL, 301 vs 307, cache patterns compared

## License

[MIT](LICENSE)
