---
topic: android
tags:
  - android
  - services
  - background-tasks
difficulty: easy
status: draft
---

# Какие есть виды сервисов?

**English**: What types of services exist in Android?

## Answer (EN)
В Android существуют следующие основные виды сервисов:

### 1. Foreground Service

Выполняет операции, видимые пользователю (например, воспроизведение музыки). Должен отображать постоянное уведомление.

### 2. Background Service

Выполняет операции, не видимые пользователю напрямую (синхронизация данных, загрузка файлов).

**Важно**: С Android 8.0 (API 26) есть ограничения на background services. Рекомендуется использовать WorkManager.

### 3. Bound Service

Позволяет компонентам приложения (Activity, другие Services) привязываться к нему и взаимодействовать через интерфейс.

### 4. IntentService (deprecated)

Упрощённый вариант Service для последовательного выполнения задач в рабочем потоке.

**Примечание**: Устарел с API 30. Рекомендуется использовать WorkManager или JobIntentService.

**English**: Android service types: **Foreground Service** (user-visible operations with notification), **Background Service** (non-visible operations, restricted since Android 8.0), **Bound Service** (allows component binding and interaction), and **IntentService** (deprecated, use WorkManager instead).
