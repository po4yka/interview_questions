---
tags:
  - recyclerview
  - adapter
  - view-types
  - design-patterns
difficulty: medium
status: draft
---

# RecyclerView ViewTypes and Delegation

# Question (EN)
> How do you handle multiple view types in RecyclerView? Explain view type patterns, implementing adapter delegation, sealed classes for view types, and performance considerations for heterogeneous lists.

# Вопрос (RU)
> Как обрабатывать множественные типы view в RecyclerView? Объясните паттерны типов view, реализацию делегирования адаптера, sealed классы для типов view и соображения производительности для гетерогенных списков.

---

## Answer (EN)

**Multiple view types** in RecyclerView allow displaying different layouts in the same list (e.g., headers, items, footers, ads). Proper implementation is crucial for maintainable, performant heterogeneous lists.

### Basic Multiple View Types

```kotlin
data class User(val id: Long, val name: String)
data class Header(val title: String)

class BasicMultiTypeAdapter(
    private val items: List<Any>
) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_HEADER = 0
        private const val TYPE_USER = 1
    }

    // 1. Determine view type for position
    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is Header -> TYPE_HEADER
            is User -> TYPE_USER
            else -> throw IllegalArgumentException("Unknown type")
        }
    }

    // 2. Create appropriate ViewHolder based on type
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_header, parent, false)
                HeaderViewHolder(view)
            }
            TYPE_USER -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(R.layout.item_user, parent, false)
                UserViewHolder(view)
            }
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }

    // 3. Bind data based on type
    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is HeaderViewHolder -> {
                val header = items[position] as Header
                holder.bind(header)
            }
            is UserViewHolder -> {
                val user = items[position] as User
                holder.bind(user)
            }
        }
    }

    override fun getItemCount(): Int = items.size

    // ViewHolders
    class HeaderViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val titleView: TextView = view.findViewById(R.id.title)

        fun bind(header: Header) {
            titleView.text = header.title
        }
    }

    class UserViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        private val nameView: TextView = view.findViewById(R.id.name)

        fun bind(user: User) {
            nameView.text = user.name
        }
    }
}
```

---

### Sealed Classes for Type Safety

**Better approach using sealed classes:**

```kotlin
sealed class ListItem {
    abstract val id: String

    data class HeaderItem(
        override val id: String,
        val title: String
    ) : ListItem()

    data class UserItem(
        override val id: String,
        val name: String,
        val email: String,
        val avatarUrl: String
    ) : ListItem()

    data class AdItem(
        override val id: String,
        val imageUrl: String,
        val targetUrl: String
    ) : ListItem()

    data class LoadingItem(
        override val id: String = "loading"
    ) : ListItem()
}

class SealedClassAdapter : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {

    companion object {
        private const val TYPE_HEADER = 0
        private const val TYPE_USER = 1
        private const val TYPE_AD = 2
        private const val TYPE_LOADING = 3
    }

    override fun getItemViewType(position: Int): Int {
        return when (getItem(position)) {
            is ListItem.HeaderItem -> TYPE_HEADER
            is ListItem.UserItem -> TYPE_USER
            is ListItem.AdItem -> TYPE_AD
            is ListItem.LoadingItem -> TYPE_LOADING
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> HeaderViewHolder.create(parent)
            TYPE_USER -> UserViewHolder.create(parent)
            TYPE_AD -> AdViewHolder.create(parent)
            TYPE_LOADING -> LoadingViewHolder.create(parent)
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = getItem(position)) {
            is ListItem.HeaderItem -> (holder as HeaderViewHolder).bind(item)
            is ListItem.UserItem -> (holder as UserViewHolder).bind(item)
            is ListItem.AdItem -> (holder as AdViewHolder).bind(item)
            is ListItem.LoadingItem -> (holder as LoadingViewHolder).bind(item)
        }
    }

    // ViewHolders with factory methods
    class HeaderViewHolder private constructor(
        private val binding: ItemHeaderBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ListItem.HeaderItem) {
            binding.title.text = item.title
        }

        companion object {
            fun create(parent: ViewGroup): HeaderViewHolder {
                val binding = ItemHeaderBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return HeaderViewHolder(binding)
            }
        }
    }

    class UserViewHolder private constructor(
        private val binding: ItemUserBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ListItem.UserItem) {
            binding.name.text = item.name
            binding.email.text = item.email

            Glide.with(binding.root)
                .load(item.avatarUrl)
                .circleCrop()
                .into(binding.avatar)
        }

        companion object {
            fun create(parent: ViewGroup): UserViewHolder {
                val binding = ItemUserBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return UserViewHolder(binding)
            }
        }
    }

    // ... other ViewHolders

    class DiffCallback : DiffUtil.ItemCallback<ListItem>() {
        override fun areItemsTheSame(oldItem: ListItem, newItem: ListItem): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ListItem, newItem: ListItem): Boolean {
            return oldItem == newItem
        }
    }
}
```

