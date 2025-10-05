---
tags:
  - android
difficulty: medium
---

# Why do we need DiffUtil?

## EN (expanded)

### What is DiffUtil?

**DiffUtil** is a utility class that calculates the difference between two lists and outputs a list of update operations that convert the first list into the second one.

### The Problem it Solves

**Without DiffUtil:**
```kotlin
class SimpleAdapter : RecyclerView.Adapter<SimpleAdapter.ViewHolder>() {
    private var items = listOf<String>()

    fun updateItems(newItems: List<String>) {
        items = newItems
        notifyDataSetChanged() // ❌ Inefficient!
        // Redraws ALL items, even unchanged ones
        // No animations
        // Poor performance
    }

    // ... rest of adapter
}
```

**Problems with `notifyDataSetChanged()`:**
1. Redraws entire list (expensive)
2. No item animations
3. List scrolls to top
4. Poor user experience
5. Wastes CPU/GPU resources

### How DiffUtil Helps

DiffUtil calculates minimal updates needed:

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {
    private var items = listOf<String>()

    fun updateItems(newItems: List<String>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items = newItems
        diffResult.dispatchUpdatesTo(this)
        // ✅ Only updates changed items
        // ✅ Smooth animations
        // ✅ Maintains scroll position
    }

    class ItemDiffCallback(
        private val oldList: List<String>,
        private val newList: List<String>
    ) : DiffUtil.Callback() {

        override fun getOldListSize() = oldList.size
        override fun getNewListSize() = newList.size

        override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos] == newList[newPos]
        }

        override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
            return oldList[oldPos] == newList[newPos]
        }
    }

    // ... rest of adapter
}
```

### DiffUtil with Data Classes

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val isActive: Boolean
)

class UserDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    // Compare IDs (unique identifier)
    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos].id == newList[newPos].id
    }

    // Compare full content
    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos] == newList[newPos]
    }

    // Optional: Provide payload for partial updates
    override fun getChangePayload(oldPos: Int, newPos: Int): Any? {
        val oldUser = oldList[oldPos]
        val newUser = newList[newPos]

        return when {
            oldUser.isActive != newUser.isActive -> "status_changed"
            oldUser.name != newUser.name -> "name_changed"
            else -> null
        }
    }
}

class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {
    private var users = listOf<User>()

    fun updateUsers(newUsers: List<User>) {
        val diffCallback = UserDiffCallback(users, newUsers)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        users = newUsers
        diffResult.dispatchUpdatesTo(this)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val user = users[position]
            when (payloads[0]) {
                "status_changed" -> holder.updateStatus(user.isActive)
                "name_changed" -> holder.updateName(user.name)
            }
        }
    }

    // ... rest of adapter
}
```

### AsyncListDiffer

For background calculation:

```kotlin
class AsyncUserAdapter : RecyclerView.Adapter<AsyncUserAdapter.ViewHolder>() {

    private val differ = AsyncListDiffer(this, object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }
    })

    fun submitList(newList: List<User>) {
        differ.submitList(newList)
        // Calculation happens on background thread
    }

    override fun getItemCount() = differ.currentList.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val user = differ.currentList[position]
        holder.bind(user)
    }

    // ... rest of adapter
}
```

### ListAdapter (Recommended)

The simplest approach:

```kotlin
class ModernUserAdapter : ListAdapter<User, ModernUserAdapter.ViewHolder>(UserComparator) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemUserBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(user: User) {
            binding.apply {
                nameText.text = user.name
                emailText.text = user.email
                statusIndicator.setImageResource(
                    if (user.isActive) R.drawable.ic_active
                    else R.drawable.ic_inactive
                )
            }
        }
    }

    object UserComparator : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }
    }
}

// Usage
val adapter = ModernUserAdapter()
recyclerView.adapter = adapter

// Update list
adapter.submitList(newUserList)
```

### Performance Comparison

```kotlin
// Test: Update list of 1000 items with 50 changes

// Without DiffUtil
// Time: ~100ms
// Updates: 1000 items redrawn
// Animations: None

// With DiffUtil
// Time: ~15ms (calculation) + ~10ms (updates)
// Updates: Only 50 items redrawn
// Animations: Smooth item animations
```

### Complex Example with Payloads

```kotlin
sealed class ListUpdate {
    data class NameChanged(val newName: String) : ListUpdate()
    data class StatusChanged(val isActive: Boolean) : ListUpdate()
    data class AvatarChanged(val avatarUrl: String) : ListUpdate()
}

class AdvancedUserAdapter : ListAdapter<User, AdvancedUserAdapter.ViewHolder>(
    UserComparator
) {
    override fun onBindViewHolder(holder: ViewHolder, position: Int, payloads: MutableList<Any>) {
        if (payloads.isEmpty()) {
            onBindViewHolder(holder, position)
        } else {
            val user = getItem(position)
            payloads.forEach { payload ->
                when (payload) {
                    is ListUpdate.NameChanged ->
                        holder.updateName(payload.newName)
                    is ListUpdate.StatusChanged ->
                        holder.updateStatus(payload.isActive)
                    is ListUpdate.AvatarChanged ->
                        holder.updateAvatar(payload.avatarUrl)
                }
            }
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    // ... ViewHolder implementation

    object UserComparator : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean {
            return oldItem == newItem
        }

        override fun getChangePayload(oldItem: User, newItem: User): Any? {
            val changes = mutableListOf<ListUpdate>()

            if (oldItem.name != newItem.name) {
                changes.add(ListUpdate.NameChanged(newItem.name))
            }
            if (oldItem.isActive != newItem.isActive) {
                changes.add(ListUpdate.StatusChanged(newItem.isActive))
            }
            if (oldItem.avatarUrl != newItem.avatarUrl) {
                changes.add(ListUpdate.AvatarChanged(newItem.avatarUrl))
            }

            return changes.ifEmpty { null }
        }
    }
}
```

### In Jetpack Compose

Compose doesn't need DiffUtil:

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // Stable key like DiffUtil's areItemsTheSame
        ) { user ->
            UserItem(user)
            // Compose automatically recomposes only changed items
        }
    }
}

@Composable
fun UserItem(user: User) {
    Row(modifier = Modifier.padding(16.dp)) {
        Text(user.name)
        Text(user.email)
        // Only recomposes if user data changes
    }
}
```

### Key Benefits

1. **Performance**: Only updates changed items
2. **Animations**: Smooth item add/remove/move animations
3. **Scroll Position**: Maintains user's scroll position
4. **Efficiency**: Reduces CPU/GPU work
5. **UX**: Better user experience

---

## RU (original)

Зачем нужен DiffUtil?

DiffUtil — это утилита для быстрого обновления списков в RecyclerView. Она сравнивает старый и новый список и находит различия, чтобы обновлять только изменённые элементы, а не весь список.
