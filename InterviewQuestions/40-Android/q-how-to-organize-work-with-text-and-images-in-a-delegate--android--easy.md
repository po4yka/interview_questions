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
---
# Вопрос (RU)

> Как организовать работу с текстом и картинками в делегате RecyclerView?

# Question (EN)

> How to organize work with text and images in a RecyclerView delegate?

---

## Ответ (RU)

Используйте подход с раздельными обработчиками (делегатами) для разных типов элементов (текст, изображения, комбинированные). Каждый делегат/`ViewHolder` отвечает за свой тип данных, что упрощает поддержку и расширение списка.

Можно реализовать:
- собственный multi-view-type `RecyclerView.Adapter` с отдельными `ViewHolder` для каждого типа
- или воспользоваться готовой библиотекой AdapterDelegates

**Подход**: Создать sealed class для типов данных, отдельные `ViewHolder` и делегаты для каждого типа.
**Преимущества**: Разделение ответственности, переиспользование, масштабируемость.

### Базовая Реализация (multi-view-type)

**Модели данных**:

```kotlin
sealed class ListItem

data class TextItem(val title: String, val description: String) : ListItem()
data class ImageItem(val imageUrl: String, val caption: String) : ListItem()
data class MixedItem(val title: String, val imageUrl: String) : ListItem()
```

**Адаптер с несколькими типами**:

```kotlin
class MultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items = mutableListOf<ListItem>()

    override fun getItemViewType(position: Int) = when (items[position]) {
        is TextItem -> TYPE_TEXT
        is ImageItem -> TYPE_IMAGE
        is MixedItem -> TYPE_MIXED
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder = when (viewType) {
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

Где `inflate` — это вспомогательная функция для `LayoutInflater.from(parent.context).inflate(...)`.

**ViewHolder с изображениями**:

```kotlin
class ImageViewHolder(private val binding: ItemImageBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(item: ImageItem) = with(binding) {
        caption.text = item.caption
        // Используйте Glide/Coil/Picasso для эффективной загрузки и кэширования
        Glide.with(root.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error_placeholder)
            .into(image)
    }
}
```

### Библиотека AdapterDelegates

Для более явного паттерна делегатов можно использовать библиотеку AdapterDelegates:

```kotlin
class TextDelegate : AdapterDelegate<List<ListItem>>() {

    override fun isForViewType(items: List<ListItem>, position: Int): Boolean =
        items[position] is TextItem

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder =
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
        delegatesManager
            .addDelegate(TextDelegate())
            .addDelegate(ImageDelegate())
            .addDelegate(MixedDelegate())
    }
}
```

**Преимущества**:
- Каждый делегат независим и переиспользуем
- Легко добавлять новые типы элементов
- Типобезопасность через sealed classes (и/или дженерики библиотеки)
- Упрощенное тестирование

## Answer (EN)

Use separate handlers (delegates) for different item types (text, images, mixed). Each delegate/`ViewHolder` is responsible for its own data type, which keeps the adapter clean and extensible.

You can either:
- implement a custom multi-view-type `RecyclerView.Adapter` with dedicated `ViewHolder`s, or
- use an external AdapterDelegates library.

**Approach**: Create a sealed class for data types and separate `ViewHolder`s/delegates for each type.
**Benefits**: Separation of concerns, reusability, scalability.

### Basic Implementation (multi-view-type)

**Data models**:

```kotlin
sealed class ListItem

data class TextItem(val title: String, val description: String) : ListItem()
data class ImageItem(val imageUrl: String, val caption: String) : ListItem()
data class MixedItem(val title: String, val imageUrl: String) : ListItem()
```

**Adapter with multiple view types**:

```kotlin
class MultiTypeAdapter : RecyclerView.Adapter<RecyclerView.ViewHolder>() {
    private val items = mutableListOf<ListItem>()

    override fun getItemViewType(position: Int) = when (items[position]) {
        is TextItem -> TYPE_TEXT
        is ImageItem -> TYPE_IMAGE
        is MixedItem -> TYPE_MIXED
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder = when (viewType) {
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

Here `inflate` is a helper around `LayoutInflater.from(parent.context).inflate(...)`.

**ViewHolder with images**:

```kotlin
class ImageViewHolder(private val binding: ItemImageBinding) :
    RecyclerView.ViewHolder(binding.root) {

    fun bind(item: ImageItem) = with(binding) {
        caption.text = item.caption
        // Use Glide/Coil/Picasso for efficient image loading and caching
        Glide.with(root.context)
            .load(item.imageUrl)
            .placeholder(R.drawable.placeholder)
            .error(R.drawable.error_placeholder)
            .into(image)
    }
}
```

### AdapterDelegates Library

For a more explicit delegates pattern, you can use the AdapterDelegates library:

```kotlin
class TextDelegate : AdapterDelegate<List<ListItem>>() {

    override fun isForViewType(items: List<ListItem>, position: Int): Boolean =
        items[position] is TextItem

    override fun onCreateViewHolder(parent: ViewGroup): RecyclerView.ViewHolder =
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
        delegatesManager
            .addDelegate(TextDelegate())
            .addDelegate(ImageDelegate())
            .addDelegate(MixedDelegate())
    }
}
```

**Benefits**:
- Each delegate is independent and reusable
- Easy to add new item types
- Type safety via sealed classes (and/or library generics)
- Simplified testing

---

## Дополнительные Вопросы (RU)

- Как обрабатывать клики для разных типов делегатов?
- Когда использовать `DiffUtil` с делегатами адаптера?
- Как оптимизировать загрузку изображений в `RecyclerView` с делегатами?
- Каковы альтернативы библиотеке AdapterDelegates?

## Follow-ups

- How to handle click events in different delegate types?
- When to use `DiffUtil` with adapter delegates?
- How to optimize image loading in `RecyclerView` with delegates?
- What are alternatives to the AdapterDelegates library?

## Ссылки (RU)

- [[c-recyclerview]]
- [[q-which-layout-for-large-list--android--easy]]
- Android RecyclerView documentation

## References

- [[c-recyclerview]]
- [[q-which-layout-for-large-list--android--easy]]
- Android RecyclerView documentation

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-which-layout-for-large-list--android--easy]]

### Связанные (того Же уровня)
- [[q-room-code-generation-timing--android--medium]]

### Продвинутые (сложнее)
- [[q-fakes-vs-mocks-testing--android--medium]]

## Related Questions

### Prerequisites (Easier)
- [[q-which-layout-for-large-list--android--easy]]

### Related (Same Level)
- [[q-room-code-generation-timing--android--medium]]

### Advanced (Harder)
- [[q-fakes-vs-mocks-testing--android--medium]]
