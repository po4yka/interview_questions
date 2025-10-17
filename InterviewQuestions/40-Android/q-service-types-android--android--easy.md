---
id: 20251012-122711101
title: "Service Types Android / Типы Service в Android"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: [services, background-tasks, difficulty/easy]
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

---

## Related Questions

### Related (Easy)
- [[q-android-service-types--android--easy]] - Service

### Advanced (Harder)
- [[q-service-component--android--medium]] - Service
- [[q-foreground-service-types--background--medium]] - Service
- [[q-when-can-the-system-restart-a-service--android--medium]] - Service
