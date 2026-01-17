---\
id: android-079
title: List Items Problems / Проблемы с элементами списка
aliases: [List Items Problems, Проблемы с элементами списка]
topic: android
subtopics: [performance-memory, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-performance, c-recyclerview, q-how-to-create-list-like-recyclerview-in-compose--android--medium, q-list-elements-problems--android--medium, q-what-to-put-in-state-for-initial-list--android--easy]
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-memory, android/ui-views, difficulty/easy, listview, memory, performance, recyclerview]
anki_cards:
  - slug: android-079-0-en
    front: "What common problems occur with list items in Android?"
    back: |
      **1. OOM** - too many images, no view recycling
      **Solution:** RecyclerView + Glide/Coil with size limits

      **2. Slow scrolling** - heavy onBindViewHolder, deep layouts
      **Solution:** Keep binding light, flatten hierarchies

      **3. Data inconsistency** - wrong data after scroll
      **Solution:** DiffUtil/ListAdapter, bind all fields

      **4. Concurrency** - UI crashes from background updates
      **Solution:** Update adapter on main thread via LiveData/Flow

      **5. Click issues** - listeners not working or leaking
      **Solution:** Pass lambda to adapter, handle in ViewHolder
    tags:
      - android_layouts
      - difficulty::easy
  - slug: android-079-0-ru
    front: "Какие типичные проблемы возникают с элементами списка в Android?"
    back: |
      **1. OOM** - много изображений, нет переиспользования view
      **Решение:** RecyclerView + Glide/Coil с ограничением размера

      **2. Медленный скролл** - тяжёлый onBindViewHolder, глубокие layout
      **Решение:** Легкий binding, плоские иерархии

      **3. Несогласованность данных** - неправильные данные после скролла
      **Решение:** DiffUtil/ListAdapter, биндить все поля

      **4. Многопоточность** - краши UI от фоновых обновлений
      **Решение:** Обновлять адаптер на main через LiveData/Flow

      **5. Проблемы с кликами** - листенеры не работают или текут
      **Решение:** Передавать лямбду в адаптер, обрабатывать в ViewHolder
    tags:
      - android_layouts
      - difficulty::easy

---\
# Вопрос (RU)
> Проблемы с элементами списка

# Question (EN)
> `List` Items Problems

---

## Ответ (RU)
Проблемы с элементами списка в Android-приложениях могут быть разнообразными. Ниже перечислены основные типичные проблемы и способы их решения, с примерами.

### 1. Переполнение Памяти (Out of Memory)

**Проблема:** Списки с большим количеством элементов, особенно с изображениями, могут приводить к OOM.

**Причины:**
- Загрузка слишком большого количества изображений одновременно
- Неправильное переиспользование `View`
- Загрузка изображений в полном разрешении вместо миниатюр
- Утечки памяти в адаптерах

**Решение (пример с `RecyclerView` и Glide):**

```kotlin
// Используем RecyclerView вместо ListView
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    private val items: List<Item> = listOf() // пример источника данных

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val imageView: ImageView = itemView.findViewById(R.id.imageView)
        private val titleText: TextView = itemView.findViewById(R.id.titleText)

        fun bind(item: Item) {
            titleText.text = item.title

            // Используем библиотеку загрузки изображений с учётом памяти
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .placeholder(R.drawable.placeholder)
                .error(R.drawable.error)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .override(300, 300) // уменьшаем размер, не грузим полный размер
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

**Дополнительные оптимизации (подбирать по профилированию):**

```kotlin
// В настройке RecyclerView
recyclerView.apply {
    setHasFixedSize(true) // если размер элементов фиксирован
    // Конкретные значения подбираются по измерениям:
    // setItemViewCacheSize(20)
    // recycledViewPool.setMaxRecycledViews(0, 20)
}
```

Используйте Glide/Coil/Picasso, не храните долгоживущие ссылки на `View` или `Activity` в адаптере, доверяйте отмену загрузки самим библиотекам.

### 2. Медленная Прокрутка (Lagging)

**Проблема:** Дёрганная или медленная прокрутка списка.

**Причины:**
- Тяжёлые операции в `onBindViewHolder()` (парсинг, вычисления, I/O)
- Сложные и глубокие иерархии `View`
- Загрузка изображений или любая I/O-работа на главном потоке
- Отсутствие или некорректное переиспользование `View`

**Решение (облегчённый `onBindViewHolder`):**

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items: List<Item> = listOf()

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)

        fun bind(item: Item) {
            // Без тяжёлых операций в UI-потоке
            titleText.text = item.title
            descText.text = item.description

            // Асинхронная загрузка изображений
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // Держим метод лёгким
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

**Оптимизация разметки:**

```xml
<!-- Используем ConstraintLayout для уменьшения глубины иерархии where appropriate -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <ImageView
        android:id="@+id/image"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 3. Неправильное Отображение Данных (Data Inconsistency)

