---
id: 20251012-122757
title: Как работает навигация Activity / Activity Navigation How It Works
aliases:
  - Навигация Activity
  - Activity Navigation
  - Activity Back Stack
  - Стек активностей
topic: android
subtopics: [activity, ui-navigation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related:
  - q-activity-lifecycle-methods--android--medium
  - q-intent-filters-android--android--medium
  - q-what-is-intent--android--easy
created: 2025-10-15
updated: 2025-10-27
tags: [android/activity, android/ui-navigation, intent, back-stack, difficulty/medium]
sources:
  - https://developer.android.com/guide/components/activities/tasks-and-back-stack
  - https://developer.android.com/guide/navigation
---
# Вопрос (RU)

> Как работает навигация между Activity в Android?

---

# Question (EN)

> How does Activity navigation work in Android?

## Ответ (RU)

Навигация между Activity в Android управляется через **Intent**, **back stack** (стек возврата) и систему задач (tasks).

**Основные механизмы:**

1. **Intent** — сообщение для запуска Activity:
   - Explicit (явный) — указывает конкретный класс Activity
   - Implicit (неявный) — описывает действие, система выбирает подходящий компонент

2. **Back Stack** — стек Activity (LIFO):
   - Каждая новая Activity добавляется в стек
   - Кнопка Back убирает верхнюю Activity из стека

3. **Task** — группа связанных Activity
4. **Launch Modes** — режимы запуска Activity (standard, singleTop, singleTask, singleInstance)

**Примеры Intent:**

```kotlin
// ✅ Explicit Intent — конкретная Activity
val intent = Intent(this, SecondActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — система выбирает приложение
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

**Жизненный цикл при навигации:**

```text
Activity A → Activity B:
  A: onPause() → onStop()
  B: onCreate() → onStart() → onResume()

Нажатие Back:
  B: onPause() → onStop() → onDestroy()
  A: onRestart() → onStart() → onResume()
```

**Флаги Intent для управления стеком:**

```kotlin
// ✅ Очистить верхние Activity до целевой
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Не создавать новый экземпляр, если уже наверху
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Очистить весь стек и начать новую задачу
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Управление стеком:**

```text
Навигация: A → B → C → D
Back stack: [A, B, C, D] ← D наверху

Back:
Back stack: [A, B, C] ← C видима, D уничтожена
```

**Закрытие Activity:**

```kotlin
// ✅ Закрыть текущую Activity
finish()

// ✅ Вернуть результат
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Современный подход — Navigation Component:**

```kotlin
// ✅ Навигация между фрагментами
findNavController().navigate(R.id.action_home_to_detail)

// ✅ С аргументами
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

---

## Answer (EN)

Activity navigation in Android is managed through **Intents**, **back stack**, and **task management**.

**Core mechanisms:**

1. **Intent** — message to launch Activity:
   - Explicit — specifies target Activity class
   - Implicit — declares action, system chooses component

2. **Back Stack** — LIFO stack of Activities:
   - Each new Activity pushed onto stack
   - Back button pops top Activity

3. **Task** — group of related Activities
4. **Launch Modes** — control instantiation (standard, singleTop, singleTask, singleInstance)

**Intent examples:**

```kotlin
// ✅ Explicit Intent — specific Activity
val intent = Intent(this, SecondActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// ✅ Implicit Intent — system chooses
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

**Lifecycle during navigation:**

```text
Activity A → Activity B:
  A: onPause() → onStop()
  B: onCreate() → onStart() → onResume()

Back pressed:
  B: onPause() → onStop() → onDestroy()
  A: onRestart() → onStart() → onResume()
```

**Intent flags for stack control:**

```kotlin
// ✅ Clear top Activities up to target
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// ✅ Don't create new instance if already on top
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// ✅ Clear entire stack and start new task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Stack management:**

```text
Navigation: A → B → C → D
Back stack: [A, B, C, D] ← D on top

Back:
Back stack: [A, B, C] ← C visible, D destroyed
```

**Closing Activity:**

```kotlin
// ✅ Close current Activity
finish()

// ✅ Return result
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Modern approach — Navigation Component:**

```kotlin
// ✅ Navigate between fragments
findNavController().navigate(R.id.action_home_to_detail)

// ✅ With arguments
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)
```

---

## Follow-ups

- Как обрабатывать deep links в навигации Activity?
- В чём разница между singleTop и singleTask launch modes?
- Что происходит со стеком при убийстве приложения системой?

## References

- https://developer.android.com/guide/components/activities/tasks-and-back-stack
- https://developer.android.com/guide/navigation
- https://developer.android.com/guide/components/intents-filters

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] — жизненный цикл Activity
- [[q-what-is-intent--android--easy]] — система Intent

### Advanced (Harder)
- [[q-intent-filters-android--android--medium]] — Intent filters и implicit navigation