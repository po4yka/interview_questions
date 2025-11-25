---
id: android-219
title: How To Create Chat Lists From A UI Perspective / Как создать списки чатов с точки зрения UI
aliases: [How To Create Chat Lists From A UI Perspective, Как создать списки чатов с точки зрения UI]
topic: android
subtopics:
  - ui-views
question_kind: theory
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-recyclerview
  - q-how-dialog-differs-from-other-navigation--android--medium
  - q-how-to-create-dynamic-screens-at-runtime--android--hard
  - q-network-error-handling-strategies--networking--medium
  - q-what-are-px-dp-sp--android--easy
  - q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium
  - q-what-is-known-about-recyclerview--android--easy
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/hard, recyclerview]

date created: Saturday, November 1st 2025, 12:46:53 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Как создать списки чатов с точки зрения UI

# Question (EN)
> How To Create Chat Lists From A UI Perspective

---

## Ответ (RU)
Создание списков чатов с точки зрения UI требует учёта нескольких ключевых аспектов: как представить список диалогов так, чтобы он был наглядным, отзывчивым, быстро работал и корректно масштабировался на большие активные чаты.

### Основные Шаги

1. Определить модель данных для элемента списка (чат/диалог).
2. Создать UI-макет элемента списка (аватар, имя, последний текст, время, индикаторы online/typing, бейдж непрочитанного, пин).
3. Реализовать RecyclerView + Adapter + ViewHolder под эту модель.
4. Настроить наблюдение за данными (`ViewModel`/`LiveData`/`Flow`) и обновление списка через `ListAdapter`/`DiffUtil`.
5. Обеспечить сортировку (сначала закреплённые, затем по времени последнего сообщения).
6. Оптимизировать производительность (`DiffUtil`, пагинация, кеширование изображений).

### 1. Модели Данных

Важно разделять модель для списка чатов и модели для сообщений: список оперирует сущностью "чат/диалог", а пузырьки сообщений относятся к экрану деталей чата. Ниже модели сообщений приведены как контекст: они не обязательны для реализации списка, но демонстрируют согласованный подход к данным UI.

```kotlin
// Модель чата (диалога) для списка чатов
data class ChatRoom(
    val id: String,
    val name: String,
    val avatarUrl: String?,
    val lastMessage: String,
    val lastMessageTime: Long,
    val unreadCount: Int,
    val isOnline: Boolean,
    val isTyping: Boolean = false,
    val isPinned: Boolean = false
)

// Модели сообщений для экрана деталей чата (контекст для UI, не часть списка чатов)
sealed class ChatMessage {
    abstract val id: String
    abstract val timestamp: Long
    abstract val senderId: String

    data class TextMessage(
        override val id: String,
        override val timestamp: Long,
        override val senderId: String,
        val text: String,
        val status: MessageStatus
    ) : ChatMessage()

    data class ImageMessage(
        override val id: String,
        override val timestamp: Long,
        override val senderId: String,
        val imageUrl: String,
        val caption: String?,
        val status: MessageStatus
    ) : ChatMessage()

    data class DateSeparator(
        override val id: String,
        override val timestamp: Long,
        val date: String
    ) : ChatMessage() {
        override val senderId: String = ""
    }
}

enum class MessageStatus {
    SENDING, SENT, DELIVERED, READ, FAILED
}
```

### 2. Макеты Элементов

#### Макет Элемента Списка Чатов

