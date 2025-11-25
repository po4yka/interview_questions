---
id: android-329
title: RecyclerView / Компонент RecyclerView
aliases: [RecyclerView, Компонент RecyclerView]
topic: android
subtopics:
  - ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-recyclerview
  - q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy
  - q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy
  - q-recyclerview-itemdecoration-advanced--android--medium
  - q-what-is-diffutil-for--android--medium
  - q-what-layout-allows-overlapping-objects--android--easy
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/easy, layoutmanager, performance, recyclerview, ui, viewholder]

date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)
> Компонент RecyclerView

# Question (EN)
> RecyclerView

---

## Ответ (RU)
RecyclerView — это мощный компонент пользовательского интерфейса, изначально предоставляемый Android Support Library и в современных приложениях доступный как часть библиотек AndroidX. Он предназначен для отображения динамических списков и других коллекций элементов и был представлен как улучшенная и более гибкая замена ListView и GridView, обеспечивая лучшую производительность и большую гибкость при создании сложных макетов списков.

### Основные Особенности

#### 1. Эффективное Повторное Использование `View`

RecyclerView использует паттерн ViewHolder для эффективного повторного использования элементов при прокрутке. Это существенно повышает производительность для больших списков: создаётся ограниченное количество `View`, которые затем переиспользуются для новых элементов (часть представлений также может кешироваться вне экрана), вместо создания отдельной `View` для каждого элемента данных.

```kotlin
class MyViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)
```

#### 2. Гибкое Отображение Элементов

RecyclerView поддерживает различные компоновки (layout'ы): линейную, табличную (grid) и произвольные пользовательские, благодаря API LayoutManager. Это позволяет создавать вертикальные списки, горизонтальные списки и сетки.

```kotlin
// Линейный (вертикальный) список
recyclerView.layoutManager = LinearLayoutManager(context)

// Сетка
recyclerView.layoutManager = GridLayoutManager(context, 2)

// Горизонтальный список
recyclerView.layoutManager = LinearLayoutManager(
    context,
    LinearLayoutManager.HORIZONTAL,
    false
)
```

#### 3. Анимация Изменений

RecyclerView предоставляет встроенную поддержку анимаций (через ItemAnimator) для операций добавления, удаления и перемещения элементов, что позволяет создавать динамичные интерфейсы без ручной реализации базовых анимаций изменений элементов.

```kotlin
recyclerView.itemAnimator = DefaultItemAnimator()
```

#### 4. Декорации И Разделители

С помощью API ItemDecoration можно добавлять разделители между элементами и выполнять другие декоративные отрисовки и отступы.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Рисуем разделитель
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Обработка Нажатий

В отличие от ListView, RecyclerView не имеет встроенного слушателя кликов по элементам. Это дает больше гибкости: обработку нажатий обычно определяют во ViewHolder или адаптере, используя свои интерфейсы или лямбда-колбэки.

```kotlin
class MyAdapter(
    private val items: List<String>,
    private val onItemClick: (position: Int) -> Unit
) : RecyclerView.Adapter<MyAdapter.MyViewHolder>() {

    class MyViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.my_text_view, parent, false) as TextView
        return MyViewHolder(textView)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
        holder.itemView.setOnClickListener {
            onItemClick(holder.bindingAdapterPosition)
        }
    }

    override fun getItemCount(): Int = items.size
}
```

### Ключевые Компоненты

- Adapter: отвечает за создание ViewHolder и привязку данных к ним.
- LayoutManager: управляет расположением элементов и поведением прокрутки внутри RecyclerView.
- ViewHolder: содержит ссылки на view внутри элемента списка и переиспользуется адаптером для повышения производительности.

RecyclerView — это гибкий и производительный компонент для отображения коллекций данных, поддерживающий эффективное переиспользование `View`, различные компоновки, анимации и настраиваемые декорации, что делает его одним из базовых инструментов для создания современных интерфейсов Android.

---

## Answer (EN)
RecyclerView is a powerful UI component provided by the Android Support Library (historically) and by AndroidX in modern apps, designed for displaying dynamic lists (and other collections) of elements. It was introduced as an improved and more flexible replacement for ListView and GridView, providing better performance and greater flexibility in creating complex list layouts.

### Key Features

#### 1. Efficient `View` Recycling

RecyclerView uses the ViewHolder pattern for efficient view reuse when scrolling. This significantly improves performance for large lists since only a limited number of item views are created and then recycled as items scroll off-screen (with some extra views kept in caches), instead of allocating a new view for each data item.

```kotlin
class MyViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)
```

#### 2. Flexible Item Display

RecyclerView supports various layouts including linear, grid, and custom layouts via the LayoutManager API. This allows creating lists with different display structures including vertical lists, horizontal lists, and grids.

```kotlin
// Linear layout (vertical by default)
recyclerView.layoutManager = LinearLayoutManager(context)

// Grid layout
recyclerView.layoutManager = GridLayoutManager(context, 2)

// Horizontal layout
recyclerView.layoutManager = LinearLayoutManager(
    context,
    LinearLayoutManager.HORIZONTAL,
    false
)
```

#### 3. Change Animations

RecyclerView provides built-in support (via ItemAnimator) for animations for add, remove, and move operations, allowing creation of dynamic interfaces without manually implementing basic item change animations.

```kotlin
recyclerView.itemAnimator = DefaultItemAnimator()
```

#### 4. Decorations and Separators

Using the ItemDecoration API, you can add separators between items and apply other decorative drawing or offsets.

```kotlin
class DividerItemDecoration : RecyclerView.ItemDecoration() {
    override fun onDraw(c: Canvas, parent: RecyclerView, state: RecyclerView.State) {
        // Draw divider
    }
}

recyclerView.addItemDecoration(DividerItemDecoration())
```

#### 5. Click Event Handling

Unlike ListView, RecyclerView doesn't have a built-in item click listener API. This gives more flexibility: you typically define click handling inside the ViewHolder or adapter, using your own interfaces or lambdas.

```kotlin
class MyAdapter(
    private val items: List<String>,
    private val onItemClick: (position: Int) -> Unit
) : RecyclerView.Adapter<MyAdapter.MyViewHolder>() {

    class MyViewHolder(val textView: TextView) : RecyclerView.ViewHolder(textView)

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val textView = LayoutInflater.from(parent.context)
            .inflate(R.layout.my_text_view, parent, false) as TextView
        return MyViewHolder(textView)
    }

    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        holder.textView.text = items[position]
        holder.itemView.setOnClickListener {
            onItemClick(holder.bindingAdapterPosition)
        }
    }

    override fun getItemCount(): Int = items.size
}
```

### Key Components

- Adapter: Responsible for creating ViewHolders and binding data to them.
- LayoutManager: Manages item positioning and scrolling behavior within RecyclerView.
- ViewHolder: Holds references to item view subviews and is reused by the adapter to improve performance.

RecyclerView is a flexible and performant component for displaying data collections, supporting efficient view reuse, multiple layouts, animations, and custom decorations, making it a core tool for building modern Android UIs.

---

## Follow-ups

- [[c-recyclerview]]
- [[q-what-is-diffutil-for--android--medium]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

### Related (Medium)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Advanced (Harder)
- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui