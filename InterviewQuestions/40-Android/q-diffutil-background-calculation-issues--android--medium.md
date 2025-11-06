---
id: android-473
title: DiffUtil Background Calculation Issues / Проблемы фонового вычисления DiffUtil
aliases:
- DiffUtil Background Calculation Issues
- DiffUtil background issues
- Проблемы DiffUtil в фоне
- Проблемы фонового вычисления DiffUtil
topic: android
subtopics:
- performance-memory
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- c-memory-management
- q-main-causes-ui-lag--android--medium
created: 2025-10-20
updated: 2025-11-02
tags:
- android/performance-memory
- android/ui-views
- difficulty/medium
- diffutil
- performance
- recyclerview
sources:
- https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
---

# Вопрос (RU)
> Когда фоновое вычисление DiffUtil работает плохо?

# Question (EN)
> When does DiffUtil background calculation work poorly?

---

## Ответ (RU)

`DiffUtil` — утилита для вычисления различий между двумя списками и применения обновлений к `RecyclerView`. При фоновом вычислении (`calculateDiff()` на фоновом потоке) возникают проблемы при изменении данных во время расчета, тяжелых вычислениях в callback, больших списках (>1000 элементов), неправильной обработке ошибок, и race conditions между потоками. Понимание этих проблем критично для оптимизации производительности `RecyclerView`.

### Основные Проблемы

**1. Изменение данных во время расчета**

**Проблема:**

Исходный список изменяется другим потоком (обычно главным потоком UI) во время выполнения `calculateDiff()` на фоновом потоке. Это приводит к:
- `IndexOutOfBoundsException` — доступ к индексу, который больше не существует
- Некорректным diff операциям — `DiffUtil` вычисляет diff на основе устаревших данных
- Race conditions — состояние списка изменяется между вызовами `getOldListSize()` и `areItemsTheSame()`

**Решение:**

Создание неизменяемой копии списка перед запуском фонового вычисления:

```kotlin
// ❌ ПЛОХО - данные могут измениться во время расчета
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // ⚠️ users может измениться!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // ⚠️ IndexOutOfBoundsException
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}

// ✅ ХОРОШО - неизменяемая копия данных перед расчетом
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Создание копии на главном потоке
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size // Безопасный доступ к копии
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}
```

**2. Тяжелые вычисления в callback**

**Проблема:**

Сложные операции в `areContentsTheSame()` вызываются многократно во время расчета `DiffUtil` (до O(N²) раз для алгоритма). Даже на фоновом потоке это может привести к:
- Долгим вычислениям — `DiffUtil` блокируется на тяжелых операциях
- Повторным вычислениям — одни и те же данные обрабатываются несколько раз
- Увеличению времени расчета — общее время расчета увеличивается пропорционально сложности callback

**Решение:**

Кэширование результатов тяжелых вычислений вне callback:

```kotlin
// ❌ ПЛОХО - парсинг JSON в callback (вызывается O(N²) раз)
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // ⚠️ Парсинг JSON каждый раз при сравнении (очень медленно!)
        val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldData == newData
    }

    // ... другие методы
}

// ✅ ХОРОШО - кэширование результатов перед callback
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    // Кэширование распарсенных данных один раз
    private val oldDataCache = oldList.map {
        Json.decodeFromString<MessageData>(it.jsonData)
    }
    private val newDataCache = newList.map {
        Json.decodeFromString<MessageData>(it.jsonData)
    }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // Быстрое сравнение закэшированных данных
        return oldDataCache[oldPos] == newDataCache[newPos]
    }

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size
    override fun areItemsTheSame(oldPos: Int, newPos: Int) =
        oldList[oldPos].id == newList[newPos].id
}
```

**3. Большие списки**

**Проблема:**

`DiffUtil` использует алгоритм `Myers` для вычисления различий, который имеет временную сложность O(N²) в худшем случае. Для больших списков (>1000 элементов) это приводит к:
- Долгим вычислениям — расчет может занимать секунды даже на фоновом потоке
- Блокировке фонового потока — другие операции не выполняются
- Ухудшению UX — задержка обновления UI

**Решение:**

