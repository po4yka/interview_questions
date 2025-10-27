---
id: 20251012-122789
title: Cache Implementation Strategies / Стратегии реализации кэша
aliases: ["Cache Implementation Strategies", "Стратегии реализации кэша"]
topic: android
subtopics: [datastore, networking-http, room]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-performance-measurement-tools--android--medium
  - q-android-storage-types--android--medium
  - q-database-optimization-android--android--medium
created: 2025-10-13
updated: 2025-01-27
sources: []
tags: [android/datastore, android/networking-http, android/room, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют стратегии реализации кэша в Android?

# Question (EN)
> What are the cache implementation strategies in Android?

---

## Ответ (RU)

### Цели и уровни кэширования
- Цели: снижение задержек, меньше сетевых вызовов, работа офлайн, предсказуемое использование памяти.
- Уровни (многоуровневое кэширование): Память → Диск → Сеть.
  - Память: самый быстрый, небольшой объем, LRU.
  - Диск (Room/Files): больший объем, TTL/индексирование.
  - Сеть: последний вариант; используем HTTP кэш.

### Основные стратегии
- **Cache-Aside** (ленивая загрузка): чтение через кэш + явное заполнение; самая простая.
- **Write-Through**: запись в кэш и источник синхронно.
- **Write-Back**: запись в кэш, отложенная запись в источник; требует очереди для надежности.
- **Refresh-Ahead**: проактивное обновление ключей перед истечением TTL.

Все стратегии требуют правильного управления памятью для предотвращения [[c-memory-leaks]].

### Ключи, TTL, вытеснение
- Ключи: стабильные, включают параметры (locale/userId).
- TTL: по типу данных (новости=5m, профиль=1h).
- Вытеснение: LRU для памяти; по размеру/времени для диска.

### Инвалидация кэша
- При изменении данных, смене версии схемы, смене пользователя, явной политике (pull-to-refresh).

### Примеры кода
```kotlin
// ✅ Cache-aside pattern: memory → disk → network
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Fastest path
  disk[key]?.let {
    if (!stale(it)) return memory.putAndReturn(key, it)
  }
  return network.load(key).also {
    memory.put(key, it)
    disk.put(key, it.withTimestamp())
  }
}

// ❌ Don't skip memory layer
suspend fun getBad(key: K): V {
  return network.load(key) // ❌ Always hits network
}
```

```kotlin
// ✅ OkHttp HTTP cache with proper size
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()
```

### Компоненты
- DataStore: малые KV данные (flags, timestamps).
- Room: структурированные закэшированные сущности с cachedAt, используем [[c-room]].
- HTTP: OkHttp кэш + Cache-Control; ETag/If-None-Match.
- Изображения: Glide/Coil встроенные кэши.

## Answer (EN)

### Goals and Layers
- Goals: lower latency, fewer network calls, offline resilience, predictable memory use.
- Layers (multi-level): Memory → Disk → Network.
  - Memory: fastest, small size, LRU eviction.
  - Disk (Room/Files): larger capacity, TTL/indexing.
  - Network: last resort; respect HTTP cache.

### Core Strategies
- **Cache-Aside** (lazy loading): read-through + explicit populate; simplest.
- **Write-Through**: write to cache and source synchronously.
- **Write-Back**: write to cache, delayed flush to source; needs durability queue.
- **Refresh-Ahead**: proactively refresh near-expiry keys.

All strategies require proper memory management to avoid [[c-memory-leaks]].

### Keys, TTL, Eviction
- Keys: stable, include parameters (locale/userId).
- TTL: per data type (news=5m, profile=1h).
- Eviction: LRU for memory; size/time-based for disk.

### Cache Invalidation
- On data change, schema version change, user switch, explicit policy (pull-to-refresh).

### Code Examples
```kotlin
// ✅ Cache-aside pattern: memory → disk → network
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Fastest path
  disk[key]?.let {
    if (!stale(it)) return memory.putAndReturn(key, it)
  }
  return network.load(key).also {
    memory.put(key, it)
    disk.put(key, it.withTimestamp())
  }
}

// ❌ Don't skip memory layer
suspend fun getBad(key: K): V {
  return network.load(key) // ❌ Always hits network
}
```

```kotlin
// ✅ OkHttp HTTP cache with proper size
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()
```

### Components
- DataStore: small KV data (flags, timestamps).
- Room: structured cached entities with cachedAt, see [[c-room]].
- HTTP: OkHttp cache + Cache-Control; ETag/If-None-Match.
- Images: Glide/Coil built-in caches.

## Follow-ups
- How to balance TTL with server cache headers (Cache-Control, max-age)?
- When to choose write-through vs write-back for mobile data consistency?
- How to measure cache hit rate and eviction patterns in production?
- What are memory pressure triggers for aggressive cache eviction?

## References
- [[c-room]]
- [[c-memory-leaks]]
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/training/data-storage

## Related Questions

### Prerequisites (Easier)
- [[q-android-storage-types--android--medium]]

### Related (Same Level)
- [[q-database-optimization-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-offline-first-architecture--android--hard]]
