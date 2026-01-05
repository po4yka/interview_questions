---
id: android-322
title: Touch Events / События касания
aliases: [Touch Events, События касания]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-view-system, q-mvi-one-time-events--android--medium, q-server-sent-events-sse--android--medium, q-view-methods-and-their-purpose--android--medium, q-what-events-are-activity-methods-tied-to--android--medium, q-what-layout-allows-overlapping-objects--android--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [android/ui-views, difficulty/medium, event-handling, interaction,
      touch-events, ui]

anki_synced: true
anki_slugs:
  - 40-android-q-what-event-is-called-when-user-presses-the-screen-android-en
  - 40-android-q-what-event-is-called-when-user-presses-the-screen-android-ru
anki_last_sync: '2025-11-26T22:32:40.783101'
---
# Вопрос (RU)

> Какое событие вызывается при нажатии пользователя на экран?

# Question (EN)

> What event is called when the user presses the screen?

## Ответ (RU)

При первом нажатии пальцем по экрану генерируется событие касания с действием **`MotionEvent.ACTION_DOWN`**, которое проходит через цепочку обработки:

1. **`dispatchTouchEvent()`** — сначала вызывается у `Activity`, затем у `ViewGroup` и далее у конкретного `View`, распределяя `MotionEvent`.
2. **`onInterceptTouchEvent()`** (только у `ViewGroup`) — родитель может решить перехватить дальнейшие события этого жеста.
3. **`onTouchEvent()`** — основной метод обработки касаний во `View`.
4. При корректной последовательности `ACTION_DOWN` → `ACTION_UP` без существенного движения, без `ACTION_CANCEL`, при кликабельном и включённом `View` — может быть вызвано **`performClick()`**, а затем **`onClick()`** слушателя.

Ключевые моменты:
- Само «нажатие» (первое прикосновение) соответствует **`ACTION_DOWN`**.
- Цепочка доставки реализуется через `dispatchTouchEvent()` и `onTouchEvent()`; `onClick()` — это производное высокоуровневое событие.

См. также: [[c-android-view-system]]

### Поток Событий Касания

```kotlin
// Поток распространения события (упрощенно):
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent()
//       → View.dispatchTouchEvent()
//         → View.onTouchEvent()
//           → View.OnClickListener.onClick()
```

### Действия Событий Касания

```kotlin
class TouchEventExample(context: Context) : View(context) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Пользователь коснулся экрана
                Log.d("Touch", "ACTION_DOWN at (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // Пользователь двигает палец при нажатии
                Log.d("Touch", "ACTION_MOVE to (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Пользователь отпустил палец
                Log.d("Touch", "ACTION_UP at (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Событие отменено (например, перехвачено родителем)
                Log.d("Touch", "ACTION_CANCEL")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### `dispatchTouchEvent()`

Первый колбэк в цепочке `Activity`/`View`/`ViewGroup`, который распределяет событие дальше.

```kotlin
class CustomView(context: Context) : View(context) {

    override fun dispatchTouchEvent(event: MotionEvent): Boolean {
        Log.d("Touch", "dispatchTouchEvent: ${event.actionToString()}")

        // При необходимости можно добавить предварительную обработку
        if (event.action == MotionEvent.ACTION_DOWN) {
            // Дополнительная логика
        }

        return super.dispatchTouchEvent(event)
    }
}
```

### `onTouchEvent()`

Основной метод обработки касаний у `View`.

```kotlin
class InteractiveView(context: Context) : View(context) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                return true // Вернуть true, чтобы продолжать получать события этого жеста
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY

                translationX += dx
                translationY += dy

                lastX = event.x
                lastY = event.y
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Для согласованности и доступности вызываем performClick()
                performClick()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        // Обработка клика при необходимости, затем вызов super
        return super.performClick()
    }
}
```

### `onClick()`

Высокоуровневый колбэк клика, вызывается после валидного tap-жеста.

```kotlin
class ClickableView(context: Context) : View(context) {

    init {
        // Установка обработчика клика
        setOnClickListener {
            Log.d("Touch", "View clicked!")
        }
    }

    // onClick вызывается только если (упрощенно):
    // 1. ACTION_DOWN произошел на этом View
    // 2. ACTION_UP произошел на том же View (в пределах touch slop)
    // 3. Не было ACTION_CANCEL
    // 4. View кликабелен и включен
}
```

### Перехват Касаний Во `ViewGroup`

```kotlin
abstract class CustomViewGroup(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Обычно не перехватываем DOWN, чтобы он ушел детям
                return false
            }

            MotionEvent.ACTION_MOVE -> {
                // Можно перехватить, например, при детектировании скролла
                if (shouldInterceptScroll(event)) {
                    return true // Перехватываем дальнейшие события этого жеста
                }
            }
        }

        return super.onInterceptTouchEvent(event)
    }

    private fun shouldInterceptScroll(event: MotionEvent): Boolean {
        // Логика определения, нужно ли перехватить
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Обработка событий, перехваченных этим ViewGroup
        return super.onTouchEvent(event)
    }
}
```

### Полный Пример Обработки Касаний

```kotlin
class CompleteTouchExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val customView = object : View(this) {

