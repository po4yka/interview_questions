---
id: 20251021-190000
title: Custom View State Saving / Сохранение состояния Custom View
aliases: ["Custom View State Saving", "Сохранение состояния Custom View"]
topic: android
subtopics: [lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-custom-view-lifecycle--android--medium]
created: 2025-10-21
updated: 2025-10-29
tags: [android/lifecycle, android/ui-views, difficulty/medium]
sources: []
---
# Вопрос (RU)
> Как реализовать сохранение состояния в Custom View при configuration changes?

# Question (EN)
> How to implement state saving in Custom View during configuration changes?

---

## Ответ (RU)

**State saving** в custom views обеспечивает выживание UI при configuration changes и process death. Система вызывает `onSaveInstanceState()` и `onRestoreInstanceState()` автоматически.

### Базовая Реализация

**Минимальный пример с BaseSavedState:**

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {
    private var count = 0

    // ✅ Сохранение состояния
    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.count = this@CounterView.count
        }
    }

    // ✅ Восстановление состояния
    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            count = state.count
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
            override fun createFromParcel(p: Parcel) = SavedState(p)
            override fun newArray(size: Int) = arrayOfNulls<SavedState>(size)
        }
    }
}
```

### Сложные Типы Данных

**Сохранение списков и enum:**

```kotlin
class ComplexView : View {
    private var items = mutableListOf<String>()
    private var mode = Mode.LIST

    override fun onSaveInstanceState(): Parcelable {
        return SavedState(super.onSaveInstanceState()).apply {
            this.items = this@ComplexView.items
            this.modeName = this@ComplexView.mode.name
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            items = state.items
            mode = Mode.valueOf(state.modeName)
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var items = mutableListOf<String>()
        var modeName = ""

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            parcel.readStringList(items) // ✅ Списки
            modeName = parcel.readString() ?: ""
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeStringList(items)
            out.writeString(modeName)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(p: Parcel) = SavedState(p)
            override fun newArray(size: Int) = arrayOfNulls<SavedState>(size)
        }
    }

    enum class Mode { LIST, GRID }
}
```

### Ключевые Правила

1. **Всегда вызывать super** - сохраняет базовое состояние View
2. **Использовать BaseSavedState** - правильная реализация для View
3. **Проверять типы** - state может быть null или другого типа
4. **Минимизировать данные** - только критичное состояние

### Pitfalls

- ❌ Забыть `super.onSaveInstanceState()`
- ❌ Сохранение Context/Activity (утечки памяти)
- ❌ Неправильный CREATOR
- ❌ Отсутствие проверки типа при восстановлении

## Answer (EN)

**State saving** in custom views ensures UI survival during configuration changes and process death. The system calls `onSaveInstanceState()` and `onRestoreInstanceState()` automatically.

### Basic Implementation

**Minimal example with BaseSavedState:**

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : View(context, attrs) {
    private var count = 0

    // ✅ Save state
    override fun onSaveInstanceState(): Parcelable {
        val superState = super.onSaveInstanceState()
        return SavedState(superState).apply {
            this.count = this@CounterView.count
        }
    }

    // ✅ Restore state
    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            count = state.count
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
            override fun createFromParcel(p: Parcel) = SavedState(p)
            override fun newArray(size: Int) = arrayOfNulls<SavedState>(size)
        }
    }
}
```

### Complex Data Types

**Saving lists and enums:**

```kotlin
class ComplexView : View {
    private var items = mutableListOf<String>()
    private var mode = Mode.LIST

    override fun onSaveInstanceState(): Parcelable {
        return SavedState(super.onSaveInstanceState()).apply {
            this.items = this@ComplexView.items
            this.modeName = this@ComplexView.mode.name
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            items = state.items
            mode = Mode.valueOf(state.modeName)
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var items = mutableListOf<String>()
        var modeName = ""

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            parcel.readStringList(items) // ✅ Lists
            modeName = parcel.readString() ?: ""
        }

        override fun writeToParcel(out: Parcel, flags: Int) {
            super.writeToParcel(out, flags)
            out.writeStringList(items)
            out.writeString(modeName)
        }

        companion object CREATOR : Parcelable.Creator<SavedState> {
            override fun createFromParcel(p: Parcel) = SavedState(p)
            override fun newArray(size: Int) = arrayOfNulls<SavedState>(size)
        }
    }

    enum class Mode { LIST, GRID }
}
```

### Key Rules

1. **Always call super** - saves base View state
2. **Use BaseSavedState** - proper implementation for View
3. **Check types** - state can be null or different type
4. **Minimize data** - only critical state

### Pitfalls

- ❌ Forgetting `super.onSaveInstanceState()`
- ❌ Saving Context/Activity (memory leaks)
- ❌ Incorrect CREATOR implementation
- ❌ Missing type check when restoring

---

## Follow-ups

1. How to handle state saving in ViewGroups with multiple children?
2. What are the size limits for saved state bundles?
3. How to test state restoration with process death?
4. When to use Serializable vs Parcelable for custom objects?
5. How does state saving interact with view recycling in RecyclerView?

## References

- [[c-lifecycle]]
- [[c-state-management]]
- [[c-parcelable]]
- [Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Parcelable Documentation](https://developer.android.com/reference/android/os/Parcelable)

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]]

### Related (Same Level)
- [[q-custom-view-lifecycle--android--medium]]
- [[q-fragment-savedinstancestate--android--medium]]

### Advanced (Harder)
- [[q-custom-viewgroup-layout--android--hard]]
