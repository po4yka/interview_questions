---
id: 20251012-122789
title: Cache Implementation Strategies / Стратегии реализации кэша
aliases:
- Cache Implementation Strategies
- Стратегии реализации кэша
topic: android
subtopics:
- room
- datastore
- networking-http
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-storage-types--android--medium
- q-android-performance-measurement-tools--android--medium
- q-database-optimization-android--android--medium
created: 2025-10-13
updated: 2025-10-20
tags:
- android/room
- android/datastore
- android/networking-http
- difficulty/medium
---

# Вопрос (RU)
> Стратегии реализации кэша?

# Question (EN)
> Cache Implementation Strategies?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Goals and Layers
- Goals: lower latency, fewer network calls, resilience offline, predictable memory use.
- Layers (prefer multi-level): Memory → Disk → Network.
  - Memory: fastest, small, LRU.
  - Disk (Room/Files): larger, TTL/indexable.
  - Network: last resort; respect HTTP cache.

### Core Strategies
- Cache-Aside (lazy): read-through + explicit populate; simplest.
- Write-Through: write to cache and source synchronously.
- Write-Back (behind): write to cache, flush to source later; needs durability queue.
- Refresh-Ahead: proactively refresh near-expiry keys.

All strategies benefit from proper memory management to avoid [[c-memory-leaks]].

### Keys, TTL, Eviction
- Keys: stable, include parameters (locale/userId/version).
- TTL: per type (e.g., news=5m, profile=1h); store timestamps alongside values.
- Eviction: LRU for memory; size/time-based for disk; segment by type.

### Invalidation
- On data change (write-through), on version/schema change, on auth/user switch, on explicit policy (pull-to-refresh).
- Provide invalidate(key), invalidateType(type), invalidateAll(), and age-based sweeping.

### Minimal Code (illustrative)
```kotlin
// Cache-aside read (memory → disk → network)
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it }
  disk[key]?.let { if (!stale(it)) return memory.putAndReturn(key, it) }
  return network.load(key).also { memory.put(key, it); disk.put(key, it.withTimestamp()) }
}
```

```kotlin
// OkHttp HTTP cache (respect server headers)
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()
```

```kotlin
// Small in-memory LRU
class Lru<K, V>(max: Int) : LruCache<K, V>(max)
```

### Tooling and Measurement
- Use Perfetto/Build Scans/Metrics: hit rate, miss rate, stale serves, size, eviction count, network reduction.
- Log cache layers and decisions at debug level; sample in production.

### Components
- Preferences/DataStore: small KV (flags, timestamps) using c-datastore or c-shared-preferences.
- Room: structured cached entities (with cachedAt, origin ETag/Last-Modified) using [[c-room]].
- HTTP: OkHttp cache + Cache-Control; ETag/If-None-Match; stale-if-error for resiliency.
- Images: Glide/Picasso built-in caches; prefer library defaults + sizing.

## Follow-ups
- How to define TTLs per domain object and align with server cache headers?
- When to choose write‑through vs write‑back in mobile contexts?
- How to observe cache metrics in production with low overhead?

## References
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/topic/libraries/architecture/room
- https://square.github.io/okhttp/features/caching/

## Related Questions

### Prerequisites (Easier)
- [[q-android-storage-types--android--medium]]

### Related (Same Level)
- [[q-database-optimization-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-offline-first-architecture--android--hard]]
