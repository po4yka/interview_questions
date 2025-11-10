---
id: android-482
title: Context Types in Android / 2b3f4b Context 32 Android
aliases:
- Context Types in Android
- 22383f4b Context 32 Android
topic: android
subtopics:
- activity
- app-startup
- lifecycle
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity
- c-activity-lifecycle
- q-activity-lifecycle-methods--android--medium
- q-memory-leaks-definition--android--easy
- q-usecase-pattern-android--android--medium
created: 2025-10-21
updated: 2025-11-10
tags:
- android/activity
- android/app-startup
- android/lifecycle
- difficulty/medium
sources:
- "https://developer.android.com/reference/android/content/Context"

---

# Вопрос (RU)
> Какие типы `Context` существуют в Android и когда следует использовать каждый из них?

# Question (EN)
> What types of `Context` exist in Android and when should each be used?

---

## Ответ (RU)

`Context` — абстрактный класс, предоставляющий доступ к ресурсам приложения, системным сервисам и операциям уровня приложения. Каждый тип имеет свой lifecycle и область применения.

### Основные Типы

**`Application` `Context`**
- Привязан к lifecycle всего приложения
- Получение: `applicationContext` или `getApplicationContext()`
- Используется для: singleton-объектов, операций БД/сети, запуска сервисов (в рамках актуальных ограничений фона и lifecycle)
- Не подходит для: UI-элементов, требующих оконного токена (диалоги, некоторые всплывающие окна), прямого запуска `Activity` без `FLAG_ACTIVITY_NEW_TASK` (иначе исключение)

**`Activity` `Context`**
- Привязан к lifecycle `Activity`
- Получение: `this` внутри `Activity`
- Используется для: UI-операций (диалоги, layout inflation), запуска `Activity`, доступа к тематизированным ресурсам `Activity`
- Риск: memory leak при передаче в долгоживущие объекты вне lifecycle `Activity`

**`Service` `Context`**
- Привязан к lifecycle `Service`
- Получение: `this` внутри `Service`
- Используется для: выполнения служебных операций сервиса, взаимодействия с системными сервисами, запуска других сервисов/`Activity` (с учетом ограничений API и флагов)
- Не подходит для: UI-элементов, требующих `Activity`-контекста; тяжелые операции должны выполняться в отдельных потоках/корутинах

### Иерархия Классов

```kotlin
Context (abstract)
  └── ContextWrapper
        ├── Application
        ├── Service
        └── ContextThemeWrapper
              └── Activity
```

### Таблица Использования

| Операция | `Application` | `Activity` | `Service` |
|----------|-------------|----------|---------|
| Диалоги | Обычно нет (нет подходящего окна) | Да | Обычно нет |
| Запуск `Activity` | Требует флага | Да | Требует флага |
| Inflate layout | Возможен, но без темы `Activity` | С темой `Activity` | Возможен, но обычно без темы `Activity` |
| Singleton | Да | Нет | Нет |
| БД/сеть | Да, для долгоживущих задач | Допустимо, если строго в рамках lifecycle `Activity` | Да |

### Распространенные Ошибки

```kotlin
// ❌ Memory leak: Activity в статическом поле
companion object {
    lateinit var context: Context
}
fun onCreate() {
    context = this // утечка Activity
}

// ✅ Application Context для долгоживущих объектов
companion object {
    lateinit var appContext: Context
}
fun onCreate() {
    appContext = applicationContext
}

// ❌ Application Context для диалогов, требующих Activity окна
AlertDialog.Builder(applicationContext) // приведет к исключению (BadTokenException) в большинстве случаев

// ✅ Activity Context для UI
AlertDialog.Builder(this@MyActivity)
```

### Правила Выбора

1. **`Application` `Context`** — для долгоживущих объектов (Repository, WorkManager, singletons), операций, не завязанных на конкретный экран
2. **`Activity` `Context`** — для UI-компонентов и операций, завязанных на конкретную `Activity` и её lifecycle
3. **WeakReference** — если нужна ссылка на `Activity` в callback/async-операциях, и вы явно проверяете актуальность `Activity`
4. Всегда учитывать lifecycle владельца `Context` перед его сохранением и использованием

## Answer (EN)

`Context` is an abstract class providing access to application resources, system services, and application-level operations. Each type has its own lifecycle and use cases.

### Main Types

**`Application` `Context`**
- Tied to the entire application lifecycle
- Access: `applicationContext` or `getApplicationContext()`
- Use for: singletons, database/network operations, starting services (within modern background execution and lifecycle limits)
- Not suitable for: UI elements that require a window token (dialogs, some popups), directly starting an `Activity` without `FLAG_ACTIVITY_NEW_TASK` (will throw)

