---
id: 20251020-200400
title: Espresso Advanced Patterns / Продвинутые паттерны Espresso
aliases:
- Espresso Advanced Patterns
- Продвинутые паттерны Espresso
topic: android
subtopics:
- testing-ui
- testing-instrumented
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://developer.android.com/training/testing/espresso
source_note: Android Espresso testing documentation
status: reviewed
moc: moc-android
related:
- q-android-testing-strategies--testing--medium
- q-ui-testing-best-practices--testing--medium
- q-android-testing-tools--testing--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/testing-ui
- android/testing-instrumented
- espresso
- ui-testing
- idling-resource
- difficulty/medium
---# Вопрос (RU)
> Как реализовать продвинутые паттерны Espresso с IdlingResource, custom matchers и ViewActions?

# Question (EN)
> How to implement Espresso advanced patterns with IdlingResource, custom matchers, and ViewActions?

---

## Ответ (RU)

Espresso - фреймворк UI тестирования для View-based интерфейсов. Продвинутое использование требует понимания IdlingResource, custom matchers и сложных паттернов взаимодействия.

### Основные паттерны

**1. IdlingResource для асинхронных операций**
- Проблема: Espresso не ждет завершения async операций
- Результат: flaky тесты, race conditions
- Решение: IdlingResource сообщает Espresso когда приложение idle

```kotlin
// Простой IdlingResource
class SimpleIdlingResource : IdlingResource {
    @Volatile private var callback: IdlingResource.ResourceCallback? = null
    @Volatile private var isIdle = true

    override fun getName() = "SimpleIdlingResource"
    override fun isIdleNow() = isIdle

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback?) {
        this.callback = callback
    }

    fun setIdleState(isIdle: Boolean) {
        this.isIdle = isIdle
        if (isIdle) callback?.onTransitionToIdle()
    }
}

// Использование в тесте
@Test
fun testWithIdlingResource() {
    val idlingResource = SimpleIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)

    try {
        idlingResource.setIdleState(false)
        // Запуск async операции
        performAsyncOperation()
        idlingResource.setIdleState(true)

        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom Matchers**
- Проблема: стандартные matchers не покрывают все случаи
- Результат: сложные тесты, плохая читаемость
- Решение: создание custom matchers для специфичных проверок

```kotlin
// Custom matcher для RecyclerView
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("RecyclerView with item count: $count")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}

// Custom matcher для текста с regex
fun withTextMatching(regex: String): Matcher<View> {
    return object : TypeSafeMatcher<View>() {
        override fun describeTo(description: Description) {
            description.appendText("with text matching: $regex")
        }

        override fun matchesSafely(item: View): Boolean {
            if (item !is TextView) return false
            return item.text.toString().matches(regex.toRegex())
        }
    }
}

// Использование
onView(withId(R.id.recycler_view))
    .check(matches(withItemCount(5)))

onView(withTextMatching("\\d+ items"))
    .check(matches(isDisplayed()))
```

**3. Custom ViewActions**
- Проблема: стандартные actions не покрывают сложные взаимодействия
- Результат: невозможность тестировать сложные UI паттерны
- Решение: создание custom ViewActions

```kotlin
// Custom action для swipe с задержкой
fun swipeWithDelay(direction: GeneralSwipeAction.Direction): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isAssignableFrom(View::class.java)

        override fun getDescription(): String = "swipe with delay to $direction"

        override fun perform(uiController: UiController, view: View) {
            val coordinates = GeneralLocation.CENTER
            val precision = GeneralLocation.CENTER
            val startCoordinates = coordinates.calculateCoordinates(view)
            val endCoordinates = precision.calculateCoordinates(view)

            val startX = startCoordinates[0]
            val startY = startCoordinates[1]
            val endX = endCoordinates[0]
            val endY = endCoordinates[1]

            val swipeAction = GeneralSwipeAction(
                Swipe.SLOW, startX, startY, endX, endY, precision
            )
            swipeAction.perform(uiController, view)
        }
    }
}

