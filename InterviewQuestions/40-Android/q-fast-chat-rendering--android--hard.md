---
id: 20251012-1227136
title: "Fast Chat Rendering / Быстрый рендеринг чата"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: [android/performance, android/recyclerview, chat, diffutil, flow, optimization, paging, performance, recyclerview, room, difficulty/hard]
---
# Как можно гарантировать быструю отрисовку чатов?

**English**: How can you guarantee fast chat rendering?

## Answer (EN)
To ensure **fast chat rendering without lags**, you need to optimize:

1. **RecyclerView** (ViewHolder, DiffUtil, Payloads)
2. **UI Thread** management (Coroutines, Paging 3)
3. **Image loading** (Glide, Coil)
4. **Offline cache** (Room + Flow/LiveData)

## Comprehensive Chat Optimization Strategy

### 1. RecyclerView Optimization

#### A. Proper ViewHolder Implementation

```kotlin
class ChatAdapter : ListAdapter<ChatMessage, ChatAdapter.ViewHolder>(ChatDiffCallback()) {

    // Multiple view types for different message types
    companion object {
        const val VIEW_TYPE_TEXT_SENT = 0
        const val VIEW_TYPE_TEXT_RECEIVED = 1
        const val VIEW_TYPE_IMAGE_SENT = 2
        const val VIEW_TYPE_IMAGE_RECEIVED = 3
    }

    sealed class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {

        class TextSentViewHolder(val binding: ItemChatTextSentBinding) :
            ViewHolder(binding.root) {
            fun bind(message: ChatMessage) {
                binding.messageText.text = message.text
                binding.timestamp.text = message.formattedTime
                binding.statusIcon.setImageResource(
                    when (message.status) {
                        MessageStatus.SENT -> R.drawable.ic_check
                        MessageStatus.DELIVERED -> R.drawable.ic_check_double
                        MessageStatus.READ -> R.drawable.ic_check_double_blue
                        else -> 0
                    }
                )
            }
        }

        class TextReceivedViewHolder(val binding: ItemChatTextReceivedBinding) :
            ViewHolder(binding.root) {
            fun bind(message: ChatMessage) {
                binding.messageText.text = message.text
                binding.timestamp.text = message.formattedTime
                binding.senderName.text = message.senderName
            }
        }

        class ImageSentViewHolder(val binding: ItemChatImageSentBinding) :
            ViewHolder(binding.root) {
            fun bind(message: ChatMessage) {
                // Optimized image loading
                Glide.with(binding.root.context)
                    .load(message.imageUrl)
                    .override(400, 400)  // Limit size
                    .centerCrop()
                    .thumbnail(0.1f)  // Show low-res thumbnail first
                    .into(binding.imageView)

                binding.timestamp.text = message.formattedTime
            }
        }
    }

    override fun getItemViewType(position: Int): Int {
        val message = getItem(position)
        return when {
            message.isSent && message.type == MessageType.TEXT -> VIEW_TYPE_TEXT_SENT
            !message.isSent && message.type == MessageType.TEXT -> VIEW_TYPE_TEXT_RECEIVED
            message.isSent && message.type == MessageType.IMAGE -> VIEW_TYPE_IMAGE_SENT
            else -> VIEW_TYPE_IMAGE_RECEIVED
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return when (viewType) {
            VIEW_TYPE_TEXT_SENT -> ViewHolder.TextSentViewHolder(
                ItemChatTextSentBinding.inflate(
                    LayoutInflater.from(parent.context), parent, false
                )
            )
            VIEW_TYPE_TEXT_RECEIVED -> ViewHolder.TextReceivedViewHolder(
                ItemChatTextReceivedBinding.inflate(
                    LayoutInflater.from(parent.context), parent, false
                )
            )
            VIEW_TYPE_IMAGE_SENT -> ViewHolder.ImageSentViewHolder(
                ItemChatImageSentBinding.inflate(
                    LayoutInflater.from(parent.context), parent, false
                )
            )
            else -> throw IllegalArgumentException("Unknown view type: $viewType")
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val message = getItem(position)
        when (holder) {
            is ViewHolder.TextSentViewHolder -> holder.bind(message)
            is ViewHolder.TextReceivedViewHolder -> holder.bind(message)
            is ViewHolder.ImageSentViewHolder -> holder.bind(message)
        }
    }

    // Stable IDs for better animations
    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        return getItem(position).id.toLong()
    }
}
```

---

#### B. DiffUtil with Payloads

```kotlin
class ChatDiffCallback : DiffUtil.ItemCallback<ChatMessage>() {

    override fun areItemsTheSame(oldItem: ChatMessage, newItem: ChatMessage): Boolean {
        return oldItem.id == newItem.id  // Same message
    }

    override fun areContentsTheSame(oldItem: ChatMessage, newItem: ChatMessage): Boolean {
        return oldItem == newItem  // Same content
    }

    // Payloads for partial updates
    override fun getChangePayload(oldItem: ChatMessage, newItem: ChatMessage): Any? {
        val changes = mutableListOf<String>()

        if (oldItem.status != newItem.status) {
            changes.add(PAYLOAD_STATUS)
        }
        if (oldItem.text != newItem.text) {
            changes.add(PAYLOAD_TEXT)
        }

        return if (changes.isNotEmpty()) changes else null
    }

    companion object {
        const val PAYLOAD_STATUS = "STATUS"
        const val PAYLOAD_TEXT = "TEXT"
    }
}

// Handle payloads in adapter
override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: List<Any>) {
    if (payloads.isEmpty()) {
        super.onBindViewHolder(holder, position, payloads)
        return
    }

    val message = getItem(position)

    payloads.forEach { payload ->
        if (payload is List<*>) {
            payload.forEach { change ->
                when (change) {
                    ChatDiffCallback.PAYLOAD_STATUS -> {
                        // Update only status icon
                        if (holder is ViewHolder.TextSentViewHolder) {
                            holder.binding.statusIcon.setImageResource(
                                getStatusIcon(message.status)
                            )
                        }
                    }
                    ChatDiffCallback.PAYLOAD_TEXT -> {
                        // Update only text
                        if (holder is ViewHolder.TextSentViewHolder) {
                            holder.binding.messageText.text = message.text
                        }
                    }
                }
            }
        }
    }
}
```

**Benefit:** Only changed parts updated, not entire item.

---

### 2. UI Thread Optimization

#### A. Coroutines for Background Work

```kotlin
class ChatViewModel(
    private val repository: ChatRepository
) : ViewModel() {

    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages.asStateFlow()

    init {
        loadMessages()
    }

    private fun loadMessages() {
        viewModelScope.launch {
            repository.getMessagesFlow(chatId)
                .flowOn(Dispatchers.IO)  // Background thread
                .collect { messages ->
                    _messages.value = messages  // Main thread
                }
        }
    }

    fun sendMessage(text: String) {
        viewModelScope.launch {
            val message = ChatMessage(
                id = generateId(),
                chatId = chatId,
                text = text,
                timestamp = System.currentTimeMillis(),
                isSent = true,
                status = MessageStatus.SENDING
            )

            // Optimistic update (instant UI)
            _messages.value = _messages.value + message

            // Send in background
            withContext(Dispatchers.IO) {
                repository.sendMessage(message)
            }
        }
    }
}
```

---

#### B. Paging 3 for Large Chat History

```kotlin
// DAO with PagingSource
@Dao
interface ChatMessageDao {

    @Query("""
        SELECT * FROM chat_messages
        WHERE chat_id = :chatId
        ORDER BY timestamp DESC
    """)
    fun getMessagesPagingSource(chatId: String): PagingSource<Int, ChatMessage>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessages(messages: List<ChatMessage>)
}

// Repository
class ChatRepository(
    private val dao: ChatMessageDao,
    private val api: ChatApiService
) {
    fun getMessagesPager(chatId: String): Flow<PagingData<ChatMessage>> {
        return Pager(
            config = PagingConfig(
                pageSize = 50,  // Load 50 messages at a time
                prefetchDistance = 10,
                enablePlaceholders = false
            ),
            pagingSourceFactory = { dao.getMessagesPagingSource(chatId) }
        ).flow
    }
}

// ViewModel
class ChatViewModel(private val repository: ChatRepository) : ViewModel() {

    val messages: Flow<PagingData<ChatMessage>> =
        repository.getMessagesPager(chatId)
            .cachedIn(viewModelScope)  // Cache data
}

// Adapter
class ChatPagingAdapter : PagingDataAdapter<ChatMessage, ChatAdapter.ViewHolder>(
    ChatDiffCallback()
) {
    // Same ViewHolder implementation as before
}

// Fragment
class ChatFragment : Fragment() {
    private val viewModel: ChatViewModel by viewModels()
    private val adapter = ChatPagingAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.recyclerView.apply {
            layoutManager = LinearLayoutManager(context).apply {
                reverseLayout = true  // Start from bottom (newest messages)
            }
            adapter = this@ChatFragment.adapter
            setHasFixedSize(true)
        }

        // Collect paging data
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.messages.collectLatest { pagingData ->
                adapter.submitData(pagingData)
            }
        }
    }
}
```

