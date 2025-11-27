---
id: android-232
title: DiffUtil / Компонент DiffUtil
aliases: [DiffUtil, Компонент DiffUtil]
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
  - q-recyclerview-diffutil-advanced--android--medium
  - q-what-is-known-about-recyclerview--android--easy
  - q-what-layout-allows-overlapping-objects--android--easy
  - q-why-diffutil-needed--android--medium
  - q-why-use-diffutil--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/medium, diffutil, optimization, performance, recyclerview]

date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> Зачем нужен DiffUtil?

# Question (EN)

> Why do we need DiffUtil?

## Ответ (RU)

**DiffUtil** — это утилитарный класс в Android, который вычисляет разницу между двумя списками и возвращает набор операций обновления для преобразования первого списка во второй. Чаще всего используется с RecyclerView для эффективного обновления только изменившихся элементов вместо перерисовки всего списка.

### Зачем Нужен DiffUtil?

1. **Производительность** — Обновляет только изменившиеся элементы, а не весь список.
2. **Анимации** — Позволяет автоматически применять корректные анимации добавления, удаления и перемещения.
3. **Эффективность** — Основан на алгоритме поиска минимальной разницы (Eugene W. Myers diff), что обычно даёт хорошую производительность для UI-списков.
4. **Меньше шаблонного кода** — Уменьшает количество ручных вызовов `notifyItem...` и `notifyDataSetChanged()`.

### 1. Базовая Реализация `DiffUtil.Callback`

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

    // Проверка, представляют ли элементы один и тот же объект (обычно по ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    // Проверка, одинаково ли содержимое элементов
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }

    // Опционально: payload для частичных обновлений (здесь возвращается только первый обнаруженный тип изменения)
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

// Использование в адаптере
class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    private val users = mutableListOf<User>()

    fun updateUsers(newUsers: List<User>) {
        val diffCallback = UserDiffCallback(users, newUsers)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        users.clear()
        users.addAll(newUsers)

        diffResult.dispatchUpdatesTo(this)
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
    // ... остальная реализация ViewHolder и onBindViewHolder/onCreateViewHolder
}
```

### 2. ListAdapter С DiffUtil (рекомендуемый подход)

`ListAdapter` и `AsyncListDiffer` под капотом используют `DiffUtil` и выполняют вычисления diff вне главного потока, упрощая код.

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

// Использование
// submitList() триггерит вычисление diff и обновление RecyclerView
adapter.submitList(newUserList)
```

### 3. AsyncListDiffer Для Кастомных Адаптеров

Используйте `AsyncListDiffer`, когда нужен свой `RecyclerView.Adapter`, но вы хотите асинхронный diff.

```kotlin
class AsyncUserAdapter : RecyclerView.Adapter<AsyncUserAdapter.ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem == newItem
    }

    private val differ = AsyncListDiffer(this, diffCallback)

    val currentList: List<User>
        get() = differ.currentList

    fun submitList(newList: List<User>) {
        differ.submitList(newList)
    }

    override fun getItemCount(): Int = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(currentList[position])
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.tvName).text = user.name
        }
    }
}
```

### 4. Частичные Обновления (payloads)

Использование `payload` позволяет обновлять только изменившиеся поля элемента.

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean =
        oldItem == newItem

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        val changes = mutableListOf<String>()

        if (oldItem.name != newItem.name) changes.add("NAME")
        if (oldItem.email != newItem.email) changes.add("EMAIL")

        return if (changes.isNotEmpty()) changes else null
    }
}

class PayloadUserAdapter : ListAdapter<User, PayloadUserAdapter.ViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
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

