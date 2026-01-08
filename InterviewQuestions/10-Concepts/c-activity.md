---\
id: "20251030-122942"
title: "Activity / Activity"
aliases: ["Activity", "Android Activity", "Активити"]
summary: "Fundamental Android component representing a single screen with UI"
topic: "android"
subtopics: ["activity", "android-components", "ui"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-30"
updated: "2025-10-30"
tags: ["activity", "android", "android-components", "concept", "ui", "difficulty/medium"]
---\

# Summary (EN)

**`Activity`** is one of the four fundamental Android application components. It represents a single screen with a user interface and serves as an entry point for user interaction. Each `Activity` is an independent component that the system can start individually, and it provides a window in which the app draws its UI.

Activities follow a well-defined lifecycle managed by the Android system, responding to state changes such as configuration changes, system memory pressure, and user navigation. Modern Android development often favors a Single `Activity` architecture with Fragments for screen navigation, though Activities remain essential for app entry points and system integration.

# Сводка (RU)

**`Activity`** - один из четырех фундаментальных компонентов приложения Android. Представляет собой отдельный экран с пользовательским интерфейсом и служит точкой входа для взаимодействия пользователя. Каждая `Activity` - независимый компонент, который система может запускать индивидуально, предоставляя окно для отрисовки UI приложения.

`Activity` следуют четко определенному жизненному циклу, управляемому системой Android, реагируя на изменения состояния, такие как изменения конфигурации, нехватка памяти и навигация пользователя. Современная разработка Android часто предпочитает архитектуру Single `Activity` с Fragments для навигации между экранами, хотя `Activity` остаются необходимыми для точек входа в приложение и системной интеграции.

---

## Core Concept (EN)

`Activity` provides:
- **Entry Point**: System launches app by starting an `Activity` via `Intent`
- **Screen Hosting**: Container for UI elements (Views, Fragments, Compose)
- **`Lifecycle` Management**: Callback methods for state transitions
- **Configuration Handling**: Responds to device changes (rotation, locale, dark mode)
- **System Integration**: Handles permissions, results, window insets, system UI

## Основная Концепция (RU)

`Activity` обеспечивает:
- **Точка входа**: Система запускает приложение через `Activity` посредством `Intent`
- **Хостинг экрана**: Контейнер для UI элементов (Views, Fragments, Compose)
- **Управление жизненным циклом**: Callback методы для переходов состояний
- **Обработка конфигурации**: Реагирует на изменения устройства (поворот, локаль, темная тема)
- **Системная интеграция**: Обрабатывает разрешения, результаты, window insets, system UI

---

## Lifecycle States (EN)

```
Created → Started → Resumed (Active)
    ↓         ↓         ↓
Stopped ← Paused ← Resumed
    ↓
Destroyed
```

**Key States**:
- **Created**: Instance created, `onCreate()` called
- **Started**: Visible but not interactive, `onStart()` called
- **Resumed**: Visible and interactive (foreground), `onResume()` called
- **Paused**: Partially obscured, `onPause()` called
- **Stopped**: Not visible, `onStop()` called
- **Destroyed**: Removed from memory, `onDestroy()` called

## Состояния Жизненного Цикла (RU)

**Ключевые состояния**:
- **Created**: Экземпляр создан, вызван `onCreate()`
- **Started**: Видима, но не интерактивна, вызван `onStart()`
- **Resumed**: Видима и интерактивна (foreground), вызван `onResume()`
- **Paused**: Частично скрыта, вызван `onPause()`
- **Stopped**: Не видима, вызван `onStop()`
- **Destroyed**: Удалена из памяти, вызван `onDestroy()`

---

## Code Example (EN/RU)

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // Initialize UI, ViewModel, restore state
        // Инициализация UI, ViewModel, восстановление состояния
    }

    override fun onStart() {
        super.onStart()
        // Activity visible, start animations, register listeners
        // Activity видима, запуск анимаций, регистрация слушателей
    }

    override fun onResume() {
        super.onResume()
        // Activity in foreground, acquire camera, start sensors
        // Activity на переднем плане, захват камеры, запуск сенсоров
    }

    override fun onPause() {
        super.onPause()
        // Losing focus, release exclusive resources (camera)
        // Потеря фокуса, освобождение эксклюзивных ресурсов (камера)
    }

    override fun onStop() {
        super.onStop()
        // No longer visible, save data, unregister listeners
        // Больше не видима, сохранение данных, отмена регистрации слушателей
    }

    override fun onDestroy() {
        super.onDestroy()
        // Cleanup, cancel background tasks
        // Очистка, отмена фоновых задач
        super.onDestroy()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save transient UI state (scroll position, selections)
        // Сохранение временного состояния UI (позиция скролла, выбор)
    }
}
```

---

## Modern Architecture (EN)

**Single `Activity` + Fragments/Navigation**:
- One `Activity` hosts multiple Fragments
- Navigation `Component` handles screen transitions
- Reduces boilerplate, simplifies deep linking
- Better for Compose (single `ComponentActivity`)

**Multiple Activities**:
- Separate task stacks
- System-level back navigation
- Better for modular features, different apps
- Required for launcher entries, widgets, shortcuts

## Современная Архитектура (RU)

**Single `Activity` + Fragments/Navigation**:
- Одна `Activity` хостит множество Fragments
- Navigation `Component` управляет переходами между экранами
- Сокращает boilerplate код, упрощает deep linking
- Лучше для Compose (одна `ComponentActivity`)

**Multiple Activities**:
- Раздельные стеки задач
- Системная навигация назад
- Лучше для модульных фич, разных приложений
- Требуется для launcher entries, виджетов, shortcuts

---

## Use Cases / Trade-offs

**When to use**:
- App entry point (launcher `Activity`)
- Different task contexts (email compose, camera)
- System integration (share target, app shortcuts)
- Permission handling, configuration changes

**Alternatives**:
- **Fragments**: Modular UI components within `Activity`
- **Compose Navigation**: Declarative navigation for Compose UI
- **ViewModels**: Survive configuration changes

**Trade-offs**:
- Multiple Activities = complex navigation, harder state sharing
- Single `Activity` = simpler navigation, easier state management
- Configuration changes = potential data loss without proper handling

---

## References

- [Android `Activity` Documentation](https://developer.android.com/guide/components/activities/intro-activities)
- [Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- [Single `Activity` Architecture](https://developer.android.com/guide/navigation/navigation-principles)
- [[c-fragment]] - Related UI component concept
- [[c-viewmodel]] - `Lifecycle`-aware state management
- [[moc-android]] - Android concepts map
