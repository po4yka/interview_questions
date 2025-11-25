---
id: android-332
title: "How To Pass Parameters To A Fragment / Как передать параметры во Fragment"
aliases: [Pass Parameters to Fragment, Передача параметров во фрагмент]
topic: android
subtopics: [fragment]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-navigation, c-bundle, q-android-app-components--android--easy]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [android/fragment, difficulty/easy]

date created: Saturday, November 1st 2025, 1:31:08 pm
date modified: Tuesday, November 25th 2025, 8:53:59 pm
---

# Вопрос (RU)

> Как передать параметры во фрагмент?

# Question (EN)

> How to pass parameters to a `Fragment`?

---

## Ответ (RU)

Рекомендуемый и безопасный способ передачи параметров во фрагмент в Android — использование `Bundle` через свойство `arguments` фрагмента. Этот подход поддерживается системой Android и переживает изменения конфигурации (например, поворот экрана).

### Основные Принципы

1. **Фабричный метод (Factory Method)**
   Создайте статический метод `newInstance()` в `companion object`, который принимает параметры и возвращает экземпляр фрагмента с установленным `Bundle`.

2. **`Bundle` для примитивов и простых типов**
   Используйте `Bundle.putInt()`, `putString()`, `putBoolean()` и т.д. для передачи примитивных типов.

3. **`Parcelable` для сложных объектов**
   Для передачи пользовательских объектов используйте интерфейс `Parcelable` и аннотацию `@Parcelize`.

4. **Извлечение в `onCreate()`**
   Получайте аргументы в методе `onCreate()` через `requireArguments()` или `arguments?.let {}`.

См. также: [[c-android-navigation]], [[c-bundle]]

### Пример 1: Передача Примитивных Типов

```kotlin
class DetailsFragment : Fragment() {

    companion object {
        private const val ARG_ITEM_ID = "item_id"
        private const val ARG_ITEM_NAME = "item_name"

        // Фабричный метод создания фрагмента с аргументами
        fun newInstance(itemId: Int, itemName: String): DetailsFragment {
            return DetailsFragment().apply {
                arguments = Bundle().apply {
                    putInt(ARG_ITEM_ID, itemId)
                    putString(ARG_ITEM_NAME, itemName)
                }
            }
        }
    }

    private val itemId: Int by lazy {
        requireArguments().getInt(ARG_ITEM_ID)
    }

    private val itemName: String by lazy {
        requireArguments().getString(ARG_ITEM_NAME) ?: ""
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Параметры уже инициализированы через lazy-делегаты
    }
}

// Использование в Activity
val fragment = DetailsFragment.newInstance(
    itemId = 42,
    itemName = "Sample Item"
)
supportFragmentManager.beginTransaction()
    .replace(R.id.fragment_container, fragment)
    .commit()
```

### Пример 2: Передача Сложных Объектов Через `Parcelable`

```kotlin
// Data класс с Parcelable
@Parcelize
data class User(
    val id: Long,
    val name: String,
    val email: String
) : Parcelable

class ProfileFragment : Fragment() {

    companion object {
        private const val ARG_USER = "user"

        fun newInstance(user: User) = ProfileFragment().apply {
            arguments = Bundle().apply {
                putParcelable(ARG_USER, user)
            }
        }
    }

    private val user: User by lazy {
        // Безопасное извлечение Parcelable для разных версий API
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelable(ARG_USER, User::class.java)!!
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelable(ARG_USER)!!
        }
    }
}
```

### Пример 3: Использование `requireArguments()`

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

    // Ленивая инициализация через requireArguments()
    private val userId: Long by lazy {
        requireArguments().getLong(ARG_USER_ID)
    }

    private val userEmail: String by lazy {
        requireArguments().getString(ARG_EMAIL) ?: ""
    }
}
```

### Лучшие Практики

1. Всегда используйте `Bundle` и `arguments` — не передавайте данные через конструктор.
2. Создавайте фабричные методы (`newInstance`) в `companion object`.
3. Извлекайте аргументы в `onCreate()` или используйте lazy-делегаты.
4. Используйте константы для ключей `Bundle`.
5. Предпочитайте `Parcelable` вместо `Serializable` для лучшей производительности.
6. Никогда не передавайте данные через конструктор — они теряются при пересоздании.
7. Не используйте setter-методы для передачи обязательных параметров — это небезопасно при изменении конфигурации.

### Распространённые Ошибки

```kotlin
// Неправильно - использование конструктора
class WrongFragment(private val itemId: Int) : Fragment() {
    // Данные потеряются при повороте экрана
}

// Неправильно - использование setter-методов
class WrongFragment : Fragment() {
    private var itemId: Int = 0

    fun setItemId(id: Int) {
        this.itemId = id  // Потеряется при изменении конфигурации
    }
}

