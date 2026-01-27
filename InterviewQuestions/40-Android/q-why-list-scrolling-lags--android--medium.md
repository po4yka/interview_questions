---
id: android-104
title: Why List Scrolling Lags / Почему тормозит скроллинг списка
aliases:
- RecyclerView Performance
- Why List Scrolling Lags
- Почему тормозит скроллинг списка
topic: android
subtopics:
- performance-rendering
- threads-sync
- ui-views
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
created: 2025-10-13
updated: 2025-11-10
tags:
- android/performance-rendering
- android/threads-sync
- android/ui-views
- difficulty/medium
- optimization
- performance
- recyclerview
moc: moc-android
related:
- c-android-profiler
- q-android-app-lag-analysis--android--medium
- q-android-performance-measurement-tools--android--medium
sources: []
anki_cards:
- slug: android-104-0-en
  language: en
- slug: android-104-0-ru
  language: ru
---
# Вопрос (RU)

> Почему при скролле может тормозить список?

# Question (EN)

> Why might list scrolling lag?

---

## Ответ (RU)

Торможение списка происходит из-за проблем производительности в реализации `RecyclerView`. Основные причины (см. также [[c-android-view-system]], [[c-android-profiler]]):

### 1. Неправильное Использование ViewHolder

❌ **Плохо**: findViewById вызывается при каждом скролле

```kotlin
// Старый подход ListView
override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
    val view = convertView ?: layoutInflater.inflate(R.layout.item, parent, false)
    // findViewById при каждом скролле!
    val title = view.findViewById<TextView>(R.id.title)
    title.text = items[position].title
    return view
}
```

✅ **Хорошо**: `ViewHolder` кэширует ссылки

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.title) // Один раз
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.title.text = items[position].title // Только присвоение
    }
}
```

### 2. Тяжелые Операции В onBindViewHolder

❌ **Плохо**: Блокировка UI-потока

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Синхронная загрузка изображения
    val bitmap = BitmapFactory.decodeFile(items[position].imagePath)
    holder.image.setImageBitmap(bitmap)

    // Запрос к базе данных
    val count = database.getRelatedCount(items[position].id)
}
```

✅ **Хорошо**: Асинхронные операции

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Библиотека для изображений
    Glide.with(holder.itemView.context)
        .load(items[position].imagePath)
        .into(holder.image)

    // Предзагруженные данные
    holder.count.text = items[position].cachedCount.toString()
}
```

**Принцип**: `onBindViewHolder` должен только устанавливать данные, не вычислять их.

### 3. Неоптимизированная Обработка Изображений

✅ **Используйте библиотеки загрузки изображений**:

```kotlin
// Glide: автоматическое кэширование, изменение размера
Glide.with(context)
    .load(imageUrl)
    .override(200, 200)
    .centerCrop()
    .into(holder.image)
```

**Преимущества**: кэширование в памяти/на диске, управление жизненным циклом, оптимизация размера.

### 4. Сложные Иерархии Layout

❌ **Плохо**: Вложенность 5 уровней

```xml
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <LinearLayout>
                    <TextView />
                </LinearLayout>
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>
```

✅ **Хорошо**: Плоская структура `ConstraintLayout`

```xml
<ConstraintLayout>
    <ImageView android:id="@+id/image"
        app:layout_constraintStart_toStartOf="parent" />
    <TextView android:id="@+id/title"
        app:layout_constraintStart_toEndOf="@id/image" />
</ConstraintLayout>
```

### 5. Избыточные Вызовы notifyDataSetChanged()

❌ **Плохо**: Перерисовка всего списка

```kotlin
fun addItem(item: Item) {
    items = items + item
    notifyDataSetChanged() // Перерисовывает ВСЕ элементы!
}
```

✅ **Хорошо**: Точечные обновления

```kotlin
fun addItem(item: Item) {
    items = items + item
    notifyItemInserted(items.size - 1) // Только новый элемент
}
```

✅ **Лучше**: `ListAdapter` с `DiffUtil`

```kotlin
class MyAdapter : ListAdapter<Item, ViewHolder>(ItemDiffCallback()) {
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }
}

