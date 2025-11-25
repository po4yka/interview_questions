---
id: android-224
title: RecyclerView AsyncListDiffer / RecyclerView AsyncListDiffer
aliases: [AsyncListDiffer, RecyclerView AsyncListDiffer]
topic: android
subtopics:
  - ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-recyclerview
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy
  - q-recyclerview-itemdecoration-advanced--android--medium
  - q-what-are-services-used-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/medium]

date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)
> Как работает AsyncListDiffer? Объясните diffing в фоновом потоке, сравнение AsyncListDiffer vs ListAdapter, безопасную обработку мутаций списка и оптимизацию для обновлений больших наборов данных.

# Question (EN)
> How does AsyncListDiffer work? Explain background thread diffing, comparing AsyncListDiffer vs ListAdapter, handling list mutations safely, and optimizing for large dataset updates.

---

## Ответ (RU)

**AsyncListDiffer** — это вспомогательный класс, который вычисляет разницу списков в фоновом потоке и применяет обновления к RecyclerView на главном потоке. Он помогает избежать фризов UI при обновлении больших списков при условии, что `submitList` и работа с адаптером выполняются на главном потоке.

### Проблема: Блокировка UI-потока

```kotlin
//  ПРОБЛЕМА - Блокирует UI-поток
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = emptyList<Item>()

    fun updateData(newItems: List<Item>) {
        val diffResult = DiffUtil.calculateDiff(
            ItemDiffCallback(items, newItems)
        ) // БЛОКИРУЕТ UI-поток для больших списков!

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }
}
```

**Для списка из 10 000+ элементов (пример):**
- Вычисление DiffUtil может занять десятки/сотни мс.
- Если делать это в главном потоке — UI может подвисать.
- В итоге дёрганый скролл и плохой UX.

---

### Решение: AsyncListDiffer

