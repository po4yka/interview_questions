---
topic: android
tags:
  - recyclerview
  - diffutil
  - android
  - ui
difficulty: medium
status: draft
---

# What is DiffUtil for?

## Question (RU)

Зачем нужен DiffUtil?

## Answer

**DiffUtil** is a utility class in Android that calculates the difference between two lists and outputs a list of update operations that convert the first list into the second one. It's primarily used with RecyclerView to efficiently update only changed items instead of refreshing the entire list.

### Why Use DiffUtil?

1. **Performance** - Only updates changed items, not the entire list
2. **Animations** - Automatically triggers appropriate item animations
3. **Efficiency** - Uses Eugene W. Myers' difference algorithm
4. **Less Boilerplate** - Reduces manual adapter update code

### 1. Basic DiffUtil Implementation

```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String
)

class UserDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {

    override fun getOldListSize(): Int = oldList.size

    override fun getNewListSize(): Int = newList.size

    // Check if items represent the same object (usually by ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    // Check if item contents are the same
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }

    // Optional: provide payload for partial updates
    override fun getChangePayload(oldItemPosition: Int, newItemPosition: Int): Any? {
        val oldItem = oldList[oldItemPosition]
        val newItem = newList[newItemPosition]

        return when {
            oldItem.name != newItem.name -> "NAME_CHANGED"
            oldItem.email != newItem.email -> "EMAIL_CHANGED"
            else -> null
        }
    }
}

// Usage in Adapter
class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    private val users = mutableListOf<User>()

    fun updateUsers(newUsers: List<User>) {
        val diffCallback = UserDiffCallback(users, newUsers)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        users.clear()
        users.addAll(newUsers)

        diffResult.dispatchUpdatesTo(this)
    }

    // ... ViewHolder and other methods
}
```

### 2. ListAdapter with DiffUtil

Modern approach using `ListAdapter` which has built-in DiffUtil support.

```kotlin
class UserListAdapter : ListAdapter<User, UserListAdapter.ViewHolder>(UserDiffCallback()) {

    class UserDiffCallback : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val nameTextView: TextView = itemView.findViewById(R.id.tvName)
        private val emailTextView: TextView = itemView.findViewById(R.id.tvEmail)

        fun bind(user: User) {
            nameTextView.text = user.name
            emailTextView.text = user.email
        }
    }
}

// Usage in Fragment/Activity
class UsersFragment : Fragment() {

    private val adapter = UserListAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recyclerView = view.findViewById<RecyclerView>(R.id.recyclerView)
        recyclerView.adapter = adapter

        // Update list - DiffUtil automatically calculates differences
        adapter.submitList(listOf(
            User(1, "John Doe", "john@example.com"),
            User(2, "Jane Smith", "jane@example.com")
        ))
    }
}
```

### 3. AsyncListDiffer for Background Calculation

Calculates diff on a background thread for better performance with large lists.

```kotlin
class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }
    }

    private val differ = AsyncListDiffer(this, diffCallback)

    // Get current list
    val currentList: List<User>
        get() = differ.currentList

    // Submit new list (diff calculated in background)
    fun submitList(newList: List<User>) {
        differ.submitList(newList)
    }

    override fun getItemCount(): Int = differ.currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_user, parent, false)
        )
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(differ.currentList[position])
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.tvName).text = user.name
        }
    }
}
```

### 4. Partial Updates with Payloads

Update only specific parts of an item for better performance.

```kotlin
class UserAdapter : ListAdapter<User, UserAdapter.ViewHolder>(UserDiffCallback()) {

    class UserDiffCallback : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }

        // Return what changed
        override fun getChangePayload(oldItem: User, newItem: User): Any? {
            val changes = mutableListOf<String>()

            if (oldItem.name != newItem.name) {
                changes.add("NAME")
            }
            if (oldItem.email != newItem.email) {
                changes.add("EMAIL")
            }

            return if (changes.isNotEmpty()) changes else null
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_user, parent, false)
        )
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // Handle partial updates
    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val user = getItem(position)
            holder.bindPartial(user, payloads)
        }
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val nameTextView: TextView = itemView.findViewById(R.id.tvName)
        private val emailTextView: TextView = itemView.findViewById(R.id.tvEmail)

        fun bind(user: User) {
            nameTextView.text = user.name
            emailTextView.text = user.email
        }

        fun bindPartial(user: User, payloads: MutableList<Any>) {
            payloads.forEach { payload ->
                if (payload is List<*>) {
                    payload.forEach { change ->
                        when (change) {
                            "NAME" -> nameTextView.text = user.name
                            "EMAIL" -> emailTextView.text = user.email
                        }
                    }
                }
            }
        }
    }
}
```

### 5. DiffUtil with Complex Objects