Использование `ListAdapter` с `AsyncListDiffer`, который оптимизирован для больших списков и автоматически выполняет расчет в фоне:

```kotlin
// ✅ ХОРОШО - ListAdapter с AsyncListDiffer для автоматической оптимизации
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        return UserViewHolder(parent)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// DiffCallback для сравнения элементов
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User) =
        oldItem == newItem
}

// Использование - автоматический расчет в фоне
adapter.updateItems(newUsers) // или adapter.submitList(newUsers)
// AsyncListDiffer автоматически:
// 1. Копирует списки перед расчетом
// 2. Выполняет calculateDiff() в фоне
// 3. Применяет обновления на главном потоке
// 4. Отменяет предыдущие операции при новых обновлениях
```

**4. Race conditions**

**Проблема:**

Множественные быстрые вызовы `updateUsers()` создают несколько параллельных задач расчета `DiffUtil`, что приводит к:
- Race conditions — несколько задач пытаются обновить `Adapter` одновременно
- Потере обновлений — более ранние обновления могут перезаписать более поздние
- Некорректному состоянию UI — `RecyclerView` показывает устаревшие данные
- Нагрузке на CPU — несколько тяжелых вычислений выполняются параллельно

**Решение:**

Отмена предыдущих операций при новых обновлениях:

```kotlin
// ✅ ХОРОШО - отмена предыдущих операций для предотвращения race conditions
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()
    private var updateJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun updateUsers(newUsers: List<User>) {
        // Отмена предыдущего расчета, если он еще выполняется
        updateJob?.cancel()

        // Создание копий списков на главном потоке
        val oldList = users.toList()
        val newList = newUsers.toList()

        // Запуск нового расчета
        updateJob = scope.launch {
            val diffResult = try {
                DiffUtil.calculateDiff(UserDiffCallback(oldList, newList))
            } catch (e: Exception) {
                // Обработка ошибок расчета
                return@launch
            }

            // Применение обновлений на главном потоке
            withContext(Dispatchers.Main) {
                // Проверка, что задача не была отменена
                if (isActive) {
                    users = newList
                    diffResult.dispatchUpdatesTo(this@UserAdapter)
                }
            }
        }
    }

    override fun onDetachedFromRecyclerView(recyclerView: RecyclerView) {
        super.onDetachedFromRecyclerView(recyclerView)
        updateJob?.cancel() // Отмена при отвязке от RecyclerView
        scope.cancel()
    }
}
```

**5. Отсутствие обработки ошибок**

**Проблема:**

Исключения в `calculateDiff()` (например, `NullPointerException`, `IndexOutOfBoundsException`, ошибки в callback) приводят к:
- Крашам приложения — необработанные исключения завершают приложение
- Потере обновлений — UI не обновляется при ошибке
- Некорректному состоянию — `RecyclerView` показывает устаревшие данные

**Решение:**

Обработка ошибок с fallback стратегиями:

```kotlin
// ✅ ХОРОШО - обработка ошибок с fallback стратегиями
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Копия на главном потоке

    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(
                UserDiffCallback(oldList, newUsers)
            )

            withContext(Dispatchers.Main) {
                users = newUsers
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        } catch (e: IndexOutOfBoundsException) {
            // Ошибка доступа к индексу - возможно, данные изменились
            withContext(Dispatchers.Main) {
                users = newUsers
                notifyDataSetChanged() // Fallback: полное обновление
            }
        } catch (e: Exception) {
            // Другие ошибки (например, в callback)
            Log.e(TAG, "DiffUtil calculation failed", e)
            withContext(Dispatchers.Main) {
                // Fallback: обновление без анимации
                users = newUsers
                notifyDataSetChanged()
            }
        }
    }
}
```

### Лучшие Практики И Рекомендации

**Архитектурные решения:**

-   **Использовать `ListAdapter`** вместо ручного `DiffUtil` — `AsyncListDiffer` внутри автоматически оптимизирует расчет и обрабатывает все описанные проблемы
-   **Захватывать неизменяемые копии данных** перед расчетом — предотвращает race conditions и `IndexOutOfBoundsException`
-   **Отменять предыдущие операции** при новых обновлениях — предотвращает race conditions и потерю обновлений
-   **Обрабатывать ошибки** с fallback стратегиями — `notifyDataSetChanged()` как резервный вариант
-   **Кэшировать тяжелые вычисления** вне callback — снижает время расчета при повторных вызовах

