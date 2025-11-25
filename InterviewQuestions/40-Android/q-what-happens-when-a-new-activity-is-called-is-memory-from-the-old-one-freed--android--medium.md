---
id: android-151
title: What Happens When A New Activity Is Called Is Memory From The Old One Freed / Что происходит когда вызывается новая Activity освобождается ли память от старой
aliases: [What Happens When A New Activity Is Called Is Memory From The Old One Freed, Что происходит когда вызывается новая Activity освобождается ли память от старой]
topic: android
subtopics:
  - lifecycle
  - performance-memory
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-lifecycle
  - c-memory-management
  - q-activity-lifecycle-methods--android--medium
  - q-activity-navigation-how-it-works--android--medium
  - q-how-does-activity-lifecycle-work--android--medium
  - q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium
  - q-how-to-pass-data-from-one-activity-to-another--android--medium
  - q-how-to-pass-data-from-one-fragment-to-another--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android, android/lifecycle, android/performance-memory, difficulty/medium, lifecycle, performance-memory]

date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)

> Что происходит, когда запускается новая `Activity`? Освобождается ли память предыдущей?

# Question (EN)

> What happens when a new `Activity` is called? Is memory from the old one freed?

---

## Ответ (RU)

Когда запускается новая `Activity`, старая **не освобождает память немедленно автоматически только из-за перехода**. Она проходит через переходы жизненного цикла и остаётся в back stack. Память объекта `Activity` и её полей остаётся занята, пока:

- `Activity` находится в состоянии `STOPPED` и на неё есть ссылки (например, в back stack),
- или пока жив целый процесс приложения.

Система может освободить эту память позже: либо когда `Activity` будет завершена (`finish()` / Back), либо при уничтожении процесса из-за нехватки памяти.

### Последовательность Жизненного Цикла

При вызове `startActivity()` (обычный сценарий, `Activity` B полностью перекрывает A):

1. **`Activity` A** → `onPause()` (теряет фокус, может быть частично видима)
2. **`Activity` B** → `onCreate()` → `onStart()` → `onResume()` (становится активной)
3. **`Activity` A** → `onStop()` (больше не видима, но остаётся в back stack)

**Ключевой момент**: `Activity` A остаётся в памяти в состоянии `STOPPED`, включая её поля и выделенные ресурсы. Объект `ViewModel`, если используется, также продолжает существовать, пока жизненный цикл владельца (`Activity`/`Fragment`) не будет окончательно завершён.

### Когда Память Освобождается

#### Явное Завершение

```kotlin
override fun onDestroy() {
    super.onDestroy()

    if (isFinishing) {
        // ✅ Пользователь нажал Back или вызван finish()
        cleanupResources() // Очистка, т.к. Activity больше не вернётся
    } else {
        // ✅ Например, конфигурационное изменение или повторное создание
        // Activity. Объект будет уничтожен, должен быть освобождён его state.
        // ВАЖНО: долгоживущие данные нужно сохранять ДО этого (onPause/onStop
        // или onSaveInstanceState), а не полагаться на этот блок.
    }
}
```

#### Системное Уничтожение Процесса

Когда системе не хватает памяти, она может убить процесс с остановленными `Activity` целиком.

Перед возможным уничтожением вызывается `onSaveInstanceState()` (не гарантируется в 100% случаев, но в типичных сценариях вызывается):

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Сохраняем критическое состояние перед возможным уничтожением процесса
    outState.putInt("user_score", userScore)
}
```

При возврате пользователя создаётся **новый экземпляр** `Activity` с восстановленным состоянием через `onCreate(savedInstanceState)`. Все прошлые объекты (`Activity`, её `ViewModel`, поля) к этому моменту уже уничтожены вместе с процессом.

### Управление Памятью В onStop()

```kotlin
class MemoryEfficientActivity : AppCompatActivity() {
    private var heavyData: Bitmap? = null

