---
id: 20251017-114255
title: "How Animations Work In Recyclerview / Как работают анимации в RecyclerView"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-spannable-text-styling--android--medium, q-broadcastreceiver-contentprovider--android--easy, q-save-data-outside-fragment--android--medium]
created: 2025-10-15
tags: [android/animations, android/recyclerview, android/ui, animations, recyclerview, ui, difficulty/medium]
---
# How are animations done in RecyclerView?

**Russian**: Как в RecyclerView делаются анимации?

**English**: How are animations done in RecyclerView?

## Answer (EN)
RecyclerView provides several ways to implement animations, from simple built-in animations to complex custom animations. Animations can be applied at different levels: item-level, adapter-level, and through custom ItemAnimators.

### 1. Using DefaultItemAnimator

The simplest approach is using the built-in **DefaultItemAnimator**:

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

### 2. Custom ItemAnimator

Create a custom ItemAnimator by extending **SimpleItemAnimator** or **DefaultItemAnimator**:

```kotlin
class CustomItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchAddFinished(holder)
                }
            })
            .start()
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    holder.itemView.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }
}

// Usage
recyclerView.itemAnimator = CustomItemAnimator()
```

### 3. Animations in Adapter (onBindViewHolder)

Animate items directly in the adapter when binding:

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]

        // Fade in animation
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .setStartDelay(position * 50L)
            .start()
    }

    // Other methods...
}
```

### 4. Scale Animation

```kotlin
class ScaleItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            scaleX = 0.5f
            scaleY = 0.5f
            alpha = 0f

            animate()
                .scaleX(1f)
                .scaleY(1f)
                .alpha(1f)
                .setDuration(300)
                .setInterpolator(OvershootInterpolator())
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }
}
```

### 5. Slide Animation

```kotlin
class SlideInLeftAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            translationX = -width.toFloat()
            alpha = 0f

            animate()
                .translationX(0f)
                .alpha(1f)
                .setDuration(300)
                .setInterpolator(DecelerateInterpolator())
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        translationX = 0f
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .translationX(holder.itemView.width.toFloat())
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    holder.itemView.translationX = 0f
                    holder.itemView.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }
}
```

### 6. Using Third-Party Libraries

#### RecyclerView Animators Library

```kotlin
// Usage
recyclerView.itemAnimator = SlideInUpAnimator()
// or
recyclerView.itemAnimator = FadeInAnimator()
// or
recyclerView.itemAnimator = ScaleInAnimator()
```

### 7. Item-Specific Animations in Adapter

```kotlin
class AnimatedAdapter(private val items: MutableList<String>) :
    RecyclerView.Adapter<AnimatedAdapter.ViewHolder>() {

    private var lastPosition = -1

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Animate only items appearing for the first time
        if (position > lastPosition) {
            animateItem(holder.itemView, position)
            lastPosition = position
        }
    }

    private fun animateItem(view: View, position: Int) {
        view.apply {
            translationY = 200f
            alpha = 0f

            animate()
                .translationY(0f)
                .alpha(1f)
                .setDuration(300)
                .setStartDelay((position * 50).toLong())
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
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

For transitions between RecyclerView and detail views:

```kotlin
class MyAdapter : RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imageView: ImageView = view.findViewById(R.id.imageView)

        fun bind(item: Item, clickListener: (View, Item) -> Unit) {
            // Set transition name for shared element
            ViewCompat.setTransitionName(imageView, "image_${item.id}")

            itemView.setOnClickListener {
                clickListener(imageView, item)
            }
        }
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position]) { view, item ->
            // Navigate with shared element
            val intent = Intent(view.context, DetailActivity::class.java)
            val options = ActivityOptionsCompat.makeSceneTransitionAnimation(
                view.context as Activity,
                view,
                ViewCompat.getTransitionName(view)!!
            )
            view.context.startActivity(intent, options.toBundle())
        }
    }
}
```

### 9. Swipe Animation

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
        val position = viewHolder.adapterPosition
        adapter.removeItem(position)
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
            val alpha = 1.0f - abs(dX) / viewHolder.itemView.width
            viewHolder.itemView.alpha = alpha
        }
        super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
    }
})

itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Best Practices

1. **Avoid animating on scroll**: Can cause performance issues
2. **Reset animation state**: Clear animations in onViewRecycled
3. **Use hardware layers**: For complex animations
4. **Keep animations short**: 200-300ms is optimal
5. **Test performance**: Ensure 60fps on all devices
6. **Consider accessibility**: Respect reduce motion settings

```kotlin
// Check reduce motion setting
val isReduceMotionEnabled = Settings.Global.getFloat(
    contentResolver,
    Settings.Global.TRANSITION_ANIMATION_SCALE,
    1f
) == 0f

if (!isReduceMotionEnabled) {
    // Apply animations
}
```

## Ответ (RU)

RecyclerView предоставляет несколько способов реализации анимаций, от простых встроенных анимаций до сложных пользовательских. Анимации могут применяться на разных уровнях: на уровне элементов, адаптера и через кастомные ItemAnimator.

