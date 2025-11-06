---
id: android-480
title: Custom View State Saving / Сохранение состояния Custom View
aliases: [Custom View State Saving, Сохранение состояния Custom View]
topic: android
subtopics:
  - lifecycle
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-activity-lifecycle-methods--android--medium
  - q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-10-30
tags: [android/lifecycle, android/ui-views, custom-view, difficulty/medium, state-management]
sources: []
---

# Вопрос (RU)
> Как реализовать сохранение состояния в Custom View при configuration changes?

# Question (EN)
> How to implement state saving in Custom View during configuration changes?

---

## Ответ (RU)

**State saving** в custom views обеспечивает выживание UI состояния при configuration changes (поворот экрана) и process death. Система вызывает `onSaveInstanceState()` и `onRestoreInstanceState()` автоматически, если View имеет ID.

### Концепция

Custom View должен самостоятельно управлять своим состоянием через `Parcelable`. Ключевые принципы:
- Использовать `BaseSavedState` для сохранения родительского состояния
- Реализовать `Parcelable.Creator` для десериализации
- Всегда вызывать `super` методы
- Проверять тип состояния при восстановлении

### Базовая Реализация

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
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

```kotlin
class ComplexView : View {
    private var items = mutableListOf<String>()
    private var mode = Mode.LIST

    override fun onSaveInstanceState(): Parcelable {
        return SavedState(super.onSaveInstanceState()).apply {
            this.items = ArrayList(this@ComplexView.items)
            this.modeName = this@ComplexView.mode.name
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            items = state.items.toMutableList()
            mode = Mode.valueOf(state.modeName)
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var items = ArrayList<String>()
        var modeName = ""

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            parcel.readStringList(items) // ✅ Поддержка списков
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

1. **ID обязателен** — View должен иметь `android:id` в layout
2. **BaseSavedState** — использовать для сохранения цепочки наследования
3. **Проверка типов** — state может быть null или другого типа
4. **Минимизация** — сохранять только критичное состояние (< 500 KB)

### Pitfalls

- ❌ Отсутствие ID у View — состояние не сохранится
- ❌ Забыть `super.onSaveInstanceState()` — потеря базового состояния
- ❌ Сохранение Context/Activity — утечки памяти
- ❌ Сохранение больших объектов — `TransactionTooLargeException`

## Answer (EN)

**State saving** in custom views ensures UI state survival during configuration changes (screen rotation) and process death. The system calls `onSaveInstanceState()` and `onRestoreInstanceState()` automatically if the View has an ID.

### Concept

Custom Views must manage their state through `Parcelable`. Key principles:
- Use `BaseSavedState` to preserve parent state
- Implement `Parcelable.Creator` for deserialization
- Always call `super` methods
- Check state type during restoration

### Basic Implementation

```kotlin
class CounterView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
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

```kotlin
class ComplexView : View {
    private var items = mutableListOf<String>()
    private var mode = Mode.LIST

    override fun onSaveInstanceState(): Parcelable {
        return SavedState(super.onSaveInstanceState()).apply {
            this.items = ArrayList(this@ComplexView.items)
            this.modeName = this@ComplexView.mode.name
        }
    }

    override fun onRestoreInstanceState(state: Parcelable?) {
        if (state is SavedState) {
            super.onRestoreInstanceState(state.superState)
            items = state.items.toMutableList()
            mode = Mode.valueOf(state.modeName)
        } else {
            super.onRestoreInstanceState(state)
        }
    }

    private class SavedState : BaseSavedState {
        var items = ArrayList<String>()
        var modeName = ""

        constructor(superState: Parcelable?) : super(superState)

        private constructor(parcel: Parcel) : super(parcel) {
            parcel.readStringList(items) // ✅ List support
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

1. **ID required** — View must have `android:id` in layout
2. **BaseSavedState** — use to preserve inheritance chain
3. **Type checking** — state can be null or different type
4. **Minimize** — save only critical state (< 500 KB)

### Pitfalls

- ❌ Missing View ID — state won't be saved
- ❌ Forgetting `super.onSaveInstanceState()` — losing base state
- ❌ Saving Context/Activity — memory leaks
- ❌ Saving large objects — `TransactionTooLargeException`

---

## Follow-ups

1. Как тестировать state restoration с process death?
2. В чём разница между `onSaveInstanceState` View и Activity?
3. Как сохранять состояние ViewGroup с множественными children?
4. Какие ограничения на размер Bundle для saved state?
5. Когда использовать ViewModel вместо View state saving?

## References

- [[c-lifecycle]]
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
- [Parcelable and Bundle](https://developer.android.com/reference/android/os/Parcelable)

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]]

### Related
- [[q-custom-view-lifecycle--android--medium]]
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]

### Advanced
- [[q-custom-viewgroup-layout--android--hard]]