**Benefits:**
- **Memory efficient**: Only loads visible + prefetch messages
- **Smooth scrolling**: Loads more as user scrolls
- **Automatic loading states**: Loading, error, retry

---

### 3. Image Loading Optimization

```kotlin
// Configure Glide globally
@GlideModule
class ChatGlideModule : AppGlideModule() {

    override fun applyOptions(context: Context, builder: GlideBuilder) {
        // Larger memory cache for chat images
        val memoryCacheSizeBytes = 1024 * 1024 * 50  // 50MB
        builder.setMemoryCache(LruResourceCache(memoryCacheSizeBytes.toLong()))

        // Disk cache
        val diskCacheSizeBytes = 1024 * 1024 * 250  // 250MB
        builder.setDiskCache(InternalCacheDiskCacheFactory(context, diskCacheSizeBytes.toLong()))

        // Bitmap pool
        builder.setBitmapPool(LruBitmapPool(memoryCacheSizeBytes.toLong()))
    }

    override fun isManifestParsingEnabled(): Boolean {
        return false  // Disable manifest parsing for performance
    }
}

// In ViewHolder
fun bind(message: ChatMessage) {
    GlideApp.with(binding.root.context)
        .load(message.imageUrl)
        .override(400, 400)  // Resize
        .centerCrop()
        .thumbnail(0.1f)  // Show low-res placeholder
        .diskCacheStrategy(DiskCacheStrategy.ALL)  // Cache original + resized
        .transition(DrawableTransitionOptions.withCrossFade(200))
        .into(binding.imageView)
}

// Or use Coil (Kotlin-first, coroutine-based)
fun bind(message: ChatMessage) {
    binding.imageView.load(message.imageUrl) {
        size(400, 400)
        crossfade(200)
        placeholder(R.drawable.placeholder)
        memoryCachePolicy(CachePolicy.ENABLED)
        diskCachePolicy(CachePolicy.ENABLED)
    }
}
```

---

### 4. Offline Cache with Room + Flow

```kotlin
// Entity
@Entity(tableName = "chat_messages")
data class ChatMessage(
    @PrimaryKey val id: String,
    val chatId: String,
    val text: String,
    val imageUrl: String? = null,
    val timestamp: Long,
    val senderId: String,
    val isSent: Boolean,
    @ColumnInfo(name = "status")
    val status: MessageStatus,
    @ColumnInfo(name = "is_synced")
    val isSynced: Boolean = false
)

// DAO
@Dao
interface ChatMessageDao {

    @Query("""
        SELECT * FROM chat_messages
        WHERE chat_id = :chatId
        ORDER BY timestamp DESC
    """)
    fun getMessagesFlow(chatId: String): Flow<List<ChatMessage>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMessages(messages: List<ChatMessage>)

    @Query("SELECT * FROM chat_messages WHERE is_synced = 0")
    suspend fun getUnsyncedMessages(): List<ChatMessage>

    @Update
    suspend fun updateMessage(message: ChatMessage)
}

// Repository with offline-first approach
class ChatRepository(
    private val dao: ChatMessageDao,
    private val api: ChatApiService
) {
    // Offline-first: Room is source of truth
    fun getMessagesFlow(chatId: String): Flow<List<ChatMessage>> {
        return dao.getMessagesFlow(chatId)
            .onStart {
                // Sync from network in background
                syncMessagesFromNetwork(chatId)
            }
    }

    private suspend fun syncMessagesFromNetwork(chatId: String) {
        try {
            val messages = api.getMessages(chatId)
            dao.insertMessages(messages.map { it.copy(isSynced = true) })
        } catch (e: Exception) {
            // Use cached data if network fails
            Log.e("Chat", "Failed to sync: ${e.message}")
        }
    }

    suspend fun sendMessage(message: ChatMessage) {
        // Insert locally first (optimistic update)
        dao.insertMessages(listOf(message.copy(isSynced = false)))

        try {
            // Send to server
            val sentMessage = api.sendMessage(message)
            dao.updateMessage(sentMessage.copy(isSynced = true))
        } catch (e: Exception) {
            // Mark as failed, retry later
            dao.updateMessage(message.copy(status = MessageStatus.FAILED))
        }
    }

    // Background sync worker
    suspend fun syncUnsyncedMessages() {
        val unsynced = dao.getUnsyncedMessages()
        unsynced.forEach { message ->
            try {
                val sentMessage = api.sendMessage(message)
                dao.updateMessage(sentMessage.copy(isSynced = true))
            } catch (e: Exception) {
                // Retry later
            }
        }
    }
}
```