```xml
<!-- item_chat_room.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/selectableItemBackground"
    android:padding="16dp">

    <!-- Аватар с индикатором онлайн -->
    <FrameLayout
        android:id="@+id/avatarContainer"
        android:layout_width="56dp"
        android:layout_height="56dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent">

        <com.google.android.material.imageview.ShapeableImageView
            android:id="@+id/avatarImage"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:scaleType="centerCrop"
            app:shapeAppearanceOverlay="@style/CircleImageView"
            tools:src="@tools:sample/avatars" />

        <View
            android:id="@+id/onlineIndicator"
            android:layout_width="12dp"
            android:layout_height="12dp"
            android:layout_gravity="bottom|end"
            android:layout_margin="2dp"
            android:background="@drawable/online_indicator"
            android:visibility="gone" />
    </FrameLayout>

    <!-- Название чата -->
    <TextView
        android:id="@+id/chatNameText"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:layout_marginEnd="8dp"
        android:ellipsize="end"
        android:maxLines="1"
        android:textColor="?android:textColorPrimary"
        android:textSize="16sp"
        android:textStyle="bold"
        app:layout_constraintEnd_toStartOf="@id/timestampText"
        app:layout_constraintStart_toEndOf="@id/avatarContainer"
        app:layout_constraintTop_toTopOf="@id/avatarContainer"
        tools:text="John Doe" />

    <!-- Последнее сообщение -->
    <TextView
        android:id="@+id/lastMessageText"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        android:layout_marginEnd="8dp"
        android:ellipsize="end"
        android:maxLines="2"
        android:textColor="?android:textColorSecondary"
        android:textSize="14sp"
        app:layout_constraintEnd_toStartOf="@id/unreadBadge"
        app:layout_constraintStart_toStartOf="@id/chatNameText"
        app:layout_constraintTop_toBottomOf="@id/chatNameText"
        tools:text="Hey, how are you doing?" />

    <!-- Индикатор набора (взаимоисключается с lastMessageText) -->
    <TextView
        android:id="@+id/typingIndicator"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        android:text="typing..."
        android:textColor="@color/primary"
        android:textSize="14sp"
        android:textStyle="italic"
        android:visibility="gone"
        app:layout_constraintEnd_toEndOf="@id/lastMessageText"
        app:layout_constraintStart_toStartOf="@id/chatNameText"
        app:layout_constraintTop_toBottomOf="@id/chatNameText" />

    <!-- Время -->
    <TextView
        android:id="@+id/timestampText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textColor="?android:textColorSecondary"
        android:textSize="12sp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="@id/chatNameText"
        tools:text="12:34 PM" />

    <!-- Бейдж непрочитанных -->
    <TextView
        android:id="@+id/unreadBadge"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:minWidth="24dp"
        android:minHeight="24dp"
        android:paddingHorizontal="6dp"
        android:gravity="center"
        android:background="@drawable/unread_badge_background"
        android:textColor="@android:color/white"
        android:textSize="12sp"
        android:visibility="gone"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@id/timestampText"
        tools:text="3"
        tools:visibility="visible" />

    <!-- Индикатор пина -->
    <ImageView
        android:id="@+id/pinIndicator"
        android:layout_width="16dp"
        android:layout_height="16dp"
        android:layout_marginEnd="4dp"
        android:src="@drawable/ic_pin"
        android:tint="?android:textColorSecondary"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="@id/timestampText"
        app:layout_constraintEnd_toStartOf="@id/timestampText"
        app:layout_constraintTop_toTopOf="@id/timestampText" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

#### Макет Сообщения (для Экрана Деталей Чата, контекст)

```xml
<!-- item_message_sent.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="8dp">

    <com.google.android.material.card.MaterialCardView
        android:id="@+id/messageCard"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="64dp"
        app:cardBackgroundColor="@color/message_sent_background"
        app:cardCornerRadius="12dp"
        app:cardElevation="1dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintWidth_max="280dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">

            <TextView
                android:id="@+id/messageText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:textColor="@android:color/white"
                android:textSize="16sp" />

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_gravity="end"
                android:layout_marginTop="4dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <TextView
                    android:id="@+id/messageTime"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:textColor="@color/message_time_color"
                    android:textSize="12sp" />

                <ImageView
                    android:id="@+id/messageStatus"
                    android:layout_width="16dp"
                    android:layout_height="16dp"
                    android:layout_marginStart="4dp"
                    android:src="@drawable/ic_check_double"
                    android:tint="@color/message_read_color" />
            </LinearLayout>
        </LinearLayout>
    </com.google.android.material.card.MaterialCardView>

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 3. Адаптер И ViewHolder

