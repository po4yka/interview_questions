---
id: cs-arch-memory
title: Computer Architecture - Memory Hierarchy
topic: computer_architecture
difficulty: medium
tags:
- cs_architecture
- memory
- cache
anki_cards:
- slug: cs-arch-mem-0-en
  language: en
  anki_id: 1769160676024
  synced_at: '2026-01-23T13:31:18.908247'
- slug: cs-arch-mem-0-ru
  language: ru
  anki_id: 1769160676050
  synced_at: '2026-01-23T13:31:18.909561'
- slug: cs-arch-mem-1-en
  language: en
  anki_id: 1769160676075
  synced_at: '2026-01-23T13:31:18.911081'
- slug: cs-arch-mem-1-ru
  language: ru
  anki_id: 1769160676100
  synced_at: '2026-01-23T13:31:18.912774'
---
# Memory Hierarchy

## Memory Hierarchy Overview

```
          Speed    Size     Cost
            ^        ^        ^
            |        |        |
Registers  [=]      [.]      [$$$]
L1 Cache   [=]      [..]     [$$]
L2 Cache   [==]     [....]   [$$]
L3 Cache   [===]    [......] [$]
RAM        [====]   [..........] [cents]
SSD        [=====]  [...................] [.]
HDD        [======] [...........................] [.]
```

| Level | Typical Size | Latency | Bandwidth |
|-------|--------------|---------|-----------|
| L1 Cache | 32-64 KB | ~1 ns | ~100 GB/s |
| L2 Cache | 256 KB - 1 MB | ~4 ns | ~50 GB/s |
| L3 Cache | 2-32 MB | ~12 ns | ~30 GB/s |
| RAM | 8-128 GB | ~100 ns | ~25 GB/s |
| SSD | 256 GB - 4 TB | ~100 us | ~3 GB/s |
| HDD | 1-20 TB | ~10 ms | ~150 MB/s |

## Cache Basics

**Cache**: Fast memory storing frequently accessed data.

**Cache line**: Unit of transfer (typically 64 bytes).

**Hit**: Data found in cache.
**Miss**: Data not in cache, fetch from lower level.

**Hit rate**: % of accesses found in cache.

## Cache Organization

### Direct-Mapped Cache

Each memory address maps to one cache line.

```
Address: [Tag | Index | Offset]

Index selects cache line
Tag verifies correct data
Offset selects byte within line
```

**Conflict miss**: Two addresses map to same line.

### Set-Associative Cache

Each address maps to a set of N lines (N-way associative).

```
Address: [Tag | Set Index | Offset]

2-way: Each set has 2 lines
4-way: Each set has 4 lines
```

**More ways = fewer conflict misses, higher latency**.

### Fully Associative Cache

Address can be in any line. Requires searching all tags.

**No conflict misses, expensive to implement**.

## Cache Policies

### Replacement Policy

Which line to evict on miss?

| Policy | Description | Performance |
|--------|-------------|-------------|
| LRU | Least Recently Used | Good, expensive |
| Pseudo-LRU | Approximation | Good, cheaper |
| Random | Random selection | Okay, simple |
| FIFO | First In First Out | Poor |

### Write Policy

**Write-through**: Write to cache and memory immediately.
- Simple, consistent
- More memory traffic

**Write-back**: Write to cache only, write to memory on eviction.
- Less memory traffic
- Requires dirty bit
- More complex

### Write-Allocate

On write miss:
- **Write-allocate**: Load line, then write
- **No-write-allocate**: Write directly to memory

## Locality Principles

### Temporal Locality

Recently accessed data likely accessed again.

```python
# Good temporal locality
for i in range(1000):
    x = a[0]  # Same location accessed repeatedly
```

### Spatial Locality

Data near recently accessed data likely accessed.

```python
# Good spatial locality
for i in range(1000):
    x = a[i]  # Sequential access, same cache line
```

### Improving Locality

