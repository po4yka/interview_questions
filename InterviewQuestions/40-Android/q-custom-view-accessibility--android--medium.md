---
id: 20251021-150000
title: Custom View Accessibility / Доступность Custom View
aliases: ["Custom View Accessibility", "Доступность Custom View"]
topic: android
subtopics: [ui-accessibility, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-accessibility-compose--android--medium, q-accessibility-talkback--android--medium, q-compose-semantics--android--medium]
sources: [https://developer.android.com/guide/topics/ui/accessibility]
created: 2025-10-21
updated: 2025-10-30
tags: [android/ui-accessibility, android/ui-views, difficulty/medium]
---
# Вопрос (RU)
> Как правильно реализовать доступность для custom view в Android?

# Question (EN)
> How to properly implement accessibility for custom views in Android?

---

## Ответ (RU)

### Ключевые Компоненты

**AccessibilityNodeInfo** - главный инструмент для описания view:
- Роль и тип элемента (кнопка, чекбокс, список)
- Текстовое описание для screen reader
- Доступные действия (клик, скролл, выбор)
- Состояние (enabled, checked, selected)

**Три обязательных шага**:
1. Установить базовые свойства (focusable, clickable)
2. Переопределить `onInitializeAccessibilityNodeInfo()`
3. Обработать accessibility actions в `performAccessibilityAction()`

### Минимальная Реализация

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        // ✅ Базовая настройка
        isFocusable = true
        isClickable = true
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES
        contentDescription = "Custom button"
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Семантическая роль
        info.className = Button::class.java.name
        info.addAction(AccessibilityNodeInfo.ACTION_CLICK)

        // ❌ Не используйте "View" для кликабельных элементов
        // info.className = View::class.java.name
    }
}
```

### Комплексные View с Действиями

```kotlin
class ScrollableCustomView : View {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        info.contentDescription = "Прокручиваемый список"
        info.isScrollable = true

        if (canScrollForward()) {
            info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        }
        if (canScrollBackward()) {
            info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)
        }
    }

    override fun performAccessibilityAction(action: Int, args: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                scrollForward()
                // ✅ Озвучиваем изменение
                announceForAccessibility("Прокручено вперед")
                true
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                scrollBackward()
                announceForAccessibility("Прокручено назад")
                true
            }
            else -> super.performAccessibilityAction(action, args)
        }
    }
}
```

### Динамические Изменения

```kotlin
class ProgressView : View {
    private var progress = 0

    fun setProgress(value: Int) {
        if (progress != value) {
            progress = value
            invalidate()

            // ✅ Уведомляем screen reader об изменении
            announceForAccessibility("Прогресс: $progress%")
            sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SELECTED)
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Описываем текущее состояние
        info.contentDescription = "Индикатор прогресса"
        info.stateDescription = "$progress процентов"

        // ❌ Не дублируйте состояние в contentDescription
        // info.contentDescription = "Прогресс $progress%" // Плохо
    }
}
```

### Критические Моменты

**Что делать**:
- Всегда устанавливайте `contentDescription` для не-текстовых элементов
- Используйте `stateDescription` для динамического состояния (API 30+)
- Тестируйте с TalkBack на реальном устройстве
- Обрабатывайте `ACTION_CLICK` для совместимости с TalkBack
- Объявляйте изменения через `announceForAccessibility()`

**Чего избегать**:
- Слишком длинные описания (>15 слов)
- Дублирование видимого текста в `contentDescription`
- Игнорирование `importantForAccessibility` для decorative элементов
- Использование `View::class.java.name` для интерактивных элементов

## Answer (EN)

### Key Components

**AccessibilityNodeInfo** - primary tool for describing views:
- Role and element type (button, checkbox, list)
- Text description for screen readers
- Available actions (click, scroll, select)
- State (enabled, checked, selected)

**Three required steps**:
1. Set base properties (focusable, clickable)
2. Override `onInitializeAccessibilityNodeInfo()`
3. Handle accessibility actions in `performAccessibilityAction()`

### Minimal Implementation

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        // ✅ Basic setup
        isFocusable = true
        isClickable = true
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES
        contentDescription = "Custom button"
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Semantic role
        info.className = Button::class.java.name
        info.addAction(AccessibilityNodeInfo.ACTION_CLICK)

        // ❌ Don't use "View" for clickable elements
        // info.className = View::class.java.name
    }
}
```

### Complex Views with Actions

```kotlin
class ScrollableCustomView : View {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        info.contentDescription = "Scrollable list"
        info.isScrollable = true

        if (canScrollForward()) {
            info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        }
        if (canScrollBackward()) {
            info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)
        }
    }

    override fun performAccessibilityAction(action: Int, args: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                scrollForward()
                // ✅ Announce changes
                announceForAccessibility("Scrolled forward")
                true
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                scrollBackward()
                announceForAccessibility("Scrolled backward")
                true
            }
            else -> super.performAccessibilityAction(action, args)
        }
    }
}
```

### Dynamic Changes

```kotlin
class ProgressView : View {
    private var progress = 0

    fun setProgress(value: Int) {
        if (progress != value) {
            progress = value
            invalidate()

            // ✅ Notify screen reader of changes
            announceForAccessibility("Progress: $progress%")
            sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SELECTED)
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // ✅ Describe current state
        info.contentDescription = "Progress indicator"
        info.stateDescription = "$progress percent"

        // ❌ Don't duplicate state in contentDescription
        // info.contentDescription = "Progress $progress%" // Bad
    }
}
```

### Critical Points

**Do**:
- Always set `contentDescription` for non-text elements
- Use `stateDescription` for dynamic state (API 30+)
- Test with TalkBack on real devices
- Handle `ACTION_CLICK` for TalkBack compatibility
- Announce changes via `announceForAccessibility()`

**Don't**:
- Use overly long descriptions (>15 words)
- Duplicate visible text in `contentDescription`
- Ignore `importantForAccessibility` for decorative elements
- Use `View::class.java.name` for interactive elements

---

## Follow-ups

- How to test custom view accessibility with Accessibility Scanner and Espresso?
- What's the difference between `contentDescription` and `stateDescription`?
- How to implement accessibility for ViewGroups with child navigation?
- How to handle custom gestures while maintaining TalkBack compatibility?
- When should you use `importantForAccessibility = NO` vs `IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS`?

## References

- [[c-accessibility]]
- [[c-android-views]]
- [[c-talkback]]
- [Android Accessibility Guide](https://developer.android.com/guide/topics/ui/accessibility)
- [AccessibilityNodeInfo API](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo)
- [Custom View Accessibility](https://developer.android.com/guide/topics/ui/accessibility/custom-views)

## Related Questions

### Prerequisites (Easier)
- [[q-accessibility-basics--android--easy]] - Understanding accessibility fundamentals
- [[q-content-description--android--easy]] - Using content descriptions properly

### Related (Same Level)
- [[q-compose-semantics--android--medium]] - Compose accessibility semantics
- [[q-accessibility-talkback--android--medium]] - TalkBack integration patterns
- [[q-accessibility-compose--android--medium]] - Compose accessibility implementation

### Advanced (Harder)
- [[q-accessibility-testing--android--hard]] - Comprehensive accessibility testing
- [[q-accessibility-services--android--hard]] - Building custom accessibility services
- [[q-viewgroup-accessibility--android--hard]] - Complex ViewGroup accessibility
