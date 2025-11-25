---
id: android-338
title: Why Use DiffUtil / Почему использовать DiffUtil
aliases: [DiffUtil, DiffUtil в RecyclerView, ListAdapter, RecyclerView DiffUtil]
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
  - q-what-is-diffutil-for--android--medium
  - q-what-is-layout-types-and-when-to-use--android--easy
  - q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard
  - q-which-class-to-use-for-detecting-gestures--android--medium
created: 2025-10-15
updated: 2025-10-30
sources:
  - https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil
tags: [android/performance-rendering, android/ui-views, difficulty/medium, diffutil, performance, recyclerview]
date created: Saturday, November 1st 2025, 12:47:11 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Почему нужно использовать DiffUtil вместо notifyDataSetChanged()?

# Question (EN)

> Why should you use DiffUtil instead of notifyDataSetChanged()?

---

## Ответ (RU)

**DiffUtil** — утилитарный класс, вычисляющий разницу между двумя списками и генерирующий операции обновления. Используется с RecyclerView для более эффективного обновления только изменённых элементов вместо полного перерендера.

### Преимущества

1. **Производительность** — рассчитываются и применяются только необходимые операции (insert/remove/move/change), уменьшается количество перерисовок
2. **Анимации** — автоматические анимации добавления/удаления/перемещения на основе рассчитанных diff-операций
3. **Алгоритм Myers** — асимптотика O(N + D²) (N — суммарный размер списков, D — число различий) с линейной сложностью по памяти, на практике лучше, чем наивное O(N²)
4. **Сохранение состояния** — корректный diff помогает сохранить позицию скролла, фокус и состояние ViewHolder'ов (в отличие от полного обновления)

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

✅ **BEST PRACTICE**: Используйте ListAdapter, который внутри использует AsyncListDiffer + DiffUtil.

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
adapter.submitList(newUsers) // DiffUtil применяется автоматически на основе ItemCallback
```

### 3. Partial Updates С Payloads

Обновление только изменённых полей с помощью payloads уменьшает объём работы onBindViewHolder.

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
            // Фоллбек на обычный полный биндинг
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

✅ **BEST PRACTICE**: Используйте AsyncListDiffer, когда нужен асинхронный расчёт diff (например, тяжёлые/частые обновления списка или кастомная логика адаптера).

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
    notifyDataSetChanged() // Обновляет все видимые элементы без диффа
}
// Проблемы: нет дифф-анимаций, избыточные биндинги и перерисовки; возможно изменение/сдвиг позиции скролла
```

✅ **ХОРОШО**: DiffUtil / ListAdapter
```kotlin
fun updateItems(newItems: List<Item>) {
    submitList(newItems) // Вычисляет diff и применяет только необходимые операции
}
// Преимущества: предсказуемые анимации, меньшая нагрузка на UI-поток, лучшее сохранение положения списка
```

### Рекомендации

1. ✅ Используйте **ListAdapter** для большинства стандартных случаев
2. ✅ Используйте **AsyncListDiffer** при сложной логике адаптера или частых/тяжёлых обновлениях
3. ✅ Реализуйте **payloads** для частичных обновлений при необходимости
4. ✅ Используйте **data class** или корректно переопределяйте equals()/hashCode() для корректной проверки содержимого
5. ❌ Не вызывайте `notifyDataSetChanged()` там, где уже используется DiffUtil или можно применить дифф-обновления

---

## Answer (EN)

**DiffUtil** is a utility class that calculates the difference between two lists and generates update operations. It is used with RecyclerView to more efficiently update only what actually changed instead of redrawing everything.

### Benefits

1. **Performance** — computes and applies only the necessary insert/remove/move/change operations, reducing unnecessary redraws
2. **Animations** — enables automatic add/remove/move/change animations based on the computed diff
3. **Myers Algorithm** — time complexity O(N + D²) (N = total size of both lists, D = number of differences) with linear memory usage; in practice more efficient than a naive O(N²) comparison
4. **State Preservation** — a proper diff helps preserve scroll position, focus, and ViewHolder state better than full refreshes

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

✅ **BEST PRACTICE**: Use ListAdapter, which internally relies on AsyncListDiffer + DiffUtil.

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
adapter.submitList(newUsers) // DiffUtil is applied automatically using the ItemCallback
```

### 3. Partial Updates with Payloads

Use payloads to update only changed fields and avoid full rebind work when possible.

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
            // Fallback to regular full bind
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

### 4. AsyncListDiffer for Large/Heavy Lists

✅ **BEST PRACTICE**: Use AsyncListDiffer when you want diff calculation off the main thread (e.g., large lists, frequent or heavy updates, or custom adapter implementations).

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
    notifyDataSetChanged() // Updates all visible items without using a diff
}
// Issues: no diff-based animations, redundant binds and redraws; scroll position and visual continuity may be negatively impacted
```

✅ **GOOD**: DiffUtil / ListAdapter
```kotlin
fun updateItems(newItems: List<Item>) {
    submitList(newItems) // Computes a diff and applies only the required operations
}
// Benefits: smoother animations, reduced UI thread work, better preservation of list position/state
```

### Recommendations

1. ✅ Use **ListAdapter** for most standard RecyclerView list cases
2. ✅ Use **AsyncListDiffer** when you have custom adapter behavior or frequent/heavy list updates
3. ✅ Implement **payloads** for partial updates when fine-grained changes matter
4. ✅ Use **data class** or correctly override equals()/hashCode() to make content comparison reliable
5. ❌ Avoid `notifyDataSetChanged()` when DiffUtil-based updates are applicable

---

## Follow-ups

1. **What's the time complexity of DiffUtil's Myers algorithm?**
   - O(N + D²), where N is the sum of list sizes and D is the number of differences; memory is O(N + D).

2. **When should you use AsyncListDiffer vs ListAdapter?**
   - AsyncListDiffer: when you need custom adapter implementations or want explicit control while still doing diffing off the main thread.
   - ListAdapter: when you want a simpler API and built-in AsyncListDiffer handling for common list use cases.

3. **How does getChangePayload() improve performance?**
   - Allows partial ViewHolder updates instead of full rebinding.
   - Only changed fields are updated, reducing binding work and layout passes.

4. **What happens if areItemsTheSame() / areContentsTheSame() returns incorrect results?**
   - DiffUtil will compute wrong operations: items may be treated as removed/added instead of moved/changed (or vice versa).
   - This leads to incorrect animations and potential visual glitches or stale data in ViewHolders.

5. **Can DiffUtil handle large lists (10,000+ items)?**
   - Yes, but diffing can be expensive; prefer AsyncListDiffer (or ListAdapter, which uses it) to run diff calculation off the main thread.
   - For very large datasets, consider pagination/incremental loading.

---

## References

- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [ListAdapter Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/ListAdapter)
- [RecyclerView Best Practices](https://developer.android.com/guide/topics/ui/layout/recyclerview)

---

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]


### Same Level
- [[q-what-should-you-pay-attention-to-in-order-to-optimize-a-large-list--android--hard]]
- [[q-cicd-pipeline-android--android--medium]]
