---
id: 20251021-150000
title: Custom View Accessibility / Доступность Custom View
aliases: [Custom View Accessibility, Доступность Custom View]
topic: android
subtopics:
  - ui-accessibility
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-accessibility-compose--android--medium
  - q-accessibility-talkback--android--medium
  - q-compose-semantics--android--medium
created: 2025-10-21
updated: 2025-10-21
tags: [android/ui-accessibility, android/ui-views, difficulty/medium]
source: https://developer.android.com/guide/topics/ui/accessibility
source_note: Official accessibility guide
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:26 pm
---

# Вопрос (RU)
> Доступность Custom View?

# Question (EN)
> Custom View Accessibility?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Why Accessibility Matters
- 15% of world population has some form of disability
- Required by law in many countries (ADA, WCAG)
- Improves usability for everyone
- Better SEO and discoverability

Based on principles from [[c-accessibility]] and c-inclusive-design.

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
