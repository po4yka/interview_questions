---
id: 20251003-140001
title: ViewModel vs onSavedInstanceState / ViewModel vs onSavedInstanceState
aliases: [ViewModel vs SavedInstanceState, Сохранение состояния Android]

# Classification
topic: android
subtopics: [lifecycle, activity]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/757
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-viewmodel
  - c-activity-lifecycle
  - c-configuration-changes
  - c-savedinstancestate

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags (EN only; no leading #)
tags: [viewmodel, lifecycle, savedinstancestate, android/lifecycle, android/activity, difficulty/medium, easy_kotlin, lang/ru, platform/android, configuration-changes]
---

# Question (EN)
> ViewModel vs onSavedInstanceState

# Вопрос (RU)
> ViewModel vs onSavedInstanceState

---

## Answer (EN)

ViewModel and onSaveInstanceState are used to preserve data during configuration changes of an activity or fragment, but they serve different purposes and have different characteristics.

### ViewModel

**Purpose**: Store and manage UI-related data that persists through configuration changes.

**Characteristics**:
- Stores data **in memory** until the Activity or Fragment is completely destroyed
- Survives configuration changes (rotation, language change, etc.)
- **Does not survive** process death
- Convenient for **complex objects** (lists, complex data structures)
- Scoped to Activity/Fragment lifecycle
- Part of Android Jetpack Architecture Components

**Use case**: Large or complex data that needs to survive configuration changes but not process death.

### onSaveInstanceState()

**Purpose**: Save data in a Bundle that the system automatically passes when recreating Activity or Fragment.

**Characteristics**:
- Data saved to **Bundle** (serialized)
- Survives configuration changes
- **Survives process death** (system-initiated)
- Suitable for **small amounts of data** (primitives, small strings)
- Limited by Bundle size constraints (~500KB)
- Requires data to be Parcelable/Serializable

**Use case**: Small, critical data that must survive both configuration changes and process death.

### Comparison Table

| Feature | ViewModel | onSavedInstanceState |
|---------|-----------|----------------------|
| **Storage** | Memory | Bundle (serialized) |
| **Survives rotation** | ✅ Yes | ✅ Yes |
| **Survives process death** | ❌ No | ✅ Yes |
| **Data size** | Large objects | Small data only |
| **Performance** | Fast | Slower (serialization) |
| **Best for** | Complex UI state | Critical small data |

### Recommendation

Use **both together**:
- ViewModel for UI state and complex data
- onSavedInstanceState for critical small data that must survive process death

**Example**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Restore critical data from Bundle
        val userId = savedInstanceState?.getInt("user_id")

        // Use ViewModel for complex state
        viewModel.loadUserData(userId)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save only critical small data
        outState.putInt("user_id", viewModel.userId)
    }
}
```

## Ответ (RU)

ViewModel и onSaveInstanceState служат для сохранения данных при изменении конфигурации активности или фрагмента, но они имеют разные назначения и характеристики.

### ViewModel

**Назначение**: Хранение и управление данными, связанными с UI, которые сохраняются при изменении конфигурации.

**Характеристики**:
- Хранит данные **в памяти** до полного уничтожения Activity или Fragment
- Переживает изменения конфигурации (поворот, смена языка и т.д.)
- **Не переживает** смерть процесса
- Удобен для **сложных объектов** (списки, сложные структуры данных)
- Привязан к жизненному циклу Activity/Fragment
- Часть Android Jetpack Architecture Components

**Применение**: Большие или сложные данные, которые должны пережить изменения конфигурации, но не смерть процесса.

### onSaveInstanceState()

**Назначение**: Сохранение данных в Bundle, который система автоматически передаёт при пересоздании Activity или Fragment.

**Характеристики**:
- Данные сохраняются в **Bundle** (сериализация)
- Переживает изменения конфигурации
- **Переживает смерть процесса** (инициированную системой)
- Подходит для **небольших данных** (примитивы, короткие строки)
- Ограничен размером Bundle (~500КБ)
- Требует, чтобы данные были Parcelable/Serializable

**Применение**: Небольшие критичные данные, которые должны пережить и изменения конфигурации, и смерть процесса.

### Сравнительная таблица

| Характеристика | ViewModel | onSavedInstanceState |
|----------------|-----------|----------------------|
| **Хранение** | Память | Bundle (сериализация) |
| **Переживает поворот** | ✅ Да | ✅ Да |
| **Переживает смерть процесса** | ❌ Нет | ✅ Да |
| **Размер данных** | Большие объекты | Только малые данные |
| **Производительность** | Быстро | Медленнее (сериализация) |
| **Лучше для** | Сложное состояние UI | Критичные малые данные |

### Рекомендация

Используйте **оба вместе**:
- ViewModel для состояния UI и сложных данных
- onSavedInstanceState для критичных малых данных, которые должны пережить смерть процесса

**Пример**:
```kotlin
class MyActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Восстановить критичные данные из Bundle
        val userId = savedInstanceState?.getInt("user_id")

        // Использовать ViewModel для сложного состояния
        viewModel.loadUserData(userId)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранить только критичные малые данные
        outState.putInt("user_id", viewModel.userId)
    }
}
```

---

## Follow-ups
- What happens to ViewModel when the process is killed?
- How to use SavedStateHandle in ViewModel?
- What's the maximum size for onSavedInstanceState Bundle?
- How to handle large data that needs to survive process death?

## References
- [[c-viewmodel]]
- [[c-activity-lifecycle]]
- [[c-configuration-changes]]
- [[c-savedinstancestate]]
- [ViewModel Documentation](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)

## Related Questions
- [[q-activity-lifecycle-methods--android--medium]]
- [[q-configuration-changes--android--medium]]
- [[q-viewmodel-scope--android--medium]]