// Custom action для long press с custom duration
fun longPressWithDuration(duration: Long): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isAssignableFrom(View::class.java)

        override fun getDescription(): String = "long press with duration $duration"

        override fun perform(uiController: UiController, view: View) {
            val coordinates = GeneralLocation.CENTER
            val precision = GeneralLocation.CENTER
            val startCoordinates = coordinates.calculateCoordinates(view)

            uiController.loopMainThreadUntilIdle()
            uiController.loopMainThreadForAtLeast(duration)
        }
    }
}
```

**4. RecyclerView тестирование**
- Проблема: RecyclerView требует специальных подходов
- Результат: сложность тестирования списков
- Решение: использование RecyclerViewActions

```kotlin
// Тестирование RecyclerView
@Test
fun testRecyclerViewInteraction() {
    // Проверка количества элементов
    onView(withId(R.id.recycler_view))
        .check(matches(withItemCount(10)))

    // Клик по элементу
    onView(withId(R.id.recycler_view))
        .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

    // Проверка текста в элементе
    onView(withId(R.id.recycler_view))
        .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(5))

    onView(withText("Item 5"))
        .check(matches(isDisplayed()))
}
```

**5. Обработка ошибок и retry**
- Проблема: flaky тесты из-за timing issues
- Результат: нестабильные тесты
- Решение: retry механизмы и proper error handling

```kotlin
// Retry механизм для flaky тестов
fun retryTest(maxAttempts: Int = 3, test: () -> Unit) {
    var lastException: Throwable? = null

    repeat(maxAttempts) { attempt ->
        try {
            test()
            return
        } catch (e: Throwable) {
            lastException = e
            if (attempt < maxAttempts - 1) {
                Thread.sleep(1000) // Wait before retry
            }
        }
    }

    throw lastException ?: AssertionError("Test failed after $maxAttempts attempts")
}

// Использование
@Test
fun flakyTest() {
    retryTest {
        onView(withText("Dynamic Content"))
            .check(matches(isDisplayed()))
    }
}
```

### Теория Espresso

**Архитектура Espresso:**
- ViewInteraction: взаимодействие с View элементами
- ViewAction: действия (click, type, swipe)
- ViewAssertion: проверки (matches, isDisplayed)
- Matcher: поиск элементов (withId, withText)

**IdlingResource принципы:**
- Espresso ждет пока все IdlingResource idle
- Автоматическая синхронизация с UI thread
- Предотвращение race conditions
- Поддержка async операций

**Custom Matchers:**
- TypeSafeMatcher: type-safe проверки
- BoundedMatcher: ограниченные типы
- BaseMatcher: базовые matchers
- describeTo(): описание для error messages

**ViewActions:**
- perform(): выполнение действия
- getConstraints(): ограничения для View
- getDescription(): описание действия
- UiController: управление UI thread

**Best Practices:**
- Использовать IdlingResource для async операций
- Создавать reusable custom matchers
- Избегать sleep() в тестах
- Proper cleanup в @After методах
- Изолированные тесты без зависимостей

## Answer (EN)

Espresso is Android's UI testing framework for View-based UIs. Advanced usage requires understanding IdlingResources, custom matchers, and complex interaction patterns.

### Key Patterns

**1. IdlingResource for async operations**
- Problem: Espresso doesn't wait for async operations
- Result: flaky tests, race conditions
- Solution: IdlingResource tells Espresso when app is idle

```kotlin
// Simple IdlingResource
class SimpleIdlingResource : IdlingResource {
    @Volatile private var callback: IdlingResource.ResourceCallback? = null
    @Volatile private var isIdle = true

    override fun getName() = "SimpleIdlingResource"
    override fun isIdleNow() = isIdle

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback?) {
        this.callback = callback
    }

    fun setIdleState(isIdle: Boolean) {
        this.isIdle = isIdle
        if (isIdle) callback?.onTransitionToIdle()
    }
}

