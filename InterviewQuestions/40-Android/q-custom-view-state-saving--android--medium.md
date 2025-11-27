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
status: draft
moc: moc-android
related:
  - c-custom-views
  - q-activity-lifecycle-methods--android--medium
  - q-custom-view-accessibility--android--medium
  - q-custom-view-attributes--android--medium
  - q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-11-10
tags: [android/lifecycle, android/ui-views, custom-view, difficulty/medium, state-management]
sources: []

date created: Saturday, November 1st 2025, 1:27:18 pm
date modified: Tuesday, November 25th 2025, 8:54:01 pm
---
# Вопрос (RU)
> Как реализовать сохранение состояния в Custom `View` при configuration changes?

# Question (EN)
> How to implement state saving in Custom `View` during configuration changes?

---

## Ответ (RU)

**State saving** в custom views обеспечивает выживание UI состояния при configuration changes (поворот экрана) и process death. Для `View`, которая имеет стабильный `id`, включена в иерархию, где родительский `ViewGroup` сохраняет состояние, и не отключено участие во вложенном сохранении (`isSaveFromParentEnabled == true`), система через механизм `ViewGroup` вызывает `onSaveInstanceState()` и `onRestoreInstanceState()`.

См. также: [[c-custom-views]]

### Концепция

Custom `View` должен самостоятельно управлять своим состоянием через `Parcelable`. Ключевые принципы:
- Использовать `BaseSavedState` (обычно `View.BaseSavedState`) для сохранения родительского состояния
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
class ComplexView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
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

1. **ID обязателен для автоматического механизма** — чтобы стандартный иерархический механизм сохранил состояние `View`, она должна иметь стабильный `android:id`, быть частью иерархии, где родительский `ViewGroup` сохраняет состояние, и участвовать в сохранении (`isSaveEnabled == true`, `isSaveFromParentEnabled == true`). В противном случае `View` можно сохранить только вручную.
2. **BaseSavedState** — использовать для сохранения цепочки наследования.
3. **Проверка типов** — state может быть `null` или другого типа.
4. **Минимизация** — сохранять только критичное состояние (ориентируйтесь на небольшой объём; слишком большие данные повышают риск `TransactionTooLargeException`).
5. **SaveEnabled** — убедиться, что `isSaveEnabled` не отключён (`android:saveEnabled="false"` выключит сохранение состояния `View`).

### Pitfalls

- Отсутствие ID у `View` — состояние не сохранится как часть стандартного механизма сохранения иерархии.
- `saveEnabled = false` или `isSaveFromParentEnabled = false` — отключает участие `View` в сохранении состояния родителем.
- Забыть `super.onSaveInstanceState()` / `super.onRestoreInstanceState()` — потеря базового состояния.
- Сохранение `Context`/`Activity` — утечки памяти.
- Сохранение больших объектов — риск `TransactionTooLargeException`.

## Answer (EN)

**State saving** in custom views ensures UI state survival during configuration changes (screen rotation) and process death. For a `View` that has a stable `id`, is included in a hierarchy whose parent `ViewGroup` participates in state saving, and does not opt out (`isSaveFromParentEnabled == true`), the system (via the parent) calls `onSaveInstanceState()` and `onRestoreInstanceState()` for it.

See also: [[c-custom-views]]

### Concept

Custom Views must manage their state through `Parcelable`. Key principles:
- Use `BaseSavedState` (commonly `View.BaseSavedState`) to preserve parent state
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
class ComplexView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {
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

1. **ID required for automatic mechanism** — for the standard hierarchy-based mechanism to save this `View`'s state, it must have a stable `android:id`, be part of a hierarchy where the parent `ViewGroup` saves states, and participate in saving (`isSaveEnabled == true`, `isSaveFromParentEnabled == true`). Otherwise, the view can only be saved manually.
2. **BaseSavedState** — use it to preserve the inheritance chain.
3. **Type checking** — state can be `null` or of a different type.
4. **Minimize** — save only critical state (aim for a small size; large payloads increase the risk of `TransactionTooLargeException`).
5. **SaveEnabled** — ensure `isSaveEnabled` is not disabled (`android:saveEnabled="false"` will prevent view state from being saved).

### Pitfalls

- Missing `View` ID — state will not be saved as part of the standard hierarchy-based mechanism.
- `saveEnabled = false` or `isSaveFromParentEnabled = false` — prevents this `View` from participating in parent-driven state saving.
- Forgetting `super.onSaveInstanceState()` / `super.onRestoreInstanceState()` — losing base state.
- Saving `Context`/`Activity` — memory leaks.
- Saving large objects — risk of `TransactionTooLargeException`.

---

## Дополнительные Вопросы (RU)

1. Как тестировать восстановление состояния Custom `View` при уничтожении процесса (process death)?
2. В чём разница между `onSaveInstanceState` у `View` и у `Activity`/`Fragment`?
3. Как подходить к сохранению состояния для `ViewGroup` с динамическими дочерними `View`?
4. Какие ограничения на размер данных для сохранения состояния и как избежать `TransactionTooLargeException`?
5. В каких случаях лучше использовать `ViewModel` или `SavedStateHandle` вместо механизма сохранения состояния `View`?

## Follow-ups (EN)

1. How can you test restoring the state of a Custom `View` after process death?
2. What is the difference between `onSaveInstanceState` in a `View` versus in an `Activity`/`Fragment`?
3. How should you handle state saving for a `ViewGroup` with dynamic child `View`s?
4. What are the data size limitations for state saving and how to avoid `TransactionTooLargeException`?
5. In which cases is it better to use `ViewModel` or `SavedStateHandle` instead of the `View` state saving mechanism?

## References

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