**Выносит вычисление diff в фон, оставляя адаптер на главном потоке:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<AsyncAdapter.ViewHolder>() {

    // AsyncListDiffer сам управляет фоновым diff'ом и обновлениями
    private val differ = AsyncListDiffer(this, DiffCallback())

    // Текущий список (только для чтения)
    val currentList: List<Item>
        get() = differ.currentList

    // Отправить новый список (diff считается асинхронно)
    fun submitList(newList: List<Item>) {
        differ.submitList(newList) // Не блокирует главный поток
    }

    override fun getItemCount() = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = currentList[position]
        holder.bind(item)
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val textView: TextView = view.findViewById(R.id.text)

        fun bind(item: Item) {
            textView.text = item.name
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

---

### Как AsyncListDiffer Работает Внутри

**Поток выполнения (схематично):**

```
Главный поток                     Фоновый поток
-----------                       -----------------
submitList(newList)
    ↓
Фиксация oldList и newList
    ↓                          →  Вычисление diff
UI остаётся отзывчивым              (DiffUtil.calculateDiff)
    ↓                          ←  Возврат DiffResult
Применение diff
    ↓
dispatchUpdatesTo(adapter)
    ↓
Плавное обновление UI
```

**Ключевые моменты:**
- `submitList` нужно вызывать с главного потока.
- Diff считается в фоне на executor'е (через `AsyncDifferConfig` / executor архитектурных компонентов).
- Операции обновления RecyclerView выполняются на главном потоке.
- `currentList` — это снимок данных; нельзя мутировать списки, переданные в `submitList`.

---

### AsyncListDiffer Vs ListAdapter

| Функция | AsyncListDiffer | ListAdapter |
|--------|-----------------|------------|
| **Базовый класс** | Можно использовать внутри любого `RecyclerView.Adapter` | Наследуется от `ListAdapter` |
| **Гибкость** | Максимальная (сложные адаптеры, композиция) | Проще API для типичных случаев |
| **Шаблонный код** | Чуть больше | Меньше |
| **Сценарии** | Нельзя/неудобно наследоваться от `ListAdapter`, сложный UI | Обычные списки (рекомендовано по умолчанию) |
| **Потоки** | Автоматический фон. diff; можно настроить executor через `AsyncDifferConfig` | Тот же механизм; построен на `AsyncListDiffer` |

**ListAdapter (поверх AsyncListDiffer):**

```kotlin
//  ListAdapter упрощает реализацию
class SimpleAdapter : ListAdapter<Item, SimpleAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ...
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position)
        holder.bind(item)
    }

    class DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }
}

// Использование
val adapter = SimpleAdapter()
adapter.submitList(items)
```

**Когда использовать AsyncListDiffer:**
- Нужен свой базовый адаптер или сложная архитектура.
- Несколько разных списков/секций в одном адаптере.

**Когда использовать ListAdapter:**
- Типичный односписочный RecyclerView.
- Хочется меньше кода и следовать рекомендациям Google.

---

### Потокобезопасность И submitList()

Основные правила:
- `submitList` и все вызовы адаптера должны выполняться на главном потоке.
- AsyncListDiffer/ListAdapter сами делают diff в фоне и применяют результат корректно, но не делают произвольные вызовы из фоновых потоков безопасными.

Пример (`LiveData` вызывает observer в главном потоке):

```kotlin
viewModel.items.observe(lifecycleOwner) { items ->
    adapter.submitList(items)
}
```

Если данные считаются в фоне — переключаемся на главный поток перед `submitList`:

```kotlin
lifecycleScope.launch(Dispatchers.Default) {
    val items = loadItems()
    withContext(Dispatchers.Main) {
        adapter.submitList(items)
    }
}
```

**Не мутируйте списки после передачи в адаптер:**

```kotlin
// ПЛОХО
val items = mutableListOf<Item>()
adapter.submitList(items)
items.add(Item()) // Опасно

// ХОРОШО
val items = listOf<Item>(/* ... */)
adapter.submitList(items)

val newItems = items + Item()
adapter.submitList(newItems)
```

---

### Безопасная Обработка Мутаций Списка

**Проблема: изменение списка во время diff или после submitList.**

```kotlin
//  НЕБЕЗОПАСНО
class UnsafeViewModel : ViewModel() {
    private val _items = MutableLiveData<MutableList<Item>>()
    val items: LiveData<MutableList<Item>> = _items

    fun addItem(item: Item) {
        _items.value?.add(item)
        _items.value = _items.value
    }
}
```

**Решение 1: неизменяемые списки**

```kotlin
//  БЕЗОПАСНО
class SafeViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    fun addItem(item: Item) {
        val currentList = _items.value ?: emptyList()
        _items.value = currentList + item
    }
}
```

**Решение 2: защитная копия**

```kotlin
adapter.submitList(items.toList())
```

**Решение 3: `StateFlow` + неизменяемые списки**

```kotlin
class FlowViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<Item>>(emptyList())
    val items: StateFlow<List<Item>> = _items.asStateFlow()

    fun addItem(item: Item) {
        _items.value = _items.value + item
    }
}

// Во Fragment/Activity
lifecycleScope.launch {
    viewModel.items.collect { items ->
        adapter.submitList(items)
    }
}
```

---

### `Callback` Завершения

**Уведомление, когда diff применён:**

```kotlin
adapter.submitList(newItems) { // Вызывается на главном потоке после применения diff
    recyclerView.scrollToPosition(0)
}

adapter.submitList(newItems, object : Runnable {
    override fun run() {
        progressBar.isVisible = false
        emptyView.isVisible = newItems.isEmpty()
    }
})
```

`Callback` стоит использовать только для лёгких UI-действий.

---

### Пользовательский Executor

По умолчанию AsyncListDiffer/ListAdapter используют executor архитектурных компонентов (через `AsyncDifferConfig`). Его можно переопределить:

```kotlin
val customExecutor = Executors.newSingleThreadExecutor()

val differ = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(customExecutor)
        .build()
)

// Для тестов можно использовать синхронный executor
val testExecutor = Executor { it.run() }

val testDiffer = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(testExecutor)
        .build()
)
```

---

### Оптимизация Производительности

**1. Debounce частых обновлений:**

```kotlin
class DebouncedAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val differ = AsyncListDiffer(this, DiffCallback())
    private val handler = Handler(Looper.getMainLooper())
    private var pendingUpdate: List<Item>? = null

    private val submitRunnable = Runnable {
        pendingUpdate?.let {
            differ.submitList(it)
            pendingUpdate = null
        }
    }

    fun submitListDebounced(items: List<Item>, delayMs: Long = 300) {
        pendingUpdate = items
        handler.removeCallbacks(submitRunnable)
        handler.postDelayed(submitRunnable, delayMs)
    }

    fun submitListImmediate(items: List<Item>) {
        handler.removeCallbacks(submitRunnable)
        pendingUpdate = null
        differ.submitList(items)
    }

    // ... остальная часть адаптера
}
```

**2. Эффективные проверки в DiffUtil.ItemCallback:**

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String,
    val metadata: Map<String, Any>
)

class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
    override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
        if (oldItem.name != newItem.name) return false
        if (oldItem.description != newItem.description) return false
        return oldItem.metadata == newItem.metadata
    }
}
```

**3. Пагинация для очень больших списков:**

```kotlin
// Для очень больших или потоковых данных используйте Paging 3.
// AsyncListDiffer останется полезным, но не загружайте тысячи элементов сразу.
```

---

### Лучшие Практики

**1. Неизменяемые списки**
```kotlin
//  ДЕЛАЙТЕ
val newList = currentList + newItem
adapter.submitList(newList)

//  НЕ ДЕЛАЙТЕ
val list = mutableListOf<Item>()
adapter.submitList(list)
list.add(item) // Опасно
```

**2. Предпочитайте ListAdapter**
```kotlin
//  ДЕЛАЙТЕ - проще
class MyAdapter : ListAdapter<Item, ViewHolder>(DiffCallback())

// AsyncListDiffer используйте, когда ListAdapter не подходит
```

**3. `Callback` после commit — только для лёгких действий**
```kotlin
//  ДЕЛАЙТЕ
adapter.submitList(items) {
    recyclerView.scrollToPosition(0)
}

//  НЕ ДЕЛАЙТЕ
adapter.submitList(items) {
    // Тяжёлая работа здесь заблокирует UI
}
```

**4. Debounce частых обновлений выше по потоку**
```kotlin
searchView.onQueryTextChange { query ->
    viewModel.search(query) // Debounce в ViewModel/слое данных
}
```

**5. Тестируйте на реалистичных размерах**
```kotlin
// Проверяйте поведение на 1000+ элементов
```

---

### Резюме

**Преимущества AsyncListDiffer:**
- Вычисление diff в фоновом потоке.
- Неблокирующие обновления при работе с главного потока.
- Использование снимков списка вместо мутаций.

**Как работает:**
- `submitList` на главном потоке фиксирует старый и новый списки.
- Diff считается в фоне.
- Обновления RecyclerView применяются на главном потоке.

**AsyncListDiffer vs ListAdapter:**
- `ListAdapter` построен на `AsyncListDiffer` и покрывает большинство кейсов.
- `AsyncListDiffer` нужен для более сложных / кастомных адаптеров.

**Лучшие практики:**
- Использовать неизменяемые списки.
- Не мутировать данные после `submitList`.
- По возможности использовать `ListAdapter`.
- Debounce частых обновлений.
- Использовать callback для лёгких UI-действий.

**Когда использовать:**
- Большие списки.
- Частые обновления.
- Требуется плавный UX и инкрементальные обновления.

---

## Answer (EN)

**AsyncListDiffer** is a helper class that calculates list differences on a background thread and dispatches updates to RecyclerView on the main thread. It helps avoid UI freezes when updating large lists, as long as `submitList` and adapter interactions happen on the main thread.

### The Problem: Blocking UI Thread

```kotlin
//  PROBLEM - Blocks UI thread
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = emptyList<Item>()

    fun updateData(newItems: List<Item>) {
        val diffResult = DiffUtil.calculateDiff(
            ItemDiffCallback(items, newItems)
        ) // BLOCKS UI thread for large lists!

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }
}
```

**For list of 10,000 items (illustrative example):**
- DiffUtil calculation can take tens or hundreds of milliseconds
- If done on the main thread, UI may freeze for that time
- Produces jank and poor UX

---

### AsyncListDiffer Solution

**Moves diff calculation off the main thread while keeping adapter usage on main:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<AsyncAdapter.ViewHolder>() {

    // AsyncListDiffer handles background diffing and update dispatching
    private val differ = AsyncListDiffer(this, DiffCallback())

    // Access current list (read-only view managed by AsyncListDiffer)
    val currentList: List<Item>
        get() = differ.currentList

    // Submit new list (diff calculated asynchronously)
    fun submitList(newList: List<Item>) {
        differ.submitList(newList) // Non-blocking on main thread
    }

    override fun getItemCount() = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = currentList[position]
        holder.bind(item)
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val textView: TextView = view.findViewById(R.id.text)

        fun bind(item: Item) {
            textView.text = item.name
        }
    }

    class DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}
```

---

### How AsyncListDiffer Works Internally

**Thread flow (conceptual):**

```
Main Thread                      Background Thread
-----------                      -----------------
submitList(newList)
    ↓
Capture oldList & newList
    ↓                         →  Calculate diff
Keep UI responsive                (DiffUtil.calculateDiff)
    ↓                         ←  Return DiffResult
Apply diff result
    ↓
dispatchUpdatesTo(adapter)
    ↓
Update UI (smooth!)
```

**Key points:**
- `submitList` should be called on the main thread.
- The diff is computed on a background executor (`AsyncDifferConfig` / Arch components executor) by default.
- RecyclerView update operations (`notifyItem*`) are dispatched on the main thread.
- `currentList` is exposed as an immutable snapshot; you must not mutate the lists you pass in.

---

### AsyncListDiffer Vs ListAdapter

| Feature | AsyncListDiffer | ListAdapter |
|--------|-----------------|------------|
| **Base class** | Can be used inside any `RecyclerView.Adapter` | Must extend `ListAdapter` |
| **Flexibility** | More flexible for custom adapters, multiple view types, composition | Simpler API for common cases |
| **Boilerplate** | Slightly more (you manage adapter methods) | Less (built-in `getItem`, etc.) |
| **Use case** | When you need custom adapter behavior or can't extend `ListAdapter` | Standard list scenarios (recommended by default) |
| **Threading** | Handles background diffing automatically; can customize executors via `AsyncDifferConfig` | Same behavior; built on `AsyncListDiffer` |

**ListAdapter (built on AsyncListDiffer):**

```kotlin
//  ListAdapter is simpler for typical usage
class SimpleAdapter : ListAdapter<Item, SimpleAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ...
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position)
        holder.bind(item)
    }

    class DiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }
}

// Usage
val adapter = SimpleAdapter()
adapter.submitList(items)
```

**When to use AsyncListDiffer:**
- Need a custom base adapter (e.g., existing hierarchy, `ConcatAdapter`, complex compositions).
- Need to share a differ between components or fine-tune exec config.

**When to use ListAdapter:**
- Typical single-list adapters (most cases).
- Want concise, recommended API with less boilerplate.

---

### Thread Safety with submitList()

Key rules:
- `submitList` and all adapter interactions must run on the main thread.
- AsyncListDiffer/ListAdapter are thread-safe in how they offload diffing and apply results, but they do NOT make arbitrary background-thread adapter calls safe.

Example (correct threading via `LiveData` on main thread):

```kotlin
// LiveData observers are called on the main thread by default when using setValue
viewModel.items.observe(lifecycleOwner) { items ->
    adapter.submitList(items)
}
```

If you ever compute data on a background thread, switch to main before calling `submitList`:

```kotlin
lifecycleScope.launch(Dispatchers.Default) {
    val items = loadItems()
    withContext(Dispatchers.Main) {
        adapter.submitList(items)
    }
}
```

**Do NOT mutate lists after submission:**

```kotlin
// BAD - Mutable list reused
val items = mutableListOf<Item>()
adapter.submitList(items)

// Later...
items.add(Item()) // Dangerous: differ may be using this list snapshot
adapter.submitList(items)

// GOOD - Immutable snapshot per update
val items = listOf<Item>(/* ... */)
adapter.submitList(items)

// Later...
val newItems = items + Item()
adapter.submitList(newItems)
```