### 5. DiffUtil Со Сложными Объектами

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

    override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean =
        oldItem == newItem

    override fun getChangePayload(oldItem: Post, newItem: Post): Any? {
        return when {
            oldItem.isLiked != newItem.isLiked || oldItem.likes != newItem.likes ->
                PayloadChange.LikeChanged(newItem.likes, newItem.isLiked)

            oldItem.title != newItem.title ->
                PayloadChange.TitleChanged(newItem.title)

            oldItem.content != newItem.content ->
                PayloadChange.ContentChanged(newItem.content)

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

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_post, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val post = getItem(position)
            payloads.forEach { payload ->
                when (payload) {
                    is PostDiffCallback.PayloadChange.LikeChanged ->
                        holder.updateLikes(payload.likes, payload.isLiked)

                    is PostDiffCallback.PayloadChange.TitleChanged ->
                        holder.updateTitle(payload.title)

                    is PostDiffCallback.PayloadChange.ContentChanged ->
                        holder.updateContent(payload.content)
                }
            }
        }
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

### 6. Замечания По Производительности

- `DiffUtil.calculateDiff` можно вызывать в фоновом потоке, но применение результата (`dispatchUpdatesTo`) и любые изменения, влияющие на UI, должны происходить на главном потоке.
- `ListAdapter` и `AsyncListDiffer` уже обрабатывают diff асинхронно, поэтому чаще всего нет необходимости вручную переносить вычисление в корутину.
- Избегайте использования `notifyDataSetChanged()` без необходимости — он ломает анимации и дороже, чем точечные обновления.

Пример вынесения diff в фон для кастомного адаптера (упрощённо, без привязки `lifecycleScope` к адаптеру):

```kotlin
class LargeListAdapter : RecyclerView.Adapter<LargeListAdapter.ViewHolder>() {

    private var items: List<Item> = emptyList()

    fun updateItems(newItems: List<Item>, scope: CoroutineScope) {
        scope.launch(Dispatchers.Default) {
            val diffCallback = object : DiffUtil.Callback() {
                override fun getOldListSize() = items.size
                override fun getNewListSize() = newItems.size

                override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean =
                    items[oldItemPosition].id == newItems[newItemPosition].id

                override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean =
                    items[oldItemPosition] == newItems[newItemPosition]
            }

            val diffResult = DiffUtil.calculateDiff(diffCallback)

            withContext(Dispatchers.Main) {
                items = newItems
                diffResult.dispatchUpdatesTo(this@LargeListAdapter)
            }
        }
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
    // ... реализация
}
```

### Сравнение: Без DiffUtil Vs С DiffUtil

```kotlin
class BadAdapter : RecyclerView.Adapter<BadAdapter.ViewHolder>() {
    private val items = mutableListOf<Item>()

    fun updateItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged() // Обновляет весь список, без диффа и анимаций
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
}
```

```kotlin
class GoodAdapter : ListAdapter<Item, GoodAdapter.ViewHolder>(ItemDiffCallback()) {

    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Использует DiffUtil под капотом
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
}
```

### Лучшие Практики (RU)

1. Используйте `ListAdapter`, когда это возможно — он уже интегрирован с `DiffUtil`.
2. Используйте `AsyncListDiffer`, если нужен свой `RecyclerView.Adapter`.
3. Реализуйте `areItemsTheSame` и `areContentsTheSame` корректно (ID vs содержимое).
4. Используйте `payloads` для частичных обновлений сложных элементов.
5. Не вызывайте `notifyDataSetChanged()`, если можно применить точечные обновления через `DiffUtil`.
6. Держите вычисление diff вне главного потока, если делаете его вручную для очень больших списков, и всегда обновляйте UI на main thread.

## Answer (EN)

**DiffUtil** is a utility class in Android that calculates the difference between two lists and produces a list of update operations that convert the first list into the second one. It is primarily used with RecyclerView to efficiently update only changed items instead of refreshing the entire list.

### Why Use DiffUtil?

1. **Performance** - Updates only changed items instead of the whole list.
2. **Animations** - Enables proper add/remove/move animations automatically.
3. **Efficiency** - Based on a minimal-diff algorithm (Eugene W. Myers) suitable for UI lists.
4. **Less Boilerplate** - Reduces manual `notifyItem...` / `notifyDataSetChanged()` calls.

### 1. Basic `DiffUtil.Callback` Implementation

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

    // Check if items represent the same logical entity (usually by ID)
    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    // Check if item contents are equal
    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }

    // Optional: provide payload for partial updates (here only the first detected change type is returned)
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

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
    // ... other ViewHolder / Adapter code
}
```

### 2. ListAdapter with DiffUtil (recommended)

`ListAdapter` and `AsyncListDiffer` use `DiffUtil` under the hood and run diff computation off the main thread for you.

```kotlin
class UserListAdapter : ListAdapter<User, UserListAdapter.ViewHolder>(UserDiffCallback()) {

    class UserDiffCallback : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem == newItem
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

// Usage
adapter.submitList(newUserList)
```

### 3. AsyncListDiffer for Custom Adapters

Use `AsyncListDiffer` when you need a custom `RecyclerView.Adapter` but still want async diffing.

```kotlin
class AsyncUserAdapter : RecyclerView.Adapter<AsyncUserAdapter.ViewHolder>() {

