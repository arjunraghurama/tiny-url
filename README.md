# 🔗 TinyURL — System Design Learning Project

A full-stack URL shortener built to learn **system design** concepts: caching, database design, API design, authentication, horizontal scaling, and trade-offs.

📖 **[Read the Documentation →](https://arjunraghurama.github.io/tiny-url)**

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React + Vite | Single-page URL shortening UI |
| Auth | Keycloak | OIDC identity provider (login/registration) |
| Backend | FastAPI (Python) | Async REST API with JWT validation |
| Cache | Valkey | Redis-compatible in-memory cache |
| Database | PostgreSQL | Persistent URL + user storage |
| Docs | Zensical | Documentation site (GitHub Pages) |

## Architecture

```
Browser → React (:5173) → Keycloak (:8080)  [OIDC login]
                         → FastAPI (:8000)   [REST API + JWT]
                              → Valkey (:6379)
                              → PostgreSQL (:5432)
```

- **Auth flow:** Keycloak OIDC → JWT access token → Bearer header on API calls → Backend validates via JWKS
- **Write path:** Authenticate → generate random code → insert into DB → cache in Valkey
- **Read path:** Check Valkey cache (~1ms) → fallback to PostgreSQL (~5-10ms) → 307 redirect

## Quick Start

```bash
# Start all services (including Keycloak)
docker compose up --build -d

# Access
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000/docs  (Swagger UI)
# Keycloak:  http://localhost:8080       (Admin: admin/admin)
```

### Test User

| Field | Value |
|---|---|
| Username | `testuser` |
| Password | `password` |

## Project Structure

```
tiny-url/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py          # App entrypoint, lifespan, CORS
│   │   ├── routes.py        # API endpoints (auth-protected)
│   │   ├── services.py      # URL shortening logic + user linking
│   │   ├── auth.py          # Keycloak JWT validation
│   │   ├── models.py        # SQLAlchemy models (User, URL)
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── cache.py         # Valkey cache client
│   │   ├── config.py        # App settings (incl. Keycloak)
│   │   └── database.py      # Async SQLAlchemy engine
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React + Vite app
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js           # Backend API client (with auth tokens)
│   │   ├── keycloak.js      # Keycloak instance config
│   │   ├── main.jsx         # Keycloak init → React render
│   │   ├── index.css        # Premium dark-mode styles
│   │   └── components/
│   │       ├── ShortenForm.jsx
│   │       ├── URLCard.jsx
│   │       ├── RecentURLs.jsx
│   │       └── UserMenu.jsx  # Login/logout/user info
│   └── Dockerfile
├── auth/
│   └── realm.json           # Keycloak realm config (auto-import)
├── docs/                    # Documentation (Zensical → GitHub Pages)
│   ├── index.md
│   ├── architecture.md
│   ├── authentication.md
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

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/shorten` | 🔒 Required | Create a short URL |
| `GET` | `/{short_code}` | 🌍 Public | Redirect to original URL |
| `GET` | `/api/urls/{short_code}/stats` | 🌍 Public | Get click statistics |
| `GET` | `/api/urls/recent` | ⚡ Optional | List recent URLs (user's when authenticated) |

## System Design Concepts Covered

- **Authentication** — Keycloak OIDC, JWT validation, protected endpoints
- **Random code generation** — cryptographically random alphanumeric codes (prevents enumeration)
- **Cache-aside pattern** — Valkey cache with TTL, graceful fallback to DB
- **Database indexing** — unique index on `short_code` for O(log n) lookups
- **Async I/O** — FastAPI + asyncpg for high concurrency
- **Horizontal scaling** — stateless backend, read replicas, sharding strategies
- **Design trade-offs** — SQL vs NoSQL, 301 vs 307, cache patterns compared

## License

[MIT](LICENSE)
