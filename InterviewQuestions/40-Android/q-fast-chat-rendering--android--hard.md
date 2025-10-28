---
id: 20251020-200700
title: Fast Chat Rendering / Быстрый рендеринг чата
aliases: [Fast Chat Rendering, Быстрый рендеринг чата]
topic: android
subtopics: [performance-memory, ui-views, ui-compose]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-performance-optimization--android--medium
  - q-diffutil-background-calculation-issues--android--medium
  - q-recyclerview-optimization--android--medium
  - c-performance-optimization
  - c-recyclerview
sources:
  - https://developer.android.com/topic/performance/rendering
created: 2025-10-20
updated: 2025-10-28
tags: [android/performance-memory, android/ui-views, android/ui-compose, chat, difficulty/hard, diffutil, paging, performance, recyclerview]
---

# Вопрос (RU)
> Как оптимизировать рендеринг чатов для высокой производительности?

# Question (EN)
> How can you optimize chat rendering for high performance?

---

## Ответ (RU)

Для быстрого рендеринга чатов оптимизируйте UI (RecyclerView/LazyColumn), загрузку данных (Paging 3), изображения (Glide/Coil) и кэш (Room).

### XML Views с RecyclerView

**1. DiffUtil с Payloads**

✅ Частичные обновления:
```kotlin
class ChatDiffCallback : DiffUtil.ItemCallback<ChatMessage>() {
    override fun areItemsTheSame(old: ChatMessage, new: ChatMessage) =
        old.id == new.id

    override fun getChangePayload(old: ChatMessage, new: ChatMessage): Any? {
        return when {
            old.status != new.status -> StatusPayload(new.status)
            old.text != new.text -> TextPayload(new.text)
            else -> null
        }
    }
}

class ChatViewHolder(private val binding: ItemChatBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(message: ChatMessage, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            binding.messageText.text = message.text
            binding.timestamp.text = message.formattedTime
            updateStatus(message.status)
        } else {
            payloads.forEach { payload ->
                when (payload) {
                    is StatusPayload -> updateStatus(payload.status)
                    is TextPayload -> binding.messageText.text = payload.text
                }
            }
        }
    }
}
```

❌ Без payloads:
```kotlin
override fun getChangePayload(old: ChatMessage, new: ChatMessage): Any? = null
// Полная перерисовка ViewHolder при любом изменении
```

**2. Paging 3**

```kotlin
class ChatRepository {
    fun getMessages(): Flow<PagingData<ChatMessage>> {
        return Pager(
            config = PagingConfig(pageSize = 50, prefetchDistance = 10),
            pagingSourceFactory = { ChatPagingSource(db) }
        ).flow
    }
}

// Использование
lifecycleScope.launch {
    viewModel.messages.collectLatest { pagingData ->
        adapter.submitData(pagingData)
    }
}
```

### Compose с LazyColumn

**1. Стабильные ключи и remember**

✅ Оптимизированный LazyColumn:
```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages by viewModel.messages.collectAsState()

    LazyColumn(
        reverseLayout = true,
        contentPadding = PaddingValues(8.dp)
    ) {
        items(
            items = messages,
            key = { it.id } // Стабильные ключи
        ) { message ->
            ChatMessageItem(message)
        }
    }
}

@Composable
fun ChatMessageItem(message: ChatMessage) {
    val formattedTime = remember(message.timestamp) {
        formatTimestamp(message.timestamp)
    }

    Row(Modifier.fillMaxWidth().padding(8.dp)) {
        Text(message.text)
        Text(formattedTime)
    }
}
```

❌ Без оптимизации:
```kotlin
items(messages) { message -> // Нет ключей
    ChatMessageItem(message)
}
// Ненужные recomposition при изменениях
```

**2. Paging с Compose**

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages = viewModel.messages.collectAsLazyPagingItems()

    LazyColumn(reverseLayout = true) {
        items(
            count = messages.itemCount,
            key = messages.itemKey { it.id }
        ) { index ->
            messages[index]?.let { ChatMessageItem(it) }
        }
    }
}
```

**3. derivedStateOf для вычислений**

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messagesState by viewModel.messages.collectAsState()

    val sortedMessages by remember {
        derivedStateOf {
            messagesState.sortedByDescending { it.timestamp }
        }
    }

    LazyColumn {
        items(sortedMessages, key = { it.id }) { message ->
            ChatMessageItem(message)
        }
    }
}
```

### Оптимизация изображений

**Glide (XML Views):**
```kotlin
fun loadChatImage(imageView: ImageView, url: String) {
    Glide.with(imageView.context)
        .load(url)
        .override(400, 400)
        .thumbnail(0.1f)
        .diskCacheStrategy(DiskCacheStrategy.ALL)
        .into(imageView)
}
```

**Coil (Compose):**
```kotlin
@Composable
fun ChatImageMessage(imageUrl: String) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .size(400, 400)
            .memoryCacheKey(imageUrl)
            .diskCacheKey(imageUrl)
            .build(),
        contentDescription = null,
        modifier = Modifier.size(200.dp)
    )
}
```

### Офлайн кэш

```kotlin
@Entity
data class ChatMessage(
    @PrimaryKey val id: String,
    val text: String,
    val timestamp: Long,
    val status: MessageStatus
)

@Dao
interface ChatDao {
    @Query("SELECT * FROM ChatMessage ORDER BY timestamp DESC")
    fun getMessages(): Flow<List<ChatMessage>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(message: ChatMessage)
}
```

### Ключевые принципы

**RecyclerView:**
- ViewHolder Pattern для переиспользования
- DiffUtil + Payloads для частичных обновлений
- Paging 3 для больших списков

**Compose:**
- Стабильные key() для идентификации
- remember/derivedStateOf для кэширования
- @Immutable data classes

