---
id: android-008
title: Android Service Component / Компонент Service в Android
aliases:
- Android Service Component
- Компонент Service в Android
topic: android
subtopics:
- background-execution
- lifecycle
- service
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- android/background-processing
- android/components
- android/lifecycle
- difficulty/medium
- en
- ru
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository
status: draft
moc: moc-android
related:
- c-service
- c-background-tasks
- c-lifecycle
- q-anr-application-not-responding--android--medium
- q-how-to-start-drawing-ui-in-android--android--easy
created: 2025-10-05
updated: 2025-10-05
tags:
- android/background-execution
- android/lifecycle
- android/service
- difficulty/medium
- en
- ru

---

# Question (EN)
> What's `Service`?
# Вопрос (RU)
> Что такое `Service`?

---

## Answer (EN)

A `Service` is an application component that can perform long-running operations in the background, and it doesn't provide a user interface. Another application component can start a service, and it continues to run in the background even if the user switches to another application. Additionally, a component can bind to a service to interact with it and even perform interprocess communication (IPC). For example, a service can handle network transactions, play music, perform file I/O, or interact with a content provider, all from the background.

By default, a service runs in the same process as the main thread of the application. If we have to implement complex logic, with longtime processing, we have to take care of creating a new thread, otherwise, the Android service runs on the main thread and it could cause ANR problem.

Services run with a higher priority than inactive or invisible activities and therefore it is less likely that the Android system terminates them. Services can also be configured to be restarted if they get terminated by the Android system once sufficient system resources are available again.

### Types of Services

These are the three different types of services: Foreground, Background, Bound.

- **Background**: A background service performs an operation that isn't directly noticed by the user. For example, if an app used a service to compact its storage, that would usually be a background service
- **Bound**: A service is bound when an application component binds to it by calling `bindService()`. A bound service offers a client-server interface that allows components to interact with the service, send requests, receive results, and even do so across processes with interprocess communication (IPC). A bound service runs only as long as another application component is bound to it. Multiple components can bind to the service at once, but when all of them unbind, the service is destroyed
- **Foreground**: A foreground service performs some operation that is noticeable to the user. For example, an audio app would use a foreground service to play an audio track. Foreground services must display a Notification. Foreground services continue running even when the user isn't interacting with the app

### Declaring a `Service`

You must declare all services in your application's manifest file, just as you do for activities and other components.

To declare your service, add a `<service>` element as a child of the `<application>` element. Here is an example:

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

To create a service, you must create a subclass of `Service` or use one of its existing subclasses. In your implementation, you must override some callback methods that handle key aspects of the service lifecycle and provide a mechanism that allows the components to bind to the service, if appropriate. These are the most important callback methods that you should override:

- **`onStartCommand()`** - The system invokes this method by calling `startService()` when another component (such as an activity) requests that the service be started. When this method executes, the service is started and can run in the background indefinitely. If you implement this, it is your responsibility to stop the service when its work is complete by calling `stopSelf()` or `stopService()`. If you only want to provide binding, you don't need to implement this method
- **`onBind()`** - The system invokes this method by calling `bindService()` when another component wants to bind with the service (such as to perform RPC). In your implementation of this method, you must provide an interface that clients use to communicate with the service by returning an `IBinder`. You must always implement this method; however, if you don't want to allow binding, you should return null
- **`onCreate()`** - The system invokes this method to perform one-time setup procedures when the service is initially created (before it calls either `onStartCommand()` or `onBind()`). If the service is already running, this method is not called
- **`onDestroy()`** - The system invokes this method when the service is no longer used and is being destroyed. Your service should implement this to clean up any resources such as threads, registered listeners, or receivers. This is the last call that the service receives

If a component starts the service by calling `startService()` (which results in a call to `onStartCommand()`), the service continues to run until it stops itself with `stopSelf()` or another component stops it by calling `stopService()`.

If a component calls `bindService()` to create the service and `onStartCommand()` is not called, the service runs only as long as the component is bound to it. After the service is unbound from all of its clients, the system destroys it.

The Android system stops a service only when memory is low and it must recover system resources for the activity that has user focus. If the service is bound to an activity that has user focus, it's less likely to be killed; if the service is declared to run in the foreground, it's rarely killed.

### onStartCommand() Return Values

`onStartCommand()` requires we return an Integer as result. This integer represents how the `Service` should be handled by the OS:

- **START_NOT_STICKY** - If the system kills the service after `onStartCommand()` returns, do not recreate the service unless there are pending intents to deliver. This is the safest option to avoid running your service when not necessary and when your application can simply restart any unfinished jobs
- **START_STICKY** - If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()`, but do not redeliver the last intent. Instead, the system calls `onStartCommand()` with a null intent unless there are pending intents to start the service. In that case, those intents are delivered. This is suitable for media players (or similar services) that are not executing commands but are running indefinitely and waiting for a job
- **START_REDELIVER_INTENT** - If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()` with the last intent that was delivered to the service. Any pending intents are delivered in turn. This is suitable for services that are actively performing a job that should be immediately resumed, such as downloading a file

### `Service` `Lifecycle`

The lifecycle of a service is much simpler than that of an activity. However, it's even more important that you pay close attention to how your service is created and destroyed because a service can run in the background without the user being aware.

The service lifecycle—from when it's created to when it's destroyed—can follow either of these two paths:

- **A started service**: The service is created when another component calls `startService()`. The service then runs indefinitely and must stop itself by calling `stopSelf()`. Another component can also stop the service by calling `stopService()`. When the service is stopped, the system destroys it

- **A bound service**: The service is created when another component (a client) calls `bindService()`. The client then communicates with the service through an `IBinder` interface. The client can close the connection by calling `unbindService()`. Multiple clients can bind to the same service and when all of them unbind, the system destroys the service. The service does not need to stop itself

These two paths aren't entirely separate. You can bind to a service that is already started with `startService()`. For example, you can start a background music service by calling `startService()` with an `Intent` that identifies the music to play. Later, possibly when the user wants to exercise some control over the player or get information about the current song, an activity can bind to the service by calling `bindService()`. In cases such as this, `stopService()` or `stopSelf()` doesn't actually stop the service until all of the clients unbind.


# Question (EN)
> What's `Service`?
# Вопрос (RU)
> Что такое `Service`?

---


---


## Answer (EN)

A `Service` is an application component that can perform long-running operations in the background, and it doesn't provide a user interface. Another application component can start a service, and it continues to run in the background even if the user switches to another application. Additionally, a component can bind to a service to interact with it and even perform interprocess communication (IPC). For example, a service can handle network transactions, play music, perform file I/O, or interact with a content provider, all from the background.

By default, a service runs in the same process as the main thread of the application. If we have to implement complex logic, with longtime processing, we have to take care of creating a new thread, otherwise, the Android service runs on the main thread and it could cause ANR problem.

Services run with a higher priority than inactive or invisible activities and therefore it is less likely that the Android system terminates them. Services can also be configured to be restarted if they get terminated by the Android system once sufficient system resources are available again.

### Types of Services

These are the three different types of services: Foreground, Background, Bound.

- **Background**: A background service performs an operation that isn't directly noticed by the user. For example, if an app used a service to compact its storage, that would usually be a background service
- **Bound**: A service is bound when an application component binds to it by calling `bindService()`. A bound service offers a client-server interface that allows components to interact with the service, send requests, receive results, and even do so across processes with interprocess communication (IPC). A bound service runs only as long as another application component is bound to it. Multiple components can bind to the service at once, but when all of them unbind, the service is destroyed
- **Foreground**: A foreground service performs some operation that is noticeable to the user. For example, an audio app would use a foreground service to play an audio track. Foreground services must display a Notification. Foreground services continue running even when the user isn't interacting with the app

### Declaring a `Service`

You must declare all services in your application's manifest file, just as you do for activities and other components.

To declare your service, add a `<service>` element as a child of the `<application>` element. Here is an example:

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

To create a service, you must create a subclass of `Service` or use one of its existing subclasses. In your implementation, you must override some callback methods that handle key aspects of the service lifecycle and provide a mechanism that allows the components to bind to the service, if appropriate. These are the most important callback methods that you should override:

- **`onStartCommand()`** - The system invokes this method by calling `startService()` when another component (such as an activity) requests that the service be started. When this method executes, the service is started and can run in the background indefinitely. If you implement this, it is your responsibility to stop the service when its work is complete by calling `stopSelf()` or `stopService()`. If you only want to provide binding, you don't need to implement this method
- **`onBind()`** - The system invokes this method by calling `bindService()` when another component wants to bind with the service (such as to perform RPC). In your implementation of this method, you must provide an interface that clients use to communicate with the service by returning an `IBinder`. You must always implement this method; however, if you don't want to allow binding, you should return null
- **`onCreate()`** - The system invokes this method to perform one-time setup procedures when the service is initially created (before it calls either `onStartCommand()` or `onBind()`). If the service is already running, this method is not called
- **`onDestroy()`** - The system invokes this method when the service is no longer used and is being destroyed. Your service should implement this to clean up any resources such as threads, registered listeners, or receivers. This is the last call that the service receives

If a component starts the service by calling `startService()` (which results in a call to `onStartCommand()`), the service continues to run until it stops itself with `stopSelf()` or another component stops it by calling `stopService()`.

If a component calls `bindService()` to create the service and `onStartCommand()` is not called, the service runs only as long as the component is bound to it. After the service is unbound from all of its clients, the system destroys it.

The Android system stops a service only when memory is low and it must recover system resources for the activity that has user focus. If the service is bound to an activity that has user focus, it's less likely to be killed; if the service is declared to run in the foreground, it's rarely killed.

### onStartCommand() Return Values

`onStartCommand()` requires we return an Integer as result. This integer represents how the `Service` should be handled by the OS:

- **START_NOT_STICKY** - If the system kills the service after `onStartCommand()` returns, do not recreate the service unless there are pending intents to deliver. This is the safest option to avoid running your service when not necessary and when your application can simply restart any unfinished jobs
- **START_STICKY** - If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()`, but do not redeliver the last intent. Instead, the system calls `onStartCommand()` with a null intent unless there are pending intents to start the service. In that case, those intents are delivered. This is suitable for media players (or similar services) that are not executing commands but are running indefinitely and waiting for a job
- **START_REDELIVER_INTENT** - If the system kills the service after `onStartCommand()` returns, recreate the service and call `onStartCommand()` with the last intent that was delivered to the service. Any pending intents are delivered in turn. This is suitable for services that are actively performing a job that should be immediately resumed, such as downloading a file

### `Service` `Lifecycle`

The lifecycle of a service is much simpler than that of an activity. However, it's even more important that you pay close attention to how your service is created and destroyed because a service can run in the background without the user being aware.

The service lifecycle—from when it's created to when it's destroyed—can follow either of these two paths:

- **A started service**: The service is created when another component calls `startService()`. The service then runs indefinitely and must stop itself by calling `stopSelf()`. Another component can also stop the service by calling `stopService()`. When the service is stopped, the system destroys it

- **A bound service**: The service is created when another component (a client) calls `bindService()`. The client then communicates with the service through an `IBinder` interface. The client can close the connection by calling `unbindService()`. Multiple clients can bind to the same service and when all of them unbind, the system destroys the service. The service does not need to stop itself

These two paths aren't entirely separate. You can bind to a service that is already started with `startService()`. For example, you can start a background music service by calling `startService()` with an `Intent` that identifies the music to play. Later, possibly when the user wants to exercise some control over the player or get information about the current song, an activity can bind to the service by calling `bindService()`. In cases such as this, `stopService()` or `stopSelf()` doesn't actually stop the service until all of the clients unbind.

## Ответ (RU)

`Service` - это компонент приложения, который может выполнять длительные операции в фоновом режиме и не предоставляет пользовательский интерфейс. Другой компонент приложения может запустить сервис, и он продолжит работать в фоновом режиме, даже если пользователь переключится на другое приложение. Кроме того, компонент может привязаться к сервису для взаимодействия с ним и даже выполнения межпроцессного взаимодействия (IPC). Например, сервис может обрабатывать сетевые транзакции, воспроизводить музыку, выполнять файловый ввод-вывод или взаимодействовать с контент-провайдером, все это в фоновом режиме.

По умолчанию сервис работает в том же процессе, что и основной поток приложения. Если нам нужно реализовать сложную логику с длительной обработкой, мы должны позаботиться о создании нового потока, в противном случае сервис Android работает в основном потоке, и это может вызвать проблему ANR.

Сервисы работают с более высоким приоритетом, чем неактивные или невидимые активити, и поэтому менее вероятно, что система Android их завершит. Сервисы также могут быть настроены на перезапуск, если они были завершены системой Android, как только снова станут доступны достаточные системные ресурсы.

### Типы Сервисов

Существует три различных типа сервисов: Foreground (передний план), Background (фоновый), Bound (привязанный).

- **Background (фоновый)**: Фоновый сервис выполняет операцию, которая не замечается пользователем напрямую. Например, если приложение использует сервис для сжатия своего хранилища, это обычно будет фоновый сервис
- **Bound (привязанный)**: Сервис становится привязанным, когда компонент приложения привязывается к нему, вызывая `bindService()`. Привязанный сервис предлагает клиент-серверный интерфейс, который позволяет компонентам взаимодействовать с сервисом, отправлять запросы, получать результаты и даже делать это между процессами с помощью межпроцессного взаимодействия (IPC). Привязанный сервис работает только до тех пор, пока к нему привязан другой компонент приложения. Несколько компонентов могут привязаться к сервису одновременно, но когда все они отвязываются, сервис уничтожается
- **Foreground (передний план)**: Сервис переднего плана выполняет некоторую операцию, заметную для пользователя. Например, аудио приложение использует сервис переднего плана для воспроизведения аудиодорожки. Сервисы переднего плана должны отображать уведомление. Сервисы переднего плана продолжают работать, даже когда пользователь не взаимодействует с приложением

### Объявление Сервиса

Вы должны объявить все сервисы в файле манифеста вашего приложения, так же, как вы делаете это для активити и других компонентов.

Чтобы объявить свой сервис, добавьте элемент `<service>` как дочерний элемент элемента `<application>`. Вот пример:

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

Чтобы создать сервис, вы должны создать подкласс `Service` или использовать один из его существующих подклассов. В вашей реализации вы должны переопределить некоторые методы обратного вызова, которые обрабатывают ключевые аспекты жизненного цикла сервиса и предоставляют механизм, который позволяет компонентам привязываться к сервису, если это необходимо. Вот наиболее важные методы обратного вызова, которые вы должны переопределить:

- **`onStartCommand()`** - Система вызывает этот метод, вызывая `startService()`, когда другой компонент (например, активити) запрашивает запуск сервиса. Когда этот метод выполняется, сервис запускается и может работать в фоновом режиме бесконечно. Если вы реализуете это, вы несете ответственность за остановку сервиса, когда его работа завершена, вызвав `stopSelf()` или `stopService()`. Если вы хотите только предоставить привязку, вам не нужно реализовывать этот метод
- **`onBind()`** - Система вызывает этот метод, вызывая `bindService()`, когда другой компонент хочет привязаться к сервису (например, для выполнения RPC). В вашей реализации этого метода вы должны предоставить интерфейс, который клиенты используют для связи с сервисом, возвращая `IBinder`. Вы всегда должны реализовывать этот метод; однако, если вы не хотите разрешать привязку, вы должны вернуть null
- **`onCreate()`** - Система вызывает этот метод для выполнения одноразовых процедур настройки, когда сервис первоначально создается (до того, как он вызовет либо `onStartCommand()`, либо `onBind()`). Если сервис уже работает, этот метод не вызывается
- **`onDestroy()`** - Система вызывает этот метод, когда сервис больше не используется и уничтожается. Ваш сервис должен реализовать это для очистки любых ресурсов, таких как потоки, зарегистрированные слушатели или приемники. Это последний вызов, который получает сервис

Если компонент запускает сервис, вызывая `startService()` (что приводит к вызову `onStartCommand()`), сервис продолжает работать, пока не остановит себя с помощью `stopSelf()` или другой компонент не остановит его, вызвав `stopService()`.

Если компонент вызывает `bindService()` для создания сервиса и `onStartCommand()` не вызывается, сервис работает только до тех пор, пока компонент привязан к нему. После того, как сервис отвязан от всех своих клиентов, система его уничтожает.

Система Android останавливает сервис только тогда, когда памяти мало, и она должна восстановить системные ресурсы для активити, которая находится в фокусе пользователя. Если сервис привязан к активити, которая находится в фокусе пользователя, он с меньшей вероятностью будет убит; если сервис объявлен для запуска на переднем плане, он редко убивается.

### Возвращаемые Значения onStartCommand()

`onStartCommand()` требует, чтобы мы вернули целое число в качестве результата. Это целое число представляет, как сервис должен обрабатываться ОС:

- **START_NOT_STICKY** - Если система убивает сервис после возврата `onStartCommand()`, не пересоздавайте сервис, если нет ожидающих интентов для доставки. Это самый безопасный вариант, чтобы избежать запуска вашего сервиса, когда это не нужно, и когда ваше приложение может просто перезапустить любые незавершенные задания
- **START_STICKY** - Если система убивает сервис после возврата `onStartCommand()`, пересоздайте сервис и вызовите `onStartCommand()`, но не доставляйте повторно последний интент. Вместо этого система вызывает `onStartCommand()` с null интентом, если нет ожидающих интентов для запуска сервиса. В этом случае эти интенты доставляются. Это подходит для медиа-плееров (или аналогичных сервисов), которые не выполняют команды, но работают бесконечно и ждут задания
- **START_REDELIVER_INTENT** - Если система убивает сервис после возврата `onStartCommand()`, пересоздайте сервис и вызовите `onStartCommand()` с последним интентом, который был доставлен сервису. Любые ожидающие интенты доставляются по очереди. Это подходит для сервисов, которые активно выполняют задание, которое должно быть немедленно возобновлено, например, загрузка файла

### Жизненный Цикл Сервиса

Жизненный цикл сервиса гораздо проще, чем у активити. Однако еще более важно, чтобы вы уделяли пристальное внимание тому, как ваш сервис создается и уничтожается, потому что сервис может работать в фоновом режиме без ведома пользователя.

Жизненный цикл сервиса - от момента его создания до момента его уничтожения - может следовать одному из этих двух путей:

- **Запущенный сервис**: Сервис создается, когда другой компонент вызывает `startService()`. Затем сервис работает бесконечно и должен остановить себя, вызвав `stopSelf()`. Другой компонент также может остановить сервис, вызвав `stopService()`. Когда сервис остановлен, система его уничтожает

- **Привязанный сервис**: Сервис создается, когда другой компонент (клиент) вызывает `bindService()`. Затем клиент взаимодействует с сервисом через интерфейс `IBinder`. Клиент может закрыть соединение, вызвав `unbindService()`. Несколько клиентов могут привязаться к одному и тому же сервису, и когда все они отвязываются, система уничтожает сервис. Сервису не нужно останавливать себя

Эти два пути не являются полностью отдельными. Вы можете привязаться к сервису, который уже запущен с помощью `startService()`. Например, вы можете запустить фоновый музыкальный сервис, вызвав `startService()` с интентом, который идентифицирует музыку для воспроизведения. Позже, возможно, когда пользователь захочет осуществить некоторый контроль над плеером или получить информацию о текущей песне, активити может привязаться к сервису, вызвав `bindService()`. В таких случаях `stopService()` или `stopSelf()` фактически не останавливают сервис до тех пор, пока все клиенты не отвяжутся.

---

## References
- [Services overview](https://developer.android.com/guide/components/services)
- [Android `Service` Tutorial](https://www.vogella.com/tutorials/AndroidServices/article.html)
- [Android `Service` Tutorial](https://www.survivingwithandroid.com/android-service-tutorial-2/)


## Follow-ups

- [[q-anr-application-not-responding--android--medium]]
- [[q-how-to-start-drawing-ui-in-android--android--easy]]
- 


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
