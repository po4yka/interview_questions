---
id: 20251016-163920
title: "Which Event On Screen Press / Какое событие при нажатии на экран"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [android/touch-events, android/ui, event handling, touch events, touch-events, ui, difficulty/easy]
---
# Какое событие вызывается при нажатии юзера по экрану?

**English**: Which event is triggered when user presses on screen?

## Answer (EN)
When a user presses on the screen in Android, the **ACTION_DOWN** event is triggered via **MotionEvent**.

### Touch Event Sequence

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // User pressed the screen
            val x = event.x
            val y = event.y
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // User is moving finger while pressed
            return true
        }
        MotionEvent.ACTION_UP -> {
            // User released the screen
            return true
        }
        MotionEvent.ACTION_CANCEL -> {
            // Touch was cancelled
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

### Complete Touch Events

| Event | Description |
|-------|-------------|
| ACTION_DOWN | Initial press |
| ACTION_MOVE | Finger moving while pressed |
| ACTION_UP | Finger lifted |
| ACTION_CANCEL | Touch cancelled by system |
| ACTION_POINTER_DOWN | Additional finger down (multi-touch) |
| ACTION_POINTER_UP | Additional finger up (multi-touch) |

### Example Usage

```kotlin
class TouchableView(context: Context) : View(context) {
    private var touchX = 0f
    private var touchY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "Press at ($touchX, $touchY)")
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                touchX = event.x
                touchY = event.y
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                Log.d("Touch", "Released at (${event.x}, ${event.y})")
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.RED }
        canvas.drawCircle(touchX, touchY, 50f, paint)
    }
}
```

### Setting Touch Listener

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Handle press
            true
        }
        else -> false
    }
}
```

## Ответ (RU)

Когда пользователь нажимает на экран в Android, срабатывает событие **ACTION_DOWN** через **MotionEvent**.

### Последовательность событий касания

```kotlin
override fun onTouchEvent(event: MotionEvent): Boolean {
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Пользователь нажал на экран
            val x = event.x
            val y = event.y
            return true
        }
        MotionEvent.ACTION_MOVE -> {
            // Пользователь перемещает палец при нажатии
            return true
        }
        MotionEvent.ACTION_UP -> {
            // Пользователь отпустил экран
            return true
        }
        MotionEvent.ACTION_CANCEL -> {
            // Касание было отменено
            return true
        }
    }
    return super.onTouchEvent(event)
}
```

### Полный список событий касания

| Событие | Описание |
|---------|----------|
| ACTION_DOWN | Начальное нажатие |
| ACTION_MOVE | Палец перемещается при нажатии |
| ACTION_UP | Палец поднят |
| ACTION_CANCEL | Касание отменено системой |
| ACTION_POINTER_DOWN | Дополнительный палец нажат (мультитач) |
| ACTION_POINTER_UP | Дополнительный палец поднят (мультитач) |

### Пример использования

```kotlin
class TouchableView(context: Context) : View(context) {
    private var touchX = 0f
    private var touchY = 0f

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                touchX = event.x
                touchY = event.y
                Log.d("Touch", "Нажатие в ($touchX, $touchY)")
                invalidate()
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                touchX = event.x
                touchY = event.y
                invalidate()
                return true
            }
            MotionEvent.ACTION_UP -> {
                Log.d("Touch", "Отпущено в (${event.x}, ${event.y})")
                return true
            }
        }
        return super.onTouchEvent(event)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val paint = Paint().apply { color = Color.RED }
        canvas.drawCircle(touchX, touchY, 50f, paint)
    }
}
```

### Установка слушателя касания

```kotlin
view.setOnTouchListener { v, event ->
    when (event.action) {
        MotionEvent.ACTION_DOWN -> {
            // Обработка нажатия
            true
        }
        else -> false
    }
}
```

**Резюме**: В Android при нажатии пользователя на экран вызывается событие **ACTION_DOWN** через **MotionEvent**. Полная последовательность событий: ACTION_DOWN (нажатие) → ACTION_MOVE (перемещение) → ACTION_UP (отпускание). Обработка осуществляется через метод `onTouchEvent()` или `setOnTouchListener()`.

