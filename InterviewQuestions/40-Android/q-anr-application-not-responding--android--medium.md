---
id: 202510051234001
title: "ANR (Application Not Responding) / ANR (Приложение не отвечает)"
topic: android
status: reviewed
created: 2025-10-05
updated: 2025-10-05
difficulty: medium
topics:
  - android
subtopics:
  - strictmode-anr
  - performance-rendering
  - profiling
tags:
  - android
  - anr
  - performance
  - main-thread
  - debugging
  - difficulty/medium
language_tags:
  - en
  - ru
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20ANR.md
author: null
related:
  - "[[moc-android]]"
  - "[[q-main-thread-vs-background-thread--android--easy]]"
  - "[[q-strictmode-detection--android--medium]]"
moc:
  - "[[moc-android]]"
connections: []
---

# ANR (Application Not Responding) / ANR (Приложение не отвечает)

## English

### Definition

When the UI thread of an Android app is blocked for too long, an "Application Not Responding" (ANR) error is triggered. If the app is in the foreground, the system displays a dialog to the user. The ANR dialog gives the user the opportunity to force quit the app.

ANRs are a problem because the app's main thread, which is responsible for updating the UI, can't process user input events or draw, causing frustration to the user.

### Triggers

An ANR is triggered for your app when one of the following conditions occur:

- **Input dispatching timed out**: If your app has not responded to an input event (such as key press or screen touch) within 5 seconds
- **Executing service**: If a service declared by your app cannot finish executing `Service.onCreate()` and `Service.onStartCommand()/Service.onBind()` within a few seconds
- **Service.startForeground() not called**: If your app uses `Context.startForegroundService()` to start a new service in the foreground, but the service then does not call `startForeground()` within 5 seconds
- **Broadcast of intent**: If a `BroadcastReceiver` hasn't finished executing within a set amount of time. If the app has any activity in the foreground, this timeout is 5 seconds
- **JobScheduler interactions**: If a `JobService` does not return from `JobService.onStartJob()` or `JobService.onStopJob()` within a few seconds, or if a user-initiated job starts and your app doesn't call `JobService.setNotification()` within a few seconds after `JobService.onStartJob()` was called

### Common Causes

It's helpful to distinguish between system and app issues when determining the cause of ANRs.

**System issues** that can cause ANRs:
- Transient issues in the system server cause usually fast binder calls to be slow
- Issues with the system server and high device load cause app threads to not be scheduled

**App issues** - common patterns when diagnosing ANRs:
- The app is doing slow operations involving I/O on the main thread
- The app is doing a long calculation on the main thread
- The main thread is doing a synchronous binder call to another process, and that other process is taking a long time to return
- The main thread is blocked waiting for a synchronized block for a long operation that is happening on another thread
- The main thread is in a deadlock with another thread, either in your process or via a binder call

### Diagnosing ANRs

#### Input Dispatch Timeout

Input dispatch ANRs occur when the app's main thread doesn't respond to an input event in time. Common causes and fixes:

| Cause | What Happened | Suggested Fix |
|-------|---------------|---------------|
| Slow binder call | Main thread makes a long synchronous binder call | Move the call off the main thread or optimize the call |
| Many consecutive binder calls | Main thread makes many consecutive synchronous binder calls | Don't perform binder calls in a tight loop |
| Blocking I/O | Main thread makes blocking I/O call (database, network) | Move all blocking IO off the main thread |
| Lock contention | Main thread is blocked waiting to acquire a lock | Reduce lock contention, optimize slow code |
| Expensive frame | Rendering too much in a single frame | Do less work rendering the frame |
| Blocked by other component | A different component is blocking the main thread | Move non-UI work off the main thread |
| GPU hang | GPU hang causing rendering to be blocked | Contact hardware team to troubleshoot |

#### Broadcast Receiver Timeout

A broadcast receiver ANR occurs when a broadcast receiver doesn't handle a broadcast in time. Common causes:

| Cause | Applies to | What Happened | Suggested Fix |
|-------|-----------|---------------|---------------|
| Slow app startup | All receivers | The app took too long to do a cold start | Optimize slow app start |
| `onReceive()` not scheduled | All receivers | Receiver thread was busy | Don't perform long tasks on receiver thread |
| Slow `onReceive()` | All receivers | `onReceive()` was blocked or slow | Optimize slow receiver code |
| Async receiver tasks not scheduled | `goAsync()` receivers | Work never started on blocked thread pool | Unblock worker thread pool |
| Workers slow or blocked | `goAsync()` receivers | Blocking operation in worker thread pool | Optimize slow async receiver code |
| Forgot to call `finish()` | `goAsync()` receivers | Call to `finish()` is missing | Ensure `finish()` is always called |

#### Execute Service Timeout

An execute service ANR happens when the app's main thread doesn't start a service in time. Common causes:

| Cause | What Happened | Suggested Fix |
|-------|---------------|---------------|
| Slow app startup | The app takes too long to perform a cold start | Optimize slow app start |
| Slow service methods | `onCreate()`, `onStartCommand()`, or `onBind()` takes too long | Optimize slow code, move operations off critical path |
| Main thread blocked | Main thread blocked by another component before service starts | Move other component's work off main thread |

#### Content Provider ANR

A content provider ANR happens when a remote content provider takes longer than the timeout period to respond to a query. Common causes:

| Cause | What Happened | Suggested Fix |
|-------|---------------|---------------|
| Slow content provider query | Content provider takes too long or is blocked | Optimize content provider query |
| Slow app startup | Content provider's app takes too long to start | Optimize app startup |
| Binder thread exhaustion | All binder threads are busy | Reduce load on binder threads |

### Detection with Android Vitals

Android vitals can help you monitor and improve your app's ANR rate. It measures several ANR rates:

- **ANR rate**: The percentage of your daily active users who experienced any type of ANR
- **User-perceived ANR rate**: The percentage of your daily active users who experienced at least one user-perceived ANR (currently only "Input dispatching timed out" ANRs)
- **Multiple ANR rate**: The percentage of your daily active users who experienced at least two ANRs

### How to Avoid ANRs

General tips to avoid ANRs:

- **Keep the main thread unblocked**: Don't perform blocking or long-running operations on the app's main thread. Instead, create a worker thread and do most of the work there
- **Minimize lock contention**: Try to minimize any lock contention between the main thread and other threads
- **Minimize non-UI work on main thread**: Minimize any non-UI related work on the main thread, such as when handling broadcasts or running services. Activities must do as little as possible in key lifecycle methods like `onCreate()` and `onResume()`
- **Be careful with shared thread pools**: Don't use the same threads for potentially long-blocking operations and time-sensitive tasks
- **Keep app startup fast**: Minimize slow or blocking operations in the app's startup code
- **Use non-main threads for receivers**: Consider running broadcast receivers in a non-main thread using `Context.registerReceiver()`

### Code Example: No-Focused-Window ANR

This code can cause a no-focused-window ANR because the window is flagged as not focusable:

```kotlin
override fun onCreate(savedInstanceState: Bundle) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    // This flag prevents the window from receiving input events
    window.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
}
```

---

## Русский

### Определение

Когда UI-поток приложения Android блокируется слишком долго, возникает ошибка "Application Not Responding" (ANR - Приложение не отвечает). Если приложение находится на переднем плане, система показывает диалоговое окно пользователю. Диалог ANR дает пользователю возможность принудительно закрыть приложение.

ANR являются проблемой, потому что главный поток приложения, который отвечает за обновление UI, не может обрабатывать события ввода пользователя или отрисовывать интерфейс, что вызывает разочарование у пользователя.

### Триггеры

ANR возникает в вашем приложении при одном из следующих условий:

