---
id: android-448
title: Espresso Advanced Patterns / Продвинутые паттерны Espresso
aliases: [Custom Matchers, Custom ``ViewAction`s`, Espresso Advanced Patterns, `IdlingResource`, Продвинутые паттерны Espresso]
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
updated: 2025-11-03
tags: [android/testing-instrumented, android/testing-ui, difficulty/medium, espresso, idling-resource, ui-testing]
---

# Вопрос (RU)
> Как реализовать продвинутые паттерны Espresso с `IdlingResource`, custom matchers и ``ViewAction`s`?

# Question (EN)
> How to implement Espresso advanced patterns with `IdlingResource`, custom matchers, and ``ViewAction`s`?

---

## Ответ (RU)

### Ключевые Концепции

**`IdlingResource`** - синхронизация с async операциями. Espresso ждет пока все ресурсы idle перед выполнением действий.

**Custom Matchers** - специфичные проверки View. Наследуют `TypeSafeMatcher` или `BoundedMatcher`, реализуют matchesSafely() и describeTo().

**Custom ``ViewAction`s`** - сложные UI взаимодействия. Реализуют perform(), getConstraints(), getDescription().

**Recycler``ViewAction`s`** - специальные действия для списков. Скроллинг, клики по позиции, custom assertions.

### Примеры Кода

**1. `IdlingResource` для network запросов**

```kotlin
// ✅ Корректная реализация
class Network`IdlingResource` : `IdlingResource` {
    @Volatile private var callback: ResourceCallback? = null
    @Volatile private var activeRequests = 0

    override fun getName() = "Network`IdlingResource`"
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
    val idlingResource = Network`IdlingResource`()
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
    return object : `BoundedMatcher`<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has $count items")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}


**3. Custom `ViewAction` для drag**

```kotlin
// ✅ Полная реализация
fun dragToPosition(x: Float, y: Float): `ViewAction` {
    return object : `ViewAction` {
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
onView(withId(R.id.recycler))
    .perform(scrollToPosition<ViewHolder>(5))
    .check(matches(hasDescendant(withText("Item 5"))))
```

### Лучшие практики
- Не используйте `Thread.sleep()`; применяйте `IdlingResource` или `IdlingPolicies`
- Регистрируйте/разрегистрируйте ресурсы через `IdlingRegistry` в `@Before/@After`
- Для корутин: инкремент/декремент при запуске/завершении
- Сужайте matchers; избегайте хрупких `withText()` без контекста
- Пишите полезные сообщения в `describeTo()`

### Типичные ошибки
- Забыли `unregister()` → утечки и ложные idle
- Глобальные idlers, влияющие на другие тесты
- `sleep()` вместо синхронизации

### Архитектура

**Espresso синхронизация:**
- Автоматически ждет UI thread idle
- Проверяет все зарегистрированные `IdlingResource`s
- Гарантирует отсутствие pending animations
- Предотвращает race conditions

**Matcher hierarchy:**
- BaseMatcher - базовый класс, минимум type safety
- `TypeSafeMatcher` - type-safe, для одного типа
- `BoundedMatcher` - для View подклассов

**`ViewAction` контракт:**
- getConstraints() - когда можно выполнить
- perform() - что делать
- getDescription() - для error messages

## Answer (EN)

### Key Concepts

`IdlingResource` — sync with async ops; `TypeSafeMatcher`/`BoundedMatcher` for safe checks; custom `ViewAction` for complex gestures; `RecyclerViewActions` for lists.

### Patterns

- Counting `IdlingResource` for network and coroutines
- Type-safe matchers for `RecyclerView`
- Minimal custom drag `ViewAction`
- Compact assertions

**1. `IdlingResource` for network requests**

```kotlin
// ✅ Correct implementation
class Network`IdlingResource` : `IdlingResource` {
    @Volatile private var callback: ResourceCallback? = null
    @Volatile private var activeRequests = 0

    override fun getName() = "Network`IdlingResource`"
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
    val idlingResource = Network`IdlingResource`()
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
    return object : `BoundedMatcher`<View, RecyclerView>(RecyclerView::class.java) {
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

**3. Custom `ViewAction` for drag**

```kotlin
// ✅ Complete implementation
fun dragToPosition(x: Float, y: Float): `ViewAction` {
    return object : `ViewAction` {
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

### Best Practices
- Avoid `Thread.sleep()`; prefer `IdlingResource` / `IdlingPolicies`
- Register/unregister via `IdlingRegistry` in `@Before/@After`
- For coroutines: increment/decrement around launches
- Narrow matchers; avoid brittle bare `withText()`
- Add diagnostics in `describeTo()`

### Common Pitfalls
- Missing `unregister()` → leaks and false idle
- Global idlers affecting other tests
- Sleeping instead of synchronization

### Architecture

**Espresso synchronization:**
- Automatically waits for UI thread idle
- Checks all registered `IdlingResource`s
- Ensures no pending animations
- Prevents race conditions

**Matcher hierarchy:**
- BaseMatcher - base class, minimal type safety
- `TypeSafeMatcher` - type-safe, single type
- `BoundedMatcher` - for View subclasses

**`ViewAction` contract:**
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

- [[q-android-testing-strategies--android--medium]]
- https://developer.android.com/training/testing/espresso/idling-resource
- https://developer.android.com/training/testing/espresso/recipes

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-compose-ui-testing-advanced--android--hard]]