**`Activity` `Context`**
- Tied to `Activity` lifecycle
- Access: `this` inside an `Activity`
- Use for: UI operations (dialogs, layout inflation), starting Activities, accessing `Activity`-themed resources
- Risk: memory leaks if passed to long-lived objects beyond the `Activity` lifecycle

**`Service` `Context`**
- Tied to `Service` lifecycle
- Access: `this` inside a `Service`
- Use for: service-specific work, interacting with system services, starting other services/Activities (respecting API-level limits and flags)
- Not suitable for: UI elements that require an `Activity` context; heavy work must be moved off the main thread

### Class Hierarchy

```kotlin
Context (abstract)
  └── ContextWrapper
        ├── Application
        ├── Service
        └── ContextThemeWrapper
              └── Activity
```

### Usage Table

| Operation | `Application` | `Activity` | `Service` |
|-----------|-------------|----------|---------|
| Dialogs | Generally no (no proper window token) | Yes | Generally no |
| Start `Activity` | Needs flag | Yes | Needs flag |
| Inflate layout | Possible, but without `Activity` theme | With `Activity` theme | Possible, usually without `Activity` theme |
| Singleton | Yes | No | No |
| DB/network | Yes for long-lived tasks | Acceptable if strictly scoped to `Activity` lifecycle | Yes |

### Common Mistakes

```kotlin
// ❌ Memory leak: Activity in static field
companion object {
    lateinit var context: Context
}
fun onCreate() {
    context = this // Activity leaked
}

// ✅ Application Context for long-lived objects
companion object {
    lateinit var appContext: Context
}
fun onCreate() {
    appContext = applicationContext
}

// ❌ Application Context for dialogs that require an Activity window
AlertDialog.Builder(applicationContext) // will throw (BadTokenException) in most real cases

// ✅ Activity Context for UI
AlertDialog.Builder(this@MyActivity)
```

### Selection Rules

1. **`Application` `Context`** — for long-lived objects (Repository, WorkManager, singletons) and operations not tied to a specific screen
2. **`Activity` `Context`** — for UI components and operations bound to a specific `Activity` and its lifecycle
3. **WeakReference** — when you must hold an `Activity` reference in callbacks/async work and explicitly check if it is still valid
4. Always consider the lifecycle of the `Context` owner before storing and using a `Context`

---

## Дополнительные вопросы (RU)

- В чем разница между `ContextWrapper` и `ContextThemeWrapper`?
- Что произойдет, если попытаться заинфлейтить тематизированный layout, используя `Application` `Context`?
- Как безопасно передавать `Context` в `ViewModel` или Repository?
- Когда следует использовать `getBaseContext()` vs `getApplicationContext()`?
- Как Jetpack Compose внутренне работает с `Context`?

## Follow-ups

- How does ContextWrapper differ from ContextThemeWrapper?
- What happens if you inflate a themed layout using `Application` `Context`?
- How to safely pass `Context` to `ViewModel` or Repository?
- When should you use `getBaseContext()` vs `getApplicationContext()`?
- How does Jetpack Compose handle `Context` internally?

## Ссылки (RU)

- [[q-activity-lifecycle-methods--android--medium]]
- [[q-memory-leaks-definition--android--easy]]
- [[q-usecase-pattern-android--android--medium]]
- https://developer.android.com/reference/android/content/Context

## References

- [[q-activity-lifecycle-methods--android--medium]]
- [[q-memory-leaks-definition--android--easy]]
- [[q-usecase-pattern-android--android--medium]]
- https://developer.android.com/reference/android/content/Context

## Связанные вопросы (RU)

### Пререквизиты / Концепции

- [[c-activity]]
- [[c-activity-lifecycle]]

### Пререквизиты
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-memory-leaks-definition--android--easy]]

### Связанные
- [[q-usecase-pattern-android--android--medium]]
- Жизненный цикл `Service` и использование `Context`
- Особенности `Context` у `Fragment`

### Продвинутые темы
- Использование WeakReference и lifecycle-aware подходов при работе с `Context`
- Тестирование кода, зависящего от `Context`
- Использование `Context` в многомодульной архитектуре

## Related Questions

### Prerequisites / Concepts

- [[c-activity]]
- [[c-activity-lifecycle]]

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-memory-leaks-definition--android--easy]]

### Related
- [[q-usecase-pattern-android--android--medium]]
- `Service` lifecycle and `Context` usage
- `Fragment` `Context` considerations

### Advanced
- WeakReference and lifecycle-aware `Context` handling
- Testing code that depends on `Context`
- `Context` in multi-module architecture
