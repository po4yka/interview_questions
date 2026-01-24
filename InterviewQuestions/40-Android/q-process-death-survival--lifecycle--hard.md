---
id: android-lc-003
title: Process Death Survival / Выживание при смерти процесса
aliases: []
topic: android
subtopics:
- lifecycle
- process-death
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
- c-process
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/process-death
- difficulty/hard
anki_cards:
- slug: android-lc-003-0-en
  language: en
  anki_id: 1769172243359
  synced_at: '2026-01-23T16:45:05.460213'
- slug: android-lc-003-0-ru
  language: ru
  anki_id: 1769172243385
  synced_at: '2026-01-23T16:45:05.461790'
---
# Question (EN)
> What survives process death and what doesn't?

# Vopros (RU)
> Что выживает при смерти процесса и что нет?

---

## Answer (EN)

**Process death** occurs when the system kills your app's process while it's in the background to reclaim memory.

**What SURVIVES process death:**
- `SavedInstanceState` bundle
- `SavedStateHandle` in ViewModel
- Data persisted to disk (Room, SharedPreferences, files)
- Pending intents and alarms
- Navigation back stack structure

**What is LOST:**
- All in-memory state
- ViewModel instances (contrary to config changes!)
- Static variables
- Singletons
- Running coroutines/threads
- Network connections
- Cached data in memory

**Cold start restore flow:**
```
User switches to app
    -> System recreates Application
    -> System recreates Activity with savedInstanceState
    -> onCreate(bundle) called with saved state
    -> New ViewModel created (old one is gone!)
```

**Testing process death:**
```bash
# Put app in background, then:
adb shell am kill com.yourapp.package

# Or use "Don't keep activities" in Developer Options
```

**Handling properly:**

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Survives process death via SavedStateHandle
    val userId: String? = savedStateHandle["user_id"]

    fun setUserId(id: String) {
        savedStateHandle["user_id"] = id
    }

    // This is LOST on process death
    var cachedData: List<Item>? = null
}
```

**Common bugs from ignoring process death:**
- NullPointerException on restored state
- Lost user input (forms, drafts)
- Broken navigation state
- Crashes on resume

## Otvet (RU)

**Смерть процесса** происходит когда система убивает процесс приложения в фоне для освобождения памяти.

**Что ВЫЖИВАЕТ при смерти процесса:**
- Bundle `SavedInstanceState`
- `SavedStateHandle` в ViewModel
- Данные, сохранённые на диск (Room, SharedPreferences, файлы)
- Pending intents и alarms
- Структура back stack навигации

**Что ТЕРЯЕТСЯ:**
- Всё in-memory состояние
- Экземпляры ViewModel (в отличие от config changes!)
- Статические переменные
- Синглтоны
- Запущенные корутины/потоки
- Сетевые соединения
- Кэшированные данные в памяти

**Поток восстановления при холодном старте:**
```
Пользователь переключается на приложение
    -> Система пересоздаёт Application
    -> Система пересоздаёт Activity с savedInstanceState
    -> onCreate(bundle) вызывается с сохранённым состоянием
    -> Создаётся новый ViewModel (старый потерян!)
```

**Тестирование смерти процесса:**
```bash
# Переведите приложение в фон, затем:
adb shell am kill com.yourapp.package

# Или используйте "Не сохранять действия" в настройках разработчика
```

**Правильная обработка:**

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Выживает при смерти процесса через SavedStateHandle
    val userId: String? = savedStateHandle["user_id"]

    fun setUserId(id: String) {
        savedStateHandle["user_id"] = id
    }

    // Это ТЕРЯЕТСЯ при смерти процесса
    var cachedData: List<Item>? = null
}
```

**Частые баги от игнорирования смерти процесса:**
- NullPointerException при восстановлении состояния
- Потерянный ввод пользователя (формы, черновики)
- Сломанное состояние навигации
- Краши при возобновлении

---

## Follow-ups
- How to test process death scenarios?
- What is SavedStateHandle and how does it work?
- How does Navigation Component handle process death?

## References
- [[c-lifecycle]]
- [[c-process]]
- [[moc-android]]
