---
id: cs-db-indexing
title: Database - Indexing
topic: database
difficulty: hard
tags:
- cs_database
- indexing
- performance
anki_cards:
- slug: cs-db-indexing-0-en
  language: en
  anki_id: 1769160676725
  synced_at: '2026-01-23T13:31:18.955992'
- slug: cs-db-indexing-0-ru
  language: ru
  anki_id: 1769160676749
  synced_at: '2026-01-23T13:31:18.957308'
- slug: cs-db-indexing-1-en
  language: en
  anki_id: 1769160676774
  synced_at: '2026-01-23T13:31:18.958749'
- slug: cs-db-indexing-1-ru
  language: ru
  anki_id: 1769160676800
  synced_at: '2026-01-23T13:31:18.960231'
- slug: cs-db-indexing-2-en
  language: en
  anki_id: 1769160676824
  synced_at: '2026-01-23T13:31:18.961834'
- slug: cs-db-indexing-2-ru
  language: ru
  anki_id: 1769160676849
  synced_at: '2026-01-23T13:31:18.965032'
---
# Database Indexing

## Index Basics

**Index**: Data structure that speeds up data retrieval at cost of storage and write performance.

**Analogy**: Book index - find topics without reading every page.

### Without Index

```
SELECT * FROM users WHERE email = 'john@example.com';

Full table scan: Check every row = O(n)
```

### With Index

```
Index lookup: O(log n) for B-tree
```

## B-Tree Index (Default)

Most common index type. Balanced tree structure.

```
                    [M]
                   /   \
              [D,H]     [R,W]
             /  |  \    /  |  \
          [A-C][E-G][I-L][N-Q][S-V][X-Z]
                              ^
                            Leaf nodes (point to data)
```

**Properties**:
- Balanced (all leaf nodes at same depth)
- O(log n) search, insert, delete
- Good for equality and range queries
- Sorted data enables ordered traversal

**Best for**:
- Equality: WHERE id = 5
- Range: WHERE age BETWEEN 20 AND 30
- Sorting: ORDER BY created_at
- Prefix search: WHERE name LIKE 'John%'

**Not good for**:
- Suffix search: WHERE name LIKE '%son'
- Functions on column: WHERE YEAR(created_at) = 2024

## Hash Index

Hash table structure.

**Properties**:
- O(1) average lookup
- Only supports equality (=)
- No range queries
- No ordering

```sql
-- PostgreSQL
CREATE INDEX idx_email_hash ON users USING HASH (email);
```

**Best for**: Exact match lookups only.

## Index Types

### Primary Index (Clustered)

Table data physically ordered by this index. Only one per table.

```sql
-- Primary key creates clustered index
CREATE TABLE users (
    id INT PRIMARY KEY,  -- Clustered index
    email VARCHAR(255)
);
```

### Secondary Index (Non-clustered)

Separate structure pointing to data. Can have many per table.

```sql
CREATE INDEX idx_email ON users(email);
```

### Unique Index

Enforces uniqueness constraint.

```sql
CREATE UNIQUE INDEX idx_email ON users(email);
```

### Composite Index (Multi-column)

Index on multiple columns.

```sql
CREATE INDEX idx_name ON users(last_name, first_name);
```

**Column order matters!** Index usable for:
- WHERE last_name = 'Smith'
- WHERE last_name = 'Smith' AND first_name = 'John'

**Not usable for**:
- WHERE first_name = 'John' (leftmost column not used)

### Covering Index

Index contains all columns needed for query (no table lookup).

```sql
-- Query
SELECT email, created_at FROM users WHERE status = 'active';

-- Covering index
CREATE INDEX idx_covering ON users(status, email, created_at);
```

### Partial Index (Filtered Index)

Index only subset of rows.

```sql
-- PostgreSQL
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- SQL Server
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

### Full-Text Index

For text search.

```sql
-- PostgreSQL
CREATE INDEX idx_search ON articles USING GIN(to_tsvector('english', content));

-- MySQL
CREATE FULLTEXT INDEX idx_search ON articles(title, content);
```

## Index Selection Guidelines

### When to Index

1. **Primary keys** (automatic)
2. **Foreign keys** (frequently joined)
3. **Columns in WHERE clauses**
4. **Columns in ORDER BY**
5. **Columns in GROUP BY**
6. **High cardinality columns** (many unique values)

### When NOT to Index

1. **Small tables** (scan is fast enough)
2. **Low cardinality** (e.g., boolean, status with few values)
3. **Frequently updated columns** (index maintenance overhead)
4. **Columns rarely used in queries**

## Query Execution Plan

### EXPLAIN

```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'john@example.com';

-- Output
Index Scan using idx_email on users  (cost=0.29..8.31 rows=1)
  Index Cond: (email = 'john@example.com')
  Actual time: 0.025..0.026 rows=1 loops=1
```

### Scan Types

| Scan Type | Description | Performance |
|-----------|-------------|-------------|
| Index Scan | Use index, fetch rows | Good |
| Index Only Scan | Data from index only | Best |
| Bitmap Index Scan | Build bitmap, then scan | Good for ranges |
| Sequential Scan | Full table scan | Avoid for large tables |

### Why Index Not Used?

1. **Low selectivity**: Most rows match (scan faster)
2. **Function on column**: WHERE UPPER(name) = 'JOHN'
3. **Type mismatch**: WHERE id = '5' (string vs int)
4. **LIKE with leading wildcard**: WHERE name LIKE '%son'
5. **OR conditions**: May require multiple indexes
6. **Outdated statistics**: Run ANALYZE

## Index Maintenance

### Index Bloat

Deleted rows leave gaps. Rebuild periodically.

```sql
-- PostgreSQL
REINDEX INDEX idx_email;

-- Or rebuild
DROP INDEX idx_email;
CREATE INDEX idx_email ON users(email);
```

### Statistics

Query planner uses statistics for decisions.

```sql
-- PostgreSQL
ANALYZE users;

-- SQL Server
UPDATE STATISTICS users;
```

## Advanced Concepts

### Index Intersection

Multiple indexes combined for single query.

```sql
-- Query uses both indexes
SELECT * FROM users WHERE status = 'active' AND country = 'US';

-- Indexes
CREATE INDEX idx_status ON users(status);
CREATE INDEX idx_country ON users(country);
```

### Index-Organized Tables (IOT)

Table stored as index structure (clustered by design).

### Write Amplification

Each index adds write overhead.

```
INSERT into table with 5 indexes:
- 1 write to table
- 5 writes to indexes
= 6 total writes
```

## Best Practices

1. **Start with query patterns**: Index based on actual queries
2. **Monitor slow queries**: Identify missing indexes
3. **Review EXPLAIN plans**: Verify index usage
4. **Limit index count**: Balance read vs write performance
5. **Use composite indexes wisely**: Order columns by selectivity
6. **Consider covering indexes**: For frequent queries
7. **Maintain indexes**: Rebuild bloated indexes

## Interview Questions

1. **How does a B-tree index work?**
   - Balanced tree with sorted keys
   - O(log n) operations
   - Leaf nodes point to data
   - Good for equality and range

2. **Why might an index not be used?**
   - Low selectivity
   - Function on column
   - Wrong data type
   - Leading wildcard
   - Outdated statistics

3. **What is a covering index?**
   - Index contains all query columns
   - No table lookup needed
   - Faster because data in index

4. **Composite index column order?**
   - Most selective column first
   - Must use leftmost columns
   - Consider query patterns
