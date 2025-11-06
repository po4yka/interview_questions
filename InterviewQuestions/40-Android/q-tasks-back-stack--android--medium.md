---
id: android-227
title: Tasks and Back Stack / Задачи и стек возврата
aliases:
- Tasks and Back Stack
- Задачи и стек возврата
topic: android
subtopics:
- activity
- lifecycle
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
- c-navigation
- q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/activity
- android/lifecycle
- android/ui-navigation
- back-stack
- difficulty/medium
- launch-mode
- tasks
---

# Вопрос (RU)
> Задачи и стек возврата

# Question (EN)
> Tasks and Back `Stack`

---

**Русский**: Что вы знаете о задачах и стеке возврата?

## Answer (EN)
**English**:

A **task** is a collection of activities that users interact with when trying to do something in your app. These activities are arranged in a stack called the **back stack** in the order in which each activity is opened.

For example, an email app might have one activity to show a list of new messages. When the user selects a message, a new activity opens to view that message. This new activity is added to the back stack. Then, when the user taps or gestures Back, that new activity finishes and is popped off the stack.

### `Lifecycle` of a Task and Its Back `Stack`

The device Home screen is the starting place for most tasks. When a user touches the icon for an app or shortcut in the app launcher or on the Home screen, that app's task comes to the foreground. If no task exists for the app, then a new task is created and the main activity for that app opens as the root activity in the stack.

When the current activity starts another, the new activity is pushed on the top of the stack and takes focus. The previous activity remains in the stack, but is stopped. When an activity is stopped, the system retains the current state of its user interface. When the user performs the back action, the current activity is popped from the top of the stack and destroyed. The previous activity resumes, and the previous state of its UI is restored.

Activities in the stack are never rearranged, only pushed onto and popped from the stack as they are started by the current activity and dismissed by the user through the Back button or gesture. Therefore, the back stack operates as a **last in, first out** object structure.

As the user continues to tap or gesture Back, each activity in the stack is popped off to reveal the previous one, until the user returns to the Home screen or to whichever activity was running when the task began. When all activities are removed from the stack, the task no longer exists.

### Background and Foreground Tasks

A task is a cohesive unit that can move to the **background** when a user begins a new task or goes to the Home screen. While in the background, all the activities in the task are stopped, but the back stack for the task remains intact—the task loses focus while another task takes place. A task can then return to the **foreground** so users can pick up where they left off.

**Note**: Multiple tasks can be held in the background at once. However, if the user runs many background tasks at the same time, the system might begin destroying background activities to recover memory. If this happens, the activity states are lost.

### Back Tap Behavior for Root Launcher Activities

Root launcher activities are activities that declare an intent filter with both `ACTION_MAIN` and `CATEGORY_LAUNCHER`. These activities are unique because they act as entry points into your app from the app launcher and are used to start a task.

When a user taps or gestures Back from a root launcher activity, the system handles the event differently depending on the version of Android that the device is running:

- **System behavior on Android 11 and lower**: The system finishes the activity.
- **System behavior on Android 12 and higher**: The system moves the activity and its task to the background instead of finishing the activity. This behavior matches the default system behavior when navigating out of an app using the Home button or gesture. In most cases, this behavior means that users can more quickly resume your app from a warm state, instead of having to completely restart the app from a cold state.

### Manage Tasks

Android manages tasks and the back stack by placing all activities started in succession in the same task, in a last in, first out stack. This works great for most apps, and you usually don't have to worry about how your activities are associated with tasks or how they exist in the back stack.

However, you might decide that you want to interrupt the normal behavior. For example, you might want an activity in your app to begin a new task when it is started, instead of being placed within the current task. Or, when you start an activity, you might want to bring forward an existing instance of it, instead of creating a new instance on top of the back stack. Or you might want your back stack to be cleared of all activities except for the root activity when the user leaves the task.

You can do these things and more using attributes in the `<activity>` manifest element and flags in the intent that you pass to `startActivity()`.