```kotlin
data class Post(
    val id: Int,
    val title: String,
    val content: String,
    val author: Author,
    val likes: Int,
    val isLiked: Boolean
)

data class Author(val id: Int, val name: String)

class PostDiffCallback : DiffUtil.ItemCallback<Post>() {

    override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean {
        // Same post if IDs match
        return oldItem.id == newItem.id
    }

    override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean {
        // All fields must match
        return oldItem == newItem
    }

    override fun getChangePayload(oldItem: Post, newItem: Post): Any? {
        return when {
            oldItem.isLiked != newItem.isLiked || oldItem.likes != newItem.likes -> {
                PayloadChange.LikeChanged(newItem.likes, newItem.isLiked)
            }
            oldItem.title != newItem.title -> {
                PayloadChange.TitleChanged(newItem.title)
            }
            oldItem.content != newItem.content -> {
                PayloadChange.ContentChanged(newItem.content)
            }
            else -> null
        }
    }

    sealed class PayloadChange {
        data class LikeChanged(val likes: Int, val isLiked: Boolean) : PayloadChange()
        data class TitleChanged(val title: String) : PayloadChange()
        data class ContentChanged(val content: String) : PayloadChange()
    }
}

class PostAdapter : ListAdapter<Post, PostAdapter.ViewHolder>(PostDiffCallback()) {

    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val post = getItem(position)
            payloads.forEach { payload ->
                when (payload) {
                    is PostDiffCallback.PayloadChange.LikeChanged -> {
                        holder.updateLikes(payload.likes, payload.isLiked)
                    }
                    is PostDiffCallback.PayloadChange.TitleChanged -> {
                        holder.updateTitle(payload.title)
                    }
                    is PostDiffCallback.PayloadChange.ContentChanged -> {
                        holder.updateContent(payload.content)
                    }
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(parent.context).inflate(R.layout.item_post, parent, false)
        )
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleTextView: TextView = itemView.findViewById(R.id.tvTitle)
        private val contentTextView: TextView = itemView.findViewById(R.id.tvContent)
        private val likesTextView: TextView = itemView.findViewById(R.id.tvLikes)
        private val likeButton: ImageButton = itemView.findViewById(R.id.btnLike)

        fun bind(post: Post) {
            titleTextView.text = post.title
            contentTextView.text = post.content
            updateLikes(post.likes, post.isLiked)
        }

        fun updateTitle(title: String) {
            titleTextView.text = title
        }

        fun updateContent(content: String) {
            contentTextView.text = content
        }

        fun updateLikes(count: Int, isLiked: Boolean) {
            likesTextView.text = count.toString()
            likeButton.setImageResource(
                if (isLiked) R.drawable.ic_liked else R.drawable.ic_like
            )
        }
    }
}
```

### 6. Performance Considerations

```kotlin
class OptimizedDiffCallback<T>(
    private val oldList: List<T>,
    private val newList: List<T>,
    private val getId: (T) -> Any,
    private val areContentsEqual: (T, T) -> Boolean = { old, new -> old == new }
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return getId(oldList[oldItemPosition]) == getId(newList[newItemPosition])
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return areContentsEqual(oldList[oldItemPosition], newList[newItemPosition])
    }
}

// Usage with large lists
class LargeListAdapter : RecyclerView.Adapter<LargeListAdapter.ViewHolder>() {

    private var items = listOf<Item>()

    fun updateItems(newItems: List<Item>) {
        // Run diff calculation in background
        lifecycleScope.launch(Dispatchers.Default) {
            val diffCallback = OptimizedDiffCallback(
                oldList = items,
                newList = newItems,
                getId = { it.id }
            )
            val diffResult = DiffUtil.calculateDiff(diffCallback)

            withContext(Dispatchers.Main) {
                items = newItems
                diffResult.dispatchUpdatesTo(this@LargeListAdapter)
            }
        }
    }

    // ... adapter implementation
}
```

### Comparison: With and Without DiffUtil

#### Without DiffUtil (Bad)
```kotlin
class BadAdapter : RecyclerView.Adapter<ViewHolder>() {
    private val items = mutableListOf<Item>()

    fun updateItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged() // ❌ Refreshes entire list, no animations
    }
}
```

#### With DiffUtil (Good)
```kotlin
class GoodAdapter : ListAdapter<Item, ViewHolder>(ItemDiffCallback()) {
    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // ✅ Only updates changed items, smooth animations
    }
}
```

### Best Practices

1. ✅ **Use ListAdapter** for simple cases
2. ✅ **Use AsyncListDiffer** for large lists (>100 items)
3. ✅ **Implement payloads** for partial updates
4. ✅ **Use data class** for automatic equality checks
5. ✅ **Run on background thread** for heavy calculations
6. ❌ **Don't use notifyDataSetChanged()** when you can use DiffUtil

### Summary

| Feature | Benefit |
|---------|---------|
| Efficient updates | Only changed items are updated |
| Animations | Automatic item animations (add, remove, move) |
| Performance | Myers' diff algorithm is fast |
| ListAdapter | Built-in DiffUtil support |
| AsyncListDiffer | Background thread calculation |
| Payloads | Partial updates for better performance |

## Answer (RU)

DiffUtil — это утилита для быстрого обновления списков в RecyclerView. Она сравнивает старый и новый список и находит различия, чтобы обновлять только изменённые элементы, а не весь список.