```kotlin
class ChatRoomAdapter(
    private val onChatClick: (ChatRoom) -> Unit
) : ListAdapter<ChatRoom, ChatRoomAdapter.ChatRoomViewHolder>(ChatRoomDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatRoomViewHolder {
        val binding = ItemChatRoomBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ChatRoomViewHolder(binding, onChatClick)
    }

    override fun onBindViewHolder(holder: ChatRoomViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Если вы используете payload'ы из getChangePayload, переопределите и этот вариант:
    override fun onBindViewHolder(
        holder: ChatRoomViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            holder.bindPartial(getItem(position), payloads)
        }
    }

    class ChatRoomViewHolder(
        private val binding: ItemChatRoomBinding,
        private val onChatClick: (ChatRoom) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(chatRoom: ChatRoom) {
            binding.apply {
                // Загрузка аватара
                Glide.with(root.context)
                    .load(chatRoom.avatarUrl)
                    .placeholder(R.drawable.default_avatar)
                    .circleCrop()
                    .into(avatarImage)

                // Имя чата
                chatNameText.text = chatRoom.name

                // Переключение между индикатором набора и последним сообщением
                if (chatRoom.isTyping) {
                    typingIndicator.visibility = View.VISIBLE
                    lastMessageText.visibility = View.GONE
                } else {
                    typingIndicator.visibility = View.GONE
                    lastMessageText.visibility = View.VISIBLE
                    lastMessageText.text = chatRoom.lastMessage
                }

                // Форматирование времени (упрощённый пример)
                timestampText.text = formatTimestamp(chatRoom.lastMessageTime)

                // Индикатор онлайн
                onlineIndicator.visibility = if (chatRoom.isOnline) View.VISIBLE else View.GONE

                // Бейдж непрочитанных + визуальный акцент
                if (chatRoom.unreadCount > 0) {
                    unreadBadge.visibility = View.VISIBLE
                    unreadBadge.text = if (chatRoom.unreadCount > 99) "99+" else chatRoom.unreadCount.toString()
                    chatNameText.setTypeface(null, Typeface.BOLD)
                } else {
                    unreadBadge.visibility = View.GONE
                    chatNameText.setTypeface(null, Typeface.NORMAL)
                }

                // Индикатор закреплённого чата
                pinIndicator.visibility = if (chatRoom.isPinned) View.VISIBLE else View.GONE

                // Обработчик клика
                root.setOnClickListener { onChatClick(chatRoom) }
            }
        }

        fun bindPartial(chatRoom: ChatRoom, payloads: List<Any>) {
            binding.apply {
                payloads.forEach { payload ->
                    when (payload) {
                        ChatRoomDiffCallback.PAYLOAD_UNREAD_COUNT -> {
                            if (chatRoom.unreadCount > 0) {
                                unreadBadge.visibility = View.VISIBLE
                                unreadBadge.text = if (chatRoom.unreadCount > 99) "99+" else chatRoom.unreadCount.toString()
                                chatNameText.setTypeface(null, Typeface.BOLD)
                            } else {
                                unreadBadge.visibility = View.GONE
                                chatNameText.setTypeface(null, Typeface.NORMAL)
                            }
                        }
                        ChatRoomDiffCallback.PAYLOAD_TYPING -> {
                            if (chatRoom.isTyping) {
                                typingIndicator.visibility = View.VISIBLE
                                lastMessageText.visibility = View.GONE
                            } else {
                                typingIndicator.visibility = View.GONE
                                lastMessageText.visibility = View.VISIBLE
                                lastMessageText.text = chatRoom.lastMessage
                            }
                        }
                        ChatRoomDiffCallback.PAYLOAD_LAST_MESSAGE -> {
                            lastMessageText.text = chatRoom.lastMessage
                            timestampText.text = formatTimestamp(chatRoom.lastMessageTime)
                        }
                    }
                }
            }
        }

        private fun formatTimestamp(timestamp: Long): String {
            val now = System.currentTimeMillis()
            val diff = now - timestamp

            return when {
                diff < 60_000 -> "Just now"
                diff < 3_600_000 -> "${diff / 60_000}m"
                diff < 86_400_000 -> SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(timestamp))
                diff < 604_800_000 -> SimpleDateFormat("EEE", Locale.getDefault()).format(Date(timestamp))
                else -> SimpleDateFormat("dd/MM/yy", Locale.getDefault()).format(Date(timestamp))
            }
        }
    }

    class ChatRoomDiffCallback : DiffUtil.ItemCallback<ChatRoom>() {
        override fun areItemsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
            return oldItem == newItem
        }

        // Поддержка payload для частичных обновлений (unread, typing, lastMessage).
        // В данном упрощённом примере возвращается один тип payload за раз.
        // В продакшне можно вернуть коллекцию payload'ов, если изменилось несколько полей.
        override fun getChangePayload(oldItem: ChatRoom, newItem: ChatRoom): Any? {
            return when {
                oldItem.unreadCount != newItem.unreadCount -> PAYLOAD_UNREAD_COUNT
                oldItem.isTyping != newItem.isTyping -> PAYLOAD_TYPING
                oldItem.lastMessage != newItem.lastMessage ||
                    oldItem.lastMessageTime != newItem.lastMessageTime -> PAYLOAD_LAST_MESSAGE
                else -> null
            }
        }

        companion object {
            const val PAYLOAD_UNREAD_COUNT = "unread_count"
            const val PAYLOAD_TYPING = "typing"
            const val PAYLOAD_LAST_MESSAGE = "last_message"
        }
    }
}
```