---

## Additional Optimizations

### 5. RecyclerView Configuration

```kotlin
binding.recyclerView.apply {
    layoutManager = LinearLayoutManager(context).apply {
        reverseLayout = true  // Newest at bottom
        stackFromEnd = true  // Start from bottom
    }

    // Fixed size improves performance
    setHasFixedSize(true)

    // Item animator optimization
    itemAnimator = DefaultItemAnimator().apply {
        supportsChangeAnimations = false  // Disable change animations
    }

    // Nested scrolling
    isNestedScrollingEnabled = true

    // Prefetch optimization
    (layoutManager as? LinearLayoutManager)?.apply {
        isItemPrefetchEnabled = true
        initialPrefetchItemCount = 4
    }
}
```

---

### 6. Text Processing Optimization

```kotlin
// Pre-process in ViewModel
class ChatViewModel : ViewModel() {

    fun processMessage(rawMessage: RawMessage): ChatMessage {
        return ChatMessage(
            id = rawMessage.id,
            text = rawMessage.text,
            // Pre-format timestamp
            formattedTime = formatTimestamp(rawMessage.timestamp),
            // Pre-parse links
            links = extractLinks(rawMessage.text),
            // Pre-detect emojis
            hasEmojis = containsEmojis(rawMessage.text)
        )
    }

    private fun formatTimestamp(timestamp: Long): String {
        val formatter = SimpleDateFormat("HH:mm", Locale.getDefault())
        return formatter.format(Date(timestamp))
    }

    private fun extractLinks(text: String): List<String> {
        val urlPattern = Patterns.WEB_URL
        val matcher = urlPattern.matcher(text)
        val links = mutableListOf<String>()
        while (matcher.find()) {
            matcher.group()?.let { links.add(it) }
        }
        return links
    }
}
```

---

### 7. Scroll Performance

```kotlin
// Detect scroll state to pause image loading
binding.recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {

    override fun onScrollStateChanged(recyclerView: RecyclerView, newState: Int) {
        when (newState) {
            RecyclerView.SCROLL_STATE_IDLE -> {
                // Resume image loading
                Glide.with(recyclerView.context).resumeRequests()
            }
            RecyclerView.SCROLL_STATE_DRAGGING,
            RecyclerView.SCROLL_STATE_SETTLING -> {
                // Pause image loading during scroll
                Glide.with(recyclerView.context).pauseRequests()
            }
        }
    }
})
```

---

## Summary Checklist

### RecyclerView
-  Use **ViewHolder** with ViewBinding
-  Implement **DiffUtil** with ListAdapter
-  Use **payloads** for partial updates
-  Enable **stable IDs**
-  Set **hasFixedSize** if applicable
-  Use **multiple view types** for different messages

### Threading
-  Use **Kotlin Coroutines** for background work
-  Use **Dispatchers.IO** for database/network
-  Use **Paging 3** for large message history
-  **Never block UI thread**

### Image Loading
-  Use **Glide** or **Coil**
-  Set **override()** to limit image size
-  Use **thumbnail()** for progressive loading
-  Configure **memory/disk cache**
-  **Pause requests** during scroll

### Offline Cache
-  Use **Room** as single source of truth
-  Use **Flow** for reactive updates
-  Implement **offline-first** pattern
-  Sync **unsynced messages** in background
-  Use **WorkManager** for reliable sync

---

## Ответ (RU)
Чтобы чат работал быстро и без лагов, нужно:

1. **Оптимизировать RecyclerView** - ViewHolder, DiffUtil, Payloads для частичных обновлений
2. **Минимизировать работу в UI Thread** - использовать Coroutines и Paging 3
3. **Оптимизировать загрузку изображений** - Glide или Coil с кэшированием
4. **Использовать офлайн-кэш** - Room + Flow/LiveData для offline-first подхода

