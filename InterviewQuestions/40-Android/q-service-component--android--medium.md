---\
id: android-008
title: Android Service Component / Компонент Service в Android
aliases: [Android Service Component, Компонент Service в Android]
topic: android
subtopics: [background-execution, lifecycle, service]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related: [c-background-tasks, c-lifecycle, c-service, q-android-service-types--android--easy, q-android-services-purpose--android--easy, q-anr-application-not-responding--android--medium, q-service-types-android--android--easy]
created: 2025-10-05
updated: 2025-11-10
tags: [android/background-execution, android/lifecycle, android/service, difficulty/medium, en, ru]
anki_cards:
  - slug: android-008-0-en
    front: "What are the three types of Android Services?"
    back: |
      **Three types**:

      1. **Foreground** - user-visible, must show notification (e.g., music player)
      2. **Background** - not noticed by user, limited on modern Android
      3. **Bound** - client-server interface via `bindService()`, destroyed when all unbind

      **Key callbacks**:
      - `onStartCommand()` - for started services
      - `onBind()` - returns IBinder for bound services
      - `onCreate()` / `onDestroy()` - lifecycle

      Note: Use `WorkManager` for most background tasks on modern Android.
    tags:
      - android_services
      - difficulty::medium
  - slug: android-008-0-ru
    front: "Какие три типа Service существуют в Android?"
    back: |
      **Три типа**:

      1. **Foreground** - видимый пользователю, должен показывать уведомление (например, музыкальный плеер)
      2. **Background** - незаметный для пользователя, ограничен на современном Android
      3. **Bound** - клиент-серверный интерфейс через `bindService()`, уничтожается когда все отвяжутся

      **Ключевые callbacks**:
      - `onStartCommand()` - для started-сервисов
      - `onBind()` - возвращает IBinder для bound-сервисов
      - `onCreate()` / `onDestroy()` - жизненный цикл

      Примечание: используйте `WorkManager` для большинства фоновых задач.
    tags:
      - android_services
      - difficulty::medium

---\
# Вопрос (RU)
> Что такое `Service`?

# Question (EN)
> What's `Service`?

## Ответ (RU)

`Service` — это компонент приложения, который может выполнять операции в фоновом режиме и не предоставляет пользовательский интерфейс. Другой компонент приложения может запустить сервис, и (в зависимости от его типа и ограничений платформы) он может продолжить работу даже при переключении пользователя на другое приложение. Кроме того, компонент может привязаться к сервису для взаимодействия с ним и даже для межпроцессного взаимодействия (IPC). Например, сервис может обрабатывать сетевые запросы, воспроизводить музыку, выполнять файловый ввод-вывод или взаимодействовать с контент-провайдером в фоне.

По умолчанию сервис выполняется в том же процессе, что и приложение, а его методы жизненного цикла вызываются в основном потоке. Если нужно реализовать сложную или длительную работу, её необходимо перенести с основного потока (например, в отдельный поток, корутину или другой асинхронный механизм), иначе блокировка UI может привести к ANR.

Как правило, процессы с запущенными сервисами в целом имеют более высокий приоритет, чем процессы только с неактивными/невидимыми активити, поэтому они реже завершаются. Однако система может остановить сервис в любой момент для высвобождения ресурсов, при убийстве процесса или при применении ограничений фонового выполнения. Сервис может запросить перезапуск (через значение, возвращаемое из `onStartCommand()`), если он был завершён и ресурсы снова стали доступны.

Замечание (современный Android): из-за ограничений фонового выполнения (начиная с Android 8.0 Oreo) приложениям запрещено свободно запускать долгоживущие фоновые сервисы из фона. Для длительных задач следует использовать сервисы переднего плана, `WorkManager` или другие подходящие API.

### Типы Сервисов

Традиционно выделяют три концептуальных типа сервисов: Foreground (передний план), Background (фоновый), Bound (привязанный).

