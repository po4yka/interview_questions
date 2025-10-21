---
id: 20251021-130000
title: "Context Types in Android / Типы Context в Android"
aliases: [Context Types in Android, Типы Context в Android]
topic: android
subtopics: [lifecycle, activity, app-startup]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-memory-leaks-android--android--medium, q-usecase-pattern-android--android--medium]
created: 2025-10-21
updated: 2025-10-21
tags: [android/lifecycle, android/activity, android/app-startup, context, application-context, activity-context, difficulty/medium]
source: https://developer.android.com/reference/android/content/Context
source_note: Official Context documentation
---

# Вопрос (RU)
> Какие типы Context существуют в Android? В чём разница между Application Context и Activity Context? Когда какой использовать и какие подводные камни есть?

# Question (EN)
> What types of Context exist in Android? What's the difference between Application Context and Activity Context? When to use which and what are the pitfalls?

---

## Ответ (RU)

### Что такое Context
- Интерфейс к глобальной информации о среде приложения
- Абстрактный класс, реализация предоставляется системой Android
- Доступ к ресурсам, классам, операциям уровня приложения

### Иерархия Context
```
Context (абстрактный класс)
├── ContextWrapper
│   ├── Application
│   ├── Service
│   └── ContextThemeWrapper
│       └── Activity
└── ... другие реализации
```

### Основные типы Context

**Application Context:**
- Глобальный контекст приложения
- Живёт весь жизненный цикл приложения
- Используется для: запуск сервисов, отправка broadcast, загрузка ресурсов
- НЕ используется для: показ диалогов, запуск Activity, inflate layout

**Activity Context:**
- Контекст конкретной Activity
- Связан с жизненным циклом Activity
- Используется для: показ диалогов, запуск Activity, inflate layout, UI операции
- Может вызывать memory leaks при неправильном использовании

**Service Context:**
- Контекст сервиса
- Связан с жизненным циклом сервиса
- Используется для фоновых операций

### Возможности по типам Context

| Действие | Application | Activity | Service |
|----------|-------------|----------|---------|
| Показать Dialog | ❌ | ✅ | ❌ |
| Запустить Activity | ❌¹ | ✅ | ❌¹ |
| Inflate Layout | ❌² | ✅ | ❌² |
| Запустить Service | ✅ | ✅ | ✅ |
| Bind к Service | ✅ | ✅ | ✅ |
| Отправить Broadcast | ✅ | ✅ | ✅ |
| Загрузить ресурсы | ✅ | ✅ | ✅ |

¹ Можно, но требует создания новой задачи
² Можно, но без theme information

### Когда использовать какой Context

**Application Context:**
- Запуск сервисов и broadcast
- Доступ к ресурсам без UI
- Singleton объекты
- Database, network operations

**Activity Context:**
- UI операции (диалоги, layout inflation)
- Запуск других Activity
- ContextMenu, Toast с UI
- Операции, связанные с Activity lifecycle

### Подводные камни

**Memory Leaks:**
- Долгоживущие ссылки на Activity Context
- Static поля с Activity Context
- Асинхронные операции, удерживающие Activity Context

**Неправильный выбор:**
- Использование Activity Context для долгоживущих объектов
- Application Context для UI операций
- Context в неподходящем scope

### Лучшие практики

1. **Используйте Application Context** для долгоживущих операций
2. **Используйте Activity Context** только для UI операций
3. **Избегайте static ссылок** на Context
4. **Проверяйте lifecycle** перед использованием Context
5. **Используйте WeakReference** при необходимости долгоживущих ссылок

### Получение Context

```kotlin
// В Activity
val context = this // Activity Context

// В Fragment
val context = requireContext() // Activity Context

// В Application
val context = this // Application Context

// В Service
val context = this // Service Context

// Глобальный доступ (осторожно!)
val context = MyApplication.getInstance()
```

---

## Answer (EN)

### What is Context
- Interface to global information about application environment
- Abstract class, implementation provided by Android system
- Access to resources, classes, application-level operations

### Context Hierarchy
```
Context (abstract class)
├── ContextWrapper
│   ├── Application
│   ├── Service
│   └── ContextThemeWrapper
│       └── Activity
└── ... other implementations
```

### Main Context Types

**Application Context:**
- Global application context
- Lives for entire app lifecycle
- Used for: starting services, sending broadcasts, loading resources
- NOT used for: showing dialogs, starting Activity, inflating layout

**Activity Context:**
- Context of specific Activity
- Tied to Activity lifecycle
- Used for: showing dialogs, starting Activity, inflating layout, UI operations
- Can cause memory leaks if used incorrectly

**Service Context:**
- Service context
- Tied to service lifecycle
- Used for background operations

### Capabilities by Context Type

| Action | Application | Activity | Service |
|--------|-------------|----------|---------|
| Show Dialog | ❌ | ✅ | ❌ |
| Start Activity | ❌¹ | ✅ | ❌¹ |
| Inflate Layout | ❌² | ✅ | ❌² |
| Start Service | ✅ | ✅ | ✅ |
| Bind to Service | ✅ | ✅ | ✅ |
| Send Broadcast | ✅ | ✅ | ✅ |
| Load Resources | ✅ | ✅ | ✅ |

¹ Possible but requires creating new task
² Possible but without theme information

### When to Use Which Context

**Application Context:**
- Starting services and broadcasts
- Accessing resources without UI
- Singleton objects
- Database, network operations

**Activity Context:**
- UI operations (dialogs, layout inflation)
- Starting other Activities
- ContextMenu, Toast with UI
- Operations tied to Activity lifecycle

### Pitfalls

**Memory Leaks:**
- Long-lived references to Activity Context
- Static fields with Activity Context
- Async operations holding Activity Context

**Wrong Choice:**
- Using Activity Context for long-lived objects
- Application Context for UI operations
- Context in inappropriate scope

### Best Practices

1. **Use Application Context** for long-lived operations
2. **Use Activity Context** only for UI operations
3. **Avoid static references** to Context
4. **Check lifecycle** before using Context
5. **Use WeakReference** when long-lived references needed

### Getting Context

```kotlin
// In Activity
val context = this // Activity Context

// In Fragment
val context = requireContext() // Activity Context

// In Application
val context = this // Application Context

// In Service
val context = this // Service Context

// Global access (careful!)
val context = MyApplication.getInstance()
```

---

## Follow-ups

- How to avoid memory leaks with Context?
- What happens when using wrong Context type?
- How to properly manage Context in background threads?
- What are the differences between ContextWrapper and ContextThemeWrapper?

## References

- [Context Documentation](https://developer.android.com/reference/android/content/Context)
- [Application Context vs Activity Context](https://developer.android.com/guide/components/activities/activity-lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]]

### Related (Same Level)
- [[q-usecase-pattern-android--android--medium]]
