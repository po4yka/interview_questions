---
id: ivm-20251012-140400
title: Backend — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/backend]
---

# Backend — Map of Content

## Overview
This MOC covers backend development topics including databases, SQL, APIs, server-side architecture, performance optimization, caching, scalability, security, and backend system design.

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
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "database") OR contains(tags, "databases") OR contains(subtopics, "databases")
SORT difficulty ASC, file.name ASC
```

### SQL & Query Optimization
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "sql") OR contains(tags, "query-optimization") OR contains(file.name, "sql")
SORT difficulty ASC, file.name ASC
```

### APIs & Web Services
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "api") OR contains(tags, "rest") OR contains(tags, "graphql") OR contains(tags, "web-services")
SORT difficulty ASC, file.name ASC
```

### Performance & Optimization
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(subtopics, "performance")
SORT difficulty ASC, file.name ASC
```

### Caching & Data Storage
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "caching") OR contains(tags, "redis") OR contains(tags, "storage")
SORT difficulty ASC, file.name ASC
```

### Security
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "security") OR contains(tags, "authentication") OR contains(tags, "authorization")
SORT difficulty ASC, file.name ASC
```

### Scalability & Architecture
```dataview
TABLE difficulty, status
FROM "50-Backend"
WHERE contains(tags, "scalability") OR contains(tags, "architecture") OR contains(tags, "distributed-systems")
SORT difficulty ASC, file.name ASC
```

### Transactions & Consistency
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
