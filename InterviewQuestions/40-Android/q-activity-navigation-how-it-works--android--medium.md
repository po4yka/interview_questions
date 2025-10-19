---
id: 20251012-122757
title: "Activity Navigation How It Works / Как работает навигация Activity"
aliases: [Activity Navigation, Навигация Activity]
topic: android
subtopics: [navigation, activity]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-intent-system--android--medium, q-navigation-component--android--medium]
created: 2025-10-15
updated: 2025-10-15
tags: [android/navigation, android/activity, navigation, activity, intent, back-stack, difficulty/medium]
---
# Question (EN)
> How does Activity navigation work in Android?

# Вопрос (RU)
> Как работает навигация по Activity в Android?

---

## Answer (EN)

Activity navigation in Android is managed through Intents, back stack, and task management.

**Main mechanisms:**

- **Explicit Intents**: Launch specific Activity by class name
- **Implicit Intents**: Declare general operation, system chooses appropriate component
- **Back Stack**: Manages Activity history (LIFO - last in, first out)
- **Task Management**: Groups related Activities together
- **Launch Modes**: Control how Activities are instantiated (standard, singleTop, singleTask, singleInstance)

**Intent types:**

```kotlin
// Explicit Intent - specific Activity
val intent = Intent(this, SecondActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// Implicit Intent - system chooses
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

**Activity lifecycle during navigation:**

```
Activity A → Activity B

Activity A: onPause() → onStop()
Activity B: onCreate() → onStart() → onResume()

User presses Back:
Activity B: onPause() → onStop() → onDestroy()
Activity A: onRestart() → onStart() → onResume()
```

**Closing Activity:**

```kotlin
// Close current Activity
finish()

// Return result
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Intent flags for back stack control:**

```kotlin
// Clear top and bring to front
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// Single top - don't create new instance
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// New task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK

// Clear entire task
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Back stack management:**

```
User flow: A → B → C → D
Back stack: [A, B, C, D] ← D on top

User presses Back:
Back stack: [A, B, C] ← C visible, D destroyed
```

**Modern approach - Navigation Component:**

```kotlin
// Navigate between Fragments
findNavController().navigate(R.id.action_home_to_detail)

// With arguments
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)

// Navigate back
findNavController().navigateUp()
```

**State saving:**

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putString("user_input", editText.text.toString())
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState != null) {
        val savedText = savedInstanceState.getString("user_input")
        editText.setText(savedText)
    }
}
```

## Ответ (RU)

Навигация между Activity в Android управляется через Intent, стек возврата (back stack) и управление задачами (task management).

**Основные механизмы:**

- **Явные Intent**: Запускают конкретную Activity по имени класса
- **Неявные Intent**: Объявляют общую операцию, система выбирает подходящий компонент
- **Back Stack**: Управляет историей Activity (LIFO - последним пришел, первым вышел)
- **Task Management**: Группирует связанные Activity вместе
- **Launch Modes**: Контролируют создание экземпляров Activity (standard, singleTop, singleTask, singleInstance)

**Типы Intent:**

```kotlin
// Явный Intent - конкретная Activity
val intent = Intent(this, SecondActivity::class.java)
intent.putExtra("USER_ID", userId)
startActivity(intent)

// Неявный Intent - система выбирает
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com"))
startActivity(intent)
```

**Жизненный цикл Activity при навигации:**

```
Activity A → Activity B

Activity A: onPause() → onStop()
Activity B: onCreate() → onStart() → onResume()

Пользователь нажимает Назад:
Activity B: onPause() → onStop() → onDestroy()
Activity A: onRestart() → onStart() → onResume()
```

**Закрытие Activity:**

```kotlin
// Закрыть текущую Activity
finish()

// Вернуть результат
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Флаги Intent для контроля back stack:**

```kotlin
// Очистить верх и поднять наверх
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)

// Single top - не создавать новый экземпляр
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP

// Новая задача
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK

// Очистить всю задачу
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
```

**Управление back stack:**

```
Поток пользователя: A → B → C → D
Back stack: [A, B, C, D] ← D наверху

Пользователь нажимает Назад:
Back stack: [A, B, C] ← C видна, D уничтожена
```

**Современный подход - Navigation Component:**

```kotlin
// Навигация между Fragment
findNavController().navigate(R.id.action_home_to_detail)

// С аргументами
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)

// Навигация назад
findNavController().navigateUp()
```

**Сохранение состояния:**

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putString("user_input", editText.text.toString())
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState != null) {
        val savedText = savedInstanceState.getString("user_input")
        editText.setText(savedText)
    }
}
```

---

## Follow-ups

- How do you handle deep links in Activity navigation?
- What's the difference between singleTop and singleTask launch modes?
- How do you prevent Activity recreation during configuration changes?
- What happens to the back stack when the app is killed?
- How do you implement custom transitions between Activities?

## References

- [Android Activity Navigation Guide](https://developer.android.com/guide/components/activities/tasks-and-back-stack)
- [Intent and Intent Filters](https://developer.android.com/guide/components/intents-filters)
- [Navigation Component](https://developer.android.com/guide/navigation)

## Related Questions

### Prerequisites (Easier)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle
- [[q-android-app-components--android--easy]] - Activity basics

### Related (Medium)
- [[q-intent-system--android--medium]] - Intent system
- [[q-navigation-component--android--medium]] - Navigation Component
- [[q-fragment-navigation--android--medium]] - Fragment navigation
- [[q-deep-links--android--medium]] - Deep linking

### Advanced (Harder)
- [[q-task-management--android--hard]] - Task management
- [[q-activity-launch-modes--android--hard]] - Launch modes