### 1. Использование DefaultItemAnimator

Самый простой подход - использовать встроенный **DefaultItemAnimator**:

```kotlin
val recyclerView: RecyclerView = findViewById(R.id.recyclerView)
recyclerView.itemAnimator = DefaultItemAnimator()

// Настройка времени анимации
(recyclerView.itemAnimator as? DefaultItemAnimator)?.apply {
    addDuration = 300
    removeDuration = 300
    moveDuration = 300
    changeDuration = 300
}
```

### 2. Пользовательский ItemAnimator

Создайте кастомный ItemAnimator, наследуя **SimpleItemAnimator** или **DefaultItemAnimator**:

```kotlin
class CustomItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    dispatchAddFinished(holder)
                }
            })
            .start()
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    holder.itemView.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }
}

// Использование
recyclerView.itemAnimator = CustomItemAnimator()
```

### 3. Анимации в адаптере (onBindViewHolder)

Анимируйте элементы непосредственно в адаптере при привязке:

```kotlin
class MyAdapter(private val items: List<String>) :
    RecyclerView.Adapter<MyAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val textView: TextView = view.findViewById(R.id.textView)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.textView.text = items[position]

        // Анимация появления
        holder.itemView.alpha = 0f
        holder.itemView.animate()
            .alpha(1f)
            .setDuration(300)
            .setStartDelay(position * 50L)
            .start()
    }

    // Другие методы...
}
```

### 4. Анимация масштабирования

```kotlin
class ScaleItemAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            scaleX = 0.5f
            scaleY = 0.5f
            alpha = 0f

            animate()
                .scaleX(1f)
                .scaleY(1f)
                .alpha(1f)
                .setDuration(300)
                .setInterpolator(OvershootInterpolator())
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }
}
```

### 5. Анимация скольжения

```kotlin
class SlideInLeftAnimator : DefaultItemAnimator() {

    override fun animateAdd(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.apply {
            translationX = -width.toFloat()
            alpha = 0f

            animate()
                .translationX(0f)
                .alpha(1f)
                .setDuration(300)
                .setInterpolator(DecelerateInterpolator())
                .setListener(object : AnimatorListenerAdapter() {
                    override fun onAnimationEnd(animation: Animator) {
                        translationX = 0f
                        dispatchAddFinished(holder)
                    }
                })
                .start()
        }
        return true
    }

    override fun animateRemove(holder: RecyclerView.ViewHolder): Boolean {
        holder.itemView.animate()
            .translationX(holder.itemView.width.toFloat())
            .alpha(0f)
            .setDuration(300)
            .setListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    holder.itemView.translationX = 0f
                    holder.itemView.alpha = 1f
                    dispatchRemoveFinished(holder)
                }
            })
            .start()
        return true
    }
}
```

### 6. Специфичные анимации элементов в адаптере

```kotlin
class AnimatedAdapter(private val items: MutableList<String>) :
    RecyclerView.Adapter<AnimatedAdapter.ViewHolder>() {

    private var lastPosition = -1

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])

        // Анимировать только элементы, появляющиеся впервые
        if (position > lastPosition) {
            animateItem(holder.itemView, position)
            lastPosition = position
        }
    }

    private fun animateItem(view: View, position: Int) {
        view.apply {
            translationY = 200f
            alpha = 0f

            animate()
                .translationY(0f)
                .alpha(1f)
                .setDuration(300)
                .setStartDelay((position * 50).toLong())
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
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

### 7. Анимация свайпа

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
        val position = viewHolder.adapterPosition
        adapter.removeItem(position)
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
            val alpha = 1.0f - abs(dX) / viewHolder.itemView.width
            viewHolder.itemView.alpha = alpha
        }
        super.onChildDraw(c, recyclerView, viewHolder, dX, dY, actionState, isCurrentlyActive)
    }
})

itemTouchHelper.attachToRecyclerView(recyclerView)
```

### Лучшие практики

1. **Избегайте анимации при прокрутке**: Может вызвать проблемы с производительностью
2. **Сбрасывайте состояние анимации**: Очищайте анимации в onViewRecycled
3. **Используйте аппаратные слои**: Для сложных анимаций
4. **Держите анимации короткими**: 200-300мс оптимально
5. **Тестируйте производительность**: Обеспечьте 60fps на всех устройствах
6. **Учитывайте доступность**: Уважайте настройку уменьшения движения

```kotlin
// Проверка настройки уменьшения движения
val isReduceMotionEnabled = Settings.Global.getFloat(
    contentResolver,
    Settings.Global.TRANSITION_ANIMATION_SCALE,
    1f
) == 0f

if (!isReduceMotionEnabled) {
    // Применить анимации
}
```


---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View, Ui
- [[q-how-to-change-the-number-of-columns-in-recyclerview-depending-on-orientation--android--easy]] - View, Ui

### Related (Medium)
- [[q-rxjava-pagination-recyclerview--android--medium]] - View, Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View, Ui
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - View, Ui
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - View, Ui
- [[q-recyclerview-diffutil-advanced--recyclerview--medium]] - View, Ui
