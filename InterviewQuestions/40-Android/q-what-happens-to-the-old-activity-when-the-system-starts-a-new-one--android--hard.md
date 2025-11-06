---
id: android-401
title: Activity Lifecycle on New Activity / Жизненный цикл при запуске новой Activity
aliases:
- Activity Lifecycle on New Activity
- Жизненный цикл при запуске новой Activity
topic: android
subtopics:
- activity
- lifecycle
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/activity
- android/lifecycle
- difficulty/hard
- lifecycle
- memory

---

# Вопрос (RU)
> Жизненный цикл при запуске новой `Activity`

# Question (EN)
> `Activity` `Lifecycle` on New `Activity`

---

## Answer (EN)
When the system starts a new `Activity` in Android, the fate of the old `Activity` depends on multiple factors including `Intent` flags, task configuration, and device memory state.

### Default Behavior (No Special Flags)

When no special flags or configurations are used:

1. **Old `Activity` lifecycle transitions**:
   - `onPause()` is called
   - `onStop()` is called
   - `Activity` remains in the back stack

2. **New `Activity` lifecycle**:
   - `onCreate()` is called
   - `onStart()` is called
   - `onResume()` is called

3. **Back navigation**: User can return to old `Activity` via back button

### FLAG_ACTIVITY_NEW_TASK

