---
id: ivm-20251012-204100
title: System Design — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-18
tags: [moc, topic/system-design]
date created: Saturday, October 18th 2025, 2:46:39 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# System Design — Map of Content

## Overview
This MOC covers system design principles, distributed systems, scalability, architecture patterns, caching strategies, database design, API design, and best practices for building large-scale systems.

**Total Questions**: 10 system design questions covering fundamentals to advanced topics.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "30-System-Design"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "30-System-Design"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "30-System-Design"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

## Study Paths

### Beginner Path
Start with fundamental concepts to build a strong foundation:

1. **Scalability Basics**
   - [[q-horizontal-vertical-scaling--system-design--medium]] - Horizontal vs vertical scaling
   - [[q-load-balancing-strategies--system-design--medium]] - Load balancing strategies

2. **Database Fundamentals**
   - [[q-sql-nosql-databases--system-design--medium]] - SQL vs NoSQL databases

3. **API Design**
   - [[q-rest-api-design-best-practices--system-design--medium]] - REST API design best practices

4. **Caching Basics**
   - [[q-caching-strategies--system-design--medium]] - Caching strategies overview

### Intermediate Path
Apply concepts to design complete systems:

1. **System Design Interview Practice**
   - [[q-design-url-shortener--system-design--medium]] - Design URL shortener (complete system)

2. **Async Communication**
   - [[q-message-queues-event-driven--system-design--medium]] - Message queues and event-driven architecture

3. **Distributed Systems Fundamentals**
   - [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem and trade-offs

### Advanced Path
Master complex distributed systems and architecture:

1. **Architecture Decisions**
   - [[q-microservices-vs-monolith--system-design--hard]] - Microservices vs monolith architecture

2. **Database Scalability**
   - [[q-database-sharding-partitioning--system-design--hard]] - Database sharding and partitioning

---

## Common Patterns

### Scalability Patterns
- **Horizontal Scaling**: Add more servers to distribute load
- **Vertical Scaling**: Add more resources (CPU, RAM) to existing servers
- **Load Balancing**: Distribute traffic across multiple servers
- **Sharding**: Split data across multiple databases
- **Caching**: Store frequently accessed data in memory
- **CDN**: Cache static content geographically close to users

### Reliability Patterns
- **Replication**: Duplicate data across multiple servers
- **Redundancy**: Have backup systems ready to take over
- **Health Checks**: Monitor service health and remove unhealthy instances
- **Circuit Breaker**: Prevent cascading failures
- **Retry with Backoff**: Retry failed requests with exponential backoff

### Communication Patterns
- **Synchronous**: REST APIs, gRPC (request-response)
- **Asynchronous**: Message queues, event streams (fire-and-forget)
- **Pub/Sub**: Publishers send events to multiple subscribers
- **Request-Reply**: Client waits for server response

### Data Patterns
- **Database per Service**: Each microservice owns its database
- **Event Sourcing**: Store all changes as sequence of events
- **CQRS**: Separate read and write models
- **Saga**: Distributed transactions across services

---

## By Subtopic

### Scalability & Architecture

**Key Questions** (Curated Learning Path):

#### Scaling Fundamentals
- [[q-horizontal-vertical-scaling--system-design--medium]] - Horizontal vs vertical scaling
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing strategies
- [[q-caching-strategies--system-design--medium]] - Caching strategies overview

#### Architecture Patterns
- [[q-microservices-vs-monolith--system-design--hard]] - Microservices vs monolith architecture
- [[q-message-queues-event-driven--system-design--medium]] - Message queues and event-driven architecture

#### Complete System Design
- [[q-design-url-shortener--system-design--medium]] - Design URL shortener (end-to-end)

**All Scalability Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "scalability") OR contains(tags, "architecture") OR contains(tags, "distributed-systems")
SORT difficulty ASC, file.name ASC
```

### Distributed Systems

**Key Questions** (Curated Learning Path):

#### Distributed System Fundamentals
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem and trade-offs
- [[q-message-queues-event-driven--system-design--medium]] - Message queues and event-driven architecture

#### Distributed Architecture
- [[q-microservices-vs-monolith--system-design--hard]] - Microservices vs monolith architecture

**Core Concepts to Master**:
- **CAP Theorem**: Consistency, Availability, Partition Tolerance trade-offs
- **Consensus Algorithms**: Paxos, Raft for distributed agreement
- **Eventual Consistency**: Accept temporary inconsistency for availability
- **Leader Election**: Choose coordinator in distributed system
- **Distributed Transactions**: 2PC, Saga pattern for cross-service transactions

**All Distributed Systems Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "distributed-systems") OR contains(tags, "consensus") OR contains(tags, "replication")
SORT difficulty ASC, file.name ASC
```

### Caching & Performance

**Key Questions** (Curated Learning Path):

#### Caching Fundamentals
- [[q-caching-strategies--system-design--medium]] - Caching strategies overview

#### Performance Optimization
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing strategies
- [[q-horizontal-vertical-scaling--system-design--medium]] - Horizontal vs vertical scaling

**Caching Strategies to Know**:
- **Cache-Aside (Lazy Loading)**: Application manages cache
- **Write-Through**: Write to cache and DB simultaneously
- **Write-Behind**: Write to cache, async write to DB
- **Refresh-Ahead**: Proactively refresh cache before expiry
- **Cache Eviction**: LRU, LFU, FIFO policies

**Cache Technologies**:
- **In-Memory**: Redis, Memcached
- **CDN**: CloudFlare, Akamai, CloudFront
- **Application-Level**: Local cache, distributed cache

