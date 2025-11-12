---
id: android-227
title: Tasks and Back Stack / Задачи и стек возврата
aliases:
- Tasks and Back Stack
- Задачи и стек возврата
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
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- android/ui-navigation
- back-stack
- difficulty/medium
- launch-mode
- tasks


---

# Вопрос (RU)
> Что вы знаете о задачах и стеке возврата?

# Question (EN)
> What do you know about tasks and the back stack?

---

## Ответ (RU)
**Задача (task)** — это коллекция `Activity`, с которыми взаимодействует пользователь при выполнении некоторого сценария в вашем приложении. Эти `Activity` организованы в стек, называемый **стеком возврата (back stack)**, в том порядке, в котором каждая `Activity` была открыта.

Например, почтовое приложение может иметь одну `Activity` для отображения списка новых сообщений. Когда пользователь выбирает сообщение, открывается новая `Activity` для просмотра этого сообщения. Эта новая `Activity` добавляется в стек возврата. Когда пользователь нажимает кнопку или использует жест "Назад", новая `Activity` завершается и удаляется из стека.

### Жизненный цикл задачи и ее back stack

Домашний экран устройства является отправной точкой для большинства задач. Когда пользователь нажимает на значок приложения или ярлык в лаунчере или на домашнем экране, задача этого приложения выводится на передний план. Если задачи для приложения еще не существует, создается новая задача, и главная `Activity` приложения открывается как корневая (root) `Activity` в стеке.

Когда текущая `Activity` запускает другую, новая `Activity` помещается в верхнюю часть стека и получает фокус. Предыдущая `Activity` остается в стеке, но переходит в состояние `stopped`. Когда `Activity` остановлена, система сохраняет текущее состояние ее пользовательского интерфейса. Когда пользователь выполняет действие "Назад", текущая `Activity` извлекается (pop) с вершины стека и уничтожается, предыдущая `Activity` возобновляется (resume), и ее состояние интерфейса восстанавливается.

В стандартной задаче `Activity` в стеке не переупорядочиваются произвольно: они в основном добавляются (push) и удаляются (pop) при запуске новых `Activity` и завершении текущих через кнопку/жест "Назад" или явный вызов `finish()`. Таким образом, стек возврата ведет себя как структура **LIFO (последним пришёл — первым вышел)**. Отдельные флаги `Intent` и режимы запуска (`singleTask`, `singleInstance`, `FLAG_ACTIVITY_CLEAR_TOP`, `FLAG_ACTIVITY_REORDER_TO_FRONT` и др.) могут модифицировать это поведение для конкретных `Activity` и должны рассматриваться отдельно.

По мере того как пользователь продолжает нажимать или использовать жест "Назад", каждая `Activity` по очереди извлекается из стека, чтобы показать предыдущую, пока пользователь не вернется на домашний экран или к той `Activity`, которая выполнялась, когда началась задача. Когда все `Activity` удалены из стека, задача перестает существовать.

### Задачи в фоне и на переднем плане

Задача — это связная единица, которая может быть отправлена в **фон** (background), когда пользователь начинает новую задачу или переходит на домашний экран. Находясь в фоне, все `Activity` задачи находятся в остановленном состоянии, но стек возврата этой задачи остается логически целостным — задача теряет фокус, пока другая задача находится на переднем плане.

Задача может быть возвращена на **передний план** (foreground), чтобы пользователь мог продолжить с того места, где остановился.

Примечания:
- Несколько задач могут одновременно находиться в фоне.
- Если системе нужно освободить память, она может уничтожать процессы и их фоновые `Activity`. В этом случае точное состояние UI не гарантируется: система может пересоздать `Activity`, используя сохраненное состояние (`savedInstanceState`) и постоянные данные, но только при условии, что приложение корректно реализует сохранение состояния.

### Поведение кнопки/жеста "Назад" для корневых launcher-`Activity`

Корневые launcher-`Activity` — это `Activity`, которые объявляют фильтр намерений с `ACTION_MAIN` и `CATEGORY_LAUNCHER`. Они выступают в роли точек входа в приложение из лаунчера и используются для запуска задачи.

Когда пользователь нажимает кнопку или делает жест "Назад" из корневой launcher-`Activity` вашей задачи, система обрабатывает событие по-разному в зависимости от версии Android:

- Android 11 и ниже: по умолчанию система завершает эту `Activity` (и задачу).
- Android 12 и выше: по умолчанию система перемещает эту `Activity` и ее задачу в фон вместо завершения. Такое поведение согласуется с выходом из приложения через кнопку/жест "Домой" и обычно позволяет быстрее вернуться в приложение из "тёплого" состояния, а не запускать его с нуля.

Пользовательская обработка "Назад" (например, через `OnBackPressedDispatcher` или `OnBackInvokedCallback`) и навигационные библиотеки могут изменить фактическое поведение, но должны использоваться осторожно, чтобы не ломать ожидаемую модель навигации платформы.

### Управление задачами

По умолчанию Android управляет задачами и стеком возврата, помещая последовательно запущенные `Activity` в одну и ту же задачу в виде стека LIFO. Для большинства приложений этого достаточно, и обычно не требуется вручную управлять привязкой `Activity` к задачам.

Однако вы можете захотеть изменить поведение по умолчанию. Например:
- сделать так, чтобы определенная `Activity` запускалась в новой задаче, а не добавлялась в текущую;
- при запуске `Activity` выводить на передний план уже существующий экземпляр, а не создавать новый поверх стека;
- очистить стек возврата от всех `Activity`, кроме корневой, при определенных сценариях выхода пользователя.

