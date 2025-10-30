---
id: 20251012-122715
title: "How Application Priority Is Determined By The System / Как система определяет приоритет приложения"
aliases: ["How Application Priority Is Determined", "Как система определяет приоритет приложения"]
topic: android
subtopics: [lifecycle, processes, performance-memory]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-anr-application-not-responding--android--medium, q-what-unites-the-main-components-of-an-android-application--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, difficulty/hard, android/lifecycle, android/processes, android/performance-memory, lifecycle, processes, performance-memory]
date created: Monday, October 27th 2025, 3:35:47 pm
date modified: Thursday, October 30th 2025, 12:48:08 pm
---

# Вопрос (RU)

> Как система определяет приоритет приложения?

# Question (EN)

> How application priority is determined by the system?

---

## Ответ (RU)

Android классифицирует процессы по **иерархии важности**, что влияет на решения **Low Memory Killer (LMK)** о завершении процессов и распределение ресурсов CPU.

### Иерархия Приоритетов

От высшего к низшему:

1. **Foreground Process** - пользователь активно взаимодействует
2. **Visible Process** - процесс частично виден пользователю
3. **Service Process** - выполняет фоновую задачу
4. **Cached Process** - остановлен, но кешируется для быстрого перезапуска
5. **Empty Process** - без активных компонентов, убивается первым

### Критерии Определения

**Foreground (oom_adj = 0):**
- Activity в состоянии resumed (onResume)
- Foreground Service с уведомлением
- BroadcastReceiver выполняет onReceive()

**Visible (oom_adj = 100-200):**
- Activity в состоянии paused, но видима (диалог поверх)
- Service привязан к visible Activity

**Service (oom_adj = 300-400):**
- Service запущен через startService()
- Выполняет длительную операцию

**Cached (oom_adj = 900-999):**
- Activity в состоянии stopped (onStop)
- Нет активных компонентов
- Убивается первым при нехватке памяти (LRU порядок)

### Проверка Приоритета

```kotlin
class PriorityChecker(private val context: Context) {
    fun logCurrentPriority() {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val processes = am.runningAppProcesses ?: return

        val myPid = android.os.Process.myPid()
        val myProcess = processes.find { it.pid == myPid } ?: return

        val level = when (myProcess.importance) {
            IMPORTANCE_FOREGROUND -> "FOREGROUND (0)" // ✅ Highest priority
            IMPORTANCE_VISIBLE -> "VISIBLE (100-200)"
            IMPORTANCE_SERVICE -> "SERVICE (300-400)"
            IMPORTANCE_CACHED -> "CACHED (900-999)" // ❌ First to be killed
            else -> "UNKNOWN"
        }
        Log.d("Priority", "Current: $level")
    }
}
```

### Факторы Влияния

1. **Состояние компонентов** - resumed Activity повышает до Foreground
2. **Тип Service** - foreground Service (startForeground) получает приоритет Foreground
3. **Bound Services** - наследуют приоритет Activity, к которой привязаны
4. **Зависимости процессов** - если процесс A зависит от B, B получает приоритет A

### Low Memory Killer

LMK убивает процессы начиная с наибольшего oom_adj:
1. Empty (1000) → немедленно
2. Cached (900-999) → LRU порядок
3. Service (300-400) → при нехватке памяти
4. Visible/Foreground → в крайнем случае

## Answer (EN)

Android classifies processes by **importance hierarchy**, affecting **Low Memory Killer (LMK)** decisions and CPU/resource allocation.

### Priority Hierarchy

From highest to lowest:

1. **Foreground Process** - user actively interacting
2. **Visible Process** - partially visible to user
3. **Service Process** - performing background task
4. **Cached Process** - stopped but cached for quick restart
5. **Empty Process** - no active components, killed first

### Determination Criteria

**Foreground (oom_adj = 0):**
- Activity in resumed state (onResume)
- Foreground Service with notification
- BroadcastReceiver executing onReceive()

**Visible (oom_adj = 100-200):**
- Activity in paused state but visible (dialog on top)
- Service bound to visible Activity

**Service (oom_adj = 300-400):**
- Service started via startService()
- Performing long-running operation

**Cached (oom_adj = 900-999):**
- Activity in stopped state (onStop)
- No active components
- Killed first during low memory (LRU order)

### Checking Priority

```kotlin
class PriorityChecker(private val context: Context) {
    fun logCurrentPriority() {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val processes = am.runningAppProcesses ?: return

        val myPid = android.os.Process.myPid()
        val myProcess = processes.find { it.pid == myPid } ?: return

        val level = when (myProcess.importance) {
            IMPORTANCE_FOREGROUND -> "FOREGROUND (0)" // ✅ Highest priority
            IMPORTANCE_VISIBLE -> "VISIBLE (100-200)"
            IMPORTANCE_SERVICE -> "SERVICE (300-400)"
            IMPORTANCE_CACHED -> "CACHED (900-999)" // ❌ First to be killed
            else -> "UNKNOWN"
        }
        Log.d("Priority", "Current: $level")
    }
}
```

### Influencing Factors

1. **Component state** - resumed Activity elevates to Foreground
2. **Service type** - foreground Service (startForeground) gets Foreground priority
3. **Bound Services** - inherit priority of bound Activity
4. **Process dependencies** - if process A depends on B, B inherits A's priority

### Low Memory Killer

LMK kills processes starting with highest oom_adj:
1. Empty (1000) → immediately
2. Cached (900-999) → LRU order
3. Service (300-400) → when memory low
4. Visible/Foreground → last resort

---

## Follow-ups

- How does the oom_adj score dynamically change during Activity lifecycle transitions?
- What are the trade-offs between using foreground Services versus WorkManager for background tasks?
- How can bound Services affect the priority of processes across different applications?

## References

- https://developer.android.com/guide/components/activities/process-lifecycle - Process lifecycle
- https://developer.android.com/guide/components/services - Services and process priority

## Related Questions

### Prerequisites (Easier)
- [[q-anr-application-not-responding--android--medium]] - ANR fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Android components

### Related (Hard)
- q-android-memory-management--android--hard - Memory management strategies
- q-background-execution-limits--android--hard - Background execution restrictions

### Advanced (Hard)
- q-process-death-handling--android--hard - Handling process death
