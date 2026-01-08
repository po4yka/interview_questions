---\
id: ivm-20251012-140400
title: Backend — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-18
tags: [moc, topic/backend]
---\

# Backend — Map of Content

## Overview
This MOC covers backend development topics including databases, SQL, APIs, server-side architecture, performance optimization, caching, scalability, security, and backend system design.

## Study Paths

### Beginner Path: Backend Fundamentals
Start with database basics, SQL fundamentals, and simple API concepts. Focus on understanding relational databases, basic queries, and REST API principles.

**Topics to cover:**
1. **`Database` Fundamentals**
   - Relational database concepts
   - Primary keys, unique constraints, foreign keys
   - Basic table design and normalization
   - [[q-relational-table-unique-data--backend--medium]] - Storing unique data

2. **SQL Basics**
   - SELECT, INSERT, UPDATE, DELETE operations
   - Basic JOIN operations
   - WHERE clauses and filtering
   - Simple aggregations (COUNT, SUM, AVG)

3. **REST API Basics**
   - HTTP methods (GET, POST, PUT, DELETE)
   - Status codes and error handling
   - Request/response structure
   - Basic authentication

4. **`Database` Management**
   - [[q-database-migration-purpose--backend--medium]] - `Database` migrations
   - Schema evolution and versioning
   - Backup and restore basics

### Intermediate Path: Query Optimization & API Design
Build on fundamentals with query optimization, advanced SQL, API design patterns, and caching strategies.

**Topics to cover:**
1. **Query Optimization**
   - [[q-sql-join-algorithms-complexity--backend--hard]] - JOIN algorithms and complexity
   - Index design and usage
   - Query execution plans
   - Performance profiling

2. **Advanced SQL**
   - Subqueries and CTEs (Common Table Expressions)
   - `Window` functions
   - Stored procedures and functions
   - Triggers and constraints

3. **Views & Virtual Tables**
   - [[q-virtual-tables-disadvantages--backend--medium]] - Virtual tables and views
   - Materialized views
   - `View` optimization strategies

4. **API Design Patterns**
   - RESTful API best practices
   - API versioning strategies
   - Pagination, filtering, sorting
   - Rate limiting and throttling

5. **Caching Strategies**
   - Cache invalidation patterns
   - Redis basics
   - Cache-aside, write-through patterns
   - CDN and edge caching

### Advanced Path: Scalability & Distributed Systems
Master database scaling, distributed transactions, microservices architecture, and high-availability systems.

**Topics to cover:**
1. **`Database` Scaling**
   - Read replicas and replication
   - Sharding strategies (horizontal/vertical)
   - Partitioning techniques
   - Multi-region databases

2. **Distributed Transactions**
   - ACID vs BASE consistency models
   - Two-phase commit (2PC)
   - Saga pattern for distributed transactions
   - Event sourcing and CQRS

3. **Microservices Architecture**
   - `Service` decomposition strategies
   - Inter-service communication (sync/async)
   - `Service` discovery and load balancing
   - Circuit breakers and resilience patterns

4. **High Availability & Reliability**
   - Failover and disaster recovery
   - `Database` clustering
   - Connection pooling optimization
   - Health checks and monitoring

5. **Performance at Scale**
   - `Database` connection optimization
   - Batch processing strategies
   - Asynchronous processing patterns
   - `Queue`-based architectures

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "50-Backend"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "50-Backend"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "50-Backend"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### Databases

**Key Questions** (Curated Learning `Path`):

#### Database Fundamentals (Start Here)
- [[q-relational-table-unique-data--backend--medium]] - Storing unique data with primary keys and constraints
- [[q-database-migration-purpose--backend--medium]] - `Database` migrations and schema evolution
- Understanding relational vs non-relational databases
- CRUD operations and basic SQL syntax
- Data types and constraints (NOT NULL, CHECK, DEFAULT)

#### Database Design & Normalization
- Normalization forms (1NF, 2NF, 3NF, BCNF)
- Denormalization strategies for performance
- `Entity`-Relationship (ER) modeling
- Foreign key relationships and referential integrity
- Composite keys vs surrogate keys

