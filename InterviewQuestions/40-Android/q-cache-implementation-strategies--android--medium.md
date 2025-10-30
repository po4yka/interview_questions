---
id: 20251012-122789
title: Cache Implementation Strategies / Стратегии реализации кэша
aliases: ["Cache Implementation Strategies", "Стратегии реализации кэша"]
topic: android
subtopics: [cache-offline, networking-http, room]
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
updated: 2025-10-29
sources: []
tags: [android/cache-offline, android/networking-http, android/room, difficulty/medium]
---
# Вопрос (RU)
> Какие существуют стратегии реализации кэша в Android?

# Question (EN)
> What are the cache implementation strategies in Android?

---

## Ответ (RU)

### Многоуровневая архитектура

**Память → Диск → Сеть**: стандартная трехуровневая иерархия в Android.

**Cache-Aside** (ленивая загрузка): проверка кэша перед запросом к источнику. Простейший паттерн.

**Write-Through**: синхронная запись в кэш и источник. Консистентность, но медленнее.

**Write-Back**: запись в кэш с отложенной синхронизацией через WorkManager.

**Refresh-Ahead**: проактивное обновление до истечения TTL.

```kotlin
// ✅ Cache-aside: все слои
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Горячий путь
  disk[key]?.let {
    if (!stale(it)) return it.also { memory.put(key, it) }
  }
  return network.load(key).also {
    memory.put(key, it)
    disk.put(key, it.withTimestamp())
  }
}

// ❌ Пропуск кэша
suspend fun getBad(key: K): V = network.load(key) // ❌ Всегда сеть
```

```kotlin
// ✅ OkHttp HTTP cache
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()

// ✅ Room entity с TTL
@Entity data class CachedUser(
  @PrimaryKey val id: String,
  val name: String,
  val cachedAt: Long = System.currentTimeMillis()
)
```

### Управление

**Ключи**: userId, locale, version в составе ключа
**TTL**: по типу данных (новости 5м, профиль 1ч)
**Вытеснение**: LruCache для памяти, FIFO для диска
**Инвалидация**: при мутациях, смене пользователя, pull-to-refresh

**Инструменты**: LruCache (память), Room (диск), DataStore (настройки), OkHttp Cache (HTTP), Glide/Coil (изображения)

## Answer (EN)

### Multi-tier Architecture

**Memory → Disk → Network**: standard three-tier hierarchy in Android.

**Cache-Aside** (lazy loading): check cache before fetching from source. Simplest pattern.

**Write-Through**: synchronous write to cache and source. Consistency but slower.

**Write-Back**: cache write with deferred sync via WorkManager.

**Refresh-Ahead**: proactive refresh before TTL expiration.

```kotlin
// ✅ Cache-aside: all layers
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Hot path
  disk[key]?.let {
    if (!stale(it)) return it.also { memory.put(key, it) }
  }
  return network.load(key).also {
    memory.put(key, it)
    disk.put(key, it.withTimestamp())
  }
}

// ❌ Skipping cache
suspend fun getBad(key: K): V = network.load(key) // ❌ Always network
```

```kotlin
// ✅ OkHttp HTTP cache
val client = OkHttpClient.Builder()
  .cache(Cache(File(cacheDir, "http"), 10L * 1024 * 1024))
  .build()

// ✅ Room entity with TTL
@Entity data class CachedUser(
  @PrimaryKey val id: String,
  val name: String,
  val cachedAt: Long = System.currentTimeMillis()
)
```

### Management

**Keys**: userId, locale, version in key composition
**TTL**: by data type (news 5m, profile 1h)
**Eviction**: LruCache for memory, FIFO for disk
**Invalidation**: on mutations, user switch, pull-to-refresh

**Tools**: LruCache (memory), Room (disk), DataStore (settings), OkHttp Cache (HTTP), Glide/Coil (images)

## Follow-ups
- How to balance TTL with server cache headers (Cache-Control, max-age)?
- When to choose write-through vs write-back for mobile data consistency?
- How to measure cache hit rate and eviction patterns in production?
- What are memory pressure triggers for aggressive cache eviction?
- How to implement stale-while-revalidate pattern for offline-first apps?

## References
- https://developer.android.com/topic/performance/memory
- https://developer.android.com/training/data-storage
- https://developer.android.com/reference/androidx/collection/LruCache
- https://square.github.io/okhttp/features/caching/

## Related Questions

### Prerequisites (Easier)
- [[q-android-storage-types--android--medium]]

### Related (Same Level)
- [[q-database-optimization-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-offline-first-architecture--android--hard]]
