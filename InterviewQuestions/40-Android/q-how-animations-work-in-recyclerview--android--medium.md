---
id: android-201
title: How Animations Work In RecyclerView / Как работают анимации в RecyclerView
aliases: [How Animations Work In RecyclerView, Как работают анимации в RecyclerView]
topic: android
subtopics: [ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-broadcastreceiver-contentprovider--android--easy, q-compose-custom-animations--android--medium, q-how-does-jetpackcompose-work--android--medium, q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--android--easy, q-save-data-outside-fragment--android--medium, q-spannable-text-styling--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-animation, animations, difficulty/medium, recyclerview]

---
# Вопрос (RU)
> Как работают анимации в RecyclerView

# Question (EN)
> How Animations Work In RecyclerView

---

## Ответ (RU)

RecyclerView предоставляет несколько способов реализации анимаций: от простых встроенных до сложных кастомных. Анимации можно применять на разных уровнях: на уровне элементов, адаптера и через пользовательские `ItemAnimator`.

Ключевые механизмы:
- `ItemAnimator`: отвечает за анимации добавления/удаления/перемещения/изменения при уведомлениях адаптера.
- Анимации во время биндинга (`onBindViewHolder`) и property-анимации: управляют тем, как появляются и меняются `View` при привязке данных (RecyclerView не использует стандартные `LayoutAnimation` для дочерних элементов, поэтому анимации делаются через `ItemAnimator` и анимации свойств).
- `ItemTouchHelper` и shared element transitions: для анимаций взаимодействия (свайпы/drag) и переходов между экранами.

### 1. Использование DefaultItemAnimator

Самый простой подход — использовать встроенный `DefaultItemAnimator` (часто включён по умолчанию):

```kotlin
val recyclerView: RecyclerView = findViewById(R.id.recyclerView)
recyclerView.itemAnimator = DefaultItemAnimator()

// Настройка длительности анимаций
(recyclerView.itemAnimator as? DefaultItemAnimator)?.apply {
    addDuration = 300
    removeDuration = 300
    moveDuration = 300
    changeDuration = 300
}
```

### 2. Пользовательский ItemAnimator (концептуально)

Можно создать кастомный `ItemAnimator`, унаследовавшись от `SimpleItemAnimator` или `DefaultItemAnimator`. Корректная реализация должна:
- Переопределять `animateAdd`/`animateRemove`/`animateMove`/`animateChange` по необходимости.
- Вызывать `dispatchAddStarting`/`dispatchAddFinished` и аналогичные методы в нужные моменты.
- Управлять и отменять анимации в `endAnimation`/`endAnimations`.
- Возвращать `true` только при реальном запуске анимации.
- В конечном итоге вызывать `dispatchAnimationFinished(holder)` (напрямую или через базовую реализацию), чтобы RecyclerView знал об окончании анимации.

Упрощённый пример анимации появления (для иллюстрации, без полной реализации всех методов и служебной логики управления списками pending/running):

```kotlin
class FadeInItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        view.alpha = 0f

        view.animate()
            .alpha(1f)
            .setDuration(addDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // В полноценной реализации нужно также убедиться,
                    // что вызвано dispatchAnimationFinished(holder)
                    // и holder удалён из внутренних коллекций анимаций.
                }
            })
            .start()

        return true
    }
}
```

### 3. Анимации В Адаптере (onBindViewHolder)

