---
id: 20251012-1227133
title: "Espresso Advanced Patterns / Espresso Advanced Паттерны"
topic: testing
difficulty: medium
status: draft
created: 2025-10-15
tags: [espresso, ui-testing, idling-resource, difficulty/medium]
---
# Espresso Advanced Patterns

**English**: Implement Espresso tests with IdlingResource, custom matchers, and ViewActions. Test RecyclerView and complex interactions.

**Russian**: Реализуйте Espresso тесты с IdlingResource, custom matchers и ViewActions. Тестируйте RecyclerView и сложные взаимодействия.

## Answer (EN)

Espresso is Android's UI testing framework for View-based UIs. Advanced usage requires understanding IdlingResources, custom matchers, and complex interaction patterns.

### Basic Espresso Setup

```kotlin
dependencies {
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.test.espresso:espresso-contrib:3.5.1")
    androidTestImplementation("androidx.test:runner:1.5.2")
    androidTestImplementation("androidx.test:rules:1.5.0")
}

@RunWith(AndroidJUnit4::class)
class LoginActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginWithValidCredentials() {
        onView(withId(R.id.email_input))
            .perform(typeText("user@example.com"))

        onView(withId(R.id.password_input))
            .perform(typeText("password123"))

        onView(withId(R.id.login_button))
            .perform(click())

        onView(withText("Welcome"))
            .check(matches(isDisplayed()))
    }
}
```

### IdlingResource for Async Operations

IdlingResources tell Espresso when app is idle (no async work):

```kotlin
// Simple IdlingResource
class SimpleIdlingResource : IdlingResource {
    @Volatile
    private var callback: IdlingResource.ResourceCallback? = null

    @Volatile
    private var isIdle = true

    override fun getName() = "SimpleIdlingResource"

    override fun isIdleNow() = isIdle

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback?) {
        this.callback = callback
    }

    fun setIdleState(isIdle: Boolean) {
        this.isIdle = isIdle
        if (isIdle) {
            callback?.onTransitionToIdle()
        }
    }
}

// Network IdlingResource
class OkHttpIdlingResource(
    private val name: String,
    private val dispatcher: Dispatcher
) : IdlingResource {
    @Volatile
    private var callback: IdlingResource.ResourceCallback? = null

    init {
        dispatcher.idleCallback = Runnable {
            callback?.onTransitionToIdle()
        }
    }

    override fun getName() = name

    override fun isIdleNow() = dispatcher.runningCallsCount() == 0

    override fun registerIdleTransitionCallback(callback: IdlingResource.ResourceCallback?) {
        this.callback = callback
    }
}

// Usage in test
@Test
fun testWithIdlingResource() {
    val idlingResource = SimpleIdlingResource()
    IdlingRegistry.getInstance().register(idlingResource)

    try {
        // Trigger async operation
        onView(withId(R.id.load_button)).perform(click())

        // Espresso automatically waits
        onView(withText("Data loaded")).check(matches(isDisplayed()))
    } finally {
        IdlingRegistry.getInstance().unregister(idlingResource)
    }
}
```

### CountingIdlingResource for Multiple Operations

```kotlin
class NetworkIdlingResource : CountingIdlingResource("NetworkIdlingResource") {
    fun beginOperation() {
        increment()
    }

    fun endOperation() {
        if (!isIdleNow) {
            decrement()
        }
    }
}

// Retrofit integration
class IdlingInterceptor(
    private val idlingResource: NetworkIdlingResource
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        idlingResource.beginOperation()
        try {
            return chain.proceed(chain.request())
        } finally {
            idlingResource.endOperation()
        }
    }
}

// Setup
val idlingResource = NetworkIdlingResource()
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(IdlingInterceptor(idlingResource))
    .build()
```

### Custom Matchers