### 4. Настройка RecyclerView

```kotlin
class ChatListFragment : Fragment() {

    private lateinit var binding: FragmentChatListBinding
    private val adapter by lazy {
        ChatRoomAdapter { chatRoom ->
            // Навигация к экрану деталей чата
            findNavController().navigate(
                ChatListFragmentDirections.actionChatListToDetail(chatRoom.id)
            )
        }
    }

    private val viewModel: ChatListViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentChatListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.chatRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = this@ChatListFragment.adapter

            // Необязательно: разделители между элементами
            addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))

            // Подсказки для производительности (подходят, если размеры элементов стабильны)
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
        }

        // Подписка на список чатов
        viewModel.chatRooms.observe(viewLifecycleOwner) { chatRooms ->
            // Убедитесь, что chats отсортированы по isPinned и lastMessageTime до передачи в адаптер
            adapter.submitList(chatRooms)
        }
    }
}
```

### 5. Оптимизация Производительности

#### Использование DiffUtil

Используйте `ListAdapter`/`DiffUtil` для эффективных обновлений, опираясь на стабильные `id` и корректное сравнение содержимого. При использовании payload для частичных обновлений реализуйте соответствующий вариант `onBindViewHolder` с `payloads`, чтобы эти payload были обработаны. Для более точного контроля можно включить `setHasStableIds(true)` и переопределить `getItemId`, но это опционально.

#### Пагинация (пример)

```kotlin
class ChatListViewModel : ViewModel() {
    private val _chatRooms = MutableLiveData<List<ChatRoom>>()
    val chatRooms: LiveData<List<ChatRoom>> = _chatRooms

    private var currentPage: Int = 0
    private var isLoading: Boolean = false

    fun loadChats(pageSize: Int = 20) {
        if (isLoading) return
        isLoading = true

        viewModelScope.launch {
            val newChats = repository.getChats(page = currentPage, pageSize = pageSize)
            val current = _chatRooms.value.orEmpty()
            _chatRooms.value = current + newChats
            if (newChats.isNotEmpty()) currentPage++
            isLoading = false
        }
    }
}
```

### Лучшие Практики

1. Использовать `RecyclerView` для эффективного скролла списка чатов.
2. Применять библиотеку загрузки изображений (`Glide`/`Coil`) с кешированием и плейсхолдерами.
3. Использовать `DiffUtil` или `ListAdapter` для обновления изменившихся элементов без полного пересоздания списка.
4. Реализовать пагинацию или ленивую подгрузку для больших списков.
5. Чётко отображать индикаторы typing/online и бейджи непрочитанных с понятной визуальной иерархией.
6. Сортировать чаты по закреплению и времени последнего сообщения (сначала `isPinned`, затем по `lastMessageTime`).
7. Использовать `ViewBinding` или data binding для безопасного доступа к вью.
8. Реализовать свайп-действия (`ItemTouchHelper`) для удаления/архивации/мута, где это уместно.
9. Отдельно проектировать макеты списка чатов и пузырьков сообщений для экрана деталей чата, используя общие принципы моделей данных, но не смешивая ответственности.

