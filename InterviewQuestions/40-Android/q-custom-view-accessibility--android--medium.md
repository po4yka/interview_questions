---\
id: android-477
title: Custom View Accessibility / Доступность Custom View
aliases: [Custom View Accessibility, Доступность Custom View]
topic: android
subtopics: [ui-accessibility, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-accessibility, c-custom-views, q-accessibility-compose--android--medium, q-accessibility-talkback--android--medium, q-compose-semantics--android--medium, q-custom-view-attributes--android--medium, q-custom-view-lifecycle--android--medium, q-custom-view-state-saving--android--medium]
sources:
  - "https://developer.android.com/guide/topics/ui/accessibility"
created: 2025-10-21
updated: 2025-11-10
tags: [android/ui-accessibility, android/ui-views, difficulty/medium]

---\
# Вопрос (RU)
> Как правильно реализовать доступность для custom view в Android?

# Question (EN)
> How to properly implement accessibility for custom views in Android?

---

## Ответ (RU)

### Ключевые Компоненты

**`AccessibilityNodeInfo`** — главный инструмент для описания view:
- Роль и тип элемента (кнопка, чекбокс, список)
- Текстовое описание для screen reader
- Доступные действия (клик, скролл, выбор)
- Состояние (`enabled`, `checked`, `selected`)

**Базовые шаги для интерактивного custom view**:
1. Установить корректные свойства (`isFocusable`, `isClickable`, `isEnabled`, `importantForAccessibility`)
2. Переопределить `onInitializeAccessibilityNodeInfo()` для описания роли и состояния
3. Переопределить `performAccessibilityAction()` ТОЛЬКО если нужны кастомные действия или своя логика на стандартные действия

Для сложных составных/скроллируемых view рекомендуется использовать `AccessibilityDelegate` или `ExploreByTouchHelper`.

