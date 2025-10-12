---
topic: android
tags:
  - android
  - performance
  - collections
  - memory-optimization
difficulty: medium
status: draft
---

# Примитивные коллекции Map в Android

**English**: Primitive Map Collections in Android (SparseArray, SparseIntArray, SparseBooleanArray, LongSparseArray)

## Answer (EN)
В Android существуют специализированные Map-коллекции, которые позволяют хранить примитивные типы данных без автоупаковки (boxing), что значительно улучшает производительность и снижает потребление памяти. Обычные `HashMap<Int, Int>` в Kotlin используют автоупаковку примитивов в объекты (Integer), что увеличивает потребление памяти и замедляет работу приложения.

### Проблема автоупаковки в стандартных Map

```kotlin
// - ПЛОХО: Стандартный HashMap с автоупаковкой
val standardMap = HashMap<Int, String>() // Int упаковывается в Integer

for (i in 0..1000) {
    standardMap[i] = "Value $i"
    // Каждый Int ключ создаёт новый объект Integer
    // Это занимает 16 байт вместо 4 байт для примитивного int
}

// Проблемы:
// 1. Автоупаковка: Int → Integer (объект)
// 2. Больше памяти: Integer = 16 байт, int = 4 байта
// 3. Больше GC: каждый объект Integer нужно собирать
// 4. Медленнее: boxing/unboxing при каждой операции
```

### Решение: Специализированные коллекции android.util

Android SDK предоставляет оптимизированные коллекции для работы с примитивными типами:

#### 1. SparseArray<E> - Map<Int, E>

Замена для `HashMap<Int, E>` (Int ключи, любые значения):

```kotlin
import android.util.SparseArray

// - ХОРОШО: SparseArray для Int → Object
val userCache = SparseArray<User>()

userCache.put(1, User("Alice", 25))
userCache.put(2, User("Bob", 30))
userCache.put(100, User("Charlie", 35))

// Получение значения
val user = userCache.get(1) // User("Alice", 25)
val notFound = userCache.get(999) // null

// Получение с дефолтным значением
val defaultUser = userCache.get(999, User("Unknown", 0))

// Размер коллекции
val size = userCache.size() // 3

// Удаление элемента
userCache.delete(2)
userCache.remove(2) // альтернатива delete()

// Очистка коллекции
userCache.clear()

// Итерация по элементам
for (i in 0 until userCache.size()) {
    val key = userCache.keyAt(i)
    val value = userCache.valueAt(i)
    println("Key: $key, Value: $value")
}

// Проверка наличия ключа
if (userCache.indexOfKey(1) >= 0) {
    println("Key 1 exists")
}
```

#### 2. SparseIntArray - Map<Int, Int>

Замена для `HashMap<Int, Int>` (оба типа Int):

```kotlin
import android.util.SparseIntArray

// - ХОРОШО: SparseIntArray для Int → Int
val scores = SparseIntArray()

scores.put(101, 95) // userId → score
scores.put(102, 87)
scores.put(103, 92)

// Получение значения
val score = scores.get(101) // 95
val notFound = scores.get(999, -1) // -1 (default)

// Обновление значения
scores.put(101, 98) // Update score

// Итерация
for (i in 0 until scores.size()) {
    val userId = scores.keyAt(i)
    val userScore = scores.valueAt(i)
    println("User $userId: Score $userScore")
}

// Пример: кэш счётчиков
class ViewCountTracker {
    private val viewCounts = SparseIntArray()

    fun incrementViewCount(itemId: Int) {
        val currentCount = viewCounts.get(itemId, 0)
        viewCounts.put(itemId, currentCount + 1)
    }

    fun getViewCount(itemId: Int): Int {
        return viewCounts.get(itemId, 0)
    }

    fun getTotalViews(): Int {
        var total = 0
        for (i in 0 until viewCounts.size()) {
            total += viewCounts.valueAt(i)
        }
        return total
    }
}
```

#### 3. SparseBooleanArray - Map<Int, Boolean>

Замена для `HashMap<Int, Boolean>`:

