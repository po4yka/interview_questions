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
- networking
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related:
- q-android-storage-types--android--medium
- q-android-performance-measurement-tools--android--medium
- q-database-optimization-android--android--medium
created: 2025-10-13
updated: 2025-10-20
original_language: en
language_tags:
- en
- ru
tags:
- android/room
- android/datastore
- android/networking
- caching
- performance
- difficulty/medium
---# Вопрос (RU)
> Как спроектировать и реализовать кэширование в Android (уровни, политики, инвалидация и инструменты) с минимально достаточным кодом?

---

# Question (EN)
> How do you design and implement caching in Android (layers, policies, invalidation, and tooling) with minimal essential code?

## Ответ (RU)

### Цели и уровни
- Цели: меньшая задержка, меньше сетевых вызовов, офлайн‑устойчивость, предсказуемая память.
- Уровни (лучше многоуровневость): Память → Диск → Сеть.
  - Память: самая быстрая, малая, LRU.
  - Диск (Room/файлы): больше, TTL/индексация.
  - Сеть: последний вариант; уважать HTTP‑кеш.

### Базовые стратегии
- Cache‑Aside (ленивая): чтение через кэш + явное заполнение; самая простая.
- Write‑Through: запись в кэш и источник синхронно.
- Write‑Back (behind): запись в кэш, поздняя запись в источник; нужен надежный буфер.
- Refresh‑Ahead: проактивное обновление ключей перед истечением.

### Ключи, TTL, выталкивание
- Ключи: стабильные, включают параметры (locale/userId/version).
- TTL: по типам (news=5m, profile=1h); храните метки времени рядом со значениями.
- Выталкивание: LRU для памяти; по размеру/времени для диска; сегментируйте по типу.

### Инвалидация
- При изменении данных (write‑through), смене версии/схемы, смене пользователя, явной политике (pull‑to‑refresh).
- Предусмотрите invalidate(key), invalidateType(type), invalidateAll(), очистку по возрасту.

### Минимальный код (иллюстрация)
```kotlin
// Cache‑aside чтение (память → диск → сеть)
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it }
  disk[key]?.let { if (!stale(it)) return memory.putAndReturn(key, it) }
  return network.load(key).also { memory.put(key, it); disk.put(key, it.withTimestamp()) }
}
```

```kotlin
// HTTP‑кеш OkHttp (уважать заголовки сервера)
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()
```

```kotlin
// Небольшой LRU в памяти
class Lru<K, V>(max: Int) : LruCache<K, V>(max)
```

### Инструменты и метрики
- Perfetto/Build Scans/метрики: hit rate, miss rate, stale, размер, эвикции, снижение сети.
- Логируйте слои и решения на debug; в проде — сэмплирование.

### Компоненты
- Preferences/DataStore: маленький KV (флаги, timestamps).
- Room: структурированные сущности кэша (cachedAt, ETag/Last‑Modified источника).
- HTTP: OkHttp + Cache‑Control; ETag/If‑None‑Match; stale‑if‑error для устойчивости.
- Изображения: Glide/Picasso из коробки; придерживайтесь дефолтов + правильных размеров.

---

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
- Preferences/DataStore: small KV (flags, timestamps).
- Room: structured cached entities (with cachedAt, origin ETag/Last-Modified).
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