// Правильно - использование Bundle
class CorrectFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(itemId: Int) = CorrectFragment().apply {
            arguments = Bundle().apply {
                putInt(ARG_ITEM_ID, itemId)
            }
        }
    }

    private val itemId by lazy {
        requireArguments().getInt(ARG_ITEM_ID)
    }
}
```

## Answer (EN)

The recommended and safe way to pass parameters to a `Fragment` in Android is using `Bundle` with the fragment's `arguments` property. This approach is supported by the Android system and survives configuration changes.

### Basic Principles

1. **Factory Method Pattern**
   Create a static `newInstance()` method in the companion object that accepts parameters and returns a fragment instance with `Bundle` set.

2. **`Bundle` for Primitives**
   Use `Bundle.putInt()`, `putString()`, `putBoolean()`, etc., for primitive types.

3. **`Parcelable` for Complex Objects**
   For custom objects, use the `Parcelable` interface with `@Parcelize` annotation.

4. **Extract in `onCreate()`**
   Retrieve arguments in `onCreate()` using `requireArguments()` or `arguments?.let {}`.

See also: [[c-android-navigation]], [[c-bundle]]

### Example 1: Passing Primitive Types

```kotlin
class DetailsFragment : Fragment() {

    companion object {
        private const val ARG_ITEM_ID = "item_id"
        private const val ARG_ITEM_NAME = "item_name"

        // Factory method to create fragment with arguments
        fun newInstance(itemId: Int, itemName: String): DetailsFragment {
            return DetailsFragment().apply {
                arguments = Bundle().apply {
                    putInt(ARG_ITEM_ID, itemId)
                    putString(ARG_ITEM_NAME, itemName)
                }
            }
        }
    }

    private val itemId: Int by lazy {
        requireArguments().getInt(ARG_ITEM_ID)
    }

    private val itemName: String by lazy {
        requireArguments().getString(ARG_ITEM_NAME) ?: ""
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Arguments already initialized via lazy delegates
    }
}

// Usage in Activity
val fragment = DetailsFragment.newInstance(
    itemId = 42,
    itemName = "Sample Item"
)
supportFragmentManager.beginTransaction()
    .replace(R.id.fragment_container, fragment)
    .commit()
```

### Example 2: Passing Complex Objects via `Parcelable`

```kotlin
// Data class with Parcelable
@Parcelize
data class User(
    val id: Long,
    val name: String,
    val email: String
) : Parcelable

class ProfileFragment : Fragment() {

    companion object {
        private const val ARG_USER = "user"

        fun newInstance(user: User) = ProfileFragment().apply {
            arguments = Bundle().apply {
                putParcelable(ARG_USER, user)
            }
        }
    }

    private val user: User by lazy {
        // Safe Parcelable extraction for different API levels
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelable(ARG_USER, User::class.java)!!
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelable(ARG_USER)!!
        }
    }
}
```

### Example 3: Using `requireArguments()`

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

    // Lazy initialization using requireArguments()
    private val userId: Long by lazy {
        requireArguments().getLong(ARG_USER_ID)
    }

    private val userEmail: String by lazy {
        requireArguments().getString(ARG_EMAIL) ?: ""
    }
}
```

### Best Practices

1. Always use `Bundle` and `arguments` — never pass data via constructor.
2. Create factory methods (`newInstance`) in the companion object.
3. Extract arguments in `onCreate()` or use lazy delegates.
4. Use constants for `Bundle` keys.
5. Prefer `Parcelable` over `Serializable` for better performance.
6. Never pass data via constructor — values are lost on configuration change.
7. Do not use setter methods for required arguments — unsafe for configuration changes.

### Common Mistakes

```kotlin
// WRONG - Using constructor
class WrongFragment(private val itemId: Int) : Fragment() {
    // Data will be lost on screen rotation
}

// WRONG - Using setter methods
class WrongFragment : Fragment() {
    private var itemId: Int = 0

    fun setItemId(id: Int) {
        this.itemId = id  // Lost on configuration change
    }
}

// CORRECT - Using Bundle
class CorrectFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(itemId: Int) = CorrectFragment().apply {
            arguments = Bundle().apply {
                putInt(ARG_ITEM_ID, itemId)
            }
        }
    }

    private val itemId by lazy {
        requireArguments().getInt(ARG_ITEM_ID)
    }
}
```

---

## Дополнительные Вопросы (RU)

1. Что происходит с аргументами фрагмента при изменении конфигурации?
2. Почему `Parcelable` предпочтительнее `Serializable` в Android?
3. В чем разница между `arguments` и `requireArguments()`?
4. Можно ли передавать lambda-функции или callback-и через `Bundle`?
5. Как обрабатывать необязательные и обязательные аргументы фрагмента?

## Follow-ups

1. What happens to fragment arguments during configuration changes?
2. Why is `Parcelable` preferred over `Serializable` for Android?
3. What is the difference between `arguments` and `requireArguments()`?
4. Can you pass lambda functions or callbacks via `Bundle`?
5. How do you handle optional vs required fragment arguments?

## Ссылки (RU)

- [Android Developer Guide: Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Guide: `Parcelable`](https://developer.android.com/reference/android/os/Parcelable)

## References

- [Android Developer Guide: Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Guide: `Parcelable`](https://developer.android.com/reference/android/os/Parcelable)

## Связанные Вопросы (RU)

### База (проще)
- [[q-android-app-components--android--easy]]

### Того Же Уровня Сложности

### Продвинутые (сложнее)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]

### Related (Same Level)

### Advanced (Harder)