```kotlin
import android.util.SparseBooleanArray

// - ХОРОШО: SparseBooleanArray для Int → Boolean
val selectedItems = SparseBooleanArray()

// Отметить элементы как выбранные
selectedItems.put(0, true)
selectedItems.put(5, true)
selectedItems.put(10, false)

// Проверить выбран ли элемент
val isSelected = selectedItems.get(0) // true
val notSelected = selectedItems.get(100, false) // false (default)

// Переключить состояние
fun toggleSelection(position: Int, array: SparseBooleanArray) {
    val currentState = array.get(position, false)
    array.put(position, !currentState)
}

// Пример: выбор элементов в RecyclerView
class RecyclerViewAdapter(private val items: List<String>) :
    RecyclerView.Adapter<RecyclerViewAdapter.ViewHolder>() {

    private val selectedPositions = SparseBooleanArray()

    fun toggleSelection(position: Int) {
        val isSelected = selectedPositions.get(position, false)
        selectedPositions.put(position, !isSelected)
        notifyItemChanged(position)
    }

    fun clearSelection() {
        selectedPositions.clear()
        notifyDataSetChanged()
    }

    fun getSelectedCount(): Int {
        var count = 0
        for (i in 0 until selectedPositions.size()) {
            if (selectedPositions.valueAt(i)) {
                count++
            }
        }
        return count
    }

    fun getSelectedPositions(): List<Int> {
        val positions = mutableListOf<Int>()
        for (i in 0 until selectedPositions.size()) {
            if (selectedPositions.valueAt(i)) {
                positions.add(selectedPositions.keyAt(i))
            }
        }
        return positions
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val isSelected = selectedPositions.get(position, false)
        holder.bind(items[position], isSelected)
    }

    // ... other methods

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(item: String, isSelected: Boolean) {
            // Update UI based on selection
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        TODO("Not yet implemented")
    }

    override fun getItemCount(): Int = items.size
}
```

#### 4. LongSparseArray<E> - Map<Long, E>

Замена для `HashMap<Long, E>` (Long ключи):

```kotlin
import android.util.LongSparseArray

// - ХОРОШО: LongSparseArray для Long → Object
val timestampCache = LongSparseArray<Event>()

data class Event(val name: String, val data: String)

// Использование timestamp как ключа
val timestamp1 = System.currentTimeMillis()
timestampCache.put(timestamp1, Event("Click", "Button A"))

val timestamp2 = System.currentTimeMillis() + 1000
timestampCache.put(timestamp2, Event("Scroll", "List View"))

// Получение события по timestamp
val event = timestampCache.get(timestamp1)

// Пример: кэш с временными метками
class TimestampedCache<T> {
    private val cache = LongSparseArray<T>()
    private val ttlMs = 60_000L // 1 минута

    fun put(key: Long, value: T) {
        cache.put(key, value)
        cleanupOldEntries()
    }

    fun get(key: Long): T? {
        return cache.get(key)
    }

    private fun cleanupOldEntries() {
        val now = System.currentTimeMillis()
        val keysToRemove = mutableListOf<Long>()

        for (i in 0 until cache.size()) {
            val key = cache.keyAt(i)
            if (now - key > ttlMs) {
                keysToRemove.add(key)
            }
        }

        keysToRemove.forEach { cache.remove(it) }
    }
}
```

### Сравнение производительности

