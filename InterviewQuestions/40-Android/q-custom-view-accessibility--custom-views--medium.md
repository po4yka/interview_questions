---
id: 20251021-150000
title: "Custom View Accessibility / Доступность Custom View"
aliases: [Custom View Accessibility, Доступность Custom View]
topic: android
subtopics: [ui-views, ui-accessibility]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-custom-view-implementation--android--medium, q-compose-semantics--android--medium, q-android-accessibility-testing--android--medium]
created: 2025-10-21
updated: 2025-10-21
tags: [android/ui-views, android/ui-accessibility, accessibility, custom-views, talkback, inclusive-design, difficulty/medium]
source: https://developer.android.com/guide/topics/ui/accessibility
source_note: Official accessibility guide
---

# Вопрос (RU)
> Как сделать пользовательские view доступными? Объясните описания содержимого, события доступности, поддержку TalkBack и реализацию AccessibilityNodeInfo для сложных пользовательских view.

# Question (EN)
> How do you make custom views accessible? Explain content descriptions, accessibility events, TalkBack support, and implementing AccessibilityNodeInfo for complex custom views.

---

## Ответ (RU)

### Зачем нужна доступность
- 15% населения мира имеют различные формы инвалидности
- Требуется законом во многих странах (ADA, WCAG)
- Улучшает удобство использования для всех пользователей
- Лучшая SEO и обнаруживаемость

### Основы доступности

**Content Description:**
- Текстовое описание визуальных элементов
- Используется screen readers (TalkBack)
- Должно быть информативным и кратким

**Focusable и Clickable:**
- View должен быть доступен для навигации
- Поддержка клавиатуры и screen reader
- Правильная обработка касаний

### Минимальная реализация

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        // Основные настройки доступности
        isFocusable = true
        isClickable = true
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES

        // Content description
        contentDescription = "Custom button"

        setOnClickListener {
            performAccessibilityAction(
                AccessibilityNodeInfo.ACTION_CLICK,
                null
            )
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // Устанавливаем роль и действия
        info.roleDescription = "Button"
        info.addAction(AccessibilityNodeInfo.ACTION_CLICK)

        // Дополнительная информация
        info.isEnabled = isEnabled
        info.isClickable = isClickable
    }
}
```

### AccessibilityNodeInfo для сложных view

```kotlin
class ComplexCustomView : ViewGroup {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // Роль и описание
        info.className = "ComplexCustomView"
        info.contentDescription = "Custom view with multiple elements"

        // Доступные действия
        info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)

        // Состояние
        info.isScrollable = true
        info.isEnabled = isEnabled

        // Дополнительная информация
        info.setStateDescription("Current state: ${currentState}")
    }

    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                scrollForward()
                announceForAccessibility("Scrolled forward")
                true
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                scrollBackward()
                announceForAccessibility("Scrolled backward")
                true
            }
            else -> super.performAccessibilityAction(action, arguments)
        }
    }
}
```

### События доступности

```kotlin
class AccessibleProgressView : View {

    private var progress = 0

    fun updateProgress(newProgress: Int) {
        progress = newProgress
        invalidate()

        // Уведомляем о изменении
        announceForAccessibility("Progress: $progress%")

        // Отправляем событие
        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SELECTED)
    }

    override fun onInitializeAccessibilityEvent(event: AccessibilityEvent) {
        super.onInitializeAccessibilityEvent(event)

        // Заполняем событие информацией
        event.text.add("Progress: $progress%")
        event.isEnabled = isEnabled
        event.isChecked = progress == 100
    }
}
```

### TalkBack поддержка

```kotlin
class TalkBackCompatibleView : View {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // Для TalkBack
        info.packageName = context.packageName
        info.className = className

        // Описание состояния
        info.setStateDescription("Selected: $isSelected")

        // Дополнительные действия
        if (isSelectable) {
            info.addAction(AccessibilityNodeInfo.ACTION_SELECT)
            info.addAction(AccessibilityNodeInfo.ACTION_CLEAR_SELECTION)
        }
    }

    // Обработка двойного касания для TalkBack
    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        if (action == AccessibilityNodeInfo.ACTION_CLICK) {
            // TalkBack использует ACTION_CLICK для активации
            handleClick()
            return true
        }
        return super.performAccessibilityAction(action, arguments)
    }
}
```

### Лучшие практики

1. **Всегда устанавливайте contentDescription** для визуальных элементов
2. **Используйте важные роли** - Button, CheckBox, EditText, etc.
3. **Предоставляйте обратную связь** через announceForAccessibility()
4. **Тестируйте с TalkBack** включенным
5. **Используйте semantic роли** вместо generic View
6. **Обрабатывайте все доступные действия** корректно
7. **Уведомляйте об изменениях** через события доступности

### Подводные камни

- **Не забывайте importantForAccessibility** для custom view
- **Правильно обрабатывайте ACTION_CLICK** для TalkBack
- **Не используйте слишком длинные описания** - они утомляют пользователей
- **Тестируйте навигацию клавиатурой** - должна работать без мыши
- **Проверяйте контрастность** цветов для слабовидящих

### Тестирование доступности

```kotlin
// В тестах
@Test
fun testAccessibility() {
    val view = AccessibleButton(context)

    // Проверяем content description
    assertThat(view.contentDescription).isEqualTo("Custom button")

    // Проверяем focusable
    assertThat(view.isFocusable).isTrue()

    // Проверяем clickable
    assertThat(view.isClickable).isTrue()

    // Тестируем действия
    assertThat(view.performAccessibilityAction(
        AccessibilityNodeInfo.ACTION_CLICK,
        null
    )).isTrue()
}
```

---

## Answer (EN)

### Why Accessibility Matters
- 15% of world population has some form of disability
- Required by law in many countries (ADA, WCAG)
- Improves usability for everyone
- Better SEO and discoverability

### Accessibility Basics

**Content Description:**
- Text alternative for visual elements
- Used by screen readers (TalkBack)
- Should be informative and concise

**Focusable and Clickable:**
- View should be accessible for navigation
- Support keyboard and screen reader
- Proper touch handling

### Minimal Implementation

```kotlin
class AccessibleButton @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    init {
        // Basic accessibility settings
        isFocusable = true
        isClickable = true
        importantForAccessibility = IMPORTANT_FOR_ACCESSIBILITY_YES

