---\
id: android-401
title: Activity Lifecycle on New Activity / Жизненный цикл при запуске новой Activity
aliases: [Activity Lifecycle on New Activity, Жизненный цикл при запуске новой Activity]
topic: android
subtopics: [activity, lifecycle]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, q-activity-lifecycle-methods--android--medium, q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium, q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium, q-what-is-activity-and-what-is-it-used-for--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/lifecycle, difficulty/hard, lifecycle, memory]

---\
# Вопрос (RU)
> Жизненный цикл при запуске новой `Activity`

# Question (EN)
> `Activity` `Lifecycle` on New `Activity`

---

## Ответ (RU)
Когда система запускает новое `Activity` в Android, поведение предыдущего ("старого") `Activity` зависит от нескольких факторов: стандартных правил жизненного цикла, флагов `Intent`, конфигурации task/affinity и состояния памяти.

### Поведение По Умолчанию (без Специальных флагов)

Предположим, `Activity` A видно на экране и запускает `Activity` B в том же task без специальных флагов.

1. Переходы жизненного цикла, когда B полностью перекрывает A:
   - У A вызывается `onPause()`.
   - Затем у A вызывается `onStop()` (если B полностью скрывает A).
   - A остаётся в back stack (остановлено, но не уничтожено).
   - У B вызываются `onCreate()` → `onStart()` → `onResume()`.

2. Возврат по Back:
   - Когда пользователь нажимает Back из B (и A не было уничтожено):
     - У B вызываются `onPause()` → `onStop()` → `onDestroy()`.
     - У A вызываются `onRestart()` → `onStart()` → `onResume()`.

3. Нюанс частичного перекрытия:
   - Если новое `Activity` не полностью закрывает A (например, прозрачное или диалоговое `Activity`), у A может быть вызван только `onPause()` без `onStop()`, и оно остаётся частично видимым/на заднем плане.

### FLAG_ACTIVITY_NEW_TASK

Когда установлен `FLAG_ACTIVITY_NEW_TASK`:
- Система ищет существующий task с подходящей affinity и поднимает его; если такого нет, создаётся новый task.
- Вызывающее ("старое") `Activity` остаётся в своём task и в своём текущем состоянии жизненного цикла (обычно остановлено, если полностью перекрыто).
- Оба `Activity` могут сосуществовать в разных стэках задач; переключение между ними зависит от действий пользователя и управления задачами.

Сценарии использования: запуск `Activity` из контекста вне `Activity`, намеренное разделение стеков навигации.

### FLAG_ACTIVITY_CLEAR_TOP

Когда установлен `FLAG_ACTIVITY_CLEAR_TOP`, и целевое `Activity` уже существует в back stack того же task:
- Все `Activity`, находящиеся над существующим экземпляром целевого `Activity`, уничтожаются (`onPause()` → `onStop()` → `onDestroy()` по мере применимости).
- Поведение для целевого `Activity` зависит от режима запуска:
  - Если у него `singleTop` (через `launchMode="singleTop"` или в комбинации с `FLAG_ACTIVITY_SINGLE_TOP`) и именно этот экземпляр становится верхним:
    - Новый экземпляр не создаётся; существующий получает `onNewIntent()` (и, при необходимости, проходит `onRestart()`/`onStart()`/`onResume()`, если был остановлен).
  - В противном случае (стандартный режим):
    - Существующий экземпляр уничтожается, и создаётся новый: `onCreate()` → `onStart()` → `onResume()`.

Сценарий использования: вернуться к уже существующему экрану, очистив промежуточные экраны в рамках одного task.

### FLAG_ACTIVITY_SINGLE_TOP

Когда установлен `FLAG_ACTIVITY_SINGLE_TOP`:
- Если `Activity` запускается, и её экземпляр уже находится на вершине back stack:
  - Новый экземпляр не создаётся.
  - Существующий экземпляр получает `onNewIntent()`.
- Если существующий экземпляр не на вершине стека, один `FLAG_ACTIVITY_SINGLE_TOP` не предотвращает создание нового экземпляра.

Сценарии использования: предотвращение дублирования `Activity`, когда оно уже отображается (например, при повторных переходах с уведомлений или deep link на тот же экран).

### Сценарии При Давлении На Память

При дефиците памяти система может завершать процессы и уничтожать `Activity`, находящиеся в фоне (обычно в состоянии `stopped`, иногда даже `paused`). Важно:

- Остановленное `Activity` (например, "старое" после запуска нового) является кандидатом на уничтожение.
- Перед возможным уничтожением может быть вызван `onSaveInstanceState()` для сохранения временного состояния UI.
- Если процесс был убит, когда `Activity` было в фоне, при возвращении пользователя:
  - `Activity` будет пересоздано: `onCreate()` (с переданным `Bundle`, если он был сохранён) → `onStart()` → `onResume()`.
- Ни одно состояние (`paused` или `stopped`) не гарантировано в памяти при давлении на ресурсы; полагаться нужно на корректную обработку колбэков жизненного цикла и восстановление состояния.

### Конфигурации launchMode

Параметр `android:launchMode` в AndroidManifest.xml влияет на то, как экземпляры `Activity` взаимодействуют с task и back stack:

- `standard` (по умолчанию):
  - Каждый запуск создаёт новый экземпляр в текущем task.

- `singleTop`:
  - Если экземпляр уже находится на вершине стека, вместо создания нового вызывается `onNewIntent()`.

