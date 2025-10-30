---
id: 20251012-122711192
title: "Why DiffUtil Needed / Зачем нужен DiffUtil"
aliases: [DiffUtil, AsyncListDiffer, ListAdapter, Зачем DiffUtil]
topic: android
subtopics: [ui-views, performance-rendering]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview, c-adapter-pattern, q-recyclerview-optimization--android--hard]
created: 2025-10-15
updated: 2025-10-30
tags: [android/ui-views, android/performance-rendering, recyclerview, adapter, diffutil, performance, difficulty/medium]
---

# Вопрос (RU)

> Зачем нужен DiffUtil в Android? Какие проблемы он решает?

# Question (EN)

> Why do we need DiffUtil in Android? What problems does it solve?

---

## Ответ (RU)

**DiffUtil** — утилита для вычисления разницы между двумя списками и генерации минимального набора операций обновления RecyclerView.

### Проблема без DiffUtil

**❌ Неэффективный подход:**

```kotlin
class SimpleAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = listOf<String>()

    fun updateItems(newItems: List<String>) {
        items = newItems
        notifyDataSetChanged() // Перерисовывает ВСЕ элементы
    }
}
```

**Последствия `notifyDataSetChanged()`:**
- Полная перерисовка всех элементов (медленно)
- Отсутствие анимаций
- Потеря позиции скролла
- Расход CPU/GPU ресурсов

### DiffUtil.Callback

**✅ Базовое использование:**

```kotlin
class ItemDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    // Сравнение по ID
    override fun areItemsTheSame(old: Int, new: Int): Boolean =
        oldList[old].id == newList[new].id

    // Сравнение содержимого
    override fun areContentsTheSame(old: Int, new: Int): Boolean =
        oldList[old] == newList[new]
}

fun updateUsers(newUsers: List<User>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(users, newUsers))
    users = newUsers
    diffResult.dispatchUpdatesTo(this)
}
```

### Частичное обновление через Payload

**✅ Оптимизация для больших объектов:**

```kotlin
override fun getChangePayload(old: Int, new: Int): Any? {
    val oldUser = oldList[old]
    val newUser = newList[new]

    return buildMap {
        if (oldUser.name != newUser.name) put("name", newUser.name)
        if (oldUser.status != newUser.status) put("status", newUser.status)
    }.takeIf { it.isNotEmpty() }
}

override fun onBindViewHolder(holder: ViewHolder, pos: Int, payloads: List<Any>) {
    if (payloads.isEmpty()) {
        onBindViewHolder(holder, pos)
    } else {
        val changes = payloads[0] as Map<*, *>
        changes["name"]?.let { holder.updateName(it as String) }
        changes["status"]?.let { holder.updateStatus(it as Boolean) }
    }
}
```

### AsyncListDiffer

**✅ Фоновые вычисления:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val differ = AsyncListDiffer(this, object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    })

    fun submitList(list: List<User>) = differ.submitList(list)

    override fun getItemCount() = differ.currentList.size
    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(differ.currentList[pos])
    }
}
```

### ListAdapter (рекомендуется)

**✅ Современный подход:**

```kotlin
class UserAdapter : ListAdapter<User, UserAdapter.ViewHolder>(DiffCallback) {

    override fun onCreateViewHolder(parent: ViewGroup, type: Int): ViewHolder {
        val binding = ItemUserBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(getItem(pos))
    }

    object DiffCallback : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    }
}

// Использование
adapter.submitList(newUsers)
```

### Compose vs Views

**В Compose DiffUtil не нужен:**

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // Аналог areItemsTheSame
        ) { user ->
            UserItem(user)
        }
    }
}
```

**Производительность (1000 элементов, 50 изменений):**
- `notifyDataSetChanged()`: ~100ms, 1000 перерисовок
- `DiffUtil`: ~25ms (15ms расчет + 10ms обновление), 50 перерисовок

---

## Answer (EN)

**DiffUtil** is a utility that calculates the difference between two lists and generates minimal update operations for RecyclerView.

