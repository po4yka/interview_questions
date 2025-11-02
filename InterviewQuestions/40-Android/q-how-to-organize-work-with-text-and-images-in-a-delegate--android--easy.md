---
id: android-349
title: "How To Organize Work With Text And Images In A Delegate / Как Организовать Работу С Текстом И Картинками В Делегате"
aliases: [Adapter Delegates, RecyclerView Delegates, Делегаты адаптера]
topic: android
subtopics: [ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-recyclerview, q-room-code-generation-timing--android--medium, q-which-layout-for-large-list--android--easy]
created: 2025-10-15
updated: 2025-10-31
sources: []
tags: [adapter, android/ui-views, delegates, difficulty/easy, recyclerview]
date created: Tuesday, October 28th 2025, 9:48:46 am
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

> Как организовать работу с текстом и картинками в делегате RecyclerView?

# Question (EN)

> How to organize work with text and images in a RecyclerView delegate?

---

## Ответ (RU)

Используйте **паттерн Adapter Delegates** для разделения логики отображения разных типов элементов (текст, изображения, комбинированные). Каждый делегат отвечает за свой тип данных.

**Подход**: Создать sealed class для типов данных, отдельные ViewHolder'ы и делегаты для каждого типа
**Преимущества**: Разделение ответственности, переиспользование, масштабируемость

### Базовая Реализация

**Модели данных**:

```kotlin
sealed class ListItem

data class TextItem(val title: String, val description: String) : ListItem()
data class ImageItem(val imageUrl: String, val caption: String) : ListItem()
data class MixedItem(val title: String, val imageUrl: String) : ListItem()
```

**Адаптер с делегатами**:

```kotlin
class MultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items = mutableListOf<ListItem>()

    override fun getItemViewType(position: Int) = when (items[position]) {
        is TextItem -> TYPE_TEXT
        is ImageItem -> TYPE_IMAGE
        is MixedItem -> TYPE_MIXED
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        TYPE_TEXT -> TextViewHolder(inflate(R.layout.item_text, parent))
        TYPE_IMAGE -> ImageViewHolder(inflate(R.layout.item_image, parent))
        TYPE_MIXED -> MixedViewHolder(inflate(R.layout.item_mixed, parent))
        else -> error("Unknown type")
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is TextItem -> (holder as TextViewHolder).bind(item)
            is ImageItem -> (holder as ImageViewHolder).bind(item)
            is MixedItem -> (holder as MixedViewHolder).bind(item)
        }
    }
}
```

**ViewHolder с изображениями**:

```kotlin
class ImageViewHolder(private val binding: ItemImageBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(item: ImageItem) = binding.apply {
        caption.text = item.caption
        // ✅ Используйте Glide/Coil для эффективной загрузки
        Glide.with(root.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .into(image)
    }
}
```

### Библиотека AdapterDelegates

Для сложных сценариев используйте готовое решение:

```kotlin
class TextDelegate : AdapterDelegate<List<ListItem>>() {
    override fun isForViewType(items: List<ListItem>, position: Int) =
        items[position] is TextItem

    override fun onCreateViewHolder(parent: ViewGroup) =
        TextViewHolder(inflate(R.layout.item_text, parent))

    override fun onBindViewHolder(
        items: List<ListItem>,
        position: Int,
        holder: RecyclerView.ViewHolder,
        payloads: List<Any>
    ) {
        (holder as TextViewHolder).bind(items[position] as TextItem)
    }
}

class DelegateAdapter : ListDelegationAdapter<List<ListItem>>() {
    init {
        delegatesManager.addDelegate(TextDelegate())
            .addDelegate(ImageDelegate())
            .addDelegate(MixedDelegate())
    }
}
```

**Преимущества**:
- Каждый делегат независим и переиспользуем
- Легко добавлять новые типы элементов
- Типобезопасность через sealed classes
- Упрощенное тестирование

## Answer (EN)

Use the **Adapter Delegates pattern** to separate display logic for different item types (text, images, combined). Each delegate handles one data type.

**Approach**: Create sealed class for data types, separate ViewHolders and delegates for each type
**Benefits**: Separation of concerns, reusability, scalability

### Basic Implementation

**Data models**:

```kotlin
sealed class ListItem

data class TextItem(val title: String, val description: String) : ListItem()
data class ImageItem(val imageUrl: String, val caption: String) : ListItem()
data class MixedItem(val title: String, val imageUrl: String) : ListItem()
```

**Adapter with delegates**:

```kotlin
class MultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items = mutableListOf<ListItem>()

    override fun getItemViewType(position: Int) = when (items[position]) {
        is TextItem -> TYPE_TEXT
        is ImageItem -> TYPE_IMAGE
        is MixedItem -> TYPE_MIXED
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        TYPE_TEXT -> TextViewHolder(inflate(R.layout.item_text, parent))
        TYPE_IMAGE -> ImageViewHolder(inflate(R.layout.item_image, parent))
        TYPE_MIXED -> MixedViewHolder(inflate(R.layout.item_mixed, parent))
        else -> error("Unknown type")
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = items[position]) {
            is TextItem -> (holder as TextViewHolder).bind(item)
            is ImageItem -> (holder as ImageViewHolder).bind(item)
            is MixedItem -> (holder as MixedViewHolder).bind(item)
        }
    }
}
```

**ViewHolder with images**:

```kotlin
class ImageViewHolder(private val binding: ItemImageBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(item: ImageItem) = binding.apply {
        caption.text = item.caption
        // ✅ Use Glide/Coil for efficient loading
        Glide.with(root.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .into(image)
    }
}
```

### AdapterDelegates Library

For complex scenarios, use the library:

```kotlin
class TextDelegate : AdapterDelegate<List<ListItem>>() {
    override fun isForViewType(items: List<ListItem>, position: Int) =
        items[position] is TextItem

    override fun onCreateViewHolder(parent: ViewGroup) =
        TextViewHolder(inflate(R.layout.item_text, parent))

    override fun onBindViewHolder(
        items: List<ListItem>,
        position: Int,
        holder: RecyclerView.ViewHolder,
        payloads: List<Any>
    ) {
        (holder as TextViewHolder).bind(items[position] as TextItem)
    }
}

class DelegateAdapter : ListDelegationAdapter<List<ListItem>>() {
    init {
        delegatesManager.addDelegate(TextDelegate())
            .addDelegate(ImageDelegate())
            .addDelegate(MixedDelegate())
    }
}
```

**Benefits**:
- Each delegate is independent and reusable
- Easy to add new item types
- Type safety through sealed classes
- Simplified testing

---

## Follow-ups

- How to handle click events in different delegate types?
- When to use DiffUtil with adapter delegates?
- How to optimize image loading in RecyclerView with delegates?
- What are alternatives to the AdapterDelegates library?

## References

- [[c-recyclerview]]
- [[q-which-layout-for-large-list--android--easy]]
- Android RecyclerView documentation

## Related Questions

### Prerequisites (Easier)
- [[q-which-layout-for-large-list--android--easy]]

### Related (Same Level)
- [[q-room-code-generation-timing--android--medium]]

### Advanced (Harder)
- [[q-fakes-vs-mocks-testing--android--medium]]