// Использование: DiffUtil автоматически
adapter.submitList(newItems)
```

### 6. Отсутствие Кэширования Данных

✅ **Repository pattern с кэшированием**:

```kotlin
class ItemRepository(private val api: ApiService, private val db: ItemDao) {
    fun getItems(): Flow<List<Item>> = db.getItemsFlow()
        .onStart { refreshFromNetwork() }

    private suspend fun refreshFromNetwork() {
        val items = api.getItems()
        db.insertAll(items) // Обновить кэш
    }
}
```

### Дополнительные Оптимизации

```kotlin
// Предзагрузка элементов
val layoutManager = LinearLayoutManager(context)
layoutManager.initialPrefetchItemCount = 4

// Фиксированный размер (если не меняется)
recyclerView.setHasFixedSize(true)

// Payload для частичных обновлений
override fun getChangePayload(old: Item, new: Item): Any? {
    return if (old.title != new.title) "TITLE_CHANGED" else null
}
```

---

## Answer (EN)

`List` scrolling lags due to **`RecyclerView` performance issues**. Main causes (see also [[c-android-view-system]], [[c-android-profiler]]):

### 1. Incorrect ViewHolder Usage

❌ **Bad**: findViewById called on every scroll

```kotlin
// Old ListView approach
override fun getView(position: Int, convertView: View?, parent: ViewGroup): View {
    val view = convertView ?: layoutInflater.inflate(R.layout.item, parent, false)
    // findViewById every time!
    val title = view.findViewById<TextView>(R.id.title)
    title.text = items[position].title
    return view
}
```

✅ **Good**: `ViewHolder` caches references

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val title: TextView = view.findViewById(R.id.title) // Once
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.title.text = items[position].title // Only assignment
    }
}
```

### 2. Heavy Operations in onBindViewHolder

❌ **Bad**: Blocking UI thread

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Synchronous image loading
    val bitmap = BitmapFactory.decodeFile(items[position].imagePath)
    holder.image.setImageBitmap(bitmap)

    // Database query
    val count = database.getRelatedCount(items[position].id)
}
```

✅ **Good**: Async operations

```kotlin
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    // Image loading library
    Glide.with(holder.itemView.context)
        .load(items[position].imagePath)
        .into(holder.image)

    // Pre-fetched data
    holder.count.text = items[position].cachedCount.toString()
}
```

**Principle**: `onBindViewHolder` should only set data, not compute it.

### 3. Unoptimized Image Handling

✅ Use image loading libraries:

```kotlin
// Glide: automatic caching, resizing
Glide.with(context)
    .load(imageUrl)
    .override(200, 200)
    .centerCrop()
    .into(holder.image)
```

**Benefits**: memory/disk caching, lifecycle management, size optimization.

### 4. Complex Layout Hierarchies

❌ **Bad**: 5-level nesting

```xml
<LinearLayout>
    <RelativeLayout>
        <LinearLayout>
            <FrameLayout>
                <LinearLayout>
                    <TextView />
                </LinearLayout>
            </FrameLayout>
        </LinearLayout>
    </RelativeLayout>
</LinearLayout>
```

✅ **Good**: Flat `ConstraintLayout` structure

```xml
<ConstraintLayout>
    <ImageView android:id="@+id/image"
        app:layout_constraintStart_toStartOf="parent" />
    <TextView android:id="@+id/title"
        app:layout_constraintStart_toEndOf="@id/image" />
