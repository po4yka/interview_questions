---
id: android-lc-015
title: Launch Modes and Tasks / Режимы запуска и Tasks
aliases: []
topic: android
subtopics:
- lifecycle
- activities
- tasks
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-activities
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/activities
- difficulty/hard
anki_cards:
- slug: android-lc-015-0-en
  language: en
  anki_id: 1769172245557
  synced_at: '2026-01-23T16:45:05.500189'
- slug: android-lc-015-0-ru
  language: ru
  anki_id: 1769172245582
  synced_at: '2026-01-23T16:45:05.502266'
---
# Question (EN)
> What are Activity launch modes and how do they affect tasks and back stack?

# Vopros (RU)
> Какие есть режимы запуска Activity и как они влияют на tasks и back stack?

---

## Answer (EN)

**Launch modes** control how Activities are instantiated and added to tasks.

**Four launch modes:**

| Mode | Instances | Task | Use Case |
|------|-----------|------|----------|
| standard | Multiple | Same task | Default, most screens |
| singleTop | One at top | Same task | Search, notifications |
| singleTask | One in task | Own task | Main entry point |
| singleInstance | One in system | Exclusive task | Launcher-like |
| singleInstancePerTask | One per task | Own task | API 31+ |

**1. standard (default):**
```
Task: A -> B -> A -> A
Each startActivity creates new instance
Back: A -> B -> A -> [exit]
```

**2. singleTop:**
```
Task: A -> B, start B with singleTop:
Result: A -> B (same B, onNewIntent called)

Task: A -> B -> C, start B with singleTop:
Result: A -> B -> C -> B (new instance, B not at top)
```

**3. singleTask:**
```
Task: A -> B -> C, start A with singleTask:
Result: A (B and C destroyed, A receives onNewIntent)

Always clears everything above it in the task.
Creates new task if not existing.
```

**4. singleInstance:**
```
Task1: A -> B (starts C with singleInstance)
Task2: C (isolated, exclusive task)

C cannot have other activities in its task.
```

**Manifest declaration:**
```xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTask"
    android:taskAffinity="com.app.main" />
```

**Intent flags (runtime):**
```kotlin
// Clear everything on top
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP

// Create new task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK

// Don't add to history
intent.flags = Intent.FLAG_ACTIVITY_NO_HISTORY

// Combine flags
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or
               Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Common combinations:**

```kotlin
// Clear entire task and start fresh
Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or
            Intent.FLAG_ACTIVITY_CLEAR_TASK
}

// Bring existing to front or create
Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
            Intent.FLAG_ACTIVITY_SINGLE_TOP
}
```

**Task affinity:**
```xml
<!-- Same affinity = same task (default) -->
<activity android:taskAffinity="com.app.checkout" />

<!-- Empty affinity = no affinity -->
<activity android:taskAffinity="" />
```

**Lifecycle implications:**
- `singleTop/singleTask`: `onNewIntent()` called instead of `onCreate()`
- `CLEAR_TOP`: Destroys activities above, then `onCreate()` or `onNewIntent()`
- `NEW_TASK + CLEAR_TASK`: Destroys entire task, fresh `onCreate()`

## Otvet (RU)

**Режимы запуска** контролируют как Activities создаются и добавляются в tasks.

**Четыре режима запуска:**

| Режим | Экземпляры | Task | Применение |
|-------|------------|------|------------|
| standard | Множество | Тот же task | По умолчанию, большинство экранов |
| singleTop | Один наверху | Тот же task | Поиск, уведомления |
| singleTask | Один в task | Свой task | Главная точка входа |
| singleInstance | Один в системе | Эксклюзивный task | Launcher-подобные |
| singleInstancePerTask | Один на task | Свой task | API 31+ |

**1. standard (по умолчанию):**
```
Task: A -> B -> A -> A
Каждый startActivity создаёт новый экземпляр
Назад: A -> B -> A -> [выход]
```

**2. singleTop:**
```
Task: A -> B, запуск B с singleTop:
Результат: A -> B (тот же B, вызван onNewIntent)

Task: A -> B -> C, запуск B с singleTop:
Результат: A -> B -> C -> B (новый экземпляр, B не наверху)
```

**3. singleTask:**
```
Task: A -> B -> C, запуск A с singleTask:
Результат: A (B и C уничтожены, A получает onNewIntent)

Всегда очищает всё над собой в task.
Создаёт новый task если не существует.
```

**4. singleInstance:**
```
Task1: A -> B (запускает C с singleInstance)
Task2: C (изолирован, эксклюзивный task)

C не может иметь других activities в своём task.
```

**Объявление в манифесте:**
```xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTask"
    android:taskAffinity="com.app.main" />
```

**Intent флаги (runtime):**
```kotlin
// Очистить всё сверху
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP

// Создать новый task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK

// Не добавлять в историю
intent.flags = Intent.FLAG_ACTIVITY_NO_HISTORY

// Комбинировать флаги
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or
               Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Частые комбинации:**

```kotlin
// Очистить весь task и начать заново
Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or
            Intent.FLAG_ACTIVITY_CLEAR_TASK
}

// Вывести существующий на передний план или создать
Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
            Intent.FLAG_ACTIVITY_SINGLE_TOP
}
```

**Task affinity:**
```xml
<!-- Один affinity = один task (по умолчанию) -->
<activity android:taskAffinity="com.app.checkout" />

<!-- Пустой affinity = без affinity -->
<activity android:taskAffinity="" />
```

**Влияние на lifecycle:**
- `singleTop/singleTask`: Вызывается `onNewIntent()` вместо `onCreate()`
- `CLEAR_TOP`: Уничтожает activities сверху, затем `onCreate()` или `onNewIntent()`
- `NEW_TASK + CLEAR_TASK`: Уничтожает весь task, свежий `onCreate()`

---

## Follow-ups
- What is taskAffinity and when to use it?
- How to debug task and back stack issues?
- What is allowTaskReparenting?

## References
- [[c-lifecycle]]
- [[c-activities]]
- [[moc-android]]