    private val diffCallback = object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: User, newItem: User): Boolean =
            oldItem == newItem
    }

    private val differ = AsyncListDiffer(this, diffCallback)

    val currentList: List<User>
        get() = differ.currentList

    fun submitList(newList: List<User>) {
        differ.submitList(newList)
    }

    override fun getItemCount(): Int = currentList.size

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(currentList[position])
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.tvName).text = user.name
        }
    }
}
```

### 4. Partial Updates with Payloads

Use `payload` to update only changed parts of an item for better performance.

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: User, newItem: User): Boolean =
        oldItem == newItem

    override fun getChangePayload(oldItem: User, newItem: User): Any? {
        val changes = mutableListOf<String>()

        if (oldItem.name != newItem.name) changes.add("NAME")
        if (oldItem.email != newItem.email) changes.add("EMAIL")

        return if (changes.isNotEmpty()) changes else null
    }
}

class PayloadUserAdapter : ListAdapter<User, PayloadUserAdapter.ViewHolder>(UserDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
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

    override fun areItemsTheSame(oldItem: Post, newItem: Post): Boolean =
        oldItem.id == newItem.id

    override fun areContentsTheSame(oldItem: Post, newItem: Post): Boolean =
        oldItem == newItem

    override fun getChangePayload(oldItem: Post, newItem: Post): Any? {
        return when {
            oldItem.isLiked != newItem.isLiked || oldItem.likes != newItem.likes ->
                PayloadChange.LikeChanged(newItem.likes, newItem.isLiked)
            oldItem.title != newItem.title ->
                PayloadChange.TitleChanged(newItem.title)
            oldItem.content != newItem.content ->
                PayloadChange.ContentChanged(newItem.content)
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

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_post, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int,
        payloads: MutableList<Any>
    ) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, position, payloads)
        } else {
            val post = getItem(position)
            payloads.forEach { payload ->
                when (payload) {
                    is PostDiffCallback.PayloadChange.LikeChanged ->
                        holder.updateLikes(payload.likes, payload.isLiked)
                    is PostDiffCallback.PayloadChange.TitleChanged ->
                        holder.updateTitle(payload.title)
                    is PostDiffCallback.PayloadChange.ContentChanged ->
                        holder.updateContent(payload.content)
                }
            }
        }
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

### 6. Performance Notes (EN)

- You may compute `DiffUtil.calculateDiff` off the main thread, but applying the result (`dispatchUpdatesTo`) and mutating adapter data must be done on the main thread.
- `ListAdapter` / `AsyncListDiffer` already handle async diffing; prefer them unless you have specific needs.
- Avoid `notifyDataSetChanged()` when granular updates via `DiffUtil` are possible.

### Comparison: Without Vs With DiffUtil

```kotlin
class BadAdapter : RecyclerView.Adapter<BadAdapter.ViewHolder>() {
    private val items = mutableListOf<Item>()

    fun updateItems(newItems: List<Item>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged() // Refreshes entire list, no diff, no fine-grained animations
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
}
```

```kotlin
class GoodAdapter : ListAdapter<Item, GoodAdapter.ViewHolder>(ItemDiffCallback()) {

    fun updateItems(newItems: List<Item>) {
        submitList(newItems) // Uses DiffUtil internally for efficient updates
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView)
}
```

### Best Practices (EN)

1. Prefer `ListAdapter` when possible; it integrates DiffUtil for you.
2. Use `AsyncListDiffer` when you need a custom adapter implementation.
3. Implement `areItemsTheSame` (identity) and `areContentsTheSame` (equality) carefully.
4. Use payloads for partial updates on complex rows.
5. Do not call `notifyDataSetChanged()` unnecessarily; let DiffUtil handle fine-grained updates.
6. If manually computing diffs for very large lists, do it off the main thread and apply results on the main thread.

---

## Follow-ups

- [[q-what-is-known-about-recyclerview--android--easy]]
- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-android-async-primitives--android--easy]]
- [[q-android-performance-measurement-tools--android--medium]]

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

- [[q-how-animations-work-in-recyclerview--android--medium]]
- [[q-is-layoutinflater-a-singleton-and-why--android--medium]]
- [[q-single-activity-pros-cons--android--medium]]
