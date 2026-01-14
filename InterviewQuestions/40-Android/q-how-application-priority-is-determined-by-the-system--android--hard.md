---
id: android-124
title: How Application Priority Is Determined By The System / Как система определяет
  приоритет приложения
aliases:
- How Application Priority Is Determined
- Как система определяет приоритет приложения
topic: android
subtopics:
- lifecycle
- performance-memory
- processes
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-lifecycle
- c-memory-management
- q-anr-application-not-responding--android--medium
- q-raise-process-priority--android--medium
- q-what-unites-the-main-components-of-an-android-application--android--medium
- q-when-can-the-system-restart-a-service--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
anki_cards:
- slug: android-124-0-en
  language: en
  anki_id: 1768367580805
  synced_at: '2026-01-14T09:17:53.015254'
- slug: android-124-0-ru
  language: ru
  anki_id: 1768367580830
  synced_at: '2026-01-14T09:17:53.017826'
tags:
- android
- android/lifecycle
- android/performance-memory
- android/processes
- difficulty/hard
- lifecycle
- performance-memory
- processes
---
# Вопрос (RU)

> Как система определяет приоритет приложения?

# Question (EN)

> How application priority is determined by the system?

---

## Ответ (RU)

Android определяет приоритет процессов по **иерархии важности**, основанной на состоянии компонентов приложения и их видимости/значимости для пользователя. Эта иерархия влияет на решения системы (ActivityManager + lmkd/LMK) о завершении процессов при нехватке памяти и на распределение ресурсов.

Важно: конкретные значения `oom_adj` и внутренние пороги являются деталями реализации и могут отличаться между версиями Android. Корректнее мыслить категориями важности (importance), а не полагаться на фиксированные числовые диапазоны.

### Иерархия Приоритетов (концептуально)

От высшего к низшему:

1. **Foreground process** — пользователь активно взаимодействует или выполняется критичный для пользователя код
2. **Visible process** — что-то из UI видно пользователю
3. **Perceptible / `Service` process** — важная фоновая работа, ощутимая пользователю (например, музыка, активный вызов)
4. **Cached process** — содержит остановленные компоненты, хранится для быстрого перезапуска
5. **Empty process** — без активных компонентов, служит в основном для кеша, высвобождается первым при нехватке памяти

### Критерии Определения (упрощенно)

Ниже описаны типичные случаи. Точные флаги/значения зависят от версии Android и внутренних алгоритмов.

**Foreground**:
- `Activity` в состоянии resumed (в фокусе)
- Foreground service через `startForeground()` с обязательным уведомлением
- Выполнение `BroadcastReceiver.onReceive()` или `ContentProvider` в процессе, связанное с актуальным пользовательским действием

**Visible**:
- `Activity` в состоянии paused, но её UI всё ещё частично видим (например, диалог поверх)
- Компоненты (например, bound service), связанные с видимой `Activity`

**Perceptible / `Service`**:
- Сервис, который играет музыку, обрабатывает активный вызов, трекинг, и т.п., когда это явно разрешено политиками фонового выполнения
- Bound service, к которому привязаны foreground/visible компоненты, может поднимать приоритет процесса, в котором он работает

**Cached**:
- `Activity` в состоянии stopped (не видно пользователю), но процесс всё ещё содержит её состояние или другие неактивные компоненты
- Нет активных foreground/visible/perceptible компонентов
- Такие процессы хранятся по LRU и завершаются при нехватке памяти

**Empty**:
- Процесс без активных компонентов и без полезного кешируемого состояния
- Может быть завершён одним из первых при необходимости освобождения памяти; не обязательно "немедленно", но имеет наименьший приоритет

### Проверка Приоритета

Для диагностики можно посмотреть важность текущего процесса через `ActivityManager.RunningAppProcessInfo.importance`.

```kotlin
class PriorityChecker(private val context: Context) {
    fun logCurrentPriority() {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val processes = am.runningAppProcesses ?: return

        val myPid = android.os.Process.myPid()
        val myProcess = processes.find { it.pid == myPid } ?: return

        val level = when (myProcess.importance) {
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND -> "FOREGROUND"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_VISIBLE -> "VISIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_SERVICE -> "SERVICE / PERCEPTIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_PERCEPTIBLE -> "PERCEPTIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_CACHED -> "CACHED"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_EMPTY -> "EMPTY"
            else -> "OTHER (${myProcess.importance})"
        }
        Log.d("Priority", "Current importance: $level")
    }
}
```

Замечания:
- Набор значений `importance` и их семантика могут отличаться между версиями Android.
- `runningAppProcesses` и эти значения не гарантируются как точный источник для продакшен-логики; используйте их преимущественно для отладки и понимания.

### Факторы Влияния

1. **Состояние компонентов** — resumed `Activity` делает процесс foreground.
2. **Тип сервиса** — foreground service (`startForeground()`) поднимает процесс до foreground-приоритета; обычные фоновые сервисы на современных версиях сильно ограничены и часто переводятся в более низкий приоритет или вовсе запрещаются.
3. **Bound services** — сервис, к которому привязан foreground/visible компонент, получает более высокий приоритет.
4. **Зависимости процессов** — если процесс A напрямую зависит от процесса B (например, binder-связь с критичным сервисом), система может повысить приоритет B ближе к A, чтобы избежать kill критичного зависимого.

### Low Memory Killer / Lmkd

Под давлением памяти система (через `ActivityManager` и `lmkd`/LMK) завершает процессы, начиная с наименее важных:

1. Empty / низкоприоритетные кешированные процессы
2. Cached процессы в порядке LRU
3. `Service` / perceptible процессы — только при серьёзной нехватке памяти
4. Visible / Foreground процессы — только в крайнем случае, если ресурсы полностью исчерпаны

