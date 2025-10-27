---
id: 20251012-122711
title: "What Happens When A New Activity Is Called Is Memory From The Old One Freed / Что происходит когда вызывается новая Activity освобождается ли память от старой"
aliases: ["What Happens When A New Activity Is Called Is Memory From The Old One Freed", "Что происходит когда вызывается новая Activity освобождается ли память от старой"]
topic: android
subtopics: [lifecycle, performance-memory]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-how-does-activity-lifecycle-work--android--medium, q-activity-navigation-how-it-works--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags:
  - android
  - android/lifecycle
  - android/performance-memory
  - lifecycle
  - performance-memory
  - difficulty/medium
---
# Вопрос (RU)

> Что происходит, когда запускается новая Activity? Освобождается ли память предыдущей?

# Question (EN)

> What happens when a new Activity is called? Is memory from the old one freed?

---

## Ответ (RU)

Когда запускается новая Activity, старая **не освобождает память немедленно**. Она проходит через переходы жизненного цикла и остаётся в back stack. Система может освободить её память позже при нехватке памяти.

### Последовательность жизненного цикла

При вызове `startActivity()`:

1. **Activity A** → `onPause()` (теряет фокус, частично видима)
2. **Activity B** → `onCreate()` → `onStart()` → `onResume()` (становится активной)
3. **Activity A** → `onStop()` (больше не видима, но остаётся в back stack)

**Ключевой момент**: Activity A остаётся в памяти в состоянии `STOPPED`, включая все её поля, ViewModel и выделенные ресурсы.

### Когда память освобождается

#### Явное завершение

```kotlin
override fun onDestroy() {
    super.onDestroy()

    if (isFinishing) {
        // ✅ Пользователь нажал Back или вызван finish()
        cleanupResources() // Постоянная очистка
    } else {
        // ❌ Система убила для освобождения памяти
        // НЕ делайте постоянную очистку - может быть восстановлена
    }
}
```

#### Системное уничтожение

Когда система испытывает нехватку памяти, она убивает остановленные Activity (от самой старой):

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Сохраняем критическое состояние перед возможным уничтожением
    outState.putInt("user_score", userScore)
}
```

При возврате пользователя создаётся **новый экземпляр** с восстановленным состоянием через `onCreate(savedInstanceState)`.

### Управление памятью в onStop()

```kotlin
class MemoryEfficientActivity : AppCompatActivity() {
    private var heavyData: Bitmap? = null

    override fun onStop() {
        super.onStop()
        // ✅ Освобождаем тяжёлые ресурсы когда Activity не видима
        heavyData?.recycle()
        heavyData = null
    }

    override fun onStart() {
        super.onStart()
        // ✅ Восстанавливаем при возврате
        if (heavyData == null) {
            heavyData = loadBitmap()
        }
    }
}
```

### ViewModel переживает onStop()

```kotlin
class DataViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Вызывается только при finish() или финальном Back
        // ❌ НЕ вызывается при onStop() или системном уничтожении
    }
}
```

**Критическое отличие**: ViewModel очищается только при **явном завершении** Activity, но переживает системное уничтожение для памяти.

### Резюме

| Сценарий | onDestroy() | Память освобождена | Восстановление |
|----------|-------------|-------------------|----------------|
| `startActivity()` | ❌ Не вызывается | ❌ Остаётся в back stack | Не требуется |
| Back/`finish()` | ✅ `isFinishing = true` | ✅ Да | Не будет |
| Системное уничтожение | ✅ `isFinishing = false` | ✅ Да | Через `savedInstanceState` |

**Ответ**: Память **не освобождается** при запуске новой Activity. Освобождается только при явном завершении или системной необходимости.

## Answer (EN)

When a new Activity is launched, the old Activity does **not** immediately free its memory. It transitions through lifecycle callbacks and remains in the back stack. The system may free its memory later under memory pressure.

### Lifecycle Sequence

When calling `startActivity()`:

1. **Activity A** → `onPause()` (loses focus, partially visible)
2. **Activity B** → `onCreate()` → `onStart()` → `onResume()` (becomes active)
3. **Activity A** → `onStop()` (no longer visible, but stays in back stack)

**Key point**: Activity A remains in memory in `STOPPED` state, including all its fields, ViewModel, and allocated resources.

### When Memory IS Freed

#### Explicit Termination

```kotlin
override fun onDestroy() {
    super.onDestroy()

    if (isFinishing) {
        // ✅ User pressed Back or finish() was called
        cleanupResources() // Permanent cleanup
    } else {
        // ❌ System killed for memory
        // DON'T do permanent cleanup - may be recreated
    }
}
```

#### System-Initiated Destruction

When the system needs memory, it kills stopped Activities (oldest first):

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Save critical state before potential destruction
    outState.putInt("user_score", userScore)
}
```

When the user returns, a **new instance** is created with state restored via `onCreate(savedInstanceState)`.

### Memory Management in onStop()

```kotlin
class MemoryEfficientActivity : AppCompatActivity() {
    private var heavyData: Bitmap? = null

    override fun onStop() {
        super.onStop()
        // ✅ Release heavy resources when Activity not visible
        heavyData?.recycle()
        heavyData = null
    }

    override fun onStart() {
        super.onStart()
        // ✅ Recreate on return
        if (heavyData == null) {
            heavyData = loadBitmap()
        }
    }
}
```

### ViewModel Survives onStop()

```kotlin
class DataViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Called only on finish() or final Back press
        // ❌ NOT called on onStop() or system-initiated kill
    }
}
```

**Critical distinction**: ViewModel is cleared only on **explicit termination**, but survives system-initiated kills for memory.

### Summary

| Scenario | onDestroy() | Memory Freed | Recovery |
|----------|-------------|--------------|----------|
| `startActivity()` | ❌ Not called | ❌ Stays in back stack | Not needed |
| Back/`finish()` | ✅ `isFinishing = true` | ✅ Yes | Won't happen |
| System kill | ✅ `isFinishing = false` | ✅ Yes | Via `savedInstanceState` |

**Answer**: Memory is **not freed** when a new Activity starts. It's only freed on explicit termination or system necessity.

## Follow-ups

- How does `onSaveInstanceState()` differ from ViewModel for state preservation?
- What happens to back stack when `FLAG_ACTIVITY_CLEAR_TOP` is used?
- How does `onTrimMemory()` callback help prevent system kills?
- What's the difference between configuration change and process death?

## References

- [Android Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Tasks and Back Stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack)

## Related Questions

### Prerequisites

- [[q-android-components-besides-activity--android--easy]] - Basic Android components

### Related

- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle handling
- [[q-how-does-activity-lifecycle-work--android--medium]] - Activity lifecycle details
- [[q-activity-navigation-how-it-works--android--medium]] - Navigation mechanics

### Advanced

- [[q-fragments-and-activity-relationship--android--hard]] - Fragment lifecycle
- Activity memory management and process death handling
