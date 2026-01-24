---
id: android-lc-020
title: Back Stack Recreation and State / Пересоздание Back Stack и состояние
aliases: []
topic: android
subtopics:
- lifecycle
- navigation
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
- c-navigation
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/navigation
- difficulty/hard
anki_cards:
- slug: android-lc-020-0-en
  language: en
  anki_id: 1769172279131
  synced_at: '2026-01-23T16:45:06.149225'
- slug: android-lc-020-0-ru
  language: ru
  anki_id: 1769172279157
  synced_at: '2026-01-23T16:45:06.150513'
---
# Question (EN)
> How is back stack recreated after process death and what state is preserved?

# Vopros (RU)
> Как пересоздаётся back stack после смерти процесса и какое состояние сохраняется?

---

## Answer (EN)

**Back stack** is automatically saved and restored after process death, but understanding what's preserved is critical.

**What's saved in back stack:**
- Fragment class names
- Fragment arguments (Bundle)
- Transaction operations order
- Navigation destination history
- Per-fragment savedInstanceState

**What's NOT saved:**
- ViewModel instances (recreated fresh)
- View bindings (views recreated)
- Runtime state not in savedInstanceState
- Non-serializable arguments

**Recreation flow:**
```
Process Death:
    [System saves: BackStackRecord[], FragmentState[], NavController state]

Process Restart:
    1. Application.onCreate()
    2. Activity.onCreate(savedInstanceState)
    3. FragmentManager.restoreAllState()
       - Each Fragment: newInstance() via reflection
       - Arguments restored from saved Bundle
       - savedInstanceState restored
    4. NavController.restoreState()
       - Back stack recreated
       - Current destination determined
    5. Fragments: onCreate(savedInstanceState) -> onViewCreated()
```

**Navigation Component state:**
```kotlin
// NavController saves:
// - Back stack structure
// - Current destination ID
// - NavArgs for each entry
// - SavedStateHandle data

// Restored automatically if using NavHostFragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // NavController restores from savedInstanceState automatically
        val navController = findNavController(R.id.nav_host)
    }
}
```

**Fragment arguments survival:**
```kotlin
// GOOD: Arguments survive process death
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // args.itemId is available after process death
        loadItem(args.itemId)
    }
}

// BAD: Not using arguments properly
class DetailFragment : Fragment() {
    var itemId: Int = 0  // Lost on recreation!
}
```

**Saving custom state:**
```kotlin
class MyFragment : Fragment() {
    private var customState: CustomState? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        if (savedInstanceState != null) {
            // Restore custom state
            customState = savedInstanceState.getParcelable("custom_state")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save custom state
        outState.putParcelable("custom_state", customState)
    }
}
```

**Back stack entry state (Navigation 2.4+):**
```kotlin
// Save state when navigating away
navController.navigate(R.id.detailFragment) {
    // Previous destination state is saved automatically
    popUpTo(R.id.listFragment) { saveState = true }
}

// Restore state when navigating back
navController.navigate(R.id.listFragment) {
    restoreState = true
}
```

**Common pitfalls:**
```kotlin
// BAD: Passing non-parcelable via arguments
arguments = bundleOf("callback" to myCallback)  // Will crash on restoration

// BAD: Storing view references in savedInstanceState
outState.putParcelable("view", binding.textView)  // Don't do this

// BAD: Large data in savedInstanceState
outState.putParcelable("bitmap", largeBitmap)  // TransactionTooLargeException

// GOOD: Store only IDs/keys, reload data
outState.putLong("item_id", currentItem.id)
```

## Otvet (RU)

**Back stack** автоматически сохраняется и восстанавливается после смерти процесса, но понимание что сохраняется - критично.

**Что сохраняется в back stack:**
- Имена классов Fragment
- Аргументы Fragment (Bundle)
- Порядок операций транзакций
- История destination навигации
- savedInstanceState для каждого фрагмента

**Что НЕ сохраняется:**
- Экземпляры ViewModel (создаются заново)
- View bindings (views пересоздаются)
- Runtime состояние не в savedInstanceState
- Несериализуемые аргументы

**Поток пересоздания:**
```
Смерть процесса:
    [Система сохраняет: BackStackRecord[], FragmentState[], состояние NavController]

Перезапуск процесса:
    1. Application.onCreate()
    2. Activity.onCreate(savedInstanceState)
    3. FragmentManager.restoreAllState()
       - Каждый Fragment: newInstance() через рефлексию
       - Аргументы восстановлены из сохранённого Bundle
       - savedInstanceState восстановлен
    4. NavController.restoreState()
       - Back stack пересоздан
       - Текущий destination определён
    5. Фрагменты: onCreate(savedInstanceState) -> onViewCreated()
```

**Состояние Navigation Component:**
```kotlin
// NavController сохраняет:
// - Структуру back stack
// - ID текущего destination
// - NavArgs для каждой записи
// - Данные SavedStateHandle

// Восстанавливается автоматически при использовании NavHostFragment
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // NavController восстанавливается из savedInstanceState автоматически
        val navController = findNavController(R.id.nav_host)
    }
}
```

**Выживание аргументов Fragment:**
```kotlin
// ХОРОШО: Аргументы переживают смерть процесса
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // args.itemId доступен после смерти процесса
        loadItem(args.itemId)
    }
}

// ПЛОХО: Неправильное использование аргументов
class DetailFragment : Fragment() {
    var itemId: Int = 0  // Теряется при пересоздании!
}
```

**Сохранение кастомного состояния:**
```kotlin
class MyFragment : Fragment() {
    private var customState: CustomState? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        if (savedInstanceState != null) {
            // Восстановить кастомное состояние
            customState = savedInstanceState.getParcelable("custom_state")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранить кастомное состояние
        outState.putParcelable("custom_state", customState)
    }
}
```

**Состояние записи back stack (Navigation 2.4+):**
```kotlin
// Сохранить состояние при уходе
navController.navigate(R.id.detailFragment) {
    // Состояние предыдущего destination сохраняется автоматически
    popUpTo(R.id.listFragment) { saveState = true }
}

// Восстановить состояние при возврате
navController.navigate(R.id.listFragment) {
    restoreState = true
}
```

**Частые ловушки:**
```kotlin
// ПЛОХО: Передача non-parcelable через аргументы
arguments = bundleOf("callback" to myCallback)  // Упадёт при восстановлении

// ПЛОХО: Хранение ссылок на view в savedInstanceState
outState.putParcelable("view", binding.textView)  // Не делайте так

// ПЛОХО: Большие данные в savedInstanceState
outState.putParcelable("bitmap", largeBitmap)  // TransactionTooLargeException

// ХОРОШО: Храните только ID/ключи, перезагружайте данные
outState.putLong("item_id", currentItem.id)
```

---

## Follow-ups
- How to handle deep link restoration after process death?
- What is the size limit for savedInstanceState?
- How to debug back stack issues?

## References
- [[c-lifecycle]]
- [[c-navigation]]
- [[moc-android]]