#### Views & Virtual Tables
- [[q-virtual-tables-disadvantages--backend--medium]] - Virtual tables and their limitations
- Regular views vs materialized views
- `View` performance characteristics
- Using views for abstraction and security
- Updatable views and restrictions

#### Indexes & Performance Optimization
- Index types (B-tree, Hash, GiST, GIN)
- Composite index strategies
- Index selectivity and cardinality
- Covering indexes and index-only scans
- When NOT to use indexes
- Index maintenance and statistics updates

#### Query Execution & Planning
- Understanding EXPLAIN and EXPLAIN ANALYZE
- Query optimizer cost estimation
- Table scan vs index scan vs bitmap scan
- Join strategies and reordering
- Sequential vs parallel query execution
- Query plan caching

#### Transactions & Concurrency Control
- ACID properties detailed (Atomicity, Consistency, Isolation, Durability)
- Transaction isolation levels (Read Uncommitted, Read Committed, Repeatable Read, `Serializable`)
- Lock types (row-level, table-level, advisory locks)
- Pessimistic vs optimistic locking
- Deadlock detection, prevention, and resolution
- MVCC (Multi-Version Concurrency Control) mechanisms

#### Database Types & Selection Criteria
- Relational databases (PostgreSQL, MySQL, SQL Server)
- Document databases (MongoDB, CouchDB)
- Key-value stores (Redis, DynamoDB)
- Column-family stores (Cassandra, HBase)
- Time-series databases (InfluxDB, TimescaleDB)
- Graph databases (Neo4j, ArangoDB)
- When to use each type

#### Connection Management & Pooling
- Connection pooling benefits
- Pool sizing strategies
- Connection lifecycle management
- Prepared statements and query caching
- Connection timeout configuration

**All `Database` Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "database") OR contains(tags, "databases") OR contains(subtopics, "databases")
SORT difficulty ASC, file.name ASC
```

### SQL & Query Optimization

**Key Questions** (Curated Learning `Path`):

#### SQL Basics & Syntax
- SELECT statements and projection
- WHERE clause filtering
- ORDER BY and sorting
- LIMIT and OFFSET for pagination
- DISTINCT for unique results

#### JOIN Operations
- [[q-sql-join-algorithms-complexity--backend--hard]] - JOIN algorithms and complexity (Nested Loop, Hash Join, Sort-Merge)
- INNER JOIN vs OUTER JOIN (LEFT, RIGHT, FULL)
- CROSS JOIN and Cartesian products
- Self-joins for hierarchical data
- JOIN ordering and query optimization
- Multiple table joins

#### Aggregations & Grouping
- Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- GROUP BY clause
- HAVING vs WHERE
- Grouping sets and ROLLUP
- `Window` functions for running totals

#### Subqueries & CTEs
- Scalar subqueries
- Correlated vs non-correlated subqueries
- IN, EXISTS, ANY, ALL operators
- Common Table Expressions (WITH clause)
- Recursive CTEs for hierarchical queries

#### Advanced SQL Features
- `Window` functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD)
- CASE expressions and conditional logic
- COALESCE and NULL handling
- `String` manipulation functions
- Date/time functions and operations
- JSON and array operations (PostgreSQL)

#### Query Optimization Techniques
- Index usage analysis
- Avoiding SELECT * in production
- Minimizing subqueries
- Using EXISTS instead of IN for large datasets
- Batch operations vs row-by-row processing
- Query hints and optimizer directives

#### Performance Analysis
- Reading EXPLAIN output
- Identifying slow queries
- Query cost estimation
- Analyzing index usage statistics
- Monitoring query execution time
- Query plan stability

#### Stored Procedures & Functions
- Creating stored procedures
- Function types (scalar, table-valued)
- Parameter passing (IN, OUT, INOUT)
- Error handling in procedures
- Transaction management in procedures
- Performance implications

**All SQL Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "sql") OR contains(tags, "query-optimization") OR contains(file.name, "sql")
SORT difficulty ASC, file.name ASC
```

### APIs & Web Services

**Key Questions** (Curated Learning `Path`):

