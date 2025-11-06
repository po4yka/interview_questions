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
- android/activity
- android/navigation
- android/task-management
- difficulty/medium
- en
- ru
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-compose-navigation
- c-activity
- c-fragments
- q-kapt-vs-ksp--android--medium
- q-viewmodel-vs-onsavedinstancestate--android--medium
- q-which-event-is-triggered-when-user-presses-screen--android--medium
created: 2025-10-05
updated: 2025-10-05
tags:
- android/activity
- android/ui-navigation
- difficulty/medium
- en
- ru
date created: Sunday, October 12th 2025, 12:27:51 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Question (EN)
> What launch modes do you know?
# Вопрос (RU)
> Какие режимы запуска (launch modes) вы знаете?

---

## Answer (EN)

When declaring an activity in your manifest file, you can specify how the activity should associate with a task. There are two ways to define the launch modes. First way is using **Android Manifest file**, and second way is using **Intent Flags**.

There are five different launch modes you can assign to the `launchMode` attribute:

- `standard`
- `singleTop`
- `singleTask`
- `singleInstance`
- `singleInstancePerTask`

### Standard (the Default mode)

Default. The system creates a new instance of the activity in the task from which it was started and routes the intent to it. The activity can be instantiated multiple times, each instance can belong to different tasks, and one task can have multiple instances.

**Example:**
Suppose you have *A*, *B*, *C* and *D* activities and your activity *B* has `<activity android:launchMode="standard" />`. Now you again launching activity *B*:

State of Activity Stack before launch *B*:
*A* -> *B* -> *C* -> *D*

State of Activity Stack after launch *B*:
*A* -> *B* -> *C* -> *D* -> *B*

### singleTop

If an instance of the activity already exists at the top of the current task, the system routes the intent to that instance through a call to its `onNewIntent()` method, rather than creating a new instance of the activity. The activity can be instantiated multiple times, each instance can belong to different tasks, and one task can have multiple instances (but only if the activity at the top of the back stack is not an existing instance of the activity).

**Scenario 1:** The `Activity` exists and it's sitting on the top of the back stack (Assume that's current activity as well). For example, the **Activity C** exists, and it's on the top of the back stack. The user wants to go to the same activity again. The Android system will not create new instance of the **Activity C**, instead it will use the existing **Activity C** that's sitting on the top of the **back stack**. Hence, the **back stack** remains intact.

**Scenario 2:** The `Activity` exists, and but it's not on the top of the **back stack**. For example, **Activity C** exists, and it's not on the top of the stack. The user wants to go to the **Activity C** from **Activity B**. Android system will create a new instance of the **Activity C**, even though **Activity C** already exists in the back stack, but it's not on the top of the back stack. Hence, the back stack is modified by adding new instance of the **Activity C**.

**Note:** When a new instance of an activity is created, the user can press or gesture Back to return to the previous activity. But when an existing instance of an activity handles a new intent, the user cannot press or gesture Back to return to the state of the activity before the new intent arrived in `onNewIntent()`.

### singleTask

The system creates the activity at the root of a new task or locates the activity on an existing task with the same affinity. If an instance of the activity already exists and is at the root of the task, the system routes the intent to existing instance through a call to its `onNewIntent()` method, rather than creating a new instance. Meanwhile all of the other activities on top of it are destroyed.

**Scenario 1:** The activity does not exist, and hence the new activity with its own **task** and **back stack** will be initiated. The Activity will be the root of the **new task**. For example, we want to open **Activity C** from **Activity B**, but it does not exist in the **back stack** or separate **task**. So **new task/back stack** will be created with root activity as **Activity C**.

From this new **back stack** the **Activity C** can launch other activities. For example, from **Activity C** if the user wants to see **Activity D** which has a default launch mode, it can launch itself.

If the user presses the back button, **Activity D** will be popped off from the **back stack** of **new task**, hence **Activity C** will be visible. So regardless of task, back button will always take the user to previous activity.

**Scenario 2:** The user wants to launch an activity which has a `singleTask` mode, and already exists with its **task** and **back stack**. For example, referring to the previous scenario where the **Activity C** exists with newly created **task** and **back stack**. Let's say the user wants to go to the **Activity C** from **Activity A**, the android system will not create a new instance of the **Activity C** along with the **task/back stack**. Instead, it just routes it to the **Activity C**, and what ever activities that was sitting on the top of the root activity will be popped off.

**Scenario 3:** The `Activity` exists, and it's not on a separate **task/back stack**, but its on the current **back stack**. Let's say we have 4 Activities in our stack respectively **Activity A**, **Activity B**, **Activity C**, and **Activity D**. Let's say that the user wants to go to **Activity A** from **Activity D**, since the **Activity A** has mode of `singleTask`, and it is exists in the root of the **back stack**. So no need to create new **task/back stack**, what would happen in this case is that the system will pop off every activity that's sitting top of **Activity A** until it becomes top of the **back stack**. Hence, the **Activity A** is being reused instead of creating new one.

**Note:** Although the activity starts in a new task, the Back button and gesture still return the user to the previous activity.

### singleInstance

Same as `singleTask`, except that the system doesn't launch any other activities into the task holding the instance. The activity is always the single and only member of its task; any activities started by this one open in a separate task. So only that instance of the activity exists in the **task/back stack**.

For example, like the previous example we have launched the **Activity C** from the **Activity B** but in this case the **Activity C** has a mode of `singleInstance`. After creating new a **task** and **back stack** which has **Activity C**, lets say we want to launch the **Activity D** which has a default mode, the **Activity D** will be launched pushed into the old task or separate task not the newly created task by the **Activity C**.

### singleInstancePerTask

The activity can only be running as the root activity of the task, the first activity that created the task, and therefore there will only be one instance of this activity in a task. In contrast to the `singleTask` launch mode, this activity can be started in multiple instances in different tasks if the `FLAG_ACTIVITY_MULTIPLE_TASK` or `FLAG_ACTIVITY_NEW_DOCUMENT` flag is set.

**Note:** `singleTask` and `singleInstancePerTask` will remove all activities which are above the starting activity from the **task**. For example, suppose a task consists of root activity *A* with activities *B*, *C* (the task is *A* -> *B* -> *C*; *C* is on top). An intent arrives for an activity of type *A*. If A's launch mode is `singleTask` or `singleInstancePerTask`, the existing instance of *A* receives the intent through `onNewIntent()`. *B* and *C* are finished, and the task is now *A*.


# Question (EN)
> What launch modes do you know?
# Вопрос (RU)
> Какие режимы запуска (launch modes) вы знаете?

---


---


## Answer (EN)

When declaring an activity in your manifest file, you can specify how the activity should associate with a task. There are two ways to define the launch modes. First way is using **Android Manifest file**, and second way is using **Intent Flags**.

There are five different launch modes you can assign to the `launchMode` attribute:

- `standard`
- `singleTop`
- `singleTask`
- `singleInstance`
- `singleInstancePerTask`

### Standard (the Default mode)

Default. The system creates a new instance of the activity in the task from which it was started and routes the intent to it. The activity can be instantiated multiple times, each instance can belong to different tasks, and one task can have multiple instances.

**Example:**
Suppose you have *A*, *B*, *C* and *D* activities and your activity *B* has `<activity android:launchMode="standard" />`. Now you again launching activity *B*:

State of Activity Stack before launch *B*:
*A* -> *B* -> *C* -> *D*

State of Activity Stack after launch *B*:
*A* -> *B* -> *C* -> *D* -> *B*

### singleTop

If an instance of the activity already exists at the top of the current task, the system routes the intent to that instance through a call to its `onNewIntent()` method, rather than creating a new instance of the activity. The activity can be instantiated multiple times, each instance can belong to different tasks, and one task can have multiple instances (but only if the activity at the top of the back stack is not an existing instance of the activity).

**Scenario 1:** The `Activity` exists and it's sitting on the top of the back stack (Assume that's current activity as well). For example, the **Activity C** exists, and it's on the top of the back stack. The user wants to go to the same activity again. The Android system will not create new instance of the **Activity C**, instead it will use the existing **Activity C** that's sitting on the top of the **back stack**. Hence, the **back stack** remains intact.

