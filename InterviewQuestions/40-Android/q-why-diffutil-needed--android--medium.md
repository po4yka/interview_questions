---
id: android-367
title: "Why DiffUtil Needed / Зачем нужен DiffUtil"
aliases: [AsyncListDiffer, DiffUtil, ListAdapter]
topic: android
subtopics: [performance-rendering, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-components, c-recyclerview, q-android-app-components--android--easy]
created: 2025-10-15
updated: 2025-11-10
tags: [adapter, android/performance-rendering, android/ui-views, difficulty/medium, diffutil, performance, recyclerview]

---

# Вопрос (RU)

> Зачем нужен DiffUtil в Android? Какие проблемы он решает?

# Question (EN)

> Why do we need DiffUtil in Android? What problems does it solve?

---

## Ответ (RU)

**DiffUtil** — утилита для вычисления разницы между двумя списками и генерации минимального набора операций обновления RecyclerView.

### Проблема Без DiffUtil

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
- Полная перерисовка всех элементов (дороже по ресурсам)
- Отсутствие точечных анимаций изменений/перемещений
- Повышенная нагрузка на CPU/GPU, возможные подлагивания
- Сложнее оптимизировать обновления для больших списков

### DiffUtil.`Callback`

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

> На практике списки, переданные в DiffUtil, должны рассматриваться как неизменяемые во время вычисления diff, чтобы избежать некорректных результатов.

### Частичное Обновление Через Payload

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
        // В реальном коде стоит корректно обработать все payloads и проверить типы
        val changes = payloads[0] as Map<*, *>
        changes["name"]?.let { holder.updateName(it as String) }
        changes["status"]?.let { holder.updateStatus(it as Boolean) }
    }
}
```

### AsyncListDiffer

**✅ Фоновые вычисления и оркестрация обновлений:**

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

> AsyncListDiffer вычисляет diff в фоне, отменяет неактуальные вычисления и применяет обновления на главном потоке, ожидая, что переданные списки не будут изменяться после передачи.

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

### Compose Vs Views

**В Compose DiffUtil не нужен:**

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // Аналог areItemsTheSame: стабильный ключ для элемента
        ) { user ->
            UserItem(user)
        }
    }
}
```

**Производительность (пример для иллюстрации, не точный бенчмарк):**
- `notifyDataSetChanged()`: полная перерисовка (дороже, чем нужно)
- `DiffUtil`: рассчитывает изменения и обновляет только изменившиеся элементы, уменьшает перерисовки и нагрузку

---

## Answer (EN)

**DiffUtil** is a utility that calculates the difference between two lists and generates a minimal set of update operations for RecyclerView.

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
- Full redraw of all items (more expensive than necessary)
- No fine-grained change/move animations
- Increased CPU/GPU usage, potential jank
- Harder to optimize updates for large lists

### DiffUtil.`Callback`

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

> In practice, lists passed to DiffUtil should be treated as immutable during diff calculation to avoid inconsistent results.

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
        // In real code, you should handle all payloads and validate their types
        val changes = payloads[0] as Map<*, *>
        changes["name"]?.let { holder.updateName(it as String) }
        changes["status"]?.let { holder.updateStatus(it as Boolean) }
    }
}
```

### AsyncListDiffer

**✅ Background calculation and update orchestration:**

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

> AsyncListDiffer computes the diff off the main thread, cancels obsolete calculations, and applies updates on the main thread, assuming the provided lists are not modified after submission.

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

### Compose Vs Views

**In Compose, DiffUtil is not needed:**

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(
            items = users,
            key = { it.id } // Similar to areItemsTheSame: stable key for each item
        ) { user ->
            UserItem(user)
        }
    }
}
```

**Performance (illustrative example, not an exact benchmark):**
- `notifyDataSetChanged()`: redraws all items (more work than necessary)
- `DiffUtil`: computes changes and updates only modified items, reducing redraws and resource usage

---

## Follow-ups

- How does DiffUtil's algorithm work internally?
- When should you use `DiffUtil.calculateDiff(detectMoves = true)`?
- What are the performance implications of DiffUtil on the main thread?
- How does `submitList()` handle rapid consecutive updates?
- When would you implement custom `getChangePayload()` logic?

## References

- [[c-recyclerview]]
- [Android DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [RecyclerView Performance](https://developer.android.com/topic/performance/recyclerview)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]

### Related (Same Level)
- [[q-recyclerview-explained--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]
