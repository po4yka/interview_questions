---
id: android-321
title: "Primitive Maps Android / Примитивные Map в Android"
aliases: ["Primitive Maps Android", "SparseArray", "SparseIntArray", "Примитивные Map в Android"]
topic: android
subtopics: [performance-memory]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [android/performance-memory, collections, difficulty/medium, memory-optimization, performance]
---

# Вопрос (RU)

> Какие специализированные `Map`-коллекции для примитивных типов предоставляет Android SDK? Когда и почему их следует использовать вместо стандартных `HashMap`?

# Question (EN)

> What specialized `Map` collections for primitive types does Android SDK provide? When and why should they be used instead of standard `HashMap`?

---

## Ответ (RU)

Android предоставляет оптимизированные коллекции для примитивных типов, которые избегают автоупаковки (boxing) и значительно эффективнее стандартных `HashMap` для небольших коллекций (< 1000 элементов).

### Основные Типы

**1. SparseArray\<E\> — `Int` → Object**

```kotlin
import android.util.SparseArray

val userCache = SparseArray<User>()
userCache.put(1, User("Alice"))
userCache.put(100, User("Bob"))

val user = userCache.get(1) // ✅ Нет boxing для ключа
val size = userCache.size()
```

**2. SparseIntArray — `Int` → `Int`**

```kotlin
import android.util.SparseIntArray

val viewCounts = SparseIntArray()
viewCounts.put(101, 95)

fun incrementCount(id: Int) {
 val current = viewCounts.get(id, 0) // ✅ Default value: 0
 viewCounts.put(id, current + 1)
}
```

**3. SparseBooleanArray — `Int` → `Boolean`**

```kotlin
import android.util.SparseBooleanArray

val selectedItems = SparseBooleanArray()
selectedItems.put(0, true)
selectedItems.put(5, true)

fun isSelected(position: Int): Boolean {
 return selectedItems.get(position, false)
}
```

**4. LongSparseArray\<E\> — `Long` → Object**

```kotlin
import android.util.LongSparseArray

val timestampCache = LongSparseArray<Event>()
val timestamp = System.currentTimeMillis()
timestampCache.put(timestamp, Event("Click"))
```

### Производительность

**`HashMap` проблемы:**
- `Int` → Integer требует 16 байт вместо 4
- Каждая операция создаёт временные объекты
- Увеличенная нагрузка на GC
- Хэш-таблица занимает дополнительную память

**SparseArray преимущества:**
- Нет boxing: примитивы хранятся напрямую
- ~50% меньше памяти (24 vs 56 байт на элемент)
- Быстрее для < 1000 элементов
- Меньше давление на GC

**Ограничения:**
- O(log n) поиск vs O(1) в `HashMap`
- Медленнее для > 10K элементов
- Оптимизирован для последовательных ключей
- Не thread-safe

### Практическое Применение

**`RecyclerView` адаптер:**
```kotlin
class Adapter : RecyclerView.Adapter<ViewHolder>() {
 private val expandedItems = SparseBooleanArray() // ✅ Флаги состояния

 fun toggleExpanded(position: Int) {
 val isExpanded = expandedItems.get(position, false)
 expandedItems.put(position, !isExpanded)
 notifyItemChanged(position)
 }
}
```

**`ViewModel` с кэшем:**
```kotlin
class UserViewModel : ViewModel() {
 private val users = SparseArray<User>() // ✅ Int → User
 private val favorites = SparseBooleanArray() // ✅ Int → Boolean
 private val scores = SparseIntArray() // ✅ Int → Int

 fun toggleFavorite(userId: Int) {
 val isFavorite = favorites.get(userId, false)
 favorites.put(userId, !isFavorite)
 }

 override fun onCleared() {
 users.clear()
 favorites.clear()
 scores.clear()
 }
}
```

**Состояние загрузки:**
```kotlin
class StateManager {
 private val loadingStates = SparseBooleanArray() // ✅ Флаги загрузки
 private val errorCounts = SparseIntArray() // ✅ Счётчики ошибок
 private val dataCache = SparseArray<Data>() // ✅ Кэш данных

 fun startLoading(id: Int) {
 loadingStates.put(id, true)
 }

 fun isLoading(id: Int): Boolean = loadingStates.get(id, false)
}
```

### Правила Использования

**Используйте SparseArray когда:**
- Коллекция < 1000 элементов
- Ключи — последовательные `Int`/`Long`
- Важна экономия памяти
- Однопоточный доступ

**Используйте `HashMap` когда:**
- Коллекция > 10K элементов
- Ключи — случайные или несортированные
- Критична скорость поиска O(1)
- Нужен многопоточный доступ (ConcurrentHashMap)

### Миграция С `HashMap`

```kotlin
// ❌ До: HashMap с boxing
val cache = HashMap<Int, String>()
cache[id] = value
cache.remove(id)
cache.containsKey(id)

// ✅ После: SparseArray без boxing
val cache = SparseArray<String>()
cache.put(id, value)
cache.remove(id)
cache.indexOfKey(id) >= 0
```

## Answer (EN)