- `singleTask`:
  - В системе существует не более одного экземпляра.
  - Он помещается (или переносится) в определённый task; последующие запуски переводят пользователя в этот task.
  - Если экземпляр уже есть, task поднимается на передний план, над ним очищаются `Activity`, и экземпляр может получить `onNewIntent()`.

- `singleInstance` (устаревший/не рекомендован для новых сценариев):
  - `Activity` работает единственным в своём task.
  - Другие `Activity` не могут быть помещены в этот task.

## Related Topics (RU)
- Жизненный цикл `Activity`
- Флаги `Intent`
- Task и back stack
- `launchMode`
- `onNewIntent()`
- `onSaveInstanceState()`

---

## Answer (EN)
When the system starts a new `Activity` in Android, what happens to the previous ("old") `Activity` depends on multiple factors: default lifecycle rules, intent flags, task/affinity configuration, and memory pressure.

### Default Behavior (No Special Flags)

Assume `Activity` A is visible and starts `Activity` B in the same task without special flags.

1. `Lifecycle` transitions when B fully covers A:
   - A: `onPause()` is called.
   - A: `onStop()` is called (if B fully obscures A).
   - A remains in the back stack (stopped, not destroyed).
   - B: `onCreate()` → `onStart()` → `onResume()`.

2. Back navigation:
   - When the user presses Back from B (and A was not destroyed):
     - B: `onPause()` → `onStop()` → `onDestroy()`.
     - A: `onRestart()` → `onStart()` → `onResume()`.

3. Partial occlusion nuance:
   - If the new UI does not fully cover A (e.g., transparent or dialog-like `Activity`), A may get `onPause()` but not `onStop()` and can remain visible behind.

### FLAG_ACTIVITY_NEW_TASK

When `FLAG_ACTIVITY_NEW_TASK` is set:
- The system looks for an existing task with a matching affinity and brings it to foreground; if none exists, it creates a new task.
- The calling ("old") `Activity` remains in its original task and in its current lifecycle state (typically stopped if fully covered).
- Both Activities can coexist in different task stacks; switching between them depends on user navigation and task management.

Use cases: starting an `Activity` from a non-`Activity` context, or intentionally separating navigation stacks.

### FLAG_ACTIVITY_CLEAR_TOP

When `FLAG_ACTIVITY_CLEAR_TOP` is set and an instance of the target `Activity` already exists in the same task's back stack:
- All Activities above that existing instance are destroyed (`onPause()` → `onStop()` → `onDestroy()` as applicable).
- Behavior for the target `Activity` depends on how it is launched:
  - If it is also `singleTop` (via `launchMode="singleTop"` or combined with `FLAG_ACTIVITY_SINGLE_TOP`) and it is the one being revealed:
    - A new instance is NOT created; instead `onNewIntent()` is called on the existing instance (which will go through `onRestart()`/`onStart()`/`onResume()` if it was stopped).
  - Otherwise (standard launch mode):
    - The existing instance is destroyed and a new instance is created with `onCreate()` → `onStart()` → `onResume()`.

Use case: returning to an existing screen while clearing intermediate screens (e.g., "go back to home" within the same task).

### FLAG_ACTIVITY_SINGLE_TOP

When `FLAG_ACTIVITY_SINGLE_TOP` is set:
- If an `Activity` is launched and an instance of that `Activity` is already at the top of the task's back stack:
  - No new instance is created.
  - `onNewIntent()` is delivered to the existing instance.
- If the existing instance is not at the top, `FLAG_ACTIVITY_SINGLE_TOP` alone does not prevent creating a new instance.

Use case: avoiding duplicate instances when relaunching an already visible `Activity` (e.g., from notifications or deep links that may target the current screen).

### Memory Pressure Scenarios

Under memory pressure, the system may reclaim processes and destroy Activities that are in the background (typically stopped, or sometimes even paused). Important points:

- A stopped `Activity` (e.g., the "old" one after starting a new `Activity`) is a candidate for destruction.
- Before potential destruction, `onSaveInstanceState()` may be called to persist transient UI state.
- If the process is killed while the `Activity` is in the background, when the user navigates back:
  - The `Activity` is recreated: `onCreate()` (with the previously saved `Bundle` if available) → `onStart()` → `onResume()`.
- No lifecycle state (paused or stopped) is strictly "guaranteed" to remain in memory under memory pressure; only the documented callbacks and restoration mechanisms should be relied upon.

### LaunchMode Configurations

`android:launchMode` in AndroidManifest.xml influences how new `Activity` instances interact with the task and back stack:

- `standard` (default):
  - Every launch creates a new instance in the current task's back stack.

- `singleTop`:
  - If an instance is already at the top of the stack, it receives `onNewIntent()` instead of creating a new instance.

- `singleTask`:
  - There is at most one instance in the system.
  - It is placed in (or moved to) a task; subsequent launches route to that task.
  - If an instance exists in a task, that task is brought to the foreground and the existing instance may receive `onNewIntent()`; Activities above it are cleared.

- `singleInstance` (legacy / discouraged for new designs):
  - `Activity` runs as the only `Activity` in its task.
  - No other Activities share that task.

## Related Topics (EN)
- `Activity` lifecycle
- `Intent` flags
- Task and back stack
- `launchMode`
- `onNewIntent()`
- `onSaveInstanceState()`

---

## Follow-ups (RU)

- [[c-activity-lifecycle]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]

## Follow-ups (EN)

- [[c-activity-lifecycle]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]

## References

- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Activity`
- [[q-single-activity-pros-cons--android--medium]] - `Activity`

### Related (Hard)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`
