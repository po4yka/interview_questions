---
id: 202510051234002
title: "Background Tasks Decision Guide / Руководство по фоновым задачам"
topic: android
status: draft
created: 2025-10-05
updated: 2025-10-05
difficulty: medium
topics:
  - android
subtopics:
  - background-execution
  - coroutines
  - service
tags: [background-tasks, workmanager, coroutines, service, difficulty/medium, android/execution, android/coroutines, android/service]
language_tags: [background-tasks, workmanager, coroutines, service, difficulty/medium, android/execution, android/coroutines, android/service]
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20background%20task%20and%20how%20it%20should%20be%20performed.md
author: null
related:
  - "[[moc-android]]"
  - "[[q-workmanager-basics--android--medium]]"
  - "[[q-foreground-services--android--medium]]"
moc:
  - "[[moc-android]]"
connections: []
---

# Background Tasks Decision Guide / Руководство по фоновым задачам

# Question (EN)
> What is a background task and how should it be performed?

# Вопрос (RU)
> Что такое фоновая задача и как она должна выполняться?

---

## Answer (EN)

### Definition

For the purposes of background work, we use the term "task" to mean an operation an app is doing outside its main workflow. Background tasks are categorized into three main types:

1. **Asynchronous work**
2. **Task scheduling APIs**
3. **Foreground services**

### 1. Asynchronous Work

In many cases, an app just needs to do concurrent operations while it's running in the foreground. For example, an app might need to do a time-consuming calculation. If it did the calculation on the UI thread, the user wouldn't be able to interact with the app until the calculation finished; this might result in an ANR error.

**Common asynchronous work options include:**
- Kotlin coroutines
- Java threads

### 2. Task Scheduling APIs

The task scheduling APIs are a more flexible option when you need to do tasks that need to continue even if the user leaves the app. In most cases, the best option for running background tasks is to use `WorkManager`, though in some cases it may be appropriate to use the platform `JobScheduler` API.

**WorkManager** is a powerful library that lets you set up simple or complicated jobs as you need. You can use `WorkManager` to:
- Schedule tasks to run at specific times
- Specify the conditions when the task should run
- Set up chains of tasks, so each task runs in turn, passing its results to the next one

**Common scenarios for background tasks include:**
- Fetching data from server periodically
- Fetching sensor data (for example, step counter data)
- Getting periodic location data
- Uploading content based on a content trigger, such as photos created by the camera

### 3. Foreground Services

Foreground services offer a powerful way to run tasks immediately that ought not to be interrupted. However, foreground services can potentially put a heavy load on the device, and sometimes they have privacy and security implications.

**Key characteristics:**
- Must be noticeable to the user
- Apps can't launch foreground services when the apps are in the background (in most cases)
- Subject to many restrictions on how and when they can be used

**Two methods for creating a foreground service:**
1. Declare your own `Service` and specify that the service is a foreground service by calling `Service.startForeground()`
2. Use `WorkManager` to create a foreground service

## Choose the Right Option

### Tasks Initiated by the User

When an app needs to perform background tasks initiated by the user while the app is visible, answer these questions:

#### 1. Does the task need to continue running while the app is in the background?

**No** → Use **asynchronous work**
- These options stop operating if the app goes into the background or is shut down
- Example: A social media app refreshing its content feed doesn't need to finish if the user leaves the screen

#### 2. Will there be a bad user experience if the task is deferred or interrupted?

**Yes, it can be deferred** → Use **task scheduling APIs**
- Consider whether the user would notice if the operation happens right away or in the middle of the night
- Example: An app updating its assets can do this during off-peak hours

#### 3. Is it a short, critical task?

**Yes** → Use **foreground service with type `shortService`**
- For tasks that cannot be delayed and will complete quickly
- Don't require as many permissions as other foreground services
- Must complete within three minutes

#### 4. Is there an alternative API just for this purpose?

**Check for specialized APIs first** → Before using a foreground service, check if there's a specialized API
- Example: For location-based actions, use the geofence API instead of tracking location with a foreground service
- Foreground services use a lot of device resources and have many restrictions

**Otherwise** → Use **foreground services**
- For tasks where interruption would create a bad user experience
- Example: A workout-tracking app recording a jogging route on a map