#### REST API Fundamentals
- HTTP methods (GET, POST, PUT, PATCH, DELETE)
- HTTP status codes (2xx, 3xx, 4xx, 5xx)
- RESTful resource design
- URL structure and naming conventions
- Request/response headers
- Content negotiation (JSON, XML)

#### REST API Design Best Practices
- Resource naming conventions
- Idempotency in API design
- HATEOAS (Hypermedia as the Engine of `Application` State)
- API versioning strategies (URL, header, media type)
- Pagination techniques (offset-based, cursor-based)
- Filtering, sorting, and searching
- Partial responses and field selection

#### API Authentication & Authorization
- Basic Authentication
- Token-based authentication (JWT)
- OAuth 2.0 flows (Authorization Code, Client Credentials, Implicit, Password)
- API keys and secrets management
- Session-based vs stateless authentication
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)

#### GraphQL
- GraphQL vs REST comparison
- Schema definition and type system
- Queries, mutations, and subscriptions
- Resolvers and data fetching
- N+1 problem and DataLoader pattern
- Error handling in GraphQL
- GraphQL federation and schema stitching

#### API Performance & Optimization
- Rate limiting strategies (token bucket, leaky bucket, fixed window, sliding window)
- Throttling and backpressure
- `Response` compression (gzip, Brotli)
- Caching strategies (ETags, Cache-Control headers)
- API gateway patterns
- Connection pooling for backend services

#### API Documentation & Standards
- OpenAPI/Swagger specifications
- API documentation best practices
- Request/response examples
- Error response formats
- API changelog and versioning
- Interactive API documentation

#### Error Handling & Resilience
- Error response formats (Problem Details RFC 7807)
- Retry strategies with exponential backoff
- Circuit breaker pattern
- Timeout configuration
- Graceful degradation
- Health check endpoints

#### WebSockets & Real-Time APIs
- WebSocket protocol basics
- `Long` polling vs Server-Sent Events (SSE) vs WebSockets
- Real-time data streaming
- Connection management and heartbeats
- Scaling WebSocket connections

**All API Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "api") OR contains(tags, "rest") OR contains(tags, "graphql") OR contains(tags, "web-services")
SORT difficulty ASC, file.name ASC
```

### Performance & Optimization

**Key Questions** (Curated Learning `Path`):

#### Performance Measurement
- Identifying performance bottlenecks
- `Application` Performance Monitoring (APM) tools
- Profiling CPU and memory usage
- `Database` query profiling
- Network latency measurement
- Load testing and stress testing

#### Database Performance
- Query optimization techniques
- Index selection and tuning
- Connection pooling configuration
- `Database` replication for read scaling
- Partitioning and sharding strategies
- Query result caching

#### Application Performance
- Code-level optimization
- Algorithm complexity reduction
- Memory management and garbage collection
- `Thread` pool sizing
- Asynchronous processing patterns
- Lazy loading and eager loading trade-offs

#### Caching Strategies
- Cache levels (browser, CDN, application, database)
- Cache invalidation patterns (TTL, write-through, write-behind)
- Cache-aside pattern
- Read-through and write-through caching
- Distributed caching with Redis/Memcached
- Cache stampede prevention

#### Response Time Optimization
- `Response` compression (gzip, Brotli)
- Minimizing payload size
- Reducing number of requests
- HTTP/2 and HTTP/3 benefits
- Server-side rendering vs client-side rendering
- Progressive rendering techniques

#### Batch Processing & Background Jobs
- Async job processing with queues
- Job scheduling and cron patterns
- Batch vs stream processing
- `Worker` pool management
- Job retry and failure handling
- Priority queues for job ordering

#### CDN & Edge Computing
- Content Delivery Network benefits
- Static asset optimization
- Edge caching strategies
- Geographic distribution
- Cache purging strategies
- Origin shield patterns

**All Performance Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(subtopics, "performance")
SORT difficulty ASC, file.name ASC
```

### Caching & Data Storage

**Key Questions** (Curated Learning `Path`):

#### Cache Fundamentals
- What is caching and why use it
- Cache hit ratio and miss ratio
- Cache warm-up strategies
- Cache eviction policies (LRU, LFU, FIFO)
- Cache coherence and consistency