- **Тайм-аут диспетчеризации ввода**: Если ваше приложение не ответило на событие ввода (например, нажатие клавиши или касание экрана) в течение 5 секунд
- **Выполнение сервиса**: Если сервис, объявленный вашим приложением, не может завершить выполнение `Service.onCreate()` и `Service.onStartCommand()/Service.onBind()` в течение нескольких секунд
- **Service.startForeground() не вызван**: Если ваше приложение использует `Context.startForegroundService()` для запуска нового сервиса на переднем плане, но сервис затем не вызывает `startForeground()` в течение 5 секунд
- **Широковещательное сообщение**: Если `BroadcastReceiver` не завершил выполнение в течение установленного времени. Если приложение имеет активность на переднем плане, этот тайм-аут составляет 5 секунд
- **Взаимодействия с JobScheduler**: Если `JobService` не возвращается из `JobService.onStartJob()` или `JobService.onStopJob()` в течение нескольких секунд, или если запускается задание, инициированное пользователем, и ваше приложение не вызывает `JobService.setNotification()` в течение нескольких секунд после вызова `JobService.onStartJob()`

### Распространенные причины

Полезно различать системные и проблемы приложения при определении причины ANR.

**Системные проблемы**, которые могут вызвать ANR:
- Временные проблемы в системном сервере делают обычно быстрые binder-вызовы медленными
- Проблемы с системным сервером и высокая нагрузка на устройство приводят к тому, что потоки приложения не планируются

**Проблемы приложения** - распространенные паттерны при диагностике ANR:
- Приложение выполняет медленные операции с I/O в главном потоке
- Приложение выполняет длительные вычисления в главном потоке
- Главный поток выполняет синхронный binder-вызов к другому процессу, и этот процесс долго возвращает результат
- Главный поток заблокирован в ожидании синхронизированного блока для длительной операции, происходящей в другом потоке
- Главный поток находится в взаимной блокировке (deadlock) с другим потоком, либо в вашем процессе, либо через binder-вызов

### Диагностика ANR

#### Тайм-аут диспетчеризации ввода

ANR диспетчеризации ввода возникают, когда главный поток приложения не отвечает на событие ввода вовремя. Распространенные причины и решения:

| Причина | Что произошло | Предлагаемое решение |
|---------|---------------|----------------------|
| Медленный binder-вызов | Главный поток делает длительный синхронный binder-вызов | Переместить вызов с главного потока или оптимизировать вызов |
| Много последовательных binder-вызовов | Главный поток делает много последовательных синхронных binder-вызовов | Не выполнять binder-вызовы в цикле |
| Блокирующий I/O | Главный поток выполняет блокирующий I/O вызов (база данных, сеть) | Переместить весь блокирующий I/O с главного потока |
| Конкуренция за блокировки | Главный поток заблокирован в ожидании получения блокировки | Уменьшить конкуренцию за блокировки, оптимизировать медленный код |
| Дорогой кадр | Слишком много рендеринга в одном кадре | Делать меньше работы при рендеринге кадра |
| Блокировка другим компонентом | Другой компонент блокирует главный поток | Переместить не-UI работу с главного потока |
| Зависание GPU | Зависание GPU вызывает блокировку рендеринга | Обратиться к команде по аппаратному обеспечению |

#### Тайм-аут широковещательного приемника

ANR широковещательного приемника возникает, когда широковещательный приемник не обрабатывает сообщение вовремя. Распространенные причины:

| Причина | Применяется к | Что произошло | Предлагаемое решение |
|---------|--------------|---------------|----------------------|
| Медленный запуск приложения | Все приемники | Приложение слишком долго запускалось | Оптимизировать медленный запуск приложения |
| `onReceive()` не запланирован | Все приемники | Поток приемника был занят | Не выполнять длительные задачи в потоке приемника |
| Медленный `onReceive()` | Все приемники | `onReceive()` был заблокирован или медленный | Оптимизировать медленный код приемника |
| Асинхронные задачи приемника не запланированы | Приемники с `goAsync()` | Работа не началась в заблокированном пуле потоков | Разблокировать пул рабочих потоков |
| Работники медленные или заблокированы | Приемники с `goAsync()` | Блокирующая операция в пуле рабочих потоков | Оптимизировать медленный асинхронный код приемника |
| Забыли вызвать `finish()` | Приемники с `goAsync()` | Вызов `finish()` отсутствует | Убедиться, что `finish()` всегда вызывается |

