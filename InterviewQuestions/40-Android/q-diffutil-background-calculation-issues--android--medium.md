---
id: 20251020-200100
title: DiffUtil Background Calculation Issues / Проблемы фонового вычисления DiffUtil
aliases:
- DiffUtil Background Calculation Issues
- Проблемы фонового вычисления DiffUtil
topic: android
subtopics:
- ui-views
- performance-memory

question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
source_note: Android DiffUtil documentation
status: draft
moc: moc-android
related:
- q-main-causes-ui-lag--android--medium
- q-recyclerview-optimization--android--medium
- q-android-performance-optimization--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/ui-views
  - android/performance
  - recyclerview
  - diffutil
  - multithreading
  - difficulty/medium
---

# Вопрос (RU)
> Когда фоновое вычисление DiffUtil работает плохо?

# Question (EN)
> When does DiffUtil background calculation work poorly?

---
## Ответ (RU)

DiffUtil в фоне плохо работает при изменении данных во время расчета, тяжелых вычислениях в callback, больших списках (>1000 элементов), неправильной обработке ошибок, race conditions между потоками.

### Основные проблемы

**1. Изменение данных во время расчета**
- Проблема: исходный список изменяется другим потоком во время DiffUtil.calculateDiff()
- Результат: некорректные diff операции, IndexOutOfBoundsException, неправильные анимации
- Решение: захватить неизменяемую копию списка перед расчетом

```kotlin
// ПЛОХО - данные могут измениться
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // users может измениться!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // ОПАСНО!
        })
    }
}

// ХОРОШО - неизменяемая копия
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Захват копии
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size // Безопасно
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
        })
    }
}
```

**2. Тяжелые вычисления в callback**
- Проблема: сложные операции в areContentsTheSame() замедляют расчет даже в фоне
- Результат: долгие вычисления блокируют background thread, задержка UI обновлений
- Решение: предварительно вычислить сравниваемые значения или кэшировать

```kotlin
// ПЛОХО - тяжелые вычисления в callback
override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
    val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData) // МЕДЛЕННО!
    val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
    return oldData == newData
}

// ХОРОШО - предварительное вычисление
class MessageCallback(private val oldList: List<Message>, private val newList: List<Message>) {
    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldDataCache[oldPos] == newData // Быстрое сравнение
    }
}
```

**3. Большие списки**
- Проблема: DiffUtil имеет O(N²) сложность для списков >1000 элементов
- Результат: долгие вычисления даже в фоне, ANR при больших списках
- Решение: пагинация, ListAdapter с AsyncListDiffer, или ручная оптимизация

```kotlin
// ПЛОХО - большой список без оптимизации
fun updateLargeList(newItems: List<Item>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(LargeListCallback(items, newItems))
        // Может занять секунды для списка >1000 элементов
    }
}

// ХОРОШО - ListAdapter с AsyncListDiffer
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {
    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Автоматически в фоне
    }
}
```

**4. Race conditions**
- Проблема: множественные вызовы updateUsers() создают race conditions
- Результат: некорректные diff операции, потеря обновлений
- Решение: отмена предыдущих операций, использование Job

```kotlin
// ПЛОХО - race conditions
class Adapter {
    fun updateUsers(newUsers: List<User>) {
        CoroutineScope(Dispatchers.Default).launch {
            // Может быть несколько одновременных вызовов
            val diffResult = DiffUtil.calculateDiff(...)
        }
    }
}

// ХОРОШО - отмена предыдущих операций
class Adapter {
    private var updateJob: Job? = null

    fun updateUsers(newUsers: List<User>) {
        updateJob?.cancel() // Отменить предыдущую операцию
        updateJob = CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                if (isActive) { // Проверить не отменена ли
                    diffResult.dispatchUpdatesTo(this@Adapter)
                }
            }
        }
    }
}
```

**5. Неправильная обработка ошибок**
- Проблема: исключения в DiffUtil.calculateDiff() не обрабатываются
- Результат: краши приложения, потеря обновлений UI
- Решение: try-catch блоки, fallback стратегии

```kotlin
// ПЛОХО - нет обработки ошибок
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(...) // Может упасть
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(this@Adapter)
        }
    }
}

// ХОРОШО - обработка ошибок
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                diffResult.dispatchUpdatesTo(this@Adapter)
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                notifyDataSetChanged() // Fallback
            }
        }
    }
}
```

### Теория DiffUtil