---

### Handling `List` Mutations Safely

**Problem: Modifying list while diff is in progress or after submission.**

```kotlin
//  UNSAFE
class UnsafeViewModel : ViewModel() {
    private val _items = MutableLiveData<MutableList<Item>>()
    val items: LiveData<MutableList<Item>> = _items

    fun addItem(item: Item) {
        _items.value?.add(item) // Mutates shared list
        _items.value = _items.value // Triggers observer with mutated instance
    }
}
```

**Solution 1: Use immutable lists**

```kotlin
//  SAFE - Immutable
class SafeViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    fun addItem(item: Item) {
        val currentList = _items.value ?: emptyList()
        _items.value = currentList + item // New list instance
    }
}
```

**Solution 2: Make defensive copy before submitting**

```kotlin
//  SAFE - Defensive copy
adapter.submitList(items.toList()) // Uses a new list instance
```

**Solution 3: Use `StateFlow` with immutable lists**

```kotlin
class FlowViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<Item>>(emptyList())
    val items: StateFlow<List<Item>> = _items.asStateFlow()

    fun addItem(item: Item) {
        _items.value = _items.value + item
    }
}

// In Fragment/Activity
lifecycleScope.launch {
    viewModel.items.collect { items ->
        adapter.submitList(items)
    }
}
```

---

### Commit `Callback`

**Get notified when diff & list update are applied:**

```kotlin
adapter.submitList(newItems) { // Callback runs on main thread after updates are applied
    recyclerView.scrollToPosition(0)
}

// Or with explicit Runnable
adapter.submitList(newItems, object : Runnable {
    override fun run() {
        progressBar.isVisible = false
        emptyView.isVisible = newItems.isEmpty()
    }
})
```

Use commit callbacks only for lightweight, UI-related work.

---

### Custom Executor

By default, AsyncListDiffer/ListAdapter use Architecture Components' background executor via `AsyncDifferConfig`. You can override this if needed:

```kotlin
val customExecutor = Executors.newSingleThreadExecutor()

val differ = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(customExecutor)
        .build()
)

// For tests, you can force synchronous execution
val testExecutor = Executor { it.run() }

val testDiffer = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(testExecutor)
        .build()
)
```

---

### Performance Optimization

**1. Debounce rapid updates:**

```kotlin
class DebouncedAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val differ = AsyncListDiffer(this, DiffCallback())
    private val handler = Handler(Looper.getMainLooper())
    private var pendingUpdate: List<Item>? = null

    private val submitRunnable = Runnable {
        pendingUpdate?.let {
            differ.submitList(it)
            pendingUpdate = null
        }
    }

    fun submitListDebounced(items: List<Item>, delayMs: Long = 300) {
        pendingUpdate = items
        handler.removeCallbacks(submitRunnable)
        handler.postDelayed(submitRunnable, delayMs)
    }

    fun submitListImmediate(items: List<Item>) {
        handler.removeCallbacks(submitRunnable)
        pendingUpdate = null
        differ.submitList(items)
    }

    // ... rest of adapter
}
```

**2. Use efficient equality in DiffUtil.ItemCallback:**

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String,
    val metadata: Map<String, Any>
)

class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
    override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
        // Check cheap fields first
        if (oldItem.name != newItem.name) return false
        if (oldItem.description != newItem.description) return false
        // Only compare metadata if needed
        return oldItem.metadata == newItem.metadata
    }
}
```

**3. Consider pagination for very large lists:**

```kotlin
// For very large or streaming datasets, prefer Paging 3.
// AsyncListDiffer still works, but pagination avoids loading huge lists at once.
```

---

### Real-World Example: Chat Adapter

```kotlin
data class Message(
    val id: String,
    val senderId: String,
    val content: String,
    val timestamp: Long,
    val isSent: Boolean = false,
    val isRead: Boolean = false
)