- **Background (фоновый)**: Выполняет операции, которые не замечаются пользователем напрямую. Ранее приложение могло запускать такой сервис для фоновой работы (например, оптимизации хранилища). В современных версиях Android запуск неограниченных долгоживущих фоновых сервисов существенно ограничен; чаще следует использовать планировщики или foreground-механизмы (`WorkManager`, foreground `Service`) там, где это уместно.
- **Bound (привязанный)**: Сервис становится привязанным, когда компонент приложения вызывает `bindService()`. Привязанный сервис предоставляет клиент-серверный интерфейс для взаимодействия: отправка запросов, получение результатов, IPC. Такой сервис работает, пока к нему привязан хотя бы один компонент. Несколько компонентов могут быть привязаны одновременно; когда все отвяжутся (и сервис не был отдельно запущен), сервис уничтожается.
- **Foreground (передний план)**: Выполняет операции, заметные для пользователя. Например, аудиоплеер использует сервис переднего плана для воспроизведения аудио. Такой сервис обязан показать продолжающееся `Notification` вскоре после старта и может продолжать работать, даже когда пользователь не взаимодействует с приложением, но остаётся под действием политик платформы (типы foreground-сервисов, ограничения на запуск и т.п.).

### Объявление Сервиса

Все сервисы необходимо объявить в манифесте приложения, как и активити и другие компоненты.

Чтобы объявить сервис, добавьте элемент `<service>` внутрь элемента `<application>`. Пример:

```xml
<manifest ... >
  ...
  <application ... >
      <service android:name=".ExampleService" />
      ...
  </application>
</manifest>
```

### Основы

Чтобы создать сервис, нужно унаследоваться от `Service` или одного из его подклассов. В реализации переопределяются методы обратного вызова жизненного цикла и, при необходимости, реализуется механизм привязки клиентов к сервису.

Ключевые методы обратного вызова:

- **`onStartCommand()`** – Вызывается, когда другой компонент (например, активити) вызывает `startService()`. После этого сервис считается запущенным и может выполнять работу в фоне до тех пор, пока не будет остановлен вызовом `stopSelf()` или `stopService()`. Если сервис предназначен только для привязки (и `startService()` не используется), этот метод можно не переопределять.
- **`onBind()`** – Вызывается при вызове `bindService()` для привязки к сервису. В этом методе нужно вернуть `IBinder`, через который клиенты будут общаться с сервисом. Для сервисов, которые используются только как запущенные (started) и не поддерживают привязку, можно вернуть `null`. Для привязанных сервисов необходимо предоставить валидную реализацию `IBinder`.
- **`onCreate()`** – Вызывается один раз при первоначальном создании сервиса (до `onStartCommand()` или `onBind()`). Если сервис уже запущен, повторно не вызывается.
- **`onDestroy()`** – Вызывается, когда сервис больше не используется и уничтожается. Здесь следует освободить ресурсы: потоки, слушателей, приёмники и т.п. Это последний колбэк жизненного цикла сервиса.

Если компонент запускает сервис через `startService()` (что приводит к вызову `onStartCommand()`), сервис продолжает работать до явной остановки (`stopSelf()` или `stopService()`), с учётом возможного вмешательства системы.

Если компонент вызывает только `bindService()` (без `startService()`), сервис работает, пока к нему привязан хотя бы один клиент. После отвязки всех клиентов (и при отсутствии статуса "запущен") система уничтожает сервис.

Система может остановить сервис при нехватке ресурсов, при убийстве процесса или при применении ограничений фонового выполнения. Сервис переднего плана или сервис, привязанный к компоненту с фокусом, имеет меньшую вероятность быть завершённым.

### Возвращаемые Значения onStartCommand()

`onStartCommand()` возвращает целочисленный флаг, определяющий, как система должна вести себя при убийстве сервиса:

- **`START_NOT_STICKY`** – Если система убивает сервис после `onStartCommand()`, сервис не пересоздаётся, пока нет ожидающих `Intent`. Подходит, когда незавершённую работу можно безопасно запустить заново при следующем обращении.
- **`START_STICKY`** – Если система убивает сервис после `onStartCommand()`, сервис пересоздаётся, `onStartCommand()` вызывается снова, но последний `Intent` не доставляется повторно. Вместо этого приходит `null` (если нет новых `Intent`). Подходит для сервисов, которые работают долго и ожидают команды (например, медиаплеер).
- **`START_REDELIVER_INTENT`** – Если система убивает сервис после `onStartCommand()`, сервис пересоздаётся, и `onStartCommand()` вызывается с последним доставленным `Intent`; ожидающие `Intent` доставляются по очереди. Подходит для задач, которые важно продолжить с того же места (например, загрузка файла).

