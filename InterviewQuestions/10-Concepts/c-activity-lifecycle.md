---\
id: "20251030-143000"
title: "Activity Lifecycle / Жизненный цикл Activity"
aliases: ["Activity Lifecycle", "Lifecycle Activity", "Жизненный цикл Activity"]
summary: "Android Activity lifecycle states and transitions"
topic: "android"
subtopics: ["activity", "android-components", "lifecycle"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: ["c-lifecycle", "c-fragment-lifecycle", "c-viewmodel", "c-savedinstancestate", "c-activity"]
created: "2025-10-30"
updated: "2025-10-30"
tags: ["activity", "android", "android-components", "concept", "lifecycle", "difficulty/medium"]
---\

# Summary (EN)

The `Activity` `Lifecycle` defines the states an Android `Activity` goes through from creation to destruction. Android provides callback methods that are invoked as the activity transitions between six key states: **Created**, **Started**, **Resumed** (Active), **Paused**, **Stopped**, and **Destroyed**. Understanding these transitions is critical for proper resource management, state preservation, and user experience.

# Сводка (RU)

Жизненный цикл `Activity` определяет состояния, через которые проходит Android `Activity` от создания до уничтожения. Android предоставляет методы обратного вызова, которые вызываются при переходе activity между шестью ключевыми состояниями: **Created** (Создано), **Started** (Запущено), **Resumed** (Активно), **Paused** (Приостановлено), **Stopped** (Остановлено) и **Destroyed** (Уничтожено). Понимание этих переходов критически важно для правильного управления ресурсами, сохранения состояния и пользовательского опыта.

---

## Lifecycle States and Methods (EN)

### 1. Created State
**`onCreate(savedInstanceState: Bundle?)`**
- First callback invoked when `Activity` is created
- Initialize essential components (ViewBinding, `ViewModel`, etc.)
- `Set` content view with `setContentView()`
- Restore saved state from `savedInstanceState` if available
- **Do not perform heavy operations here** (they block UI thread)

### 2. Started State
**`onStart()`**
- `Activity` becomes visible to user (but not yet interactive)
- Start UI-related animations or observers
- Register broadcast receivers that only need to work while visible

### 3. Resumed State (Active)
**`onResume()`**
- `Activity` is in foreground and user can interact with it
- Resume paused operations (camera, sensors, animations)
- Start active data updates or location tracking
- **`Activity` is fully interactive here**

### 4. Paused State
**`onPause()`**
- Another `Activity` comes to foreground (dialog, multi-window mode)
- `Activity` is partially visible but loses focus
- **Pause heavy operations** (camera, sensors, GPS)
- Save critical user data (do not rely on `onStop()` being called)
- **Keep this method fast** (system may kill process if it takes too long)

### 5. Stopped State
**`onStop()`**
- `Activity` is no longer visible (another `Activity` fully covers it)
- Release resources that are not needed when not visible
- Unregister broadcast receivers registered in `onStart()`
- Save user progress or application state

### 6. Destroyed State
**`onDestroy()`**
- Final cleanup before `Activity` is destroyed
- Release all remaining resources, cancel background tasks
- Called when:
  - User finishes `Activity` (`finish()` or back button)
  - Configuration change (rotation, language change)
  - System destroys `Activity` to reclaim memory

**`onRestart()`** - called when `Activity` is restarted after being stopped (before `onStart()`).

---

## Состояния Жизненного Цикла И Методы (RU)

### 1. Состояние Created
**`onCreate(savedInstanceState: Bundle?)`**
- Первый вызываемый метод при создании `Activity`
- Инициализация основных компонентов (ViewBinding, `ViewModel` и т.д.)
- Установка разметки через `setContentView()`
- Восстановление сохраненного состояния из `savedInstanceState` при наличии
- **Не выполняйте тяжелые операции здесь** (они блокируют UI-поток)

### 2. Состояние Started
**`onStart()`**
- `Activity` становится видимой пользователю (но еще неинтерактивной)
- Запуск UI-анимаций и observers
- Регистрация broadcast receivers, которые нужны только пока `Activity` видна

### 3. Состояние Resumed (Активное)
**`onResume()`**
- `Activity` на переднем плане и пользователь может взаимодействовать с ней
- Возобновление приостановленных операций (камера, сенсоры, анимации)
- Запуск активных обновлений данных или отслеживания местоположения
- **`Activity` полностью интерактивна здесь**

### 4. Состояние Paused
**`onPause()`**
- Другая `Activity` выходит на передний план (диалог, многооконный режим)
- `Activity` частично видна, но теряет фокус
- **Приостановка тяжелых операций** (камера, сенсоры, GPS)
- Сохранение критически важных данных (не полагайтесь на вызов `onStop()`)
- **Метод должен быть быстрым** (система может убить процесс при долгом выполнении)

### 5. Состояние Stopped
**`onStop()`**
- `Activity` больше не видна (другая `Activity` полностью закрывает её)
- Освобождение ресурсов, не нужных когда `Activity` невидима
- Отмена регистрации broadcast receivers из `onStart()`
- Сохранение прогресса пользователя или состояния приложения

### 6. Состояние Destroyed
**`onDestroy()`**
- Финальная очистка перед уничтожением `Activity`
- Освобождение всех оставшихся ресурсов, отмена фоновых задач
- Вызывается когда:
  - Пользователь закрывает `Activity` (`finish()` или кнопка назад)
  - Изменение конфигурации (поворот экрана, смена языка)
  - Система уничтожает `Activity` для освобождения памяти

**`onRestart()`** - вызывается при перезапуске `Activity` после остановки (перед `onStart()`).

---

## State Transitions and Best Practices

### Normal Flow
```
onCreate() → onStart() → onResume() → [RUNNING] → onPause() → onStop() → onDestroy()
```

### Configuration Changes
```
onPause() → onStop() → onDestroy() → onCreate() → onStart() → onResume()
```
Use `ViewModel` to survive configuration changes without data loss.

### Process Death Recovery
When system kills the process to reclaim memory:
```
System saves state → Process killed → User returns → onCreate(savedInstanceState) with saved state
```
Always save UI state in `onSaveInstanceState()`.

### Best Practices (EN)
- **onCreate()**: Initialize `ViewModel`, ViewBinding, setup UI structure
- **onStart()**: Start observers, register receivers needed while visible
- **onResume()**: Resume sensors, camera, active updates
- **onPause()**: Pause expensive operations immediately, save critical data
- **onStop()**: Release resources, save user progress
- **onDestroy()**: Cancel coroutines, release all resources
- **Use `Lifecycle`-aware components** (`ViewModel`, `LiveData`, `Lifecycle` observers)
- **Avoid memory leaks**: do not reference `Activity` in long-lived objects

### Лучшие Практики (RU)
- **onCreate()**: Инициализация `ViewModel`, ViewBinding, настройка структуры UI
- **onStart()**: Запуск observers, регистрация receivers нужных пока видна
- **onResume()**: Возобновление сенсоров, камеры, активных обновлений
- **onPause()**: Немедленная приостановка дорогих операций, сохранение критичных данных
- **onStop()**: Освобождение ресурсов, сохранение прогресса пользователя
- **onDestroy()**: Отмена coroutines, освобождение всех ресурсов
- **Используйте `Lifecycle`-aware компоненты** (`ViewModel`, `LiveData`, `Lifecycle` observers)
- **Избегайте утечек памяти**: не храните ссылки на `Activity` в долгоживущих объектах

---

## Use Cases / Trade-offs

**When to use lifecycle methods**:
- Resource management (camera, sensors, network connections)
- State preservation (form data, scroll position, user progress)
- Background task coordination (pause downloads, stop polling)
- `Observer` registration/unregistration (`LiveData`, `Flow`, broadcasts)

**Common pitfalls**:
- Heavy work in `onCreate()` delays `Activity` appearance
- Not saving state leads to data loss on configuration changes
- Slow `onPause()` can cause ANR (`Application` Not Responding)
- Memory leaks from holding `Activity` references in static or long-lived objects
- Assuming `onDestroy()` will always be called (system may kill process without calling it)

---

## References

- [Android `Activity` `Lifecycle` - Official Documentation](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Handling Lifecycles with `Lifecycle`-Aware Components](https://developer.android.com/topic/libraries/architecture/lifecycle)
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
- [[moc-android]]