**Проблема:** Элементы показывают чужие данные, мигают или не обновляются.

**Причины:**
- Изменение списка без уведомления адаптера
- Многопоточное обновление без синхронизации
- Переиспользование `ViewHolder` без полного обновления всех полей

**Решение (`DiffUtil`):**

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size

    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }
}

class MyDiffAdapter : RecyclerView.Adapter<MyDiffAdapter.ViewHolder>() {
    private val items = mutableListOf<Item>()

    fun updateData(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items.clear()
        items.addAll(newItems)
        diffResult.dispatchUpdatesTo(this)
    }

    // ViewHolder и остальные методы...
}
```

**Использование ListAdapter (рекомендуется):**

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Безопасно биндим данные, не храним устаревшие ссылки
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Использование
adapter.submitList(newItems)
```

### 4. Проблемы Многопоточности (Concurrency Issues)

**Проблема:** Обновления данных из разных потоков могут вызывать краши или неконсистентный UI.

**Причины:**
- Обновление адаптера из фоновых потоков
- Гонки между UI и фоновыми операциями
- Обновление `RecyclerView` не с главного потока

**Решение (`ViewModel` + `LiveData`):**

```kotlin
class MyViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    fun loadItems() {
        viewModelScope.launch {
            val newItems = withContext(Dispatchers.IO) {
                repository.getItems()
            }
            _items.value = newItems // обновляем на главном потоке
        }
    }
}

class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    private val adapter = ModernAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        viewModel.items.observe(viewLifecycleOwner) { items ->
            adapter.submitList(items)
        }

        viewModel.loadItems()
    }
}
```

**Использование Kotlin `Flow` с учётом жизненного цикла:**

```kotlin
class FlowViewModel : ViewModel() {
    val items: Flow<List<Item>> = repository.itemsFlow
        .flowOn(Dispatchers.IO)
}

class FlowFragment : Fragment() {
    private val viewModel: FlowViewModel by viewModels()
    private val adapter = ModernAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.items.collect { items ->
                    adapter.submitList(items)
                }
            }
        }
    }
}
```

### 5. Проблемы С Обработкой Кликов

**Проблема:** Обработчики кликов не срабатывают или приводят к утечкам памяти.

**Причины:**
- Установка листенеров в `onBindViewHolder` без учёта переиспользования
- Хранение сильных ссылок на `Activity`/`Fragment` внутри `ViewHolder`

**Решение (передача лямбды в адаптер):**

```kotlin
class ClickableAdapter(
    private val onItemClick: (Item) -> Unit
) : ListAdapter<Item, ClickableAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(
        itemView: View,
        private val onItemClick: (Item) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {

        fun bind(item: Item) {
            itemView.setOnClickListener {
                onItemClick(item)
            }
            // Привязка остальных данных
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view, onItemClick)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// Использование
val adapter = ClickableAdapter { item ->
    navigateToDetail(item)
}
```

### 6. Неправильное Позиционирование Элементов

**Проблема:** Элементы "скачут", пропадают или отображаются не на своих местах при скролле.

**Причины:**
- Не все поля обновляются в `onBindViewHolder`
- Состояние `View` не сбрасывается при переиспользовании
- Отсутствие стабильных ID при анимациях или сложных обновлениях

**Решение (стабильные ID при необходимости):**

```kotlin
class StableAdapter(
    private val items: List<Item>
) : RecyclerView.Adapter<StableAdapter.ViewHolder>() {

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        // Используем стабильный Long ID из модели данных
        return items[position].id // предполагаем, что id уже стабильный Long
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Полностью обновляем состояние всех view, избегаем остатков
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

### Итог (RU)

Частые проблемы и решения:

1. OOM → `RecyclerView`, эффективная загрузка изображений (Glide/Coil/Picasso), отсутствие утечек.
2. Медленная прокрутка → Лёгкий `onBindViewHolder`, простая разметка, отсутствие тяжёлых операций на UI-потоке, корректное переиспользование `View`.
3. Некорректные данные → DiffUtil/ListAdapter, полное обновление полей в `bind`.
4. Многопоточность → Обновления адаптера только с главного потока через `LiveData`/`Flow`/`ViewModel`, коллекция `Flow` в `repeatOnLifecycle`.
5. Клики → Передача лямбды в адаптер, обработка во `ViewHolder` без утечек контекста.
6. Позиционирование → Полный rebinding состояния и стабильные ID при сложных обновлениях.

---

## Answer (EN)
Problems with list items in Android applications can be diverse. Let's examine some of the most common problems and their solutions.

### 1. Out of Memory (OOM)

**Problem:** Lists with a large number of elements can cause out of memory errors, especially when loading images.

**Causes:**
- Loading too many images simultaneously
- Not recycling views properly
- Loading full-resolution images when thumbnails would suffice
- Memory leaks in adapters

**Solution:**

```kotlin
// Use RecyclerView instead of ListView
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    private val items: List<Item> = listOf() // example data source

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val imageView: ImageView = itemView.findViewById(R.id.imageView)
        private val titleText: TextView = itemView.findViewById(R.id.titleText)

        fun bind(item: Item) {
            titleText.text = item.title

            // Use image loading library with memory management
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .placeholder(R.drawable.placeholder)
                .error(R.drawable.error)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .override(300, 300) // Resize images to avoid loading full-resolution
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

**Additional optimizations (tune per use case):**

```kotlin
// In RecyclerView setup
recyclerView.apply {
    setHasFixedSize(true) // If item size is fixed
    // The following values should be chosen based on profiling:
    // setItemViewCacheSize(20)
    // recycledViewPool.setMaxRecycledViews(0, 20)
}
```

Use libraries like Glide, Coil, or Picasso, ensure you cancel image requests on view reuse (handled by these libs), and avoid holding long-lived references to views or Activities in adapters.

### 2. Slow Scrolling (Lagging)

**Problem:** Scrolling can be slow due to long rendering time of elements.

**Causes:**
- Heavy operations in `onBindViewHolder()`
- Complex layouts with deep view hierarchies
- Loading images or doing I/O on the main thread
- Incorrect or missing view recycling

**Solution:**

```kotlin
class OptimizedAdapter : RecyclerView.Adapter<OptimizedAdapter.ViewHolder>() {

    private val items: List<Item> = listOf()

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val titleText: TextView = itemView.findViewById(R.id.title)
        private val descText: TextView = itemView.findViewById(R.id.description)
        private val imageView: ImageView = itemView.findViewById(R.id.image)

        fun bind(item: Item) {
            // Avoid heavy operations here
            titleText.text = item.title
            descText.text = item.description

            // Load images asynchronously
            Glide.with(itemView.context)
                .load(item.imageUrl)
                .into(imageView)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // Keep this method lightweight
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

**Layout optimization:**

```xml
<!-- Use ConstraintLayout to flatten view hierarchy where appropriate -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content">

    <ImageView
        android:id="@+id/image"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/title"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintStart_toEndOf="@id/image"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### 3. Data Inconsistency

**Problem:** If the adapter doesn't properly manage data updates, items may display incorrect data.

**Causes:**
- Not notifying adapter of data changes
- Modifying data while adapter is using it
- Race conditions in multi-threaded updates
- `ViewHolder` reuse showing stale data

**Solution (`DiffUtil`):**

```kotlin
class ItemDiffCallback(
    private val oldList: List<Item>,
    private val newList: List<Item>
) : DiffUtil.Callback() {

    override fun getOldListSize() = oldList.size

    override fun getNewListSize() = newList.size

    override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition].id == newList[newItemPosition].id
    }

    override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
        return oldList[oldItemPosition] == newList[newItemPosition]
    }
}

class MyDiffAdapter : RecyclerView.Adapter<MyDiffAdapter.ViewHolder>() {
    private val items = mutableListOf<Item>()

    fun updateData(newItems: List<Item>) {
        val diffCallback = ItemDiffCallback(items, newItems)
        val diffResult = DiffUtil.calculateDiff(diffCallback)

        items.clear()
        items.addAll(newItems)
        diffResult.dispatchUpdatesTo(this)
    }

    // ViewHolder and other required methods...
}
```

**Using ListAdapter (recommended):**

```kotlin
class ModernAdapter : ListAdapter<Item, ModernAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind data safely, avoid keeping stale references
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ItemDiffCallback : DiffUtil.ItemCallback<Item>() {
        override fun areItemsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Item, newItem: Item): Boolean {
            return oldItem == newItem
        }
    }
}

// Usage
adapter.submitList(newItems)
```

### 4. Concurrency Issues

**Problem:** Data updates from different threads without proper synchronization can cause crashes or inconsistent UI.

**Causes:**
- Updating adapter from background threads
- Race conditions between UI and background threads
- Not using main thread for `RecyclerView` updates

**Solution (`LiveData`):**

```kotlin
class MyViewModel : ViewModel() {
    private val _items = MutableLiveData<List<Item>>()
    val items: LiveData<List<Item>> = _items

    fun loadItems() {
        viewModelScope.launch {
            val newItems = withContext(Dispatchers.IO) {
                repository.getItems()
            }
            _items.value = newItems // main thread
        }
    }
}

class MyFragment : Fragment() {
    private val viewModel: MyViewModel by viewModels()
    private val adapter = ModernAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        viewModel.items.observe(viewLifecycleOwner) { items ->
            adapter.submitList(items)
        }

        viewModel.loadItems()
    }
}
```

**Using Kotlin `Flow` (scoped to `Lifecycle`):**

```kotlin
class FlowViewModel : ViewModel() {
    val items: Flow<List<Item>> = repository.itemsFlow
        .flowOn(Dispatchers.IO)
}

class FlowFragment : Fragment() {
    private val viewModel: FlowViewModel by viewModels()
    private val adapter = ModernAdapter()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        recyclerView.adapter = adapter

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.items.collect { items ->
                    adapter.submitList(items)
                }
            }
        }
    }
}
```

### 5. Item Click Issues

**Problem:** Click listeners not working correctly or causing memory leaks.

**Causes:**
- Setting listeners incorrectly in `onBindViewHolder` without considering reuse
- Holding strong references to `Activity`/`Fragment` inside `ViewHolder`

**Solution:**

```kotlin
class ClickableAdapter(
    private val onItemClick: (Item) -> Unit
) : ListAdapter<Item, ClickableAdapter.ViewHolder>(ItemDiffCallback()) {

    class ViewHolder(
        itemView: View,
        private val onItemClick: (Item) -> Unit
    ) : RecyclerView.ViewHolder(itemView) {

        fun bind(item: Item) {
            itemView.setOnClickListener {
                onItemClick(item)
            }
            // Bind other data
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view, onItemClick)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// Usage
val adapter = ClickableAdapter { item ->
    navigateToDetail(item)
}
```

### 6. Incorrect Item Positioning

**Problem:** Items appear in wrong positions or disappear after scrolling.

**Causes:**
- Not binding all required fields in `onBindViewHolder`
- Reusing views without resetting state
- Lack of stable IDs when using animations or complex updates

**Solution (use stable IDs when appropriate):**

```kotlin
class StableAdapter(
    private val items: List<Item>
) : RecyclerView.Adapter<StableAdapter.ViewHolder>() {

    init {
        setHasStableIds(true)
    }

    override fun getItemId(position: Int): Long {
        // Prefer a real stable Long ID from your data model.
        // Example: return items[position].stableId
        return items[position].id // assume id is already a stable Long
    }

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        fun bind(item: Item) {
            // Bind all stateful views to avoid leftover state
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }

    override fun getItemCount() = items.size
}
```

### Summary (EN)

Common problems and solutions:

1. Out of Memory → Use `RecyclerView`, efficient image loading (Glide/Coil/Picasso), avoid leaks.
2. Slow scrolling → Keep `onBindViewHolder` light, simplify layouts, avoid main-thread I/O, ensure proper view recycling.
3. Data inconsistency → Use DiffUtil/ListAdapter, bind all fields correctly.
4. Concurrency issues → Perform adapter updates on the main thread via `LiveData`/`Flow`/`ViewModel`, collect `Flow` with lifecycle-aware APIs.
5. Click issues → Use proper click listener patterns, avoid leaking contexts.
6. Positioning issues → Reset state on bind, and use stable IDs when needed.

---

## Follow-ups

- [[c-performance]] — How would you profile and measure list scrolling performance in a real project?
- [[c-recyclerview]] — Which `RecyclerView`-specific tools and patterns (e.g. `ListAdapter`, `ConcatAdapter`, `DiffUtil`) would you choose for large or heterogeneous lists and why?
- Как бы вы диагностировали редкие визуальные артефакты (мигание, скачущие элементы) в списке, используя инструменты профилирования и логи?

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

### Computer Science Fundamentals
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Kotlin Language Features
- [[q-array-vs-list-kotlin--kotlin--easy]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-list-vs-sequence--kotlin--medium]] - Data Structures

### Related Algorithms
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
