---
id: android-377
title: Как работает навигация Activity / How Activity Navigation Works
aliases: [Activity Back Stack, Activity Navigation, Навигация Activity, Стек активностей]
topic: android
subtopics:
  - activity
  - lifecycle
  - ui-navigation
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-activity-lifecycle
  - c-intent-system
  - q-activity-lifecycle-methods--android--medium
  - q-what-is-intent--android--easy
created: 2025-10-15
updated: 2025-10-29
tags: [android/activity, android/lifecycle, android/ui-navigation, back-stack, difficulty/medium, intent]
sources:
  - https://developer.android.com/guide/components/activities/tasks-and-back-stack
  - https://developer.android.com/guide/navigation
date created: Wednesday, October 29th 2025, 4:18:18 pm
date modified: Sunday, November 2nd 2025, 12:43:25 pm
---

# Вопрос (RU)

> Как работает навигация между Activity в Android?

---

# Question (EN)

> How does Activity navigation work in Android?

---

## Ответ (RU)

Навигация между Activity управляется через **Intent** (намерение), **back stack** (стек возврата) и **Task** (задача). Система использует стек LIFO для управления жизненным циклом Activity.

**Ключевые компоненты:**

### 1. Intent — Механизм Запуска Activity

```kotlin
// ✅ Explicit Intent — указываем конкретный класс
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — система выбирает подходящее приложение
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

### 2. Back Stack — LIFO Стек Activity

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

### 3. Управление Стеком Через Intent Flags

```kotlin
// ✅ Очистить все Activity выше целевой
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Не создавать новый экземпляр, если уже на вершине
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Начать новую задачу и очистить старую
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
// Используется для logout: очищает весь стек и открывает LoginActivity
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

### 5. Возврат Результата Из Activity

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

**Современный подход — Navigation Component:**

```kotlin
// ✅ Навигация через NavController (рекомендуется для фрагментов)
findNavController().navigate(R.id.action_home_to_detail)

// ✅ С аргументами
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

---

## Answer (EN)

Activity navigation is managed via **Intent**, **back stack**, and **Task**. The system uses a LIFO stack to manage Activity lifecycle.

**Core components:**

### 1. Intent — Activity Launch Mechanism

```kotlin
// ✅ Explicit Intent — specify target class
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — system chooses appropriate app
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

### 2. Back Stack — LIFO Stack of Activities

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

### 3. Stack Management via Intent Flags

```kotlin
// ✅ Clear all Activities above target
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Don't create new instance if already on top
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Start new task and clear old one
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
// Used for logout: clears entire stack and opens LoginActivity
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

### 5. Returning Result from Activity

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

**Modern approach — Navigation Component:**

```kotlin
// ✅ Navigate via NavController (recommended for fragments)
findNavController().navigate(R.id.action_home_to_detail)

// ✅ With arguments
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

---

## Follow-ups

- Что происходит со стеком Activity при повороте экрана?
- В чём разница между launch modes: standard, singleTop, singleTask, singleInstance?
- Как обрабатывать deep links и навигацию из push-уведомлений?
- Почему Navigation Component рекомендуется вместо прямой навигации Activity?
- Как восстановить стек Activity после убийства процесса системой?

## References

- [[c-activity-lifecycle]] — жизненный цикл Activity
- https://developer.android.com/guide/components/activities/tasks-and-back-stack
- https://developer.android.com/guide/navigation
- https://developer.android.com/guide/components/intents-filters

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-intent--android--easy]] — основы Intent в Android
- [[q-activity-lifecycle-methods--android--medium]] — методы жизненного цикла Activity

### Related (Same Level)
- [[q-intent-filters-android--android--medium]] — Intent filters для implicit навигации