**Общие:**
- Lazy loading изображений с ограничением размера
- Офлайн кэш через Room
- Фоновые потоки для загрузки данных

## Answer (EN)

For fast chat rendering, optimize UI (RecyclerView/LazyColumn), data loading (Paging 3), images (Glide/Coil), and cache (Room).

### XML Views with RecyclerView

**1. DiffUtil with Payloads**

✅ Partial updates:
```kotlin
class ChatDiffCallback : DiffUtil.ItemCallback<ChatMessage>() {
    override fun areItemsTheSame(old: ChatMessage, new: ChatMessage) =
        old.id == new.id

    override fun getChangePayload(old: ChatMessage, new: ChatMessage): Any? {
        return when {
            old.status != new.status -> StatusPayload(new.status)
            old.text != new.text -> TextPayload(new.text)
            else -> null
        }
    }
}

class ChatViewHolder(private val binding: ItemChatBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(message: ChatMessage, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            binding.messageText.text = message.text
            binding.timestamp.text = message.formattedTime
            updateStatus(message.status)
        } else {
            payloads.forEach { payload ->
                when (payload) {
                    is StatusPayload -> updateStatus(payload.status)
                    is TextPayload -> binding.messageText.text = payload.text
                }
            }
        }
    }
}
```

❌ Without payloads:
```kotlin
override fun getChangePayload(old: ChatMessage, new: ChatMessage): Any? = null
// Full ViewHolder redraw on any change
```

**2. Paging 3**

```kotlin
class ChatRepository {
    fun getMessages(): Flow<PagingData<ChatMessage>> {
        return Pager(
            config = PagingConfig(pageSize = 50, prefetchDistance = 10),
            pagingSourceFactory = { ChatPagingSource(db) }
        ).flow
    }
}

// Usage
lifecycleScope.launch {
    viewModel.messages.collectLatest { pagingData ->
        adapter.submitData(pagingData)
    }
}
```

### Compose with LazyColumn

**1. Stable keys and remember**

✅ Optimized LazyColumn:
```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages by viewModel.messages.collectAsState()

    LazyColumn(
        reverseLayout = true,
        contentPadding = PaddingValues(8.dp)
    ) {
        items(
            items = messages,
            key = { it.id } // Stable keys
        ) { message ->
            ChatMessageItem(message)
        }
    }
}

@Composable
fun ChatMessageItem(message: ChatMessage) {
    val formattedTime = remember(message.timestamp) {
        formatTimestamp(message.timestamp)
    }

    Row(Modifier.fillMaxWidth().padding(8.dp)) {
        Text(message.text)
        Text(formattedTime)
    }
}
```

❌ Without optimization:
```kotlin
items(messages) { message -> // No keys
    ChatMessageItem(message)
}
// Unnecessary recomposition on changes
```

**2. Paging with Compose**

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messages = viewModel.messages.collectAsLazyPagingItems()

    LazyColumn(reverseLayout = true) {
        items(
            count = messages.itemCount,
            key = messages.itemKey { it.id }
        ) { index ->
            messages[index]?.let { ChatMessageItem(it) }
        }
    }
}
```

**3. derivedStateOf for calculations**

```kotlin
@Composable
fun ChatScreen(viewModel: ChatViewModel) {
    val messagesState by viewModel.messages.collectAsState()

    val sortedMessages by remember {
        derivedStateOf {
            messagesState.sortedByDescending { it.timestamp }
        }
    }

    LazyColumn {
        items(sortedMessages, key = { it.id }) { message ->
            ChatMessageItem(message)
        }
    }
}
```

### Image optimization

**Glide (XML Views):**
```kotlin
fun loadChatImage(imageView: ImageView, url: String) {
    Glide.with(imageView.context)
        .load(url)
        .override(400, 400)
        .thumbnail(0.1f)
        .diskCacheStrategy(DiskCacheStrategy.ALL)
        .into(imageView)
}
```

**Coil (Compose):**
```kotlin
@Composable
fun ChatImageMessage(imageUrl: String) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .size(400, 400)
            .memoryCacheKey(imageUrl)
            .diskCacheKey(imageUrl)
            .build(),
        contentDescription = null,
        modifier = Modifier.size(200.dp)
    )
}
```

### Offline cache

```kotlin
@Entity
data class ChatMessage(
    @PrimaryKey val id: String,
    val text: String,
    val timestamp: Long,
    val status: MessageStatus
)

@Dao
interface ChatDao {
    @Query("SELECT * FROM ChatMessage ORDER BY timestamp DESC")
    fun getMessages(): Flow<List<ChatMessage>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessage(message: ChatMessage)
}
```

### Key principles

**RecyclerView:**
- ViewHolder Pattern for reuse
- DiffUtil + Payloads for partial updates
- Paging 3 for large lists

**Compose:**
- Stable key() for identification
- remember/derivedStateOf for caching
- @Immutable data classes

**Common:**
- Lazy image loading with size limits
- Offline cache via Room
- Background threads for data loading

---

## Follow-ups

- How to handle real-time message updates efficiently?
- What are the memory implications of caching thousands of messages?
- When should you use AsyncListDiffer vs ListAdapter?
- How to optimize chat with rich media (videos, GIFs)?
- What's the best strategy for bidirectional infinite scrolling?

## References

- [[c-performance-optimization]]
- [[c-recyclerview]]
- [[moc-android]]

## Related Questions

### Prerequisites
- [[q-recyclerview-optimization--android--medium]]
- [[q-diffutil-background-calculation-issues--android--medium]]

### Same Level
- [[q-android-performance-optimization--android--medium]]

### Advanced
- [[q-memory-optimization-large-datasets--android--hard]]
