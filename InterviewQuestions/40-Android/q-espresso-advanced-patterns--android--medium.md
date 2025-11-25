---
id: android-448
title: Espresso Advanced Patterns / Продвинутые паттерны Espresso
aliases: [Custom Matchers, Custom ViewActions, Espresso Advanced Patterns, IdlingResource, Продвинутые паттерны Espresso]
topic: android
subtopics:
  - testing-instrumented
  - testing-ui
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-testing
  - q-android-architectural-patterns--android--medium
  - q-android-testing-strategies--android--medium
  - q-camerax-advanced-pipeline--android--hard
  - q-wear-compose-ux-patterns--android--hard
sources:
  - "https://developer.android.com/training/testing/espresso"
created: 2025-10-20
updated: 2025-11-10
tags: [android/testing-instrumented, android/testing-ui, difficulty/medium, espresso, idling-resource, ui-testing]

date created: Saturday, November 1st 2025, 1:29:00 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Как реализовать продвинутые паттерны Espresso с `IdlingResource`, custom matchers и `ViewAction`s?

# Question (EN)
> How to implement Espresso advanced patterns with `IdlingResource`, custom matchers, and `ViewAction`s?

---

## Ответ (RU)

### Ключевые Концепции

- `IdlingResource` — механизм синхронизации с асинхронными операциями. Espresso ждет, пока основной поток и все зарегистрированные ресурсы станут idle перед выполнением действий.
- Custom matchers — специфичные проверки `View`. Как правило, наследуют `TypeSafeMatcher` или `BoundedMatcher`, реализуют `matchesSafely()` и `describeTo()`.
- Custom `ViewAction`s — для сложных или нетипичных UI-взаимодействий. Реализуют `perform()`, `getConstraints()`, `getDescription()`.
- `RecyclerViewActions` — специальные действия и проверки для списков: скролл, клики по позиции, проверки содержимого.

### Паттерны

- Counting `IdlingResource` для сетевых вызовов и корутин.
- Типобезопасные matchers для `RecyclerView`.
- Минимальный custom drag `ViewAction` (иллюстративно; по возможности использовать встроенные swipe/click действия).
- Сфокусированные проверки конкретных элементов.

### Примеры Кода

**1. Counting `IdlingResource` для сетевых запросов**

Упрощенный пример паттерна подсчета активных операций (аналог `CountingIdlingResource`).

```kotlin
class NetworkIdlingResource : IdlingResource {
    @Volatile
    private var callback: IdlingResource.ResourceCallback? = null

    @Volatile
    private var activeRequests = 0

    override fun getName(): String = "NetworkIdlingResource"

    override fun isIdleNow(): Boolean = activeRequests == 0

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback) {
        this.callback = callback
    }

    @Synchronized
    fun increment() {
        activeRequests++
    }

    @Synchronized
    fun decrement() {
        if (activeRequests > 0) {
            activeRequests--
            if (isIdleNow()) {
                callback?.onTransitionToIdle()
            }
        }
    }
}

// Использование в тесте
@Test
fun testWithNetwork() {
    val idlingResource = NetworkIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)
    try {
        // production code должен вызывать increment()/decrement() вокруг сетевых запросов
        onView(withId(R.id.button)).perform(click())
        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom matcher для RecyclerView**

```kotlin
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
```

**Анти-пример (менее безопасно):**

```kotlin
fun badMatcher(count: Int) = object : BaseMatcher<View>() {
    override fun matches(item: Any?): Boolean =
        (item as? RecyclerView)?.adapter?.itemCount == count

    override fun describeTo(description: Description) {
        description.appendText("is RecyclerView with $count items")
    }
}
```

**3. Custom `ViewAction` для drag-жеста (упрощенный пример)**

На практике лучше использовать готовые `GeneralClickAction`/`GeneralSwipeAction`. Ниже — иллюстративный пример кастомного действия (координаты вычисляются относительно `View`).

```kotlin
fun dragToCenter(): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isDisplayed()

        override fun getDescription(): String = "drag from center to bottom-right"

        override fun perform(uiController: UiController, view: View) {
            val location = IntArray(2)
            view.getLocationOnScreen(location)

            val startX = (location[0] + view.width / 2).toFloat()
            val startY = (location[1] + view.height / 2).toFloat()
            val endX = startX + view.width / 4
            val endY = startY + view.height / 4

            val precision = floatArrayOf(1f, 1f)
            val down = MotionEvents.sendDown(uiController, floatArrayOf(startX, startY), precision).down
            uiController.loopMainThreadForAtLeast(100)
            MotionEvents.sendMovement(uiController, down, floatArrayOf(endX, endY))
            MotionEvents.sendUp(uiController, down, floatArrayOf(endX, endY))
        }
    }
}
```

**4. RecyclerView assertions**

```kotlin
// Проверка текста элемента на позиции 5
onView(withId(R.id.recycler))
    .perform(scrollToPosition<RecyclerView.ViewHolder>(5))
    .check(matches(hasDescendant(withText("Item 5"))))

// Действие по элементу, удовлетворяющему условию
onView(withId(R.id.recycler))
    .perform(
        actionOnItem<RecyclerView.ViewHolder>(
            hasDescendant(withText("Delete")),
            click()
        )
    )
```

### Лучшие Практики
- Не используйте `Thread.sleep()`; применяйте `IdlingResource` или настройки `IdlingPolicies`.
- Регистрируйте/разрегистрируйте ресурсы через `IdlingRegistry` в `@Before/@After`.
- Для корутин и асинхронных операций: инкремент/декремент вокруг запуска/завершения операции.
- Сужайте matchers; избегайте хрупких `withText()` без контекста.
- Пишите полезные сообщения в `describeTo()` для диагностики падений.

### Типичные Ошибки
- Забыли `unregister()` → утечки и ложные состояния idle для других тестов.
- Глобальные idling resources, влияющие на соседние тесты.
- Использование `sleep()` вместо синхронизации через Espresso и `IdlingResource`.

### Архитектура

**Espresso синхронизация:**
- Автоматически ждет, пока UI-поток станет idle.
- Проверяет все зарегистрированные `IdlingResource`.
- Учитывает отсутствие pending-анимаций.
- Снижает вероятность race conditions.

**Иерархия matcher-ов:**
- `BaseMatcher` — базовый класс, минимум type-safety.
- `TypeSafeMatcher` — type-safe для одного типа.
- `BoundedMatcher` — type-safe для конкретных `View`-подклассов.

**Контракт `ViewAction`:**
- `getConstraints()` — когда можно выполнить действие.
- `perform()` — что именно сделать.
- `getDescription()` — сообщение для ошибок.

См. также: [[c-android-testing]]

## Answer (EN)

### Key Concepts

- `IdlingResource` — sync with async operations; Espresso waits until the main thread and all registered resources are idle.
- Custom matchers — use `TypeSafeMatcher` / `BoundedMatcher` for type-safe view checks.
- Custom `ViewAction`s — for complex or non-standard UI interactions.
- `RecyclerViewActions` — helpers for scrolling, clicking, and asserting list items.

### Patterns

- Counting `IdlingResource` for network calls and coroutines.
- Type-safe matchers for `RecyclerView`.
- Minimal custom drag `ViewAction` (illustrative; prefer built-in swipe/click actions when possible).
- Focused assertions on specific items.

**1. Counting `IdlingResource` for network requests**

```kotlin
class NetworkIdlingResource : IdlingResource {
    @Volatile
    private var callback: IdlingResource.ResourceCallback? = null

    @Volatile
    private var activeRequests = 0

    override fun getName(): String = "NetworkIdlingResource"

    override fun isIdleNow(): Boolean = activeRequests == 0

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback) {
        this.callback = callback
    }

    @Synchronized
    fun increment() {
        activeRequests++
    }

    @Synchronized
    fun decrement() {
        if (activeRequests > 0) {
            activeRequests--
            if (isIdleNow()) {
                callback?.onTransitionToIdle()
            }
        }
    }
}

// Usage
@Test
fun testWithNetwork() {
    val idlingResource = NetworkIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)
    try {
        // production code must call increment()/decrement() around network calls
        onView(withId(R.id.button)).perform(click())
        onView(withText("Success")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

**2. Custom matcher for RecyclerView**

```kotlin
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
```

**Anti-example (less safe):**

```kotlin
fun badMatcher(count: Int) = object : BaseMatcher<View>() {
    override fun matches(item: Any?): Boolean =
        (item as? RecyclerView)?.adapter?.itemCount == count

    override fun describeTo(description: Description) {
        description.appendText("is RecyclerView with $count items")
    }
}
```

**3. Custom `ViewAction` for a drag gesture (simplified)**

```kotlin
fun dragToCenter(): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isDisplayed()

        override fun getDescription(): String = "drag from center to bottom-right"

        override fun perform(uiController: UiController, view: View) {
            val location = IntArray(2)
            view.getLocationOnScreen(location)

            val startX = (location[0] + view.width / 2).toFloat()
            val startY = (location[1] + view.height / 2).toFloat()
            val endX = startX + view.width / 4
            val endY = startY + view.height / 4

            val precision = floatArrayOf(1f, 1f)
            val down = MotionEvents.sendDown(uiController, floatArrayOf(startX, startY), precision).down
            uiController.loopMainThreadForAtLeast(100)
            MotionEvents.sendMovement(uiController, down, floatArrayOf(endX, endY))
            MotionEvents.sendUp(uiController, down, floatArrayOf(endX, endY))
        }
    }
}
```

**4. RecyclerView assertions**

```kotlin
// Check specific item text at position 5
onView(withId(R.id.recycler))
    .perform(scrollToPosition<RecyclerView.ViewHolder>(5))
    .check(matches(hasDescendant(withText("Item 5"))))

// Action on item matching a condition
onView(withId(R.id.recycler))
    .perform(
        actionOnItem<RecyclerView.ViewHolder>(
            hasDescendant(withText("Delete")),
            click()
        )
    )
```

### Best Practices
- Avoid `Thread.sleep()`; prefer `IdlingResource` or `IdlingPolicies`.
- Register/unregister idling resources via `IdlingRegistry` in `@Before/@After`.
- For coroutines/async work: increment/decrement around start/finish.
- Narrow matchers; avoid brittle bare `withText()`.
- Provide useful diagnostics in `describeTo()`.

### Common Pitfalls
- Missing `unregister()` → leaks and false idle for subsequent tests.
- Global idlers accidentally affecting unrelated tests.
- Using sleeps instead of Espresso synchronization.

### Architecture

**Espresso synchronization:**
- Automatically waits for the UI thread to be idle.
- Evaluates all registered `IdlingResource`s.
- Ensures no pending animations.
- Reduces race conditions in UI tests.

**Matcher hierarchy:**
- `BaseMatcher` — base class, minimal type-safety.
- `TypeSafeMatcher` — type-safe for a single type.
- `BoundedMatcher` — type-safe for specific `View` subclasses.

**`ViewAction` contract:**
- `getConstraints()` — when the action can be executed.
- `perform()` — what the action does.
- `getDescription()` — for error messages.

See also: [[c-android-testing]]

---

## Дополнительные Вопросы (RU)

- Как отлаживать нестабильные (flaky) Espresso-тесты?
- Когда стоит использовать UI Automator вместо Espresso?
- Как тестировать содержимое `WebView` с помощью Espresso?
- Каковы альтернативы `sleep()` в тестах?
- Как обрабатывать диалоги и фрагменты в тестах?

## Follow-ups

- How to debug flaky Espresso tests?
- When to use UI Automator instead of Espresso?
- How to test WebView content with Espresso?
- What are alternatives to sleep() in tests?
- How to handle dialogs and fragments?

## Ссылки (RU)

- [[q-android-testing-strategies--android--medium]]
- https://developer.android.com/training/testing/espresso/idling-resource
- https://developer.android.com/training/testing/espresso/recipes

## References

- [[q-android-testing-strategies--android--medium]]
- https://developer.android.com/training/testing/espresso/idling-resource
- https://developer.android.com/training/testing/espresso/recipes

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[q-android-testing-strategies--android--medium]]

### Связанные (тот Же уровень)

- [[q-android-testing-strategies--android--medium]]

### Продвинутые (сложнее)

- [[q-compose-ui-testing-advanced--android--hard]]

## Related Questions

### Prerequisites / Concepts

- [[q-android-testing-strategies--android--medium]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)
- [[q-compose-ui-testing-advanced--android--hard]]
