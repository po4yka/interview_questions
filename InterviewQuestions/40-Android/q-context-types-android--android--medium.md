---
id: android-482
title: Context Types in Android / Типы Context в Android
aliases:
- Context Types in Android
- Типы Context в Android
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
status: reviewed
moc: moc-android
related:
- c-lifecycle
- c-activity
- c-activity-lifecycle
- q-activity-lifecycle-methods--android--medium
- q-memory-leaks-definition--android--easy
- q-usecase-pattern-android--android--medium
created: 2025-10-21
updated: 2025-10-30
tags:
- android/activity
- android/app-startup
- android/lifecycle
- difficulty/medium
sources:
- https://developer.android.com/reference/android/content/Context
---

# Вопрос (RU)
> Какие типы `Context` существуют в Android и когда каждый из них использовать?

# Question (EN)
> What types of `Context` exist in Android and when should each be used?

---

## Ответ (RU)

`Context` — абстрактный класс, предоставляющий доступ к ресурсам приложения, системным сервисам и операциям уровня приложения. Каждый тип имеет свой lifecycle и область применения.

### Основные Типы

**`Application` `Context`**
- Привязан к lifecycle всего приложения
- Получение: `applicationContext` или `getApplicationContext()`
- Используется для: singleton-объектов, операций БД/сети, запуска сервисов
- Не может: создавать диалоги, запускать `Activity` без `FLAG_ACTIVITY_NEW_TASK`

**`Activity` `Context`**
- Привязан к lifecycle `Activity`
- Получение: `this` внутри `Activity`
- Используется для: UI-операций (диалоги, layout inflation), запуска `Activity`, тем оформления
- Риск: memory leak при передаче в долгоживущие объекты

**`Service` `Context`**
- Привязан к lifecycle `Service`
- Получение: `this` внутри `Service`
- Используется для: фоновых операций, запуска других сервисов

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
| Диалоги | Нет | Да | Нет |
| Запуск `Activity` | Требует флага | Да | Требует флага |
| Inflate layout | Без темы | С темой | Без темы |
| Singleton | Да | Нет | Нет |
| БД/сеть | Да | Избегать | Да |

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

// ❌ Application Context для диалогов
AlertDialog.Builder(applicationContext) // crash

// ✅ Activity Context для UI
AlertDialog.Builder(this@MyActivity)
```

### Правила Выбора

1. **`Application` `Context`** — для долгоживущих объектов (`Repository`, WorkManager, singleton)
2. **`Activity` `Context`** — строго для UI-компонентов с коротким lifecycle
3. **WeakReference** — если нужна `Activity`-ссылка в callback/async операциях
4. Проверять lifecycle перед использованием `Context`

## Answer (EN)

`Context` is an abstract class providing access to application resources, system services, and application-level operations. Each type has its own lifecycle and use cases.

### Main Types

**`Application` `Context`**
- Tied to entire application lifecycle
- Access: `applicationContext` or `getApplicationContext()`
- Use for: singletons, database/network operations, starting services
- Cannot: create dialogs, start `Activity` without `FLAG_ACTIVITY_NEW_TASK`

**`Activity` `Context`**
- Tied to `Activity` lifecycle
- Access: `this` inside `Activity`
- Use for: UI operations (dialogs, layout inflation), starting Activities, themed resources
- Risk: memory leak if passed to long-lived objects

**`Service` `Context`**
- Tied to `Service` lifecycle
- Access: `this` inside `Service`
- Use for: background operations, starting other services

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
| Dialogs | No | Yes | No |
| Start `Activity` | Needs flag | Yes | Needs flag |
| Inflate layout | No theme | With theme | No theme |
| Singleton | Yes | No | No |
| DB/network | Yes | Avoid | Yes |

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

// ❌ Application Context for dialogs
AlertDialog.Builder(applicationContext) // crash

// ✅ Activity Context for UI
AlertDialog.Builder(this@MyActivity)
```

### Selection Rules

1. **`Application` `Context`** — for long-lived objects (`Repository`, WorkManager, singletons)
2. **`Activity` `Context`** — strictly for UI components with short lifecycle
3. **WeakReference** — if `Activity` reference needed in callbacks/async operations
4. Check lifecycle before using `Context`

---

## Follow-ups

- How does ContextWrapper differ from ContextThemeWrapper?
- What happens if you inflate a themed layout using `Application` `Context`?
- How to safely pass `Context` to `ViewModel` or `Repository`?
- When should you use `getBaseContext()` vs `getApplicationContext()`?
- How does Jetpack Compose handle `Context` internally?

## References

- [[q-activity-lifecycle-methods--android--medium]]
- [[q-memory-leaks-definition--android--easy]]
- [[q-usecase-pattern-android--android--medium]]
- https://developer.android.com/reference/android/content/`Context`

## Related Questions

### Prerequisites / Concepts

- [[c-lifecycle]]
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
