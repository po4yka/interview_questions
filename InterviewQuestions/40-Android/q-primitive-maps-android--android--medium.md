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
related: [c-android, q-recyclerview-explained--android--medium, q-reduce-apk-size-techniques--android--medium, q-where-is-composition-created--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-memory, collections, difficulty/medium, memory-optimization, performance]

date created: Saturday, November 1st 2025, 1:03:50 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)

> Какие специализированные `Map`-коллекции для примитивных типов предоставляет Android SDK? Когда и почему их следует использовать вместо стандартных `HashMap`?

# Question (EN)

> What specialized `Map` collections for primitive types does Android SDK provide? When and why should they be used instead of standard `HashMap`?

---

## Ответ (RU)

Android предоставляет оптимизированные коллекции для целочисленных ключей и примитивных значений, которые минимизируют автоупаковку (boxing) и часто оказываются более эффективными по памяти, чем стандартные `HashMap` при работе с относительно небольшими коллекциями (порядка сотен элементов).

См. также: [[c-android]].

### Основные Типы

**1. `SparseArray<E>` — `Int` → Object**

```kotlin
import android.util.SparseArray

val userCache = SparseArray<User>()
userCache.put(1, User("Alice"))
userCache.put(100, User("Bob"))

val user = userCache.get(1)  // ✅ Нет boxing для ключа (int хранится как примитив)
val size = userCache.size()
```

**2. SparseIntArray — `Int` → `Int`**

```kotlin
import android.util.SparseIntArray

val viewCounts = SparseIntArray()
viewCounts.put(101, 95)

fun incrementCount(id: Int) {
    val current = viewCounts.get(id, 0)  // ✅ Значение по умолчанию: 0
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

**4. `LongSparseArray<E>` — `Long` → Object**

```kotlin
import android.util.LongSparseArray

val timestampCache = LongSparseArray<Event>()
val timestamp = System.currentTimeMillis()
timestampCache.put(timestamp, Event("Click"))
```

(В современных проектах также часто используют реализации из `androidx.collection.*`, например `androidx.collection.LongSparseArray`, которые обеспечивают аналогичное поведение.)

### Производительность

**`HashMap`: особенности при использовании примитивных ключей/значений:**
- Для хранения примитивов используются объекты-обёртки (например, `Int` → `Integer`), что приводит к дополнительным накладным расходам по памяти и может создавать лишние объекты.
- Дополнительная структура хэш-таблицы занимает память сверх самих записей.

**SparseArray и аналоги: преимущества:**
- Нет boxing для ключей типа `int`/`long` (они хранятся во внутренних массивах примитивов).
- Меньше накладных расходов по памяти по сравнению с `HashMap<`Int`, T>` или `HashMap<`Long`, T>`; на практических измерениях часто выигрывает порядка десятков процентов, но точные значения зависят от реализации и версии платформы.
- Снижение давления на GC за счёт уменьшения количества объектов.

**Ограничения и нюансы:**
- Поиск — O(log n), так как ключи хранятся в отсортированном массиве и используется бинарный поиск, в то время как у `HashMap` ожидаемо O(1) в среднем.
- При очень больших коллекциях (тысячи–десятки тысяч элементов и выше) `HashMap` часто оказывается быстрее по времени доступа; точка перелома зависит от конкретного сценария и профилирования.
- Эффективнее всего при работе с целочисленными ключами, которые относительно упорядочены или добавляются монотонно (особенно при использовании `append()`), но не требуется строго последовательных значений.
- Не являются потокобезопасными (аналогично обычному `HashMap`).

### Практическое Применение

**RecyclerView адаптер:**
```kotlin
class Adapter : RecyclerView.Adapter<ViewHolder>() {
    private val expandedItems = SparseBooleanArray()  // ✅ Флаги состояния по позициям/ID

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
    private val users = SparseArray<User>()          // ✅ Int → User
    private val favorites = SparseBooleanArray()     // ✅ Int → Boolean
    private val scores = SparseIntArray()            // ✅ Int → Int

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
    private val loadingStates = SparseBooleanArray()  // ✅ Флаги загрузки
    private val errorCounts = SparseIntArray()        // ✅ Счётчики ошибок
    private val dataCache = SparseArray<Data>()       // ✅ Кэш данных