Для этого используются атрибуты элемента `<activity>` в манифесте и флаги `Intent`, передаваемого в `startActivity()`.

Основные атрибуты `<activity>` для управления задачами:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`

## Answer (EN)
A **task** is a collection of activities that users interact with when trying to do something in your app. These activities are arranged in a stack called the **back stack** in the order in which each activity is opened.

For example, an email app might have one activity to show a list of new messages. When the user selects a message, a new activity opens to view that message. This new activity is added to the back stack. Then, when the user taps or gestures Back, that new activity finishes and is popped off the stack.

### Lifecycle of a Task and Its Back Stack

The device Home screen is the starting place for most tasks. When a user touches the icon for an app or shortcut in the app launcher or on the Home screen, that app's task comes to the foreground. If no task exists for the app, then a new task is created and the main activity for that app opens as the root activity in the stack.

When the current activity starts another, the new activity is pushed on the top of the stack and takes focus. The previous activity remains in the stack, but is stopped. When an activity is stopped, the system retains the current state of its user interface. When the user performs the back action, the current activity is popped from the top of the stack and destroyed. The previous activity resumes, and the previous state of its UI is restored.

Activities in a standard task back stack are not arbitrarily rearranged: they are primarily pushed onto and popped from the stack as they are started and finished via user navigation (Back button/gesture) or app calls to `finish()`. Therefore, the back stack operates as a **last in, first out** structure for that task. Specific intent flags and launch modes (for example `singleTask`, `singleInstance`, `FLAG_ACTIVITY_CLEAR_TOP`, `FLAG_ACTIVITY_REORDER_TO_FRONT`) can modify this behavior for particular activities and should be understood separately.

As the user continues to tap or gesture Back, each activity in the stack is popped off to reveal the previous one, until the user returns to the Home screen or to whichever activity was running when the task began. When all activities are removed from the stack, the task no longer exists.

### Background and Foreground Tasks

A task is a cohesive unit that can move to the **background** when a user begins a new task or goes to the Home screen. While in the background, all the activities in the task are stopped, but the back stack for the task remains intact — the task loses focus while another task is in the foreground. A task can then return to the **foreground** so users can pick up where they left off.

Note:
- Multiple tasks can be held in the background at once.
- If the system needs to reclaim memory, it may destroy processes and their activities that are in the background. In such cases, the exact UI state is not guaranteed: the system can recreate activities using saved instance state and persistent data, but only if the app has implemented proper state saving.

### Back Tap Behavior for Root Launcher Activities

Root launcher activities are activities that declare an intent filter with both `ACTION_MAIN` and `CATEGORY_LAUNCHER`. These activities act as primary entry points into your app from the app launcher and are used to start a task.

When a user taps or gestures Back from a root launcher activity of your task, the system handles the event differently depending on the version of Android:

- System behavior on Android 11 and lower: the system finishes the activity (and thus the task) by default.
- System behavior on Android 12 and higher: the system moves the activity and its task to the background instead of finishing the activity. This behavior matches the default system behavior when navigating out of an app using the Home button or gesture. In most cases, this means that users can more quickly resume your app from a warm state, instead of having to restart it from a cold state.

Custom back handling (for example, using `OnBackPressedDispatcher` or `OnBackInvokedCallback`) or navigation libraries can modify the effective behavior, but should be used carefully to keep expectations consistent with the platform.

### Manage Tasks

Android manages tasks and the back stack by placing activities started in succession into the same task, in a last-in, first-out stack. This works for most apps, and you usually don't have to manually manage how activities are associated with tasks or how they exist in the back stack.

However, you might decide that you want to modify the default behavior. For example:
- You might want an activity in your app to begin a new task when it is started, instead of being placed within the current task.
- When you start an activity, you might want to bring forward an existing instance of it instead of creating a new instance on top of the back stack.
- You might want your back stack to be cleared of all activities except for the root activity when the user leaves the task.

You can do this using attributes in the `<activity>` manifest element and flags in the `Intent` that you pass to `startActivity()`.

These are the principal `<activity>` attributes that you can use to manage tasks:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`

## Follow-ups

- [[c-activity-lifecycle]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]
- How does `launchMode` (`standard`, `singleTop`, `singleTask`, `singleInstance`) affect task and back stack behavior?
- How do `Intent` flags (`FLAG_ACTIVITY_NEW_TASK`, `FLAG_ACTIVITY_CLEAR_TOP`, etc.) affect existing tasks and their back stacks?
- How does Back behavior at the system level differ from navigation logic handled inside `NavController` / Navigation Component?

## References

- [Tasks and the back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack)

## Related Questions

- [[q-recyclerview-itemdecoration-advanced--android--medium]]
- [[q-database-encryption-android--android--medium]]
- [[q-what-to-put-in-state-for-initial-list--android--easy]]

## Ссылки (RU)
- [Задачи и стек возврата](https://developer.android.com/guide/components/activities/tasks-and-back-stack)
## Дополнительные вопросы (RU)
- Как `launchMode` (`standard`, `singleTop`, `singleTask`, `singleInstance`) влияет на формирование задач и стека возврата?
- Как флаги `Intent` (`FLAG_ACTIVITY_NEW_TASK`, `FLAG_ACTIVITY_CLEAR_TOP` и др.) влияют на существующие задачи и их back stack?
- Чем поведение кнопки/жеста "Назад" в системе навигации отличается от логики навигации внутри `NavController`/`Navigation Component`?