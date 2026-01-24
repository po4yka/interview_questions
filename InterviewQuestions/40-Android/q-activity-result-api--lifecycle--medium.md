---
id: android-lc-010
title: Activity Result API / Activity Result API
aliases: []
topic: android
subtopics:
- lifecycle
- activities
question_kind: theory
difficulty: medium
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
- difficulty/medium
anki_cards:
- slug: android-lc-010-0-en
  language: en
  anki_id: 1769172289182
  synced_at: '2026-01-23T16:45:06.265328'
- slug: android-lc-010-0-ru
  language: ru
  anki_id: 1769172289208
  synced_at: '2026-01-23T16:45:06.267291'
---
# Question (EN)
> How does Activity Result API handle lifecycle and why is it safer than onActivityResult?

# Vopros (RU)
> Как Activity Result API обрабатывает lifecycle и почему он безопаснее onActivityResult?

---

## Answer (EN)

**Activity Result API** is a modern replacement for `startActivityForResult()` that properly handles lifecycle and configuration changes.

**Why old approach was problematic:**
```kotlin
// OLD way - problems:
// 1. onActivityResult called after onStart, Fragment might not exist
// 2. Request codes scattered across codebase
// 3. No type safety
// 4. Fragment result routing is manual

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    if (requestCode == REQUEST_IMAGE && resultCode == RESULT_OK) {
        // Handle result - but is Fragment still alive?
    }
}
```

**New Activity Result API:**
```kotlin
class MyFragment : Fragment() {

    // 1. Register BEFORE onCreate (at property initialization)
    private val getContent = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        // Safe: callback called only when Fragment is at least STARTED
        uri?.let { processImage(it) }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        button.setOnClickListener {
            // 2. Launch when needed
            getContent.launch("image/*")
        }
    }
}
```

**Lifecycle safety guarantees:**
- Callback registered in `CREATED` state
- Callback delivered only when owner is at least `STARTED`
- Survives configuration changes automatically
- Result stored until owner reaches correct state

**Built-in contracts:**
```kotlin
// Take photo
val takePicture = registerForActivityResult(TakePicture()) { success ->
    if (success) { /* photo saved to uri */ }
}

// Request permissions
val requestPermission = registerForActivityResult(RequestPermission()) { granted ->
    if (granted) { /* permission granted */ }
}

// Pick contact
val pickContact = registerForActivityResult(PickContact()) { uri ->
    uri?.let { loadContact(it) }
}
```

**Custom contract:**
```kotlin
class MyContract : ActivityResultContract<Input, Output>() {
    override fun createIntent(context: Context, input: Input): Intent {
        return Intent(context, TargetActivity::class.java)
            .putExtra("data", input)
    }

    override fun parseResult(resultCode: Int, intent: Intent?): Output {
        return if (resultCode == RESULT_OK) {
            intent?.getParcelableExtra("result")!!
        } else {
            Output.Empty
        }
    }
}
```

**Key rules:**
- Register in initialization or `onCreate()`, NOT in `onStart()/onResume()`
- Launcher can be called anytime after registration
- Result delivered when lifecycle allows

## Otvet (RU)

**Activity Result API** - современная замена `startActivityForResult()`, которая правильно обрабатывает lifecycle и изменения конфигурации.

**Почему старый подход был проблемным:**
```kotlin
// СТАРЫЙ способ - проблемы:
// 1. onActivityResult вызывается после onStart, Fragment может не существовать
// 2. Request codes разбросаны по кодовой базе
// 3. Нет типобезопасности
// 4. Маршрутизация результата во Fragment ручная

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    if (requestCode == REQUEST_IMAGE && resultCode == RESULT_OK) {
        // Обработать результат - но Fragment ещё жив?
    }
}
```

**Новый Activity Result API:**
```kotlin
class MyFragment : Fragment() {

    // 1. Регистрация ДО onCreate (при инициализации свойства)
    private val getContent = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        // Безопасно: callback вызывается только когда Fragment минимум STARTED
        uri?.let { processImage(it) }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        button.setOnClickListener {
            // 2. Запуск когда нужно
            getContent.launch("image/*")
        }
    }
}
```

**Гарантии безопасности lifecycle:**
- Callback зарегистрирован в состоянии `CREATED`
- Callback доставляется только когда owner минимум `STARTED`
- Автоматически переживает изменения конфигурации
- Результат хранится пока owner не достигнет правильного состояния

**Встроенные контракты:**
```kotlin
// Сделать фото
val takePicture = registerForActivityResult(TakePicture()) { success ->
    if (success) { /* фото сохранено в uri */ }
}

// Запросить разрешения
val requestPermission = registerForActivityResult(RequestPermission()) { granted ->
    if (granted) { /* разрешение получено */ }
}

// Выбрать контакт
val pickContact = registerForActivityResult(PickContact()) { uri ->
    uri?.let { loadContact(it) }
}
```

**Кастомный контракт:**
```kotlin
class MyContract : ActivityResultContract<Input, Output>() {
    override fun createIntent(context: Context, input: Input): Intent {
        return Intent(context, TargetActivity::class.java)
            .putExtra("data", input)
    }

    override fun parseResult(resultCode: Int, intent: Intent?): Output {
        return if (resultCode == RESULT_OK) {
            intent?.getParcelableExtra("result")!!
        } else {
            Output.Empty
        }
    }
}
```

**Ключевые правила:**
- Регистрация при инициализации или в `onCreate()`, НЕ в `onStart()/onResume()`
- Launcher можно вызвать в любое время после регистрации
- Результат доставляется когда lifecycle позволяет

---

## Follow-ups
- How to test Activity Result API?
- How does result survive configuration change?
- What are all built-in ActivityResultContracts?

## References
- [[c-lifecycle]]
- [[c-activities]]
- [[moc-android]]