### Жизненный Цикл Сервиса

Жизненный цикл сервиса проще, чем у активити, но требует аккуратной реализации, так как сервис может работать в фоне без явной индикации для пользователя.

Два основных варианта:

- **Запущенный сервис (started)**: Создаётся вызовом `startService()`. Работает (с учётом системных ограничений) до вызова `stopSelf()` или `stopService()`. После остановки система уничтожает сервис.

- **Привязанный сервис (bound)**: Создаётся при вызове `bindService()`. Клиенты взаимодействуют с сервисом через `IBinder`. Несколько клиентов могут быть привязаны одновременно; когда все отвязываются и сервис не запущен как started, система уничтожает его. В этом сценарии сервис обычно не вызывает `stopSelf()`.

Эти варианты можно комбинировать. Например, можно запустить музыкальный сервис через `startService()`, а затем привязать к нему активити через `bindService()` для управления воспроизведением. В таком случае `stopService()` или `stopSelf()` не остановят сервис, пока все привязанные клиенты не отвяжутся.

## Answer (EN)

A `Service` is an application component that can perform operations in the background without providing a user interface. Another application component can start a service, and (depending on its type and platform constraints) it may continue to run even if the user switches to another application. Additionally, a component can bind to a service to interact with it and even perform interprocess communication (IPC). For example, a service can handle network transactions, play music, perform file I/O, or interact with a content provider from the background.

By default, a service runs in the same process as the application, and its lifecycle callbacks are executed on the main thread. If you need to implement complex or long-running work, you must move that work off the main thread (e.g., to your own thread, coroutine, or other async mechanism), otherwise it may block the UI and cause ANR issues.

Services generally have a higher process priority than inactive or invisible activities, so they are less likely to be terminated than purely cached/background activities. However, the system can still stop services at any time to reclaim resources or enforce background execution limits. Services can request to be restarted (via the value returned from `onStartCommand()`) if they are terminated and resources later become available.

Note (modern Android): due to background execution limits (starting with Android 8.0 Oreo), apps have restrictions on starting background services while in the background. `Long`-running background work should typically use foreground services, `WorkManager`, or other appropriate APIs.

### Types of Services

These are three conceptual types of services: Foreground, Background, Bound.

- **Background**: A background service performs an operation that is not directly noticed by the user. Traditionally, an app could start such a service to do work in the background (e.g., compact storage). On modern Android versions, starting unrestricted long-running background services is limited; use scheduled or foreground mechanisms when appropriate.
- **Bound**: A service is bound when an application component binds to it by calling `bindService()`. A bound service offers a client-server interface that allows components to interact with the service, send requests, receive results, and even do so across processes with IPC. A bound service runs only as long as another application component is bound to it. Multiple components can bind to the service at once, but when all of them unbind, the service is destroyed (unless it was also started).
- **Foreground**: A foreground service performs some operation that is noticeable to the user. For example, an audio app would use a foreground service to play an audio track. Foreground services must display an ongoing `Notification` shortly after starting; they continue running even when the user isn't directly interacting with the app, but are still subject to platform policies (e.g., foreground service types, user-initiated restrictions).

### Declaring a `Service`

You must declare services in your application's manifest file, just as you do for activities and other components.

To declare your service, add a `<service>` element as a child of the `<application>` element. For example:

```xml
<manifest ... >
  ...
  <application ... >
      <service android:name=".ExampleService" />
      ...
  </application>
</manifest>
```

### The Basics

To create a service, you create a subclass of `Service` or use one of its existing subclasses. In your implementation, you override callback methods that handle key aspects of the service lifecycle and, if needed, provide a mechanism that allows components to bind to the service.

These are the most important callback methods:

- **`onStartCommand()`** – Called when another component (such as an activity) calls `startService()`. After this method is called, the service is considered started and can run in the background until you explicitly stop it by calling `stopSelf()` or another component calls `stopService()`. If you only want to support binding (and never call `startService()`), you don't need to implement this method.
- **`onBind()`** – Called when another component calls `bindService()` to bind to the service. In this method you return an `IBinder` that clients use to communicate with the service. For services that are only ever started (not bound), you can return `null`. For bound services, you must provide a valid binder implementation.
- **`onCreate()`** – Called once when the service is first created (before `onStartCommand()` or `onBind()`). If the service is already running, this method is not called again.
- **`onDestroy()`** – Called when the service is no longer used and is being destroyed. Use this to clean up resources such as threads, registered listeners, or receivers. This is the last lifecycle callback the service receives.

If a component starts the service by calling `startService()` (which results in a call to `onStartCommand()`), the service continues to run until it stops itself with `stopSelf()` or another component stops it with `stopService()`, subject to system constraints.

If a component calls `bindService()` (without also calling `startService()`), the service runs only as long as at least one client remains bound. After all clients unbind, the system destroys the service.

The system may stop a service when it needs resources, when background execution limits apply, or when the process is killed. If the service is running in the foreground or is bound to a component in the foreground, it is less likely to be killed.

### onStartCommand() Return Values

`onStartCommand()` requires that you return an integer flag indicating how the system should handle the service if it is killed:

- **`START_NOT_STICKY`** – If the system kills the service after `onStartCommand()` returns, do not recreate the service unless there are pending intents to deliver. Suitable when your app can simply restart unfinished work as needed.
- **`START_STICKY`** – If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()`, but do not redeliver the last intent. Instead, the system calls `onStartCommand()` with a `null` intent unless there are pending intents. Suitable for services that run indefinitely and wait for work (e.g., a media player idle and awaiting commands).
- **`START_REDELIVER_INTENT`** – If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()` again with the last intent. Pending intents are delivered in turn. Suitable for services that must resume the exact ongoing work (e.g., downloading a file).

### `Service` Lifecycle

The lifecycle of a service is simpler than that of an activity but requires careful handling because a service can run in the background without the user being aware.

Two primary lifecycle paths:

- **Started service**: Created when another component calls `startService()`. It runs (subject to system/background limits) until `stopSelf()` or `stopService()` is called. When stopped, the system destroys it.

- **Bound service**: Created when a client calls `bindService()`. The client communicates with the service through an `IBinder`. Multiple clients can bind; when all have unbound and the service is not started, the system destroys it. The service does not call `stopSelf()` in the purely bound-only case.

These paths can be combined. For example, you can start a background music service with `startService()` and later have an activity bind to it with `bindService()` to control playback. In such cases, `stopService()`/`stopSelf()` will not fully stop the service until all bound clients have unbound.

## Follow-ups

- [[q-anr-application-not-responding--android--medium]]
- Как реализовать безопасную работу `Service` с долгими задачами, чтобы избежать ANR и утечек памяти?
- В каких случаях предпочтительнее использовать `WorkManager` вместо `Service`?
- Каковы ключевые отличия между started и bound `Service` в плане жизненного цикла и управления ресурсами?
- Как правильно организовать foreground `Service` и уведомления для длительных операций (например, воспроизведения медиа или загрузок)?

## References
- [Services overview](https://developer.android.com/guide/components/services)
- [Android `Service` Tutorial](https://www.vogella.com/tutorials/AndroidServices/article.html)
- [Android `Service` Tutorial](https://www.survivingwithandroid.com/android-service-tutorial-2/)

## Related Questions

### Prerequisites / Concepts

- [[c-service]]
- [[c-background-tasks]]
- [[c-lifecycle]]

### Related (Medium)
- [[q-memory-leak-detection--android--medium]] - Performance
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]] - Coroutines
- [[q-repeatonlifecycle-android--kotlin--medium]] - Coroutines
- [[q-viewmodel-coroutines-lifecycle--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-lifecycle-aware-coroutines--kotlin--hard]] - Coroutines