### Tasks in Response to an Event

Sometimes an app needs to do background work in response to a trigger:
- Broadcast messages
- Firebase Cloud Messaging (FCM) messages
- Alarms set by the app

#### Decision tree:

**Can the task finish in a few seconds?**
- **Yes** → Use **asynchronous work**
  - The system allows your app a few seconds to perform such tasks, even if your app was in the background

**Will the task take longer than a few seconds?**
- **Check if you can start a foreground service** → Even if your app is in the background, it might be permitted to start a foreground service if:
  - The task was triggered by the user
  - It falls into one of the approved exemptions from background start restrictions
  - Example: An app receiving a high-priority FCM message is permitted to start a foreground service

- **Otherwise** → Use **task scheduling APIs**

## Summary Table

| Scenario | Duration | User Visible | Recommended Solution |
|----------|----------|--------------|---------------------|
| App in foreground, task doesn't need to continue in background | Any | Yes | Asynchronous work (coroutines/threads) |
| Task can be deferred | Long | No | Task scheduling APIs (WorkManager) |
| Short, critical task | < 3 minutes | Yes | Foreground service (shortService) |
| Long, critical task with specialized API | Long | Yes | Use specialized API (e.g., geofence) |
| Long, critical task without alternative | Long | Yes | Foreground service |
| Response to event, quick task | < few seconds | No | Asynchronous work |
| Response to event, long task | > few seconds | Varies | Foreground service or task scheduling APIs |

---

## Ответ (RU)

### Определение

Для целей фоновой работы мы используем термин "задача" для обозначения операции, которую приложение выполняет вне своего основного рабочего процесса. Фоновые задачи делятся на три основных типа:

1. **Асинхронная работа**
2. **API планирования задач**
3. **Сервисы переднего плана**

### 1. Асинхронная работа

Во многих случаях приложению просто нужно выполнять параллельные операции, пока оно работает на переднем плане. Например, приложению может понадобиться выполнить трудоемкие вычисления. Если бы оно выполняло вычисления в UI-потоке, пользователь не смог бы взаимодействовать с приложением до завершения вычислений; это могло бы привести к ошибке ANR.

**Распространенные варианты асинхронной работы включают:**
- Kotlin корутины
- Java потоки

### 2. API планирования задач

API планирования задач - более гибкий вариант, когда вам нужно выполнять задачи, которые должны продолжаться, даже если пользователь покидает приложение. В большинстве случаев лучшим вариантом для выполнения фоновых задач является использование `WorkManager`, хотя в некоторых случаях может быть уместно использовать платформенный API `JobScheduler`.

**WorkManager** - это мощная библиотека, которая позволяет настраивать простые или сложные задания по мере необходимости. Вы можете использовать `WorkManager` для:
- Планирования задач для запуска в определенное время
- Указания условий, при которых задача должна запуститься
- Настройки цепочек задач, чтобы каждая задача выполнялась по очереди, передавая свои результаты следующей

**Распространенные сценарии для фоновых задач включают:**
- Периодическое получение данных с сервера
- Получение данных с датчиков (например, данных счетчика шагов)
- Получение периодических данных о местоположении
- Загрузка контента на основе триггера контента, например, фотографий, созданных камерой

### 3. Сервисы переднего плана

Сервисы переднего плана предлагают мощный способ немедленного выполнения задач, которые не должны прерываться. Однако сервисы переднего плана могут потенциально создавать большую нагрузку на устройство, а иногда имеют последствия для конфиденциальности и безопасности.

**Ключевые характеристики:**
- Должны быть заметны пользователю
- Приложения не могут запускать сервисы переднего плана, когда приложения находятся в фоновом режиме (в большинстве случаев)
- Подлежат многим ограничениям на то, как и когда они могут использоваться

**Два метода создания сервиса переднего плана:**
1. Объявить свой собственный `Service` и указать, что сервис является сервисом переднего плана, вызвав `Service.startForeground()`
2. Использовать `WorkManager` для создания сервиса переднего плана

## Выберите правильный вариант

### Задачи, инициированные пользователем

Когда приложению нужно выполнять фоновые задачи, инициированные пользователем, пока приложение видимо, ответьте на эти вопросы:

#### 1. Должна ли задача продолжать выполняться, пока приложение находится в фоновом режиме?

**Нет** → Используйте **асинхронную работу**
- Эти варианты прекращают работу, если приложение переходит в фоновый режим или завершается
- Пример: Приложение социальных сетей, обновляющее ленту контента, не нужно завершать, если пользователь покидает экран

#### 2. Будет ли плохой пользовательский опыт, если задача будет отложена или прервана?

**Да, может быть отложена** → Используйте **API планирования задач**
- Подумайте, заметит ли пользователь, произойдет ли операция прямо сейчас или посреди ночи
- Пример: Приложение, обновляющее свои ресурсы, может сделать это в непиковые часы

#### 3. Это короткая, критическая задача?

**Да** → Используйте **сервис переднего плана с типом `shortService`**
- Для задач, которые нельзя откладывать и которые быстро завершатся
- Не требуют столько разрешений, сколько другие сервисы переднего плана
- Должны завершиться в течение трех минут

#### 4. Существует ли альтернативный API специально для этой цели?

**Сначала проверьте наличие специализированных API** → Перед использованием сервиса переднего плана проверьте наличие специализированного API
- Пример: Для действий на основе местоположения используйте API geofence вместо отслеживания местоположения с помощью сервиса переднего плана
- Сервисы переднего плана используют много ресурсов устройства и имеют много ограничений

**В противном случае** → Используйте **сервисы переднего плана**
- Для задач, где прерывание создаст плохой пользовательский опыт
- Пример: Приложение для отслеживания тренировок, записывающее маршрут пробежки на карту

### Задачи в ответ на событие

Иногда приложению нужно выполнять фоновую работу в ответ на триггер:
- Широковещательные сообщения
- Сообщения Firebase Cloud Messaging (FCM)
- Будильники, установленные приложением

#### Дерево решений:

**Может ли задача завершиться за несколько секунд?**
- **Да** → Используйте **асинхронную работу**
  - Система позволяет вашему приложению несколько секунд для выполнения таких задач, даже если ваше приложение было в фоновом режиме

**Займет ли задача больше нескольких секунд?**
- **Проверьте, можете ли вы запустить сервис переднего плана** → Даже если ваше приложение находится в фоновом режиме, ему может быть разрешено запустить сервис переднего плана, если:
  - Задача была запущена пользователем
  - Она попадает под одно из утвержденных исключений из ограничений фонового запуска
  - Пример: Приложение, получающее высокоприоритетное сообщение FCM, может запустить сервис переднего плана

- **В противном случае** → Используйте **API планирования задач**

## Сводная таблица

| Сценарий | Длительность | Видим пользователю | Рекомендуемое решение |
|----------|--------------|-------------------|----------------------|
| Приложение на переднем плане, задача не должна продолжаться в фоне | Любая | Да | Асинхронная работа (корутины/потоки) |
| Задачу можно отложить | Долгая | Нет | API планирования задач (WorkManager) |
| Короткая, критическая задача | < 3 минут | Да | Сервис переднего плана (shortService) |
| Долгая, критическая задача со специализированным API | Долгая | Да | Использовать специализированный API (например, geofence) |
| Долгая, критическая задача без альтернативы | Долгая | Да | Сервис переднего плана |
| Ответ на событие, быстрая задача | < нескольких секунд | Нет | Асинхронная работа |
| Ответ на событие, долгая задача | > нескольких секунд | Варьируется | Сервис переднего плана или API планирования задач |

---

## References

- [Android Developer Docs: Background tasks overview](https://developer.android.com/develop/background-work/background-tasks)
- [Kotlin Coroutines](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Kotlin/What%20are%20coroutines.md)
- [WorkManager](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What's%20WorkManager.md)
- [Foreground Services](https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20Foreground%20Services.md)

---

## Related Questions

### Prerequisites (Easier)
- [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
- [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
- [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)
- [[q-dagger-build-time-optimization--android--medium]] - Ui
- [[q-rxjava-pagination-recyclerview--android--medium]] - Ui
- [[q-build-optimization-gradle--gradle--medium]] - Ui
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui
- [[q-testing-compose-ui--android--medium]] - Ui