### Минимальная Реализация

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        // ✅ Базовая настройка
        isFocusable = true
        isClickable = true
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_YES
        // Если на кастомной кнопке нет собственного текста — задаем описание
        contentDescription = "Custom button"
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Семантическая роль (чтобы TalkBack воспринимал ее как кнопку)
        info.className = Button::class.java.name
        info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK)

        // ❌ Не используйте абстрактный "View" для кликабельных элементов,
        // если по смыслу это кнопка/переключатель и т.п.
        // info.className = View::class.java.name
    }
}
```

### Комплексные `View` С Действиями

```kotlin
class ScrollableCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        info.contentDescription = "Прокручиваемый список"
        info.isScrollable = true

        if (canScrollForward()) {
            info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)
        }
        if (canScrollBackward()) {
            info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD)
        }
    }

    override fun performAccessibilityAction(action: Int, args: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                val handled = scrollForward()
                if (handled) {
                    // ✅ При существенном изменении контента можно уведомить пользователя
                    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED)
                }
                handled
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                val handled = scrollBackward()
                if (handled) {
                    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED)
                }
                handled
            }
            else -> super.performAccessibilityAction(action, args)
        }
    }

    private fun canScrollForward(): Boolean { /* ... */ return false }
    private fun canScrollBackward(): Boolean { /* ... */ return false }
    private fun scrollForward(): Boolean { /* ... */ return false }
    private fun scrollBackward(): Boolean { /* ... */ return false }
}
```

### Динамические Изменения

```kotlin
class ProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0

    fun setProgress(value: Int) {
        val newValue = value.coerceIn(0, 100)
        if (progress != newValue) {
            progress = newValue
            invalidate()

            // ✅ Уведомляем об изменении доступности: пусть сервис сам решит, как озвучить
            sendAccessibilityEvent(AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED)
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Описываем текущее состояние
        info.className = ProgressBar::class.java.name
        info.contentDescription = "Индикатор прогресса"
        info.stateDescription = "$progress процентов"

        // Альтернатива для старых API — использовать RangeInfo или обновление
        // text/contentDescription через sendAccessibilityEvent.
    }
}
```

### Критические Моменты

**Что делать**:
- Всегда обеспечивайте описания для не-текстовых элементов, которые несут смысл
- Используйте `contentDescription`, если текст/значение недоступны TalkBack из других свойств
- Используйте `stateDescription` для динамического состояния (API 30+)
- Для сложных custom view (несколько виртуальных элементов, сложная навигация) применяйте `AccessibilityDelegate` / `ExploreByTouchHelper`
- Тестируйте с `TalkBack` на реальном устройстве и в разных состояниях
- Обрабатывайте `ACTION_CLICK` или другие действия, если вы меняете стандартное поведение
- Используйте `announceForAccessibility()` для значимых изменений (ошибки форм, завершение действия и т.п.), а не для каждого мелкого апдейта

**Чего избегать**:
- Слишком длинные описания (>15–20 слов)
- Дублирование текста: не повторяйте `contentDescription`, если видимый текст уже корректно доступен читателям экрана; но НЕ опускайте описание, если иначе оно не будет доступно
- Игнорирование `importantForAccessibility` для декоративных элементов (таким элементам задавайте `View.IMPORTANT_FOR_ACCESSIBILITY_NO`)
- Указание `View::class.java.name` для интерактивных элементов, если они по смыслу являются кнопками/переключателями/чекбоксами и т.п.

## Answer (EN)

### Key Components

**`AccessibilityNodeInfo`** — primary tool for describing views:
- Role and element type (button, checkbox, list)
- Text description for screen readers
- Available actions (click, scroll, select)
- State (`enabled`, `checked`, `selected`)

**Basic steps for an interactive custom view**:
1. `Set` correct properties (`isFocusable`, `isClickable`, `isEnabled`, `importantForAccessibility`)
2. Override `onInitializeAccessibilityNodeInfo()` to describe role and state
3. Override `performAccessibilityAction()` ONLY when you provide custom actions or override default behavior

For complex composite/scrollable views, prefer using `AccessibilityDelegate` or `ExploreByTouchHelper`.

### Minimal Implementation

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        // ✅ Basic setup
        isFocusable = true
        isClickable = true
        importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_YES
        // If the custom button has no own visible text, expose its purpose
        contentDescription = "Custom button"
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Semantic role so TalkBack treats it as a button
        info.className = Button::class.java.name
        info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_CLICK)

        // ❌ Don't use generic "View" for interactive elements
        // if they are semantically buttons/toggles/etc.
        // info.className = View::class.java.name
    }
}
```

### Complex Views with Actions

```kotlin
class ScrollableCustomView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        info.contentDescription = "Scrollable list"
        info.isScrollable = true

        if (canScrollForward()) {
            info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_FORWARD)
        }
        if (canScrollBackward()) {
            info.addAction(AccessibilityNodeInfo.AccessibilityAction.ACTION_SCROLL_BACKWARD)
        }
    }

    override fun performAccessibilityAction(action: Int, args: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                val handled = scrollForward()
                if (handled) {
                    // ✅ Fire appropriate accessibility event on content change
                    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED)
                }
                handled
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                val handled = scrollBackward()
                if (handled) {
                    sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED)
                }
                handled
            }
            else -> super.performAccessibilityAction(action, args)
        }
    }

    private fun canScrollForward(): Boolean { /* ... */ return false }
    private fun canScrollBackward(): Boolean { /* ... */ return false }
    private fun scrollForward(): Boolean { /* ... */ return false }
    private fun scrollBackward(): Boolean { /* ... */ return false }
}
```

### Dynamic Changes

```kotlin
class ProgressView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    private var progress = 0

    fun setProgress(value: Int) {
        val newValue = value.coerceIn(0, 100)
        if (progress != newValue) {
            progress = newValue
            invalidate()

            // ✅ Notify accessibility services that content/state has changed;
            // they decide how/when to announce.
            sendAccessibilityEvent(AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED)
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Describe current state
        info.className = ProgressBar::class.java.name
        info.contentDescription = "Progress indicator"
        info.stateDescription = "$progress percent"

        // For older APIs you can use RangeInfo or update text/contentDescription
        // and send an appropriate accessibility event.
    }
}
```

