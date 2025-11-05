---
id: android-219
title: "How To Create Chat Lists From A UI Perspective / Как создать списки чатов с точки зрения UI"
aliases: [How To Create Chat Lists From A UI Perspective, Как создать списки чатов с точки зрения UI]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-network-error-handling-strategies--networking--medium, q-what-are-px-dp-sp--android--easy, q-what-is-known-about-recyclerview--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/hard, recyclerview]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Как Делать Списки Чатов С Точки Зрения UI?

**English**: How to create chat lists from a UI perspective?

## Answer (EN)
Creating chat lists from a UI perspective requires considering multiple aspects to ensure usability, good performance, and attractive appearance.

### Main Steps

1. **Define data models**
2. **Create layouts for list items**
3. **Create adapter for RecyclerView**
4. **Configure RecyclerView and data management**
5. **Optimize performance**

### 1. Define Data Models

For chat applications, define two main types of items: chat rooms and messages.

```kotlin
// Chat room model
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

// Message model for chat detail view
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

    <!-- Typing indicator -->
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
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_marginTop="4dp"
        android:background="@drawable/unread_badge_background"
        android:gravity="center"
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

#### Message Item Layouts

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

                // Show/hide typing indicator
                if (chatRoom.isTyping) {
                    typingIndicator.visibility = View.VISIBLE
                    lastMessageText.visibility = View.GONE
                } else {
                    typingIndicator.visibility = View.GONE
                    lastMessageText.visibility = View.VISIBLE
                    lastMessageText.text = chatRoom.lastMessage
                }

                // Format timestamp
                timestampText.text = formatTimestamp(chatRoom.lastMessageTime)

                // Show/hide online indicator
                onlineIndicator.visibility = if (chatRoom.isOnline) View.VISIBLE else View.GONE

                // Show/hide unread badge
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

        private fun formatTimestamp(timestamp: Long): String {
            val now = System.currentTimeMillis()
            val diff = now - timestamp

            return when {
                diff < 60_000 -> "Just now"
                diff < 3600_000 -> "${diff / 60_000}m"
                diff < 86400_000 -> SimpleDateFormat("HH:mm", Locale.getDefault()).format(Date(timestamp))
                diff < 604800_000 -> SimpleDateFormat("EEE", Locale.getDefault()).format(Date(timestamp))
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

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.chatRecyclerView.apply {
            layoutManager = LinearLayoutManager(context)
            adapter = this@ChatListFragment.adapter

            // Add item decoration for dividers
            addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))

            // Optimize performance
            setHasFixedSize(true)
            itemAnimator = DefaultItemAnimator()
        }

        // Observe chat list
        viewModel.chatRooms.observe(viewLifecycleOwner) { chatRooms ->
            adapter.submitList(chatRooms)
        }
    }
}
```

### 5. Performance Optimization

#### Use DiffUtil for Efficient Updates

```kotlin
class ChatRoomDiffCallback : DiffUtil.ItemCallback<ChatRoom>() {
    override fun areItemsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: ChatRoom, newItem: ChatRoom): Boolean {
        return oldItem == newItem
    }

    override fun getChangePayload(oldItem: ChatRoom, newItem: ChatRoom): Any? {
        return when {
            oldItem.unreadCount != newItem.unreadCount -> PAYLOAD_UNREAD_COUNT
            oldItem.isTyping != newItem.isTyping -> PAYLOAD_TYPING
            oldItem.lastMessage != newItem.lastMessage -> PAYLOAD_LAST_MESSAGE
            else -> null
        }
    }

    companion object {
        const val PAYLOAD_UNREAD_COUNT = "unread_count"
        const val PAYLOAD_TYPING = "typing"
        const val PAYLOAD_LAST_MESSAGE = "last_message"
    }
}
```

#### Implement Pagination

```kotlin
class ChatListViewModel : ViewModel() {
    private val _chatRooms = MutableLiveData<List<ChatRoom>>()
    val chatRooms: LiveData<List<ChatRoom>> = _chatRooms

    fun loadChats(page: Int = 0, pageSize: Int = 20) {
        viewModelScope.launch {
            val chats = repository.getChats(page, pageSize)
            _chatRooms.value = chats
        }
    }
}
```

### Best Practices

1. **Use RecyclerView** with adapter for efficient scrolling
2. **Optimize images** with Glide or Coil
3. **Use DiffUtil** for smart list updates
4. **Implement pagination** for large chat lists
5. **Handle typing indicators** in real-time
6. **Sort chats** by pinned status and last message time
7. **Use ViewBinding** for type-safe view access
8. **Implement swipe actions** for delete/archive

## Ответ (RU)
Создание списков чатов с точки зрения UI требует учёта множества аспектов, чтобы обеспечить удобство использования, хорошую производительность и красивый внешний вид. Основные шаги: определение данных, создание макетов для элементов списка, создание адаптера для RecyclerView, настройка RecyclerView и управление данными, оптимизация производительности. Для чата можно определить два типа элементов: чат-комнаты и сообщения. Важно использовать RecyclerView с адаптером для отображения элементов списка и оптимизировать производительность с помощью DiffUtil и пагинации.


---


## Follow-ups

- [[q-network-error-handling-strategies--networking--medium]]
- [[q-what-are-px-dp-sp--android--easy]]
- [[q-what-is-known-about-recyclerview--android--easy]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Prerequisites (Easier)
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- q-rxjava-pagination-recyclerview--android--medium - Ui