---

### Adapter Delegation Pattern

**Delegate each view type to separate class for better separation of concerns.**

```kotlin
// Base interface
interface AdapterDelegate {
    fun isForViewType(item: ListItem): Boolean
    fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
    fun onBindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem)
}

// Header delegate
class HeaderDelegate : AdapterDelegate {
    override fun isForViewType(item: ListItem): Boolean {
        return item is ListItem.HeaderItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val binding = ItemHeaderBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem) {
        (holder as ViewHolder).bind(item as ListItem.HeaderItem)
    }

    private class ViewHolder(
        private val binding: ItemHeaderBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ListItem.HeaderItem) {
            binding.title.text = item.title
        }
    }
}

// User delegate
class UserDelegate(
    private val onUserClick: (ListItem.UserItem) -> Unit
) : AdapterDelegate {

    override fun isForViewType(item: ListItem): Boolean {
        return item is ListItem.UserItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding, onUserClick)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem) {
        (holder as ViewHolder).bind(item as ListItem.UserItem)
    }

    private class ViewHolder(
        private val binding: ItemUserBinding,
        private val onUserClick: (ListItem.UserItem) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ListItem.UserItem) {
            binding.name.text = item.name
            binding.email.text = item.email

            Glide.with(binding.root)
                .load(item.avatarUrl)
                .into(binding.avatar)

            binding.root.setOnClickListener {
                onUserClick(item)
            }
        }
    }
}

// Delegating adapter
class DelegatingAdapter(
    private val onUserClick: (ListItem.UserItem) -> Unit
) : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {

    private val delegates: List<AdapterDelegate> = listOf(
        HeaderDelegate(),
        UserDelegate(onUserClick),
        AdDelegate(),
        LoadingDelegate()
    )

    override fun getItemViewType(position: Int): Int {
        val item = getItem(position)

        // Find delegate index
        return delegates.indexOfFirst { it.isForViewType(item) }
            .also { if (it == -1) throw IllegalArgumentException("No delegate for $item") }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return delegates[viewType].onCreateViewHolder(parent)
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item = getItem(position)
        val viewType = getItemViewType(position)
        delegates[viewType].onBindViewHolder(holder, item)
    }

    class DiffCallback : DiffUtil.ItemCallback<ListItem>() {
        override fun areItemsTheSame(oldItem: ListItem, newItem: ListItem) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: ListItem, newItem: ListItem) =
            oldItem == newItem
    }
}
```

**Benefits:**
- Each delegate handles one view type
- Easy to add new types
- Better testability
- Clear separation of concerns

---

### Using Library: Hannes Dorfmann's AdapterDelegates

```gradle
implementation 'com.hannesdorfmann:adapterdelegates4:4.3.2'
```

```kotlin
class HeaderAdapterDelegate : AdapterDelegate<List<ListItem>>() {

    override fun isForViewType(items: List<ListItem>, position: Int): Boolean {
        return items[position] is ListItem.HeaderItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val binding = ItemHeaderBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(
        items: List<ListItem>,
        position: Int,
        holder: RecyclerView.ViewHolder,
        payloads: List<Any>
    ) {
        val item = items[position] as ListItem.HeaderItem
        (holder as ViewHolder).bind(item)
    }

    private class ViewHolder(
        private val binding: ItemHeaderBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: ListItem.HeaderItem) {
            binding.title.text = item.title
        }
    }
}

// Adapter using delegates
class MyAdapter : ListDelegationAdapter<List<ListItem>>() {
    init {
        delegatesManager
            .addDelegate(HeaderAdapterDelegate())
            .addDelegate(UserAdapterDelegate())
            .addDelegate(AdAdapterDelegate())
    }
}
```

---

### Real-World Example: Social Feed

```kotlin
sealed class FeedItem {
    abstract val id: String

    data class Post(
        override val id: String,
        val authorName: String,
        val authorAvatar: String,
        val content: String,
        val imageUrl: String?,
        val likeCount: Int,
        val isLiked: Boolean,
        val timestamp: Long
    ) : FeedItem()

    data class Story(
        override val id: String,
        val stories: List<StoryPreview>
    ) : FeedItem()

    data class Suggestion(
        override val id: String,
        val suggestedUsers: List<UserSuggestion>
    ) : FeedItem()

    data class Ad(
        override val id: String,
        val imageUrl: String,
        val title: String,
        val cta: String
    ) : FeedItem()

    data class LoadMore(
        override val id: String = "load_more"
    ) : FeedItem()
}

class FeedAdapter(
    private val onPostLike: (FeedItem.Post) -> Unit,
    private val onPostClick: (FeedItem.Post) -> Unit,
    private val onStoryClick: (String) -> Unit,
    private val onUserSuggestionClick: (String) -> Unit,
    private val onLoadMore: () -> Unit
) : ListAdapter<FeedItem, RecyclerView.ViewHolder>(DiffCallback()) {

    companion object {
        private const val TYPE_POST = 0
        private const val TYPE_STORY = 1
        private const val TYPE_SUGGESTION = 2
        private const val TYPE_AD = 3
        private const val TYPE_LOAD_MORE = 4
    }

    override fun getItemViewType(position: Int) = when (getItem(position)) {
        is FeedItem.Post -> TYPE_POST
        is FeedItem.Story -> TYPE_STORY
        is FeedItem.Suggestion -> TYPE_SUGGESTION
        is FeedItem.Ad -> TYPE_AD
        is FeedItem.LoadMore -> TYPE_LOAD_MORE
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        TYPE_POST -> PostViewHolder.create(parent, onPostLike, onPostClick)
        TYPE_STORY -> StoryViewHolder.create(parent, onStoryClick)
        TYPE_SUGGESTION -> SuggestionViewHolder.create(parent, onUserSuggestionClick)
        TYPE_AD -> AdViewHolder.create(parent)
        TYPE_LOAD_MORE -> LoadMoreViewHolder.create(parent, onLoadMore)
        else -> throw IllegalArgumentException("Unknown viewType")
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = getItem(position)) {
            is FeedItem.Post -> (holder as PostViewHolder).bind(item)
            is FeedItem.Story -> (holder as StoryViewHolder).bind(item)
            is FeedItem.Suggestion -> (holder as SuggestionViewHolder).bind(item)
            is FeedItem.Ad -> (holder as AdViewHolder).bind(item)
            is FeedItem.LoadMore -> (holder as LoadMoreViewHolder).bind()
        }
    }

    // Post ViewHolder
    class PostViewHolder private constructor(
        private val binding: ItemPostBinding,
        private val onLike: (FeedItem.Post) -> Unit,
        private val onClick: (FeedItem.Post) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        private var currentPost: FeedItem.Post? = null

        init {
            binding.likeButton.setOnClickListener {
                currentPost?.let { onLike(it) }
            }
            binding.root.setOnClickListener {
                currentPost?.let { onClick(it) }
            }
        }

        fun bind(post: FeedItem.Post) {
            currentPost = post

            binding.authorName.text = post.authorName
            binding.content.text = post.content
            binding.likeCount.text = post.likeCount.toString()

            binding.likeButton.setImageResource(
                if (post.isLiked) R.drawable.ic_liked else R.drawable.ic_like
            )

            Glide.with(binding.root)
                .load(post.authorAvatar)
                .circleCrop()
                .into(binding.authorAvatar)

            post.imageUrl?.let { url ->
                binding.postImage.isVisible = true
                Glide.with(binding.root)
                    .load(url)
                    .into(binding.postImage)
            } ?: run {
                binding.postImage.isVisible = false
            }
        }

        companion object {
            fun create(
                parent: ViewGroup,
                onLike: (FeedItem.Post) -> Unit,
                onClick: (FeedItem.Post) -> Unit
            ): PostViewHolder {
                val binding = ItemPostBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return PostViewHolder(binding, onLike, onClick)
            }
        }
    }

    // Story ViewHolder (horizontal RecyclerView)
    class StoryViewHolder private constructor(
        private val binding: ItemStoryBinding,
        private val onStoryClick: (String) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        private val storyAdapter = StoryPreviewAdapter(onStoryClick)

        init {
            binding.storyRecyclerView.apply {
                layoutManager = LinearLayoutManager(
                    context,
                    LinearLayoutManager.HORIZONTAL,
                    false
                )
                adapter = storyAdapter
            }
        }

        fun bind(item: FeedItem.Story) {
            storyAdapter.submitList(item.stories)
        }

        companion object {
            fun create(
                parent: ViewGroup,
                onStoryClick: (String) -> Unit
            ): StoryViewHolder {
                val binding = ItemStoryBinding.inflate(
                    LayoutInflater.from(parent.context),
                    parent,
                    false
                )
                return StoryViewHolder(binding, onStoryClick)
            }
        }
    }

    // ... other ViewHolders

    class DiffCallback : DiffUtil.ItemCallback<FeedItem>() {
        override fun areItemsTheSame(oldItem: FeedItem, newItem: FeedItem) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: FeedItem, newItem: FeedItem) =
            oldItem == newItem

        override fun getChangePayload(oldItem: FeedItem, newItem: FeedItem): Any? {
            // Handle partial updates for posts (like count, etc.)
            if (oldItem is FeedItem.Post && newItem is FeedItem.Post) {
                val changes = Bundle()

                if (oldItem.likeCount != newItem.likeCount) {
                    changes.putInt("likeCount", newItem.likeCount)
                }

                if (oldItem.isLiked != newItem.isLiked) {
                    changes.putBoolean("isLiked", newItem.isLiked)
                }

                return if (changes.isEmpty) null else changes
            }

            return null
        }
    }
}
```

