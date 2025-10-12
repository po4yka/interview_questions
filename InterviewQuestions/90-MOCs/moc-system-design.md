---
id: ivm-20251012-204100
title: System Design — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/system-design]
---

# System Design — Map of Content

## Overview
This MOC covers system design principles, distributed systems, scalability, architecture patterns, caching strategies, database design, API design, and best practices for building large-scale systems.

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

## By Subtopic

### Scalability & Architecture

**Key Questions**:

#### Scaling Strategies
- [[q-horizontal-vertical-scaling--system-design--medium]] - Horizontal vs vertical scaling
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing strategies
- [[q-microservices-vs-monolith--system-design--hard]] - Microservices vs monolith architecture

**All Scalability Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "scalability") OR contains(tags, "architecture") OR contains(tags, "distributed-systems")
SORT difficulty ASC, file.name ASC
```

### Distributed Systems

**Key Questions**:

#### Distributed System Fundamentals
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem and trade-offs
- [[q-message-queues-event-driven--system-design--medium]] - Message queues and event-driven architecture

**All Distributed Systems Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "distributed-systems") OR contains(tags, "consensus") OR contains(tags, "replication")
SORT difficulty ASC, file.name ASC
```

### Caching & Performance

**Key Questions**:

#### Caching Strategies
- [[q-caching-strategies--system-design--medium]] - Caching strategies overview

**All Caching Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "caching") OR contains(tags, "performance") OR contains(tags, "cdn")
SORT difficulty ASC, file.name ASC
```

### Database Design

**Key Questions**:

#### Database Selection
- [[q-sql-nosql-databases--system-design--medium]] - SQL vs NoSQL databases

**All Database Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "databases") OR contains(tags, "data-modeling") OR contains(tags, "sharding")
SORT difficulty ASC, file.name ASC
```

### API Design

**Key Questions**:

#### REST API Design
- [[q-rest-api-design-best-practices--system-design--medium]] - REST API design best practices

**All API Questions:**
```dataview
TABLE difficulty, status
FROM "30-System-Design"
WHERE contains(tags, "api") OR contains(tags, "rest") OR contains(tags, "graphql")
SORT difficulty ASC, file.name ASC
```

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

## Related MOCs
- [[moc-backend]]
- [[moc-compSci]]
- [[moc-android]]
