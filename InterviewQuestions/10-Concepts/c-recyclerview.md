---
id: ivc-20251030-140000
title: RecyclerView / RecyclerView
aliases: [Android RecyclerView, RecyclerView]
kind: concept
summary: Flexible view for displaying large datasets with view recycling and efficient scrolling
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, performance, recyclerview, ui]
date created: Thursday, October 30th 2025, 12:30:06 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

RecyclerView is a flexible Android view component designed for efficiently displaying large datasets. It uses the ViewHolder pattern to recycle views as they scroll off-screen, significantly reducing memory usage and improving performance. The architecture separates concerns through three key components: Adapter (data binding), ViewHolder (view caching), and LayoutManager (positioning logic).

**Core Principles**:
- **View Recycling**: Reuses view objects instead of creating new ones
- **Adapter Pattern**: Separates data from presentation logic
- **Flexible Layout**: Supports vertical, horizontal, grid, and custom layouts
- **Efficient Updates**: Uses DiffUtil for smart dataset change detection

# Сводка (RU)

RecyclerView — это гибкий компонент Android для эффективного отображения больших наборов данных. Использует паттерн ViewHolder для переиспользования представлений при прокрутке, значительно снижая потребление памяти и улучшая производительность. Архитектура разделяет ответственность через три ключевых компонента: Adapter (привязка данных), ViewHolder (кеширование представлений) и LayoutManager (логика позиционирования).

**Основные принципы**:
- **Переиспользование представлений**: Повторно использует объекты вместо создания новых
- **Паттерн Adapter**: Отделяет данные от логики отображения
- **Гибкая компоновка**: Поддерживает вертикальные, горизонтальные, сеточные и кастомные макеты
- **Эффективные обновления**: Использует DiffUtil для умного определения изменений в наборе данных

---

## Key Components

**Adapter**: Binds data to views and creates ViewHolders
**ViewHolder**: Holds references to item views for reuse
**LayoutManager**: Manages item positioning (Linear, Grid, Staggered)
**ItemDecoration**: Adds visual decorations (dividers, spacing)
**ItemAnimator**: Animates item changes

---

## Performance Considerations

**View Recycling**:
- Views are recycled as they scroll off-screen
- Reduces inflation overhead and memory allocations
- ViewHolder pattern eliminates expensive findViewById() calls

**Efficient Updates**:
- Use DiffUtil to calculate minimal changes between datasets
- Avoid notifyDataSetChanged() for partial updates
- Use specific notify methods: notifyItemInserted(), notifyItemChanged()

**Best Practices**:
- Cache expensive calculations in ViewHolder
- Use setHasFixedSize(true) when size doesn't change
- Set RecycledViewPool for nested RecyclerViews
- Avoid nested scrolling when possible

---

## Basic Implementation

**Kotlin Example**:

```kotlin
// Data class
data class Item(val id: Int, val title: String)

// ViewHolder
class ItemViewHolder(view: View) : RecyclerView.ViewHolder(view) {
    private val titleText: TextView = view.findViewById(R.id.titleText)

    fun bind(item: Item) {
        titleText.text = item.title
    }
}

// Adapter
class ItemAdapter(private val items: List<Item>) :
    RecyclerView.Adapter<ItemViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ItemViewHolder(view)
    }

    override fun onBindViewHolder(holder: ItemViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}

// Setup in Activity/Fragment
recyclerView.apply {
    layoutManager = LinearLayoutManager(context)
    adapter = ItemAdapter(itemList)
    setHasFixedSize(true) // Performance optimization
}
```

**Using DiffUtil for Updates**:

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size
    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos].id == newList[newPos].id
    }

    override fun areContentsTheSame(oldPos: Int, newPos: Int): Boolean {
        return oldList[oldPos] == newList[newPos]
    }
}

// Update adapter
fun updateItems(newItems: List<Item>) {
    val diffResult = DiffUtil.calculateDiff(ItemDiffCallback(items, newItems))
    items = newItems
    diffResult.dispatchUpdatesTo(this)
}
```

---

## Use Cases / Trade-offs

**When to Use**:
- Displaying lists, grids, or custom layouts with many items
- Need for smooth scrolling with large datasets
- Dynamic content that requires frequent updates
- Complex item layouts with multiple view types

**Alternatives**:
- ListView: Simpler but less flexible, deprecated for most use cases
- Compose LazyColumn/LazyRow: Modern declarative alternative
- ViewPager2: For horizontal paging (uses RecyclerView internally)

**Trade-offs**:
- More complex setup than ListView
- Requires understanding of ViewHolder pattern
- Initial learning curve for DiffUtil and ItemDecorations

---

## References

- [Official RecyclerView Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView)
- [RecyclerView Guide](https://developer.android.com/guide/topics/ui/layout/recyclerview)
- [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)
- [Best Practices for RecyclerView](https://developer.android.com/topic/performance/vitals/render)
