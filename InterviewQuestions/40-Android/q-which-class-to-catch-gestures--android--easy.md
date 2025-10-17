---
id: 20251012-122711185
title: "Which Class To Catch Gestures / Какой класс для ловли жестов"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [gesture-detector, gestures, ui, difficulty/easy]
---

# Question (EN)

> Which class can be used to catch different gestures?

# Вопрос (RU)

> Какой класс можно использовать, чтобы ловить разные жесты?

---

## Answer (EN)

Use **GestureDetector** to handle standard gestures like taps, swipes, long presses, double taps, and flings.

### Basic Usage

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        gestureDetector = GestureDetector(this, MyGestureListener())

        view.setOnTouchListener { _, event ->
            gestureDetector.onTouchEvent(event)
        }
    }

    inner class MyGestureListener : GestureDetector.SimpleOnGestureListener() {
        override fun onSingleTapUp(e: MotionEvent): Boolean {
            // Handle tap
            return true
        }

        override fun onDoubleTap(e: MotionEvent): Boolean {
            // Handle double tap
            return true
        }

        override fun onLongPress(e: MotionEvent) {
            // Handle long press
        }

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            // Handle swipe/fling
            return true
        }

        override fun onScroll(
            e1: MotionEvent?,
            e2: MotionEvent,
            distanceX: Float,
            distanceY: Float
        ): Boolean {
            // Handle scroll
            return true
        }
    }
}
```

### In Custom View

```kotlin
class GestureView(context: Context) : View(context) {
    private val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
        override fun onDown(e: MotionEvent): Boolean = true

        override fun onFling(
            e1: MotionEvent?,
            e2: MotionEvent,
            velocityX: Float,
            velocityY: Float
        ): Boolean {
            if (abs(velocityX) > abs(velocityY)) {
                if (velocityX > 0) {
                    // Swipe right
                } else {
                    // Swipe left
                }
            }
            return true
        }
    })

    override fun onTouchEvent(event: MotionEvent): Boolean {
        return gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
    }
}
```

## Ответ (RU)

Для обработки жестов в Android используйте класс **GestureDetector**. Он помогает отслеживать стандартные жесты: одиночные нажатия (tap), свайпы (swipe/fling), долгие нажатия (long press), двойные касания (double tap) и scroll.

### Основное использование GestureDetector

**GestureDetector** - это вспомогательный класс, который обрабатывает `MotionEvent` и вызывает соответствующие callback методы для распознанных жестов.

#### Базовая настройка

1. Создать экземпляр `GestureDetector` с `GestureDetector.OnGestureListener` или `SimpleOnGestureListener`
2. Передать touch events в `gestureDetector.onTouchEvent(event)`
3. Реализовать нужные callback методы

**SimpleOnGestureListener** - это адаптер класс, позволяющий переопределить только нужные методы вместо реализации всех методов интерфейса.

#### Поддерживаемые жесты

**Основные жесты:**
- `onDown()` - палец коснулся экрана
- `onSingleTapUp()` - одиночное касание
- `onDoubleTap()` - двойное касание
- `onLongPress()` - долгое нажатие
- `onFling()` - быстрый свайп с инерцией
- `onScroll()` - прокрутка/перетаскивание
- `onShowPress()` - палец коснулся но ещё не поднят

**Параметры Fling:**
- `velocityX` - скорость по горизонтали (pixels/second)
- `velocityY` - скорость по вертикали (pixels/second)
- Можно использовать для определения направления свайпа

#### Использование в кастомных View

В кастомных View удобно создавать GestureDetector в конструкторе и обрабатывать события в `onTouchEvent()`. Важно вернуть `true` из `onDown()` чтобы получать последующие события.

#### Определение направления свайпа

Для определения направления свайпа в `onFling()`:
- Сравнить `abs(velocityX)` с `abs(velocityY)`
- Если `velocityX > 0` - свайп вправо
- Если `velocityX < 0` - свайп влево
- Если `velocityY > 0` - свайп вниз
- Если `velocityY < 0` - свайп вверх

### Дополнительные GestureDetector'ы

**ScaleGestureDetector** - для pinch-to-zoom:
- Определяет жесты масштабирования двумя пальцами
- Callback методы: `onScale()`, `onScaleBegin()`, `onScaleEnd()`
- Предоставляет `scaleFactor` для применения масштаба

**RotationGestureDetector** - для вращения двумя пальцами (custom implementation required)

### Compose Gestures

В Jetpack Compose жесты обрабатываются через модификаторы:
- `Modifier.pointerInput()` - низкоуровневый API
- `Modifier.clickable()` - для кликов
- `Modifier.draggable()` - для перетаскивания
- `detectTapGestures()` - для tap жестов
- `detectDragGestures()` - для drag жестов
- `detectTransformGestures()` - для multi-touch (zoom, pan, rotate)

### Best Practices

1. **Возвращать true из onDown()** - иначе последующие события не будут получены

2. **Обрабатывать return values** - возвращать `true` если жест обработан

3. **Комбинировать с OnTouchListener** - для обработки дополнительных событий:
   ```kotlin
   gestureDetector.onTouchEvent(event) || super.onTouchEvent(event)
   ```

4. **Избегать конфликтов в ScrollView** - использовать `requestDisallowInterceptTouchEvent()`

5. **Для сложных жестов** - рассмотреть custom MotionEvent handling

### Когда НЕ использовать GestureDetector

- Для simple clicks - используйте `OnClickListener`
- В Compose - используйте Compose gesture APIs
- Для multi-touch transformations - используйте `ScaleGestureDetector` + `RotationGestureDetector`

**Резюме**: GestureDetector упрощает обработку стандартных жестов (tap, double-tap, long-press, fling, scroll) путём абстрагирования от низкоуровневых MotionEvent. Для новых приложений на Compose используйте Compose gesture modifiers.

---

## Follow-ups

-   How do you detect pinch-to-zoom and rotation gestures (ScaleGestureDetector)?
-   When should you use GestureDetector vs OnGestureListener vs Compose gestures?
-   How do you avoid gesture conflicts inside nested scrolling containers?

## References

-   `https://developer.android.com/reference/android/view/GestureDetector` — GestureDetector
-   `https://developer.android.com/reference/android/view/ScaleGestureDetector` — ScaleGestureDetector
-   `https://developer.android.com/jetpack/compose/gestures` — Compose gestures

## Related Questions

-   [[q-what-is-known-about-methods-that-redraw-view--android--medium]]
-   [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]]