            override fun dispatchTouchEvent(event: MotionEvent): Boolean {
                Log.d("Touch", "1. dispatchTouchEvent: ${event.actionToString()}")
                return super.dispatchTouchEvent(event)
            }

            override fun onTouchEvent(event: MotionEvent): Boolean {
                Log.d("Touch", "2. onTouchEvent: ${event.actionToString()}")

                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        Log.d("Touch", "   → Пользователь нажал на экран")
                        return true
                    }

                    MotionEvent.ACTION_MOVE -> {
                        Log.d("Touch", "   → Пользователь двигает палец")
                        return true
                    }

                    MotionEvent.ACTION_UP -> {
                        Log.d("Touch", "   → Пользователь отпустил палец")
                        // Для валидного клика логично вызвать performClick()
                        performClick()
                        return true
                    }

                    MotionEvent.ACTION_CANCEL -> {
                        Log.d("Touch", "   → Касание отменено")
                        return true
                    }
                }

                return super.onTouchEvent(event)
            }

            override fun performClick(): Boolean {
                Log.d("Touch", "3. performClick() (вызывается для валидного клика)")
                return super.performClick()
            }
        }

        customView.setOnClickListener {
            Log.d("Touch", "4. onClick callback")
        }

        setContentView(customView)
    }
}

fun MotionEvent.actionToString(): String = when (action) {
    MotionEvent.ACTION_DOWN -> "DOWN"
    MotionEvent.ACTION_UP -> "UP"
    MotionEvent.ACTION_MOVE -> "MOVE"
    MotionEvent.ACTION_CANCEL -> "CANCEL"
    else -> "OTHER"
}
```

### Последовательность Событий Для Одиночного Тапа (упрощенно)

```text
1. ACTION_DOWN → dispatchTouchEvent()
2. ACTION_DOWN → onTouchEvent()
3. ACTION_UP   → dispatchTouchEvent()
4. ACTION_UP   → onTouchEvent()
5. performClick() (если жест распознан как клик)
6. onClick() callback
```

### Распознавание Жестов

```kotlin
class GestureView(context: Context) : View(context) {

    private val gestureDetector = GestureDetector(context,
        object : GestureDetector.SimpleOnGestureListener() {

            override fun onDown(e: MotionEvent): Boolean {
                Log.d("Gesture", "onDown")
                return true
            }

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                Log.d("Gesture", "Single tap")
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                Log.d("Gesture", "Double tap")
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                Log.d("Gesture", "Long press")
            }

            override fun onFling(
                e1: MotionEvent,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                Log.d("Gesture", "Fling: velocity ($velocityX, $velocityY)")
                return true
            }

            override fun onScroll(
                e1: MotionEvent,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                Log.d("Gesture", "Scroll: distance ($distanceX, $distanceY)")
                return true
            }
        })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### События Касания В Jetpack Compose

```kotlin
@Composable
fun ComposeTouchEvents() {
    var tapInfo by remember { mutableStateOf("Tap the box") }

    Box(
        modifier = Modifier
            .size(200.dp)
            .background(Color.Blue)
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        tapInfo = "Pressed"
                        tryAwaitRelease()
                        tapInfo = "Released"
                    },
                    onTap = {
                        tapInfo = "Tapped at (${it.x}, ${it.y})"
                    },
                    onDoubleTap = {
                        tapInfo = "Double tapped"
                    },
                    onLongPress = {
                        tapInfo = "Long pressed"
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Text(tapInfo, color = Color.White)
    }
}
```

### Резюме

Когда пользователь нажимает на экран:

1. Генерируется **`ACTION_DOWN`** — начальное касание.
2. **`dispatchTouchEvent()`** запускает распространение события (`Activity` → `ViewGroup` → `View`).
3. **`onInterceptTouchEvent()`** (`ViewGroup`) может перехватить дальнейшие события жеста.
4. **`onTouchEvent()`** в целевом `View` обрабатывает касание.
5. Если жест завершается подходящим **`ACTION_UP`** (без отмены, в пределах допусков, `View` кликабелен и включен), вызывается **`performClick()`**, ведущий к **`onClick()`**.

Ключевые моменты:
- Низкоуровневое событие для нажатия — `MotionEvent.ACTION_DOWN`.
- Возвращайте `true` из `onTouchEvent()`, чтобы продолжать получать события того же жеста.
- `onClick()` — высокоуровневая абстракция, вызывается только для валидного клика.
- `ViewGroup` управляет доставкой событий детям через `onInterceptTouchEvent()`.

