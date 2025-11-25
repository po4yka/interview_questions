---
id: android-473
title: DiffUtil Background Calculation Issues / Проблемы фонового вычисления DiffUtil
aliases: [DiffUtil Background Calculation Issues, DiffUtil background issues, Проблемы DiffUtil в фоне, Проблемы фонового вычисления DiffUtil]
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
  - q-background-vs-foreground-service--android--medium
  - q-keep-service-running-background--android--medium
  - q-main-causes-ui-lag--android--medium
  - q-what-is-diffutil-for--android--medium
created: 2025-10-20
updated: 2025-11-02
tags: [android/performance-memory, android/ui-views, difficulty/medium, diffutil, performance, recyclerview]
sources:
  - https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
date created: Saturday, November 1st 2025, 1:28:34 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---

# Вопрос (RU)
> Когда фоновое вычисление DiffUtil работает плохо?

# Question (EN)
> When does DiffUtil background calculation work poorly?

---

## Ответ (RU)

`DiffUtil` — утилита для вычисления различий между двумя списками и применения обновлений к `RecyclerView`. При фоновом вычислении (`calculateDiff()` на фоновом потоке) проблемы возникают при изменении данных во время расчета, тяжелых вычислениях в callback, больших списках, неправильной обработке ошибок и race conditions между потоками. Понимание этих проблем критично для оптимизации производительности `RecyclerView`.

### Основные Проблемы

**1. Изменение данных во время расчета**

**Проблема:**

Исходный список изменяется другим потоком (обычно главным потоком UI) во время выполнения `calculateDiff()` на фоновом потоке. Это приводит к:
- `IndexOutOfBoundsException` — доступ к индексу, который больше не существует
- Некорректным diff-операциям — `DiffUtil` вычисляет diff на основе устаревших данных
- Race conditions — состояние списка меняется между вызовами `getOldListSize()` и `areItemsTheSame()`

**Решение:**

Создание неизменяемых снимков (копий) списков перед запуском фонового вычисления:

```kotlin
// ❌ ПЛОХО - данные могут измениться во время расчета
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // ⚠️ users может измениться!
            override fun getNewListSize() = newUsers.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // ⚠️ IndexOutOfBoundsException / устаревшие данные
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}

// ✅ ХОРОШО - неизменяемые копии данных перед расчетом
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Создание копии на главном потоке
    val newList = newUsers.toList()
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size // Безопасный доступ к копии
            override fun getNewListSize() = newList.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newList[newPos].id
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos] == newList[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}
```

(В реальном коде корутины для таких задач следует привязывать к жизненному циклу `ViewModel` или `Lifecycle`, а не создавать новый `CoroutineScope` внутри метода адаптера.)

**2. Тяжелые вычисления в callback**

**Проблема:**

Сложные операции в `areContentsTheSame()` вызываются многократно во время расчета `DiffUtil` (алгоритм на основе Myers: в среднем O(N * D), в худшем случае O(N²)). Даже на фоновом потоке это может привести к:
- Долгим вычислениям — `DiffUtil` блокируется на тяжелых операциях
- Повторным вычислениям — одни и те же данные обрабатываются несколько раз
- Увеличению времени расчета — общее время расчета растет пропорционально сложности callback

**Решение:**

Кэширование результатов тяжелых вычислений вне callback:

```kotlin
// ❌ ПЛОХО - парсинг JSON в callback (может вызываться очень много раз)
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // ⚠️ Парсинг JSON каждый раз при сравнении (очень медленно!)
        val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldData == newData
    }
}

// ✅ ХОРОШО - кэширование результатов перед callback
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }
    private val newDataCache = newList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldDataCache[oldPos] == newDataCache[newPos]
}
```

**3. Большие списки**

**Проблема:**

`DiffUtil` использует алгоритм Myers для вычисления различий. Его сложность в среднем O(N * D), но в худшем случае может достигать O(N²). Для больших списков это может привести к:
- Долгим вычислениям — расчет может занимать заметное время даже на фоновом потоке
- Блокировке фонового потока — другие операции не выполняются, если выполняются в том же пуле
- Ухудшению UX — задержка между изменением данных и обновлением UI

