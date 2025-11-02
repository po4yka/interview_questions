---
id: android-085
title: "RecyclerView ViewTypes Delegation / Делегирование ViewTypes в RecyclerView"
aliases:
  - "RecyclerView ViewTypes Delegation"
  - "Делегирование ViewTypes в RecyclerView"
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview-viewtypes, q-recyclerview-basics--android--easy, q-adapter-patterns--android--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [android/ui-views, adapter, view-types, design-patterns, difficulty/medium]
sources: [https://developer.android.com/guide/topics/ui/layout/recyclerview]
---

# Вопрос (RU)
> Как обрабатывать множественные типы view в RecyclerView?

# Question (EN)
> How to handle multiple view types in RecyclerView?

---

## Ответ (RU)

**Теория ViewTypes:**
ViewTypes позволяют отображать разные макеты в одном RecyclerView (заголовки, элементы, футеры, реклама). Правильная реализация критична для производительности и поддерживаемости гетерогенных списков.

**Основные компоненты:**
- `getItemViewType()` - определяет тип view для позиции
- `onCreateViewHolder()` - создает ViewHolder по типу
- `onBindViewHolder()` - привязывает данные к ViewHolder

```kotlin
// Базовый адаптер с множественными типами
class MultiTypeAdapter(private val items: List<Any>) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_HEADER = 0
        private const val TYPE_USER = 1
    }

    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is Header -> TYPE_HEADER
            is User -> TYPE_USER
            else -> throw IllegalArgumentException("Unknown type")
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> HeaderViewHolder(LayoutInflater.from(parent.context)
                .inflate(R.layout.item_header, parent, false))
            TYPE_USER -> UserViewHolder(LayoutInflater.from(parent.context)
                .inflate(R.layout.item_user, parent, false))
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is HeaderViewHolder -> holder.bind(items[position] as Header)
            is UserViewHolder -> holder.bind(items[position] as User)
        }
    }
}
```

**Sealed классы для типобезопасности:**
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
        val email: String
    ) : ListItem()
}
```

**Adapter Delegation Pattern:**
Делегирование позволяет разделить логику разных типов элементов на отдельные адаптеры.

```kotlin
// Делегат для заголовка
class HeaderDelegate : AdapterDelegate<ListItem> {
    override fun isForViewType(items: List<ListItem>, position: Int): Boolean {
        return items[position] is ListItem.HeaderItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_header, parent, false)
        return HeaderViewHolder(view)
    }

    override fun onBindViewHolder(items: List<ListItem>, position: Int, holder: RecyclerView.ViewHolder) {
        val header = items[position] as ListItem.HeaderItem
        (holder as HeaderViewHolder).bind(header)
    }
}
```

## Answer (EN)

**ViewTypes Theory:**
ViewTypes allow displaying different layouts in the same RecyclerView (headers, items, footers, ads). Proper implementation is critical for performance and maintainability of heterogeneous lists.

**Main components:**
- `getItemViewType()` - determines view type for position
- `onCreateViewHolder()` - creates ViewHolder by type
- `onBindViewHolder()` - binds data to ViewHolder

```kotlin
// Basic adapter with multiple types
class MultiTypeAdapter(private val items: List<Any>) : RecyclerView.Adapter<RecyclerView.ViewHolder>() {

    companion object {
        private const val TYPE_HEADER = 0
        private const val TYPE_USER = 1
    }

    override fun getItemViewType(position: Int): Int {
        return when (items[position]) {
            is Header -> TYPE_HEADER
            is User -> TYPE_USER
            else -> throw IllegalArgumentException("Unknown type")
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> HeaderViewHolder(LayoutInflater.from(parent.context)
                .inflate(R.layout.item_header, parent, false))
            TYPE_USER -> UserViewHolder(LayoutInflater.from(parent.context)
                .inflate(R.layout.item_user, parent, false))
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (holder) {
            is HeaderViewHolder -> holder.bind(items[position] as Header)
            is UserViewHolder -> holder.bind(items[position] as User)
        }
    }
}
```

**Sealed classes for type safety:**
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
        val email: String
    ) : ListItem()
}
```

**Adapter Delegation Pattern:**
Delegation allows separating logic for different item types into separate adapters.

```kotlin
// Delegate for header
class HeaderDelegate : AdapterDelegate<ListItem> {
    override fun isForViewType(items: List<ListItem>, position: Int): Boolean {
        return items[position] is ListItem.HeaderItem
    }

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_header, parent, false)
        return HeaderViewHolder(view)
    }

    override fun onBindViewHolder(items: List<ListItem>, position: Int, holder: RecyclerView.ViewHolder) {
        val header = items[position] as ListItem.HeaderItem
        (holder as HeaderViewHolder).bind(header)
    }
}
```

---

## Follow-ups

- How do you optimize performance with multiple view types?
- What are the benefits of using adapter delegation?
- How do you handle view type changes efficiently?

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-basics--android--easy]] - RecyclerView basics
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-adapter-patterns--android--medium]] - Adapter patterns
- [[q-recyclerview-performance--android--medium]] - RecyclerView performance
- [[q-viewholder-pattern--android--medium]] - ViewHolder pattern

### Advanced (Harder)
- [[q-recyclerview-advanced--android--hard]] - RecyclerView advanced
- [[q-android-runtime-internals--android--hard]] - Runtime internals
