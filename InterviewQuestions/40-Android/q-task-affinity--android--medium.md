---
id: 20251012-122711115
title: "Task Affinity in Android / Task Affinity в Android"
aliases:
  - "Task Affinity in Android"
  - "Task Affinity в Android"
topic: android
subtopics: [activity, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-task-affinity, q-activity-lifecycle--android--medium, q-android-navigation--android--medium]
created: 2025-10-05
updated: 2025-01-25
tags: [android/activity, android/ui-navigation, task-affinity, tasks, activity, navigation, difficulty/medium]
sources: [https://developer.android.com/guide/components/activities/tasks-and-back-stack]
---

# Вопрос (RU)
> Что такое taskAffinity и как она работает?

# Question (EN)
> What is taskAffinity and how does it work?

---

## Ответ (RU)

**Теория Task Affinity:**
TaskAffinity определяет, к какой задаче активность "предпочитает" принадлежать. По умолчанию все активности одного приложения имеют одинаковое сродство, но можно изменить это поведение для группировки активностей из разных приложений или разделения активностей внутри одного приложения.

**Объявление в AndroidManifest:**
```xml
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**Когда сродство вступает в силу:**
TaskAffinity влияет на поведение активностей в двух случаях.

**1. FLAG_ACTIVITY_NEW_TASK:**
При использовании флага NEW_TASK система ищет задачу с тем же сродством.

```kotlin
// Запуск активности в новой задаче или существующей с тем же сродством
val intent = Intent(this, WeatherActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**2. allowTaskReparenting:**
Активность может переместиться в задачу с тем же сродством при выходе на передний план.

```xml
<!-- Активность может переместиться в задачу с тем же сродством -->
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**Практические примеры:**
- Группировка связанных активностей из разных приложений
- Разделение рабочих процессов внутри одного приложения
- Управление активностями из уведомлений

## Answer (EN)

**Task Affinity Theory:**
TaskAffinity defines which task an activity "prefers" to belong to. By default, all activities from the same app have the same affinity, but you can change this behavior to group activities from different apps or separate activities within one app.

**Declaration in AndroidManifest:**
```xml
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**When affinity comes into play:**
TaskAffinity affects activity behavior in two cases.

**1. FLAG_ACTIVITY_NEW_TASK:**
When using NEW_TASK flag, system looks for a task with the same affinity.

```kotlin
// Launch activity in new task or existing one with same affinity
val intent = Intent(this, WeatherActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**2. allowTaskReparenting:**
Activity can move to a task with the same affinity when it comes to foreground.

```xml
<!-- Activity can move to task with same affinity -->
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**Practical examples:**
- Grouping related activities from different apps
- Separating workflows within one app
- Managing activities launched from notifications

---

## Follow-ups

- How does taskAffinity affect the back stack?
- What happens when you don't specify taskAffinity?
- How do you handle taskAffinity with notifications?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-activity-basics--android--easy]] - Activity basics

### Related (Same Level)
- [[q-activity-lifecycle--android--medium]] - Activity lifecycle
- [[q-android-navigation--android--medium]] - Android navigation
- [[q-task-back-stack--android--medium]] - Task back stack

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
- [[q-activity-launch-modes--android--hard]] - Launch modes