```kotlin
import android.os.SystemClock
import android.util.Log
import android.util.SparseArray

class PerformanceComparison {

    fun compareHashMapVsSparseArray() {
        val iterations = 10_000

        // Тест 1: HashMap<Int, String>
        val hashMapStart = SystemClock.elapsedRealtimeNanos()
        val hashMap = HashMap<Int, String>()
        for (i in 0 until iterations) {
            hashMap[i] = "Value $i"
        }
        val hashMapEnd = SystemClock.elapsedRealtimeNanos()
        val hashMapTime = (hashMapEnd - hashMapStart) / 1_000_000.0

        // Тест 2: SparseArray<String>
        val sparseArrayStart = SystemClock.elapsedRealtimeNanos()
        val sparseArray = SparseArray<String>()
        for (i in 0 until iterations) {
            sparseArray.put(i, "Value $i")
        }
        val sparseArrayEnd = SystemClock.elapsedRealtimeNanos()
        val sparseArrayTime = (sparseArrayEnd - sparseArrayStart) / 1_000_000.0

        Log.d("Performance", """
            HashMap time: ${hashMapTime}ms
            SparseArray time: ${sparseArrayTime}ms
            SparseArray is ${hashMapTime / sparseArrayTime}x faster
        """.trimIndent())

        // Память
        val hashMapMemory = estimateHashMapMemory(iterations)
        val sparseArrayMemory = estimateSparseArrayMemory(iterations)

        Log.d("Memory", """
            HashMap estimated memory: ${hashMapMemory / 1024}KB
            SparseArray estimated memory: ${sparseArrayMemory / 1024}KB
            Memory saved: ${(hashMapMemory - sparseArrayMemory) / 1024}KB
        """.trimIndent())
    }

    private fun estimateHashMapMemory(size: Int): Long {
        // HashMap entry: ~32 bytes overhead per entry
        // Integer object: ~16 bytes
        // String reference: ~8 bytes
        // Total: ~56 bytes per entry
        return size * 56L
    }

    private fun estimateSparseArrayMemory(size: Int): Long {
        // SparseArray: ~12 bytes per entry
        // int key: 4 bytes
        // Object reference: 8 bytes
        // Total: ~24 bytes per entry
        return size * 24L
    }
}

// Результаты (примерные):
// HashMap time: 15.2ms
// SparseArray time: 8.7ms
// SparseArray is 1.75x faster
//
// HashMap estimated memory: 546KB
// SparseArray estimated memory: 234KB
// Memory saved: 312KB
```

### Когда использовать каждый тип

```kotlin
// 1. SparseArray<E>: Int → Object
// Используйте для: кэш объектов по ID, маппинг позиций в списке
val userCache = SparseArray<User>()
val viewCache = SparseArray<View>()
val adapterData = SparseArray<ListItem>()

// 2. SparseIntArray: Int → Int
// Используйте для: счётчики, индексы, ID маппинги
val positionToId = SparseIntArray()
val viewCounts = SparseIntArray()
val scores = SparseIntArray()

// 3. SparseBooleanArray: Int → Boolean
// Используйте для: флаги состояния, выбор элементов в списке
val selectedItems = SparseBooleanArray()
val expandedGroups = SparseBooleanArray()
val visibilityFlags = SparseBooleanArray()

// 4. LongSparseArray<E>: Long → Object
// Используйте для: timestamp → данные, ID базы данных
val timestampCache = LongSparseArray<Event>()
val dbIdToObject = LongSparseArray<DatabaseEntity>()
```

### Ограничения и особенности

#### 1. Производительность для больших коллекций

```kotlin
// WARNING: ВАЖНО: SparseArray медленнее для больших коллекций
// SparseArray использует бинарный поиск: O(log n)
// HashMap использует хэш-таблицу: O(1)

// Рекомендации по размеру:
// • < 1000 элементов → SparseArray быстрее
// • > 1000 элементов → HashMap может быть быстрее

class SizeRecommendation {
    fun chooseCollection(expectedSize: Int): String {
        return when {
            expectedSize < 100 -> "Use SparseArray - best performance"
            expectedSize < 1000 -> "Use SparseArray - good performance"
            expectedSize < 10000 -> "Consider HashMap if speed critical"
            else -> "Use HashMap - better for large collections"
        }
    }
}
```

#### 2. Несортированные ключи

```kotlin
// WARNING: SparseArray оптимизирован для последовательных ключей
// Лучший случай: 0, 1, 2, 3, 4...
// Худший случай: 1000, 5, 999, 2, 888...

// - ХОРОШО: Последовательные ключи
val sequential = SparseArray<String>()
for (i in 0..100) {
    sequential.put(i, "Value $i")
}

// - ПЛОХО: Случайные ключи
val random = SparseArray<String>()
val randomKeys = listOf(1000, 5, 999, 2, 888, 42, 777)
randomKeys.forEach { key ->
    random.put(key, "Value $key")
    // Каждая вставка может требовать пересортировки
}
```

#### 3. Не thread-safe

