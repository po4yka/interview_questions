---
id: android-338
title: Why Use DiffUtil / Почему использовать DiffUtil
aliases:
- DiffUtil
- DiffUtil в RecyclerView
- ListAdapter
- RecyclerView DiffUtil
topic: android
subtopics:
- performance-rendering
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
- c-performance
- q-cicd-pipeline-android--android--medium
- q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard
created: 2025-10-15
updated: 2025-10-30
sources:
- https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
tags:
- android/performance-rendering
- android/ui-views
- difficulty/medium
- diffutil
- performance
- recyclerview
---

# Вопрос (RU)

> Почему нужно использовать DiffUtil вместо notifyDataSetChanged()?

# Question (EN)

> Why should you use DiffUtil instead of notifyDataSetChanged()?

---

## Ответ (RU)

**DiffUtil** — утилитарный класс, вычисляющий разницу между двумя списками и генерирующий операции обновления. Используется с `RecyclerView` для эффективного обновления только изменённых элементов.

### Преимущества

1. **Производительность** — обновляются только изменённые элементы
2. **Анимации** — автоматические анимации добавления/удаления/перемещения
3. **Алгоритм Myers** — O(N + D²) вместо O(N²)
4. **Сохранение состояния** — позиция скролла и фокус не сбрасываются

### 1. Базовая Реализация

```kotlin
data class User(val id: Int, val name: String)

class UserDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {
    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos] == newList[newPos]
}

class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {
    private val users = mutableListOf<User>()

    fun updateUsers(newUsers: List<User>) {
        val diffResult = DiffUtil.calculateDiff(
            UserDiffCallback(users, newUsers)
        )
        users.clear()
        users.addAll(newUsers)
        diffResult.dispatchUpdatesTo(this)
    }
}
```

### 2. ListAdapter (рекомендуемый подход)

✅ **BEST PRACTICE**: Используйте ListAdapter для автоматического DiffUtil

```kotlin
class UserListAdapter : ListAdapter<User, UserListAdapter.ViewHolder>(
    object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    }
) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.tvName).text = user.name
        }
    }
}

// Использование
adapter.submitList(newUsers) // DiffUtil применяется автоматически
```

### 3. Partial Updates С Payloads

Обновление только изменённых полей:

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(old: User, new: User) = old.id == new.id
    override fun areContentsTheSame(old: User, new: User) = old == new

    override fun getChangePayload(old: User, new: User): Any? {
        val changes = mutableListOf<String>()
        if (old.name != new.name) changes.add("NAME")
        if (old.email != new.email) changes.add("EMAIL")
        return changes.ifEmpty { null }
    }
}

class UserAdapter : ListAdapter<User, ViewHolder>(UserDiffCallback()) {
    override fun onBindViewHolder(holder: ViewHolder, pos: Int, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, pos, payloads)
        } else {
            val user = getItem(pos)
            payloads.forEach { payload ->
                (payload as? List<*>)?.forEach { change ->
                    when (change) {
                        "NAME" -> holder.updateName(user.name)
                        "EMAIL" -> holder.updateEmail(user.email)
                    }
                }
            }
        }
    }
}
```

### 4. AsyncListDiffer Для Больших Списков

✅ **BEST PRACTICE**: Для списков >100 элементов

```kotlin
class LargeListAdapter : RecyclerView.Adapter<ViewHolder>() {
    private val differ = AsyncListDiffer(this,
        object : DiffUtil.ItemCallback<Item>() {
            override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
            override fun areContentsTheSame(old: Item, new: Item) = old == new
        }
    )

    val currentList: List<Item> get() = differ.currentList

    fun submitList(list: List<Item>) = differ.submitList(list)

    override fun getItemCount() = differ.currentList.size
    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(differ.currentList[pos])
    }
}
```

### Сравнение

❌ **ПЛОХО**: notifyDataSetChanged()
```kotlin
fun updateItems(newItems: List<Item>) {
    items.clear()
    items.addAll(newItems)
    notifyDataSetChanged() // Пересоздаёт все ViewHolder'ы
}
// Проблемы: нет анимаций, плохая производительность, скролл сбрасывается
```

✅ **ХОРОШО**: DiffUtil
```kotlin
fun updateItems(newItems: List<Item>) {
    submitList(newItems) // Обновляет только изменённые элементы
}
// Преимущества: анимации, производительность, позиция скролла сохраняется
```

### Рекомендации

1. ✅ Используйте **ListAdapter** для простых случаев
2. ✅ Используйте **AsyncListDiffer** для больших списков
3. ✅ Реализуйте **payloads** для частичных обновлений
4. ✅ Используйте **data class** для автоматической проверки equals()
5. ❌ Избегайте notifyDataSetChanged() при использовании DiffUtil

---

## Answer (EN)

**DiffUtil** is a utility class that calculates the difference between two lists and generates update operations. Used with `RecyclerView` to efficiently update only changed items.

### Benefits

1. **Performance** — updates only changed items
2. **Animations** — automatic add/remove/move animations
3. **Myers Algorithm** — O(N + D²) instead of O(N²)
4. **State Preservation** — scroll position and focus maintained

### 1. Basic Implementation

```kotlin
data class User(val id: Int, val name: String)

