---
id: android-lc-006
title: onNewIntent When Called / Когда вызывается onNewIntent
aliases: []
topic: android
subtopics:
- lifecycle
- intent
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
- c-intent
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/intent
- difficulty/medium
anki_cards:
- slug: android-lc-006-0-en
  language: en
  anki_id: 1769172288482
  synced_at: '2026-01-23T16:45:06.255786'
- slug: android-lc-006-0-ru
  language: ru
  anki_id: 1769172288507
  synced_at: '2026-01-23T16:45:06.256659'
---
# Question (EN)
> When is onNewIntent() called and how to handle it properly?

# Vopros (RU)
> Когда вызывается onNewIntent() и как его правильно обрабатывать?

---

## Answer (EN)

**onNewIntent()** is called when an existing Activity instance receives a new Intent instead of creating a new instance.

**When onNewIntent is called:**
1. Activity has `launchMode="singleTop"` and is at top of stack
2. Activity has `launchMode="singleTask"` or `singleInstance"`
3. Intent has `FLAG_ACTIVITY_SINGLE_TOP` flag
4. Activity has `launchMode="singleInstancePerTask"` (API 31+)

**Lifecycle flow:**
```
// Activity already running, new intent arrives:
onPause() -> onNewIntent(intent) -> onResume()

// NOT called: onCreate(), onStart()
```

**Common mistake - forgetting to update intent:**
```kotlin
override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)

    // IMPORTANT: Update the activity's intent
    setIntent(intent)

    // Now handle the new intent
    handleIntent(intent)
}

private fun handleIntent(intent: Intent?) {
    val action = intent?.action
    val data = intent?.data
    // Process deep link, notification, etc.
}
```

**Typical use cases:**
- Deep links to already-open screen
- Notification taps when app is foreground
- Search queries in singleTop Activity
- Single-instance main screen

**Example with deep links:**
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent?.action == Intent.ACTION_VIEW) {
            val uri = intent.data
            navigateToDeepLink(uri)
        }
    }
}
```

**Key points:**
- Original `getIntent()` still returns OLD intent until you call `setIntent()`
- `onNewIntent()` is called BEFORE `onResume()`
- Activity is NOT recreated, so state is preserved

## Otvet (RU)

**onNewIntent()** вызывается когда существующий экземпляр Activity получает новый Intent вместо создания нового экземпляра.

**Когда вызывается onNewIntent:**
1. Activity имеет `launchMode="singleTop"` и находится на вершине стека
2. Activity имеет `launchMode="singleTask"` или `singleInstance"`
3. Intent имеет флаг `FLAG_ACTIVITY_SINGLE_TOP`
4. Activity имеет `launchMode="singleInstancePerTask"` (API 31+)

**Поток lifecycle:**
```
// Activity уже запущена, приходит новый intent:
onPause() -> onNewIntent(intent) -> onResume()

// НЕ вызываются: onCreate(), onStart()
```

**Частая ошибка - забыть обновить intent:**
```kotlin
override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)

    // ВАЖНО: Обновить intent activity
    setIntent(intent)

    // Теперь обработать новый intent
    handleIntent(intent)
}

private fun handleIntent(intent: Intent?) {
    val action = intent?.action
    val data = intent?.data
    // Обработать deep link, уведомление и т.д.
}
```

**Типичные сценарии использования:**
- Deep links на уже открытый экран
- Тапы по уведомлениям когда приложение на переднем плане
- Поисковые запросы в singleTop Activity
- Single-instance главный экран

**Пример с deep links:**
```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent?) {
        if (intent?.action == Intent.ACTION_VIEW) {
            val uri = intent.data
            navigateToDeepLink(uri)
        }
    }
}
```

**Ключевые моменты:**
- Оригинальный `getIntent()` возвращает СТАРЫЙ intent пока не вызовете `setIntent()`
- `onNewIntent()` вызывается ДО `onResume()`
- Activity НЕ пересоздаётся, поэтому состояние сохраняется

---

## Follow-ups
- What is the difference between singleTop and singleTask?
- How to handle pending intents with onNewIntent?
- How does Navigation Component handle new intents?

## References
- [[c-lifecycle]]
- [[c-intent]]
- [[moc-android]]
