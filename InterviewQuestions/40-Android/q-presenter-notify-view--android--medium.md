---
tags:
  - android
  - presenter
  - view
  - callback
  - livedata
  - android/architecture-mvi
  - android/lifecycle
  - easy_kotlin
  - platform/android
  - architecture-mvi
  - lifecycle
difficulty: medium
---

# После получения результата внутри Presenter как сообщить об этом View

**English**: After getting a result inside Presenter, how to notify the View

## Answer

Through an interface: Presenter calls interface methods that View implements. Using callbacks: View provides Presenter with a callback that's invoked when data updates. Through LiveData if using MVVM: Presenter can update data that View observes.

## Ответ

Через интерфейс: Presenter вызывает методы интерфейса который реализует View С помощью callback-ов: View предоставляет Presenter-у callback который вызывается при обновлении данных Через LiveData если используется MVVM: Presenter может обновить данные которые View наблюдает