These are the principal `<activity>` attributes that you can use to manage tasks:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`

**Русский**:

**Задача (task)** - это коллекция activities, с которыми взаимодействуют пользователи, когда пытаются что-то сделать в вашем приложении. Эти activities организованы в стек, называемый **стеком возврата (back stack)**, в том порядке, в котором открывается каждая activity.

Например, почтовое приложение может иметь одну activity для отображения списка новых сообщений. Когда пользователь выбирает сообщение, открывается новая activity для просмотра этого сообщения. Эта новая activity добавляется в стек возврата. Затем, когда пользователь нажимает или использует жест Назад, эта новая activity завершается и удаляется из стека.

### `Lifecycle` of a Task and Its Back `Stack`

Домашний экран устройства является отправной точкой для большинства задач. Когда пользователь касается значка приложения или ярлыка в средстве запуска приложений или на домашнем экране, задача этого приложения выходит на передний план. Если задачи для приложения не существует, то создается новая задача, и основная activity для этого приложения открывается как корневая activity в стеке.

Когда текущая activity запускает другую, новая activity помещается в верхнюю часть стека и получает фокус. Предыдущая activity остается в стеке, но останавливается. Когда activity остановлена, система сохраняет текущее состояние ее пользовательского интерфейса. Когда пользователь выполняет действие возврата, текущая activity извлекается из верхней части стека и уничтожается. Предыдущая activity возобновляется, и предыдущее состояние ее UI восстанавливается.

Activities в стеке никогда не переупорядочиваются, только помещаются в стек и извлекаются из него, когда они запускаются текущей activity и закрываются пользователем через кнопку или жест Назад. Следовательно, стек возврата работает как структура объектов **последним пришел, первым ушел (last in, first out)**.

По мере того, как пользователь продолжает нажимать или использовать жест Назад, каждая activity в стеке извлекается, чтобы показать предыдущую, пока пользователь не вернется на домашний экран или к той activity, которая выполнялась, когда началась задача. Когда все activities удалены из стека, задача больше не существует.

### Background and Foreground Tasks

Задача - это связная единица, которая может переместиться в **фон (background)**, когда пользователь начинает новую задачу или переходит на домашний экран. Находясь в фоне, все activities в задаче останавливаются, но стек возврата для задачи остается нетронутым - задача теряет фокус, пока выполняется другая задача. Затем задача может вернуться на **передний план (foreground)**, чтобы пользователи могли продолжить с того места, где остановились.

**Примечание**: Несколько задач могут одновременно находиться в фоне. Однако, если пользователь запускает много фоновых задач одновременно, система может начать уничтожать фоновые activities для восстановления памяти. Если это происходит, состояния activity теряются.

### Back Tap Behavior for Root Launcher Activities

Корневые launcher activities - это activities, которые объявляют intent filter с обоими `ACTION_MAIN` и `CATEGORY_LAUNCHER`. Эти activities уникальны, потому что они действуют как точки входа в ваше приложение из средства запуска приложений и используются для запуска задачи.

Когда пользователь нажимает или использует жест Назад из корневой launcher activity, система обрабатывает событие по-разному в зависимости от версии Android, которая работает на устройстве:

- **Поведение системы на Android 11 и ниже**: Система завершает activity.
- **Поведение системы на Android 12 и выше**: Система перемещает activity и ее задачу в фон вместо завершения activity. Это поведение соответствует стандартному поведению системы при выходе из приложения с помощью кнопки или жеста Домой. В большинстве случаев это поведение означает, что пользователи могут быстрее возобновить ваше приложение из теплого состояния, вместо того чтобы полностью перезапускать приложение из холодного состояния.

### Manage Tasks

Android управляет задачами и стеком возврата, помещая все последовательно запущенные activities в одну и ту же задачу в стек последним пришел, первым ушел. Это отлично работает для большинства приложений, и вам обычно не нужно беспокоиться о том, как ваши activities связаны с задачами или как они существуют в стеке возврата.

Однако вы можете решить, что хотите прервать нормальное поведение. Например, вы можете захотеть, чтобы activity в вашем приложении начала новую задачу при запуске, вместо того чтобы быть помещенной в текущую задачу. Или, когда вы запускаете activity, вы можете захотеть вывести на передний план существующий экземпляр, вместо создания нового экземпляра поверх стека возврата. Или вы можете захотеть, чтобы ваш стек возврата был очищен от всех activities, кроме корневой activity, когда пользователь покидает задачу.

Вы можете делать это и многое другое, используя атрибуты в элементе манифеста `<activity>` и флаги в intent, который вы передаете в `startActivity()`.

Это основные атрибуты `<activity>`, которые вы можете использовать для управления задачами:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`



# Question (EN)
> Tasks and Back `Stack`

---

**Русский**: Что вы знаете о задачах и стеке возврата?


---


## Answer (EN)
**English**:

A **task** is a collection of activities that users interact with when trying to do something in your app. These activities are arranged in a stack called the **back stack** in the order in which each activity is opened.

For example, an email app might have one activity to show a list of new messages. When the user selects a message, a new activity opens to view that message. This new activity is added to the back stack. Then, when the user taps or gestures Back, that new activity finishes and is popped off the stack.

### `Lifecycle` of a Task and Its Back `Stack`

The device Home screen is the starting place for most tasks. When a user touches the icon for an app or shortcut in the app launcher or on the Home screen, that app's task comes to the foreground. If no task exists for the app, then a new task is created and the main activity for that app opens as the root activity in the stack.

When the current activity starts another, the new activity is pushed on the top of the stack and takes focus. The previous activity remains in the stack, but is stopped. When an activity is stopped, the system retains the current state of its user interface. When the user performs the back action, the current activity is popped from the top of the stack and destroyed. The previous activity resumes, and the previous state of its UI is restored.

Activities in the stack are never rearranged, only pushed onto and popped from the stack as they are started by the current activity and dismissed by the user through the Back button or gesture. Therefore, the back stack operates as a **last in, first out** object structure.

As the user continues to tap or gesture Back, each activity in the stack is popped off to reveal the previous one, until the user returns to the Home screen or to whichever activity was running when the task began. When all activities are removed from the stack, the task no longer exists.

### Background and Foreground Tasks

A task is a cohesive unit that can move to the **background** when a user begins a new task or goes to the Home screen. While in the background, all the activities in the task are stopped, but the back stack for the task remains intact—the task loses focus while another task takes place. A task can then return to the **foreground** so users can pick up where they left off.

**Note**: Multiple tasks can be held in the background at once. However, if the user runs many background tasks at the same time, the system might begin destroying background activities to recover memory. If this happens, the activity states are lost.

### Back Tap Behavior for Root Launcher Activities

Root launcher activities are activities that declare an intent filter with both `ACTION_MAIN` and `CATEGORY_LAUNCHER`. These activities are unique because they act as entry points into your app from the app launcher and are used to start a task.

When a user taps or gestures Back from a root launcher activity, the system handles the event differently depending on the version of Android that the device is running:

- **System behavior on Android 11 and lower**: The system finishes the activity.
- **System behavior on Android 12 and higher**: The system moves the activity and its task to the background instead of finishing the activity. This behavior matches the default system behavior when navigating out of an app using the Home button or gesture. In most cases, this behavior means that users can more quickly resume your app from a warm state, instead of having to completely restart the app from a cold state.

### Manage Tasks

Android manages tasks and the back stack by placing all activities started in succession in the same task, in a last in, first out stack. This works great for most apps, and you usually don't have to worry about how your activities are associated with tasks or how they exist in the back stack.

However, you might decide that you want to interrupt the normal behavior. For example, you might want an activity in your app to begin a new task when it is started, instead of being placed within the current task. Or, when you start an activity, you might want to bring forward an existing instance of it, instead of creating a new instance on top of the back stack. Or you might want your back stack to be cleared of all activities except for the root activity when the user leaves the task.

You can do these things and more using attributes in the `<activity>` manifest element and flags in the intent that you pass to `startActivity()`.

