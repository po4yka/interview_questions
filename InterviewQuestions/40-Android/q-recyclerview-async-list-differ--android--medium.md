---
id: android-224
title: "RecyclerView AsyncListDiffer / RecyclerView AsyncListDiffer"
aliases: [AsyncListDiffer, RecyclerView AsyncListDiffer]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-side-effects-advanced--jetpack-compose--hard, q-vector-graphics-animations--graphics--medium, q-what-are-services-used-for--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/medium]
date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# RecyclerView Async List Diffing

# Question (EN)
> How does AsyncListDiffer work? Explain background thread diffing, comparing AsyncListDiffer vs ListAdapter, handling list mutations safely, and optimizing for large dataset updates.

# Вопрос (RU)
> Как работает AsyncListDiffer? Объясните diffing в фоновом потоке, сравнение AsyncListDiffer vs ListAdapter, безопасную обработку мутаций списка и оптимизацию для обновлений больших наборов данных.

---

## Answer (EN)

**AsyncListDiffer** is a helper class that calculates list differences on a background thread and dispatches updates to RecyclerView. It prevents UI freezes when updating large lists.

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

**For list of 10,000 items:**
- DiffUtil calculation: ~200ms
- UI freezes for 200ms
- Janky, poor UX

---

### AsyncListDiffer Solution

**Calculates diff on background thread:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<AsyncAdapter.ViewHolder>() {

    //  AsyncListDiffer handles threading automatically
    private val differ = AsyncListDiffer(this, DiffCallback())

    // Access current list
    val currentList: List<Item>
        get() = differ.currentList

    // Submit new list (async calculation)
    fun submitList(newList: List<Item>) {
        differ.submitList(newList) // Async, non-blocking!
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

**Thread flow:**

```
Main Thread                 Background Thread
-----------                 -----------------
submitList(newList)
    ↓
Store newList
    ↓                    →  Calculate diff
Keep UI responsive           (DiffUtil.calculateDiff)
    ↓                    ←  Return DiffResult
Receive result
    ↓
dispatchUpdatesTo(adapter)
    ↓
Update UI (smooth!)
```

**Key points:**
- Diff calculation on background executor
- UI thread stays responsive
- Updates dispatched on main thread
- Thread-safe list access

---

### AsyncListDiffer Vs ListAdapter

| Feature | AsyncListDiffer | ListAdapter |
|---------|----------------|-------------|
| **Base class** | Any adapter | Must extend ListAdapter |
| **Flexibility** | More flexible | Simpler API |
| **Boilerplate** | Slightly more | Less |
| **Use case** | Custom adapters | Standard adapters |
| **Threading** | Manual setup | Automatic |

**ListAdapter (built on AsyncListDiffer):**

```kotlin
//  ListAdapter is simpler
class SimpleAdapter : ListAdapter<Item, SimpleAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ...
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position) // ListAdapter provides this
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
adapter.submitList(items) // Same API as AsyncListDiffer!
```

**When to use AsyncListDiffer:**
- Need custom adapter base class
- Multiple types of lists in same adapter
- Advanced customization

**When to use ListAdapter:**
- Standard use case (95% of time)
- Simpler, cleaner code
- Recommended by Google

---

### Thread Safety with submitList()

**submitList() is thread-safe:**

```kotlin
//  Safe to call from any thread
viewModel.items.observe(lifecycleOwner) { items ->
    adapter.submitList(items) // Can be called from background thread
}
```

**But list itself must not be mutated:**

```kotlin
//  BAD - Mutable list
val items = mutableListOf<Item>()
adapter.submitList(items)

// Later...
items.add(Item()) // DANGER! List is being diffed in background
adapter.submitList(items) // May crash or produce incorrect results

//  GOOD - Immutable list
val items = listOf<Item>(...)
adapter.submitList(items)

// Later...
val newItems = items + Item() // Create new list
adapter.submitList(newItems) // Safe!
```

---

### Handling List Mutations Safely

**Problem: Modifying list during diff:**

```kotlin
//  UNSAFE
class UnsafeViewModel : ViewModel() {
    private val _items = MutableLiveData<MutableList<Item>>()
    val items: LiveData<MutableList<Item>> = _items

    fun addItem(item: Item) {
        _items.value?.add(item) // Mutates list!
        _items.value = _items.value // Triggers observer
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
        _items.value = currentList + item // Creates new list
    }
}
```

**Solution 2: Make defensive copy**

```kotlin
//  SAFE - Defensive copy
adapter.submitList(items.toList()) // Creates copy
```

**Solution 3: Use StateFlow with immutable lists**

```kotlin
class FlowViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<Item>>(emptyList())
    val items: StateFlow<List<Item>> = _items.asStateFlow()

    fun addItem(item: Item) {
        _items.value = _items.value + item // Creates new list
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

### Commit Callback

**Get notified when diff is complete:**

```kotlin
adapter.submitList(newItems) { // Callback runs when diff complete
    // Scroll to top after update
    recyclerView.scrollToPosition(0)
}

// Or with more control
adapter.submitList(newItems, object : Runnable {
    override fun run() {
        // Update complete
        progressBar.isVisible = false
        emptyView.isVisible = newItems.isEmpty()
    }
})
```

---

### Custom Executor

**By default, uses Architecture Components executor. Can customize:**

```kotlin
// Custom executor (e.g., for testing)
val customExecutor = Executors.newSingleThreadExecutor()

val differ = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(customExecutor)
        .build()
)

// For testing with instant execution
val testExecutor = Executor { it.run() } // Runs synchronously

val differ = AsyncListDiffer(
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

**2. Use efficient equals():**

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String,
    val metadata: Map<String, Any> // Expensive to compare
) {
    // Optimize equals
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Item) return false

        // Check cheap fields first
        if (id != other.id) return false
        if (name != other.name) return false
        if (description != other.description) return false

        // Only check expensive field if everything else matches
        return metadata == other.metadata
    }
}
```

**3. Consider pagination for very large lists:**

```kotlin
// For lists > 10,000 items, use Paging 3 instead
// AsyncListDiffer still works but pagination is more efficient
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
            // Partial update for message status
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
                currentMessage?.let { onMessageClick(it) }
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
            // Format timestamp
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
                currentMessage?.let { onMessageClick(it) }
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

        // Observe messages
        viewModel.messages.observe(viewLifecycleOwner) { messages ->
            adapter.submitList(messages) {
                // Scroll to bottom after new message
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

```kotlin
@RunWith(AndroidJUnit4::class)
class AsyncAdapterTest {

    @Test
    fun testListUpdate() = runBlocking {
        val adapter = AsyncAdapter()

        val initialList = listOf(Item(1, "A"), Item(2, "B"))
        adapter.submitList(initialList)

        // Wait for diff to complete
        delay(100)

        assertEquals(2, adapter.itemCount)
        assertEquals("A", adapter.currentList[0].name)
    }

    @Test
    fun testListUpdateWithCallback() {
        val adapter = AsyncAdapter()
        val initialList = listOf(Item(1, "A"))

        var callbackCalled = false

        adapter.submitList(initialList) {
            callbackCalled = true
        }

        // Wait for callback
        eventually(timeoutMs = 1000) {
            assertTrue(callbackCalled)
        }
    }
}
```

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
list.add(item) // Dangerous!
```

**2. Prefer ListAdapter**
```kotlin
//  DO - Simpler
class MyAdapter : ListAdapter<Item, ViewHolder>(DiffCallback())

// Only use AsyncListDiffer for custom needs
```

**3. Use commit callback wisely**
```kotlin
//  DO - Scroll after update
adapter.submitList(items) {
    recyclerView.scrollToPosition(0)
}

//  DON'T - Heavy work in callback
adapter.submitList(items) {
    // Heavy operation - blocks UI!
}
```

**4. Debounce rapid updates**
```kotlin
//  DO - Debounce user input
searchView.onQueryTextChange { query ->
    viewModel.search(query) // Debounced in ViewModel
}
```

**5. Test with large lists**
```kotlin
// Test with 1000+ items to ensure no jank
```

---

### Summary

**AsyncListDiffer benefits:**
- Background thread diffing
- Non-blocking UI updates
- Automatic thread safety
- Smooth UX for large lists

**How it works:**
- Calculates diff on background executor
- Dispatches updates on main thread
- Thread-safe submitList()

**AsyncListDiffer vs ListAdapter:**
- ListAdapter is built on AsyncListDiffer
- ListAdapter is simpler (recommended)
- AsyncListDiffer for custom adapters

**Best practices:**
- Use immutable lists
- Prefer ListAdapter when possible
- Debounce rapid updates
- Use commit callback for post-update actions
- Test with large datasets

**When to use:**
- Lists with 100+ items
- Frequent updates
- Need smooth UX
- Background processing desired

---

## Ответ (RU)

**AsyncListDiffer** - это вспомогательный класс, который вычисляет разницу списков в фоновом потоке и отправляет обновления в RecyclerView. Он предотвращает зависание UI при обновлении больших списков.

### Проблема: Блокировка UI Потока

```kotlin
//  ПРОБЛЕМА - Блокирует UI поток
class SlowAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = emptyList<Item>()

    fun updateData(newItems: List<Item>) {
        val diffResult = DiffUtil.calculateDiff(
            ItemDiffCallback(items, newItems)
        ) // БЛОКИРУЕТ UI поток для больших списков!

        items = newItems
        diffResult.dispatchUpdatesTo(this)
    }
}
```

**Для списка из 10,000 элементов:**
- Вычисление DiffUtil: ~200мс
- UI зависает на 200мс
- Дёрганый, плохой UX

---

### Решение AsyncListDiffer

**Вычисляет diff в фоновом потоке:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<AsyncAdapter.ViewHolder>() {

    //  AsyncListDiffer обрабатывает потоки автоматически
    private val differ = AsyncListDiffer(this, DiffCallback())

    // Доступ к текущему списку
    val currentList: List<Item>
        get() = differ.currentList

    // Отправить новый список (асинхронное вычисление)
    fun submitList(newList: List<Item>) {
        differ.submitList(newList) // Асинхронно, не блокирует!
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

**Поток выполнения:**

```
Главный поток              Фоновый поток
-----------                -----------------
submitList(newList)
    ↓
Сохранить newList
    ↓                    →  Вычислить diff
UI остается отзывчивым      (DiffUtil.calculateDiff)
    ↓                    ←  Вернуть DiffResult
Получить результат
    ↓
dispatchUpdatesTo(adapter)
    ↓
Обновить UI (плавно!)
```

**Ключевые моменты:**
- Вычисление diff на фоновом executor
- UI поток остается отзывчивым
- Обновления отправляются на главном потоке
- Потокобезопасный доступ к списку

---

### AsyncListDiffer Vs ListAdapter

| Функция | AsyncListDiffer | ListAdapter |
|---------|----------------|-------------|
| **Базовый класс** | Любой адаптер | Должен расширять ListAdapter |
| **Гибкость** | Более гибкий | Проще API |
| **Шаблонный код** | Немного больше | Меньше |
| **Случай использования** | Пользовательские адаптеры | Стандартные адаптеры |
| **Потоки** | Ручная настройка | Автоматически |

**ListAdapter (построен на AsyncListDiffer):**

```kotlin
//  ListAdapter проще
class SimpleAdapter : ListAdapter<Item, SimpleAdapter.ViewHolder>(DiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        // ...
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = getItem(position) // ListAdapter предоставляет это
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
adapter.submitList(items) // Тот же API, что и AsyncListDiffer!
```

**Когда использовать AsyncListDiffer:**
- Нужен пользовательский базовый класс адаптера
- Несколько типов списков в одном адаптере
- Продвинутая кастомизация

**Когда использовать ListAdapter:**
- Стандартный случай использования (95% времени)
- Проще, чище код
- Рекомендуется Google

---

### Безопасность Потоков С submitList()

**submitList() потокобезопасен:**

```kotlin
//  Безопасно вызывать из любого потока
viewModel.items.observe(lifecycleOwner) { items ->
    adapter.submitList(items) // Можно вызывать из фонового потока
}
```

**Но сам список не должен мутировать:**

```kotlin
//  ПЛОХО - Изменяемый список
val items = mutableListOf<Item>()
adapter.submitList(items)

// Позже...
items.add(Item()) // ОПАСНО! Список вычисляется в фоне
adapter.submitList(items) // Может упасть или дать неправильные результаты

//  ХОРОШО - Неизменяемый список
val items = listOf<Item>(...)
adapter.submitList(items)

// Позже...
val newItems = items + Item() // Создать новый список
adapter.submitList(newItems) // Безопасно!
```

---

### Безопасная Обработка Мутаций Списка

**Проблема: Изменение списка во время diff:**

```kotlin
//  НЕБЕЗОПАСНО
class UnsafeViewModel : ViewModel() {
    private val _items = MutableLiveData<MutableList<Item>>()
    val items: LiveData<MutableList<Item>> = _items

    fun addItem(item: Item) {
        _items.value?.add(item) // Мутирует список!
        _items.value = _items.value // Запускает observer
    }
}
```

**Решение 1: Используйте неизменяемые списки**

```kotlin
//  БЕЗОПАСНО - Неизменяемый
class SafeViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    fun addItem(item: Item) {
        val currentList = _items.value ?: emptyList()
        _items.value = currentList + item // Создает новый список
    }
}
```

**Решение 2: Делайте защитную копию**

```kotlin
//  БЕЗОПАСНО - Защитная копия
adapter.submitList(items.toList()) // Создает копию
```

**Решение 3: Используйте StateFlow с неизменяемыми списками**

```kotlin
class FlowViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<Item>>(emptyList())
    val items: StateFlow<List<Item>> = _items.asStateFlow()

    fun addItem(item: Item) {
        _items.value = _items.value + item // Создает новый список
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

### Callback Завершения

**Получить уведомление, когда diff завершен:**

```kotlin
adapter.submitList(newItems) { // Callback выполняется когда diff завершен
    // Прокрутить наверх после обновления
    recyclerView.scrollToPosition(0)
}

// Или с большим контролем
adapter.submitList(newItems, object : Runnable {
    override fun run() {
        // Обновление завершено
        progressBar.isVisible = false
        emptyView.isVisible = newItems.isEmpty()
    }
})
```

---

### Пользовательский Executor

**По умолчанию использует Architecture Components executor. Можно настроить:**

```kotlin
// Пользовательский executor (например, для тестирования)
val customExecutor = Executors.newSingleThreadExecutor()

val differ = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(customExecutor)
        .build()
)

// Для тестирования с мгновенным выполнением
val testExecutor = Executor { it.run() } // Выполняется синхронно

val differ = AsyncListDiffer(
    adapter,
    AsyncDifferConfig.Builder(DiffCallback())
        .setBackgroundThreadExecutor(testExecutor)
        .build()
)
```

---

### Оптимизация Производительности

**1. Debounce быстрых обновлений:**

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

**2. Используйте эффективный equals():**

```kotlin
data class Item(
    val id: Long,
    val name: String,
    val description: String,
    val metadata: Map<String, Any> // Дорого сравнивать
) {
    // Оптимизировать equals
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is Item) return false

        // Сначала проверить дешевые поля
        if (id != other.id) return false
        if (name != other.name) return false
        if (description != other.description) return false

        // Проверить дорогое поле только если все остальное совпадает
        return metadata == other.metadata
    }
}
```

**3. Рассмотрите пагинацию для очень больших списков:**

```kotlin
// Для списков > 10,000 элементов используйте Paging 3 вместо этого
// AsyncListDiffer все еще работает, но пагинация более эффективна
```

---

### Лучшие Практики

**1. Используйте неизменяемые списки**
```kotlin
//  ДЕЛАЙТЕ
val newList = currentList + newItem
adapter.submitList(newList)

//  НЕ ДЕЛАЙТЕ
val list = mutableListOf<Item>()
adapter.submitList(list)
list.add(item) // Опасно!
```

**2. Предпочитайте ListAdapter**
```kotlin
//  ДЕЛАЙТЕ - Проще
class MyAdapter : ListAdapter<Item, ViewHolder>(DiffCallback())

// Используйте AsyncListDiffer только для специальных нужд
```

**3. Используйте commit callback разумно**
```kotlin
//  ДЕЛАЙТЕ - Прокрутка после обновления
adapter.submitList(items) {
    recyclerView.scrollToPosition(0)
}

//  НЕ ДЕЛАЙТЕ - Тяжелая работа в callback
adapter.submitList(items) {
    // Тяжелая операция - блокирует UI!
}
```

**4. Debounce частых обновлений**
```kotlin
//  ДЕЛАЙТЕ - Debounce пользовательского ввода
searchView.onQueryTextChange { query ->
    viewModel.search(query) // Debounced в ViewModel
}
```

**5. Тестируйте с большими списками**
```kotlin
// Тестируйте с 1000+ элементами, чтобы убедиться в отсутствии дёрганий
```

---

### Резюме

**Преимущества AsyncListDiffer:**
- Вычисление diff в фоновом потоке
- Неблокирующие обновления UI
- Автоматическая потокобезопасность
- Плавный UX для больших списков

**Как это работает:**
- Вычисляет diff на фоновом executor
- Отправляет обновления на главном потоке
- Потокобезопасный submitList()

**AsyncListDiffer vs ListAdapter:**
- ListAdapter построен на AsyncListDiffer
- ListAdapter проще (рекомендуется)
- AsyncListDiffer для пользовательских адаптеров

**Лучшие практики:**
- Используйте неизменяемые списки
- Предпочитайте ListAdapter когда возможно
- Debounce частых обновлений
- Используйте commit callback для действий после обновления
- Тестируйте с большими наборами данных

**Когда использовать:**
- Списки с 100+ элементами
- Частые обновления
- Нужен плавный UX
- Желательна фоновая обработка

---


## Follow-ups

- Follow-up questions to be populated

## References

- References to be populated
## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-diffutil-advanced--android--medium]] - View, Ui
