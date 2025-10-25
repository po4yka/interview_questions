---
id: 20251021-130000
title: Context Types in Android / Типы Context в Android
aliases:
- Context Types in Android
- Типы Context в Android
topic: android
subtopics:
- lifecycle
- activity
- app-startup
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-activity-lifecycle-methods--android--medium
- q-memory-leaks-definition--android--easy
- q-usecase-pattern-android--android--medium
created: 2025-10-21
updated: 2025-10-21
tags:
- android/lifecycle
- android/activity
- android/app-startup
- difficulty/medium
source: https://developer.android.com/reference/android/content/Context
source_note: Official Context documentation
---

# Вопрос (RU)
> Типы Context в Android?

# Question (EN)
> Context Types in Android?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### What is Context
- Interface to global information about application environment
- Abstract class, implementation provided by Android system
- Access to resources, classes, application-level operations

Understanding Context is critical for working with [[c-dependency-injection]] and [[c-lifecycle]].

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