class ChatAdapter(
    private val currentUserId: String,
    private val onMessageClick: (Message) -> Unit
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_SENT = 0
        private const val TYPE_RECEIVED = 1
    }

    private val differ = AsyncListDiffer(this, MessageDiffCallback())

    val currentList: List<Message>
        get() = differ.currentList

    fun submitList(messages: List<Message>) {
        differ.submitList(messages)
    }

    fun submitList(messages: List<Message>, commitCallback: Runnable?) {
        differ.submitList(messages, commitCallback)
    }

    override fun getItemViewType(position: Int): Int {
        val message = currentList[position]
        return if (message.senderId == currentUserId) TYPE_SENT else TYPE_RECEIVED
    }

    override fun getItemCount() = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_SENT -> SentMessageViewHolder.create(parent, onMessageClick)
            TYPE_RECEIVED -> ReceivedMessageViewHolder.create(parent, onMessageClick)
            else -> throw IllegalArgumentException("Unknown viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val message = currentList[position]
        when (holder) {
            is SentMessageViewHolder -> holder.bind(message)
            is ReceivedMessageViewHolder -> holder.bind(message)
        }
    }

    override fun onBindViewHolder(
        holder: RecyclerView.ViewHolder,
        position: Int,
        payloads: List<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val message = currentList[position]

            @Suppress("UNCHECKED_CAST")
            val changes = payloads[0] as Map<String, Any>

            if (holder is SentMessageViewHolder) {
                changes["isSent"]?.let {
                    holder.updateSentStatus(message.isSent)
                }
                changes["isRead"]?.let {
                    holder.updateReadStatus(message.isRead)
                }
            }
        }
    }

    class SentMessageViewHolder private constructor(
        private val binding: ItemMessageSentBinding,
        private val onMessageClick: (Message) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        private var currentMessage: Message? = null

        init {
            binding.root.setOnClickListener {
                currentMessage?.let(onMessageClick)
            }
        }

        fun bind(message: Message) {
            currentMessage = message

            binding.content.text = message.content
            binding.timestamp.text = formatTimestamp(message.timestamp)

            updateSentStatus(message.isSent)
            updateReadStatus(message.isRead)
        }

        fun updateSentStatus(isSent: Boolean) {
            binding.sentIcon.isVisible = isSent
            binding.sendingIcon.isVisible = !isSent
        }

        fun updateReadStatus(isRead: Boolean) {
            binding.readIcon.isVisible = isRead
        }

        private fun formatTimestamp(timestamp: Long): String {
            return DateFormat.format("HH:mm", timestamp).toString()
        }

        companion object {
            fun create(
                parent: ViewGroup,
                onMessageClick: (Message) -> Unit
            ): SentMessageViewHolder {
                val binding = ItemMessageSentBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return SentMessageViewHolder(binding, onMessageClick)
            }
        }
    }

    class ReceivedMessageViewHolder private constructor(
        private val binding: ItemMessageReceivedBinding,
        private val onMessageClick: (Message) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        private var currentMessage: Message? = null

        init {
            binding.root.setOnClickListener {
                currentMessage?.let(onMessageClick)
            }
        }

        fun bind(message: Message) {
            currentMessage = message

            binding.content.text = message.content
            binding.timestamp.text = formatTimestamp(message.timestamp)
        }

        private fun formatTimestamp(timestamp: Long): String {
            return DateFormat.format("HH:mm", timestamp).toString()
        }

        companion object {
            fun create(
                parent: ViewGroup,
                onMessageClick: (Message) -> Unit
            ): ReceivedMessageViewHolder {
                val binding = ItemMessageReceivedBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return ReceivedMessageViewHolder(binding, onMessageClick)
            }
        }
    }

    class MessageDiffCallback : DiffUtil.ItemCallback<Message>() {
        override fun areItemsTheSame(oldItem: Message, newItem: Message): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Message, newItem: Message): Boolean {
            return oldItem == newItem
        }

        override fun getChangePayload(oldItem: Message, newItem: Message): Any? {
            val changes = mutableMapOf<String, Any>()

            if (oldItem.isSent != newItem.isSent) {
                changes["isSent"] = newItem.isSent
            }

            if (oldItem.isRead != newItem.isRead) {
                changes["isRead"] = newItem.isRead
            }

            return if (changes.isNotEmpty()) changes else null
        }
    }
}

