---
id: 20251012-122711115
title: "Task Affinity in Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-05
tags: [task-affinity, tasks, activity, navigation, manifest, difficulty/medium, android/ui-navigation, android/lifecycle]
aliases:   - Task Affinity in Android
  - Task Affinity в Android
category: android
date_modified: 2025-10-05
language_tags: [task-affinity, tasks, activity, navigation, manifest, difficulty/medium, android/ui-navigation, android/lifecycle]
moc: moc-android
related: [q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard, q-espresso-advanced-patterns--testing--medium, q-fix-slow-app-startup-legacy--android--hard]
original_language: en
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20taskAffinity.md"
subtopics:
  - activity
  - ui-navigation
  - lifecycle
type: question
---
# Task Affinity in Android / Task Affinity в Android

# Question (EN)
> 

What do you know about taskAffinity?

## Answer (EN)
The `taskAffinity` is the attribute that is declared in the AndroidManifest file.

An *affinity* indicates which task an activity "prefers" to belong to. By default, all the activities from the same app have an affinity for each other: they "prefer" to be in the same task.

However, you can modify the default affinity for an activity. Activities defined in different apps can share an affinity, and activities defined in the same app can be assigned different task affinities.

You can modify an activity's affinity using the `taskAffinity` attribute of the `<activity>` element.

The `taskAffinity` attribute takes a string value that must be different than the default package name declared in the `<manifest>` element, because the system uses that name to identify the default task affinity for the app.

### When Affinity Comes Into Play

The affinity comes into play in two circumstances:

#### 1. When the intent contains the FLAG_ACTIVITY_NEW_TASK flag

A new activity, by default, is launched into the task of the activity that called `startActivity()`. It's pushed onto the same back stack as the caller.

However, if the intent passed to `startActivity()` contains the `FLAG_ACTIVITY_NEW_TASK` flag, the system looks for a different task to house the new activity. Often, this is a new task. However, it doesn't have to be. If there's an existing task with the same affinity as the new activity, the activity is launched into that task. If not, it begins a new task.

If this flag causes an activity to begin a new task and the user uses the Home button or gesture to leave it, there must be some way for the user to navigate back to the task. Some entities, such as the notification manager, always start activities in an external task, never as part of their own, so they always put `FLAG_ACTIVITY_NEW_TASK` in the intents they pass to `startActivity()`.

If an external entity that might use this flag can invoke your activity, take care that the user has an independent way to get back to the task that's started, such as with a launcher icon, where the root activity of the task has a `CATEGORY_LAUNCHER` intent filter.

#### 2. When an activity has its allowTaskReparenting attribute set to "true"

In this case, the activity can move from the task it starts in to the task it has an affinity for when that task comes to the foreground.

For example, suppose an activity that reports weather conditions in selected cities is defined as part of a travel app. It has the same affinity as other activities in the same app, the default app affinity, and it can be re-parented with this attribute.

When one of your activities starts the weather reporter activity, it initially belongs to the same task as your activity. However, when the travel app's task comes to the foreground, the weather reporter activity is reassigned to that task and displayed within it.

### Important Note

**Note**: If an APK file contains more than one "app" from the user's point of view, you probably want to use the taskAffinity attribute to assign different affinities to the activities associated with each "app".

### Use Cases

Common use cases for taskAffinity include:

- Grouping related activities from different apps together
- Separating different workflows within the same app
- Managing activities launched from notifications
- Controlling activity reparenting behavior
- Creating separate task stacks for different app sections

---

# Вопрос (RU)
> 

Что вы знаете о taskAffinity?

## Ответ (RU)
`taskAffinity` - это атрибут, который объявляется в файле AndroidManifest.

*Affinity* (сродство) указывает, к какой задаче активность "предпочитает" принадлежать. По умолчанию все активности из одного приложения имеют сродство друг к другу: они "предпочитают" находиться в одной задаче.

Однако вы можете изменить сродство по умолчанию для активности. Активности, определенные в разных приложениях, могут иметь общее сродство, а активности, определенные в одном приложении, могут иметь разные сродства задач.

Вы можете изменить сродство активности, используя атрибут `taskAffinity` элемента `<activity>`.

Атрибут `taskAffinity` принимает строковое значение, которое должно отличаться от имени пакета по умолчанию, объявленного в элементе `<manifest>`, поскольку система использует это имя для идентификации сродства задачи по умолчанию для приложения.

### Когда сродство вступает в силу

Сродство вступает в силу в двух обстоятельствах:

#### 1. Когда intent содержит флаг FLAG_ACTIVITY_NEW_TASK

Новая активность по умолчанию запускается в задаче активности, которая вызвала `startActivity()`. Она помещается в тот же стек возврата, что и вызывающий.

Однако, если intent, переданный в `startActivity()`, содержит флаг `FLAG_ACTIVITY_NEW_TASK`, система ищет другую задачу для размещения новой активности. Часто это новая задача. Однако это не обязательно. Если существует задача с тем же сродством, что и новая активность, активность запускается в этой задаче. Если нет, начинается новая задача.

Если этот флаг заставляет активность начать новую задачу, и пользователь использует кнопку или жест Home, чтобы покинуть ее, должен быть какой-то способ для пользователя вернуться к задаче. Некоторые сущности, такие как менеджер уведомлений, всегда запускают активности во внешней задаче, никогда как часть своей собственной, поэтому они всегда помещают `FLAG_ACTIVITY_NEW_TASK` в intents, которые они передают в `startActivity()`.

Если внешняя сущность, которая может использовать этот флаг, может вызвать вашу активность, позаботьтесь о том, чтобы у пользователя был независимый способ вернуться к запущенной задаче, например, с помощью значка лаунчера, где корневая активность задачи имеет фильтр intent `CATEGORY_LAUNCHER`.

#### 2. Когда активность имеет атрибут allowTaskReparenting, установленный в "true"

В этом случае активность может переместиться из задачи, в которой она запускается, в задачу, к которой она имеет сродство, когда эта задача выходит на передний план.

Например, предположим, что активность, которая сообщает о погодных условиях в выбранных городах, определена как часть туристического приложения. Она имеет то же сродство, что и другие активности в том же приложении, сродство приложения по умолчанию, и она может быть перенесена с этим атрибутом.

Когда одна из ваших активностей запускает активность отчета о погоде, она изначально принадлежит той же задаче, что и ваша активность. Однако, когда задача туристического приложения выходит на передний план, активность отчета о погоде переназначается этой задаче и отображается в ней.

### Важное замечание

**Примечание**: Если APK-файл содержит более одного "приложения" с точки зрения пользователя, вы, вероятно, захотите использовать атрибут taskAffinity для назначения различных сродств активностям, связанным с каждым "приложением".

### Варианты использования

Распространенные варианты использования taskAffinity включают:

- Группировка связанных активностей из разных приложений вместе
- Разделение различных рабочих процессов в одном приложении
- Управление активностями, запускаемыми из уведомлений
- Контроль поведения переноса активностей
- Создание отдельных стеков задач для различных разделов приложения

## Related Questions

- [[q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard]]
- [[q-espresso-advanced-patterns--testing--medium]]
- [[q-fix-slow-app-startup-legacy--android--hard]]