**All Caching Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "caching") OR contains(tags, "performance") OR contains(tags, "cdn")
SORT difficulty ASC, file.name ASC
```

### Database Design

**Key Questions** (Curated Learning Path):

#### Database Selection
- [[q-sql-nosql-databases--system-design--medium]] - SQL vs NoSQL databases

#### Database Scalability
- [[q-database-sharding-partitioning--system-design--hard]] - Database sharding and partitioning

**Database Types**:
- **SQL (Relational)**: PostgreSQL, MySQL - ACID transactions, complex queries
- **NoSQL Document**: MongoDB, CouchDB - flexible schema
- **NoSQL Key-Value**: Redis, DynamoDB - fast lookups
- **NoSQL Column-Family**: Cassandra, HBase - write-heavy workloads
- **NoSQL Graph**: Neo4j, Amazon Neptune - relationship queries

**Scaling Strategies**:
- **Vertical Scaling**: Bigger server (limited)
- **Read Replicas**: Multiple read copies
- **Sharding**: Horizontal partitioning across servers
- **Partitioning**: Split table within same server

**All Database Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "databases") OR contains(tags, "data-modeling") OR contains(tags, "sharding")
SORT difficulty ASC, file.name ASC
```

### API Design

**Key Questions** (Curated Learning Path):

#### REST API Design
- [[q-rest-api-design-best-practices--system-design--medium]] - REST API design best practices

**API Design Principles**:
- **RESTful Design**: Use HTTP methods correctly (GET, POST, PUT, DELETE)
- **Versioning**: /v1/, /v2/ for backwards compatibility
- **Pagination**: Limit result sets for large collections
- **Rate Limiting**: Prevent abuse, protect backend
- **Authentication**: OAuth2, JWT, API keys
- **Idempotency**: Safe to retry (PUT, DELETE are idempotent)
- **Error Handling**: Meaningful HTTP status codes and error messages

**API Patterns**:
- **REST**: Resource-based, HTTP verbs
- **GraphQL**: Query language, client specifies data needs
- **gRPC**: Binary protocol, high performance
- **WebSocket**: Bi-directional, real-time communication

**All API Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "api") OR contains(tags, "rest") OR contains(tags, "graphql")
SORT difficulty ASC, file.name ASC
```

### System Design Interviews

**Complete System Design Examples**:

#### End-to-End Designs
- [[q-design-url-shortener--system-design--medium]] - Design URL shortener (complete example)

**System Design Interview Framework**:

1. **Requirements Clarification** (5 min)
   - Functional requirements: What features?
   - Non-functional requirements: Scale, latency, availability?
   - Constraints: Budget, timeline, team size?

2. **Capacity Estimation** (5 min)
   - Traffic: QPS (queries per second)
   - Storage: Data size over time
   - Bandwidth: Network throughput
   - Memory: Cache size needed

3. **API Design** (5 min)
   - Define endpoints
   - Request/response formats
   - Error handling

4. **Database Schema** (5 min)
   - Tables/collections
   - Relationships
   - Indexes

5. **High-Level Design** (10 min)
   - Draw architecture diagram
   - Components: Load balancer, app servers, databases, cache
   - Data flow

6. **Detailed Design** (15 min)
   - Deep dive into 2-3 components
   - Algorithms, data structures
   - Trade-offs and alternatives

7. **Scale & Optimize** (10 min)
   - Bottlenecks identification
   - Caching, sharding, replication
   - Monitoring, logging

**Tips for Success**:
- Think out loud - explain your reasoning
- Start simple, then optimize
- Discuss trade-offs (consistency vs availability)
- Ask clarifying questions
- Draw diagrams
- Consider failure scenarios
- Mention monitoring and metrics

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "30-System-Design"
SORT created DESC
LIMIT 10
```

---

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "30-System-Design"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "30-System-Design"
GROUP BY difficulty
SORT difficulty ASC
```

---

## Quick Reference: When to Use What

### Choose SQL When:
- ACID transactions required
- Complex joins and queries
- Structured, relational data
- Data integrity critical
- Examples: Banking, e-commerce orders

### Choose NoSQL When:
- High scalability needed
- Flexible schema required
- High write throughput
- Eventual consistency acceptable
- Examples: Social media feeds, IoT data, analytics

### Choose Microservices When:
- Large team (multiple teams)
- Independent scaling needed
- Polyglot persistence (different DBs)
- Frequent deployments
- Complex domain

### Choose Monolith When:
- Small team
- Simple domain
- Shared data model
- Starting new project
- Lower operational complexity

### Choose Message Queue When:
- Async processing needed
- Decouple services
- Handle traffic spikes
- Guaranteed delivery required
- Event-driven architecture

### Choose Caching When:
- Read-heavy workload (90%+ reads)
- Expensive computations
- Slow database queries
- Need low latency (<50ms)
- Limited write frequency

---

## Related MOCs
- [[moc-backend]] - Backend development and databases
- [[moc-cs]] - Computer science fundamentals
- [[moc-android]] - Android-specific architecture
- [[moc-kotlin]] - Kotlin for backend services
- [[moc-architecture-patterns]] - Architecture patterns (MVVM, MVI, Clean Architecture)

---

## Resources for Further Learning

**Books**:
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu (Vol 1 & 2)
- "Building Microservices" by Sam Newman

**Online Resources**:
- System Design Primer (GitHub)
- High Scalability Blog
- AWS Architecture Center
- Google Cloud Architecture Framework

**Practice Platforms**:
- LeetCode System Design
- Exponent.io
- Pramp (mock interviews)

---

**Total Questions in This MOC**: 10 covering all major system design topics