Такой подход соответствует рекомендациям по работе с списками в Android и покрывает как визуальную часть (UI-паттерн списка чатов), так и реалистичную реализацию.

---

## Answer (EN)
Creating chat lists from a UI perspective requires considering usability, clarity, performance, and scalability for large/active chat sets. The focus is on how to visually structure and render a list of conversations and how that maps to efficient Android implementation.

### Main Steps

1. Define a data model for chat list items (chat/conversation).
2. Create a layout for each chat row (avatar, name, last message, timestamp, online/typing indicators, unread badge, pin).
3. Implement RecyclerView + Adapter + ViewHolder for that model.
4. Wire up data observation (`ViewModel`/`LiveData`/`Flow`) and submit updates via `ListAdapter`/`DiffUtil`.
5. Ensure proper sorting (pinned first, then by last message time).
6. Optimize for performance (DiffUtil, pagination, image caching).

### 1. Define Data Models

Keep a clear separation between the chat list model and message models: the list works with a "chat/conversation" entity, while message bubbles belong to the chat detail screen. Message models below are included as context to illustrate a consistent UI/data approach; they are not required to implement the list itself.

```kotlin
// Chat room model for the chat list
data class ChatRoom(
    val id: String,
    val name: String,
    val avatarUrl: String?,
    val lastMessage: String,
    val lastMessageTime: Long,
    val unreadCount: Int,
    val isOnline: Boolean,
    val isTyping: Boolean = false,
    val isPinned: Boolean = false
)

// Message models for the chat detail screen (context for UI; not required for the list screen itself)
sealed class ChatMessage {
    abstract val id: String
    abstract val timestamp: Long
    abstract val senderId: String

    data class TextMessage(
        override val id: String,
        override val timestamp: Long,
        override val senderId: String,
        val text: String,
        val status: MessageStatus
    ) : ChatMessage()

    data class ImageMessage(
        override val id: String,
        override val timestamp: Long,
        override val senderId: String,
        val imageUrl: String,
        val caption: String?,
        val status: MessageStatus
    ) : ChatMessage()

    data class DateSeparator(
        override val id: String,
        override val timestamp: Long,
        val date: String
    ) : ChatMessage() {
        override val senderId: String = ""
    }
}

enum class MessageStatus {
    SENDING, SENT, DELIVERED, READ, FAILED
}
```

### 2. Create Item Layouts

#### Chat Room Item Layout