These are the principal `<activity>` attributes that you can use to manage tasks:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`

**Русский**:

**Задача (task)** - это коллекция activities, с которыми взаимодействуют пользователи, когда пытаются что-то сделать в вашем приложении. Эти activities организованы в стек, называемый **стеком возврата (back stack)**, в том порядке, в котором открывается каждая activity.

Например, почтовое приложение может иметь одну activity для отображения списка новых сообщений. Когда пользователь выбирает сообщение, открывается новая activity для просмотра этого сообщения. Эта новая activity добавляется в стек возврата. Затем, когда пользователь нажимает или использует жест Назад, эта новая activity завершается и удаляется из стека.

### `Lifecycle` of a Task and Its Back `Stack`

Домашний экран устройства является отправной точкой для большинства задач. Когда пользователь касается значка приложения или ярлыка в средстве запуска приложений или на домашнем экране, задача этого приложения выходит на передний план. Если задачи для приложения не существует, то создается новая задача, и основная activity для этого приложения открывается как корневая activity в стеке.

Когда текущая activity запускает другую, новая activity помещается в верхнюю часть стека и получает фокус. Предыдущая activity остается в стеке, но останавливается. Когда activity остановлена, система сохраняет текущее состояние ее пользовательского интерфейса. Когда пользователь выполняет действие возврата, текущая activity извлекается из верхней части стека и уничтожается. Предыдущая activity возобновляется, и предыдущее состояние ее UI восстанавливается.

Activities в стеке никогда не переупорядочиваются, только помещаются в стек и извлекаются из него, когда они запускаются текущей activity и закрываются пользователем через кнопку или жест Назад. Следовательно, стек возврата работает как структура объектов **последним пришел, первым ушел (last in, first out)**.

По мере того, как пользователь продолжает нажимать или использовать жест Назад, каждая activity в стеке извлекается, чтобы показать предыдущую, пока пользователь не вернется на домашний экран или к той activity, которая выполнялась, когда началась задача. Когда все activities удалены из стека, задача больше не существует.

### Background and Foreground Tasks

Задача - это связная единица, которая может переместиться в **фон (background)**, когда пользователь начинает новую задачу или переходит на домашний экран. Находясь в фоне, все activities в задаче останавливаются, но стек возврата для задачи остается нетронутым - задача теряет фокус, пока выполняется другая задача. Затем задача может вернуться на **передний план (foreground)**, чтобы пользователи могли продолжить с того места, где остановились.

**Примечание**: Несколько задач могут одновременно находиться в фоне. Однако, если пользователь запускает много фоновых задач одновременно, система может начать уничтожать фоновые activities для восстановления памяти. Если это происходит, состояния activity теряются.

### Back Tap Behavior for Root Launcher Activities

Корневые launcher activities - это activities, которые объявляют intent filter с обоими `ACTION_MAIN` и `CATEGORY_LAUNCHER`. Эти activities уникальны, потому что они действуют как точки входа в ваше приложение из средства запуска приложений и используются для запуска задачи.

Когда пользователь нажимает или использует жест Назад из корневой launcher activity, система обрабатывает событие по-разному в зависимости от версии Android, которая работает на устройстве:

- **Поведение системы на Android 11 и ниже**: Система завершает activity.
- **Поведение системы на Android 12 и выше**: Система перемещает activity и ее задачу в фон вместо завершения activity. Это поведение соответствует стандартному поведению системы при выходе из приложения с помощью кнопки или жеста Домой. В большинстве случаев это поведение означает, что пользователи могут быстрее возобновить ваше приложение из теплого состояния, вместо того чтобы полностью перезапускать приложение из холодного состояния.

### Manage Tasks

Android управляет задачами и стеком возврата, помещая все последовательно запущенные activities в одну и ту же задачу в стек последним пришел, первым ушел. Это отлично работает для большинства приложений, и вам обычно не нужно беспокоиться о том, как ваши activities связаны с задачами или как они существуют в стеке возврата.

Однако вы можете решить, что хотите прервать нормальное поведение. Например, вы можете захотеть, чтобы activity в вашем приложении начала новую задачу при запуске, вместо того чтобы быть помещенной в текущую задачу. Или, когда вы запускаете activity, вы можете захотеть вывести на передний план существующий экземпляр, вместо создания нового экземпляра поверх стека возврата. Или вы можете захотеть, чтобы ваш стек возврата был очищен от всех activities, кроме корневой activity, когда пользователь покидает задачу.

Вы можете делать это и многое другое, используя атрибуты в элементе манифеста `<activity>` и флаги в intent, который вы передаете в `startActivity()`.

Это основные атрибуты `<activity>`, которые вы можете использовать для управления задачами:
- `taskAffinity`
- `launchMode`
- `allowTaskReparenting`
- `clearTaskOnLaunch`
- `alwaysRetainTaskState`
- `finishOnTaskLaunch`


## Ответ (RU)


## Ответ (RU)

## References

- [Tasks and the back stack](https://developer.android.com/guide/components/activities/tasks-and-back-stack)


## Follow-ups

- [[c-activity-lifecycle]]
- [[c-navigation]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]


## Related Questions

- [[q-recyclerview-itemdecoration-advanced--android--medium]]
- [[q-database-encryption-android--android--medium]]
- [[q-what-to-put-in-state-for-initial-list--android--easy]]