Можно анимировать элементы напрямую при биндинге, но важно учитывать переиспользование `View`, чтобы не оставлять некорректные состояния.

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.itemView.clearAnimation()
        holder.textView.text = items[position]

        // Пример анимации появления (упрощённый, без проверки "уже анимировано")
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .start()
    }

    override fun onViewRecycled(holder: ViewHolder) {
        holder.itemView.clearAnimation()
        holder.itemView.alpha = 1f
        super.onViewRecycled(holder)
    }

    // Другие методы адаптера опущены для краткости
}
```

### 4. Анимация Масштабирования Через ItemAnimator

```kotlin
class ScaleItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        view.scaleX = 0.5f
        view.scaleY = 0.5f
        view.alpha = 0f

        view.animate()
            .scaleX(1f)
            .scaleY(1f)
            .alpha(1f)
            .setDuration(addDuration)
            .setInterpolator(OvershootInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.scaleX = 1f
                    view.scaleY = 1f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // Аналогично, в полной реализации нужно уведомить о завершении
                    // анимации через инфраструктуру ItemAnimator.
                }
            })
            .start()

        return true
    }
}
```

### 5. Анимация Слайдом Через ItemAnimator

```kotlin
class SlideInLeftAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        // В упрощённом примере используем width; на практике важно учитывать,
        // что при старте анимации элемент должен быть уже измерен/размещён.
        view.translationX = -view.width.toFloat()
        view.alpha = 0f

        view.animate()
            .translationX(0f)
            .alpha(1f)
            .setDuration(addDuration)
            .setInterpolator(DecelerateInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                }
            })
            .start()

        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()

        view.animate()
            .translationX(view.width.toFloat())
            .alpha(0f)
            .setDuration(removeDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchRemoveStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()

        return true
    }
}
```

(Полная реализация должна также корректно обрабатывать pending/running анимации и вызывать соответствующие методы завершения.)

### 6. Использование Сторонних Библиотек

Можно использовать библиотеки (например, RecyclerView Animators) для готовых анимаций элементов:

```kotlin
// Пример использования (подключение зависимости не показано)
recyclerView.itemAnimator = SlideInUpAnimator()
// или
recyclerView.itemAnimator = FadeInAnimator()
// или
recyclerView.itemAnimator = ScaleInAnimator()
```

### 7. Специфичные Анимации Элементов В Адаптере

Анимирование только впервые появляющихся элементов:

```kotlin
class AnimatedAdapter(private val items: MutableList<String>) :
    RecyclerView.Adapter<AnimatedAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(text: String) {
            (itemView as? TextView)?.text = text
        }
    }

    private var lastPosition = -1

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.itemView.clearAnimation()
        holder.bind(items[position])

        if (position > lastPosition) {
            animateItem(holder.itemView, position)
            lastPosition = position
        }
    }

    private fun animateItem(view: View, position: Int) {
        view.translationY = 200f
        view.alpha = 0f

        view.animate()
            .translationY(0f)
            .alpha(1f)
            .setDuration(300)
            .setStartDelay((position * 50).toLong())
            .setInterpolator(DecelerateInterpolator())
            .start()
    }

    override fun onViewRecycled(holder: ViewHolder) {
        holder.itemView.clearAnimation()
        holder.itemView.alpha = 1f
        holder.itemView.translationY = 0f
        super.onViewRecycled(holder)
    }

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }
}
```

### 8. Shared Element Transitions

Для перехода от элемента `RecyclerView` к экрану деталей можно использовать shared element transitions:

```kotlin
class Item(val id: Long)