```xml
<!-- item_chat_room.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="?attr/selectableItemBackground"
    android:padding="16dp">

    <!-- Avatar with online indicator -->
    <FrameLayout
        android:id="@+id/avatarContainer"
        android:layout_width="56dp"
        android:layout_height="56dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent">

        <com.google.android.material.imageview.ShapeableImageView
            android:id="@+id/avatarImage"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:scaleType="centerCrop"
            app:shapeAppearanceOverlay="@style/CircleImageView"
            tools:src="@tools:sample/avatars" />

        <View
            android:id="@+id/onlineIndicator"
            android:layout_width="12dp"
            android:layout_height="12dp"
            android:layout_gravity="bottom|end"
            android:layout_margin="2dp"
            android:background="@drawable/online_indicator"
            android:visibility="gone" />
    </FrameLayout>

    <!-- Chat name -->
    <TextView
        android:id="@+id/chatNameText"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:layout_marginEnd="8dp"
        android:ellipsize="end"
        android:maxLines="1"
        android:textColor="?android:textColorPrimary"
        android:textSize="16sp"
        android:textStyle="bold"
        app:layout_constraintEnd_toStartOf="@id/timestampText"
        app:layout_constraintStart_toEndOf="@id/avatarContainer"
        app:layout_constraintTop_toTopOf="@id/avatarContainer"
        tools:text="John Doe" />

    <!-- Last message -->
    <TextView
        android:id="@+id/lastMessageText"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        android:layout_marginEnd="8dp"
        android:ellipsize="end"
        android:maxLines="2"
        android:textColor="?android:textColorSecondary"
        android:textSize="14sp"
        app:layout_constraintEnd_toStartOf="@id/unreadBadge"
        app:layout_constraintStart_toStartOf="@id/chatNameText"
        app:layout_constraintTop_toBottomOf="@id/chatNameText"
        tools:text="Hey, how are you doing?" />

    <!-- Typing indicator (mutually exclusive with last message) -->
    <TextView
        android:id="@+id/typingIndicator"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
        android:text="typing..."
        android:textColor="@color/primary"
        android:textSize="14sp"
        android:textStyle="italic"
        android:visibility="gone"
        app:layout_constraintEnd_toEndOf="@id/lastMessageText"
        app:layout_constraintStart_toStartOf="@id/chatNameText"
        app:layout_constraintTop_toBottomOf="@id/chatNameText" />

    <!-- Timestamp -->
    <TextView
        android:id="@+id/timestampText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:textColor="?android:textColorSecondary"
        android:textSize="12sp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="@id/chatNameText"
        tools:text="12:34 PM" />

    <!-- Unread badge -->
    <TextView
        android:id="@+id/unreadBadge"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:minWidth="24dp"
        android:minHeight="24dp"
        android:paddingHorizontal="6dp"
        android:gravity="center"
        android:background="@drawable/unread_badge_background"
        android:textColor="@android:color/white"
        android:textSize="12sp"
        android:visibility="gone"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@id/timestampText"
        tools:text="3"
        tools:visibility="visible" />

    <!-- Pin indicator -->
    <ImageView
        android:id="@+id/pinIndicator"
        android:layout_width="16dp"
        android:layout_height="16dp"
        android:layout_marginEnd="4dp"
        android:src="@drawable/ic_pin"
        android:tint="?android:textColorSecondary"
        android:visibility="gone"
        app:layout_constraintBottom_toBottomOf="@id/timestampText"
        app:layout_constraintEnd_toStartOf="@id/timestampText"
        app:layout_constraintTop_toTopOf="@id/timestampText" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

#### Message Item Layouts (for Detail Screen, context)

```xml
<!-- item_message_sent.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="8dp">

    <com.google.android.material.card.MaterialCardView
        android:id="@+id/messageCard"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="64dp"
        app:cardBackgroundColor="@color/message_sent_background"
        app:cardCornerRadius="12dp"
        app:cardElevation="1dp"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintWidth_max="280dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="12dp">

            <TextView
                android:id="@+id/messageText"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:textColor="@android:color/white"
                android:textSize="16sp" />

            <LinearLayout
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_gravity="end"
                android:layout_marginTop="4dp"
                android:gravity="center_vertical"
                android:orientation="horizontal">

                <TextView
                    android:id="@+id/messageTime"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:textColor="@color/message_time_color"
                    android:textSize="12sp" />

                <ImageView
                    android:id="@+id/messageStatus"
                    android:layout_width="16dp"
                    android:layout_height="16dp"
                    android:layout_marginStart="4dp"
                    android:src="@drawable/ic_check_double"
                    android:tint="@color/message_read_color" />
            </LinearLayout>
        </LinearLayout>
    </com.google.android.material.card.MaterialCardView>

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 3. Create Adapter with ViewHolders