When `FLAG_ACTIVITY_NEW_TASK` is set:
- New `Activity` starts in a separate task (if one doesn't exist)
- Old `Activity` remains in its original task
- Both Activities can coexist in different task stacks

**Use case**: Starting `Activity` from non-`Activity` context, creating separate navigation stacks.

### FLAG_ACTIVITY_CLEAR_TOP

When `FLAG_ACTIVITY_CLEAR_TOP` is set:
- If target `Activity` already exists in the stack, all Activities above it are removed
- Target `Activity` receives `onNewIntent()` call (if using `FLAG_ACTIVITY_SINGLE_TOP`)
- Otherwise, target `Activity` is destroyed and recreated

**Use case**: Navigating back to root `Activity`, clearing intermediate screens.

### FLAG_ACTIVITY_SINGLE_TOP

When `FLAG_ACTIVITY_SINGLE_TOP` is set:
- If new `Activity` is already at the top of the stack, it's not recreated
- Instead, `onNewIntent()` is called on the existing instance
- No new `Activity` instance is created

**Use case**: Preventing duplicate instances when `Activity` is already visible.

### Memory Pressure Scenarios

When the system needs memory:
- Activities in `onStop()` state may be destroyed
- Their state is saved via `onSaveInstanceState()`
- When user returns, `Activity` is recreated with `onCreate()` and state is restored
- Only `onPause()` state is guaranteed to remain in memory

### LaunchMode Configurations

The behavior can also be controlled via `android:launchMode` in AndroidManifest.xml:
- `standard`: Default, creates new instance
- `singleTop`: Same as FLAG_ACTIVITY_SINGLE_TOP
- `singleTask`: `Activity` becomes root of new task
- `singleInstance`: `Activity` is only member of its task


# Question (EN)
> `Activity` `Lifecycle` on New `Activity`

---


---


## Answer (EN)
When the system starts a new `Activity` in Android, the fate of the old `Activity` depends on multiple factors including `Intent` flags, task configuration, and device memory state.

### Default Behavior (No Special Flags)

When no special flags or configurations are used:

1. **Old `Activity` lifecycle transitions**:
   - `onPause()` is called
   - `onStop()` is called
   - `Activity` remains in the back stack

2. **New `Activity` lifecycle**:
   - `onCreate()` is called
   - `onStart()` is called
   - `onResume()` is called

3. **Back navigation**: User can return to old `Activity` via back button

### FLAG_ACTIVITY_NEW_TASK

When `FLAG_ACTIVITY_NEW_TASK` is set:
- New `Activity` starts in a separate task (if one doesn't exist)
- Old `Activity` remains in its original task
- Both Activities can coexist in different task stacks

**Use case**: Starting `Activity` from non-`Activity` context, creating separate navigation stacks.

### FLAG_ACTIVITY_CLEAR_TOP

When `FLAG_ACTIVITY_CLEAR_TOP` is set:
- If target `Activity` already exists in the stack, all Activities above it are removed
- Target `Activity` receives `onNewIntent()` call (if using `FLAG_ACTIVITY_SINGLE_TOP`)
- Otherwise, target `Activity` is destroyed and recreated

**Use case**: Navigating back to root `Activity`, clearing intermediate screens.

### FLAG_ACTIVITY_SINGLE_TOP

When `FLAG_ACTIVITY_SINGLE_TOP` is set:
- If new `Activity` is already at the top of the stack, it's not recreated
- Instead, `onNewIntent()` is called on the existing instance
- No new `Activity` instance is created

**Use case**: Preventing duplicate instances when `Activity` is already visible.

### Memory Pressure Scenarios

When the system needs memory:
- Activities in `onStop()` state may be destroyed
- Their state is saved via `onSaveInstanceState()`
- When user returns, `Activity` is recreated with `onCreate()` and state is restored
- Only `onPause()` state is guaranteed to remain in memory

### LaunchMode Configurations

The behavior can also be controlled via `android:launchMode` in AndroidManifest.xml:
- `standard`: Default, creates new instance
- `singleTop`: Same as FLAG_ACTIVITY_SINGLE_TOP
- `singleTask`: `Activity` becomes root of new task
- `singleInstance`: `Activity` is only member of its task

## Ответ (RU)
Когда система запускает новое `Activity` в Android, судьба старого `Activity` зависит от множества факторов, включая флаги намерения intent flags конфигурацию задачи task configuration и состояние памяти устройства. По умолчанию без специальных флагов если не используются специальные флаги или конфигурации то при запуске нового `Activity` старое `Activity` остается в стеке задач back stack. Старое `Activity` переходит в состояние onPause затем onStop. Новое `Activity` создается и проходит состояния onCreate onStart и onResume. Использование флага FLAG_ACTIVITY_NEW_TASK если флаг FLAG_ACTIVITY_NEW_TASK установлен новое `Activity` запускается в новом отдельном стеке задач если такого еще нет. Старое `Activity` остается в своей задаче. Новое `Activity` запускается в новой задаче. Использование флага FLAG_ACTIVITY_CLEAR_TOP если флаг FLAG_ACTIVITY_CLEAR_TOP установлен новое `Activity` будет запускаться а все активности над ним в стеке будут удалены. Если старое `Activity` уже в стеке задач все активности выше него будут удалены. Старое `Activity` будет возвращено в состояние onRestart onStart и onResume. Использование флага FLAG_ACTIVITY_SINGLE_TOP если флаг FLAG_ACTIVITY_SINGLE_TOP установлен и новое `Activity` уже находится на вершине стека оно не будет пересоздано а просто получит вызов onNewIntent. Если новое `Activity` уже на вершине стека его метод onNewIntent будет вызван вместо создания нового экземпляра. Сценарии работы с памятью если система нуждается в памяти она может уничтожить старое `Activity` которое находится в состоянии onStop. Когда пользователь вернется к этому `Activity` оно будет пересоздано и его метод onCreate будет вызван снова

## Related Topics
- `Activity` lifecycle
- `Intent` flags
- Task and back stack
- LaunchMode
- onNewIntent()
- onSaveInstanceState()

---


## Follow-ups

- [[c-activity-lifecycle]]
- 
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]


## References

- [Android Documentation](https://developer.android.com/docs)
- [`Lifecycle`](https://developer.android.com/topic/libraries/architecture/lifecycle)


## Related Questions

### Prerequisites (Easier)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Activity`
- [[q-single-activity-pros-cons--android--medium]] - `Activity`

### Related (Hard)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`
