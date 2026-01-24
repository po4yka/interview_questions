---
id: android-lc-019
title: Activity Recreation vs Process Death / Пересоздание Activity vs Смерть процесса
aliases: []
topic: android
subtopics:
- lifecycle
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
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- difficulty/medium
anki_cards:
- slug: android-lc-019-0-en
  language: en
  anki_id: 1769172241833
  synced_at: '2026-01-23T16:45:05.427882'
- slug: android-lc-019-0-ru
  language: ru
  anki_id: 1769172241858
  synced_at: '2026-01-23T16:45:05.429444'
---
# Question (EN)
> What is the difference between Activity recreation and process death?

# Vopros (RU)
> В чём разница между пересозданием Activity и смертью процесса?

---

## Answer (EN)

**Activity recreation** and **process death** are different scenarios with different survival guarantees.

**Comparison:**

| Aspect | Activity Recreation | Process Death |
|--------|-------------------|---------------|
| Trigger | Config change, system kills Activity | System kills entire process |
| ViewModel | Survives | Destroyed |
| SavedInstanceState | Available | Available |
| SavedStateHandle | Not used (ViewModel alive) | Restored |
| Static variables | Preserved | Lost |
| In-memory cache | Preserved | Lost |

**Activity Recreation triggers:**
- Screen rotation
- Locale change
- Font size change
- Keyboard availability
- Night mode change
- System kills for memory (Activity only)

**Process Death triggers:**
- App in background, system needs memory
- User force stops app
- `adb shell am kill <package>`
- Device reboot

**Lifecycle flow comparison:**

```
Configuration Change (rotation):
    Activity A: onPause -> onStop -> onDestroy
                 -> NEW Activity A: onCreate(bundle) -> onStart -> onResume
    ViewModel: SURVIVES (same instance)

Process Death:
    [App in background]
    [System kills process]
    [User returns to app]
    Application: onCreate() (NEW Application instance!)
    Activity A: onCreate(bundle) -> onStart -> onResume
    ViewModel: NEW instance (old one gone!)
```

**Testing both scenarios:**
```bash
# Test configuration change
adb shell settings put system font_scale 1.1

# Test process death (preferred)
# 1. Put app in background
# 2. Run:
adb shell am kill <package-name>
# 3. Return to app from recents

# Alternative: Developer Options > "Don't keep activities"
# (But this is NOT the same as process death!)
```

**Handling both correctly:**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Survives config change AND process death
    val searchQuery: StateFlow<String> =
        savedStateHandle.getStateFlow("query", "")

    // Survives config change only
    private var cachedResults: List<Item>? = null

    fun getData(): Flow<List<Item>> = flow {
        // Check cache first (only valid if no process death)
        cachedResults?.let {
            emit(it)
            return@flow
        }

        // Fetch from network
        val data = repository.fetchData()
        cachedResults = data
        emit(data)
    }
}
```

**Common mistake:**
```kotlin
// Assuming ViewModel survives everything
class MyViewModel : ViewModel() {
    // Lost on process death - user loses progress!
    var formDraft: FormData? = null
}

// Fix: Use SavedStateHandle
class MyViewModel(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    val formDraft: StateFlow<FormData?> =
        savedStateHandle.getStateFlow("draft", null)
}
```

## Otvet (RU)

**Пересоздание Activity** и **смерть процесса** - разные сценарии с разными гарантиями выживания.

**Сравнение:**

| Аспект | Пересоздание Activity | Смерть процесса |
|--------|----------------------|-----------------|
| Триггер | Изменение конфига, система убивает Activity | Система убивает весь процесс |
| ViewModel | Выживает | Уничтожается |
| SavedInstanceState | Доступен | Доступен |
| SavedStateHandle | Не используется (ViewModel жив) | Восстанавливается |
| Статические переменные | Сохраняются | Теряются |
| Кэш в памяти | Сохраняется | Теряется |

**Триггеры пересоздания Activity:**
- Поворот экрана
- Смена локали
- Изменение размера шрифта
- Доступность клавиатуры
- Смена ночного режима
- Система убивает для памяти (только Activity)

**Триггеры смерти процесса:**
- Приложение в фоне, системе нужна память
- Пользователь принудительно закрывает
- `adb shell am kill <package>`
- Перезагрузка устройства

**Сравнение потоков lifecycle:**

```
Изменение конфигурации (поворот):
    Activity A: onPause -> onStop -> onDestroy
                 -> НОВАЯ Activity A: onCreate(bundle) -> onStart -> onResume
    ViewModel: ВЫЖИВАЕТ (тот же экземпляр)

Смерть процесса:
    [Приложение в фоне]
    [Система убивает процесс]
    [Пользователь возвращается]
    Application: onCreate() (НОВЫЙ экземпляр Application!)
    Activity A: onCreate(bundle) -> onStart -> onResume
    ViewModel: НОВЫЙ экземпляр (старый потерян!)
```

**Тестирование обоих сценариев:**
```bash
# Тест изменения конфигурации
adb shell settings put system font_scale 1.1

# Тест смерти процесса (предпочтительно)
# 1. Переведите приложение в фон
# 2. Выполните:
adb shell am kill <package-name>
# 3. Вернитесь в приложение из недавних

# Альтернатива: Developer Options > "Не сохранять действия"
# (Но это НЕ то же самое что смерть процесса!)
```

**Правильная обработка обоих:**
```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Выживает изменение конфига И смерть процесса
    val searchQuery: StateFlow<String> =
        savedStateHandle.getStateFlow("query", "")

    // Выживает только изменение конфига
    private var cachedResults: List<Item>? = null

    fun getData(): Flow<List<Item>> = flow {
        // Сначала проверить кэш (валиден только если не было смерти процесса)
        cachedResults?.let {
            emit(it)
            return@flow
        }

        // Загрузить из сети
        val data = repository.fetchData()
        cachedResults = data
        emit(data)
    }
}
```

**Частая ошибка:**
```kotlin
// Предполагая что ViewModel выживает всё
class MyViewModel : ViewModel() {
    // Теряется при смерти процесса - пользователь теряет прогресс!
    var formDraft: FormData? = null
}

// Исправление: Используйте SavedStateHandle
class MyViewModel(
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    val formDraft: StateFlow<FormData?> =
        savedStateHandle.getStateFlow("draft", null)
}
```

---

## Follow-ups
- How to detect if app was restored from process death?
- What are the limitations of SavedStateHandle?
- How does Navigation handle process death?

## References
- [[c-lifecycle]]
- [[moc-android]]
