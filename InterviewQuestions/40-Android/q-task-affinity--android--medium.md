---
id: android-016
title: Task Affinity in Android / Task Affinity в Android
aliases: [Task Affinity in Android, Task Affinity в Android]
topic: android
subtopics:
  - activity
  - ui-navigation
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-activity
  - q-android-app-components--android--easy
  - q-android-lint-tool--android--medium
  - q-main-thread-android--android--medium
  - q-parsing-optimization-android--android--medium
created: 2025-10-05
updated: 2025-11-10
tags: [android/activity, android/ui-navigation, difficulty/medium, task-affinity, tasks]
sources:
  - "https://developer.android.com/guide/components/activities/tasks-and-back-stack"

date created: Saturday, November 1st 2025, 1:24:35 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Что такое taskAffinity и как она работает?

# Question (EN)
> What is taskAffinity and how does it work?

---

## Ответ (RU)

**Теория Task Affinity:**
TaskAffinity определяет, к какой задаче (task) активность "предпочитает" принадлежать. По умолчанию (если не переопределено ни у application, ни у activity) все активности одного приложения имеют одинаковое сродство, равное package name приложения. Это поведение можно изменить:
- настроив `taskAffinity` на уровне `<application>` (тогда оно станет значением по умолчанию для активностей);
- переопределив `taskAffinity` на уровне конкретной `<activity>`, чтобы:
  - разделять независимые потоки внутри одного приложения;
  - (реже) согласованно группировать связанные активности между приложениями.

Важно: `taskAffinity` само по себе не изменяет обычное поведение back stack внутри одной задачи. Оно учитывается системой в определённых сценариях (см. ниже) — в том числе при использовании `FLAG_ACTIVITY_NEW_TASK`, специальных `launchMode` и при перепривязке задач (`allowTaskReparenting`).

**Объявление в AndroidManifest:**
```xml
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```
Также можно указать пустую строку ("") , чтобы активность не наследовала affinity приложения по умолчанию и не присоединялась к задачам только на основании этого affinity (обычно используется для более точного контроля в сочетании с флагами запуска и launchMode).

**Когда сродство вступает в силу:**
TaskAffinity влияет на поведение активностей в типичных случаях:

**1. FLAG_ACTIVITY_NEW_TASK (и связанные флаги/launchMode):**
При использовании флага `FLAG_ACTIVITY_NEW_TASK` (или launchMode вроде `singleTask` / `singleInstance` / `singleInstancePerTask`), система рассматривает `taskAffinity` целевой активности:
- если уже существует задача с таким `taskAffinity`, активность будет запущена/добавлена именно в эту задачу;
- если нет — будет создана новая задача с указанным affinity.

```kotlin
// Запуск активности в новой задаче или существующей с тем же affinity
val intent = Intent(this, WeatherActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**2. allowTaskReparenting:**
`android:allowTaskReparenting="true"` позволяет уже запущенной активности (часто запущенной из другого приложения или задачи) "перепривязаться" (reparent) к задаче с совпадающим `taskAffinity`, когда такая задача выходит на передний план. Типичный сценарий:
- активность A вашего приложения запущена в задаче чужого приложения (например, по ссылке из другого приложения);
- позже пользователь открывает основную задачу вашего приложения;
- при включённом `allowTaskReparenting` активность A может быть перенесена в задачу вашего приложения, affinity которой она соответствует.

```xml
<!-- Активность может быть перепривязана к задаче с тем же affinity -->
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**Практические примеры:**
- Разделение независимых рабочих процессов внутри одного приложения по разным задачам.
- Управление задачами и back stack при запуске активностей из уведомлений через `FLAG_ACTIVITY_NEW_TASK` с нужным `taskAffinity`.
- (Аккуратно) использование общего affinity между приложениями одного вендора для общего пользовательского сценария.

## Answer (EN)

**Task Affinity Theory:**
TaskAffinity defines which task an activity "prefers" to belong to. By default (when not overridden at either the application or activity level), all activities in the same app share the same affinity, equal to the app's package name. You can change this by:
- setting `taskAffinity` on the `<application>` element (which becomes the default for its activities);
- overriding `taskAffinity` on individual `<activity>` elements to:
  - separate independent flows within one app;
  - (less commonly) coordinate grouping of related activities across apps.

Important: `taskAffinity` does not by itself change normal back stack behavior within a single task. It is taken into account by the system in specific scenarios (see below), including when using `FLAG_ACTIVITY_NEW_TASK`, special launch modes, and task reparenting via `allowTaskReparenting`.

**Declaration in AndroidManifest:**
```xml
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```
You can also set an empty string ("") so that an activity does not inherit the app's default affinity and will not join tasks solely based on that affinity (typically used for more fine-grained control together with specific launch flags and launch modes).

**When affinity comes into play:**
TaskAffinity affects activity behavior in typical cases:

**1. FLAG_ACTIVITY_NEW_TASK (and related flags/launch modes):**
When using `FLAG_ACTIVITY_NEW_TASK` (or launch modes like `singleTask` / `singleInstance` / `singleInstancePerTask`), the system uses the target activity's `taskAffinity` to resolve the task:
- if there is an existing task with that `taskAffinity`, the activity will be launched/placed into that task;
- otherwise a new task with that affinity will be created.

```kotlin
// Launch activity in a new task or an existing one with the same affinity
val intent = Intent(this, WeatherActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**2. allowTaskReparenting:**
`android:allowTaskReparenting="true"` allows an already running activity (often launched from another app or task) to move (reparent) to a task with the same `taskAffinity` when that matching task comes to the foreground. A common scenario:
- your activity A is started in another app's task (e.g., via a link);
- later, the user brings your main task to the foreground;
- with `allowTaskReparenting` enabled, activity A may be moved into your task whose affinity it matches.

```xml
<!-- Activity can be reparented to the task with the same affinity -->
<activity
    android:name=".WeatherActivity"
    android:taskAffinity="com.example.weather"
    android:allowTaskReparenting="true" />
```

**Practical examples:**
- Separating independent workflows within a single app into different tasks.
- Controlling tasks and back stack when launching activities from notifications via `FLAG_ACTIVITY_NEW_TASK` and an appropriate `taskAffinity`.
- (Carefully) sharing a common affinity between related vendor apps to support a unified user flow.

---

## Дополнительные Вопросы (RU)

- Как taskAffinity влияет на back stack?
- Что происходит, если не указывать taskAffinity (ни у application, ни у activity)?
- Как использовать taskAffinity при работе с уведомлениями и `FLAG_ACTIVITY_NEW_TASK`?

## Follow-ups

- How does taskAffinity affect the back stack?
- What happens when you don't specify taskAffinity (neither on application nor on activity)?
- How do you handle taskAffinity with notifications and `FLAG_ACTIVITY_NEW_TASK`?


## Ссылки (RU)

- [Навигация](https://developer.android.com/guide/navigation)
- [Активности](https://developer.android.com/guide/components/activities)

## References

- [Navigation](https://developer.android.com/guide/navigation)
- [Activities](https://developer.android.com/guide/components/activities)


## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-activity-lifecycle]]

### Предпосылки (проще)

- [[q-android-app-components--android--easy]] - Компоненты приложения

### Связанные (средний уровень)

- [[q-tasks-back-stack--android--medium]] - Task back stack

### Продвинутые (сложнее)

- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство Runtime


## Related Questions

### Prerequisites / Concepts

- [[c-activity-lifecycle]]


### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-tasks-back-stack--android--medium]] - Task back stack

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime internals
