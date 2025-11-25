---
id: lang-086
title: "How System Knows WeakReference Can Be Cleared"
aliases: [How System Knows WeakReference Can Be Cleared, Как система знает что WeakReference можно очистить]
topic: kotlin
subtopics: [references]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-concepts--kotlin--medium, q-garbage-collector-basics--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [difficulty/medium, kotlin, references]
date created: Friday, October 31st 2025, 6:31:28 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---

# Вопрос (RU)
> Как система понимает, что WeakReference можно очистить?

---

# Question (EN)
> How does the system know that WeakReference can be cleared?

## Ответ (RU)

Система определяет, что `WeakReference` можно очистить, с помощью сборщика мусора и анализа достижимости объектов.

Ключевой принцип:
- Объект, на который ссылается `WeakReference`, может быть собран, когда он становится достижимым ТОЛЬКО через слабые ссылки (нет сильных ссылок). В момент выполнения GC такие объекты помечаются как подлежащие сборке, а их слабые ссылки очищаются.

Как это работает (упрощённо):

1. Фаза пометки:
   - GC находит все объекты, достижимые по сильным ссылкам, и помечает их как "сильно достижимые".

2. Обработка слабых ссылок:
   - Для каждой `WeakReference` проверяется, является ли её объект сильно достижимым.
   - Если нет — ссылка на объект внутри `WeakReference` очищается (становится `null`), а сама слабая ссылка может быть поставлена в `ReferenceQueue` для последующей обработки.

3. Фаза очистки:
   - Непомеченные объекты освобождаются.

Важно:
- Очистка слабых ссылок и сборка объекта происходят только при выполнении GC; вызов `System.gc()` лишь даёт подсказку, но не гарантирует немедленный запуск.
- После того как GC очистил слабую ссылку, вызов `weakRef.get()` для неё будет возвращать `null`, что сигнализирует об удалении объекта.

### Пример 1: Базовое Поведение

```kotlin
import java.lang.ref.WeakReference

val data = Data()  // Сильная ссылка
val weakRef = WeakReference(data)

// data сильно достижим
// Во время GC объект сохраняется
// weakRef.get() != null
```

```kotlin
val weakRef = WeakReference(Data())

// Других сильных ссылок на этот экземпляр Data нет
// Во время цикла GC объект может быть собран,
// а ссылка WeakReference — очищена

System.gc()  // Подсказка: может вызвать GC

// После GC weakRef.get() может вернуть null,
// если объект был собран
```

### Пример 2: Простой Кэш

```kotlin
class Cache {
    val weakCache = mutableMapOf<String, WeakReference<Data>>()

    fun put(key: String, value: Data) {
        weakCache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        val weakRef = weakCache[key]
        val data = weakRef?.get()

        if (data == null) {
            // Объект был собран; очищаем запись
            weakCache.remove(key)
        }

        return data
    }
}

fun example() {
    val cache = Cache()

    var data: Data? = Data()
    cache.put("key1", data!!)

    println(cache.get("key1"))  // Скорее всего не null: сильная ссылка ещё есть

    data = null  // Удаляем сильную ссылку

    System.gc()  // Только подсказка GC

    println(cache.get("key1"))  // Может быть null, если GC собрал объект
}
```

### Сильные Vs Слабые Ссылки

```kotlin
// Сценарий 1: Есть сильная ссылка
val strongRef = Data()
val weakRef1 = WeakReference(strongRef)

// При работе GC:
// - strongRef удерживает Data
// - weakRef1.get() возвращает экземпляр Data

// Сценарий 2: Осталась только слабая ссылка
val weakRef2 = WeakReference(Data())

// При работе GC:
// - Нет сильных ссылок на этот экземпляр Data
// - Объект становится кандидатом на сборку
// - После сборки weakRef2.get() возвращает null
```

### Состояния Достижимости (упрощённо)

- Сильно достижимый:
  - Есть хотя бы одна цепочка сильных ссылок от GC root.
  - Действие: объект сохраняется; `WeakReference` к нему не очищаются.

- Слабо достижимый:
  - Нет сильных ссылок от GC root, но есть слабые ссылки.
  - Действие: во время GC объект может быть собран; соответствующие `WeakReference` очищаются (и могут быть поставлены в `ReferenceQueue`); после этого объект собирается.

- Недостижимый:
  - Нет ссылок, удерживающих объект.
  - Действие: объект собирается.

### Практический Пример

```kotlin
class ImageCache {
    private val cache = mutableMapOf<String, WeakReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()?.also {
            println("Cache hit!")
        } ?: run {
            println("Cache miss (возможно, GC очистил ссылку)")
            return null
        }
    }

    fun put(url: String, bitmap: Bitmap) {
        cache[url] = WeakReference(bitmap)
    }
}

// Использование:
val imageCache = ImageCache()
var bitmap: Bitmap? = loadBitmap()

imageCache.put("url", bitmap!!)
// bitmap сильно удерживает объект → он жив

bitmap = null  // Удаляем сильную ссылку
System.gc()     // Только подсказка GC

// Позже imageCache.get("url") может вернуть null,
// если GC собрал Bitmap и очистил WeakReference
```