**Оптимизация производительности:**

-   **Использовать `equals()` эффективно** — переопределять `equals()` для правильного сравнения в `areContentsTheSame()`
-   **Избегать глубокого сравнения** — сравнивать только изменяемые поля, не всю структуру данных
-   **Минимизировать вызовы в callback** — каждый вызов должен быть максимально быстрым
-   **Использовать `Payload` для частичных обновлений** — передавать информацию о том, что именно изменилось для оптимизации `onBindViewHolder()`

**Пример оптимизированного DiffCallback:**

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        // Быстрое сравнение по ID
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        // Сравнение только изменяемых полей (не включая computed properties)
        return oldItem.name == newItem.name &&
               oldItem.email == newItem.email &&
               oldItem.avatarUrl == newItem.avatarUrl
    }

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        // Возврат информации о том, что именно изменилось для оптимизации
        val payload = mutableListOf<String>()
        if (oldItem.name != newItem.name) payload.add("name")
        if (oldItem.email != newItem.email) payload.add("email")
        if (oldItem.avatarUrl != newItem.avatarUrl) payload.add("avatar")
        return if (payload.isEmpty()) null else payload
    }
}

// В Adapter
override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
    holder.bind(getItem(position))
}

override fun onBindViewHolder(
    holder: UserViewHolder,
    position: Int,
    payloads: MutableList<Any>
) {
    if (payloads.isEmpty()) {
        super.onBindViewHolder(holder, position, payloads)
    } else {
        // Частичное обновление только измененных View
        val payload = payloads[0] as List<String>
        if (payload.contains("name")) holder.updateName(getItem(position).name)
        if (payload.contains("email")) holder.updateEmail(getItem(position).email)
        if (payload.contains("avatar")) holder.updateAvatar(getItem(position).avatarUrl)
    }
}
```

**Альтернативы для очень больших списков:**

-   **Paging Library**: для списков >10,000 элементов использовать `Paging 3` вместо `DiffUtil`
-   **Локальная фильтрация**: для динамической фильтрации использовать `Filter` API вместо пересчета всего списка
-   **Разбиение на страницы**: разбивать большие списки на страницы и обновлять только текущую страницу

## Answer (EN)

`DiffUtil` is a utility for calculating differences between two lists and applying updates to `RecyclerView`. When calculating in background (`calculateDiff()` on background thread), issues occur with data changes during calculation, heavy computations in callbacks, large lists (>1000 items), improper error handling, and race conditions between threads. Understanding these problems is critical for optimizing `RecyclerView` performance.

### Main Issues

**1. Data modification during calculation**

**Problem:**

Source list changes by another thread (usually main UI thread) during `calculateDiff()` execution on background thread. This leads to:
- `IndexOutOfBoundsException` — accessing index that no longer exists
- Incorrect diff operations — `DiffUtil` calculates diff based on stale data
- Race conditions — list state changes between `getOldListSize()` and `areItemsTheSame()` calls

**Solution:**

Creating immutable copy of list before starting background calculation:

```kotlin
// ❌ BAD - data can change during calculation
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // ⚠️ users can change!
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // ⚠️ IndexOutOfBoundsException
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}

// ✅ GOOD - immutable copy before calculation
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Create copy on main thread
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size // Safe access to copy
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newUsers[newPos].id
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}
```

**2. Heavy computations in callback**

**Problem:**

Complex operations in `areContentsTheSame()` are called multiple times during `DiffUtil` calculation (up to O(N²) times for algorithm). Even on background thread this can lead to:
- Long computations — `DiffUtil` blocks on heavy operations
- Repeated computations — same data processed multiple times
- Increased calculation time — total time increases proportionally to callback complexity

**Solution:**

Caching results of heavy computations outside callback:

```kotlin
// ❌ BAD - JSON parsing in callback (called O(N²) times)
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // ⚠️ JSON parsing every time on comparison (very slow!)
        val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldData == newData
    }

    // ... other methods
}