</ConstraintLayout>
```

### 5. Excessive `notifyDataSetChanged()`

❌ **Bad**: Redraw entire list

```kotlin
fun addItem(item: Item) {
    items = items + item
    notifyDataSetChanged() // Redraws ALL items!
}
```

✅ **Good**: Granular updates

```kotlin
fun addItem(item: Item) {
    items = items + item
    notifyItemInserted(items.size - 1) // Only new item
}
```

✅ **Better**: `ListAdapter` with `DiffUtil`

```kotlin
class MyAdapter : ListAdapter<Item, ViewHolder>(ItemDiffCallback()) {
    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(old: Item, new: Item) = old.id == new.id
        override fun areContentsTheSame(old: Item, new: Item) = old == new
    }
}

// Usage: DiffUtil automatically applied
adapter.submitList(newItems)
```

### 6. Missing Data Caching

✅ Repository pattern with caching:

```kotlin
class ItemRepository(private val api: ApiService, private val db: ItemDao) {
    fun getItems(): Flow<List<Item>> = db.getItemsFlow()
        .onStart { refreshFromNetwork() }

    private suspend fun refreshFromNetwork() {
        val items = api.getItems()
        db.insertAll(items) // Update cache
    }
}
```

### Additional Optimizations

```kotlin
// Prefetch items
val layoutManager = LinearLayoutManager(context)
layoutManager.initialPrefetchItemCount = 4

// Fixed size (if unchanging)
recyclerView.setHasFixedSize(true)

// Payload for partial updates
override fun getChangePayload(old: Item, new: Item): Any? {
    return if (old.title != new.title) "TITLE_CHANGED" else null
}
```

---

## Дополнительные Вопросы (RU)

- Как внутренне работает механизм переиспользования `ViewHolder` в `RecyclerView`?
- В чем разница между RecycledViewPool и ViewCacheExtension?
- Как профилировать производительность `RecyclerView` с помощью Android Profiler?
- Когда стоит использовать AsyncListDiffer по сравнению с ListAdapter?
- Как `ConstraintLayout` улучшает производительность по сравнению с другими Layout?

## Follow-ups

- How does `RecyclerView`'s `ViewHolder` recycling mechanism work internally?
- What is the difference between RecycledViewPool and ViewCacheExtension?
- How can you profile `RecyclerView` performance using Android Profiler?
- When should you use AsyncListDiffer vs ListAdapter?
- How does `ConstraintLayout` improve performance compared to other layouts?

## Ссылки (RU)

- https://developer.android.com/topic/performance

## References

- https://developer.android.com/topic/performance

## Связанные Вопросы (RU)

### База (Easy)

- [[q-what-is-known-about-recyclerview--android--easy]] - основы `RecyclerView`
- [[q-recyclerview-sethasfixedsize--android--easy]] - оптимизация setHasFixedSize

### Связанные (Medium)

- [[q-recyclerview-explained--android--medium]] - подробное устройство `RecyclerView`
- [[q-recyclerview-diffutil-advanced--android--medium]] - продвинутое использование `DiffUtil`
- [[q-recyclerview-async-list-differ--android--medium]] - шаблоны использования AsyncListDiffer
- [[q-performance-optimization-android--android--medium]] - общая оптимизация производительности
- [[q-android-performance-measurement-tools--android--medium]] - инструменты профилирования производительности

### Продвинутое (Hard)

- [[q-compose-performance-optimization--android--hard]] - паттерны оптимизации производительности в Compose

## Related Questions

### Prerequisites (Easy)

- [[q-what-is-known-about-recyclerview--android--easy]] - `RecyclerView` basics
- [[q-recyclerview-sethasfixedsize--android--easy]] - setHasFixedSize optimization

### Related (Medium)

- [[q-recyclerview-explained--android--medium]] - `RecyclerView` deep dive
- [[q-recyclerview-diffutil-advanced--android--medium]] - `DiffUtil` advanced usage
- [[q-recyclerview-async-list-differ--android--medium]] - AsyncListDiffer patterns
- [[q-performance-optimization-android--android--medium]] - General performance optimization
- [[q-android-performance-measurement-tools--android--medium]] - Performance profiling tools

### Advanced (Hard)

- [[q-compose-performance-optimization--android--hard]] - Compose performance patterns
