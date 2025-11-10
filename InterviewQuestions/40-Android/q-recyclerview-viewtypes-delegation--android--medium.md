---
id: android-085
title: RecyclerView ViewTypes Delegation / Делегирование ViewTypes в RecyclerView
aliases:
- RecyclerView ViewTypes Delegation
- Делегирование ViewTypes в RecyclerView
topic: android
subtopics:
- ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-recyclerview-explained--android--medium
- c-android
created: 2025-10-13
updated: 2025-11-10
tags:
- adapter
- android/ui-views
- design-patterns
- difficulty/medium
- view-types
sources:
- "https://developer.android.com/guide/topics/ui/layout/recyclerview"

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
- `getItemViewType(position)` — определяет тип view для позиции; его результат используется фреймворком при вызове `onCreateViewHolder(parent, viewType)`
- `onCreateViewHolder(parent, viewType)` — создает `ViewHolder` по полученному типу
- `onBindViewHolder(holder, position)` — привязывает данные к соответствующему `ViewHolder`

```kotlin
// Базовый адаптер с множественными типами (упрощённый пример)
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
// На практике вместо List<Any> лучше использовать типизированные модели (например, sealed-классы ниже) для типобезопасности.
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
Делегирование позволяет разделить логику разных типов элементов на отдельные делегаты и тем самым упростить адаптер.

```kotlin
// Пример контракта делегата (упрощённо)
interface AdapterDelegate<T> {
    fun isForViewType(items: List<T>, position: Int): Boolean
    fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
    fun onBindViewHolder(items: List<T>, position: Int, holder: RecyclerView.ViewHolder)
}

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

// В реальном адаптере регистрируются несколько делегатов, и каждый вызов
// getItemViewType / onCreateViewHolder / onBindViewHolder проксируется
// к подходящему делегату по isForViewType.
```

## Answer (EN)

**ViewTypes Theory:**
ViewTypes allow displaying different layouts in the same RecyclerView (headers, items, footers, ads). Proper implementation is critical for performance and maintainability of heterogeneous lists.

**Main components:**
- `getItemViewType(position)` - determines view type for a position; its result is used by the framework when calling `onCreateViewHolder(parent, viewType)`
- `onCreateViewHolder(parent, viewType)` - creates a `ViewHolder` based on the given type
- `onBindViewHolder(holder, position)` - binds data to the appropriate `ViewHolder`

```kotlin
// Basic adapter with multiple types (simplified example)
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
// In real-world code, prefer typed models (e.g., the sealed classes below) over List<Any> for better type safety.
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
Delegation allows separating logic for different item types into dedicated delegates, simplifying the main adapter.

```kotlin
// Example of a delegate contract (simplified)
interface AdapterDelegate<T> {
    fun isForViewType(items: List<T>, position: Int): Boolean
    fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder
    fun onBindViewHolder(items: List<T>, position: Int, holder: RecyclerView.ViewHolder)
}

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

// In a real adapter, multiple delegates are registered, and each call to
// getItemViewType / onCreateViewHolder / onBindViewHolder is routed
// to the appropriate delegate based on isForViewType.
```

---

## Дополнительные вопросы (RU)

- Как оптимизировать производительность при использовании нескольких типов `View`?
- В чем преимущества использования делегирования адаптера?
- Как эффективно обрабатывать изменения типов `View`?

## Follow-ups

- How do you optimize performance with multiple view types?
- What are the benefits of using adapter delegation?
- How do you handle view type changes efficiently?

## Ссылки (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Документация Android](https://developer.android.com/docs)

## References (EN)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Связанные вопросы (RU)

### Предпосылки / Концепции


### Предпосылки (Проще)
- [[q-android-app-components--android--easy]] - Компоненты приложения

### Связанные (Того же уровня)
- [[q-recyclerview-explained--android--medium]] - Объяснение RecyclerView

### Продвинутые (Сложнее)
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство Runtime

## Related Questions (EN)

### Prerequisites / Concepts


### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-recyclerview-explained--android--medium]] - RecyclerView explanation

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