### Problem Without DiffUtil

**❌ Inefficient approach:**

```kotlin
class SimpleAdapter : RecyclerView.Adapter<ViewHolder>() {
    private var items = listOf<String>()

    fun updateItems(newItems: List<String>) {
        items = newItems
        notifyDataSetChanged() // Redraws ALL items
    }
}
```

**Issues with `notifyDataSetChanged()`:**
- Complete redraw of all items (slow)
- No animations
- Lost scroll position
- Wasted CPU/GPU resources

### DiffUtil.Callback

**✅ Basic usage:**

```kotlin
class ItemDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    // Compare by ID
    override fun areItemsTheSame(old: Int, new: Int): Boolean =
        oldList[old].id == newList[new].id

    // Compare content
    override fun areContentsTheSame(old: Int, new: Int): Boolean =
        oldList[old] == newList[new]
}

fun updateUsers(newUsers: List<User>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(users, newUsers))
    users = newUsers
    diffResult.dispatchUpdatesTo(this)
}
```

### Partial Updates via Payload

**✅ Optimization for large objects:**

```kotlin
override fun getChangePayload(old: Int, new: Int): Any? {
    val oldUser = oldList[old]
    val newUser = newList[new]

    return buildMap {
        if (oldUser.name != newUser.name) put("name", newUser.name)
        if (oldUser.status != newUser.status) put("status", newUser.status)
    }.takeIf { it.isNotEmpty() }
}

override fun onBindViewHolder(holder: ViewHolder, pos: Int, payloads: List<Any>) {
    if (payloads.isEmpty()) {
        onBindViewHolder(holder, pos)
    } else {
        val changes = payloads[0] as Map<*, *>
        changes["name"]?.let { holder.updateName(it as String) }
        changes["status"]?.let { holder.updateStatus(it as Boolean) }
    }
}
```

### AsyncListDiffer

**✅ Background calculation:**

```kotlin
class AsyncAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val differ = AsyncListDiffer(this, object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    })

    fun submitList(list: List<User>) = differ.submitList(list)

    override fun getItemCount() = differ.currentList.size
    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(differ.currentList[pos])
    }
}
```

### ListAdapter (recommended)

**✅ Modern approach:**

```kotlin
class UserAdapter : ListAdapter<User, UserAdapter.ViewHolder>(DiffCallback) {

    override fun onCreateViewHolder(parent: ViewGroup, type: Int): ViewHolder {
        val binding = ItemUserBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(getItem(pos))
    }

    object DiffCallback : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    }
}

// Usage
adapter.submitList(newUsers)
```

### Compose vs Views

**In Compose, DiffUtil is not needed:**

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // Similar to areItemsTheSame
        ) { user ->
            UserItem(user)
        }
    }
}
```

**Performance (1000 items, 50 changes):**
- `notifyDataSetChanged()`: ~100ms, 1000 redraws
- `DiffUtil`: ~25ms (15ms calculation + 10ms updates), 50 redraws

---

## Follow-ups

- How does DiffUtil's Myers algorithm work internally?
- When should you use `DiffUtil.calculateDiff(detectMoves = true)`?
- What are the performance implications of DiffUtil on the main thread?
- How does `submitList()` handle rapid consecutive updates?
- When would you implement custom `getChangePayload()` logic?

## References

- [[c-recyclerview]]
- [[c-adapter-pattern]]
- [[c-myers-diff-algorithm]]
- [Android DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [RecyclerView Performance](https://developer.android.com/topic/performance/recyclerview)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-basics--android--easy]]
- [[q-viewholder-pattern--android--easy]]

### Related (Same Level)
- [[q-recyclerview-optimization--android--medium]]
- [[q-listadapter-vs-adapter--android--medium]]
- [[q-payload-updates--android--medium]]

### Advanced (Harder)
- [[q-custom-diff-algorithm--android--hard]]
- [[q-recyclerview-memory-leaks--android--hard]]
