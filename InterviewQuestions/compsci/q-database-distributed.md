---
id: cs-db-distributed
title: Database - Distributed Databases
topic: database
difficulty: hard
tags:
- cs_database
- distributed_systems
anki_cards:
- slug: cs-db-dist-0-en
  language: en
  anki_id: 1769160676475
  synced_at: '2026-01-23T13:31:18.938938'
- slug: cs-db-dist-0-ru
  language: ru
  anki_id: 1769160676499
  synced_at: '2026-01-23T13:31:18.940119'
- slug: cs-db-dist-1-en
  language: en
  anki_id: 1769160676524
  synced_at: '2026-01-23T13:31:18.941465'
- slug: cs-db-dist-1-ru
  language: ru
  anki_id: 1769160676548
  synced_at: '2026-01-23T13:31:18.942932'
---
# Distributed Databases

## CAP Theorem

In distributed system, can only guarantee 2 of 3:

- **Consistency**: All nodes see same data at same time
- **Availability**: Every request gets response
- **Partition tolerance**: System works despite network failures

**Reality**: Must choose P (partitions happen), so choose between C and A.

### CA, CP, AP Systems

| Type | Sacrifice | Example |
|------|-----------|---------|
| CA | Partition tolerance | Traditional RDBMS (single node) |
| CP | Availability | MongoDB, HBase, Redis Cluster |
| AP | Consistency | Cassandra, DynamoDB, CouchDB |

## Consistency Models

### Strong Consistency

All reads see most recent write. Like single node.

**Pros**: Easy to reason about.
**Cons**: High latency, reduced availability.

### Eventual Consistency

Given no new updates, all replicas converge eventually.

**Pros**: High availability, low latency.
**Cons**: May read stale data.

```
Write to Node A: x = 1
Read from Node B: x = 0 (stale)
... time passes ...
Read from Node B: x = 1 (converged)
```

### Read Your Writes

Client always sees their own writes.

### Monotonic Reads

Once you read a value, you won't see older value.

### Causal Consistency

If A causes B, everyone sees A before B.

## Replication

### Single Leader (Master-Slave)

```
    [Master] <-- Writes
       |
   +---+---+
   |       |
[Slave] [Slave] <-- Reads
```

**Pros**: Simple, no write conflicts.
**Cons**: Master is bottleneck, failover complexity.

### Multi-Leader

```
[Leader A] <--> [Leader B] <--> [Leader C]
    |              |              |
[Replica]     [Replica]      [Replica]
```

**Pros**: Writes to any leader, geo-distribution.
**Cons**: Conflict resolution needed.

### Leaderless (Quorum)

```
Write to W nodes
Read from R nodes
If W + R > N, guaranteed to read latest

Example: N=3, W=2, R=2
Write to 2/3 nodes
Read from 2/3 nodes
At least 1 node has latest
```

**Pros**: High availability, no single point of failure.
**Cons**: Complex conflict resolution.

## Sharding (Partitioning)

Split data across multiple nodes.

### Horizontal Partitioning

Split by rows (most common).

```
Shard 1: users A-M
Shard 2: users N-Z
```

### Vertical Partitioning

Split by columns.

```
Users table -> users_basic (id, name, email)
            -> users_profile (id, bio, avatar)
```

### Sharding Strategies

**Range-based**:
```
Shard by ID range: 1-1M, 1M-2M, etc.
Pros: Simple, range queries efficient
Cons: Hotspots if skewed access
```

**Hash-based**:
```
Shard = hash(key) % num_shards
Pros: Even distribution
Cons: Range queries require all shards
```

**Consistent Hashing**:
```
Keys and nodes on hash ring
Minimizes reshuffling when nodes added/removed
Used by Cassandra, DynamoDB
```

### Sharding Challenges

1. **Cross-shard joins**: Expensive, avoid if possible
2. **Transactions**: Distributed transactions are hard
3. **Resharding**: Adding shards requires data movement
4. **Hotspots**: Uneven distribution

## NoSQL Databases

### Document Stores

Store JSON/BSON documents. Schema flexible.

**Examples**: MongoDB, CouchDB

```json
{
  "id": 1,
  "name": "John",
  "orders": [
    {"id": 101, "total": 50},
    {"id": 102, "total": 75}
  ]
}
```

**Best for**: Variable schema, nested data, rapid development.

### Key-Value Stores

Simple get/put by key.

**Examples**: Redis, DynamoDB, Memcached

```
SET user:1 "{name: 'John'}"
GET user:1
```

**Best for**: Caching, sessions, simple lookups.

### Wide-Column Stores

Tables with dynamic columns per row.

**Examples**: Cassandra, HBase, BigTable

```
Row key: user1
  Column family 'profile':
    name: 'John'
    email: 'john@example.com'
  Column family 'orders':
    order_1: {...}
    order_2: {...}
```

**Best for**: Time series, analytics, large scale.

### Graph Databases

Nodes and relationships.

**Examples**: Neo4j, Amazon Neptune

```
(User)-[:FRIENDS_WITH]->(User)
(User)-[:PURCHASED]->(Product)
```

**Best for**: Social networks, recommendations, fraud detection.

## SQL vs NoSQL

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| Schema | Fixed | Flexible |
| Scaling | Vertical (mostly) | Horizontal |
| Transactions | ACID | Usually eventual |
| Query language | SQL | Varies |
| Joins | Yes | Limited/none |
| Best for | Complex queries, consistency | Scale, flexibility |

## ACID vs BASE

| ACID | BASE |
|------|------|
| Atomicity | Basically Available |
| Consistency | Soft state |
| Isolation | Eventual consistency |
| Durability | |

**BASE**: Prioritizes availability over consistency.

## Normalization vs Denormalization

### Normalized (SQL approach)

```sql
users:     id, name
orders:    id, user_id, total
items:     id, order_id, product_id, qty

-- Requires joins
SELECT u.name, o.total
FROM users u JOIN orders o ON u.id = o.user_id;
```

**Pros**: No redundancy, easier updates.
**Cons**: Requires joins, slower reads.

### Denormalized (NoSQL approach)

```json
{
  "user_id": 1,
  "user_name": "John",
  "orders": [
    {"total": 50, "items": [...]},
    {"total": 75, "items": [...]}
  ]
}
```

**Pros**: Fast reads, no joins.
**Cons**: Data duplication, harder updates.

## Interview Questions

1. **What is CAP theorem?**
   - Can only have 2 of: Consistency, Availability, Partition tolerance
   - Partitions happen, so choose C or A
   - CP: Strong consistency, may be unavailable
   - AP: Always available, may be inconsistent

2. **When to use SQL vs NoSQL?**
   - SQL: Complex queries, ACID needed, relationships
   - NoSQL: Scale, flexible schema, simple access patterns

3. **What is sharding?**
   - Split data across multiple nodes
   - Horizontal scaling
   - Challenges: cross-shard queries, transactions

4. **What is eventual consistency?**
   - All replicas converge given no new updates
   - May read stale data temporarily
   - Trade-off for availability and performance