```kotlin
// WARNING: SparseArray НЕ THREAD-SAFE!

// - ПЛОХО: Небезопасное использование в многопоточной среде
val sharedArray = SparseArray<String>()

thread {
    sharedArray.put(1, "Thread 1")
}

thread {
    sharedArray.put(2, "Thread 2")
}
// Может привести к ConcurrentModificationException

// - ХОРОШО: Использовать синхронизацию
class ThreadSafeSparseArray<E> {
    private val array = SparseArray<E>()
    private val lock = Any()

    fun put(key: Int, value: E) {
        synchronized(lock) {
            array.put(key, value)
        }
    }

    fun get(key: Int): E? {
        synchronized(lock) {
            return array.get(key)
        }
    }
}

// Или использовать ConcurrentHashMap для многопоточного доступа
val threadSafeMap = ConcurrentHashMap<Int, String>()
```

### Практические примеры использования

#### Пример 1: Адаптер с кэшем View

```kotlin
class OptimizedRecyclerAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    // Кэш ViewHolder по позиции
    private val viewHolderCache = SparseArray<RecyclerView.ViewHolder>()

    // Кэш размеров View
    private val viewHeights = SparseIntArray()

    // Флаги развёрнутых элементов
    private val expandedItems = SparseBooleanArray()

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        // Кэшировать ViewHolder
        viewHolderCache.put(position, holder)

        // Проверить развёрнут ли элемент
        val isExpanded = expandedItems.get(position, false)

        // Получить высоту из кэша
        val cachedHeight = viewHeights.get(position, -1)
        if (cachedHeight > 0) {
            holder.itemView.layoutParams.height = cachedHeight
        }
    }

    fun toggleExpanded(position: Int) {
        val wasExpanded = expandedItems.get(position, false)
        expandedItems.put(position, !wasExpanded)
        notifyItemChanged(position)
    }

    override fun onViewRecycled(holder: RecyclerView.ViewHolder) {
        super.onViewRecycled(holder)

        // Сохранить высоту View перед переработкой
        val position = holder.adapterPosition
        if (position != RecyclerView.NO_POSITION) {
            viewHeights.put(position, holder.itemView.height)
            viewHolderCache.remove(position)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        TODO("Not yet implemented")
    }

    override fun getItemCount(): Int = 0
}
```

#### Пример 2: Менеджер состояния

```kotlin
class StateManager {

    // Состояния загрузки по ID
    private val loadingStates = SparseBooleanArray()

    // Счётчики ошибок по ID
    private val errorCounts = SparseIntArray()

    // Кэш данных по ID
    private val dataCache = SparseArray<Data>()

    // Временные метки последнего обновления
    private val lastUpdateTimes = LongSparseArray<Long>()

    data class Data(val id: Int, val content: String)

    fun startLoading(id: Int) {
        loadingStates.put(id, true)
    }

    fun finishLoading(id: Int, data: Data) {
        loadingStates.put(id, false)
        dataCache.put(id, data)
        lastUpdateTimes.put(id.toLong(), System.currentTimeMillis())
        errorCounts.put(id, 0) // Reset error count on success
    }

    fun onError(id: Int) {
        loadingStates.put(id, false)
        val currentErrors = errorCounts.get(id, 0)
        errorCounts.put(id, currentErrors + 1)
    }

    fun isLoading(id: Int): Boolean {
        return loadingStates.get(id, false)
    }

    fun getData(id: Int): Data? {
        return dataCache.get(id)
    }

    fun shouldRetry(id: Int, maxRetries: Int = 3): Boolean {
        val errors = errorCounts.get(id, 0)
        return errors < maxRetries
    }

    fun isCacheValid(id: Int, ttlMs: Long = 300_000): Boolean {
        val lastUpdate = lastUpdateTimes.get(id.toLong()) ?: return false
        val now = System.currentTimeMillis()
        return (now - lastUpdate) < ttlMs
    }

    fun clearCache() {
        dataCache.clear()
        loadingStates.clear()
        errorCounts.clear()
        lastUpdateTimes.clear()
    }
}
```

#### Пример 3: Оптимизация памяти в ViewModel