    fun startLoading(id: Int) {
        loadingStates.put(id, true)
    }

    fun isLoading(id: Int): Boolean = loadingStates.get(id, false)
}
```

### Правила Использования

**Используйте SparseArray и родственные коллекции когда:**
- Ключи — целочисленные (`int` или `long`), значения часто примитивные или объекты, привязанные к таким ключам (ID ресурсов, view ID, позиции и т.п.).
- Важна экономия памяти и снижение количества объектов-обёрток.
- Размер коллекции обычно не слишком велик (сотни–несколько тысяч элементов), и профилирование показывает выигрыши.
- Доступ — из одного потока или вы сами обеспечиваете синхронизацию.

**Используйте `HashMap` (или `ConcurrentHashMap`) когда:**
- Нужны произвольные типы ключей (`String`, сложные объекты и т.п.).
- Коллекция очень большая и критично среднее время доступа O(1).
- Требуется потокобезопасный доступ (например, `ConcurrentHashMap`), или проще масштабировать через стандартные concurrent-структуры.

### Миграция С `HashMap`

```kotlin
// ❌ До: HashMap с boxing для ключей Int
val cache = HashMap<Int, String>()
cache[id] = value
cache.remove(id)
cache.containsKey(id)

// ✅ После: SparseArray без boxing для ключей
val cache2 = SparseArray<String>()
cache2.put(id, value)
cache2.remove(id)
val exists = cache2.indexOfKey(id) >= 0
```

---

## Answer (EN)

Android provides optimized collections for integer keys and primitive-like mappings that minimize boxing overhead and can be more memory-efficient than standard `HashMap` when dealing with relatively small to moderate collections (on the order of hundreds of elements) with int/long keys.

See also: [[c-android]].

### Main Types

**1. `SparseArray<E>` — `Int` → Object**

```kotlin
import android.util.SparseArray

val userCache = SparseArray<User>()
userCache.put(1, User("Alice"))
userCache.put(100, User("Bob"))

val user = userCache.get(1)  // ✅ No boxing for the int key
val size = userCache.size()
```

**2. SparseIntArray — `Int` → `Int`**

```kotlin
import android.util.SparseIntArray

val viewCounts = SparseIntArray()
viewCounts.put(101, 95)