```kotlin
class ChatRoomAdapter(
    private val onChatClick: (ChatRoom) -> Unit
) : ListAdapter<ChatRoom, ChatRoomAdapter.ChatRoomViewHolder>(ChatRoomDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ChatRoomViewHolder {
        val binding = ItemChatRoomBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ChatRoomViewHolder(binding, onChatClick)
    }

    override fun onBindViewHolder(holder: ChatRoomViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // If you use payloads from getChangePayload, also override this variant:
    override fun onBindViewHolder(
        holder: ChatRoomViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            holder.bindPartial(getItem(position), payloads)
        }
    }

    class ChatRoomViewHolder(
        private val binding: ItemChatRoomBinding,
        private val onChatClick: (ChatRoom) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(chatRoom: ChatRoom) {
            binding.apply {
                // Load avatar
                Glide.with(root.context)
                    .load(chatRoom.avatarUrl)
                    .placeholder(R.drawable.default_avatar)
                    .circleCrop()
                    .into(avatarImage)

                // Set chat name
                chatNameText.text = chatRoom.name

                // Show/hide typing indicator vs last message
                if (chatRoom.isTyping) {
                    typingIndicator.visibility = View.VISIBLE
                    lastMessageText.visibility = View.GONE
                } else {
                    typingIndicator.visibility = View.GONE
                    lastMessageText.visibility = View.VISIBLE
                    lastMessageText.text = chatRoom.lastMessage
                }

                // Format timestamp (simplified human-friendly example)
                timestampText.text = formatTimestamp(chatRoom.lastMessageTime)

                // Show/hide online indicator
                onlineIndicator.visibility = if (chatRoom.isOnline) View.VISIBLE else View.GONE

                // Show/hide unread badge and emphasize unread chats
                if (chatRoom.unreadCount > 0) {
                    unreadBadge.visibility = View.VISIBLE
                    unreadBadge.text = if (chatRoom.unreadCount > 99) "99+" else chatRoom.unreadCount.toString()
                    chatNameText.setTypeface(null, Typeface.BOLD)
                } else {
                    unreadBadge.visibility = View.GONE
                    chatNameText.setTypeface(null, Typeface.NORMAL)
                }

                // Show/hide pin indicator
                pinIndicator.visibility = if (chatRoom.isPinned) View.VISIBLE else View.GONE

                // Click listener
                root.setOnClickListener { onChatClick(chatRoom) }
            }
        }

        fun bindPartial(chatRoom: ChatRoom, payloads: List<Any>) {
            binding.apply {
                payloads.forEach { payload ->
                    when (payload) {
                        ChatRoomDiffCallback.PAYLOAD_UNREAD_COUNT -> {
                            if (chatRoom.unreadCount > 0) {
                                unreadBadge.visibility = View.VISIBLE
                                unreadBadge.text = if (chatRoom.unreadCount > 99) "99+" else chatRoom.unreadCount.toString()
                                chatNameText.setTypeface(null, Typeface.BOLD)
                            } else {
                                unreadBadge.visibility = View.GONE
                                chatNameText.setTypeface(null, Typeface.NORMAL)
                            }
                        }
                        ChatRoomDiffCallback.PAYLOAD_TYPING -> {
                            if (chatRoom.isTyping) {
                                typingIndicator.visibility = View.VISIBLE
                                lastMessageText.visibility = View.GONE
                            } else {
                                typingIndicator.visibility = View.GONE
                                lastMessageText.visibility = View.VISIBLE
                                lastMessageText.text = chatRoom.lastMessage
                            }
                        }
                        ChatRoomDiffCallback.PAYLOAD_LAST_MESSAGE -> {
                            lastMessageText.text = chatRoom.lastMessage
                            timestampText.text = formatTimestamp(chatRoom.lastMessageTime)
                        }
                    }
                }
            }
        }

        private fun formatTimestamp(timestamp: Long): String {
            val now = System.currentTimeMillis()
            val diff = now - timestamp

            return when {
                diff < 60_000 -> "Just now"
                diff < 3_600_000 -> "${diff / 60_000}m"
                diff < 86_400_000 -> SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(timestamp))
                diff < 604_800_000 -> SimpleDateFormat("EEE", Locale.getDefault()).format(Date(timestamp))
                else -> SimpleDateFormat("dd/MM/yy", Locale.getDefault()).format(Date(timestamp))
            }
        }
    }

    class ChatRoomDiffCallback : DiffUtil.ItemCallback<ChatRoom>() {
        override fun areItemsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
            return oldItem == newItem
        }

        // Payload support for partial updates (unread, typing, lastMessage).
        // This simplified example returns a single payload at a time.
        // In production you may return a collection if multiple properties changed.
        override fun getChangePayload(oldItem: ChatRoom, newItem: ChatRoom): Any? {
            return when {
                oldItem.unreadCount != newItem.unreadCount -> PAYLOAD_UNREAD_COUNT
                oldItem.isTyping != newItem.isTyping -> PAYLOAD_TYPING
                oldItem.lastMessage != newItem.lastMessage ||
                    oldItem.lastMessageTime != newItem.lastMessageTime -> PAYLOAD_LAST_MESSAGE
                else -> null
            }
        }

        companion object {
            const val PAYLOAD_UNREAD_COUNT = "unread_count"
            const val PAYLOAD_TYPING = "typing"
            const val PAYLOAD_LAST_MESSAGE = "last_message"
        }
    }
}
```