```kotlin
// Match view with specific drawable
fun withDrawable(@DrawableRes id: Int): Matcher<View> {
    return object : BoundedMatcher<View, ImageView>(ImageView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has drawable with id $id")
        }

        override fun matchesSafely(imageView: ImageView): Boolean {
            val expectedDrawable = ContextCompat.getDrawable(imageView.context, id)
            return imageView.drawable.constantState == expectedDrawable?.constantState
        }
    }
}

// Match RecyclerView item count
fun withItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("RecyclerView with $count items")
        }

        override fun matchesSafely(recyclerView: RecyclerView): Boolean {
            return recyclerView.adapter?.itemCount == count
        }
    }
}

// Match text color
fun withTextColor(@ColorRes colorRes: Int): Matcher<View> {
    return object : BoundedMatcher<View, TextView>(TextView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has text color")
        }

        override fun matchesSafely(textView: TextView): Boolean {
            val expectedColor = ContextCompat.getColor(textView.context, colorRes)
            return textView.currentTextColor == expectedColor
        }
    }
}

// Usage
@Test
fun customMatchers_test() {
    onView(withId(R.id.image))
        .check(matches(withDrawable(R.drawable.ic_check)))

    onView(withId(R.id.recycler_view))
        .check(matches(withItemCount(5)))

    onView(withId(R.id.error_text))
        .check(matches(withTextColor(R.color.error_red)))
}
```

### Custom ViewActions

```kotlin
// Click on child view in RecyclerView item
fun clickChildViewWithId(@IdRes id: Int): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> {
            return isDisplayed()
        }

        override fun getDescription(): String {
            return "Click on child view with id $id"
        }

        override fun perform(uiController: UiController, view: View) {
            val childView = view.findViewById<View>(id)
            childView.performClick()
        }
    }
}

// Set progress on SeekBar
fun setProgress(progress: Int): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> {
            return isAssignableFrom(SeekBar::class.java)
        }

        override fun getDescription(): String {
            return "Set progress to $progress"
        }

        override fun perform(uiController: UiController, view: View) {
            (view as SeekBar).progress = progress
        }
    }
}

// Wait for view
fun waitForView(millis: Long): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> {
            return isDisplayed()
        }

        override fun getDescription(): String {
            return "Wait for $millis milliseconds"
        }

        override fun perform(uiController: UiController, view: View) {
            uiController.loopMainThreadForAtLeast(millis)
        }
    }
}

// Usage
@Test
fun customActions_test() {
    onView(withId(R.id.volume_seekbar))
        .perform(setProgress(50))

    onView(withId(R.id.loading_view))
        .perform(waitForView(2000))
}
```

### Testing RecyclerView

```kotlin
// Match item at position
fun atPosition(position: Int, itemMatcher: Matcher<View>): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has item at position $position: ")
            itemMatcher.describeTo(description)
        }

        override fun matchesSafely(recyclerView: RecyclerView): Boolean {
            val viewHolder = recyclerView.findViewHolderForAdapterPosition(position)
                ?: return false
            return itemMatcher.matches(viewHolder.itemView)
        }
    }
}

@Test
fun recyclerView_test() {
    // Scroll to position
    onView(withId(R.id.recycler_view))
        .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(10))

    // Click item at position
    onView(withId(R.id.recycler_view))
        .perform(
            RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                5,
                click()
            )
        )

    // Click item with specific text
    onView(withId(R.id.recycler_view))
        .perform(
            RecyclerViewActions.actionOnItem<RecyclerView.ViewHolder>(
                hasDescendant(withText("Item 3")),
                click()
            )
        )

    // Check item at position
    onView(withId(R.id.recycler_view))
        .check(
            matches(
                atPosition(
                    0,
                    hasDescendant(withText("First Item"))
                )
            )
        )

    // Click child view in item
    onView(withId(R.id.recycler_view))
        .perform(
            RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
                2,
                clickChildViewWithId(R.id.delete_button)
            )
        )
}
```

### Testing ViewPager

```kotlin
@Test
fun viewPager_swipe() {
    // Swipe to next page
    onView(withId(R.id.view_pager))
        .perform(swipeLeft())

    // Check current page
    onView(withText("Page 2"))
        .check(matches(isDisplayed()))

    // Swipe to previous
    onView(withId(R.id.view_pager))
        .perform(swipeRight())

    onView(withText("Page 1"))
        .check(matches(isDisplayed()))
}
```

### Testing Dialogs and Popups

