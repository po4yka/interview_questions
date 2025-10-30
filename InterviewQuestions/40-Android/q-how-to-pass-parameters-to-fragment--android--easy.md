---
id: 20251012-1227191
title: "How To Pass Parameters To Fragment / Как передать параметры во Fragment"
aliases: ["How To Pass Parameters To Fragment", "Как передать параметры во Fragment", "Fragment arguments", "Fragment Bundle"]
topic: android
subtopics: [fragment, bundle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragment-basics--android--easy, q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium, q-how-to-pass-data-from-one-fragment-to-another--android--medium]
created: 2025-10-15
updated: 2025-10-30
sources: []
tags: [android, android/fragment, android/bundle, fragment, bundle, arguments, difficulty/medium]
date created: Thursday, October 30th 2025, 12:56:08 pm
date modified: Thursday, October 30th 2025, 2:17:20 pm
---

# Вопрос (RU)

Как передать параметры во фрагмент?

# Question (EN)

How to pass parameters to a Fragment?

---

## Ответ (RU)

Рекомендуемый и безопасный способ передачи параметров во Fragment в Android — использование **Bundle** через свойство `arguments` фрагмента. Этот подход поддерживается системой Android и сохраняет данные при изменении конфигурации.

### Основные подходы

**1. Базовый подход — Bundle с фабричным методом**

```kotlin
class DetailsFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"
        private const val ARG_ITEM_NAME = "item_name"

        // ✅ Фабричный метод для создания фрагмента с аргументами
        fun newInstance(itemId: Int, itemName: String) = DetailsFragment().apply {
            arguments = Bundle().apply {
                putInt(ARG_ITEM_ID, itemId)
                putString(ARG_ITEM_NAME, itemName)
            }
        }
    }

    // ✅ Извлечение аргументов в onCreate
    private var itemId: Int = -1
    private var itemName: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            itemId = it.getInt(ARG_ITEM_ID, -1)
            itemName = it.getString(ARG_ITEM_NAME)
        }
    }
}

// Использование
val fragment = DetailsFragment.newInstance(itemId = 42, itemName = "Item")
```

**2. Kotlin-способ с requireArguments() и lazy**

```kotlin
class UserFragment : Fragment() {
    companion object {
        private const val ARG_USER_ID = "user_id"
        private const val ARG_EMAIL = "user_email"

        fun newInstance(userId: Long, email: String) = UserFragment().apply {
            arguments = Bundle().apply {
                putLong(ARG_USER_ID, userId)
                putString(ARG_EMAIL, email)
            }
        }
    }

    // ✅ Ленивая инициализация из аргументов
    private val userId: Long by lazy {
        requireArguments().getLong(ARG_USER_ID)
    }
    private val email: String by lazy {
        requireArguments().getString(ARG_EMAIL) ?: ""
    }
}
```

**3. Передача сложных объектов — Parcelable**

```kotlin
@Parcelize
data class User(val id: Long, val name: String, val email: String) : Parcelable

class ProfileFragment : Fragment() {
    companion object {
        private const val ARG_USER = "user"

        fun newInstance(user: User) = ProfileFragment().apply {
            arguments = Bundle().apply { putParcelable(ARG_USER, user) }
        }
    }

    // ✅ Безопасное извлечение Parcelable с учетом API 33+
    private val user: User by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelable(ARG_USER, User::class.java)!!
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelable(ARG_USER)!!
        }
    }
}
```

### Лучшие практики

1. **Всегда используйте Bundle и arguments** — не передавайте данные через конструктор или сеттеры
2. **Создавайте фабричные методы** (newInstance) в companion object
3. **Извлекайте аргументы в onCreate()**, не в конструкторе
4. **Используйте requireArguments()** для обязательных параметров
5. **Используйте константы** для ключей аргументов
6. **Предпочитайте Parcelable** вместо Serializable (лучше производительность)

### Распространенные ошибки

```kotlin
// ❌ НЕПРАВИЛЬНО — конструктор (данные теряются при повороте экрана)
class WrongFragment(private val itemId: Int) : Fragment() {
    // Данные потеряются при изменении конфигурации!
}

// ❌ НЕПРАВИЛЬНО — сеттеры (небезопасно при изменении конфигурации)
class WrongFragment : Fragment() {
    private var itemId: Int = 0
    fun setItemId(id: Int) {
        this.itemId = id  // Потеряется при повороте экрана
    }
}

// ✅ ПРАВИЛЬНО — Bundle
class CorrectFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(itemId: Int) = CorrectFragment().apply {
            arguments = Bundle().apply { putInt(ARG_ITEM_ID, itemId) }
        }
    }

    private val itemId by lazy { requireArguments().getInt(ARG_ITEM_ID) }
}
```

