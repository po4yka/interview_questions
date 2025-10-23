---
id: 20251012-12271147
title: "Mvi Handle One Time Events / Обработка одноразовых событий в MVI"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-view-methods-and-their-purpose--android--medium, q-annotation-processing--android--medium, q-what-each-android-component-represents--android--easy]
created: 2025-10-15
tags: [android/architecture-mvi, android/lifecycle, architecture-mvi, lifecycle, livedata, mvi, platform/android, sharedflow, stateflow, viewmodel, difficulty/hard]
---
# Как с MVI обрабатывать события, которые не нужно хранить?

**English**: How to handle events in MVI that don't need to be stored?

## Answer (EN)
In MVI (Model-View-Intent), to handle events that don't need to be stored in State and avoid re-displaying them when the screen is recreated, you can use: 1. SingleLiveEvent - LiveData that sends an event only once and doesn't resend it to new subscribers. 2. SharedFlow with replay = 0 for events that shouldn't repeat on new subscriber. 3. EventWrapper as a workaround for StateFlow - a class that checks if an event was already handled and doesn't show it again.

## Ответ (RU)
В MVI (Model-View-Intent) для обработки событий, которые не нужно хранить в State и избежать их повторного отображения при пересоздании экрана можно использовать следующие подходы: 1. Использовать SingleLiveEvent - LiveData, которая отправляет событие только один раз и не пересылает его новым подписчикам. Пример реализации SingleLiveEvent и использования в ViewModel показаны в тексте вопроса. 2. Использовать SharedFlow с replay = 0 для событий, которые не должны повторяться при подписке новых потребителей. Пример реализации SharedFlow в ViewModel и подписки на него показаны в тексте вопроса. 3. Использовать EventWrapper как обходной путь для StateFlow - класс, который позволяет проверять было ли событие уже обработано и не показывать его повторно.



---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture
- [[q-kmm-architecture--multiplatform--hard]] - KMM architecture patterns

