---
id: android-377
title: Как работает навигация Activity / How Activity Navigation Works
aliases:
- Activity Back Stack
- Activity Navigation
- Навигация Activity
- Стек активностей
topic: android
subtopics:
- activity
- ui-navigation
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- q-activity-lifecycle-methods--android--medium
- q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium
- q-how-to-pass-data-from-one-activity-to-another--android--medium
- q-single-activity-approach--android--medium
- q-what-is-intent--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- android/ui-navigation
- back-stack
- difficulty/medium
- intent
anki_cards:
- slug: android-377-0-en
  language: en
  anki_id: 1768363502598
  synced_at: '2026-01-23T16:45:06.281726'
- slug: android-377-0-ru
  language: ru
  anki_id: 1768363502622
  synced_at: '2026-01-23T16:45:06.282594'
sources:
- https://developer.android.com/guide/components/activities/tasks-and-back-stack
- https://developer.android.com/guide/navigation
---
# Вопрос (RU)

> Как работает навигация между `Activity` в Android?

---

# Question (EN)

> How does `Activity` navigation work in Android?

---

## Ответ (RU)

Навигация между `Activity` управляется через **`Intent`** (намерение), **back stack** (стек возврата) и **Task** (задача). Система использует LIFO-структуру для управления стеком `Activity` внутри задачи и их жизненным циклом.

**Ключевые компоненты:**

### 1. `Intent` — Механизм Запуска `Activity`

```kotlin
// ✅ Explicit Intent — указываем конкретный класс
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — система выбирает подходящее приложение
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

### 2. Back `Stack` — LIFO Стек `Activity`

```text
Навигация: HomeActivity → ListActivity → DetailActivity

Back Stack:
┌─────────────────┐
│ DetailActivity  │ ← top (видима)
├─────────────────┤
│ ListActivity    │
├─────────────────┤
│ HomeActivity    │
└─────────────────┘

После Back:
┌─────────────────┐
│ ListActivity    │ ← top (видима)
├─────────────────┤
│ HomeActivity    │
└─────────────────┘
DetailActivity уничтожена (onDestroy)
```

### 3. Управление Стеком Через `Intent` Flags

```kotlin
// ✅ Очистить стек над существующим экземпляром Activity (если он есть в текущей задаче)
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Не создавать новый экземпляр, если Activity уже на вершине стека
// (обычно используется в сочетании с CLEAR_TOP или launchMode="singleTop")
val intent2 = Intent(this, MainActivity::class.java)
intent2.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent2)

// ✅ Комбинирование флагов — используем побитовое ИЛИ, а не перезапись
val intent3 = Intent(this, MainActivity::class.java)
intent3.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent3)

// ✅ Начать новую задачу и очистить текущую
val logoutIntent = Intent(this, LoginActivity::class.java)
logoutIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(logoutIntent)
// Используется для logout: очищает все Activity текущей задачи и делает LoginActivity корнем новой задачи
```

### 4. Жизненный Цикл При Навигации

```text
A → B (открытие новой Activity):
  A: onPause() → onStop()
  B: onCreate() → onStart() → onResume()

B → A (кнопка Back):
  B: onPause() → onStop() → onDestroy()
  A: onRestart() → onStart() → onResume()
```

### 5. Возврат Результата Из `Activity`

```kotlin
// ✅ Activity B возвращает результат в A
// В Activity A (запуск):
val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("RESULT_DATA")
    }
}
launcher.launch(Intent(this, ActivityB::class.java))

// В Activity B (возврат):
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Современный подход — Navigation `Component`:**

```kotlin
// ✅ Навигация через NavController (рекомендуется для фрагментов внутри одной Activity)
findNavController().navigate(R.id.action_home_to_detail)

// ✅ С аргументами
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

Navigation `Component` в основном управляет навигацией между фрагментами и графом навигации.
Для переходов между `Activity` по-прежнему используются `Intent` и back stack задач.

---

## Answer (EN)

`Activity` navigation is managed via **`Intent`**, **back stack**, and **Task**. The system uses a LIFO structure to manage the `Activity` stack within a task and their lifecycle.

**Core components:**

### 1. `Intent` — `Activity` Launch Mechanism

```kotlin
// ✅ Explicit Intent — specify target class
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — system chooses appropriate app
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

