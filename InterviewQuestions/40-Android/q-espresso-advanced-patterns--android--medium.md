---
id: 20251020-200400
title: Espresso Advanced Patterns / Продвинутые паттерны Espresso
aliases: [Espresso Advanced Patterns, Продвинутые паттерны Espresso, IdlingResource, Custom Matchers, Custom ViewActions]
topic: android
subtopics: [testing-instrumented, testing-ui]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-testing-strategies--android--medium, q-android-testing-tools--testing--medium, q-ui-testing-best-practices--testing--medium]
sources: [https://developer.android.com/training/testing/espresso]
created: 2025-10-20
updated: 2025-10-28
tags: [android/testing-instrumented, android/testing-ui, difficulty/medium, espresso, idling-resource, ui-testing]
---

# Вопрос (RU)
> Как реализовать продвинутые паттерны Espresso с IdlingResource, custom matchers и ViewActions?

# Question (EN)
> How to implement Espresso advanced patterns with IdlingResource, custom matchers, and ViewActions?

---

## Ответ (RU)

### Ключевые концепции

**IdlingResource** - синхронизация с async операциями. Espresso ждет пока все ресурсы idle перед выполнением действий.

**Custom Matchers** - специфичные проверки View. Наследуют TypeSafeMatcher или BoundedMatcher, реализуют matchesSafely() и describeTo().

**Custom ViewActions** - сложные UI взаимодействия. Реализуют perform(), getConstraints(), getDescription().

**RecyclerViewActions** - специальные действия для списков. Скроллинг, клики по позиции, custom assertions.

### Примеры кода

**1. IdlingResource для network запросов**

```kotlin
// ✅ Корректная реализация
class NetworkIdlingResource : IdlingResource {
    @Volatile private var callback: ResourceCallback? = null
    @Volatile private var activeRequests = 0

    override fun getName() = "NetworkIdlingResource"
    override fun isIdleNow() = activeRequests == 0

    override fun registerIdleTransitionCallback(callback: ResourceCallback?) {
        this.callback = callback
    }

    fun increment() {
        activeRequests++
    }

    fun decrement() {
        activeRequests--
        if (isIdleNow) callback?.onTransitionToIdle()
    }
}

// Использование
@Test
fun testWithNetwork() {
    val idlingResource = NetworkIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)
    try {
        onView(withId(R.id.button)).perform(click())
        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom matcher для RecyclerView**

```kotlin
// ✅ Type-safe matcher
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has $count items")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}

// ❌ Проблема: нет type safety
fun badMatcher(count: Int) = object : BaseMatcher<View>() {
    override fun matches(item: Any?) = (item as? RecyclerView)?.adapter?.itemCount == count
    override fun describeTo(description: Description) {}
}
```

**3. Custom ViewAction для drag**

```kotlin
// ✅ Полная реализация
fun dragToPosition(x: Float, y: Float): ViewAction {
    return object : ViewAction {
        override fun getConstraints() = isDisplayed()

        override fun getDescription() = "drag to ($x, $y)"

        override fun perform(uiController: UiController, view: View) {
            val location = IntArray(2)
            view.getLocationOnScreen(location)

            MotionEvents.sendDown(uiController, location, Press.FINGER)
            uiController.loopMainThreadForAtLeast(100)
            MotionEvents.sendMovement(uiController, floatArrayOf(x, y))
            MotionEvents.sendUp(uiController, floatArrayOf(x, y))
        }
    }
}
```

**4. RecyclerView assertions**

```kotlin
// ✅ Проверка конкретного элемента
onView(withId(R.id.recycler))
    .perform(scrollToPosition<ViewHolder>(5))
    .check(matches(hasDescendant(withText("Item 5"))))

// ✅ Действие на элементе с matcher
onView(withId(R.id.recycler))
    .perform(actionOnItem<ViewHolder>(
        hasDescendant(withText("Delete")),
        click()
    ))
```

### Архитектура

**Espresso синхронизация:**
- Автоматически ждет UI thread idle
- Проверяет все зарегистрированные IdlingResources
- Гарантирует отсутствие pending animations
- Предотвращает race conditions

**Matcher hierarchy:**
- BaseMatcher - базовый класс, минимум type safety
- TypeSafeMatcher - type-safe, для одного типа
- BoundedMatcher - для View подклассов

**ViewAction контракт:**
- getConstraints() - когда можно выполнить
- perform() - что делать
- getDescription() - для error messages

## Answer (EN)

### Key Concepts

**IdlingResource** - synchronizes with async operations. Espresso waits until all resources idle before performing actions.

**Custom Matchers** - specific View checks. Extend TypeSafeMatcher or BoundedMatcher, implement matchesSafely() and describeTo().

**Custom ViewActions** - complex UI interactions. Implement perform(), getConstraints(), getDescription().

**RecyclerViewActions** - special actions for lists. Scrolling, position-based clicks, custom assertions.

### Code Examples

**1. IdlingResource for network requests**

```kotlin
// ✅ Correct implementation
class NetworkIdlingResource : IdlingResource {
    @Volatile private var callback: ResourceCallback? = null
    @Volatile private var activeRequests = 0

    override fun getName() = "NetworkIdlingResource"
    override fun isIdleNow() = activeRequests == 0

    override fun registerIdleTransitionCallback(callback: ResourceCallback?) {
        this.callback = callback
    }

    fun increment() {
        activeRequests++
    }

    fun decrement() {
        activeRequests--
        if (isIdleNow) callback?.onTransitionToIdle()
    }
}

// Usage
@Test
fun testWithNetwork() {
    val idlingResource = NetworkIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)
    try {
        onView(withId(R.id.button)).perform(click())
        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom matcher for RecyclerView**

```kotlin
// ✅ Type-safe matcher
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has $count items")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}

// ❌ Problem: no type safety
fun badMatcher(count: Int) = object : BaseMatcher<View>() {
    override fun matches(item: Any?) = (item as? RecyclerView)?.adapter?.itemCount == count
    override fun describeTo(description: Description) {}
}
```

**3. Custom ViewAction for drag**

```kotlin
// ✅ Complete implementation
fun dragToPosition(x: Float, y: Float): ViewAction {
    return object : ViewAction {
        override fun getConstraints() = isDisplayed()

        override fun getDescription() = "drag to ($x, $y)"

        override fun perform(uiController: UiController, view: View) {
            val location = IntArray(2)
            view.getLocationOnScreen(location)

            MotionEvents.sendDown(uiController, location, Press.FINGER)
            uiController.loopMainThreadForAtLeast(100)
            MotionEvents.sendMovement(uiController, floatArrayOf(x, y))
            MotionEvents.sendUp(uiController, floatArrayOf(x, y))
        }
    }
}
```

**4. RecyclerView assertions**

```kotlin
// ✅ Check specific item
onView(withId(R.id.recycler))
    .perform(scrollToPosition<ViewHolder>(5))
    .check(matches(hasDescendant(withText("Item 5"))))

// ✅ Action on item with matcher
onView(withId(R.id.recycler))
    .perform(actionOnItem<ViewHolder>(
        hasDescendant(withText("Delete")),
        click()
    ))
```

### Architecture

**Espresso synchronization:**
- Automatically waits for UI thread idle
- Checks all registered IdlingResources
- Ensures no pending animations
- Prevents race conditions

**Matcher hierarchy:**
- BaseMatcher - base class, minimal type safety
- TypeSafeMatcher - type-safe, single type
- BoundedMatcher - for View subclasses

**ViewAction contract:**
- getConstraints() - when can execute
- perform() - what to do
- getDescription() - for error messages

---

## Follow-ups

- How to debug flaky Espresso tests?
- When to use UI Automator instead of Espresso?
- How to test WebView content with Espresso?
- What are alternatives to sleep() in tests?
- How to handle dialogs and fragments?

## References

- [[c-ui-testing]]
- [[c-test-automation]]
- [[q-android-testing-strategies--android--medium]]
- https://developer.android.com/training/testing/espresso/idling-resource
- https://developer.android.com/training/testing/espresso/recipes

## Related Questions

### Prerequisites (Easier)
- [[q-android-testing-basics--android--easy]]
- [[q-espresso-basics--android--easy]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]
- [[q-ui-testing-best-practices--testing--medium]]
- [[q-android-testing-tools--testing--medium]]

### Advanced (Harder)
- [[q-compose-testing-advanced--android--hard]]
- [[q-test-automation-architecture--testing--hard]]