// Usage in Fragment
class ChatFragment : Fragment() {

    private val viewModel: ChatViewModel by viewModels()
    private lateinit var adapter: ChatAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        adapter = ChatAdapter(
            currentUserId = getCurrentUserId(),
            onMessageClick = { message ->
                // Handle message click
            }
        )

        binding.recyclerView.adapter = adapter

        // Observe messages (main thread)
        viewModel.messages.observe(viewLifecycleOwner) { messages ->
            adapter.submitList(messages) {
                // Scroll to bottom after new message batch
                if (adapter.currentList.isNotEmpty()) {
                    binding.recyclerView.scrollToPosition(adapter.currentList.size - 1)
                }
            }
        }
    }
}
```

---

### Testing AsyncListDiffer

Avoid relying on arbitrary delays; prefer deterministic hooks:

```kotlin
@RunWith(AndroidJUnit4::class)
class AsyncAdapterTest {

    @Test
    fun testListUpdateWithCallback() {
        val adapter = AsyncAdapter()
        val initialList = listOf(Item(1, "A"))

        var callbackCalled = false

        adapter.submitList(initialList) {
            callbackCalled = true
        }

        // Use an assertion helper that waits until condition or times out,
        // or configure AsyncListDiffer with a synchronous executor in tests.
        eventually(timeoutMs = 1000) {
            assertTrue(callbackCalled)
        }
    }
}
```

For unit-style tests, you can inject an `AsyncDifferConfig` with a synchronous executor to make updates immediate.

---

### Best Practices

**1. Use immutable lists**
```kotlin
//  DO
val newList = currentList + newItem
adapter.submitList(newList)

//  DON'T
val list = mutableListOf<Item>()
adapter.submitList(list)
list.add(item) // Dangerous
```

**2. Prefer ListAdapter where possible**
```kotlin
//  DO - Simpler
class MyAdapter : ListAdapter<Item, ViewHolder>(DiffCallback())

// Use AsyncListDiffer only when ListAdapter is not a good fit
```

**3. Use commit callback for light post-update actions**
```kotlin
//  DO - Scroll after update
adapter.submitList(items) {
    recyclerView.scrollToPosition(0)
}

//  DON'T - Heavy work in callback (still runs on main thread)
adapter.submitList(items) {
    // Heavy operation here would block UI
}
```

**4. Debounce rapid updates upstream**
```kotlin
// Example: debounce user input in ViewModel instead of hammering submitList
searchView.onQueryTextChange { query ->
    viewModel.search(query) // Debounced in ViewModel
}
```

**5. Test with realistic list sizes**
```kotlin
// Use large-enough lists (e.g., 1000+ items) to verify no jank or ANR
```

---

### Summary

**AsyncListDiffer benefits:**
- Background thread diffing via `DiffUtil`.
- Non-blocking UI updates when used from main thread.
- Safer, snapshot-based list handling.

**How it works:**
- `submitList` on main thread captures old/new lists.
- Diff is calculated on a background executor.
- RecyclerView updates are dispatched on main thread.

**AsyncListDiffer vs ListAdapter:**
- `ListAdapter` is built on top of `AsyncListDiffer`.
- `ListAdapter` is recommended for most simple/standard uses.
- `AsyncListDiffer` is for custom adapters and advanced scenarios.

**Best practices:**
- Always treat lists as immutable snapshots.
- Avoid mutating lists after submission.
- Prefer `ListAdapter` if you can extend it.
- Debounce frequent updates.
- Use commit callbacks only for lightweight UI logic.

**When to use:**
- Lists with many items or frequent updates.
- When you need smooth UX and incremental updates.
- When naive `notifyDataSetChanged()` would be too heavy.

---

## Follow-ups

- [[q-what-are-services-used-for--android--medium]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]


### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - `View`, Ui
- [[q-recyclerview-diffutil-advanced--android--medium]] - `View`, Ui