// ✅ GOOD - cache results before callback
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    // Cache parsed data once
    private val oldDataCache = oldList.map {
        Json.decodeFromString<MessageData>(it.jsonData)
    }
    private val newDataCache = newList.map {
        Json.decodeFromString<MessageData>(it.jsonData)
    }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // Fast comparison of cached data
        return oldDataCache[oldPos] == newDataCache[newPos]
    }

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size
    override fun areItemsTheSame(oldPos: Int, newPos: Int) =
        oldList[oldPos].id == newList[newPos].id
}
```

**3. Large lists**

**Problem:**

`DiffUtil` uses `Myers` algorithm for difference calculation with O(N²) time complexity in worst case. For large lists (>1000 items) this leads to:
- Long calculations — calculation can take seconds even on background thread
- Background thread blocking — other operations don't execute
- UX degradation — UI update delay

**Solution:**

Using `ListAdapter` with `AsyncListDiffer`, optimized for large lists and automatically calculates in background:

```kotlin
// ✅ GOOD - ListAdapter with AsyncListDiffer for automatic optimization
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        return UserViewHolder(parent)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// DiffCallback for item comparison
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User) =
        oldItem == newItem
}

// Usage - automatic background calculation
adapter.updateItems(newUsers) // or adapter.submitList(newUsers)
// AsyncListDiffer automatically:
// 1. Copies lists before calculation
// 2. Executes calculateDiff() in background
// 3. Applies updates on main thread
// 4. Cancels previous operations on new updates
```

**4. Race conditions**

**Problem:**

Multiple fast calls to `updateUsers()` create several parallel `DiffUtil` calculation tasks, leading to:
- Race conditions — multiple tasks try to update `Adapter` simultaneously
- Lost updates — earlier updates can overwrite later ones
- Incorrect UI state — `RecyclerView` shows stale data
- CPU load — multiple heavy computations execute in parallel

**Solution:**

Cancelling previous operations on new updates:

```kotlin
// ✅ GOOD - cancel previous operations to prevent race conditions
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()
    private var updateJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun updateUsers(newUsers: List<User>) {
        // Cancel previous calculation if still running
        updateJob?.cancel()

        // Create list copies on main thread
        val oldList = users.toList()
        val newList = newUsers.toList()

        // Start new calculation
        updateJob = scope.launch {
            val diffResult = try {
                DiffUtil.calculateDiff(UserDiffCallback(oldList, newList))
            } catch (e: Exception) {
                // Handle calculation errors
                return@launch
            }

            // Apply updates on main thread
            withContext(Dispatchers.Main) {
                // Check task wasn't cancelled
                if (isActive) {
                    users = newList
                    diffResult.dispatchUpdatesTo(this@UserAdapter)
                }
            }
        }
    }

    override fun onDetachedFromRecyclerView(recyclerView: RecyclerView) {
        super.onDetachedFromRecyclerView(recyclerView)
        updateJob?.cancel() // Cancel on RecyclerView detachment
        scope.cancel()
    }
}
```

**5. Missing error handling**

**Problem:**

Exceptions in `calculateDiff()` (e.g., `NullPointerException`, `IndexOutOfBoundsException`, callback errors) lead to:
- App crashes — unhandled exceptions crash the app
- Lost updates — UI doesn't update on error
- Incorrect state — `RecyclerView` shows stale data

**Solution:**

Error handling with fallback strategies:

```kotlin
// ✅ GOOD - error handling with fallback strategies
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Copy on main thread

    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(
                UserDiffCallback(oldList, newUsers)
            )

            withContext(Dispatchers.Main) {
                users = newUsers
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        } catch (e: IndexOutOfBoundsException) {
            // Index access error - possibly data changed
            withContext(Dispatchers.Main) {
                users = newUsers
                notifyDataSetChanged() // Fallback: full refresh
            }
        } catch (e: Exception) {
            // Other errors (e.g., in callback)
            Log.e(TAG, "DiffUtil calculation failed", e)
            withContext(Dispatchers.Main) {
                // Fallback: update without animation
                users = newUsers
                notifyDataSetChanged()
            }
        }
    }
}
```

### Best Practices and Recommendations

**Architectural decisions:**

-   **Use `ListAdapter`** instead of manual `DiffUtil` — `AsyncListDiffer` internally automatically optimizes calculation and handles all described issues
-   **Capture immutable copies** before calculation — prevents race conditions and `IndexOutOfBoundsException`
-   **Cancel previous operations** on new updates — prevents race conditions and lost updates
-   **Handle errors** with fallback strategies — `notifyDataSetChanged()` as fallback option
-   **Cache heavy computations** outside callback — reduces calculation time on repeated calls

**Performance optimization:**

-   **Use `equals()` efficiently** — override `equals()` for correct comparison in `areContentsTheSame()`
-   **Avoid deep comparison** — compare only mutable fields, not entire data structure
-   **Minimize calls in callback** — each call should be as fast as possible
-   **Use `Payload` for partial updates** — pass information about what exactly changed to optimize `onBindViewHolder()`

**Optimized DiffCallback example:**

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        // Fast comparison by ID
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        // Compare only mutable fields (excluding computed properties)
        return oldItem.name == newItem.name &&
               oldItem.email == newItem.email &&
               oldItem.avatarUrl == newItem.avatarUrl
    }

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        // Return information about what exactly changed for optimization
        val payload = mutableListOf<String>()
        if (oldItem.name != newItem.name) payload.add("name")
        if (oldItem.email != newItem.email) payload.add("email")
        if (oldItem.avatarUrl != newItem.avatarUrl) payload.add("avatar")
        return if (payload.isEmpty()) null else payload
    }
}

// In Adapter
override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
    holder.bind(getItem(position))
}

override fun onBindViewHolder(
    holder: UserViewHolder,
    position: Int,
    payloads: MutableList<Any>
) {
    if (payloads.isEmpty()) {
        super.onBindViewHolder(holder, position, payloads)
    } else {
        // Partial update of only changed Views
        val payload = payloads[0] as List<String>
        if (payload.contains("name")) holder.updateName(getItem(position).name)
        if (payload.contains("email")) holder.updateEmail(getItem(position).email)
        if (payload.contains("avatar")) holder.updateAvatar(getItem(position).avatarUrl)
    }
}
```

