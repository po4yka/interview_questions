---
id: 20251012-12271168
title: "Presenter Notify View / Presenter уведомляет View"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-what-are-fragments-for-if-there-is-activity--android--medium, q-kapt-vs-ksp--android--medium, q-app-store-optimization--distribution--medium]
created: 2025-10-15
tags: [android/architecture-mvi, android/lifecycle, architecture-mvi, callback, lifecycle, livedata, platform/android, presenter, view, difficulty/medium]
---
# После получения результата внутри Presenter как сообщить об этом View

**English**: After getting a result inside Presenter, how to notify the View

## Answer (EN)
Through an interface: Presenter calls interface methods that View implements. Using callbacks: View provides Presenter with a callback that's invoked when data updates. Through LiveData if using MVVM: Presenter can update data that View observes.

## Ответ (RU)
Через интерфейс: Presenter вызывает методы интерфейса который реализует View С помощью callback-ов: View предоставляет Presenter-у callback который вызывается при обновлении данных Через LiveData если используется MVVM: Presenter может обновить данные которые View наблюдает


---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View