Критерий — не только категория, но и объём потребляемой памяти, недавняя активность и политика конкретной версии Android.

### Дополнительные Вопросы (RU)

- Как `oom_adj`/importance-оценка динамически меняется при переходах состояний `Activity`?
- В чем компромиссы между использованием foreground-сервисов и `WorkManager` для фоновых задач?
- Как привязанные (`bound`) сервисы могут влиять на приоритет процессов между разными приложениями?

### Ссылки (RU)

- https://developer.android.com/guide/components/activities/process-lifecycle - Жизненный цикл процессов
- https://developer.android.com/guide/components/services - Сервисы и приоритет процессов

### Связанные Вопросы (RU)

#### Предпосылки / Концепции

- [[c-memory-management]]
- [[c-lifecycle]]

#### Предпосылки (проще)

- [[q-anr-application-not-responding--android--medium]] - Основы ANR
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Компоненты Android

#### Связанные (сложные)

- q-android-memory-management--android--hard - Стратегии управления памятью
- q-background-execution-limits--android--hard - Ограничения фонового выполнения

#### Продвинутые (сложные)

- q-process-death-handling--android--hard - Обработка смерти процесса

## Answer (EN)

Android determines process priority via an **importance hierarchy** based on component state and user visibility/impact. This hierarchy guides the system (ActivityManager together with lmkd/LMK and related mechanisms) when reclaiming memory and allocating CPU/resources.

Important: concrete `oom_adj` values and internal thresholds are implementation details and vary across Android versions. It is safer to reason in terms of importance categories, not fixed numeric ranges.

### Priority Hierarchy (conceptual)

From highest to lowest:

1. **Foreground process** - user actively interacting or running user-critical work
2. **Visible process** - some part of its UI visible to the user
3. **Perceptible / `Service` process** - important background work perceptible to the user (e.g., music playback, ongoing call)
4. **Cached process** - holds stopped components, kept for fast restart
5. **Empty process** - no active components, mostly used as cache, reclaimed first under pressure

### Determination Criteria (simplified)

Below are typical conditions; exact flags/values depend on Android version and internal logic.

**Foreground:**
- `Activity` in resumed state (in focus)
- Foreground service via `startForeground()` with a required notification
- `BroadcastReceiver.onReceive()` or `ContentProvider` work associated with current user-visible operations

**Visible:**
- `Activity` paused but still visible (e.g., dialog on top)
- Components (e.g., bound service) associated with a visible `Activity`

**Perceptible / `Service`:**
- Services doing user-perceptible work (music, active call, allowed tracking, etc.) when permitted by background execution policies
- Bound services referenced by foreground/visible components can elevate the hosting process priority

**Cached:**
- `Activity` in stopped state (not visible) but process still holds its state or other inactive components
- No active foreground/visible/perceptible components
- Processes kept in LRU and killed under memory pressure

**Empty:**
- Process without active components or useful cached state
- Among the first candidates to be killed when memory is needed; not literally "immediately", but lowest priority

### Checking Priority

For debugging you can inspect your process importance via `ActivityManager.RunningAppProcessInfo.importance`:

```kotlin
class PriorityChecker(private val context: Context) {
    fun logCurrentPriority() {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val processes = am.runningAppProcesses ?: return

        val myPid = android.os.Process.myPid()
        val myProcess = processes.find { it.pid == myPid } ?: return

        val level = when (myProcess.importance) {
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_FOREGROUND -> "FOREGROUND"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_VISIBLE -> "VISIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_SERVICE -> "SERVICE / PERCEPTIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_PERCEPTIBLE -> "PERCEPTIBLE"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_CACHED -> "CACHED"
            ActivityManager.RunningAppProcessInfo.IMPORTANCE_EMPTY -> "EMPTY"
            else -> "OTHER (${myProcess.importance})"
        }
        Log.d("Priority", "Current importance: $level")
    }
}
```

Notes:
- The set and meaning of `importance` values can evolve across API levels.
- `runningAppProcesses` and these flags are best used for diagnostics and understanding, not as a strict production contract.

### Influencing Factors

1. **`Component` state** - a resumed `Activity` promotes the process to foreground.
2. **`Service` type** - a foreground service (`startForeground()`) raises the process to foreground-level priority; regular background services are heavily restricted on modern Android and may run at lower priority or be disallowed.
3. **Bound services** - a service bound to a foreground/visible component gets higher priority.
4. **Process dependencies** - if process A depends on process B via critical binder bindings, the system may raise B's priority closer to A's.

### Low Memory Killer / Lmkd

Under memory pressure, the system (via `ActivityManager` and `lmkd`/LMK) kills processes starting from the least important:

1. Empty / low-priority cached processes
2. Cached processes in LRU order
3. `Service` / perceptible processes — only under significant pressure
4. Visible / Foreground processes — only as a last resort when resources are exhausted

Decisions consider not only the category, but also actual memory usage, recency, and policies of the specific Android version.

---

## Follow-ups

- How does the oom_adj/importance score dynamically change during `Activity` lifecycle transitions?
- What are the trade-offs between using foreground Services versus `WorkManager` for background tasks?
- How can bound Services affect the priority of processes across different applications?

## References

- https://developer.android.com/guide/components/activities/process-lifecycle - Process lifecycle
- https://developer.android.com/guide/components/services - Services and process priority

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-lifecycle]]

### Prerequisites (Easier)
- [[q-anr-application-not-responding--android--medium]] - ANR fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Android components

### Related (Hard)
- q-android-memory-management--android--hard - Memory management strategies
- q-background-execution-limits--android--hard - Background execution restrictions

### Advanced (Hard)
- q-process-death-handling--android--hard - Handling process death