---

### Performance Considerations

**1. View recycling across different types**

```kotlin
//  DO - RecyclerView pools views by type
override fun getItemViewType(position: Int): Int {
    // Consistent types improve recycling
    return when (getItem(position)) {
        is ListItem.HeaderItem -> TYPE_HEADER
        is ListItem.UserItem -> TYPE_USER
        // ...
    }
}
```

**2. Set RecycledViewPool sizes for each type**

```kotlin
recyclerView.apply {
    val pool = recycledViewPool
    pool.setMaxRecycledViews(TYPE_HEADER, 5)
    pool.setMaxRecycledViews(TYPE_USER, 20)
    pool.setMaxRecycledViews(TYPE_AD, 3)
}
```

**3. Share RecycledViewPool for nested RecyclerViews**

```kotlin
// Parent RecyclerView
val sharedPool = RecycledViewPool()
parentRecyclerView.setRecycledViewPool(sharedPool)

// Child RecyclerView (in ViewHolder)
childRecyclerView.setRecycledViewPool(sharedPool)
```

**4. Optimize view inflation**

```kotlin
//  DO - Cache inflater
private val inflater = LayoutInflater.from(parent.context)

override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
    val view = inflater.inflate(R.layout.item_layout, parent, false)
    return ViewHolder(view)
}
```