## Answer (EN)

The system uses the garbage collector (GC) and reachability analysis to determine when a WeakReference can be cleared.

Key principle:
- The referent of a WeakReference becomes eligible for collection when it is reachable ONLY through weak references (no strong references). During a GC cycle, such objects are treated as collectible, and their weak references are cleared.

How it works:

1. Mark phase:
   - The GC finds all objects reachable through strong references and marks them as strongly reachable.

2. Weak reference processing:
   - For each WeakReference, the GC checks whether its referent is strongly reachable.
   - If the referent is not strongly reachable, the GC clears the referent inside the WeakReference (its `get()` will later return `null`) and may enqueue the WeakReference into an associated ReferenceQueue.

3. Sweep phase:
   - Unmarked (unreachable) objects are reclaimed.

Note: `System.gc()` only suggests that the GC may run; it does not guarantee immediate collection or clearing.

### Example 1: Basic Behavior

```kotlin
import java.lang.ref.WeakReference

val data = Data()  // Strong reference
val weakRef = WeakReference(data)

// data is strongly reachable
// So during GC, the referent is kept alive
// weakRef.get() != null
```

```kotlin
val weakRef = WeakReference(Data())

// No other strong reference to this Data instance is kept
// On a GC cycle, the referent may be collected and the WeakReference referent cleared

System.gc()  // Hint: may trigger GC

// After GC, weakRef.get() may return null if the referent was collected
```

### Example 2: Simple Cache

```kotlin
class Cache {
    val weakCache = mutableMapOf<String, WeakReference<Data>>()

    fun put(key: String, value: Data) {
        weakCache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        val weakRef = weakCache[key]
        val data = weakRef?.get()

        if (data == null) {
            // Referent was collected; clean up the entry
            weakCache.remove(key)
        }

        return data
    }
}

fun example() {
    val cache = Cache()

    var data: Data? = Data()
    cache.put("key1", data!!)

    println(cache.get("key1"))  // Likely non-null: strong reference still exists

    data = null  // Remove strong reference

    System.gc()  // Hint: may trigger GC

    println(cache.get("key1"))  // May be null if GC collected the referent
}
```

### Strong Vs Weak References

```kotlin
// Scenario 1: Strong reference exists
val strongRef = Data()
val weakRef1 = WeakReference(strongRef)

// When GC runs:
// - strongRef keeps Data strongly reachable
// - weakRef1.get() returns the Data instance

// Scenario 2: Only weak reference remains
val weakRef2 = WeakReference(Data())

// When GC runs:
// - No strong reference to this Data instance is kept
// - The referent becomes eligible for collection
// - After collection, weakRef2.get() returns null
```

### Reachability States (simplified)

- Strongly reachable:
  - Has at least one chain of strong references from GC roots.
  - Action: object is kept; WeakReferences to it are not cleared.

- Weakly reachable:
  - No strong references from GC roots, but at least one weak reference exists.
  - Action: during GC, the referent is eligible for reclamation; WeakReferences to it are cleared (and may be enqueued); after that it is collected.

- Unreachable:
  - No references keep it; purely garbage.
  - Action: collected.

### Practical Example

```kotlin
class ImageCache {
    private val cache = mutableMapOf<String, WeakReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()?.also {
            println("Cache hit!")
        } ?: run {
            println("Cache miss (possibly GC cleared referent)")
            return null
        }
    }

    fun put(url: String, bitmap: Bitmap) {
        cache[url] = WeakReference(bitmap)
    }
}

// Usage:
val imageCache = ImageCache()
var bitmap: Bitmap? = loadBitmap()

imageCache.put("url", bitmap!!)
// bitmap is strongly held → referent is alive

bitmap = null  // Remove strong reference
System.gc()     // Hint only

// Later, imageCache.get("url") may return null
// if GC has collected the Bitmap referent and cleared the WeakReference
```

### Summary

The GC determines a WeakReference's referent can be cleared when:
- The object is not strongly reachable from GC roots.
- It is reachable only via weak references.
- A GC cycle processes weak references and clears them before reclaiming the object.

---

## Дополнительные Вопросы (RU)

- Как это связано с Kotlin на JVM по сравнению с другими таргетами Kotlin (например, Native)?
- Когда на практике стоит использовать `WeakReference`?
- Каковы типичные подводные камни при использовании `WeakReference` и полагании на `System.gc()` в примерах?

## Follow-ups

- How does this relate to Kotlin on JVM vs other Kotlin targets (e.g., Native)?
- When would you use WeakReference in practice?
- What are common pitfalls when relying on WeakReference and System.gc() in examples?

## Ссылки (RU)

- [[c-garbage-collection]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-garbage-collection]]

## Связанные Вопросы (RU)

- [[q-garbage-collector-basics--programming-languages--medium]]

## Related Questions

- [[q-garbage-collector-basics--programming-languages--medium]]
