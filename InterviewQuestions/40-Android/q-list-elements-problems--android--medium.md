---\
id: android-100
title: "List Elements Problems / Проблемы элементов списка"
aliases: ["List Elements Problems", "RecyclerView Issues", "Проблемы RecyclerView", "Проблемы элементов списка"]
topic: android
subtopics: [performance-memory, performance-rendering, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-11
tags: [android/performance-memory, android/performance-rendering, android/ui-views, concurrency, difficulty/medium, diffutil, memory, recyclerview]
moc: moc-android
related: [c-android, q-android-app-components--android--easy, q-android-lint-tool--android--medium]
sources: []

---\
# Вопрос (RU)

> Какие могут быть проблемы с элементами списка в Android и как их решать?

# Question (EN)

> What problems can occur with list elements in Android and how to solve them?

---

## Ответ (RU)

Элементы списка в Android приложениях сталкиваются с четырьмя основными категориями проблем: **память**, **производительность**, **консистентность данных** и **многопоточность**.

### 1. Out of Memory (OOM)

**Проблема:** Большие изображения или отсутствие корректного переиспользования / масштабирования `View` и битмапов приводят к переполнению памяти.

**Симптомы:**
```java
java.lang.OutOfMemoryError: Failed to allocate a 12345678 byte allocation
```

**Причины:**
```kotlin
// ❌ BAD - Загрузка полноразмерных изображений на UI-потоке без масштабирования
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val bitmap = BitmapFactory.decodeFile(photos[position].path) // 4K image!
    holder.imageView.setImageBitmap(bitmap) // Высокий расход памяти, риск OOM
}
```

**Решение:** `RecyclerView` (или корректно настроенный ListView) + библиотеки изображений
```kotlin
// ✅ GOOD - Glide управляет памятью и кэшем
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    Glide.with(holder.itemView.context)
        .load(photos[position].path)
        .override(400, 400) // Resize до фактического размера отображения
        .centerCrop()
        .into(holder.binding.imageView)
}
```

**Преимущества:**
- RecyclerView/Adapter используют переиспользование `ViewHolder`, снижая число аллокаций
- Glide/Coil автоматически изменяют размер изображений и переиспользуют ресурсы
- Memory + disk cache предотвращают повторную загрузку
- `Lifecycle` awareness помогает корректно освобождать память

### 2. Медленная Прокрутка

**Проблема:** Прокрутка зависает из-за тяжелых операций в `onBindViewHolder`.

**Причины:**
```kotlin
// ❌ BAD - Тяжелые операции при биндинге
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // Сложные вычисления
    val processedText = item.text.split(" ").map { it.uppercase() }.joinToString(" ")

    // Синхронный сетевой запрос - БЛОКИРУЕТ UI!
    val response = api.getUserDetails(item.userId).execute()

    // Синхронный запрос к БД - БЛОКИРУЕТ UI!
    val count = database.getCommentCount(item.id)
}
```

**Решение:** Предобработка данных вне адаптера (`ViewModel`/Repository, фоновые потоки)
```kotlin
// ✅ GOOD - Обработка в ViewModel/Repository
class ItemViewModel(private val repository: ItemRepository) : ViewModel() {
    val items: LiveData<List<ProcessedItem>> = repository.getItems()
        .map { rawItems ->
            rawItems.map { item ->
                ProcessedItem(
                    id = item.id,
                    processedText = item.text.uppercase(), // Предварительно обработано
                    userName = item.userName, // Уже получено/вычислено
                    commentCount = item.commentCount // Уже посчитано
                )
            }
        }
        .asLiveData() // Обработка может выполняться в нужном диспетчере внутри репозитория
}

// Простой биндинг - только установка уже подготовленных данных
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = getItem(position)
    holder.binding.apply {
        textView.text = item.processedText
        userName.text = item.userName
    }
}
```

**Паттерн:** Prepare data → Bind data (не "Bind data → Process data").

### 3. Несогласованность Данных

**Проблема:** `Adapter` показывает неверные или устаревшие данные.

**Причины:**
```kotlin
// ❌ BAD - Прямое изменение списка без корректного notify
fun addItem(item: Item) {
    items.add(item)
    // Забыли notify!
}

fun updateItem(position: Int, item: Item) {
    items[position] = item
    notifyDataSetChanged() // Неэффективно, нет точечных обновлений
}
```

**Решение:** `DiffUtil` для точных обновлений
```kotlin
// ✅ GOOD - ListAdapter с DiffUtil
class ItemAdapter : ListAdapter<Item, ViewHolder>(ItemDiffCallback()) {

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }
}

// Использование - DiffUtil вычисляет изменения автоматически
adapter.submitList(newItems)
```

**Преимущества:**
- Автоматический расчет diff (обновляются только измененные элементы)
- Плавные анимации вставок/удалений
- Корректная работа с положениями элементов и их состоянием
- Более безопасный API (нельзя напрямую изменять внутренний список ListAdapter)

### 4. Проблемы Многопоточности

**Проблема:** Обновление данных из нескольких потоков вызывает crashes.

**Симптомы:**
```java
java.lang.IndexOutOfBoundsException: Index: 5, Size: 3
java.util.ConcurrentModificationException
android.view.ViewRootImpl$CalledFromWrongThreadException
```

**Причины:**
```kotlin
// ❌ BAD - Обновление из background-потока
fun loadDataInBackground() {
    Thread {
        val newItems = api.fetchItems()
        items.clear() // Изменение коллекции из background!
        items.addAll(newItems)
        notifyDataSetChanged() // Вызов из background! Потенциальный CRASH!
    }.start()
}
```

**Решение:** `LiveData`/`Flow` с учетом lifecycle и правильными диспетчерами
```kotlin
// ✅ GOOD - ViewModel - фоновая работа здесь
class ItemViewModel(private val repository: ItemRepository) : ViewModel() {
    // repository.getItems() возвращает Flow<List<Item>> или другой асинхронный источник,
    // тяжелая работа должна выполняться вне main thread
    val items: LiveData<List<Item>> = repository.getItems()
        .asLiveData() // Наблюдатели LiveData вызываются на main thread

    // Или через Flow для более гибкой обработки
    val itemsFlow: Flow<List<Item>> = repository.getItemsFlow()
        .flowOn(Dispatchers.IO) // upstream на IO, collect { submitList(...) } вызывать на main thread
}

// Fragment - observe на main-потоке
viewModel.items.observe(viewLifecycleOwner) { items ->
    adapter.submitList(items) // Вызывается на main thread
}
```

**Преимущества:**
- Доставка обновлений UI на main thread
- `Lifecycle`-aware (меньше утечек памяти, корректная отписка)
- Меньше шансов получить concurrent modification за счет единого потока обновлений

### Лучшие Практики

**Stable IDs для предотвращения проблем с кликами и переиспользованием:**
```kotlin
// Для обычного RecyclerView.Adapter с собственным списком
class ItemAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val items: List<Item> = listOf()

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long = items[position].id.toLong()
}
```

(В реальном адаптере необходимо гарантировать стабильность ID между обновлениями данных и вызывать соответствующие `notify*` методы. При использовании `ListAdapter` stable IDs должны вычисляться на основе `getItem(position)`, без прямой модификации внутреннего списка.)

**Безопасная обработка кликов:**
```kotlin
// ✅ GOOD - Используем bindingAdapterPosition
holder.itemView.setOnClickListener {
    val position = holder.bindingAdapterPosition
    if (position != RecyclerView.NO_POSITION) {
        onClick(getItem(position))
    }
}
```

**Предотвращение утечек памяти:**
```kotlin
override fun onViewRecycled(holder: ViewHolder) {
    super.onViewRecycled(holder)
    holder.binding.root.setOnClickListener(null)
    Glide.with(holder.itemView.context).clear(holder.binding.imageView)
}
```

Также см. официальные рекомендации по `RecyclerView` и `DiffUtil` для более глубокого понимания, а также [[c-android]] для общего контекста платформы.

### Таблица Решений

| Проблема | Причина | Решение |
|---------|---------|---------|
| Out of Memory | Большие изображения, некорректное использование битмапов, нет recycling/масштабирования | RecyclerView/ListView с переиспользованием view + Glide/Coil |
| Медленная прокрутка | Тяжелые операции в onBindViewHolder | Предобработка данных, вынос тяжелой работы в `ViewModel`/Repository |
| Несогласованность | Неправильные adapter updates | `DiffUtil`, ListAdapter |
| Многопоточность | Multi-threaded updates без синхронизации/обновлений на main | `LiveData`, `Flow` (обновления UI на main thread) |
| Утечки памяти | Удержание ссылок на `Activity`/`Context`, ресурсы не очищаются | ViewBinding, lifecycle components, очистка в onViewRecycled/onViewDetached |
| Неверные клики | Position меняется async | Stable IDs (при необходимости), item callbacks с bindingAdapterPosition |

---

## Answer (EN)

`List` elements in Android applications face four main categories of problems: **memory**, **performance**, **data consistency**, and **concurrency**.

### 1. Out of Memory (OOM)

**Problem:** Large images or incorrect view/bitmap usage (no scaling/reuse) cause excessive memory usage and OOM.

**Symptoms:**
```java
java.lang.OutOfMemoryError: Failed to allocate a 12345678 byte allocation
```

**Causes:**
```kotlin
// ❌ BAD - Loading full-resolution images on the UI thread without downscaling
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val bitmap = BitmapFactory.decodeFile(photos[position].path) // 4K image!
    holder.imageView.setImageBitmap(bitmap) // High memory usage, OOM risk
}
```

**Solution:** `RecyclerView` (or properly configured ListView) + image loading libraries
```kotlin
// ✅ GOOD - Glide manages memory and caching
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    Glide.with(holder.itemView.context)
        .load(photos[position].path)
        .override(400, 400) // Resize to actual display size
        .centerCrop()
        .into(holder.binding.imageView)
}
```

**Benefits:**
- RecyclerView/Adapter use `ViewHolder` recycling, reducing allocations
- Glide/Coil automatically resize images and reuse resources
- Memory + disk cache prevent redundant loading
- `Lifecycle` awareness helps free memory correctly

### 2. Lagging Scrolling

**Problem:** Scroll stutters due to heavy operations in `onBindViewHolder`.

**Causes:**
```kotlin
// ❌ BAD - Heavy operations during binding
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = items[position]

    // Complex calculations
    val processedText = item.text.split(" ").map { it.uppercase() }.joinToString(" ")

    // Synchronous network request - BLOCKS UI!
    val response = api.getUserDetails(item.userId).execute()

    // Synchronous database query - BLOCKS UI!
    val count = database.getCommentCount(item.id)
}
```

**Solution:** Pre-process data outside the adapter (`ViewModel`/Repository, background threads)
```kotlin
// ✅ GOOD - Processing in ViewModel/Repository
class ItemViewModel(private val repository: ItemRepository) : ViewModel() {
    val items: LiveData<List<ProcessedItem>> = repository.getItems()
        .map { rawItems ->
            rawItems.map { item ->
                ProcessedItem(
                    id = item.id,
                    processedText = item.text.uppercase(), // Pre-processed
                    userName = item.userName, // Already fetched/derived
                    commentCount = item.commentCount // Already counted
                )
            }
        }
        .asLiveData() // Heavy work should be dispatched appropriately inside repository/Flow
}

// Simple binding - only setting prepared data
override fun onBindViewHolder(holder: ViewHolder, position: Int) {
    val item = getItem(position)
    holder.binding.apply {
        textView.text = item.processedText
        userName.text = item.userName
    }
}
```

**Pattern:** Prepare data → Bind data (not "Bind data → Process data").

### 3. Data Inconsistency

**Problem:** `Adapter` displays wrong or outdated data.

**Causes:**
```kotlin
// ❌ BAD - Direct list modification without proper notifications
fun addItem(item: Item) {
    items.add(item)
    // Forgot to notify!
}

fun updateItem(position: Int, item: Item) {
    items[position] = item
    notifyDataSetChanged() // Inefficient, no granular updates
}
```

**Solution:** `DiffUtil` for accurate updates
```kotlin
// ✅ GOOD - ListAdapter with DiffUtil
class ItemAdapter : ListAdapter<Item, ViewHolder>(ItemDiffCallback()) {

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item) =
            oldItem.id == newItem.id

        override fun areContentsTheSame(oldItem: Item, newItem: Item) =
            oldItem == newItem
    }
}

// Usage - DiffUtil calculates changes automatically
adapter.submitList(newItems)
```

**Benefits:**
- Automatic diff calculation (only changed items updated)
- Smooth animations for insertions/deletions
- Correct handling of item positions and state
- Safer API (cannot directly mutate ListAdapter's internal list)

### 4. Concurrency Issues

**Problem:** Multi-threaded data updates cause crashes.

**Symptoms:**
```java
java.lang.IndexOutOfBoundsException: Index: 5, Size: 3
java.util.ConcurrentModificationException
android.view.ViewRootImpl$CalledFromWrongThreadException
```

**Causes:**
```kotlin
// ❌ BAD - Updating from background thread
fun loadDataInBackground() {
    Thread {
        val newItems = api.fetchItems()
        items.clear() // Modifying collection from background!
        items.addAll(newItems)
        notifyDataSetChanged() // Called from background! Potential CRASH!
    }.start()
}
```

**Solution:** `LiveData`/`Flow` with lifecycle awareness and proper dispatchers
```kotlin
// ✅ GOOD - ViewModel - background work here
class ItemViewModel(private val repository: ItemRepository) : ViewModel() {
    // repository.getItems() returns Flow<List<Item>> or another async source;
    // heavy work must run off the main thread
    val items: LiveData<List<Item>> = repository.getItems()
        .asLiveData() // LiveData observers are notified on the main thread

    // Or using Flow for more flexibility
    val itemsFlow: Flow<List<List<Item>>> = repository.getItemsFlow()
        .flowOn(Dispatchers.IO) // upstream on IO; collect { submitList(...) } on main thread
}

// Fragment - observes on main thread
viewModel.items.observe(viewLifecycleOwner) { items ->
    adapter.submitList(items) // Called on main thread
}
```

**Benefits:**
- UI updates dispatched on the main thread
- `Lifecycle`-aware (fewer memory leaks, proper unsubscribing)
- Reduced risk of concurrent modification via a single source of truth

### Best Practices

**Stable IDs to prevent click/reuse issues:**
```kotlin
// For a regular RecyclerView.Adapter with its own list
class ItemAdapter : RecyclerView.Adapter<ViewHolder>() {

    private val items: List<Item> = listOf()

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long = items[position].id.toLong()
}
```

(In a real adapter, you must ensure IDs remain stable across data updates and call appropriate `notify*` methods. When using `ListAdapter`, stable IDs should be based on `getItem(position)`, and you must not mutate the internal list directly.)

**Safe click handling:**
```kotlin
// ✅ GOOD - Use bindingAdapterPosition
holder.itemView.setOnClickListener {
    val position = holder.bindingAdapterPosition
    if (position != RecyclerView.NO_POSITION) {
        onClick(getItem(position))
    }
}
```

**Prevent memory leaks:**
```kotlin
override fun onViewRecycled(holder: ViewHolder) {
    super.onViewRecycled(holder)
    holder.binding.root.setOnClickListener(null)
    Glide.with(holder.itemView.context).clear(holder.binding.imageView)
}
```

Also see official `RecyclerView` and `DiffUtil` documentation for more details, as well as [[c-android]] for general Android platform context.

### Solution Table

| Problem | Cause | Solution |
|---------|-------|----------|
| Out of Memory | Large images, incorrect bitmap usage, no recycling/downscaling | RecyclerView/ListView with view recycling + Glide/Coil |
| Lagging scroll | Heavy operations in onBindViewHolder | Pre-process data, move heavy work to `ViewModel`/Repository |
| Data inconsistency | Incorrect adapter updates | `DiffUtil`, ListAdapter |
| Concurrency | Multi-threaded updates without proper main-thread dispatch | `LiveData`, `Flow` (UI updates on main thread) |
| Memory leaks | Holding `Activity`/`Context` references, not clearing resources | ViewBinding, lifecycle components, cleanup in onViewRecycled/onViewDetached |
| Wrong clicks | Position changes async | Stable IDs (when needed), item callbacks with bindingAdapterPosition |

---

## Follow-ups

1. How does `RecyclerView`'s `ViewHolder` pattern reduce memory allocations compared to `ListView`?
2. When should you use `notifyItemChanged(position)` vs `submitList()` with a `DiffUtil`-backed `ListAdapter`?
3. What's the difference between `DiffUtil.ItemCallback` methods `areItemsTheSame()` and `areContentsTheSame()` and how does this influence item change animations?
4. How can you detect and fix ANR ("`Application` Not Responding") issues caused by heavy work inside `onBindViewHolder` or other adapter callbacks?
5. How would you design a `ViewModel` + `Flow` pipeline to safely update a paginated `RecyclerView` from multiple data sources (e.g., network + cache)?

## References

- Official: [RecyclerView Best Practices](https://developer.android.com/develop/ui/views/layout/recyclerview)
- Official: [DiffUtil Documentation](https://developer.android.com/reference/androidx/recyclerview/widget/DiffUtil)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android app components basics

### Related (Same Level)
- [[q-android-lint-tool--android--medium]] - Static analysis for Android

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]] - Performance tools for Android