#### Тайм-аут выполнения сервиса

ANR выполнения сервиса происходит, когда главный поток приложения не запускает сервис вовремя. Распространенные причины:

| Причина | Что произошло | Предлагаемое решение |
|---------|---------------|----------------------|
| Медленный запуск приложения | Приложение слишком долго выполняет холодный запуск | Оптимизировать медленный запуск приложения |
| Медленные методы сервиса | `onCreate()`, `onStartCommand()` или `onBind()` выполняются слишком долго | Оптимизировать медленный код, переместить операции с критического пути |
| Главный поток заблокирован | Главный поток заблокирован другим компонентом перед запуском сервиса | Переместить работу другого компонента с главного потока |

#### ANR провайдера контента

ANR провайдера контента происходит, когда удаленный провайдер контента отвечает на запрос дольше периода тайм-аута. Распространенные причины:

| Причина | Что произошло | Предлагаемое решение |
|---------|---------------|----------------------|
| Медленный запрос к провайдеру контента | Провайдер контента работает слишком долго или заблокирован | Оптимизировать запрос к провайдеру контента |
| Медленный запуск приложения | Приложение провайдера контента слишком долго запускается | Оптимизировать запуск приложения |
| Исчерпание потоков binder | Все потоки binder заняты | Уменьшить нагрузку на потоки binder |

### Обнаружение с помощью Android Vitals

Android vitals может помочь вам отслеживать и улучшать показатель ANR вашего приложения. Он измеряет несколько показателей ANR:

- **Показатель ANR**: Процент ваших ежедневных активных пользователей, которые столкнулись с любым типом ANR
- **Показатель воспринимаемых пользователем ANR**: Процент ваших ежедневных активных пользователей, которые столкнулись как минимум с одним воспринимаемым пользователем ANR (в настоящее время только ANR "Тайм-аут диспетчеризации ввода")
- **Показатель множественных ANR**: Процент ваших ежедневных активных пользователей, которые столкнулись как минимум с двумя ANR

### Как избежать ANR

Общие советы по избежанию ANR:

- **Держите главный поток разблокированным**: Не выполняйте блокирующие или длительные операции в главном потоке приложения. Вместо этого создавайте рабочий поток и выполняйте большую часть работы там
- **Минимизируйте конкуренцию за блокировки**: Старайтесь минимизировать любую конкуренцию за блокировки между главным потоком и другими потоками
- **Минимизируйте не-UI работу в главном потоке**: Минимизируйте любую работу, не связанную с UI, в главном потоке, например, при обработке широковещательных сообщений или работе сервисов. Активности должны делать как можно меньше в ключевых методах жизненного цикла, таких как `onCreate()` и `onResume()`
- **Будьте осторожны с общими пулами потоков**: Не используйте одни и те же потоки для потенциально длительных блокирующих операций и чувствительных ко времени задач
- **Держите запуск приложения быстрым**: Минимизируйте медленные или блокирующие операции в коде запуска приложения
- **Используйте не-главные потоки для приемников**: Рассмотрите возможность запуска широковещательных приемников в не-главном потоке с использованием `Context.registerReceiver()`

### Пример кода: ANR отсутствия фокусированного окна

Этот код может вызвать ANR отсутствия фокусированного окна, потому что окно помечено как не фокусируемое:

```kotlin
override fun onCreate(savedInstanceState: Bundle) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    // Этот флаг предотвращает получение окном событий ввода
    window.addFlags(WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
}
```

---

## References

- [Android Developer Docs: ANRs](https://developer.android.com/topic/performance/vitals/anr)
- [Android Developer Docs: Diagnose and fix ANRs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)
- [Android Developer Docs: Keep your app responsive](https://developer.android.com/topic/performance/anrs/keep-your-app-responsive)
- [Medium: Android - Tackling Application Not Responding (ANRs)](https://medium.com/codex/android-tackling-application-not-responding-anrs-3c91360cd023)
- [Medium: How to resolve ANR issue in the Android System](https://medium.com/make-android/how-to-resolve-anr-issue-in-the-android-system-0d2eff3205f9)