    override fun onStop() {
        super.onStop()
        // ✅ Освобождаем тяжёлые ссылки, когда Activity не видима,
        // чтобы уменьшить риск убийства процесса
        heavyData?.recycle() // В современных реализациях часто достаточно убрать ссылки
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

### `ViewModel` И Жизненный Цикл

```kotlin
class DataViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Вызывается, когда владелец ViewModel (Activity/Fragment)
        // окончательно уничтожен и не будет пересоздан с тем же scope.
        // Например: пользователь ушёл назад (finish()) или scope был сменён.
        // ❌ Не вызывается просто при onStop().
    }
}
```

**Важно**:

- `ViewModel` не переживает уничтожение процесса: при процесс-death создаётся новый экземпляр `Activity` и новый `ViewModel`.
- Для восстановления после процесс-death/конфигурационных изменений используются `savedInstanceState`, persistent storage и/или SavedStateHandle.

### Резюме

| Сценарий | onDestroy() | Память (объекты `Activity`/`ViewModel`) | Восстановление |
|----------|-------------|--------------------------------------|----------------|
| `startActivity()` (A → B, без finish A) | Для A: ❌ обычно не вызывается сразу | A и её `ViewModel` остаются в памяти (`STOPPED`) пока жив процесс | Не требуется |
| Back/`finish()` | ✅ `isFinishing = true` | ✅ Объекты A и её `ViewModel` становятся доступны для GC | Не будет |
| Конфигурационное изменение | ✅ `isFinishing = false` | ✅ Текущие объекты уничтожаются, создаются новые; состояние восстанавливается | Через `savedInstanceState`/SavedStateHandle и др. |
| Убийство процесса системой | (Колбэки не вызываются в момент убийства) | ✅ Вся память процесса освобождена | Новый процесс, восстановление через `savedInstanceState` (если было), persistence |

**Ответ**: При запуске новой `Activity` память предыдущей **сразу не освобождается только из-за перехода**. `Activity` и её `ViewModel` продолжают жить, пока находятся в back stack и процесс жив. Память освобождается, когда `Activity` окончательно завершена или когда система убивает процесс/очищает `Activity` при нехватке ресурсов.

## Answer (EN)

When a new `Activity` is launched, the previous `Activity` does **not** automatically free its memory just because of the transition. It moves through lifecycle callbacks and remains in the back stack. Its memory (the `Activity` instance and its fields) stays allocated as long as:

- the `Activity` is in `STOPPED` state and still referenced (e.g., on the back stack),
- and the app process remains alive.

The system may release this memory later: either when the `Activity` is finished (`finish()` / Back press) or when the process is killed under memory pressure.

### Lifecycle Sequence

When calling `startActivity()` (typical case, `Activity` B fully covers A):

1. **`Activity` A** → `onPause()` (loses focus, may be partially visible)
2. **`Activity` B** → `onCreate()` → `onStart()` → `onResume()` (becomes active)
3. **`Activity` A** → `onStop()` (no longer visible, but stays in back stack)

**Key point**: `Activity` A remains in memory in the `STOPPED` state, including its fields and allocated resources. A `ViewModel`, if used, also remains as long as its owner (`Activity`/`Fragment`) has not been definitively destroyed.

### When Memory IS Freed

#### Explicit Termination

```kotlin
override fun onDestroy() {
    super.onDestroy()

    if (isFinishing) {
        // ✅ User pressed Back or finish() was called
        cleanupResources() // Cleanup since Activity won't return
    } else {
        // ✅ E.g. configuration change / recreation case.
        // The current instance is being destroyed; its resources should be released.
        // IMPORTANT: persist important data earlier (onPause/onStop or
        // onSaveInstanceState); don't rely solely on this branch.
    }
}
```

#### System-Initiated Process Kill

When the system is under memory pressure, it may kill the entire process containing stopped Activities.

Before possible destruction, `onSaveInstanceState()` is typically called (though not strictly guaranteed in all cases):

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Save critical state before potential process death
    outState.putInt("user_score", userScore)
}
```

When the user returns, a **new instance** of the `Activity` is created, and its state is restored via `onCreate(savedInstanceState)`. All previous `Activity` and `ViewModel` instances are gone with the old process.

### Memory Management in onStop()

```kotlin
class MemoryEfficientActivity : AppCompatActivity() {
    private var heavyData: Bitmap? = null

    override fun onStop() {
        super.onStop()
        // ✅ Release heavy references while Activity is not visible
        // to reduce memory footprint and risk of process kill
        heavyData?.recycle() // Often it's enough to drop strong references
        heavyData = null
    }

    override fun onStart() {
        super.onStart()
        // ✅ Recreate when coming back
        if (heavyData == null) {
            heavyData = loadBitmap()
        }
    }
}
```

### `ViewModel` And Lifecycle

```kotlin
class DataViewModel : ViewModel() {
    override fun onCleared() {
        // ✅ Called when the ViewModel's owner (Activity/Fragment)
        // is definitively destroyed and that scope won't be recreated.
        // For example: user navigated back (finish()) or scope changed.
        // ❌ Not called merely on onStop().
    }
}
```

Key points:

- `ViewModel` does NOT survive process death: on process kill, both `Activity` and its `ViewModel` are destroyed; new instances are created after restart.
- Recovery after process death/configuration changes relies on `savedInstanceState`, persistent storage, and/or SavedStateHandle.

### Summary

| Scenario | onDestroy() | Memory (`Activity`/`ViewModel` objects) | Recovery |
|----------|-------------|--------------------------------------|----------|
| `startActivity()` (A → B, A not finished) | For A: ❌ usually not called immediately | A and its `ViewModel` stay in memory (`STOPPED`) while process lives | Not needed |
| Back/`finish()` | ✅ `isFinishing = true` | ✅ Eligible for GC; `Activity` and `ViewModel` go away | Won't be restored |
| Configuration change | ✅ `isFinishing = false` | ✅ Current instances destroyed; new ones created; state restored | Via `savedInstanceState`/SavedStateHandle etc. |
| System kill | (Callbacks not invoked at kill time) | ✅ Entire process memory freed | New process; restore via `savedInstanceState` (if available), persistence |

**Answer**: Starting a new `Activity` does **not** immediately free the previous `Activity`'s memory. The previous `Activity` and its `ViewModel` remain as long as they are on the back stack and the process is alive. Memory is freed when the `Activity` is definitively finished or when the system kills the process/clears Activities under memory pressure.

## Follow-ups

- How does `onSaveInstanceState()` differ from `ViewModel` for state preservation?
- What happens to back stack when `FLAG_ACTIVITY_CLEAR_TOP` is used?
- How does `onTrimMemory()` callback help prevent system kills?
- What's the difference between configuration change and process death?

## References

- [Android `Activity` Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Tasks and Back `Stack`](https://developer.android.com/guide/components/activities/tasks-and-back-stack)

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-lifecycle]]


### Prerequisites

- [[q-android-components-besides-activity--android--easy]] - Basic Android components

### Related

- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle handling
- [[q-how-does-activity-lifecycle-work--android--medium]] - `Activity` lifecycle details
- [[q-activity-navigation-how-it-works--android--medium]] - Navigation mechanics

### Advanced

- [[q-fragments-and-activity-relationship--android--hard]] - `Fragment` lifecycle
- `Activity` memory management and process death handling