```kotlin
class UserViewModel : ViewModel() {

    // Вместо HashMap<Int, User>
    private val users = SparseArray<User>()

    // Вместо HashMap<Int, Boolean>
    private val favorites = SparseBooleanArray()

    // Вместо HashMap<Int, Int>
    private val userScores = SparseIntArray()

    data class User(val id: Int, val name: String, val email: String)

    fun loadUsers(userList: List<User>) {
        userList.forEach { user ->
            users.put(user.id, user)
        }
    }

    fun toggleFavorite(userId: Int) {
        val isFavorite = favorites.get(userId, false)
        favorites.put(userId, !isFavorite)
    }

    fun updateScore(userId: Int, score: Int) {
        userScores.put(userId, score)
    }

    fun getUserWithFavoriteStatus(userId: Int): Pair<User?, Boolean> {
        val user = users.get(userId)
        val isFavorite = favorites.get(userId, false)
        return Pair(user, isFavorite)
    }

    fun getTopUsers(count: Int): List<Pair<User, Int>> {
        val results = mutableListOf<Pair<User, Int>>()

        for (i in 0 until userScores.size()) {
            val userId = userScores.keyAt(i)
            val score = userScores.valueAt(i)
            val user = users.get(userId)

            if (user != null) {
                results.add(Pair(user, score))
            }
        }

        return results
            .sortedByDescending { it.second }
            .take(count)
    }

    override fun onCleared() {
        super.onCleared()
        users.clear()
        favorites.clear()
        userScores.clear()
    }
}
```

### Миграция с HashMap на SparseArray

```kotlin
// До: HashMap
class BeforeOptimization {
    private val cache = HashMap<Int, String>()

    fun put(id: Int, value: String) {
        cache[id] = value
    }

    fun get(id: Int): String? {
        return cache[id]
    }

    fun remove(id: Int) {
        cache.remove(id)
    }

    fun clear() {
        cache.clear()
    }

    fun containsKey(id: Int): Boolean {
        return cache.containsKey(id)
    }

    fun getSize(): Int {
        return cache.size
    }
}

// После: SparseArray
class AfterOptimization {
    private val cache = SparseArray<String>()

    fun put(id: Int, value: String) {
        cache.put(id, value) // или cache[id] = value (Kotlin)
    }

    fun get(id: Int): String? {
        return cache.get(id) // или cache[id] (Kotlin)
    }

    fun remove(id: Int) {
        cache.remove(id) // или cache.delete(id)
    }

    fun clear() {
        cache.clear()
    }

    fun containsKey(id: Int): Boolean {
        return cache.indexOfKey(id) >= 0
    }

    fun getSize(): Int {
        return cache.size()
    }
}
```

### Best Practices

1. **Используйте SparseArray вместо HashMap<Int, ?>** для коллекций < 1000 элементов
2. **Используйте SparseIntArray** вместо HashMap<Int, Int> для счётчиков и индексов
3. **Используйте SparseBooleanArray** для флагов состояния в RecyclerView
4. **Используйте LongSparseArray** для работы с timestamp или database ID
5. **Избегайте случайных ключей** - SparseArray оптимизирован для последовательных ключей
6. **Добавьте синхронизацию** для многопоточного доступа
7. **Для коллекций > 10000** элементов рассмотрите HashMap
8. **Очищайте коллекции** в onDestroy/onCleared для предотвращения утечек памяти

### Производительность: Ключевые метрики

| Коллекция | Память на элемент | Скорость (< 1000) | Скорость (> 10000) |
|-----------|-------------------|-------------------|---------------------|
| HashMap<Int, E> | ~56 байт | Средняя | Быстрая (O(1)) |
| SparseArray<E> | ~24 байт | Быстрая | Средняя (O(log n)) |
| SparseIntArray | ~12 байт | Очень быстрая | Средняя (O(log n)) |
| SparseBooleanArray | ~8 байт | Очень быстрая | Средняя (O(log n)) |

### Common Pitfalls

1. **Использование для больших коллекций** - SparseArray медленнее HashMap при > 10K элементов
2. **Небезопасная многопоточность** - всегда добавляйте синхронизацию
3. **Случайные ключи** - ухудшают производительность
4. **Забывать очищать** - может привести к утечкам памяти

**English**: Android provides specialized Map collections for primitive types (SparseArray, SparseIntArray, SparseBooleanArray, LongSparseArray) that avoid boxing overhead. These collections use ~50% less memory and are faster for collections under 1000 elements. Use SparseArray for Int→Object, SparseIntArray for Int→Int, SparseBooleanArray for Int→Boolean, and LongSparseArray for Long→Object mappings. Best for RecyclerView item states, caches, and counters.
