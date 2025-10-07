---
topic: android
tags:
  - android
difficulty: medium
status: draft
---

# When can the system restart a service?

## Answer

Android system can restart a service in several cases, depending on the service type and return value from `onStartCommand()`:

### 1. START_STICKY
When the service returns `START_STICKY` from `onStartCommand()`, the system will automatically restart the service if it's killed due to memory pressure. However, the Intent that was originally sent to the service will not be redelivered - `onStartCommand()` will be called with a null Intent.

**Use case**: Long-running services that don't depend on the original Intent data (e.g., music player).

### 2. START_REDELIVER_INTENT
When the service returns `START_REDELIVER_INTENT`, the system restarts the service and redelivers the last Intent that was sent to it. This ensures that the service can continue processing the exact task it was performing.

**Use case**: Services that need to complete a specific task (e.g., file download, data sync).

### 3. Foreground Services
Foreground services have the highest priority in the system. They are:
- Much less likely to be killed by the system
- Display a persistent notification to the user
- If killed, the system makes a strong effort to restart them

**Use case**: Services that require continuous user awareness (e.g., music playback, navigation, fitness tracking).

### System Restart Conditions
The system typically restarts services when:
- Memory pressure decreases after the service was killed
- The device has sufficient resources
- The service is considered important for app functionality

### Prevention of Restarts
To prevent automatic restart, use `START_NOT_STICKY` - the service won't be restarted unless there are pending Intents to deliver.

## Answer (RU)
Система Android может перезапустить сервис в нескольких случаях, особенно если это касается долгосрочных или критически важных задач, которые должны продолжаться даже если приложение было закрыто или убито системой. Использование START_STICKY позволяет системе перезапустить сервис если он был убит. Использование START_REDELIVER_INTENT также позволяет системе перезапустить сервис если он был убит но с повторной доставкой последнего Intent. Foreground сервисы имеют более высокий приоритет и менее вероятно будут убиты системой но если это произойдет система постарается их перезапустить

## Related Topics
- Service lifecycle
- onStartCommand() return values
- Foreground services
- Memory management
