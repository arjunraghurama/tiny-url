# 📈 Scaling

## Current Architecture (Single Server)

Our current setup runs on a single machine:

```mermaid
graph LR
    A["👤 Users"] --> B["FastAPI<br/>Single Instance"]
    B --> C["PostgreSQL<br/>Single Instance"]
    B --> D["Valkey<br/>Single Instance"]
```

**Capacity:** ~1,000-5,000 requests/second on modern hardware.

But what happens when you go viral and need to handle **100K+ requests/second**?

## Scaling Strategy

### Step 1: Horizontal API Scaling

Add a **load balancer** in front of multiple FastAPI instances:

```mermaid
graph TD
    A["👤 Users"] --> LB["⚖️ Load Balancer<br/>Nginx / AWS ALB"]
    LB --> F1["FastAPI #1"]
    LB --> F2["FastAPI #2"]
    LB --> F3["FastAPI #3"]
    F1 --> V["Valkey"]
    F2 --> V
    F3 --> V
    F1 --> DB["PostgreSQL"]
    F2 --> DB
    F3 --> DB
```

!!! tip "Why this works"
    Our FastAPI instances are **stateless** — they don't store any session data. Any instance can handle any request, making horizontal scaling straightforward.

### Step 2: Read Replicas

Database reads (redirects) far outnumber writes (URL creation). Add **read replicas**:

```mermaid
graph TD
    F["FastAPI Instances"] -->|"Writes"| P["PostgreSQL Primary"]
    F -->|"Reads"| R1["PostgreSQL Replica 1"]
    F -->|"Reads"| R2["PostgreSQL Replica 2"]
    P -->|"Replication"| R1
    P -->|"Replication"| R2
```

| Operation | Database | Ratio |
|---|---|---|
| `POST /api/shorten` | Primary | ~1% |
| `GET /{short_code}` | Replica | ~99% |

### Step 3: Cache Clustering

Scale Valkey with a **cluster** or **replica set**:

```mermaid
graph LR
    F["FastAPI"] --> VS["Valkey Sentinel"]
    VS --> VM["Valkey Primary"]
    VS --> VR1["Valkey Replica 1"]
    VS --> VR2["Valkey Replica 2"]
```

### Step 4: Database Sharding

At massive scale (billions of URLs), shard by **short_code**:

```mermaid
graph TD
    F["FastAPI"] --> R["Shard Router"]
    R -->|"a-m"| S1["Shard 1<br/>PostgreSQL"]
    R -->|"n-z"| S2["Shard 2<br/>PostgreSQL"]
    R -->|"A-Z, 0-9"| S3["Shard 3<br/>PostgreSQL"]
```

**Sharding strategies:**

| Strategy | How | Pros | Cons |
|---|---|---|---|
| Range-based | a-m → Shard 1 | Simple | Uneven distribution |
| Hash-based | `hash(code) % N` | Even distribution | Hard to add shards |
| **Consistent Hashing** | Hash ring | Even + easy rebalancing | More complex |

## Consistent Hashing

The gold standard for distributed systems:

```mermaid
graph TD
    subgraph Hash Ring
        direction TB
        H0["Position 0°"]
        H90["Position 90°"]
        H180["Position 180°"]
        H270["Position 270°"]
    end

    S1["Shard A"] -.-> H0
    S2["Shard B"] -.-> H90
    S3["Shard C"] -.-> H180

    K1["Key: abc123"] -->|"Clockwise to nearest shard"| S2
    K2["Key: xyz789"] -->|"Clockwise to nearest shard"| S3
```

**Why consistent hashing?**

- Adding/removing a shard only moves **K/N** keys (K = total keys, N = shards)
- Compare with hash-based: adding a shard moves **~all** keys
- Used by: DynamoDB, Cassandra, Discord, and most CDNs

## Rate Limiting

Prevent abuse with rate limiting:

```mermaid
flowchart TD
    A["Incoming Request"] --> B{"Rate Limit<br/>Check"}
    B -->|"Under limit"| C["Process Request"]
    B -->|"Over limit"| D["429 Too Many Requests"]
    
    style C fill:#34d399,color:#000
    style D fill:#f87171,color:#000
```

**Common algorithms:**

| Algorithm | Description | Use Case |
|---|---|---|
| Fixed Window | Count requests per time window | Simple, some edge cases |
| Sliding Window | Rolling count over time | More accurate |
| Token Bucket | Refill tokens at fixed rate | Allow bursts |
| Leaky Bucket | Process at fixed rate | Smooth traffic |

## Scaling Checklist

| Scale | Users | Strategy |
|---|---|---|
| **Hobby** | < 1K/day | Single server (current setup) |
| **Startup** | < 100K/day | Horizontal API + Valkey |
| **Growth** | < 1M/day | + Read replicas + CDN |
| **Scale** | < 100M/day | + Sharding + Rate limiting |
| **Massive** | 1B+/day | Multi-region + Consistent hashing |

## Additional Considerations

### CDN for Redirects
For global users, put a CDN (CloudFlare, CloudFront) in front to cache redirects at the edge.

### Analytics Pipeline
At scale, move click tracking to an **async pipeline** (Kafka → analytics DB) to avoid slowing down redirects.

### URL Expiration
Add a background job to clean up expired URLs and free up short codes for reuse.
