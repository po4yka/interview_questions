---
id: moc-backend-20251006
title: Backend & Databases — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [moc, backend, databases]
---

# Backend & Databases — Map of Content

Welcome to the backend and database knowledge base! This covers databases, SQL, APIs, and backend architecture.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "50-Backend"
WHERE file.name != "moc-backend"
GROUP BY difficulty
SORT difficulty ASC
```

---

## All Questions

### Easy Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "50-Backend"
WHERE difficulty = "easy" AND file.name != "moc-backend"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "50-Backend"
WHERE difficulty = "medium" AND file.name != "moc-backend"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "50-Backend"
WHERE difficulty = "hard" AND file.name != "moc-backend"
SORT file.name ASC
```

---

## By Category

### Databases — SQL

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "sql") OR contains(tags, "database") OR contains(tags, "relational")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

### Databases — NoSQL

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "nosql") OR contains(tags, "mongodb") OR contains(tags, "redis")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

### Database Design

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "schema") OR contains(tags, "normalization") OR contains(tags, "indexes")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

### Database Operations

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "migration") OR contains(tags, "transactions") OR contains(tags, "optimization")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

### APIs

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "api") OR contains(tags, "rest") OR contains(tags, "graphql")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

### Backend Architecture

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "50-Backend"
WHERE contains(tags, "architecture") OR contains(tags, "microservices") OR contains(tags, "scalability")
    AND file.name != "moc-backend"
SORT difficulty ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "50-Backend"
WHERE file.name != "moc-backend"
SORT created DESC
LIMIT 10
```

---

## Study Path

### Database Fundamentals

Essential database concepts:

1. **SQL Basics**: SELECT, JOIN, WHERE, GROUP BY
2. **Database Design**: Normalization, relationships
3. **Indexing**: Performance optimization
4. **Transactions**: ACID properties

### Backend Development

API and server-side development:

1. **RESTful APIs**: HTTP methods, status codes
2. **Database Integration**: ORMs, query optimization
3. **Authentication**: JWT, OAuth
4. **Caching**: Redis, in-memory caching

### Advanced Backend

Scalability and architecture:

1. **Microservices**: Service design, communication
2. **Scaling**: Horizontal vs vertical, load balancing
3. **Database Scaling**: Sharding, replication
4. **Performance**: Query optimization, caching strategies

---

## Related MOCs

- [[moc-android]] - Android data persistence (Room, DataStore)
- [[moc-architecture-patterns]] - Backend architecture patterns

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "50-Backend"
WHERE file.name != "moc-backend"
```