### Critical Points

**Do**:
- Always provide descriptions for non-text elements that convey meaning
- Use `contentDescription` when the text/value is not otherwise exposed to accessibility services
- Use `stateDescription` for dynamic state (API 30+)
- For complex custom views (multiple virtual elements, custom navigation), leverage `AccessibilityDelegate` / `ExploreByTouchHelper`
- Test with TalkBack on real devices across different states
- Handle `ACTION_CLICK` or other actions when you override default behavior
- Use `announceForAccessibility()` for significant, user-noticeable state changes (e.g., form errors, completion), not every minor change

**Don't**:
- Use overly long descriptions (>15–20 words)
- Blindly duplicate visible text in `contentDescription`: avoid redundancy if the visible text is already correctly exposed; but don't omit descriptions when otherwise inaccessible
- Ignore `importantForAccessibility` for decorative elements (set `View.IMPORTANT_FOR_ACCESSIBILITY_NO` for them)
- Use `View::class.java.name` for interactive elements when they are semantically buttons/toggles/checkboxes/etc.

---

## Дополнительные Вопросы (RU)

- Как тестировать доступность custom view с помощью Accessibility Scanner и Espresso?
- В чем разница между `contentDescription` и `stateDescription`?
- Как реализовать доступность для `ViewGroup` с навигацией по дочерним элементам?
- Как обрабатывать пользовательские жесты, сохраняя совместимость с TalkBack?
- Когда использовать `importantForAccessibility = NO` и когда `IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS`?

## Follow-ups

- How to test custom view accessibility with Accessibility Scanner and Espresso?
- What's the difference between `contentDescription` and `stateDescription`?
- How to implement accessibility for ViewGroups with child navigation?
- How to handle custom gestures while maintaining TalkBack compatibility?
- When should you use `importantForAccessibility = NO` vs `IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS`?

## Ссылки (RU)

- [[c-accessibility]]
- [Android Accessibility Guide](https://developer.android.com/guide/topics/ui/accessibility)
- [AccessibilityNodeInfo API](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo)
- [Доступность кастомных `View`](https://developer.android.com/guide/topics/ui/accessibility/custom-views)

## References

- [[c-accessibility]]
- [Android Accessibility Guide](https://developer.android.com/guide/topics/ui/accessibility)
- [AccessibilityNodeInfo API](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo)
- [Custom `View` Accessibility](https://developer.android.com/guide/topics/ui/accessibility/custom-views)

## Связанные Вопросы (RU)

### Предварительные (проще)
- Понимание базовых принципов системы `View` в Android
- Базовые знания концепций доступности

### Связанные (такой Же уровень)
- [[q-compose-semantics--android--medium]] — семантика доступности в Compose
- [[q-accessibility-talkback--android--medium]] — паттерны интеграции с `TalkBack`
- [[q-accessibility-compose--android--medium]] — реализация доступности в Compose

### Продвинутые (сложнее)
- [[q-accessibility-testing--android--medium]] — комплексное тестирование доступности
- Создание собственных сервисов доступности
- Сложные паттерны доступности для `ViewGroup`

## Related Questions

### Prerequisites (Easier)
- Understanding of Android `View` system basics
- Basic knowledge of accessibility concepts

### Related (Same Level)
- [[q-compose-semantics--android--medium]] — Compose accessibility semantics
- [[q-accessibility-talkback--android--medium]] — `TalkBack` integration patterns
- [[q-accessibility-compose--android--medium]] — Compose accessibility implementation

### Advanced (Harder)
- [[q-accessibility-testing--android--medium]] — Comprehensive accessibility testing
- Building custom accessibility services
- Complex `ViewGroup` accessibility patterns