```python
# Bad locality (column-major access)
for j in range(n):
    for i in range(n):
        sum += matrix[i][j]

# Good locality (row-major access)
for i in range(n):
    for j in range(n):
        sum += matrix[i][j]
```

## Cache Misses

### Three C's

**Compulsory (Cold)**: First access to data.

**Capacity**: Cache too small for working set.

**Conflict**: Multiple addresses map to same set.

### Solutions

| Miss Type | Solution |
|-----------|----------|
| Compulsory | Prefetching |
| Capacity | Larger cache |
| Conflict | Higher associativity |

## Prefetching

Load data before it's needed.

**Hardware prefetching**: CPU detects access patterns.

**Software prefetching**: Explicit prefetch instructions.

```c
// Software prefetch
for (int i = 0; i < n; i++) {
    __builtin_prefetch(&a[i + 16]);  // Prefetch ahead
    sum += a[i];
}
```

## Memory Alignment

Data should be aligned to its size for efficient access.

```c
struct Bad {
    char a;     // 1 byte
    // 7 bytes padding
    double b;   // 8 bytes
    char c;     // 1 byte
    // 7 bytes padding
};  // 24 bytes total

struct Good {
    double b;   // 8 bytes
    char a;     // 1 byte
    char c;     // 1 byte
    // 6 bytes padding
};  // 16 bytes total
```

## Memory Bandwidth

**Rate of data transfer between memory levels.**

**Optimization**:
- Minimize data movement
- Use SIMD instructions
- Prefetch data

## Cache-Conscious Programming

### Data Structure Layout

```c
// Array of Structures (AoS) - poor for partial access
struct Point {
    float x, y, z;
    int color;
};
Point points[1000];

// Structure of Arrays (SoA) - better for partial access
struct Points {
    float x[1000];
    float y[1000];
    float z[1000];
    int color[1000];
};
```

### Loop Optimization

```c
// Cache blocking / tiling
// Instead of:
for (i = 0; i < N; i++)
    for (j = 0; j < N; j++)
        for (k = 0; k < N; k++)
            C[i][j] += A[i][k] * B[k][j];

// Use blocking:
for (ii = 0; ii < N; ii += BLOCK)
    for (jj = 0; jj < N; jj += BLOCK)
        for (kk = 0; kk < N; kk += BLOCK)
            for (i = ii; i < min(ii+BLOCK, N); i++)
                for (j = jj; j < min(jj+BLOCK, N); j++)
                    for (k = kk; k < min(kk+BLOCK, N); k++)
                        C[i][j] += A[i][k] * B[k][j];
```

## Virtual Memory and TLB

**TLB (Translation Lookaside Buffer)**: Cache for page table entries.

```
Virtual Address -> TLB -> Physical Address (hit)
                      -> Page Table Walk (miss)
```

**TLB miss cost**: 10-100+ cycles.

**Optimization**: Use large pages (2MB, 1GB).

## NUMA (Non-Uniform Memory Access)

Memory access time depends on location.

```
+--------+     +--------+
| CPU 0  |-----| CPU 1  |
| Local  |     | Local  |
| Memory |     | Memory |
+--------+     +--------+

CPU 0 accessing local memory: Fast
CPU 0 accessing CPU 1's memory: Slower
```

**Optimization**: Allocate memory near the CPU using it.

## Interview Questions

1. **What are the 3 C's of cache misses?**
   - Compulsory: First access
   - Capacity: Cache too small
   - Conflict: Same cache set

2. **How does write-back differ from write-through?**
   - Write-through: Update memory immediately
   - Write-back: Update memory on eviction
   - Write-back has less memory traffic

3. **What is cache line?**
   - Unit of data transfer
   - Typically 64 bytes
   - Spatial locality exploits this

4. **How to write cache-friendly code?**
   - Exploit temporal locality (reuse)
   - Exploit spatial locality (sequential access)
   - Use blocking/tiling
   - Align data structures
