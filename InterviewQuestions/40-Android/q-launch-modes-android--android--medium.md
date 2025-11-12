---
id: android-010
title: Android Activity Launch Modes / Режимы запуска Activity в Android
aliases:
- Android Activity Launch Modes
- Режимы запуска Activity в Android
topic: android
subtopics:
- activity
- ui-navigation
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-compose-navigation
- c-activity
- q-kapt-vs-ksp--android--medium
- q-viewmodel-vs-onsavedinstancestate--android--medium
- q-which-event-is-triggered-when-user-presses-screen--android--medium
created: 2025-10-05
updated: 2025-11-11
tags:
- android/activity
- android/ui-navigation
- difficulty/medium
- en
- ru


---

# Вопрос (RU)
> Какие режимы запуска (launch modes) вы знаете?

# Question (EN)
> What launch modes do you know?

---

## Ответ (RU)

При объявлении `Activity` в файле манифеста вы можете указать, как `Activity` должна ассоциироваться с задачей (task). Есть два основных способа влиять на поведение запуска:
- через атрибут `android:launchMode` в AndroidManifest
- через флаги `Intent`

Существует четыре стандартных режима запуска, которые можно явно указать в атрибуте `launchMode`:

- `standard`
- `singleTop`
- `singleTask`
- `singleInstance`

Начиная с Android 5.0, документ-ориентированный режим (`FLAG_ACTIVITY_NEW_DOCUMENT` и `FLAG_ACTIVITY_MULTIPLE_TASK`) вводит поведение, аналогичное `singleInstancePerTask`, для отдельных `Activity`, но это не отдельное значение атрибута `android:launchMode` и не отдельный «режим запуска» в манифесте.

### standard (режим по умолчанию)

Режим по умолчанию. Система создает новый экземпляр `Activity` в задаче, из которой она была запущена, и направляет в него `Intent`. `Activity` может быть создана несколько раз; каждый экземпляр может принадлежать разным задачам, и одна задача может содержать несколько экземпляров.

Пример:
- Активити: A, B, C, D
- B объявлена как `<activity android:launchMode="standard" />`

Состояние стека до повторного запуска B:
A -> B -> C -> D

Состояние стека после повторного запуска B:
A -> B -> C -> D -> B

### singleTop

Если экземпляр `Activity` уже существует в верхней части стека текущей задачи, система направляет `Intent` в этот экземпляр через вызов `onNewIntent()`, вместо создания нового экземпляра. В целом может существовать несколько экземпляров такой `Activity`: в разных задачах или в одной задаче (если при запуске ни один существующий экземпляр не находится на вершине стека).

Сценарий 1:
- `Activity` C находится на вершине стека.
- Вы снова запускаете C.
- Новый экземпляр не создается; существующая C получает `onNewIntent()`.
- Стек остается без изменений.

Сценарий 2:
- Стек: A -> C -> B (B сверху).
- Из B запускаем C.
- Так как C не на вершине, создается новый экземпляр C.
- Новый стек: A -> C -> B -> C.

Примечание: Если создается новый экземпляр `Activity`, пользователь может с помощью "Назад" вернуться к предыдущей `Activity`. Если же существующий экземпляр обрабатывает новый `Intent` через `onNewIntent()`, поведение при возврате по "Назад" зависит от того, как вы обновляете состояние в `onNewIntent()` (по умолчанию стек задач не дополняется новой записью, и отдельного «предыдущего состояния» этой же `Activity` в стеке не появляется).

### singleTask

Система создает `Activity` в корне новой задачи или переиспользует существующую задачу, корневой `Activity` которой является экземпляр этой `Activity` (с совпадающим affinity). Если такой экземпляр уже существует в корне своей задачи, система направляет `Intent` в него через `onNewIntent()` вместо создания нового, а все `Activity` над ним в этой задаче уничтожаются.

Сценарий 1 (экземпляра еще нет):
- Из B запускаем C (singleTask).
- Экземпляра C еще нет.
- Создается новая задача, C становится корневой `Activity`.
- Из C можно запускать другие `Activity` (например, D с режимом по умолчанию), которые будут добавляться поверх C в этой задаче.
- В пределах этой задачи "Назад" удаляет D и возвращает к C; выход из задачи вернет пользователя к предыдущей задаче (в соответствии с поведением лаунчера/списка недавних).

Сценарий 2 (экземпляр существует в своей задаче):
- C (singleTask) уже существует как корень собственной задачи, над ним есть другие `Activity`.
- Из A запускаем C.
- Система переиспользует существующую задачу: все `Activity` над C завершаются; C получает `onNewIntent()` и выводится на передний план.

Сценарий 3 (экземпляр существует в текущей задаче как корень):
- Стек: A (singleTask) -> B -> C -> D.
- Из D запускаем A.
- Поскольку A имеет режим `singleTask` и уже находится в корне этой задачи, все `Activity` над A (B, C, D) будут уничтожены; A получит `onNewIntent()` и станет верхней.

Примечание: Кнопка/жест "Назад" работает внутри стека текущей задачи. Когда `singleTask`-`Activity` переиспользуется и очищает стек над собой, "Назад" перемещает пользователя по оставшимся `Activity` этой задачи или выводит из задачи.

### singleInstance

Похожа на `singleTask`, но `Activity` всегда является единственным элементом своей задачи. Система не добавляет другие `Activity` в задачу, содержащую `singleInstance`.

- Существует только один экземпляр такой `Activity` на устройстве.
- Этот экземпляр всегда единственный в своем task.
- Любые `Activity`, запускаемые из нее, открываются в других задачах.

Пример:
- B запускает C (singleInstance).
- Создается новая задача только с C.
- Если C запускает D (режим по умолчанию), D будет помещена в другую подходящую задачу, а не в задачу C.

### singleInstancePerTask

`singleInstancePerTask` не является допустимым значением `android:launchMode` в манифесте. Это термин для описания поведения документ-ориентированных `Activity` (например, с флагами `FLAG_ACTIVITY_NEW_DOCUMENT` и `FLAG_ACTIVITY_MULTIPLE_TASK`). В этом подходе:

- Экземпляр `Activity` может быть только корневой `Activity` своей задачи.
- Может существовать несколько таких задач (каждая со своим корневым экземпляром этой `Activity`), но в каждой задаче не более одного экземпляра этой `Activity`.
- При повторном использовании существующего экземпляра (по аналогии с `singleTask` для этой задачи) `Activity`, расположенные выше него в стеке, удаляются.

Примечание: Для поведения `singleTask` и `singleInstancePerTask` (в контексте document mode), при переиспользовании существующего экземпляра все `Activity`, находящиеся над ним в задаче, уничтожаются. Например:
- Задача: A (root) -> B -> C (top)
- Приходит `Intent` для A (с `singleTask`-подобным поведением).
- Существующий A получает `onNewIntent()`, B и C завершаются, задача становится A.

---

## Answer (EN)

When declaring an activity in your manifest file, you can specify how the activity should associate with a task. There are two main ways to influence launch behavior:
- via the `android:launchMode` attribute in the Android Manifest
- via `Intent` flags

There are four standard launch modes you can assign directly to the `launchMode` attribute:

- `standard`
- `singleTop`
- `singleTask`
- `singleInstance`

Starting with Android 5.0, document-mode flags (such as `FLAG_ACTIVITY_NEW_DOCUMENT` and `FLAG_ACTIVITY_MULTIPLE_TASK`) can be used to achieve behavior similar to `singleInstancePerTask` for specific activities, but this is not a distinct `android:launchMode` value and not an official manifest launch mode.

### standard (the default mode)

Default. The system creates a new instance of the activity in the task from which it was started and routes the intent to it. The activity can be instantiated multiple times; each instance can belong to different tasks, and one task can contain multiple instances.

Example:
- Activities: A, B, C, D
- B declared as `<activity android:launchMode="standard" />`

State of activity stack before launching B again:
A -> B -> C -> D

State of activity stack after launching B again:
A -> B -> C -> D -> B

### singleTop

If an instance of the activity already exists at the top of the current task's back stack, the system routes the intent to that instance through a call to its `onNewIntent()` method, rather than creating a new instance. Multiple instances of such an activity may still exist overall: across different tasks, or within one task if none of the existing instances (except possibly the top one) is at the top at launch time.