class UserDiffCallback(
    private val oldList: List<User>,
    private val newList: List<User>
) : DiffUtil.Callback() {
    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos].id == newList[newPos].id

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean =
        oldList[oldPos] == newList[newPos]
}

class UserAdapter : RecyclerView.Adapter<UserAdapter.ViewHolder>() {
    private val users = mutableListOf<User>()

    fun updateUsers(newUsers: List<User>) {
        val diffResult = DiffUtil.calculateDiff(
            UserDiffCallback(users, newUsers)
        )
        users.clear()
        users.addAll(newUsers)
        diffResult.dispatchUpdatesTo(this)
    }
}
```

### 2. ListAdapter (Recommended)

✅ **BEST PRACTICE**: Use ListAdapter for automatic DiffUtil

```kotlin
class UserListAdapter : ListAdapter<User, UserListAdapter.ViewHolder>(
    object : DiffUtil.ItemCallback<User>() {
        override fun areItemsTheSame(old: User, new: User) = old.id == new.id
        override fun areContentsTheSame(old: User, new: User) = old == new
    }
) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ViewHolder(LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false))

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(user: User) {
            itemView.findViewById<TextView>(R.id.tvName).text = user.name
        }
    }
}

// Usage
adapter.submitList(newUsers) // DiffUtil applied automatically
```

### 3. Partial Updates with Payloads

Update only changed fields:

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(old: User, new: User) = old.id == new.id
    override fun areContentsTheSame(old: User, new: User) = old == new

    override fun getChangePayload(old: User, new: User): Any? {
        val changes = mutableListOf<String>()
        if (old.name != new.name) changes.add("NAME")
        if (old.email != new.email) changes.add("EMAIL")
        return changes.ifEmpty { null }
    }
}

class UserAdapter : ListAdapter<User, ViewHolder>(UserDiffCallback()) {
    override fun onBindViewHolder(holder: ViewHolder, pos: Int, payloads: List<Any>) {
        if (payloads.isEmpty()) {
            super.onBindViewHolder(holder, pos, payloads)
        } else {
            val user = getItem(pos)
            payloads.forEach { payload ->
                (payload as? List<*>)?.forEach { change ->
                    when (change) {
                        "NAME" -> holder.updateName(user.name)
                        "EMAIL" -> holder.updateEmail(user.email)
                    }
                }
            }
        }
    }
}
```

### 4. AsyncListDiffer for Large Lists

✅ **BEST PRACTICE**: For lists >100 items

```kotlin
class LargeListAdapter : RecyclerView.Adapter<ViewHolder>() {
    private val differ = AsyncListDiffer(this,
        object : DiffUtil.ItemCallback<Item>() {
            override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
            override fun areContentsTheSame(old: Item, new: Item) = old == new
        }
    )

    val currentList: List<Item> get() = differ.currentList

    fun submitList(list: List<Item>) = differ.submitList(list)

    override fun getItemCount() = differ.currentList.size
    override fun onBindViewHolder(holder: ViewHolder, pos: Int) {
        holder.bind(differ.currentList[pos])
    }
}
```

### Comparison

❌ **BAD**: notifyDataSetChanged()
```kotlin
fun updateItems(newItems: List<Item>) {
    items.clear()
    items.addAll(newItems)
    notifyDataSetChanged() // Recreates all ViewHolders
}
// Issues: no animations, poor performance, scroll resets
```

✅ **GOOD**: DiffUtil
```kotlin
fun updateItems(newItems: List<Item>) {
    submitList(newItems) // Updates only changed items
}
// Benefits: animations, performance, scroll position maintained
```

### Recommendations

1. ✅ Use **ListAdapter** for simple cases
2. ✅ Use **AsyncListDiffer** for large lists
3. ✅ Implement **payloads** for partial updates
4. ✅ Use **data class** for automatic equals() check
5. ❌ Avoid notifyDataSetChanged() when using DiffUtil

---

## Follow-ups

1. **What's the time complexity of DiffUtil's Myers algorithm?**
   - O(N + D²) where N is sum of list sizes, D is number of differences

2. **When should you use AsyncListDiffer vs ListAdapter?**
   - AsyncListDiffer: custom adapter logic needed
   - ListAdapter: simpler cases, built-in lifecycle handling

3. **How does getChangePayload() improve performance?**
   - Allows partial ViewHolder updates instead of full rebinding
   - Only changed fields are updated, reducing layout passes

4. **What happens if areItemsTheSame() returns wrong result?**
   - Items will be treated as removed/added instead of changed
   - Animations will be incorrect (fade instead of move/change)

5. **Can DiffUtil handle large lists (10,000+ items)?**
   - Yes, but use AsyncListDiffer or run calculateDiff() on background thread
   - Consider pagination or incremental loading for very large datasets

---

## References

- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)
- [`RecyclerView` Best Practices](https://developer.android.com/guide/topics/ui/layout/recyclerview)

---

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]


### Same Level
- [[q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard]]
- [[q-cicd-pipeline-android--android--medium]]