### 4. Configure RecyclerView

```kotlin
class ChatListFragment : Fragment() {

    private lateinit var binding: FragmentChatListBinding
    private val adapter by lazy {
        ChatRoomAdapter { chatRoom ->
            // Navigate to chat detail
            findNavController().navigate(
                ChatListFragmentDirections.actionChatListToDetail(chatRoom.id)
            )
        }
    }

    private val viewModel: ChatListViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentChatListBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.chatRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = this@ChatListFragment.adapter

            // Optional: item decoration for dividers
            addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))

            // Basic performance hints (appropriate if item size is relatively stable)
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
        }

        // Observe chat list
        viewModel.chatRooms.observe(viewLifecycleOwner) { chatRooms ->
            // Ensure chats are sorted (pinned first, then by lastMessageTime) before submission
            adapter.submitList(chatRooms)
        }
    }
}
```

### 5. Performance Optimization

#### Use DiffUtil for Efficient Updates

Use `ListAdapter`/`DiffUtil` for efficient updates based on stable chat identifiers and correct content equality. If you leverage payloads, implement the `onBindViewHolder` overload with `payloads` so that partial updates are applied. Optionally, for stricter control, you may enable `setHasStableIds(true)` and override `getItemId`, but it is not mandatory.

#### Implement Pagination (Conceptual Example)

```kotlin
class ChatListViewModel : ViewModel() {
    private val _chatRooms = MutableLiveData<List<ChatRoom>>()
    val chatRooms: LiveData<List<ChatRoom>> = _chatRooms

    private var currentPage: Int = 0
    private var isLoading: Boolean = false

    fun loadChats(pageSize: Int = 20) {
        if (isLoading) return
        isLoading = true

        viewModelScope.launch {
            val newChats = repository.getChats(page = currentPage, pageSize = pageSize)
            val current = _chatRooms.value.orEmpty()
            _chatRooms.value = current + newChats
            if (newChats.isNotEmpty()) currentPage++
            isLoading = false
        }
    }
}
```

### Best Practices

1. Use RecyclerView for efficient scrolling of chat rows.
2. Use an image loading library (Glide/Coil) with caching and placeholders.
3. Use DiffUtil (or ListAdapter) for efficient updates when chats change.
4. Implement pagination or incremental loading for large numbers of chats.
5. Handle typing/online indicators and unread badges with clear visual hierarchy.
6. Sort chats by pinned status and last message time (pinned first, then by `lastMessageTime`).
7. Use ViewBinding or data binding for safer view access.
8. Implement swipe actions (delete/archive/mute) with ItemTouchHelper where appropriate.
9. Keep chat list item layouts separate from message bubble layouts used on the chat detail screen; they share data principles but serve different purposes.

---

## Дополнительные Вопросы (RU)

- [[q-network-error-handling-strategies--networking--medium]]
- [[q-what-are-px-dp-sp--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]

## Follow-ups

- [[q-network-error-handling-strategies--networking--medium]]
- [[q-what-are-px-dp-sp--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]


## Ссылки (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Связанные Вопросы (RU)

### Предпосылки / Концепты

- [[c-recyclerview]]

### Предпосылки (проще)

- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui

## Related Questions

### Prerequisites / Concepts

- [[c-recyclerview]]

### Prerequisites (Easier)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
