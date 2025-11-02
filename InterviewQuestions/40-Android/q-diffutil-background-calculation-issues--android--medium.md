---
id: android-473
title: DiffUtil Background Calculation Issues / Проблемы фонового вычисления DiffUtil
aliases: [DiffUtil Background Calculation Issues, Проблемы фонового вычисления DiffUtil, DiffUtil background issues, Проблемы DiffUtil в фоне]
topic: android
subtopics: [performance-memory, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-performance-optimization--android--medium, q-main-causes-ui-lag--android--medium, q-recyclerview-optimization--android--medium]
sources: [https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil]
created: 2025-10-20
updated: 2025-10-28
tags: [android/performance-memory, android/ui-views, difficulty/medium, diffutil, recyclerview]
date created: Tuesday, October 28th 2025, 9:22:13 am
date modified: Thursday, October 30th 2025, 12:47:42 pm
---

# Вопрос (RU)
> Когда фоновое вычисление DiffUtil работает плохо?

# Question (EN)
> When does DiffUtil background calculation work poorly?

---

## Ответ (RU)

DiffUtil в фоне плохо работает при изменении данных во время расчета, тяжелых вычислениях в callback, больших списках (>1000 элементов), неправильной обработке ошибок, race conditions между потоками.

### Основные Проблемы

**1. Изменение данных во время расчета**

Исходный список изменяется другим потоком во время calculateDiff(), что приводит к IndexOutOfBoundsException и некорректным diff операциям.

```kotlin
// ❌ ПЛОХО - данные могут измениться
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // users может измениться!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id
        })
    }
}

// ✅ ХОРОШО - неизменяемая копия
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList()
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
        })
    }
}
```

**2. Тяжелые вычисления в callback**

Сложные операции в areContentsTheSame() замедляют расчет даже в фоне.

```kotlin
// ❌ ПЛОХО - парсинг JSON в callback
override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
    val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
    val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
    return oldData == newData
}

// ✅ ХОРОШО - кэширование результатов
class MessageCallback(oldList: List<Message>, newList: List<Message>) {
    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldDataCache[oldPos] == newData
    }
}
```

**3. Большие списки**

DiffUtil имеет O(N²) сложность, что критично для списков >1000 элементов.

```kotlin
// ✅ ХОРОШО - ListAdapter с AsyncListDiffer
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {
    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Автоматически в фоне
    }
}
```

**4. Race conditions**

Множественные вызовы updateUsers() создают race conditions и потерю обновлений.

```kotlin
// ✅ ХОРОШО - отмена предыдущих операций
class Adapter {
    private var updateJob: Job? = null

    fun updateUsers(newUsers: List<User>) {
        updateJob?.cancel()
        updateJob = CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                if (isActive) {
                    diffResult.dispatchUpdatesTo(this@Adapter)
                }
            }
        }
    }
}
```

**5. Отсутствие обработки ошибок**

Исключения в calculateDiff() приводят к крашам приложения.

```kotlin
// ✅ ХОРОШО - обработка ошибок
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                diffResult.dispatchUpdatesTo(this@Adapter)
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                notifyDataSetChanged()
            }
        }
    }
}
```

### Best Practices

- Использовать ListAdapter вместо ручного DiffUtil
- Захватывать неизменяемые копии данных перед расчетом
- Отменять предыдущие операции при новых обновлениях
- Обрабатывать ошибки с fallback стратегиями
- Кэшировать тяжелые вычисления вне callback

## Answer (EN)

DiffUtil in background works poorly with data changes during calculation, heavy computations in callbacks, large lists (>1000 items), improper error handling, race conditions between threads.

### Main Issues

**1. Data modification during calculation**

Source list changes by another thread during calculateDiff(), causing IndexOutOfBoundsException and incorrect diff operations.

```kotlin
// ❌ BAD - data can change
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // users can change!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id
        })
    }
}

// ✅ GOOD - immutable copy
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList()
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
        })
    }
}
```

**2. Heavy computations in callback**

Complex operations in areContentsTheSame() slow down calculation even in background.

```kotlin
// ❌ BAD - JSON parsing in callback
override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
    val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
    val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
    return oldData == newData
}

// ✅ GOOD - cached results
class MessageCallback(oldList: List<Message>, newList: List<Message>) {
    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldDataCache[oldPos] == newData
    }
}
```

**3. Large lists**

DiffUtil has O(N²) complexity, critical for lists >1000 items.

```kotlin
// ✅ GOOD - ListAdapter with AsyncListDiffer
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {
    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Automatically in background
    }
}
```

**4. Race conditions**

Multiple updateUsers() calls create race conditions and lost updates.

```kotlin
// ✅ GOOD - cancel previous operations
class Adapter {
    private var updateJob: Job? = null

    fun updateUsers(newUsers: List<User>) {
        updateJob?.cancel()
        updateJob = CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                if (isActive) {
                    diffResult.dispatchUpdatesTo(this@Adapter)
                }
            }
        }
    }
}
```

**5. Missing error handling**

Exceptions in calculateDiff() cause app crashes.

```kotlin
// ✅ GOOD - error handling
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                diffResult.dispatchUpdatesTo(this@Adapter)
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                notifyDataSetChanged()
            }
        }
    }
}
```

### Best Practices

- Use ListAdapter instead of manual DiffUtil
- Capture immutable copies before calculation
- Cancel previous operations on new updates
- Handle errors with fallback strategies
- Cache heavy computations outside callbacks

---

## Follow-ups

- How to optimize DiffUtil for lists with >10,000 items?
- What's the difference between DiffUtil and AsyncListDiffer?
- When to use ListAdapter vs manual DiffUtil implementation?
- How to handle DiffUtil with complex nested data structures?
- What are alternatives to DiffUtil for very large datasets?

## References

- [[c-diff-algorithm]]
- [[c-concurrency]]
- https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
- https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-basics--android--easy]]

### Related (Same Level)
- [[q-main-causes-ui-lag--android--medium]]
- [[q-android-performance-optimization--android--medium]]
- [[q-recyclerview-optimization--android--medium]]

### Advanced (Harder)
- [[q-implement-custom-diffutil-algorithm--android--hard]]
