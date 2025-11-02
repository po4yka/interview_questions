---
id: android-322
title: "Touch Events / События касания"
aliases: [Touch Events, События касания]
topic: android
subtopics: [ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-event-handling, c-touch-input, q-view-methods-and-their-purpose--android--medium, q-what-layout-allows-overlapping-objects--android--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-views, difficulty/medium, event-handling, interaction, touch-events, ui]
date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# What Event is Called when User Presses the Screen?

# Вопрос (RU)

Какое событие вызывается при нажатии юзера по экрану

## Answer (EN)
When a user presses the screen in Android, the system calls a series of touch event methods. The main events are: **dispatchTouchEvent()**, **onInterceptTouchEvent()** (for ViewGroups), **onTouchEvent()**, and if configured, **onClick()**.

### Touch Event Flow

```kotlin
// Event dispatch flow:
// Activity.dispatchTouchEvent()
//   → ViewGroup.dispatchTouchEvent()
//     → ViewGroup.onInterceptTouchEvent()
//       → View.dispatchTouchEvent()
//         → View.onTouchEvent()
//           → View.OnClickListener.onClick()
```

### Touch Event Actions

```kotlin
class TouchEventExample : View {

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
                // Touch cancelled (e.g., parent intercepts)
                Log.d("Touch", "ACTION_CANCEL")
                return true
            }
        }
        return super.onTouchEvent(event)
    }
}
```

### dispatchTouchEvent()

First method called - distributes the event.

```kotlin
class CustomView : View {

    override fun dispatchTouchEvent(event: MotionEvent): Boolean {
        Log.d("Touch", "dispatchTouchEvent: ${event.actionToString()}")

        // Can intercept before normal handling
        if (event.action == MotionEvent.ACTION_DOWN) {
            // Custom logic
        }

        return super.dispatchTouchEvent(event)
    }
}
```

### onTouchEvent()

Main touch handling method.

```kotlin
class InteractiveView : View {

    private var lastX = 0f
    private var lastY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                lastX = event.x
                lastY = event.y
                return true // Consume event
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
                performClick() // Important for accessibility
                return true
            }
        }

        return super.onTouchEvent(event)
    }

    override fun performClick(): Boolean {
        return super.performClick()
    }
}
```

### onClick()

Called when ACTION_UP occurs without significant movement.

```kotlin
class ClickableView : View {

    init {
        // Set click listener
        setOnClickListener {
            Log.d("Touch", "View clicked!")
        }
    }

    // onClick is called only if:
    // 1. ACTION_DOWN occurred
    // 2. ACTION_UP occurred in same location
    // 3. No ACTION_CANCEL
    // 4. View is clickable
}
```

### ViewGroup Touch Interception

```kotlin
class CustomViewGroup : ViewGroup {

    override fun onInterceptTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                // Decide whether to intercept
                return false // Let children handle
            }

            MotionEvent.ACTION_MOVE -> {
                // Intercept if scrolling
                if (shouldInterceptScroll(event)) {
                    return true // Intercept future events
                }
            }
        }

        return super.onInterceptTouchEvent(event)
    }

    private fun shouldInterceptScroll(event: MotionEvent): Boolean {
        // Custom logic to determine if should intercept
        return false
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        // Handle intercepted events
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
                        performClick()
                        return true
                    }
                }

                return super.onTouchEvent(event)
            }

            override fun performClick(): Boolean {
                Log.d("Touch", "3. performClick (if no movement)")
                return super.performClick()
            }
        }

        customView.setOnClickListener {
            Log.d("Touch", "4. onClick callback")
        }

        setContentView(customView)
    }
}

fun MotionEvent.actionToString() = when (action) {
    MotionEvent.ACTION_DOWN -> "DOWN"
    MotionEvent.ACTION_UP -> "UP"
    MotionEvent.ACTION_MOVE -> "MOVE"
    MotionEvent.ACTION_CANCEL -> "CANCEL"
    else -> "OTHER"
}
```

### Event Sequence for Single Tap

```
1. ACTION_DOWN - dispatchTouchEvent()
2. ACTION_DOWN - onTouchEvent()
3. ACTION_UP - dispatchTouchEvent()
4. ACTION_UP - onTouchEvent()
5. performClick()
6. onClick()
```

### Gesture Detection

```kotlin
class GestureView : View {

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

When user presses screen, Android calls:

1. **ACTION_DOWN** - User touches screen
2. **dispatchTouchEvent()** - Event distribution starts
3. **onInterceptTouchEvent()** - Parent can intercept (ViewGroup only)
4. **onTouchEvent()** - View handles event
5. **ACTION_UP** - User lifts finger
6. **onClick()** - Called if no movement occurred

Key points:
- Return `true` from onTouchEvent() to consume event
- onClick() only fires on ACTION_UP without movement
- dispatchTouchEvent() is first, onTouchEvent() handles actual touch
- ViewGroups can intercept child events with onInterceptTouchEvent()

## Ответ (RU)

Система вызывает: dispatchTouchEvent() — распределяет событие. onTouchEvent() — обрабатывает вью, если не перехвачено. onClick() — вызывается, если был ACTION_UP без движения.

## Related Questions

- [[q-cicd-pipeline-android--android--medium]]
- [[q-kotlin-context-receivers--android--hard]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]