        // Content description
        contentDescription = "Custom button"

        setOnClickListener {
            performAccessibilityAction(
                AccessibilityNodeInfo.ACTION_CLICK,
                null
            )
        }
    }

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // Set role and actions
        info.roleDescription = "Button"
        info.addAction(AccessibilityNodeInfo.ACTION_CLICK)

        // Additional information
        info.isEnabled = isEnabled
        info.isClickable = isClickable
    }
}
```

### AccessibilityNodeInfo for Complex Views

```kotlin
class ComplexCustomView : ViewGroup {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // Role and description
        info.className = "ComplexCustomView"
        info.contentDescription = "Custom view with multiple elements"

        // Available actions
        info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD)
        info.addAction(AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD)

        // State
        info.isScrollable = true
        info.isEnabled = isEnabled

        // Additional information
        info.setStateDescription("Current state: ${currentState}")
    }

    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        return when (action) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD -> {
                scrollForward()
                announceForAccessibility("Scrolled forward")
                true
            }
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD -> {
                scrollBackward()
                announceForAccessibility("Scrolled backward")
                true
            }
            else -> super.performAccessibilityAction(action, arguments)
        }
    }
}
```

### Accessibility Events

```kotlin
class AccessibleProgressView : View {

    private var progress = 0

    fun updateProgress(newProgress: Int) {
        progress = newProgress
        invalidate()

        // Announce changes
        announceForAccessibility("Progress: $progress%")

        // Send event
        sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_SELECTED)
    }

    override fun onInitializeAccessibilityEvent(event: AccessibilityEvent) {
        super.onInitializeAccessibilityEvent(event)

        // Fill event with information
        event.text.add("Progress: $progress%")
        event.isEnabled = isEnabled
        event.isChecked = progress == 100
    }
}
```

### TalkBack Support

```kotlin
class TalkBackCompatibleView : View {

    override fun onInitializeAccessibilityNodeInfo(info: AccessibilityNodeInfo) {
        super.onInitializeAccessibilityNodeInfo(info)

        // For TalkBack
        info.packageName = context.packageName
        info.className = className

        // State description
        info.setStateDescription("Selected: $isSelected")

        // Additional actions
        if (isSelectable) {
            info.addAction(AccessibilityNodeInfo.ACTION_SELECT)
            info.addAction(AccessibilityNodeInfo.ACTION_CLEAR_SELECTION)
        }
    }

    // Handle double-tap for TalkBack
    override fun performAccessibilityAction(action: Int, arguments: Bundle?): Boolean {
        if (action == AccessibilityNodeInfo.ACTION_CLICK) {
            // TalkBack uses ACTION_CLICK for activation
            handleClick()
            return true
        }
        return super.performAccessibilityAction(action, arguments)
    }
}
```

### Best Practices

1. **Always set contentDescription** for visual elements
2. **Use important roles** - Button, CheckBox, EditText, etc.
3. **Provide feedback** through announceForAccessibility()
4. **Test with TalkBack** enabled
5. **Use semantic roles** instead of generic View
6. **Handle all available actions** correctly
7. **Notify about changes** through accessibility events

### Pitfalls

- **Don't forget importantForAccessibility** for custom views
- **Handle ACTION_CLICK properly** for TalkBack
- **Don't use too long descriptions** - they tire users
- **Test keyboard navigation** - should work without mouse
- **Check color contrast** for visually impaired users

### Accessibility Testing

```kotlin
// In tests
@Test
fun testAccessibility() {
    val view = AccessibleButton(context)

    // Check content description
    assertThat(view.contentDescription).isEqualTo("Custom button")

    // Check focusable
    assertThat(view.isFocusable).isTrue()

    // Check clickable
    assertThat(view.isClickable).isTrue()

    // Test actions
    assertThat(view.performAccessibilityAction(
        AccessibilityNodeInfo.ACTION_CLICK,
        null
    )).isTrue()
}
```

---

## Follow-ups

- How to test accessibility with automated tools?
- What are the differences between TalkBack and other screen readers?
- How to implement accessibility for custom gestures?
- What are the WCAG guidelines for mobile apps?

## References

- [Android Accessibility Guide](https://developer.android.com/guide/topics/ui/accessibility)
- [TalkBack User Guide](https://support.google.com/accessibility/android/answer/6283677)

## Related Questions

### Related (Same Level)
- [[q-compose-semantics--android--medium]]