**Alternatives for very large lists:**

-   **Paging Library**: for lists >10,000 items use `Paging 3` instead of `DiffUtil`
-   **Local filtering**: for dynamic filtering use `Filter` API instead of recalculating entire list
-   **Pagination**: split large lists into pages and update only current page

---

## Follow-ups

**Базовая теория:**
- Почему `DiffUtil` имеет O(N²) сложность и когда это критично?
- Как работает алгоритм `Myers` внутри `DiffUtil`?
- В чем разница между `DiffUtil` и `AsyncListDiffer`?

**Практические вопросы:**
- Как оптимизировать `DiffUtil` для списков с >10,000 элементов?
- Когда использовать `ListAdapter` vs ручную реализацию `DiffUtil`?
- Как обрабатывать `DiffUtil` со сложными вложенными структурами данных?

**Производительность:**
- Как использовать `Payload` для частичных обновлений в `RecyclerView`?
- Какие альтернативы `DiffUtil` существуют для очень больших datasets?
- Как измерить производительность `DiffUtil` и найти узкие места?

**Архитектура:**
- Как правильно обрабатывать race conditions при множественных обновлениях?
- Как избежать утечек памяти при использовании `DiffUtil` с корутинами?
- Когда использовать `Paging 3` вместо `DiffUtil`?

## References

- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)
- [AsyncListDiffer Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/AsyncListDiffer)
- [Paging 3 Library](https://developer.android.com/topic/libraries/architecture/paging/v3-overview)
- [RecyclerView Optimization](https://developer.android.com/guide/topics/ui/layout/recyclerview#performance)

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]


### Prerequisites (Easier)
- RecyclerView basics and adapter patterns
- Coroutines and background threading

### Related (Same Level)
- Main causes of UI lag
- RecyclerView optimization techniques

### Advanced (Harder)
- Custom DiffUtil algorithm implementation
- Paging 3 library for large datasets