class MyAdapter(private val items: List<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imageView: ImageView = view.findViewById(R.id.imageView)

        fun bind(item: Item, clickListener: (View, Item) -> Unit) {
            ViewCompat.setTransitionName(imageView, "image_${item.id}")
            itemView.setOnClickListener { clickListener(imageView, item) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position]) { sharedView, item ->
            val context = sharedView.context
            val intent = Intent(context, DetailActivity::class.java)

            val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
                context as Activity,
                sharedView,
                ViewCompat.getTransitionName(sharedView) ?: ""
            )

            context.startActivity(intent, options.toBundle())
        }
    }

    override fun getItemCount(): Int = items.size
}
```

### 9. Анимация Свайпа С ItemTouchHelper

`ItemTouchHelper` даёт свайп и drag-жесты; можно анимировать `alpha`/`translation` во время свайпа:

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0,
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onMove(
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        target: RecyclerView.ViewHolder
    ): Boolean = false

    override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
        val position = viewHolder.bindingAdapterPosition
        if (position != RecyclerView.NO_POSITION) {
            adapter.removeItem(position)
        }
    }

    override fun onChildDraw(
        c: Canvas,
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        dX: Float,
        dY: Float,
        actionState: Int,
        isCurrentlyActive: Boolean
    ) {
        if (actionState == ItemTouchHelper.ACTION_STATE_SWIPE) {
            val alpha = 1.0f - (kotlin.math.abs(dX) / viewHolder.itemView.width.coerceAtLeast(1))
            viewHolder.itemView.alpha = alpha.coerceIn(0f, 1f)
        }
        super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
    }
})

itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Лучшие Практики

1. Избегайте тяжёлых анимаций для каждого элемента при прокрутке: это может вызвать лаги.
2. Всегда сбрасывайте состояние: очищайте анимации и возвращайте свойства в `onViewRecycled`.
3. По возможности используйте `ItemAnimator` и property-анимации для структурных изменений.
4. Держите анимации короткими: обычно 150–300 мс.
5. Профилируйте производительность и стремитесь к плавной (~60 fps) прокрутке.
6. Уважайте настройки пользователя: если системные анимации отключены/уменьшены, минимизируйте необязательные анимации. Пример ниже — упрощённая проверка одного из масштабов анимаций.

```kotlin
fun Context.isGlobalAnimationsDisabled(): Boolean {
    return try {
        val scale = Settings.Global.getFloat(
            contentResolver,
            Settings.Global.ANIMATOR_DURATION_SCALE
        )
        scale == 0f
    } catch (e: Settings.SettingNotFoundException) {
        false
    }
}

if (!context.isGlobalAnimationsDisabled()) {
    // Применяем анимации (пример; в реальном коде можно учитывать и другие системные флаги)
}
```

---

## Answer (EN)
RecyclerView provides several ways to implement animations, from simple built-in animations to complex custom animations. Animations can be applied at different levels: item-level, adapter-level, and via custom `ItemAnimator`s.

Key mechanisms:
- `ItemAnimator`: handles add/remove/move/change animations when the adapter notifies item changes.
- View property animations in `onBindViewHolder` and programmatic layout/position changes: control how views appear as they are bound (RecyclerView does not use standard `LayoutAnimation` for its children; animations are driven via `ItemAnimator` and property animations).
- `ItemTouchHelper` and shared element transitions: for interaction and navigation related animations.

### 1. Using DefaultItemAnimator

The simplest approach is using the built-in `DefaultItemAnimator` (enabled by default for many RecyclerView setups):

```kotlin
val recyclerView: RecyclerView = findViewById(R.id.recyclerView)
recyclerView.itemAnimator = DefaultItemAnimator()

// Customize animation timing
(recyclerView.itemAnimator as? DefaultItemAnimator)?.apply {
    addDuration = 300
    removeDuration = 300
    moveDuration = 300
    changeDuration = 300
}
```

### 2. Custom ItemAnimator (conceptually)

You can create a custom `ItemAnimator` by extending `SimpleItemAnimator` or `DefaultItemAnimator`. A correct implementation must:
- Override `animateAdd`/`animateRemove`/`animateMove`/`animateChange` as needed.
- Call `dispatchAddStarting`/`dispatchAddFinished`, etc., at appropriate times.
- Manage and cancel running animations in `endAnimation`/`endAnimations`.
- Return `true` only when an animation was started.
- Eventually call `dispatchAnimationFinished(holder)` (directly or via base helpers) so RecyclerView knows the animation is complete.

Conceptual example for a fade-in on add (simplified; production code should also implement other required methods and proper cleanup of pending/running animations):

```kotlin
class FadeInItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        view.alpha = 0f

        view.animate()
            .alpha(1f)
            .setDuration(addDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // In a complete implementation, ensure dispatchAnimationFinished(holder)
                    // is called and internal tracking is updated.
                }
            })
            .start()

        return true
    }
}
```

### 3. Animations in Adapter (onBindViewHolder)

You can animate items directly when binding, but must handle recycling to avoid incorrect states.

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.itemView.clearAnimation()
        holder.textView.text = items[position]

        // Simple fade-in for newly bound items (simplified example)
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .start()
    }

    override fun onViewRecycled(holder: ViewHolder) {
        holder.itemView.clearAnimation()
        holder.itemView.alpha = 1f
        super.onViewRecycled(holder)
    }

    // Other required adapter methods omitted for brevity
}
```