**Scenario 2:** The `Activity` exists, and but it's not on the top of the **back stack**. For example, **Activity C** exists, and it's not on the top of the stack. The user wants to go to the **Activity C** from **Activity B**. Android system will create a new instance of the **Activity C**, even though **Activity C** already exists in the back stack, but it's not on the top of the back stack. Hence, the back stack is modified by adding new instance of the **Activity C**.

**Note:** When a new instance of an activity is created, the user can press or gesture Back to return to the previous activity. But when an existing instance of an activity handles a new intent, the user cannot press or gesture Back to return to the state of the activity before the new intent arrived in `onNewIntent()`.

### singleTask

The system creates the activity at the root of a new task or locates the activity on an existing task with the same affinity. If an instance of the activity already exists and is at the root of the task, the system routes the intent to existing instance through a call to its `onNewIntent()` method, rather than creating a new instance. Meanwhile all of the other activities on top of it are destroyed.

**Scenario 1:** The activity does not exist, and hence the new activity with its own **task** and **back stack** will be initiated. The Activity will be the root of the **new task**. For example, we want to open **Activity C** from **Activity B**, but it does not exist in the **back stack** or separate **task**. So **new task/back stack** will be created with root activity as **Activity C**.

From this new **back stack** the **Activity C** can launch other activities. For example, from **Activity C** if the user wants to see **Activity D** which has a default launch mode, it can launch itself.

If the user presses the back button, **Activity D** will be popped off from the **back stack** of **new task**, hence **Activity C** will be visible. So regardless of task, back button will always take the user to previous activity.

**Scenario 2:** The user wants to launch an activity which has a `singleTask` mode, and already exists with its **task** and **back stack**. For example, referring to the previous scenario where the **Activity C** exists with newly created **task** and **back stack**. Let's say the user wants to go to the **Activity C** from **Activity A**, the android system will not create a new instance of the **Activity C** along with the **task/back stack**. Instead, it just routes it to the **Activity C**, and what ever activities that was sitting on the top of the root activity will be popped off.

**Scenario 3:** The `Activity` exists, and it's not on a separate **task/back stack**, but its on the current **back stack**. Let's say we have 4 Activities in our stack respectively **Activity A**, **Activity B**, **Activity C**, and **Activity D**. Let's say that the user wants to go to **Activity A** from **Activity D**, since the **Activity A** has mode of `singleTask`, and it is exists in the root of the **back stack**. So no need to create new **task/back stack**, what would happen in this case is that the system will pop off every activity that's sitting top of **Activity A** until it becomes top of the **back stack**. Hence, the **Activity A** is being reused instead of creating new one.

**Note:** Although the activity starts in a new task, the Back button and gesture still return the user to the previous activity.

### singleInstance

Same as `singleTask`, except that the system doesn't launch any other activities into the task holding the instance. The activity is always the single and only member of its task; any activities started by this one open in a separate task. So only that instance of the activity exists in the **task/back stack**.

For example, like the previous example we have launched the **Activity C** from the **Activity B** but in this case the **Activity C** has a mode of `singleInstance`. After creating new a **task** and **back stack** which has **Activity C**, lets say we want to launch the **Activity D** which has a default mode, the **Activity D** will be launched pushed into the old task or separate task not the newly created task by the **Activity C**.

### singleInstancePerTask

The activity can only be running as the root activity of the task, the first activity that created the task, and therefore there will only be one instance of this activity in a task. In contrast to the `singleTask` launch mode, this activity can be started in multiple instances in different tasks if the `FLAG_ACTIVITY_MULTIPLE_TASK` or `FLAG_ACTIVITY_NEW_DOCUMENT` flag is set.