#### Caching Patterns
- Cache-aside (lazy loading)
- Read-through caching
- Write-through caching
- Write-behind (write-back) caching
- Refresh-ahead caching
- Cache invalidation strategies

#### Distributed Caching
- Redis fundamentals and data structures
- Memcached vs Redis
- Cache partitioning and sharding
- Consistent hashing for cache distribution
- Cache replication for high availability
- Cache failover strategies

#### Redis Advanced Topics
- Redis data structures (strings, lists, sets, sorted sets, hashes, bitmaps)
- Redis pub/sub for messaging
- Redis streams for event processing
- Redis transactions and pipelines
- Redis persistence (RDB, AOF)
- Redis cluster and sentinel

#### File Storage & Object Storage
- Local filesystem vs distributed storage
- Object storage (S3, GCS, Azure Blob)
- Block storage vs object storage
- File upload strategies
- Multipart upload for large files
- Signed URLs for secure access

#### Session Management
- Session storage options (memory, database, cache)
- Distributed session management
- Sticky sessions vs session replication
- JWT for stateless sessions
- Session expiration and renewal

**All Caching & Storage Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "caching") OR contains(tags, "redis") OR contains(tags, "storage")
SORT difficulty ASC, file.name ASC
```

### Security

**Key Questions** (Curated Learning `Path`):

#### Authentication Fundamentals
- Username/password authentication
- Multi-factor authentication (MFA)
- Biometric authentication
- Password hashing (bcrypt, Argon2, PBKDF2)
- Salt and pepper in password storage
- Session-based authentication
- Token-based authentication (JWT)

#### Authorization & Access Control
- Role-Based Access Control (RBAC)
- Attribute-Based Access Control (ABAC)
- Permission models and hierarchies
- Principle of least privilege
- Access control lists (ACLs)
- OAuth 2.0 and OpenID Connect
- API key management

#### Common Web Vulnerabilities
- SQL injection prevention
- Cross-Site Scripting (XSS) prevention
- Cross-Site `Request` Forgery (CSRF) protection
- Server-Side `Request` Forgery (SSRF)
- XML External `Entity` (XXE) attacks
- Command injection prevention
- `Path` traversal vulnerabilities

#### Secure Communication
- HTTPS and TLS/SSL
- Certificate management
- Man-in-the-middle attack prevention
- Certificate pinning
- HSTS (HTTP Strict Transport Security)
- Perfect forward secrecy

#### Data Protection
- Encryption at rest
- Encryption in transit
- Key management and rotation
- Secrets management (Vault, AWS Secrets Manager)
- PII (Personally Identifiable Information) handling
- GDPR and data privacy compliance
- Data masking and tokenization

#### API Security
- API authentication mechanisms
- Rate limiting for DoS protection
- Input validation and sanitization
- Output encoding
- CORS (Cross-Origin Resource Sharing) configuration
- API versioning for security patches
- Security headers (CSP, X-Frame-Options, etc.)

#### Security Best Practices
- Secure coding practices
- Security audits and penetration testing
- Dependency vulnerability scanning
- Security logging and monitoring
- Incident response planning
- Security patching strategies

**All Security Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "security") OR contains(tags, "authentication") OR contains(tags, "authorization")
SORT difficulty ASC, file.name ASC
```

### Scalability & Architecture

**Key Questions** (Curated Learning `Path`):

#### Horizontal Vs Vertical Scaling
- Vertical scaling (scale-up) benefits and limits
- Horizontal scaling (scale-out) strategies
- Auto-scaling based on metrics
- Stateless vs stateful services
- Load balancing algorithms
- `Service` discovery mechanisms

#### Database Scaling Strategies
- Read replicas for read scaling
- Write scaling with sharding
- `Database` partitioning (horizontal, vertical, functional)
- Consistent hashing for data distribution
- Multi-master replication
- Cross-region replication

#### Microservices Architecture
- Monolith vs microservices trade-offs
- `Service` decomposition strategies
- Domain-Driven Design (DDD) and bounded contexts
- Inter-service communication (REST, gRPC, message queues)
- `Service` mesh (Istio, Linkerd)
- API gateway patterns
- Backend for Frontend (BFF) pattern