```kotlin
@Test
fun dialog_test() {
    // Show dialog
    onView(withId(R.id.show_dialog_button))
        .perform(click())

    // Interact with dialog
    onView(withText("Dialog Title"))
        .inRoot(isDialog())
        .check(matches(isDisplayed()))

    onView(withText("Confirm"))
        .inRoot(isDialog())
        .perform(click())

    // Verify dialog dismissed
    onView(withText("Dialog Title"))
        .check(doesNotExist())
}

@Test
fun popup_test() {
    onView(withId(R.id.show_menu_button))
        .perform(click())

    // Match popup window
    onView(withText("Menu Item"))
        .inRoot(isPlatformPopup())
        .perform(click())
}
```

### Testing with Intent Verification

```kotlin
@Test
fun intent_verification() {
    // Setup intent verification
    Intents.init()

    try {
        onView(withId(R.id.share_button))
            .perform(click())

        // Verify intent sent
        intended(
            allOf(
                hasAction(Intent.ACTION_SEND),
                hasExtra(Intent.EXTRA_TEXT, "Share text")
            )
        )
    } finally {
        Intents.release()
    }
}

@Test
fun intent_stubbing() {
    val result = ActivityResult(Activity.RESULT_OK, Intent())

    Intents.init()

    try {
        // Stub external activity
        intending(hasComponent(CameraActivity::class.java.name))
            .respondWith(result)

        onView(withId(R.id.take_photo_button))
            .perform(click())

        // Verify intent was sent
        intended(hasComponent(CameraActivity::class.java.name))
    } finally {
        Intents.release()
    }
}
```

### Complex Interaction Patterns

```kotlin
@Test
fun complexInteraction_multiStep() {
    // Fill form
    onView(withId(R.id.name_input))
        .perform(
            typeText("John Doe"),
            closeSoftKeyboard()
        )

    onView(withId(R.id.email_input))
        .perform(
            typeText("john@example.com"),
            closeSoftKeyboard()
        )

    // Select from spinner
    onView(withId(R.id.country_spinner))
        .perform(click())

    onData(allOf(instanceOf(String::class.java), `is`("USA")))
        .perform(click())

    // Check checkbox
    onView(withId(R.id.terms_checkbox))
        .perform(click())
        .check(matches(isChecked()))

    // Submit
    onView(withId(R.id.submit_button))
        .perform(click())

    // Verify result
    onView(withText("Registration successful"))
        .check(matches(isDisplayed()))
}
```

### Best Practices

1. **Use IdlingResources** for async operations
2. **Create custom matchers** for reusable assertions
3. **Use custom ViewActions** for complex interactions
4. **Test RecyclerView** with proper position matching
5. **Handle dialogs and popups** with inRoot
6. **Verify intents** for external activity interactions
7. **Close keyboard** to prevent flaky tests
8. **Use meaningful descriptions** in custom matchers
9. **Clean up IdlingResources** in finally blocks
10. **Keep tests independent** and atomic

## Ответ (RU)

Espresso - это фреймворк для UI тестирования View-based интерфейсов Android.

[Полные примеры IdlingResource, custom matchers, ViewActions, тестирования RecyclerView и сложных взаимодействий приведены в английском разделе]

### Лучшие практики

1. **Используйте IdlingResources** для async операций
2. **Создавайте custom matchers** для переиспользуемых проверок
3. **Используйте custom ViewActions** для сложных взаимодействий
4. **Тестируйте RecyclerView** с правильным position matching
5. **Обрабатывайте dialogs и popups** с inRoot
6. **Проверяйте intents** для взаимодействия с внешними activity
7. **Закрывайте клавиатуру** чтобы предотвратить flaky тесты
8. **Используйте осмысленные описания** в custom matchers
9. **Очищайте IdlingResources** в finally блоках
10. **Держите тесты независимыми** и атомарными

---

## Related Questions

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing
- [[q-testing-compose-ui--android--medium]] - Testing
- [[q-compose-testing--android--medium]] - Testing
- [[q-robolectric-vs-instrumented--testing--medium]] - Testing
- [[q-screenshot-snapshot-testing--testing--medium]] - Testing

### Advanced (Harder)
- [[q-testing-coroutines-flow--testing--hard]] - Testing