### 4. Scale Animation via ItemAnimator

Example of scaling items on add (simplified):

```kotlin
class ScaleItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        view.scaleX = 0.5f
        view.scaleY = 0.5f
        view.alpha = 0f

        view.animate()
            .scaleX(1f)
            .scaleY(1f)
            .alpha(1f)
            .setDuration(addDuration)
            .setInterpolator(OvershootInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.scaleX = 1f
                    view.scaleY = 1f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                    // For a full implementation, also mark this animation as finished
                    // via the ItemAnimator's completion mechanisms.
                }
            })
            .start()

        return true
    }
}
```

### 5. Slide Animation via ItemAnimator

```kotlin
class SlideInLeftAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()
        // Simplified: relies on view.width; in real code ensure the view is laid out
        // or use a fixed/relative offset.
        view.translationX = -view.width.toFloat()
        view.alpha = 0f

        view.animate()
            .translationX(0f)
            .alpha(1f)
            .setDuration(addDuration)
            .setInterpolator(DecelerateInterpolator())
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchAddStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchAddFinished(holder)
                }
            })
            .start()

        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        val view = holder.itemView
        view.clearAnimation()

        view.animate()
            .translationX(view.width.toFloat())
            .alpha(0f)
            .setDuration(removeDuration)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationStart(animation: Animator) {
                    dispatchRemoveStarting(holder)
                }

                override fun onAnimationEnd(animation: Animator) {
                    view.translationX = 0f
                    view.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()

        return true
    }
}
```

(Other lifecycle methods are omitted; a production `ItemAnimator` must properly track and finish all pending/running animations.)

### 6. Using Third-Party Libraries

You can use libraries like RecyclerView Animators to get ready-made item animators:

```kotlin
// Example usage (library dependency not shown here)
recyclerView.itemAnimator = SlideInUpAnimator()
// or
recyclerView.itemAnimator = FadeInAnimator()
// or
recyclerView.itemAnimator = ScaleInAnimator()
```

### 7. Item-Specific Animations in Adapter

Animating only items that appear for the first time:

```kotlin
class AnimatedAdapter(private val items: MutableList<String>) :
    RecyclerView.Adapter<AnimatedAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        fun bind(text: String) {
            (itemView as? TextView)?.text = text
        }
    }

    private var lastPosition = -1

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.itemView.clearAnimation()
        holder.bind(items[position])

        if (position > lastPosition) {
            animateItem(holder.itemView, position)
            lastPosition = position
        }
    }

    private fun animateItem(view: View, position: Int) {
        view.translationY = 200f
        view.alpha = 0f

        view.animate()
            .translationY(0f)
            .alpha(1f)
            .setDuration(300)
            .setStartDelay((position * 50).toLong())
            .setInterpolator(DecelerateInterpolator())
            .start()
    }

    override fun onViewRecycled(holder: ViewHolder) {
        holder.itemView.clearAnimation()
        holder.itemView.alpha = 1f
        holder.itemView.translationY = 0f
        super.onViewRecycled(holder)
    }

    fun addItem(item: String, position: Int) {
        items.add(position, item)
        notifyItemInserted(position)
    }

    fun removeItem(position: Int) {
        items.removeAt(position)
        notifyItemRemoved(position)
    }
}
```

