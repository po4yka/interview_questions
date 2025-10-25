---
id: 20251021-190000
title: Custom View State Saving / Сохранение состояния Custom View
aliases:
- Custom View State Saving
- Сохранение состояния Custom View
topic: android
subtopics:
- ui-views
- lifecycle
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-custom-view-lifecycle--android--medium
- q-activity-lifecycle-methods--android--medium
created: 2025-10-21
updated: 2025-10-21
tags:
- android/ui-views
- android/lifecycle
- difficulty/medium
source: https://developer.android.com/guide/components/activities/activity-lifecycle
source_note: Official activity lifecycle guide
---

# Вопрос (RU)
> Сохранение состояния Custom View?

# Question (EN)
> Custom View State Saving?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### State Saving Theory

**State saving** in custom views ensures UI survival during configuration changes (screen rotation, language change) and process death. Android system automatically calls state saving methods during specific events.

Based on [[c-lifecycle]], c-state-management, and c-parcelable.

**Key principles**:
- **Automatic invocation** - system calls onSaveInstanceState() when needed
- **Parcelable interface** - state must be serializable
- **BaseSavedState inheritance** - proper implementation for View
- **Configuration changes** - screen rotation, language change, themes

### When State Saving Happens

**Triggered by:**
- Screen rotation
- Language change
- Multi-window mode
- Theme change
- Process death (low memory)

**Not triggered by:**
- Back navigation
- Activity finish
- App killed by user

### Basic State Saving Implementation

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {

    private var count = 0

    fun increment() {
        count++
        invalidate()
    }

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

    private class SavedState : BaseSavedState {
        var count = 0

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

### Complex Data Types

**Theory**: For complex data types (lists, objects, enums) proper serialization must be implemented. Use writeTypedList/readTypedList for object lists, writeSerializable/readSerializable for Serializable objects.

```kotlin
class ComplexView : View {

    private var items = mutableListOf<Item>()
    private var selectedItem: Item? = null
    private var viewMode = ViewMode.LIST

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.items = this@ComplexView.items
            this.selectedItem = this@ComplexView.selectedItem
            this.viewMode = this@ComplexView.viewMode.name
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            items = state.items
            selectedItem = state.selectedItem
            viewMode = ViewMode.valueOf(state.viewMode)
            invalidate()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var items = mutableListOf<Item>()
        var selectedItem: Item? = null
        var viewMode = ""

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            parcel.readTypedList(items, Item.CREATOR)
            selectedItem = parcel.readTypedObject(Item.CREATOR)
            viewMode = parcel.readString() ?: ""
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeTypedList(items)
            out.writeTypedObject(selectedItem, flags)
            out.writeString(viewMode)
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

    data class Item(val id: Int, val name: String) : Parcelable {
        override fun writeToParcel(out: Parcel, flags: Int) {
            out.writeInt(id)
            out.writeString(name)
        }

        override fun describeContents(): Int = 0

        companion object CREATOR : Parcelable.Creator<Item> {
            override fun createFromParcel(parcel: Parcel): Item {
                return Item(parcel.readInt(), parcel.readString() ?: "")
            }

            override fun newArray(size: Int): Array<Item?> {
                return arrayOfNulls(size)
            }
        }
    }

    enum class ViewMode { LIST, GRID }
}
```

### Handling Configuration Changes

**Theory**: Configuration changes (configChanges) can be handled at Activity or View level. View can save state automatically, but for complex cases additional logic is needed.

```kotlin
class ConfigAwareView : View {

    private var isLandscape = false
    private var savedScrollPosition = 0

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)

        val wasLandscape = isLandscape
        isLandscape = newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE

        if (wasLandscape != isLandscape) {
            // Orientation changed - adapt UI
            adaptToOrientation()
        }
    }

    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.isLandscape = this@ConfigAwareView.isLandscape
            this.scrollPosition = this@ConfigAwareView.savedScrollPosition
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            isLandscape = state.isLandscape
            savedScrollPosition = state.scrollPosition
            restoreScrollPosition()
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private fun adaptToOrientation() {
        // Adapt UI to new orientation
        requestLayout()
    }

    private fun restoreScrollPosition() {
        // Restore scroll position
    }

    private class SavedState : BaseSavedState {
        var isLandscape = false
        var scrollPosition = 0

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            isLandscape = parcel.readByte() != 0.toByte()
            scrollPosition = parcel.readInt()
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeByte(if (isLandscape) 1 else 0)
            out.writeInt(scrollPosition)
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

### Best Practices

1. **Always call super.onSaveInstanceState()** - saves base View state
2. **Use BaseSavedState** - proper implementation for View
3. **Implement Parcelable.Creator** - mandatory for Parcelable
4. **Handle null states** - check types in onRestoreInstanceState()
5. **Save only necessary data** - don't save temporary data
6. **Test on configuration changes** - screen rotation, language change
7. **Use correct data types** - primitives, Parcelable, Serializable

### Pitfalls

- **Don't forget super calls** - can break base functionality
- **Implement Parcelable correctly** - errors in CREATOR can cause crashes
- **Don't save Context references** - can cause memory leaks
- **Check types when restoring** - state can be null or different type
- **Test edge cases** - rapid screen rotations, low memory

---

## Follow-ups

- How to handle state saving in ViewGroups?
- What are the performance implications of state saving?
- How to implement custom Parcelable for complex objects?
- When to use Serializable vs Parcelable?

## References

- [Activity Lifecycle Guide](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Parcelable Documentation](https://developer.android.com/reference/android/os/Parcelable)

## Related Questions

### Prerequisites (Easier)
- [[q-custom-drawable-implementation--android--medium]]

### Related (Same Level)
- [[q-custom-view-lifecycle--android--medium]]
- [[q-activity-lifecycle-methods--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