// Usage in test
@Test
fun testWithIdlingResource() {
    val idlingResource = SimpleIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)

    try {
        idlingResource.setIdleState(false)
        // Start async operation
        performAsyncOperation()
        idlingResource.setIdleState(true)

        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom Matchers**
- Problem: standard matchers don't cover all cases
- Result: complex tests, poor readability
- Solution: create custom matchers for specific checks

```kotlin
// Custom matcher for RecyclerView
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("RecyclerView with item count: $count")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}

// Custom matcher for text with regex
fun withTextMatching(regex: String): Matcher<View> {
    return object : TypeSafeMatcher<View>() {
        override fun describeTo(description: Description) {
            description.appendText("with text matching: $regex")
        }

        override fun matchesSafely(item: View): Boolean {
            if (item !is TextView) return false
            return item.text.toString().matches(regex.toRegex())
        }
    }
}

// Usage
onView(withId(R.id.recycler_view))
    .check(matches(withItemCount(5)))

onView(withTextMatching("\\d+ items"))
    .check(matches(isDisplayed()))
```

**3. Custom ViewActions**
- Problem: standard actions don't cover complex interactions
- Result: inability to test complex UI patterns
- Solution: create custom ViewActions

```kotlin
// Custom action for swipe with delay
fun swipeWithDelay(direction: GeneralSwipeAction.Direction): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isAssignableFrom(View::class.java)

        override fun getDescription(): String = "swipe with delay to $direction"

        override fun perform(uiController: UiController, view: View) {
            val coordinates = GeneralLocation.CENTER
            val precision = GeneralLocation.CENTER
            val startCoordinates = coordinates.calculateCoordinates(view)
            val endCoordinates = precision.calculateCoordinates(view)

            val startX = startCoordinates[0]
            val startY = startCoordinates[1]
            val endX = endCoordinates[0]
            val endY = endCoordinates[1]

            val swipeAction = GeneralSwipeAction(
                Swipe.SLOW, startX, startY, endX, endY, precision
            )
            swipeAction.perform(uiController, view)
        }
    }
}

// Custom action for long press with custom duration
fun longPressWithDuration(duration: Long): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isAssignableFrom(View::class.java)

        override fun getDescription(): String = "long press with duration $duration"

        override fun perform(uiController: UiController, view: View) {
            val coordinates = GeneralLocation.CENTER
            val precision = GeneralLocation.CENTER
            val startCoordinates = coordinates.calculateCoordinates(view)

            uiController.loopMainThreadUntilIdle()
            uiController.loopMainThreadForAtLeast(duration)
        }
    }
}
```

**4. RecyclerView testing**
- Problem: RecyclerView requires special approaches
- Result: complexity in testing lists
- Solution: use RecyclerViewActions

```kotlin
// Testing RecyclerView
@Test
fun testRecyclerViewInteraction() {
    // Check item count
    onView(withId(R.id.recycler_view))
        .check(matches(withItemCount(10)))

    // Click on item
    onView(withId(R.id.recycler_view))
        .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

    // Check text in item
    onView(withId(R.id.recycler_view))
        .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(5))

    onView(withText("Item 5"))
        .check(matches(isDisplayed()))
}
```

**5. Error handling and retry**
- Problem: flaky tests due to timing issues
- Result: unstable tests
- Solution: retry mechanisms and proper error handling

```kotlin
// Retry mechanism for flaky tests
fun retryTest(maxAttempts: Int = 3, test: () -> Unit) {
    var lastException: Throwable? = null

    repeat(maxAttempts) { attempt ->
        try {
            test()
            return
        } catch (e: Throwable) {
            lastException = e
            if (attempt < maxAttempts - 1) {
                Thread.sleep(1000) // Wait before retry
            }
        }
    }

    throw lastException ?: AssertionError("Test failed after $maxAttempts attempts")
}

// Usage
@Test
fun flakyTest() {
    retryTest {
        onView(withText("Dynamic Content"))
            .check(matches(isDisplayed()))
    }
}
```

### Espresso Theory

**Espresso Architecture:**
- ViewInteraction: interaction with View elements
- ViewAction: actions (click, type, swipe)
- ViewAssertion: checks (matches, isDisplayed)
- Matcher: element finding (withId, withText)

**IdlingResource principles:**
- Espresso waits until all IdlingResources are idle
- Automatic synchronization with UI thread
- Prevents race conditions
- Supports async operations

**Custom Matchers:**
- TypeSafeMatcher: type-safe checks
- BoundedMatcher: bounded types
- BaseMatcher: basic matchers
- describeTo(): description for error messages

**ViewActions:**
- perform(): execute action
- getConstraints(): View constraints
- getDescription(): action description
- UiController: UI thread control

**Best Practices:**
- Use IdlingResource for async operations
- Create reusable custom matchers
- Avoid sleep() in tests
- Proper cleanup in @After methods
- Isolated tests without dependencies

## Follow-ups
- How to test Compose UI with Espresso?
- What's the difference between Espresso and UI Automator?
- How to handle flaky tests in CI/CD?
