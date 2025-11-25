---
id: concept-intent
title: Intent / Intent (намерение)
aliases: [Android Intent, Intent, Intent (намерение)]
kind: concept
summary: Messaging objects used to request actions from Android components
links: []
created: 2025-11-06
updated: 2025-11-06
tags: [android, concept, intent, ipc]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

An Intent is a messaging object used to request an action from another app component. Intents facilitate communication between components in several ways:

**Types of Intents**:

1. **Explicit Intents** - Specify the exact component to start
   - Used for starting components within your app
   - Example: `Intent(context, TargetActivity::class.java)`

2. **Implicit Intents** - Declare general action to perform
   - System finds appropriate component based on intent filters
   - Example: `ACTION_VIEW`, `ACTION_SEND`

**Common Uses**:
- Starting Activities
- Starting Services
- Delivering Broadcasts
- Passing data between components

**Intent Components**:
- Action - Action to perform (VIEW, SEND, EDIT)
- Data - URI of data
- Category - Additional intent category
- Extras - Key-value pairs of data
- Flags - Modify behavior

# Сводка (RU)

Intent — это объект сообщений, используемый для запроса действия от другого компонента приложения. Intents облегчают взаимодействие между компонентами несколькими способами:

**Типы Intent**:

1. **Явные (Explicit) Intent** - Указывают точный компонент для запуска
   - Используются для запуска компонентов внутри вашего приложения
   - Пример: `Intent(context, TargetActivity::class.java)`

2. **Неявные (Implicit) Intent** - Объявляют общее действие для выполнения
   - Система находит подходящий компонент на основе intent filters
   - Пример: `ACTION_VIEW`, `ACTION_SEND`

**Обычное использование**:
- Запуск Activities
- Запуск Services
- Отправка Broadcast
- Передача данных между компонентами

**Компоненты Intent**:
- Action - Действие для выполнения (VIEW, SEND, EDIT)
- Data - URI данных
- Category - Дополнительная категория intent
- Extras - Пары ключ-значение данных
- Flags - Модифицируют поведение

## Use Cases / Trade-offs

**Explicit Intents**:
- Navigation between app screens
- Starting background services
- Precise component targeting

**Implicit Intents**:
- Sharing content to other apps
- Opening web pages
- Taking photos with camera
- Sending emails

**Intent Extras**:
- `putExtra()` for primitive types and `Serializable`
- `putParcelableExtra()` for `Parcelable` objects (more efficient)
- Bundle for grouping multiple extras

**Trade-offs**:
- `Serializable` vs `Parcelable` (ease vs performance)
- Intent size limits (~1MB for IPC)
- Security considerations for implicit intents

## References

- [Intents and Intent Filters](https://developer.android.com/guide/components/intents-filters)
- [Common Intents](https://developer.android.com/guide/components/intents-common)
- [Parcelable vs Serializable](https://developer.android.com/reference/android/os/Parcelable)