**Алгоритм Myer's diff:**
- Основан на алгоритме поиска кратчайшего пути редактирования между двумя списками
- Временная сложность: O(N²) в худшем случае, O(N) в лучшем
- Пространственная сложность: O(N²) для хранения матрицы различий

**Оптимизации:**
- **Предварительная фильтрация**: исключение заведомо разных элементов
- **Кэширование**: сохранение результатов сравнения для повторного использования
- **Chunking**: разбиение больших списков на части для параллельной обработки

**Best practices:**
- Использовать ListAdapter вместо ручного DiffUtil
- Предварительно вычислять сравниваемые значения
- Отменять предыдущие операции при новых обновлениях
- Обрабатывать ошибки с fallback стратегиями

## Answer (EN)

DiffUtil in background works poorly with data changes during calculation, heavy computations in callbacks, large lists (>1000 items), improper error handling, race conditions between threads.

### Main Issues

**1. Data modification during calculation**
- Problem: source list changes by another thread during DiffUtil.calculateDiff()
- Result: incorrect diff operations, IndexOutOfBoundsException, wrong animations
- Solution: capture immutable copy before calculation

```kotlin
// BAD - data can change
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // users can change!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // DANGEROUS!
        })
    }
}

// GOOD - immutable copy
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Capture copy
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size // Safe
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
        })
    }
}
```

**2. Heavy computations in callback**
- Problem: complex operations in areContentsTheSame() slow down calculation even in background
- Result: long computations block background thread, UI update delays
- Solution: pre-compute comparable values or cache

```kotlin
// BAD - heavy computations in callback
override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
    val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData) // SLOW!
    val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
    return oldData == newData
}

// GOOD - pre-computation
class MessageCallback(private val oldList: List<Message>, private val newList: List<Message>) {
    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldDataCache[oldPos] == newData // Fast comparison
    }
}
```

**3. Large lists**
- Problem: DiffUtil has O(N²) complexity for lists >1000 items
- Result: long calculations even in background, ANR for large lists
- Solution: pagination, ListAdapter with AsyncListDiffer, or manual optimization

```kotlin
// BAD - large list without optimization
fun updateLargeList(newItems: List<Item>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(LargeListCallback(items, newItems))
        // Can take seconds for list >1000 items
    }
}

// GOOD - ListAdapter with AsyncListDiffer
class OptimizedAdapter : ListAdapter<Item, ViewHolder>(DiffCallback()) {
    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Automatically in background
    }
}
```

**4. Race conditions**
- Problem: multiple updateUsers() calls create race conditions
- Result: incorrect diff operations, lost updates
- Solution: cancel previous operations, use Job

```kotlin
// BAD - race conditions
class Adapter {
    fun updateUsers(newUsers: List<User>) {
        CoroutineScope(Dispatchers.Default).launch {
            // Can have multiple concurrent calls
            val diffResult = DiffUtil.calculateDiff(...)
        }
    }
}

// GOOD - cancel previous operations
class Adapter {
    private var updateJob: Job? = null

    fun updateUsers(newUsers: List<User>) {
        updateJob?.cancel() // Cancel previous operation
        updateJob = CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                if (isActive) { // Check if not cancelled
                    diffResult.dispatchUpdatesTo(this@Adapter)
                }
            }
        }
    }
}
```

**5. Improper error handling**
- Problem: exceptions in DiffUtil.calculateDiff() not handled
- Result: app crashes, lost UI updates
- Solution: try-catch blocks, fallback strategies

```kotlin
// BAD - no error handling
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(...) // Can crash
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(this@Adapter)
        }
    }
}

// GOOD - error handling
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                diffResult.dispatchUpdatesTo(this@Adapter)
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                notifyDataSetChanged() // Fallback
            }
        }
    }
}
```

### DiffUtil Theory

**Myer's diff algorithm:**
- Based on shortest edit path algorithm between two lists
- Time complexity: O(N²) worst case, O(N) best case
- Space complexity: O(N²) for difference matrix storage

**Optimizations:**
- **Pre-filtering**: exclude obviously different elements
- **Caching**: store comparison results for reuse
- **Chunking**: split large lists for parallel processing

**Best practices:**
- Use ListAdapter instead of manual DiffUtil
- Pre-compute comparable values
- Cancel previous operations on new updates
- Handle errors with fallback strategies

**See also:** c-diff-algorithm, c-concurrency


## Follow-ups
- How to optimize DiffUtil for lists with >10,000 items?
- What's the difference between DiffUtil and AsyncListDiffer?
- How to handle DiffUtil with complex nested data structures?

## Related Questions
- [[q-main-causes-ui-lag--android--medium]]