Android provides optimized collections for primitive types that avoid boxing overhead and are significantly more efficient than standard `HashMap` for small collections (< 1000 elements).

### Main Types

**1. SparseArray\<E\> — `Int` → Object**

```kotlin
import android.util.SparseArray

val userCache = SparseArray<User>()
userCache.put(1, User("Alice"))
userCache.put(100, User("Bob"))

val user = userCache.get(1) // ✅ No boxing for key
val size = userCache.size()
```

**2. SparseIntArray — `Int` → `Int`**

```kotlin
import android.util.SparseIntArray

val viewCounts = SparseIntArray()
viewCounts.put(101, 95)

fun incrementCount(id: Int) {
 val current = viewCounts.get(id, 0) // ✅ Default value: 0
 viewCounts.put(id, current + 1)
}
```

**3. SparseBooleanArray — `Int` → `Boolean`**

```kotlin
import android.util.SparseBooleanArray

val selectedItems = SparseBooleanArray()
selectedItems.put(0, true)
selectedItems.put(5, true)

fun isSelected(position: Int): Boolean {
 return selectedItems.get(position, false)
}
```

**4. LongSparseArray\<E\> — `Long` → Object**

```kotlin
import android.util.LongSparseArray

val timestampCache = LongSparseArray<Event>()
val timestamp = System.currentTimeMillis()
timestampCache.put(timestamp, Event("Click"))
```

### Performance

**`HashMap` problems:**
- `Int` → Integer requires 16 bytes instead of 4
- Every operation creates temporary objects
- Increased GC pressure
- Hash table requires additional memory

**SparseArray advantages:**
- No boxing: primitives stored directly
- ~50% less memory (24 vs 56 bytes per entry)
- Faster for < 1000 elements
- Less GC pressure

**Limitations:**
- O(log n) lookup vs O(1) in `HashMap`
- Slower for > 10K elements
- Optimized for sequential keys
- Not thread-safe

### Practical Use Cases

**`RecyclerView` adapter:**
```kotlin
class Adapter : RecyclerView.Adapter<ViewHolder>() {
 private val expandedItems = SparseBooleanArray() // ✅ State flags

 fun toggleExpanded(position: Int) {
 val isExpanded = expandedItems.get(position, false)
 expandedItems.put(position, !isExpanded)
 notifyItemChanged(position)
 }
}
```

**`ViewModel` with cache:**
```kotlin
class UserViewModel : ViewModel() {
 private val users = SparseArray<User>() // ✅ Int → User
 private val favorites = SparseBooleanArray() // ✅ Int → Boolean
 private val scores = SparseIntArray() // ✅ Int → Int

 fun toggleFavorite(userId: Int) {
 val isFavorite = favorites.get(userId, false)
 favorites.put(userId, !isFavorite)
 }

 override fun onCleared() {
 users.clear()
 favorites.clear()
 scores.clear()
 }
}
```

**Loading state:**
```kotlin
class StateManager {
 private val loadingStates = SparseBooleanArray() // ✅ Loading flags
 private val errorCounts = SparseIntArray() // ✅ Error counters
 private val dataCache = SparseArray<Data>() // ✅ Data cache

 fun startLoading(id: Int) {
 loadingStates.put(id, true)
 }

 fun isLoading(id: Int): Boolean = loadingStates.get(id, false)
}
```

### Usage Guidelines

**Use SparseArray when:**
- `Collection` < 1000 elements
- Keys are sequential `Int`/`Long`
- Memory efficiency is important
- Single-threaded access

**Use `HashMap` when:**
- `Collection` > 10K elements
- Keys are random or unsorted
- O(1) lookup speed is critical
- Multi-threaded access needed (ConcurrentHashMap)

### Migration from `HashMap`

```kotlin
// ❌ Before: HashMap with boxing
val cache = HashMap<Int, String>()
cache[id] = value
cache.remove(id)
cache.containsKey(id)

// ✅ After: SparseArray without boxing
val cache = SparseArray<String>()
cache.put(id, value)
cache.remove(id)
cache.indexOfKey(id) >= 0
```

---

## Follow-ups

- What happens when SparseArray runs out of capacity? Does it automatically resize like `ArrayList`?
- How does SparseArray handle concurrent modifications? What exceptions might be thrown?
- Can you use SparseArray with Jetpack Compose State? Are there any considerations?
- How do you implement thread-safe access to SparseArray without significant performance degradation?
- What are the memory implications of storing large objects as values in SparseArray?

## References

- Android SDK Documentation: [SparseArray](https://developer.android.com/reference/android/util/SparseArray)
- Android Performance Patterns: [Memory Churn and Performance](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)
- 
- 

## Related Questions

### Prerequisites
- - Understanding autoboxing overhead
- - How `HashMap` works internally

### Related
- [[q-reduce-apk-size-techniques--android--medium]] - Memory optimization techniques
- [[q-where-is-composition-created--android--medium]] - State management in Compose
- [[q-recyclerview-explained--android--medium]] - `RecyclerView` performance patterns

### Advanced
- - Profiling memory usage with Android Studio
- - Implementing custom optimized collections
