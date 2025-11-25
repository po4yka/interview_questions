---
id: android-074
title: Cache Implementation Strategies / Стратегии реализации кэша
aliases: [Cache Implementation Strategies, Стратегии реализации кэша]
topic: android
subtopics:
  - cache-offline
  - networking-http
  - room
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-performance
  - c-room
  - q-android-performance-measurement-tools--android--medium
  - q-android-storage-types--android--medium
  - q-android-testing-strategies--android--medium
  - q-database-optimization-android--android--medium
  - q-integration-testing-strategies--android--medium
  - q-tflite-acceleration-strategies--android--hard
created: 2024-10-13
updated: 2025-11-10
tags: [android/cache-offline, android/networking-http, android/room, difficulty/medium]
date created: Saturday, November 1st 2025, 12:46:45 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Какие существуют стратегии реализации кэша в Android?

# Question (EN)
> What are the cache implementation strategies in Android?

---

## Ответ (RU)

### Многоуровневая Архитектура

**Память → Диск → Сеть**: стандартная трехуровневая иерархия в Android.

**Cache-Aside** (ленивая загрузка): проверка кэша перед запросом к источнику. Простейший паттерн.

**Write-Through**: синхронная запись в кэш и источник. Хорошая консистентность, но дополнительная задержка.

**Write-Back**: запись в кэш с отложенной синхронизацией с источником (например, через WorkManager или другой надежный фоновой механизм). Меньше задержка, но риск потери изменений / расхождения данных.

**Refresh-Ahead**: проактивное обновление до истечения TTL.

```kotlin
// ✅ Упрощенный cache-aside для всех слоев
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Горячий путь

  disk[key]?.let { cached ->
    if (!stale(cached)) {
      memory.put(key, cached)
      return cached
    }
  }

  val loaded = network.load(key) // выбросит исключение, если сеть недоступна
  memory.put(key, loaded)
  disk.put(key, loaded.withTimestamp())
  return loaded
}

// ❌ Пропуск кэша — нарушает идею cache-aside
suspend fun <K, V> getBad(key: K): V = network.load(key) // ❌ Всегда сеть
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

**Ключи**: включать userId, locale, версию и другие параметры в состав ключа.
**TTL**: по типу данных (новости 5м, профиль 1ч).
**Вытеснение**:
- LruCache для памяти (LRU по размеру).
- Для диска стратегия зависит от реализации: OkHttp использует size-based LRU, для Room вы реализуете свою (например, по времени/размеру), а не обязаны использовать FIFO.
**Инвалидация**: при мутациях, смене пользователя, pull-to-refresh.

**Инструменты**: LruCache (память), Room (диск), DataStore (настройки), OkHttp Cache (HTTP), Glide/Coil (изображения).

## Answer (EN)

### Multi-tier Architecture

**Memory → Disk → Network**: standard three-tier hierarchy in Android.

**Cache-Aside** (lazy loading): check cache before fetching from source. Simplest pattern.

**Write-Through**: synchronous write to cache and source. Good consistency but added latency.

**Write-Back**: write to cache with deferred synchronization to the source (e.g., via WorkManager or another reliable background mechanism). Lower latency but risk of lost updates / inconsistency.

**Refresh-Ahead**: proactive refresh before TTL expiration.

```kotlin
// ✅ Simplified cache-aside across all layers
suspend fun <K, V> get(key: K): V {
  memory[key]?.let { return it } // ✅ Hot path

  disk[key]?.let { cached ->
    if (!stale(cached)) {
      memory.put(key, cached)
      return cached
    }
  }

  val loaded = network.load(key) // will throw if network fails
  memory.put(key, loaded)
  disk.put(key, loaded.withTimestamp())
  return loaded
}

// ❌ Skipping cache — breaks cache-aside idea
suspend fun <K, V> getBad(key: K): V = network.load(key) // ❌ Always network
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

**Keys**: include userId, locale, version and other parameters in key composition.
**TTL**: by data type (e.g., news 5m, profile 1h).
**Eviction**:
- LruCache for memory (size-based LRU).
- For disk, strategy depends on implementation: OkHttp uses size-based LRU; with Room you implement your own (e.g., by time/size) and are not required to use FIFO.
**Invalidation**: on mutations, user switch, pull-to-refresh.

**Tools**: LruCache (memory), Room (disk), DataStore (settings), OkHttp Cache (HTTP), Glide/Coil (images).

## Дополнительные Вопросы (RU)
- Как балансировать TTL с серверными заголовками кэша (`Cache-Control`, `max-age`)?
- Когда выбирать `write-through` vs `write-back` для консистентности данных на мобильных устройствах?
- Как измерять `cache hit rate` и паттерны вытеснения в продакшене?
- Какие триггеры по давлению на память использовать для агрессивного очищения кэша?
- Как реализовать паттерн `stale-while-revalidate` для offline-first приложений?

## Follow-ups
- How to balance TTL with server cache headers (`Cache-Control`, `max-age`)?
- When to choose `write-through` vs `write-back` for mobile data consistency?
- How to measure cache hit rate and eviction patterns in production?
- What are memory pressure triggers for aggressive cache eviction?
- How to implement `stale-while-revalidate` pattern for offline-first apps?

## Ссылки (RU)

- https://developer.android.com/topic/performance/memory
- https://developer.android.com/training/data-storage
- https://developer.android.com/reference/androidx/collection/LruCache
- https://square.github.io/okhttp/features/caching/

## References

- https://developer.android.com/topic/performance/memory
- https://developer.android.com/training/data-storage
- https://developer.android.com/reference/androidx/collection/LruCache
- https://square.github.io/okhttp/features/caching/

## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-room]]
- [[c-performance]]

### Предпосылки (проще)
- [[q-android-storage-types--android--medium]]

### Связанные (тот Же уровень)
- [[q-database-optimization-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Продвинутые (сложнее)
- [[q-offline-first-architecture--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[c-room]]
- [[c-performance]]


### Prerequisites (Easier)
- [[q-android-storage-types--android--medium]]

### Related (Same Level)
- [[q-database-optimization-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-offline-first-architecture--android--hard]]