---

## Answer (EN)

The recommended and safe way to pass parameters to a Fragment in Android is using **Bundle** with the fragment's `arguments` property. This approach is supported by the Android system and survives configuration changes.

### Key Approaches

**1. Basic Approach — Bundle with Factory Method**

```kotlin
class DetailsFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"
        private const val ARG_ITEM_NAME = "item_name"

        // ✅ Factory method to create fragment with arguments
        fun newInstance(itemId: Int, itemName: String) = DetailsFragment().apply {
            arguments = Bundle().apply {
                putInt(ARG_ITEM_ID, itemId)
                putString(ARG_ITEM_NAME, itemName)
            }
        }
    }

    // ✅ Extract arguments in onCreate
    private var itemId: Int = -1
    private var itemName: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            itemId = it.getInt(ARG_ITEM_ID, -1)
            itemName = it.getString(ARG_ITEM_NAME)
        }
    }
}

// Usage
val fragment = DetailsFragment.newInstance(itemId = 42, itemName = "Item")
```

**2. Kotlin Way with requireArguments() and Lazy**

```kotlin
class UserFragment : Fragment() {
    companion object {
        private const val ARG_USER_ID = "user_id"
        private const val ARG_EMAIL = "user_email"

        fun newInstance(userId: Long, email: String) = UserFragment().apply {
            arguments = Bundle().apply {
                putLong(ARG_USER_ID, userId)
                putString(ARG_EMAIL, email)
            }
        }
    }

    // ✅ Lazy initialization from arguments
    private val userId: Long by lazy {
        requireArguments().getLong(ARG_USER_ID)
    }
    private val email: String by lazy {
        requireArguments().getString(ARG_EMAIL) ?: ""
    }
}
```

**3. Passing Complex Objects — Parcelable**

```kotlin
@Parcelize
data class User(val id: Long, val name: String, val email: String) : Parcelable

class ProfileFragment : Fragment() {
    companion object {
        private const val ARG_USER = "user"

        fun newInstance(user: User) = ProfileFragment().apply {
            arguments = Bundle().apply { putParcelable(ARG_USER, user) }
        }
    }

    // ✅ Safe Parcelable extraction with API 33+ support
    private val user: User by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelable(ARG_USER, User::class.java)!!
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelable(ARG_USER)!!
        }
    }
}
```

### Best Practices

1. **Always use Bundle and arguments** — never pass data via constructor or setters
2. **Create factory methods** (newInstance) in companion object
3. **Extract arguments in onCreate()**, not in constructors
4. **Use requireArguments()** for required parameters
5. **Use constants** for argument keys
6. **Prefer Parcelable** over Serializable (better performance)

### Common Mistakes

```kotlin
// ❌ WRONG — constructor (data lost on configuration change)
class WrongFragment(private val itemId: Int) : Fragment() {
    // Data will be lost on screen rotation!
}

// ❌ WRONG — setters (unsafe for configuration changes)
class WrongFragment : Fragment() {
    private var itemId: Int = 0
    fun setItemId(id: Int) {
        this.itemId = id  // Lost on screen rotation
    }
}

// ✅ CORRECT — Bundle
class CorrectFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(itemId: Int) = CorrectFragment().apply {
            arguments = Bundle().apply { putInt(ARG_ITEM_ID, itemId) }
        }
    }

    private val itemId by lazy { requireArguments().getInt(ARG_ITEM_ID) }
}
```

---

## Follow-ups

- What happens if you don't use Bundle and pass data via constructor?
- How does Bundle survive configuration changes like screen rotation?
- When should you use Parcelable vs Serializable for complex objects?
- How does the Navigation Component's Safe Args plugin improve type safety?
- What are the memory limits for data passed through Bundle?

## References

- [[c-fragment-lifecycle]] - Fragment lifecycle fundamentals
- [[c-bundle]] - Bundle data structure
- [[c-parcelable]] - Parcelable implementation
- [Android Documentation - Fragments](https://developer.android.com/guide/fragments)
- [Navigation Component Safe Args](https://developer.android.com/guide/navigation/navigation-pass-data#Safe-args)

## Related Questions

### Prerequisites (Easier)
- [[q-fragment-basics--android--easy]] - Fragment fundamentals
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment layout basics

### Related (Same Level)
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - Fragment communication
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Fragment lifecycle
- [[q-save-data-outside-fragment--android--medium]] - Fragment state persistence

### Advanced (Harder)
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment state loss
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment architecture