Scenario 1:
- `Activity` C is at the top of the back stack.
- You navigate to C again with an intent targeting C.
- No new instance is created; existing C receives `onNewIntent()`.
- Back stack remains unchanged.

Scenario 2:
- Back stack contains A -> C -> B (B is on top).
- You start C from B.
- Because C is not at the top, a new instance of C is created.
- New back stack: A -> C -> B -> C.

Note: When a new instance of an activity is created, the user can press or gesture Back to return to the previous activity. When an existing instance handles a new intent via `onNewIntent()`, the task's back stack is not extended with an additional entry for that same activity; the actual Back behavior then depends on how you update the activity's state in `onNewIntent()`.

### singleTask

The system creates the activity as the root of a new task or reuses an existing task whose root activity is an instance of that activity (matching task affinity). If such an instance already exists at the root of its task, the system routes the intent to that existing instance via `onNewIntent()` instead of creating a new one, and all activities above it in that task are destroyed.

Scenario 1 (no existing instance):
- You start `Activity` C (singleTask) from B.
- No C exists yet.
- A new task is created; C becomes the root of this new task.
- From C you can start other activities (e.g., D with default mode), which will be placed on top of C in that task.
- Within that task, Back pops D and returns to C; leaving the task then returns to the previous task (if any), according to launcher/recents behavior.

Scenario 2 (existing instance in its own task):
- C (singleTask) already exists as root of its own task with some activities above it.
- You start C from A.
- Android reuses the existing task: all activities above C in that task are finished; C receives `onNewIntent()` and comes to foreground.

Scenario 3 (existing instance in current task as root):
- Back stack: A (singleTask) -> B -> C -> D.
- From D you start A.
- Because A is singleTask and already at the root of this task, all activities above A (B, C, D) are finished; A receives `onNewIntent()` and becomes top.

Note: The Back button/gesture operates within the current task's back stack. When a singleTask activity reuses its existing task and clears activities above it, Back navigates among the remaining activities in that task or eventually leaves the task.

### singleInstance

Similar to `singleTask`, except that the activity is the only activity in its task. The system does not launch any other activities into the task holding this instance. Any activities started by a `singleInstance` activity always open in other tasks.

- Only one instance of this activity exists on the device.
- That instance is always the sole member of its task.

Example:
- B starts C (singleInstance).
- System creates a new task with only C.
- If C starts D (default mode), D is launched into another appropriate task, not into C's task.

### singleInstancePerTask

`singleInstancePerTask` is not a value of `android:launchMode` in the manifest. It is a term used to describe behavior achieved with document-mode activities (e.g., using `FLAG_ACTIVITY_NEW_DOCUMENT` and `FLAG_ACTIVITY_MULTIPLE_TASK`). In this approach:

- An activity instance can only be the root of its task.
- There can be multiple such tasks (each with its own root instance of that activity), but each task has at most one instance of that activity.
- When reusing an existing instance (similar to singleTask semantics for that task), activities above it in that task are removed.

Note: For both singleTask-like behavior and `singleInstancePerTask` in document mode, when an existing instance is reused, all activities that are above that instance in its task are finished. For example:
- Task: A (root) -> B -> C (top)
- An intent arrives for A (singleTask-like behavior).
- Existing A receives `onNewIntent()`, B and C are finished, and the task becomes A.

---

## Follow-ups

- [[q-kapt-vs-ksp--android--medium]]
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- [[q-which-event-is-triggered-when-user-presses-screen--android--medium]]


## References
- [Tasks and the back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack)
- [Understand the types of Launch Modes in an Android `Activity`](https://mohamedyousufmo.medium.com/understand-android-activity-launch-mode-c21fcecf04b8)
- [Android `Activity` Launch Mode](https://medium.com/android-news/android-activity-launch-mode-e0df1aa72242)
- [Understand Android `Activity`'s launchMode: standard, singleTop, singleTask and singleInstance](https://inthecheesefactory.com/blog/understand-android-activity-launchmode/en)


## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-activity]]


### Related (Medium)
- [[q-compose-navigation-advanced--android--medium]] - Jetpack Compose