**Решение:**

Использование `ListAdapter` с `AsyncListDiffer`, который автоматически выполняет расчет diff в фоне, копирует списки и гарантирует применение только последнего актуального результата:

```kotlin
// ✅ ХОРОШО - ListAdapter с AsyncListDiffer для автоматической обработки diff
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        return UserViewHolder(parent)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User) =
        oldItem == newItem
}

// Использование - автоматический расчет в фоне
adapter.submitList(newUsers)
// AsyncListDiffer внутри:
// 1. Захватывает копии списков перед расчетом
// 2. Выполняет calculateDiff() в фоне
// 3. Применяет обновления на главном потоке
// 4. Гарантирует, что к Adapter будет применен результат только для последнего submitList()
```

**4. Race conditions**

**Проблема:**

Множественные быстрые вызовы `updateUsers()` создают несколько параллельных задач расчета `DiffUtil`, что приводит к:
- Race conditions — несколько задач пытаются обновить `Adapter` одновременно
- Потере обновлений — более ранние результаты могут перезаписать более новые
- Некорректному состоянию UI — `RecyclerView` показывает устаревшие данные
- Лишней нагрузке на CPU — несколько тяжелых вычислений в параллели

**Решение:**

Отмена предыдущих операций при новых обновлениях и работа только с последним diff-результатом:

```kotlin
// ✅ ХОРОШО - отмена предыдущих операций для предотвращения race conditions
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()
    private var updateJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun updateUsers(newUsers: List<User>) {
        // Отмена предыдущего расчета, если он еще выполняется
        updateJob?.cancel()

        val oldList = users.toList()
        val newList = newUsers.toList()

        updateJob = scope.launch {
            val diffResult = try {
                DiffUtil.calculateDiff(UserDiffCallback(oldList, newList))
            } catch (e: Exception) {
                // Ошибка расчета - выходим, можно залогировать
                return@launch
            }

            withContext(Dispatchers.Main) {
                if (isActive) { // проверка, что задача не отменена
                    users = newList
                    diffResult.dispatchUpdatesTo(this@UserAdapter)
                }
            }
        }
    }

    override fun onDetachedFromRecyclerView(recyclerView: RecyclerView) {
        super.onDetachedFromRecyclerView(recyclerView)
        updateJob?.cancel()
        scope.cancel()
    }
}
```

(В продакшене предпочтительнее использовать `AsyncListDiffer`/`ListAdapter`, который аналогичным образом гарантирует применение только актуальных результатов.)

**5. Отсутствие обработки ошибок**

**Проблема:**

Исключения в `calculateDiff()` (например, `NullPointerException`, `IndexOutOfBoundsException`, ошибки в callback) приводят к:
- Крашам приложения — необработанные исключения завершают приложение
- Потере обновлений — UI не обновляется при ошибке
- Некорректному состоянию — `RecyclerView` показывает устаревшие данные

**Решение:**

Обработка ошибок с fallback-стратегиями:

```kotlin
// ✅ ХОРОШО - обработка ошибок с fallback стратегиями
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList()
    val safeNewList = newUsers.toList()

    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(
                UserDiffCallback(oldList, safeNewList)
            )

            withContext(Dispatchers.Main) {
                users = safeNewList
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        } catch (e: IndexOutOfBoundsException) {
            withContext(Dispatchers.Main) {
                users = safeNewList
                notifyDataSetChanged() // Fallback: полное обновление
            }
        } catch (e: Exception) {
            Log.e(TAG, "DiffUtil calculation failed", e)
            withContext(Dispatchers.Main) {
                users = safeNewList
                notifyDataSetChanged() // Fallback без анимаций
            }
        }
    }
}
```

### Лучшие Практики И Рекомендации

**Архитектурные решения:**