## Answer (EN)

When a user presses the screen in Android, the system generates a touch event with action **`MotionEvent.ACTION_DOWN`**, which travels through the touch dispatch chain. The main callbacks involved are: **`dispatchTouchEvent()`**, **`onInterceptTouchEvent()`** (for `ViewGroup`s), **`onTouchEvent()`**, and, for clickable views with a valid tap sequence, **`performClick()` / `onClick()`**.

Key idea: the physical press corresponds to **`ACTION_DOWN`**; higher-level callbacks (`onClick`) are derived from the full gesture (DOWN → UP without cancel/too much movement, etc.).

See also: [[c-android-view-system]]

### Touch Event `Flow`

```kotlin
// Event dispatch flow (simplified):
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent()
//       → View.dispatchTouchEvent()
//         → View.onTouchEvent()
//           → View.OnClickListener.onClick()
```

### Touch Event Actions

```kotlin
class TouchEventExample(context: Context) : View(context) {

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // User pressed down on screen
                Log.d("Touch", "ACTION_DOWN at (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                // User moved finger while pressing
                Log.d("Touch", "ACTION_MOVE to (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_UP -> {
                // User lifted finger
                Log.d("Touch", "ACTION_UP at (${event.x}, ${event.y})")
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                // Touch cancelled (e.g., parent intercepts or gesture taken over)
                Log.d("Touch", "ACTION_CANCEL")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### dispatchTouchEvent()

First callback in the `View`/`Activity` chain; responsible for dispatching the event further.

```kotlin
class CustomView(context: Context) : View(context) {

    override fun dispatchTouchEvent(event: MotionEvent): Boolean {
        Log.d("Touch", "dispatchTouchEvent: ${event.actionToString()}")

        // Custom pre-processing if needed
        if (event.action == MotionEvent.ACTION_DOWN) {
            // Custom logic
        }

        return super.dispatchTouchEvent(event)
    }
}
```

### onTouchEvent()

Main touch handling method of a `View`.

```kotlin
class InteractiveView(context: Context) : View(context) {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                return true // Consume event to continue receiving this gesture
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastX
                val dy = event.y - lastY

                translationX += dx
                translationY += dy

                lastX = event.x
                lastY = event.y
                return true
            }

            MotionEvent.ACTION_UP -> {
                // Delegate to click handling for accessibility and consistency
                performClick()
                return true
            }

            MotionEvent.ACTION_CANCEL -> {
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        // Handle click if needed, then call super
        return super.performClick()
    }
}
```

### onClick()

High-level click callback triggered after a valid tap gesture.

```kotlin
class ClickableView(context: Context) : View(context) {

    init {
        // Set click listener
        setOnClickListener {
            Log.d("Touch", "View clicked!")
        }
    }

    // onClick is called only if (simplified):
    // 1. ACTION_DOWN occurred on the view
    // 2. ACTION_UP occurred on the same view (within touch slop)
    // 3. No ACTION_CANCEL was received
    // 4. View is clickable and enabled
}
```

### `ViewGroup` Touch Interception

```kotlin
abstract class CustomViewGroup(context: Context) : ViewGroup(context) {

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Decide whether to intercept; usually false so children get the DOWN
                return false
            }

            MotionEvent.ACTION_MOVE -> {
                // Intercept if, for example, we detect scrolling
                if (shouldInterceptScroll(event)) {
                    return true // Intercept subsequent events in this gesture
                }
            }
        }

        return super.onInterceptTouchEvent(event)
    }

    private fun shouldInterceptScroll(event: MotionEvent): Boolean {
        // Custom logic to determine if we should intercept
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Handle events intercepted by this ViewGroup
        return super.onTouchEvent(event)
    }
}
```

### Complete Touch Event Example

```kotlin
class CompleteTouchExample : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val customView = object : View(this) {

            override fun dispatchTouchEvent(event: MotionEvent): Boolean {
                Log.d("Touch", "1. dispatchTouchEvent: ${event.actionToString()}")
                return super.dispatchTouchEvent(event)
            }

            override fun onTouchEvent(event: MotionEvent): Boolean {
                Log.d("Touch", "2. onTouchEvent: ${event.actionToString()}")

                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        Log.d("Touch", "   → User pressed screen")
                        return true
                    }

                    MotionEvent.ACTION_MOVE -> {
                        Log.d("Touch", "   → User moving finger")
                        return true
                    }

                    MotionEvent.ACTION_UP -> {
                        Log.d("Touch", "   → User lifted finger")
                        // Conceptually, performClick() should be invoked for a valid tap
                        performClick()
                        return true
                    }