### 8. Shared Element Transitions

For transitions between a RecyclerView item and a detail screen, you can use shared element transitions:

```kotlin
class Item(val id: Long)

class MyAdapter(private val items: List<Item>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imageView: ImageView = view.findViewById(R.id.imageView)

        fun bind(item: Item, clickListener: (View, Item) -> Unit) {
            ViewCompat.setTransitionName(imageView, "image_${item.id}")
            itemView.setOnClickListener { clickListener(imageView, item) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_layout, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position]) { sharedView, item ->
            val context = sharedView.context
            val intent = Intent(context, DetailActivity::class.java)

            val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
                context as Activity,
                sharedView,
                ViewCompat.getTransitionName(sharedView) ?: ""
            )

            context.startActivity(intent, options.toBundle())
        }
    }

    override fun getItemCount(): Int = items.size
}
```

### 9. Swipe Animation with ItemTouchHelper

`ItemTouchHelper` provides swipe and drag interactions; you can animate `alpha`/`translation` during swipe:

```kotlin
val itemTouchHelper = ItemTouchHelper(object : ItemTouchHelper.SimpleCallback(
    0,
    ItemTouchHelper.LEFT or ItemTouchHelper.RIGHT
) {
    override fun onMove(
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        target: RecyclerView.ViewHolder
    ): Boolean = false

    override fun onSwiped(viewHolder: RecyclerView.ViewHolder, direction: Int) {
        val position = viewHolder.bindingAdapterPosition
        if (position != RecyclerView.NO_POSITION) {
            adapter.removeItem(position)
        }
    }

    override fun onChildDraw(
        c: Canvas,
        recyclerView: RecyclerView,
        viewHolder: RecyclerView.ViewHolder,
        dX: Float,
        dY: Float,
        actionState: Int,
        isCurrentlyActive: Boolean
    ) {
        if (actionState == ItemTouchHelper.ACTION_STATE_SWIPE) {
            val alpha = 1.0f - (kotlin.math.abs(dX) / viewHolder.itemView.width.coerceAtLeast(1))
            viewHolder.itemView.alpha = alpha.coerceIn(0f, 1f)
        }
        super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
    }
})

itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Best Practices

1. Avoid heavy per-item animations during scroll: can hurt performance and cause jank.
2. Always reset animation state: clear animations and restore properties in `onViewRecycled`.
3. Prefer property animations and let `RecyclerView`/`ItemAnimator` handle structural changes.
4. Keep animations short: around 150–300 ms is usually a good balance.
5. Profile performance (e.g., with Android Studio Profiler) and aim for smooth (~60 fps) scrolling.
6. Respect user settings: if system animations are disabled or reduced, minimize or disable non-essential animations. The example below checks only one global scale as a simplified illustration.

```kotlin
fun Context.isGlobalAnimationsDisabled(): Boolean {
    return try {
        val scale = Settings.Global.getFloat(
            contentResolver,
            Settings.Global.ANIMATOR_DURATION_SCALE
        )
        scale == 0f
    } catch (e: Settings.SettingNotFoundException) {
        false
    }
}

if (!context.isGlobalAnimationsDisabled()) {
    // Apply animations (example; real-world code may check additional flags)
}
```

---

## Follow-ups

- [[q-broadcastreceiver-contentprovider--android--easy]]
- [[q-save-data-outside-fragment--android--medium]]
- [[q-spannable-text-styling--android--medium]]

## References

- [Animations](https://developer.android.com/develop/ui/views/animations)

## Related Questions

### Prerequisites / Concepts

- [[c-custom-views]]

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - `View`, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - `View`, Ui

### Related (Medium)
- q-rxjava-pagination-recyclerview--android--medium - `View`, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - `View`, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - `View`, Ui
- [[q-recyclerview-async-list-differ--android--medium]] - `View`, Ui
- [[q-recyclerview-diffutil-advanced--android--medium]] - `View`, Ui