-   Использовать `ListAdapter` вместо ручного `DiffUtil`, когда это возможно — `AsyncListDiffer` внутри автоматически выполняет расчет в фоне, захватывает копии и обрабатывает большинство описанных проблем.
-   Захватывать неизменяемые копии данных перед расчетом — предотвращает race conditions и `IndexOutOfBoundsException`.
-   Отменять предыдущие операции при новых обновлениях — предотвращает race conditions и потерю обновлений.
-   Обрабатывать ошибки с fallback-стратегиями — `notifyDataSetChanged()` как резервный вариант для восстановления консистентного состояния.
-   Кэшировать тяжелые вычисления вне callback — снижает время расчета при повторных вызовах.

**Оптимизация производительности:**

-   Эффективно использовать `equals()` и/или сравнение по полям — корректная логика в `areContentsTheSame()`.
-   Избегать глубокого сравнения всего объекта, если меняются только отдельные поля.
-   Минимизировать работу в callback — каждый вызов должен быть максимально быстрым.
-   Использовать `payload` для частичных обновлений — передавать информацию о конкретных изменениях для оптимизации `onBindViewHolder()`.

**Пример оптимизированного DiffCallback:**

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.name == newItem.name &&
               oldItem.email == newItem.email &&
               oldItem.avatarUrl == newItem.avatarUrl
    }

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        val payload = mutableListOf<String>()
        if (oldItem.name != newItem.name) payload.add("name")
        if (oldItem.email != newItem.email) payload.add("email")
        if (oldItem.avatarUrl != newItem.avatarUrl) payload.add("avatar")
        return if (payload.isEmpty()) null else payload
    }
}

// В Adapter (с ListAdapter)
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
        val fields = payloads[0] as List<String>
        val item = getItem(position)
        if ("name" in fields) holder.updateName(item.name)
        if ("email" in fields) holder.updateEmail(item.email)
        if ("avatar" in fields) holder.updateAvatar(item.avatarUrl)
    }
}
```

**Альтернативы для очень больших списков:**

-   `Paging 3`: для действительно больших наборов данных использовать пагинацию вместо загрузки и diff всего списка в памяти.
-   Локальная фильтрация: при фильтрации уже загруженного списка можно обновлять только отфильтрованный подмножество и избегать повторного diff для всей исходной коллекции.
-   Разбиение на страницы: разбивать очень большие списки на страницы и обновлять только текущую страницу/окно просмотра.

## Answer (EN)

`DiffUtil` is a utility for calculating differences between two lists and applying updates to `RecyclerView`. When calculating in background (`calculateDiff()` on a background thread), issues arise with data changes during calculation, heavy computations in callbacks, large lists, missing error handling, and race conditions between threads. Understanding these problems is critical for optimizing `RecyclerView` performance.

### Main Issues

**1. Data modification during calculation**

**Problem:**

The source list is modified by another thread (usually the main UI thread) while `calculateDiff()` is running on a background thread. This leads to:
- `IndexOutOfBoundsException` — accessing an index that no longer exists
- Incorrect diff operations — `DiffUtil` computes the diff against stale data
- Race conditions — list state changes between `getOldListSize()` and `areItemsTheSame()`

**Solution:**

Create immutable snapshots of lists before starting background calculation:

```kotlin
// ❌ BAD - data can change during calculation
fun updateUsers(newUsers: List<User>) {
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = users.size // ⚠️ users can change!
            override fun getNewListSize() = newUsers.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos].id == newUsers[newPos].id // ⚠️ IndexOutOfBoundsException / stale data
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                users[oldPos] == newUsers[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}

// ✅ GOOD - immutable copies before calculation
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList() // Capture copy on main thread
    val newList = newUsers.toList()
    CoroutineScope(Dispatchers.Default).launch {
        val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
            override fun getOldListSize() = oldList.size
            override fun getNewListSize() = newList.size
            override fun areItemsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos].id == newList[newPos].id
            override fun areContentsTheSame(oldPos: Int, newPos: Int) =
                oldList[oldPos] == newList[newPos]
        })
        withContext(Dispatchers.Main) {
            diffResult.dispatchUpdatesTo(adapter)
        }
    }
}
```

(In real code, such coroutines should be scoped to a `ViewModel`/`Lifecycle` rather than creating a new `CoroutineScope` inside the adapter method.)

**2. Heavy computations in callback**

**Problem:**

Complex operations in `areContentsTheSame()` are invoked many times during `DiffUtil` calculation (Myers-based algorithm: average O(N * D), worst-case O(N²)). Even on a background thread this can cause:
- Long computations — `DiffUtil` is blocked by heavy operations
- Repeated work — same data processed multiple times
- Increased total time — runtime grows with callback complexity

**Solution:**

Cache heavy computations outside callbacks:

```kotlin
// ❌ BAD - JSON parsing in callback (can be invoked many times)
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // ⚠️ JSON parsing on every comparison (very slow!)
        val oldData = Json.decodeFromString<MessageData>(oldList[oldPos].jsonData)
        val newData = Json.decodeFromString<MessageData>(newList[newPos].jsonData)
        return oldData == newData
    }
}

// ✅ GOOD - cache results before callback
class MessageDiffCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    private val oldDataCache = oldList.map { Json.decodeFromString<MessageData>(it.jsonData) }
    private val newDataCache = newList.map { Json.decodeFromString<MessageData>(it.jsonData) }

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldDataCache[oldPos] == newDataCache[newPos]
}
```

**3. Large lists**

**Problem:**

`DiffUtil` uses the Myers algorithm. It runs in O(N * D) on average but can degrade to O(N²) in the worst case. For large lists this can lead to:
- Long calculations — can take noticeable time even on a background thread
- Background thread saturation — if sharing the same pool, it can delay other work
- UX degradation — lag between data change and UI update

**Solution:**

Use `ListAdapter` with `AsyncListDiffer`, which runs diff in background, snapshots lists, and ensures only the latest submitted result is applied:

```kotlin
// ✅ GOOD - ListAdapter with AsyncListDiffer
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        return UserViewHolder(parent)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User) =
        oldItem == newItem
}

// Usage - background diff handled internally
adapter.submitList(newUsers)
// AsyncListDiffer internally:
// 1. Captures list snapshots before diff
// 2. Executes calculateDiff() in background
// 3. Dispatches updates on main thread
// 4. Ensures only the latest submitList() result is applied
```

**4. Race conditions**

**Problem:**

Multiple rapid calls to `updateUsers()` create several parallel `DiffUtil` computations, leading to:
- Race conditions — multiple tasks try to update the adapter concurrently
- Lost updates — earlier results can overwrite newer data
- Incorrect UI state — `RecyclerView` shows stale data
- Extra CPU load — multiple heavy computations in parallel

**Solution:**

Cancel previous operations on new updates and only apply the latest diff result:

```kotlin
// ✅ GOOD - cancel previous operations to prevent race conditions
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()
    private var updateJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    fun updateUsers(newUsers: List<User>) {
        updateJob?.cancel()

        val oldList = users.toList()
        val newList = newUsers.toList()

        updateJob = scope.launch {
            val diffResult = try {
                DiffUtil.calculateDiff(UserDiffCallback(oldList, newList))
            } catch (e: Exception) {
                return@launch
            }

            withContext(Dispatchers.Main) {
                if (isActive) {
                    users = newList
                    diffResult.dispatchUpdatesTo(this@UserAdapter)
                }
            }
        }
    }

    override fun onDetachedFromRecyclerView(recyclerView: RecyclerView) {
        super.onDetachedFromRecyclerView(recyclerView)
        updateJob?.cancel()
        scope.cancel()
    }
}
```

(Again, `AsyncListDiffer` / `ListAdapter` is usually preferred as it encapsulates this behavior.)

**5. Missing error handling**

**Problem:**

Exceptions in `calculateDiff()` (e.g., `NullPointerException`, `IndexOutOfBoundsException`, errors in callbacks) cause:
- App crashes — unhandled exceptions crash the app
- Lost updates — UI not updated on error
- Inconsistent state — `RecyclerView` shows stale data

**Solution:**

Handle errors with fallback strategies:

```kotlin
// ✅ GOOD - error handling with fallbacks
fun updateUsers(newUsers: List<User>) {
    val oldList = users.toList()
    val safeNewList = newUsers.toList()

    CoroutineScope(Dispatchers.Default).launch {
        try {
            val diffResult = DiffUtil.calculateDiff(
                UserDiffCallback(oldList, safeNewList)
            )

            withContext(Dispatchers.Main) {
                users = safeNewList
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        } catch (e: IndexOutOfBoundsException) {
            withContext(Dispatchers.Main) {
                users = safeNewList
                notifyDataSetChanged() // Fallback: full refresh
            }
        } catch (e: Exception) {
            Log.e(TAG, "DiffUtil calculation failed", e)
            withContext(Dispatchers.Main) {
                users = safeNewList
                notifyDataSetChanged() // Fallback without animations
            }
        }
    }
}
```

### Best Practices and Recommendations

**Architectural decisions:**

-   Use `ListAdapter` instead of manual `DiffUtil` when possible — `AsyncListDiffer` inside automatically runs background diff, snapshots lists, and handles most described pitfalls.
-   Capture immutable copies before calculation — prevents race conditions and `IndexOutOfBoundsException`.
-   Cancel previous operations on new updates — prevents race conditions and lost updates.
-   Handle errors with fallback strategies — `notifyDataSetChanged()` as a safe fallback to restore consistency.
-   Cache heavy computations outside callbacks — reduces total diff calculation time.

**Performance optimization:**

-   Use `equals()`/field comparisons efficiently — implement correct logic for `areContentsTheSame()`.
-   Avoid deep comparison of entire objects when only a few fields can change.
-   Minimize work in callbacks — each invocation must be fast.
-   Use `payload` for partial updates — pass information about what exactly changed to optimize `onBindViewHolder()`.

**Optimized DiffCallback example:**

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
        return oldItem.name == newItem.name &&
               oldItem.email == newItem.email &&
               oldItem.avatarUrl == newItem.avatarUrl
    }

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        val payload = mutableListOf<String>()
        if (oldItem.name != newItem.name) payload.add("name")
        if (oldItem.email != newItem.email) payload.add("email")
        if (oldItem.avatarUrl != newItem.avatarUrl) payload.add("avatar")
        return if (payload.isEmpty()) null else payload
    }
}

// In Adapter (with ListAdapter)
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
        val fields = payloads[0] as List<String>
        val item = getItem(position)
        if ("name" in fields) holder.updateName(item.name)
        if ("email" in fields) holder.updateEmail(item.email)
        if ("avatar" in fields) holder.updateAvatar(item.avatarUrl)
    }
}
```

**Alternatives for very large lists:**

-   `Paging 3`: for truly large datasets use paging instead of holding and diffing the full list in memory.
-   Local filtering: when filtering an already loaded list, update only the filtered subset and avoid recomputing diff against the entire original dataset each time.
-   Pagination: split very large collections into pages/windows and update only the currently visible page.

---

## Follow-ups

**Базовая теория / Core theory:**
- Почему `DiffUtil` может иметь O(N²) сложность в худшем случае и когда это становится критичным?
- Как в общих чертах работает алгоритм Myers внутри `DiffUtil`?
- В чем разница между `DiffUtil`, `AsyncListDiffer` и `ListAdapter`?

**Практические вопросы / Practical:**
- Как оптимизировать работу `DiffUtil` для списков с десятками тысяч элементов?
- Когда использовать `ListAdapter` vs ручную реализацию `DiffUtil`?
- Как обрабатывать `DiffUtil` при сложных вложенных структурах данных?

**Производительность / Performance:**
- Как использовать `payload` для частичных обновлений в `RecyclerView`?
- Какие альтернативы / подходы использовать для очень больших наборов данных помимо голого `DiffUtil`?
- Как измерить производительность `DiffUtil` и найти узкие места?

**Архитектура / Architecture:**
- Как правильно обрабатывать race conditions при множественных обновлениях?
- Как избежать утечек памяти при использовании `DiffUtil` с корутинами?
- Когда использовать `Paging 3` вместо простого `DiffUtil`?

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