                    MotionEvent.ACTION_CANCEL -> {
                        Log.d("Touch", "   → Touch cancelled")
                        return true
                    }
                }

                return super.onTouchEvent(event)
            }

            override fun performClick(): Boolean {
                Log.d("Touch", "3. performClick() (called for valid click gesture)")
                return super.performClick()
            }
        }

        customView.setOnClickListener {
            Log.d("Touch", "4. onClick callback")
        }

        setContentView(customView)
    }
}

fun MotionEvent.actionToString(): String = when (action) {
    MotionEvent.ACTION_DOWN -> "DOWN"
    MotionEvent.ACTION_UP -> "UP"
    MotionEvent.ACTION_MOVE -> "MOVE"
    MotionEvent.ACTION_CANCEL -> "CANCEL"
    else -> "OTHER"
}
```

### Event Sequence for Single Tap (Simplified)

```text
1. ACTION_DOWN → dispatchTouchEvent()
2. ACTION_DOWN → onTouchEvent()
3. ACTION_UP   → dispatchTouchEvent()
4. ACTION_UP   → onTouchEvent()
5. performClick() (if gesture qualifies as a click)
6. onClick() callback
```

### Gesture Detection

```kotlin
class GestureView(context: Context) : View(context) {

    private val gestureDetector = GestureDetector(context,
        object : GestureDetector.SimpleOnGestureListener() {

            override fun onDown(e: MotionEvent): Boolean {
                Log.d("Gesture", "onDown")
                return true
            }

            override fun onSingleTapUp(e: MotionEvent): Boolean {
                Log.d("Gesture", "Single tap")
                return true
            }

            override fun onDoubleTap(e: MotionEvent): Boolean {
                Log.d("Gesture", "Double tap")
                return true
            }

            override fun onLongPress(e: MotionEvent) {
                Log.d("Gesture", "Long press")
            }

            override fun onFling(
                e1: MotionEvent,
                e2: MotionEvent,
                velocityX: Float,
                velocityY: Float
            ): Boolean {
                Log.d("Gesture", "Fling: velocity ($velocityX, $velocityY)")
                return true
            }

            override fun onScroll(
                e1: MotionEvent,
                e2: MotionEvent,
                distanceX: Float,
                distanceY: Float
            ): Boolean {
                Log.d("Gesture", "Scroll: distance ($distanceX, $distanceY)")
                return true
            }
        })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

### Touch Event in Jetpack Compose

```kotlin
@Composable
fun ComposeTouchEvents() {
    var tapInfo by remember { mutableStateOf("Tap the box") }

    Box(
        modifier = Modifier
            .size(200.dp)
            .background(Color.Blue)
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        tapInfo = "Pressed"
                        tryAwaitRelease()
                        tapInfo = "Released"
                    },
                    onTap = {
                        tapInfo = "Tapped at (${it.x}, ${it.y})"
                    },
                    onDoubleTap = {
                        tapInfo = "Double tapped"
                    },
                    onLongPress = {
                        tapInfo = "Long pressed"
                    }
                )
            },
        contentAlignment = Alignment.Center
    ) {
        Text(tapInfo, color = Color.White)
    }
}
```

### Summary

When the user presses the screen:

1. **`ACTION_DOWN`** is generated — represents the initial touch.
2. **`dispatchTouchEvent()`** starts the event distribution (`Activity` → `ViewGroup` → `View`).
3. **`onInterceptTouchEvent()`** (`ViewGroup`) may choose to intercept subsequent events for this gesture.
4. **`onTouchEvent()`** in the target `View` handles the touch.
5. If the gesture completes with a suitable **`ACTION_UP`** (no cancel, within touch slop, view clickable/enabled), **`performClick()`** is invoked, leading to **`onClick()`**.

Key points:
- The low-level event for the press is `MotionEvent.ACTION_DOWN`.
- Return `true` from `onTouchEvent()` to keep receiving events in the same gesture.
- `onClick()` is a high-level abstraction invoked only for a valid click gesture, not for every `ACTION_DOWN`/`ACTION_UP` pair.
- `ViewGroup` can control whether children receive events via `onInterceptTouchEvent()`.

## Follow-ups

### Дополнительные Вопросы (RU)

- [[q-view-methods-and-their-purpose--android--medium]]
- [[q-what-layout-allows-overlapping-objects--android--easy]]
- Как обрабатываются последовательные события `ACTION_DOWN`, `ACTION_MOVE`, `ACTION_UP` в сложной иерархии `ViewGroup`?

### Additional Questions (EN)

- [[q-view-methods-and-their-purpose--android--medium]]
- [[q-what-layout-allows-overlapping-objects--android--easy]]
- How are `ACTION_DOWN`, `ACTION_MOVE`, and `ACTION_UP` sequences handled in a complex `ViewGroup` hierarchy?

## Ссылки (RU)

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Связанные Вопросы (RU)

- [[q-what-layout-allows-overlapping-objects--android--easy]]

## Related Questions

- [[q-what-layout-allows-overlapping-objects--android--easy]]