**Note:** `singleTask` and `singleInstancePerTask` will remove all activities which are above the starting activity from the **task**. For example, suppose a task consists of root activity *A* with activities *B*, *C* (the task is *A* -> *B* -> *C*; *C* is on top). An intent arrives for an activity of type *A*. If A's launch mode is `singleTask` or `singleInstancePerTask`, the existing instance of *A* receives the intent through `onNewIntent()`. *B* and *C* are finished, and the task is now *A*.

## Ответ (RU)

При объявлении активити в файле манифеста вы можете указать, как активити должна ассоциироваться с задачей (task). Существует два способа определения режимов запуска. Первый способ - использование **файла Android Manifest**, второй способ - использование **флагов Intent**.

Существует пять различных режимов запуска, которые вы можете назначить атрибуту `launchMode`:

- `standard`
- `singleTop`
- `singleTask`
- `singleInstance`
- `singleInstancePerTask`

### Standard (режим По умолчанию)

Режим по умолчанию. Система создает новый экземпляр активити в задаче, из которой она была запущена, и направляет туда интент. Активити может быть создана несколько раз, каждый экземпляр может принадлежать разным задачам, и одна задача может иметь несколько экземпляров.

**Пример:**
Предположим, у вас есть активити *A*, *B*, *C* и *D*, и ваша активити *B* имеет `<activity android:launchMode="standard" />`. Теперь вы снова запускаете активити *B*:

Состояние стека активити до запуска *B*:
*A* -> *B* -> *C* -> *D*

Состояние стека активити после запуска *B*:
*A* -> *B* -> *C* -> *D* -> *B*

### singleTop

Если экземпляр активити уже существует в верхней части текущей задачи, система направляет интент в этот экземпляр через вызов метода `onNewIntent()`, вместо создания нового экземпляра активити. Активити может быть создана несколько раз, каждый экземпляр может принадлежать разным задачам, и одна задача может иметь несколько экземпляров (но только если активити в верхней части стека возврата не является существующим экземпляром активити).

**Сценарий 1:** `Activity` существует и находится в верхней части стека возврата (предположим, что это также текущая активити). Например, **Activity C** существует и находится в верхней части стека возврата. Пользователь хочет снова перейти к той же активити. Система Android не создаст новый экземпляр **Activity C**, вместо этого она будет использовать существующую **Activity C**, которая находится в верхней части **стека возврата**. Таким образом, **стек возврата** остается неизменным.

**Сценарий 2:** `Activity` существует, но не находится в верхней части **стека возврата**. Например, **Activity C** существует и не находится в верхней части стека. Пользователь хочет перейти к **Activity C** из **Activity B**. Система Android создаст новый экземпляр **Activity C**, даже если **Activity C** уже существует в стеке возврата, но не находится в его верхней части. Таким образом, стек возврата изменяется путем добавления нового экземпляра **Activity C**.

**Примечание:** Когда создается новый экземпляр активити, пользователь может нажать кнопку "Назад" или использовать жест для возврата к предыдущей активити. Но когда существующий экземпляр активити обрабатывает новый интент, пользователь не может нажать кнопку "Назад" или использовать жест для возврата к состоянию активити до прибытия нового интента в `onNewIntent()`.

### singleTask

Система создает активити в корне новой задачи или находит активити в существующей задаче с тем же сродством (affinity). Если экземпляр активити уже существует и находится в корне задачи, система направляет интент в существующий экземпляр через вызов метода `onNewIntent()`, вместо создания нового экземпляра. При этом все другие активити над ним уничтожаются.

**Сценарий 1:** Активити не существует, и поэтому будет инициирована новая активити со своей собственной **задачей** и **стеком возврата**. Активити будет корнем **новой задачи**. Например, мы хотим открыть **Activity C** из **Activity B**, но она не существует в **стеке возврата** или отдельной **задаче**. Таким образом, будет создана **новая задача/стек возврата** с корневой активити **Activity C**.

Из этого нового **стека возврата** **Activity C** может запускать другие активити. Например, из **Activity C**, если пользователь хочет увидеть **Activity D**, которая имеет режим запуска по умолчанию, она может запустить себя.

Если пользователь нажмет кнопку "Назад", **Activity D** будет извлечена из **стека возврата** **новой задачи**, и **Activity C** станет видимой. Таким образом, независимо от задачи, кнопка "Назад" всегда будет возвращать пользователя к предыдущей активити.