#### Message Queues & Event-Driven Architecture
- `Message` queue benefits (RabbitMQ, Kafka, SQS)
- Publisher-subscriber pattern
- Event sourcing pattern
- Command Query Responsibility Segregation (CQRS)
- Saga pattern for distributed transactions
- Dead letter queues
- `Message` ordering and idempotency

#### Load Balancing & High Availability
- Load balancer types (L4 vs L7)
- Load balancing algorithms (round-robin, least connections, IP hash)
- Health checks and circuit breakers
- Failover and redundancy strategies
- Active-active vs active-passive configurations
- Disaster recovery and backup strategies
- Multi-region deployments

#### Distributed Systems Concepts
- CAP theorem (Consistency, Availability, Partition tolerance)
- BASE vs ACID consistency models
- Eventual consistency
- Distributed consensus (Paxos, Raft)
- Two-phase commit (2PC) and three-phase commit (3PC)
- Clock synchronization and vector clocks
- Distributed tracing and observability

#### Caching for Scalability
- Multi-level caching strategies
- Cache invalidation at scale
- Distributed cache consistency
- Cache warming and preloading
- Cache stampede prevention
- CDN for global content delivery

#### Containerization & Orchestration
- Docker containerization benefits
- Container orchestration with Kubernetes
- `Service` deployment strategies (blue-green, canary, rolling)
- Resource limits and requests
- Pod autoscaling (HPA, VPA)
- StatefulSets for stateful applications

**All Scalability Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "scalability") OR contains(tags, "architecture") OR contains(tags, "distributed-systems")
SORT difficulty ASC, file.name ASC
```

### Transactions & Consistency

**Key Questions** (Curated Learning `Path`):

#### Transaction Fundamentals
- ACID properties detailed (Atomicity, Consistency, Isolation, Durability)
- Transaction lifecycle (BEGIN, COMMIT, ROLLBACK)
- Savepoints and nested transactions
- Transaction logs and WAL (Write-Ahead Logging)
- Transaction performance considerations

#### Isolation Levels
- Read Uncommitted (dirty reads possible)
- Read Committed (prevents dirty reads)
- Repeatable Read (prevents non-repeatable reads)
- `Serializable` (full isolation, prevents phantom reads)
- Isolation level trade-offs (performance vs consistency)
- Default isolation levels by database

#### Concurrency Control
- Pessimistic locking (read/write locks)
- Optimistic locking (versioning)
- Two-Phase Locking (2PL)
- Multi-Version Concurrency Control (MVCC)
- Lock granularity (row-level, page-level, table-level)
- Lock escalation and deadlock prevention

#### Deadlocks
- Deadlock conditions (mutual exclusion, hold and wait, no preemption, circular wait)
- Deadlock detection strategies
- Deadlock prevention techniques
- Deadlock resolution (victim selection)
- Timeout-based deadlock handling

#### Distributed Transactions
- Two-Phase Commit (2PC) protocol
- Three-Phase Commit (3PC)
- Compensating transactions
- Saga pattern for long-running transactions
- Transaction coordinator role
- Handling partial failures

#### Consistency Models
- Strong consistency
- Eventual consistency
- Causal consistency
- Read-your-writes consistency
- Monotonic reads and monotonic writes
- Session consistency

#### BASE Vs ACID
- BASE (Basically Available, Soft state, Eventually consistent)
- ACID vs BASE trade-offs
- When to choose ACID vs BASE
- CAP theorem implications
- Consistency guarantees in NoSQL databases

#### Conflict Resolution
- Last-write-wins (LWW)
- Version vectors and vector clocks
- Conflict-free Replicated Data Types (CRDTs)
- `Application`-level conflict resolution
- Merge strategies for concurrent updates

**All Transaction Questions:**
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "transactions") OR contains(tags, "acid") OR contains(tags, "consistency")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "50-Backend"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "50-Backend"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-system-design]]
- [[moc-kotlin]]
- [[moc-compSci]]
