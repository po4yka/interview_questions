---
id: 20251012-1227116
title: "Custom View State Saving / Сохранение состояния кастомных View"
topic: android
difficulty: medium
status: draft
created: 2025-10-13
tags: [views, state-management, lifecycle, android-framework, android/ui-views, android/lifecycle, difficulty/medium]
moc: moc-android
related: []
subtopics: [ui-views, lifecycle]
---
# Custom View State Saving

# Question (EN)
> How do you save and restore state in custom views? Explain the state saving mechanism, handling configuration changes, and implementing Parcelable state classes properly.

# Вопрос (RU)
> Как сохранять и восстанавливать состояние в пользовательских view? Объясните механизм сохранения состояния, обработку изменений конфигурации и правильную реализацию Parcelable классов состояния.

---

## Answer (EN)

**State saving** in custom views ensures your UI survives configuration changes (rotation, language change, etc.) and process death. Implementing this correctly is essential for a seamless user experience.

### When State Saving Happens

**Triggered by:**
- Screen rotation
- Language change
- Multi-window mode
- Theme change
- Process death (low memory)

**Not triggered by:**
- Back navigation
- Finish activity
- App killed by user

---

### 1. Basic State Saving

Override `onSaveInstanceState()` and `onRestoreInstanceState()`.

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var count: Int = 0

    fun increment() {
        count++
        invalidate()
    }

    //  Save state
    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()

        val savedState = SavedState(superState).apply {
            this.count = this@CounterView.count
        }

        return savedState
    }

    //  Restore state
    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            count = state.count
            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    //  Custom SavedState class
    private class SavedState : BaseSavedState {
        var count: Int = 0

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            count = parcel.readInt()
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeInt(count)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(parcel: Parcel): SavedState {
                return SavedState(parcel)
            }

            override fun newArray(size: Int): Array<SavedState?> {
                return arrayOfNulls(size)
            }
        }
    }
}
```

**Important:** Always call `super.onSaveInstanceState()` and wrap it in your custom state!

---

### 2. Requiring Unique ID

State saving requires a unique view ID.

```kotlin
init {
    //  Check if ID is set
    if (id == View.NO_ID) {
        Log.w("CounterView", "View must have an ID to save state")
        // Optionally assign a default ID
        id = View.generateViewId()
    }
}
```

**XML:**
```xml
<!--  With ID - state will be saved -->
<com.example.ui.CounterView
    android:id="@+id/counter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!--  Without ID - state will be lost! -->
<com.example.ui.CounterView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

---

### 3. Complex State with Multiple Properties

```kotlin
class ProgressView : View {

    private var progress: Float = 0f
    private var progressColor: Int = Color.BLUE
    private var label: String = ""
    private var isAnimating: Boolean = false

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()

        return SavedState(superState).apply {
            this.progress = this@ProgressView.progress
            this.progressColor = this@ProgressView.progressColor
            this.label = this@ProgressView.label
            this.isAnimating = this@ProgressView.isAnimating
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)

            progress = state.progress
            progressColor = state.progressColor
            label = state.label
            isAnimating = state.isAnimating

            // Resume animation if needed
            if (isAnimating) {
                startAnimation()
            }

            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var progress: Float = 0f
        var progressColor: Int = 0
        var label: String = ""
        var isAnimating: Boolean = false

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            progress = parcel.readFloat()
            progressColor = parcel.readInt()
            label = parcel.readString() ?: ""
            isAnimating = parcel.readByte() != 0.toByte()
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeFloat(progress)
            out.writeInt(progressColor)
            out.writeString(label)
            out.writeByte(if (isAnimating) 1 else 0)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(parcel: Parcel) = SavedState(parcel)
            override fun newArray(size: Int) = arrayOfNulls<SavedState>(size)
        }
    }
}
```

---

### 4. Using @Parcelize (Kotlin)

Simplify Parcelable implementation with Kotlin Android Extensions.

```kotlin
import kotlinx.parcelize.Parcelize
import android.os.Parcelable

class ModernView : View {

    private var progress: Float = 0f
    private var label: String = ""

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState, progress, label)
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            progress = state.progress
            label = state.label
            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    //  Much simpler with @Parcelize!
    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val progress: Float,
        val label: String
    ) : BaseSavedState(superState), Parcelable
}
```

**Add to build.gradle:**
```gradle
plugins {
    id 'kotlin-parcelize'
}
```

---

### 5. Saving Collections

```kotlin
class ChartView : View {

    private val dataPoints = mutableListOf<DataPoint>()

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState, ArrayList(dataPoints))
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            dataPoints.clear()
            dataPoints.addAll(state.dataPoints)
            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    @Parcelize
    data class DataPoint(
        val x: Float,
        val y: Float,
        val label: String
    ) : Parcelable

    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val dataPoints: ArrayList<DataPoint>
    ) : BaseSavedState(superState), Parcelable
}
```

---

### 6. State Saving in ViewGroups

ViewGroups must handle their own state AND children's state.

```kotlin
class CustomLayout : ViewGroup {

    private var layoutMode: LayoutMode = LayoutMode.GRID

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState, layoutMode)
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            layoutMode = state.layoutMode
            requestLayout()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    // Enable state saving for children
    override fun dispatchSaveInstanceState(container: SparseArray<Parcelable>) {
        // Save children's state
        dispatchFreezeSelfOnly(container)
    }

    override fun dispatchRestoreInstanceState(container: SparseArray<Parcelable>) {
        // Restore children's state
        dispatchThawSelfOnly(container)
    }

    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val layoutMode: LayoutMode
    ) : BaseSavedState(superState), Parcelable

    enum class LayoutMode {
        GRID, LIST
    }
}
```

---

### 7. Handling Large State

For large data, don't save in view state—use ViewModel instead.

```kotlin
class LargeDataView : View {

    //  DON'T save large data in view state
    // private val largeList = List(10000) { /* ... */ }

    //  DO save reference/ID only
    private var dataSetId: String? = null

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        // Only save ID, not actual data
        return SavedState(superState, dataSetId)
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            dataSetId = state.dataSetId

            // Reload data from ViewModel/Repository
            dataSetId?.let { id ->
                loadDataSet(id)
            }
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val dataSetId: String?
    ) : BaseSavedState(superState), Parcelable

    private fun loadDataSet(id: String) {
        // Load from ViewModel or Repository
    }
}
```

---

### 8. State Saving with Animations

Handle animation state properly.

```kotlin
class AnimatedView : View {

    private var animator: ValueAnimator? = null
    private var animatedValue: Float = 0f
    private var targetValue: Float = 100f
    private var isAnimating: Boolean = false

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()

        // Save current animated value, not target
        val currentValue = if (isAnimating) {
            animator?.animatedValue as? Float ?: animatedValue
        } else {
            animatedValue
        }

        return SavedState(superState, currentValue, targetValue, isAnimating)
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)

            animatedValue = state.currentValue
            targetValue = state.targetValue

            if (state.isAnimating) {
                // Resume animation from saved position
                animateTo(targetValue, startValue = animatedValue)
            }

            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private fun animateTo(target: Float, startValue: Float = animatedValue) {
        animator?.cancel()

        animator = ValueAnimator.ofFloat(startValue, target).apply {
            duration = 500
            addUpdateListener { animation ->
                animatedValue = animation.animatedValue as Float
                invalidate()
            }
            start()
        }

        isAnimating = true
    }

    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val currentValue: Float,
        val targetValue: Float,
        val isAnimating: Boolean
    ) : BaseSavedState(superState), Parcelable
}
```

---

### 9. Testing State Saving

```kotlin
@RunWith(AndroidJUnit4::class)
class StateRestorationTest {

    @Test
    fun testStateSaving() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val view = CounterView(context).apply {
            id = View.generateViewId() // Required!
        }

        // Set state
        view.increment()
        view.increment()
        view.increment()

        // Save state
        val state = view.onSaveInstanceState()

        // Create new view and restore
        val newView = CounterView(context).apply {
            id = view.id // Must have same ID
        }
        newView.onRestoreInstanceState(state)

        // Verify state was restored
        // (You'd need to expose count or verify visually)
    }

    @Test
    fun testRotation() {
        val scenario = ActivityScenario.launch(MainActivity::class.java)

        // Interact with view
        onView(withId(R.id.counter))
            .perform(click())
            .perform(click())

        // Rotate device
        scenario.onActivity { activity ->
            activity.requestedOrientation =
                ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
        }

        // Verify state survived
        onView(withId(R.id.counter))
            .check(matches(withText("Count: 2")))
    }
}
```

---

### 10. Common Mistakes

** Not calling super:**
```kotlin
override fun onSaveInstanceState(): Parcelable {
    // Missing super call!
    return SavedState(null, progress)
}
```

** Always call super:**
```kotlin
override fun onSaveInstanceState(): Parcelable {
    val superState = super.onSaveInstanceState() // 
    return SavedState(superState, progress)
}
```

** No view ID:**
```xml
<!-- State won't be saved! -->
<com.example.ui.CounterView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

** With ID:**
```xml
<com.example.ui.CounterView
    android:id="@+id/counter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

** Saving too much data:**
```kotlin
data class SavedState(
    val superState: Parcelable?,
    val hugeList: List<LargeObject> //  TransactionTooLargeException!
) : BaseSavedState(superState), Parcelable
```

** Save references only:**
```kotlin
data class SavedState(
    val superState: Parcelable?,
    val dataId: String //  Just the ID
) : BaseSavedState(superState), Parcelable
```

---

### 11. Best Practices

**1. Always save critical UI state**
```kotlin
//  Save user input, selections, scroll position
override fun onSaveInstanceState(): Parcelable {
    val superState = super.onSaveInstanceState()
    return SavedState(superState, selectedIndex, scrollY, inputText)
}
```

**2. Don't save transient state**
```kotlin
//  Don't save temporary UI states
// - Loading indicators
// - Error messages (should be recomputed)
// - Temporary animations
```

**3. Use ViewModel for complex state**
```kotlin
// ViewModel survives configuration changes automatically
class MyViewModel : ViewModel() {
    val largeDataSet = MutableLiveData<List<Data>>()
}

// View only saves minimal state
class MyView : View {
    override fun onSaveInstanceState(): Parcelable {
        // Just save scroll position, selection, etc.
        // Large data lives in ViewModel
    }
}
```

**4. Test with "Don't keep activities"**
```
Developer Options → Don't keep activities → ON
```
This simulates process death on every background.

**5. Size limits**
```kotlin
// Parcelable transaction size limit: ~1MB total
// Keep individual view state < 50KB
// For larger data, use:
// - ViewModel (config changes)
// - Saved State Handle (process death)
// - Persistent storage (database, files)
```

---

### 12. State Saving Checklist

**Required:**
-  Override `onSaveInstanceState()`
-  Override `onRestoreInstanceState()`
-  Call `super.onSaveInstanceState()`
-  Wrap super state in custom state
-  View must have unique ID
-  Implement Parcelable correctly

**Recommended:**
-  Use `@Parcelize` for simplicity
-  Keep state size small (< 50KB)
-  Test with "Don't keep activities"
-  Test rotation in all screens
-  Use ViewModel for large/complex data

**Avoid:**
-  Saving transient UI state
-  Saving data available from other sources
-  Exceeding size limits
-  Forgetting to call super
-  Views without IDs

---

### Summary

**State saving basics:**
1. Override `onSaveInstanceState()` and `onRestoreInstanceState()`
2. Wrap super state in custom BaseSavedState subclass
3. Implement Parcelable (use @Parcelize for simplicity)
4. Ensure view has unique ID

**What to save:**
- User input and selections
- Scroll positions
- Expanded/collapsed states
- Custom view state (progress, colors, etc.)

**What NOT to save:**
- Transient states (loading indicators)
- Large data sets (use ViewModel)
- Data available from other sources
- Non-user-facing state

**Testing:**
- Enable "Don't keep activities"
- Test all configuration changes
- Verify state on process death
- Check for TransactionTooLargeException

---

## Ответ (RU)

**Сохранение состояния** в пользовательских view гарантирует, что ваш UI переживает изменения конфигурации (поворот, смена языка и т.д.) и смерть процесса.

### Когда происходит сохранение состояния

**Триггеры:**
- Поворот экрана
- Смена языка
- Режим многозадачности
- Смена темы
- Смерть процесса (мало памяти)

### Базовое сохранение состояния

```kotlin
class CounterView : View {

    private var count: Int = 0

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.count = this@CounterView.count
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            count = state.count
            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    @Parcelize
    data class SavedState(
        val superState: Parcelable?,
        val count: Int = 0
    ) : BaseSavedState(superState), Parcelable
}
```

### Требования

**View должен иметь уникальный ID:**
```xml
<!--  С ID - состояние сохранится -->
<com.example.ui.CounterView
    android:id="@+id/counter"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />

<!--  Без ID - состояние потеряется! -->
<com.example.ui.CounterView
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
```

### Что сохранять

 **Сохранять:**
- Пользовательский ввод и выборы
- Позиции прокрутки
- Раскрытые/свёрнутые состояния
- Состояние custom view (прогресс, цвета и т.д.)

 **НЕ сохранять:**
- Временные состояния (индикаторы загрузки)
- Большие наборы данных (использовать ViewModel)
- Данные, доступные из других источников

### Checklist

-  Переопределить `onSaveInstanceState()`
-  Переопределить `onRestoreInstanceState()`
-  Вызвать `super.onSaveInstanceState()`
-  Обернуть super state в custom state
-  View должен иметь уникальный ID
-  Корректно реализовать Parcelable
-  Использовать `@Parcelize` для упрощения
-  Держать размер состояния малым (< 50KB)