### 2. Back `Stack` — LIFO `Stack` of Activities

```text
Navigation: HomeActivity → ListActivity → DetailActivity

Back Stack:
┌─────────────────┐
│ DetailActivity  │ ← top (visible)
├─────────────────┤
│ ListActivity    │
├─────────────────┤
│ HomeActivity    │
└─────────────────┘

After Back:
┌─────────────────┐
│ ListActivity    │ ← top (visible)
├─────────────────┤
│ HomeActivity    │
└─────────────────┘
DetailActivity destroyed (onDestroy)
```

### 3. `Stack` Management via `Intent` Flags

```kotlin
// ✅ Clear activities above existing target instance (if present in current task)
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Don't create new instance if Activity is already at the top of the stack
// (commonly used with CLEAR_TOP or launchMode="singleTop")
val intent2 = Intent(this, MainActivity::class.java)
intent2.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent2)

// ✅ Combine flags using bitwise OR instead of overwriting
val intent3 = Intent(this, MainActivity::class.java)
intent3.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent3)

// ✅ Start a new task and clear the current one
val logoutIntent = Intent(this, LoginActivity::class.java)
logoutIntent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(logoutIntent)
// Used for logout: clears all Activities in the current task and makes LoginActivity the root of the new task
```

### 4. Lifecycle During Navigation

```text
A → B (opening new Activity):
  A: onPause() → onStop()
  B: onCreate() → onStart() → onResume()

B → A (Back button):
  B: onPause() → onStop() → onDestroy()
  A: onRestart() → onStart() → onResume()
```

### 5. Returning Result from `Activity`

```kotlin
// ✅ Activity B returns result to A
// In Activity A (launch):
val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("RESULT_DATA")
    }
}
launcher.launch(Intent(this, ActivityB::class.java))

// In Activity B (return):
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Modern approach — Navigation `Component`:**

```kotlin
// ✅ Navigate via NavController (recommended for fragments within a single-Activity architecture)
findNavController().navigate(R.id.action_home_to_detail)

// ✅ With arguments
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

Navigation `Component` primarily manages navigation between fragments and the navigation graph.
For navigation between Activities, Intents and the task back stack are still used.

---

## Follow-ups (RU)

- Что происходит со стеком `Activity` при повороте экрана?
- В чём разница между launch modes: `standard`, `singleTop`, `singleTask`, `singleInstance`?
- Как обрабатывать deep links и навигацию из push-уведомлений?
- Почему Navigation `Component` рекомендуется вместо прямой навигации `Activity`?
- Как восстановить стек `Activity` после убийства процесса системой?

## Follow-ups (EN)

- What happens to the `Activity` back stack on configuration change (e.g., rotation)?
- What is the difference between launch modes: `standard`, `singleTop`, `singleTask`, `singleInstance`?
- How to handle deep links and navigation from push notifications?
- Why is Navigation `Component` recommended instead of direct `Activity`-to-`Activity` navigation?
- How can you restore the `Activity` back stack after the system kills the process?

## References (RU)

- [[c-activity-lifecycle]] — жизненный цикл `Activity`
- https://developer.android.com/guide/components/activities/tasks-and-back-stack
- https://developer.android.com/guide/navigation
- https://developer.android.com/guide/components/intents-filters

## References (EN)

- [[c-activity-lifecycle]] — `Activity` lifecycle
- https://developer.android.com/guide/components/activities/tasks-and-back-stack
- https://developer.android.com/guide/navigation
- https://developer.android.com/guide/components/intents-filters

## Related Questions (RU)

### Prerequisites (Easier)

- [[q-what-is-intent--android--easy]] — основы `Intent` в Android
- [[q-activity-lifecycle-methods--android--medium]] — методы жизненного цикла `Activity`

### Related (Same Level)

- [[q-intent-filters-android--android--medium]] — `Intent` filters для implicit навигации

## Related Questions (EN)

### Prerequisites (Easier)

- [[q-what-is-intent--android--easy]] — basics of `Intent` in Android
- [[q-activity-lifecycle-methods--android--medium]] — `Activity` lifecycle methods

### Related (Same Level)

- [[q-intent-filters-android--android--medium]] — `Intent` filters for implicit navigation