**Сценарий 2:** Пользователь хочет запустить активити, которая имеет режим `singleTask` и уже существует со своей **задачей** и **стеком возврата**. Например, ссылаясь на предыдущий сценарий, где **Activity C** существует с вновь созданной **задачей** и **стеком возврата**. Допустим, пользователь хочет перейти к **Activity C** из **Activity A**, система Android не создаст новый экземпляр **Activity C** вместе с **задачей/стеком возврата**. Вместо этого она просто направит его к **Activity C**, и все активити, которые находились над корневой активити, будут удалены.

**Сценарий 3:** `Activity` существует и находится не в отдельной **задаче/стеке возврата**, а в текущем **стеке возврата**. Допустим, у нас есть 4 активити в нашем стеке соответственно **Activity A**, **Activity B**, **Activity C** и **Activity D**. Допустим, что пользователь хочет перейти к **Activity A** из **Activity D**, поскольку **Activity A** имеет режим `singleTask` и существует в корне **стека возврата**. Нет необходимости создавать новую **задачу/стек возврата**, что произойдет в этом случае - система удалит все активити, находящиеся над **Activity A**, пока она не станет верхней в **стеке возврата**. Таким образом, **Activity A** переиспользуется вместо создания новой.

**Примечание:** Хотя активити запускается в новой задаче, кнопка "Назад" и жест по-прежнему возвращают пользователя к предыдущей активити.

### singleInstance

Аналогично `singleTask`, за исключением того, что система не запускает никакие другие активити в задачу, содержащую экземпляр. Активити всегда является единственным членом своей задачи; любые активити, запущенные ею, открываются в отдельной задаче. Таким образом, только этот экземпляр активити существует в **задаче/стеке возврата**.

Например, как в предыдущем примере, мы запустили **Activity C** из **Activity B**, но в этом случае **Activity C** имеет режим `singleInstance`. После создания новой **задачи** и **стека возврата**, которые содержат **Activity C**, допустим, мы хотим запустить **Activity D**, которая имеет режим по умолчанию, **Activity D** будет запущена и добавлена в старую задачу или отдельную задачу, а не во вновь созданную задачу **Activity C**.

### singleInstancePerTask

Активити может работать только как корневая активити задачи, первая активити, создавшая задачу, и поэтому в задаче будет только один экземпляр этой активити. В отличие от режима запуска `singleTask`, эта активити может быть запущена в нескольких экземплярах в разных задачах, если установлен флаг `FLAG_ACTIVITY_MULTIPLE_TASK` или `FLAG_ACTIVITY_NEW_DOCUMENT`.

**Примечание:** `singleTask` и `singleInstancePerTask` удалят все активити, которые находятся над запускаемой активити из **задачи**. Например, предположим, что задача состоит из корневой активити *A* с активити *B*, *C* (задача: *A* -> *B* -> *C*; *C* находится сверху). Приходит интент для активити типа *A*. Если режим запуска A - `singleTask` или `singleInstancePerTask`, существующий экземпляр *A* получает интент через `onNewIntent()`. *B* и *C* завершаются, и задача теперь представляет собой *A*.

---

## References
- [Tasks and the back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack)
- [Understand the types of Launch Modes in an Android Activity](https://mohamedyousufmo.medium.com/understand-android-activity-launch-mode-c21fcecf04b8)
- [Android Activity Launch Mode](https://medium.com/android-news/android-activity-launch-mode-e0df1aa72242)
- [Understand Android Activity's launchMode: standard, singleTop, singleTask and singleInstance](https://inthecheesefactory.com/blog/understand-android-activity-launchmode/en)


## Follow-ups

- [[q-kapt-vs-ksp--android--medium]]
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]]
- [[q-which-event-is-triggered-when-user-presses-screen--android--medium]]


## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-activity]]
- [[c-fragments]]


### Related (Medium)
- [[q-compose-navigation-advanced--android--medium]] - Jetpack Compose