fun incrementCount(id: Int) {
    val current = viewCounts.get(id, 0)  // ✅ Default value: 0
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

**4. `LongSparseArray<E>` — `Long` → Object**

```kotlin
import android.util.LongSparseArray

val timestampCache = LongSparseArray<Event>()
val timestamp = System.currentTimeMillis()
timestampCache.put(timestamp, Event("Click"))
```

(In modern projects you may also use `androidx.collection.*` variants such as `androidx.collection.LongSparseArray` which provide similar behavior.)

### Performance

**`HashMap` characteristics when used with primitive-like keys/values:**
- Requires wrapper objects (e.g., `Int` → `Integer`) for primitive keys/values, which adds memory overhead and may create additional objects.
- Hash table structure itself introduces extra memory overhead.

**SparseArray-family advantages:**
- No boxing for int/long keys (stored in primitive arrays internally).
- Lower memory overhead compared to `HashMap<`Int`, T>` / `HashMap<`Long`, T>` in many practical scenarios; the exact numbers are implementation-dependent.
- Reduced GC pressure due to fewer allocated objects.

**Limitations and trade-offs:**
- Lookup is O(log n) because keys are stored in a sorted array and found via binary search; `HashMap` offers expected O(1) average-time lookup.
- For very large maps (thousands to tens of thousands of entries and above), `HashMap` often wins in raw access speed; the crossover point is heuristic and should be validated with profiling.
- Works best with integer keys that are relatively ordered or append-increasing (especially when using `append()`), but keys do not have to be strictly sequential.
- Not thread-safe (similar to regular `HashMap`).

### Practical Use Cases

**RecyclerView adapter:**
```kotlin
class Adapter : RecyclerView.Adapter<ViewHolder>() {
    private val expandedItems = SparseBooleanArray()  // ✅ State flags by position/ID

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
    private val users = SparseArray<User>()          // ✅ Int → User
    private val favorites = SparseBooleanArray()     // ✅ Int → Boolean
    private val scores = SparseIntArray()            // ✅ Int → Int

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
    private val loadingStates = SparseBooleanArray()  // ✅ Loading flags
    private val errorCounts = SparseIntArray()        // ✅ Error counters
    private val dataCache = SparseArray<Data>()       // ✅ Data cache

    fun startLoading(id: Int) {
        loadingStates.put(id, true)
    }

    fun isLoading(id: Int): Boolean = loadingStates.get(id, false)
}
```

### Usage Guidelines

**Use SparseArray and related collections when:**
- Keys are integers (`int` or `long`), often representing IDs, positions, or resource identifiers.
- Memory efficiency and reduced allocations/GC are important.
- Collection size is typically not extremely large (hundreds to a few thousands), and profiling indicates benefits.
- Access is single-threaded, or you provide your own synchronization.

**Use `HashMap` (or `ConcurrentHashMap`) when:**
- You need arbitrary key types (`String`, complex objects, etc.).
- The map is very large and O(1) average-time lookup is critical.
- You require thread-safe access and prefer using standard concurrent collections.

### Migration from `HashMap`

```kotlin
// ❌ Before: HashMap with boxing for Int keys
val cache = HashMap<Int, String>()
cache[id] = value
cache.remove(id)
cache.containsKey(id)

// ✅ After: SparseArray without boxing for keys
val cache2 = SparseArray<String>()
cache2.put(id, value)
cache2.remove(id)
val exists = cache2.indexOfKey(id) >= 0
```

---

## Дополнительные Вопросы (RU)

- Что происходит, когда `SparseArray` исчерпывает ёмкость? Масштабируется ли она автоматически, как `ArrayList`?
- Как `SparseArray` ведёт себя при конкурентных модификациях? Какие исключения могут возникать?
- Можно ли использовать `SparseArray` вместе с состоянием в Jetpack Compose? Какие есть особенности?
- Как реализовать потокобезопасный доступ к `SparseArray` без существенной потери производительности?
- Каковы особенности потребления памяти при хранении крупных объектов в качестве значений в `SparseArray`?

## Follow-ups

- What happens when SparseArray runs out of capacity? Does it automatically resize like `ArrayList`?
- How does SparseArray handle concurrent modifications? What exceptions might be thrown?
- Can you use SparseArray with Jetpack Compose State? Are there any considerations?
- How do you implement thread-safe access to SparseArray without significant performance degradation?
- What are the memory implications of storing large objects as values in SparseArray?

## Ссылки (RU)

- Документация Android SDK: [SparseArray](https://developer.android.com/reference/android/util/SparseArray)
- Android Performance Patterns: [Memory Churn and Performance](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)

## References

- Android SDK Documentation: [SparseArray](https://developer.android.com/reference/android/util/SparseArray)
- Android Performance Patterns: [Memory Churn and Performance](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-reduce-apk-size-techniques--android--medium]] — Подходы к оптимизации размера и косвенно памяти
- [[q-where-is-composition-created--android--medium]] — Управление состоянием в Compose

### Похожие
- [[q-recyclerview-explained--android--medium]] — Паттерны производительности RecyclerView

## Related Questions

### Prerequisites
- [[q-reduce-apk-size-techniques--android--medium]] - Memory optimization techniques
- [[q-where-is-composition-created--android--medium]] - State management in Compose

### Related
- [[q-recyclerview-explained--android--medium]] - RecyclerView performance patterns