---

### Best Practices

**1. Use sealed classes for type safety**
```kotlin
//  Compiler ensures all types handled
sealed class ListItem { /* ... */ }
```

**2. Separate ViewHolder creation logic**
```kotlin
//  Factory methods in ViewHolder
companion object {
    fun create(parent: ViewGroup): ViewHolder { /* ... */ }
}
```

**3. Use delegation for complex adapters**
```kotlin
//  Each delegate handles one type
val delegates = listOf(HeaderDelegate(), UserDelegate(), /* ... */)
```

**4. Implement efficient DiffUtil**
```kotlin
//  Use stable IDs
override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
```

**5. Consider view pool optimization**
```kotlin
//  Set appropriate pool sizes
pool.setMaxRecycledViews(TYPE, appropriate_size)
```

---

### Summary

**Multiple view types patterns:**
1. **Basic** - Simple `when` statements
2. **Sealed classes** - Type safety
3. **Adapter delegation** - Separation of concerns
4. **Library (AdapterDelegates)** - Production-ready solution

**Key concepts:**
- `getItemViewType()` - Determine type
- `onCreateViewHolder()` - Create appropriate holder
- `onBindViewHolder()` - Bind data to holder
- DiffUtil - Efficient updates

**Performance tips:**
- Optimize view recycling
- Set pool sizes appropriately
- Share pools for nested RecyclerViews
- Use ViewBinding for efficiency

**Best practices:**
- Use sealed classes
- Implement factory methods
- Consider delegation pattern
- Efficient DiffUtil implementation

---

## Ответ (RU)

**Множественные типы view** в RecyclerView позволяют отображать различные макеты в одном списке (например, заголовки, элементы, футеры, реклама).

### Базовые множественные типы view

```kotlin
class BasicMultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    // 1. Определить тип view для позиции
    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is Header -> TYPE_HEADER
            is User -> TYPE_USER
            else -> throw IllegalArgumentException()
        }
    }

    // 2. Создать соответствующий ViewHolder
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> HeaderViewHolder.create(parent)
            TYPE_USER -> UserViewHolder.create(parent)
            else -> throw IllegalArgumentException()
        }
    }

    // 3. Привязать данные
    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is HeaderViewHolder -> holder.bind(items[position] as Header)
            is UserViewHolder -> holder.bind(items[position] as User)
        }
    }
}
```

### Sealed классы для безопасности типов

```kotlin
sealed class ListItem {
    abstract val id: String

    data class HeaderItem(override val id: String, val title: String) : ListItem()
    data class UserItem(override val id: String, val name: String) : ListItem()
    data class AdItem(override val id: String, val imageUrl: String) : ListItem()
}

class SealedClassAdapter : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {
    // Компилятор гарантирует, что все типы обработаны
}
```

### Паттерн делегирования адаптера

```kotlin
interface AdapterDelegate {
    fun isForViewType(item: ListItem): Boolean
    fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
    fun onBindViewHolder(holder: RecyclerView.ViewHolder, item: ListItem)
}

// Каждый делегат обрабатывает один тип
class HeaderDelegate : AdapterDelegate { /* ... */ }
class UserDelegate : AdapterDelegate { /* ... */ }

class DelegatingAdapter : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {
    private val delegates = listOf(HeaderDelegate(), UserDelegate())
    // ...
}
```

### Соображения производительности

**1. Пул переработанных view**
```kotlin
recyclerView.recycledViewPool.setMaxRecycledViews(TYPE_HEADER, 5)
```

**2. Оптимизация инфляции view**
```kotlin
private val inflater = LayoutInflater.from(parent.context)
```

### Лучшие практики

1. Используйте sealed классы для безопасности типов
2. Разделяйте логику создания ViewHolder
3. Используйте делегирование для сложных адаптеров
4. Реализуйте эффективный DiffUtil
5. Оптимизируйте пул view

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-how-animations-work-in-recyclerview--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui
