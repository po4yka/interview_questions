---
topic: android
tags:
  - android
  - recyclerview
  - diffutil
  - performance
  - multithreading
difficulty: medium
status: draft
---

# Проблемы расчета DiffUtil в фоновом потоке

**English**: When does DiffUtil background calculation work poorly?

## Answer (EN)
Расчет DiffUtil в фоновом потоке может работать плохо при следующих условиях, которые приводят к некорректным результатам, проблемам производительности или race conditions.

### 1. Модификация данных во время расчета

**Проблема**: DiffUtil может дать некорректные результаты из-за изменений в списке во время вычисления diff.

```kotlin
// НЕПРАВИЛЬНО - данные могут измениться во время расчета
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: MutableList<User> = mutableListOf()

    fun updateUsers(newUsers: List<User>) {
        // Запуск DiffUtil в фоне
        CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
                override fun getOldListSize() = users.size
                override fun getNewListSize() = newUsers.size

                override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
                    // ОПАСНО! users может быть изменен другим потоком
                    return users[oldPos].id == newUsers[newPos].id
                }

                override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
                    return users[oldPos] == newUsers[newPos]
                }
            })

            withContext(Dispatchers.Main) {
                users.clear()
                users.addAll(newUsers)
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        }
    }
}

//  ПРАВИЛЬНО - использовать неизменяемую копию
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()

    fun updateUsers(newUsers: List<User>) {
        val oldList = users // Захватить текущее состояние

        CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
                override fun getOldListSize() = oldList.size
                override fun getNewListSize() = newUsers.size

                override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
                    return oldList[oldPos].id == newUsers[newPos].id
                }

                override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
                    return oldList[oldPos] == newUsers[newPos]
                }
            })

            withContext(Dispatchers.Main) {
                users = newUsers
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        }
    }
}
```

### 2. Сложные и долгие вычисления в Callback

**Проблема**: Тяжелые операции в `areContentsTheSame()` замедляют расчет даже в фоне.

```kotlin
// НЕПРАВИЛЬНО - тяжелые вычисления в callback
class MessageCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        val old = oldList[oldPos]
        val new = newList[newPos]

        // МЕДЛЕННО! Парсинг JSON для каждого сравнения
        val oldData = Json.decodeFromString<MessageData>(old.jsonData)
        val newData = Json.decodeFromString<MessageData>(new.jsonData)

        return oldData == newData
    }
}

//  ПРАВИЛЬНО - предварительная обработка данных
data class Message(
    val id: Int,
    val text: String,
    val timestamp: Long,
    // Кэшированные данные для быстрого сравнения
    val contentHash: Int
) {
    companion object {
        fun fromJson(json: String): Message {
            val data = Json.decodeFromString<MessageData>(json)
            return Message(
                id = data.id,
                text = data.text,
                timestamp = data.timestamp,
                // Вычислить hash один раз
                contentHash = data.hashCode()
            )
        }
    }
}

class MessageCallback(
    private val oldList: List<Message>,
    private val newList: List<Message>
) : DiffUtil.Callback() {

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        // Быстрое сравнение по hash
        return oldList[oldPos].contentHash == newList[newPos].contentHash
    }
}
```

### 3. Работа с очень большими наборами данных

**Проблема**: DiffUtil имеет сложность O(N*M), что становится медленным для больших списков.

```kotlin
// НЕПРАВИЛЬНО - DiffUtil для 10,000+ элементов
fun updateLargeList(newItems: List<Item>) {
    // Будет очень медленно!
    val diffResult = DiffUtil.calculateDiff(
        ItemCallback(oldItems, newItems)
    )
    diffResult.dispatchUpdatesTo(adapter)
}

//  ПРАВИЛЬНО - использовать Paging или частичные обновления
class ItemAdapter : PagedListAdapter<Item, ItemViewHolder>(
    DIFF_CALLBACK
) {
    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<Item>() {
            override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
                return oldItem.id == newItem.id
            }

            override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
                return oldItem == newItem
            }
        }
    }
}

// Или использовать AsyncListDiffer с лимитом
class ItemAdapter : RecyclerView.Adapter<ItemViewHolder>() {
    private val differ = AsyncListDiffer(this, object : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    })

    fun submitList(list: List<Item>) {
        // Ограничить размер для производительности
        val limitedList = if (list.size > MAX_ITEMS) {
            list.take(MAX_ITEMS)
        } else {
            list
        }
        differ.submitList(limitedList)
    }

    companion object {
        private const val MAX_ITEMS = 1000
    }
}
```

### 4. Race Conditions при множественных обновлениях

**Проблема**: Множественные вызовы `calculateDiff()` могут перекрываться и давать неверный результат.

```kotlin
// НЕПРАВИЛЬНО - несколько одновременных обновлений
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    fun updateUsers(newUsers: List<User>) {
        // Если вызвать дважды подряд, будет race condition!
        CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(...)
            withContext(Dispatchers.Main) {
                users = newUsers
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        }
    }
}

//  ПРАВИЛЬНО - использовать Job для отмены предыдущих расчетов
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var diffJob: Job? = null
    private var users: List<User> = emptyList()

    fun updateUsers(newUsers: List<User>) {
        // Отменить предыдущий расчет
        diffJob?.cancel()

        val oldList = users

        diffJob = CoroutineScope(Dispatchers.Default).launch {
            val diffResult = DiffUtil.calculateDiff(object : DiffUtil.Callback() {
                override fun getOldListSize() = oldList.size
                override fun getNewListSize() = newUsers.size

                override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
                    // Проверить, не отменена ли корутина
                    ensureActive()
                    return oldList[oldPos].id == newUsers[newPos].id
                }

                override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
                    ensureActive()
                    return oldList[oldPos] == newUsers[newPos]
                }
            })

            withContext(Dispatchers.Main) {
                users = newUsers
                diffResult.dispatchUpdatesTo(this@UserAdapter)
            }
        }
    }
}

//  ЕЩЕ ЛУЧШЕ - использовать ListAdapter
class UserAdapter : ListAdapter<User, UserViewHolder>(
    object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: User, newItem: User) =
            oldItem == newItem
    }
) {
    // submitList автоматически управляет race conditions!
    // adapter.submitList(newUsers)
}
```

### 5. Изменение данных во время обновления UI

**Проблема**: Данные меняются между `calculateDiff()` и `dispatchUpdatesTo()`.

```kotlin
// НЕПРАВИЛЬНО - данные могут измениться
class ChatAdapter : RecyclerView.Adapter<MessageViewHolder>() {
    private var messages: MutableList<Message> = mutableListOf()

    fun addMessage(message: Message) {
        // Добавление во время расчета diff может вызвать crash!
        messages.add(message)
        notifyItemInserted(messages.size - 1)
    }

    fun updateMessages(newMessages: List<Message>) {
        val oldList = messages.toList()

        CoroutineScope(Dispatchers.Default).launch {
            val diff = DiffUtil.calculateDiff(...)

            withContext(Dispatchers.Main) {
                // Между расчетом и применением messages мог измениться!
                messages.clear()
                messages.addAll(newMessages)
                diff.dispatchUpdatesTo(this@ChatAdapter)
            }
        }
    }
}

//  ПРАВИЛЬНО - использовать неизменяемые списки
class ChatAdapter : RecyclerView.Adapter<MessageViewHolder>() {
    private var messages: List<Message> = emptyList()
    private val updateLock = Mutex()

    suspend fun updateMessages(newMessages: List<Message>) {
        updateLock.withLock {
            val oldList = messages

            val diff = withContext(Dispatchers.Default) {
                DiffUtil.calculateDiff(MessageCallback(oldList, newMessages))
            }

            withContext(Dispatchers.Main) {
                messages = newMessages
                diff.dispatchUpdatesTo(this@ChatAdapter)
            }
        }
    }
}
```

### 6. Неправильная реализация equals/hashCode

**Проблема**: Некорректное сравнение объектов приводит к лишним обновлениям.

```kotlin
// НЕПРАВИЛЬНО - нет equals/hashCode
class User(
    val id: Int,
    var name: String,
    var avatarUrl: String?,
    val lastUpdate: Long = System.currentTimeMillis() // Всегда разное!
)

// DiffUtil всегда считает объекты разными
// areContentsTheSame() всегда возвращает false

//  ПРАВИЛЬНО - data class с правильными полями
data class User(
    val id: Int,
    val name: String,
    val avatarUrl: String?
    // lastUpdate не включен в сравнение
) {
    // Храним timestamp отдельно, не влияет на equals
    @Transient
    var lastUpdate: Long = System.currentTimeMillis()
}

// Или явно переопределить equals
class User(
    val id: Int,
    var name: String,
    var avatarUrl: String?,
    val lastUpdate: Long
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is User) return false

        // Сравниваем только значимые поля
        return id == other.id &&
                name == other.name &&
                avatarUrl == other.avatarUrl
        // lastUpdate игнорируем!
    }

    override fun hashCode(): Int {
        var result = id
        result = 31 * result + name.hashCode()
        result = 31 * result + (avatarUrl?.hashCode() ?: 0)
        return result
    }
}
```

### 7. Проблемы с памятью при больших списках

```kotlin
// НЕПРАВИЛЬНО - держим ссылки на старые списки
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private val updateHistory = mutableListOf<List<User>>()

    fun updateUsers(newUsers: List<User>) {
        updateHistory.add(users) // Memory leak!

        CoroutineScope(Dispatchers.Default).launch {
            // ...
        }
    }
}

//  ПРАВИЛЬНО - не храним лишние ссылки
class UserAdapter : RecyclerView.Adapter<UserViewHolder>() {
    private var users: List<User> = emptyList()

    fun updateUsers(newUsers: List<User>) {
        val oldList = users // Локальная переменная

        CoroutineScope(Dispatchers.Default).launch {
            val diff = DiffUtil.calculateDiff(...)

            withContext(Dispatchers.Main) {
                users = newUsers // oldList может быть GC'd
                diff.dispatchUpdatesTo(this@UserAdapter)
            }
        }
    }
}
```

### Решения и Best Practices

**1. Использовать ListAdapter**

```kotlin
// Автоматически обрабатывает все edge cases
class UserAdapter : ListAdapter<User, UserViewHolder>(UserDiffCallback()) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        // ...
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

    // Опционально - частичное обновление
    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        return if (oldItem.name != newItem.name) {
            "name_changed"
        } else {
            null
        }
    }
}
```

**2. Оптимизация для больших списков**

```kotlin
// Использовать Paging 3
class UserAdapter : PagingDataAdapter<User, UserViewHolder>(UserDiffCallback()) {
    // Автоматически загружает данные порциями
}

// Или ограничить размер diff
fun submitListSafely(newList: List<User>) {
    val oldList = currentList

    // Если списки слишком большие, не использовать diff
    if (oldList.size > 5000 || newList.size > 5000) {
        // Просто заменить весь список
        submitList(newList)
        return
    }

    // Для небольших списков использовать diff
    submitList(newList)
}
```

**3. Debouncing для частых обновлений**

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())

    // Debounce updates
    val users: StateFlow<List<User>> = _users
        .debounce(300) // Wait 300ms before processing
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun updateUsers(newUsers: List<User>) {
        _users.value = newUsers
    }
}
```

**English**: DiffUtil background calculation issues occur when: 1) **Data modified during calculation** - use immutable copies, 2) **Heavy computations in callbacks** - pre-compute hashes/comparisons, 3) **Very large datasets** (10,000+) - use Paging or limit size, 4) **Race conditions** - cancel previous jobs, use `ListAdapter`, 5) **Data changes between calc and dispatch** - use mutex/locks, 6) **Incorrect equals/hashCode** - implement properly, exclude timestamps, 7) **Memory issues** - avoid storing old list references. **Solution**: Use `ListAdapter` which handles all edge cases automatically. For large lists, use `PagingDataAdapter` or skip diff if size > 5000.
