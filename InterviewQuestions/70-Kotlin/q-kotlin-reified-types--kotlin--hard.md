---
id: 20251012-12271111150
title: "Kotlin Reified Types / Reified типы в Kotlin"
aliases: [Kotlin Reified Types, Reified типы в Kotlin]
topic: kotlin
subtopics: [generics, type-system]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-jit-compilation-definition--programming-languages--medium, q-extensions-in-java--programming-languages--medium, q-coroutinescope-vs-supervisorscope--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - reified
  - generics
  - type-parameters
  - inline
  - difficulty/hard
---
# Reified Type Parameters

**English**: Explain reified type parameters. Implement type-safe builders and factories using reified. What are the limitations?

**Russian**: Объясните reified type parameters. Реализуйте type-safe builders и factories используя reified. Каковы ограничения?

## Answer (EN)

**Reified type parameters** in Kotlin, used with `inline` functions, preserve generic type information at runtime, which is normally lost due to Java's type erasure. This allows for runtime type checks (`is T`), casting (`as T`), and accessing the `T::class.java` of a generic type `T`.

**Use cases:**
- Type-safe JSON parsing (e.g., `gson.fromJson<User>(json)`)
- Creating generic factories for Android components (e.g., `newFragment<MyFragment>()`)
- Type-safe builders and DSLs

**Limitations:**
- Can only be used on `inline` functions.
- Cannot be used for class or property type parameters.
- Cannot be used to create new instances of `T` directly (e.g., `T()`).

## Ответ (RU)

**Reified параметры типа** в Kotlin, используемые с `inline` функциями, сохраняют информацию о generic типе во время выполнения, которая обычно теряется из-за стирания типов в Java. Это позволяет выполнять проверки типов во время выполнения (`is T`), приведения типов (`as T`) и получать доступ к `T::class.java` для generic типа `T`.

### Проблема: Стирание типов (Type Erasure)

```kotlin
// Не работает - тип стирается во время выполнения
fun <T> isInstance(value: Any): Boolean {
    return value is T  //  Невозможно проверить тип T
}

// Обходной путь: передать класс явно
fun <T> isInstance(value: Any, clazz: Class<T>): Boolean {
    return clazz.isInstance(value)  //  Работает, но многословно
}
```

### Решение: Reified

```kotlin
// Reified - тип доступен во время выполнения
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  //  Работает!
}

// Использование
isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false
```

### Безопасный для типов парсинг JSON

```kotlin
inline fun <reified T> String.parseJson(): T {
    return Json.decodeFromString<T>(this)
}

// Использование
val user: User = jsonString.parseJson()
val users: List<User> = jsonString.parseJson()
```

### Создание Fragment/Activity

```kotlin
inline fun <reified T : Fragment> newFragment(args: Bundle? = null): T {
    return T::class.java.newInstance().apply {
        arguments = args
    }
}

// Использование
val fragment = newFragment<UserFragment>()

// Безопасный для типов Intent
inline fun <reified T : Activity> Context.startActivity(extras: Bundle? = null) {
    val intent = Intent(this, T::class.java).apply {
        extras?.let { putExtras(it) }
    }
    startActivity(intent)
}

// Использование
context.startActivity<MainActivity>()
```

### Фабрика ViewModel

```kotlin
inline fun <reified VM : ViewModel> Fragment.viewModels(
    noinline factoryProducer: (() -> ViewModelProvider.Factory)? = null
): Lazy<VM> {
    return ViewModelLazy(
        VM::class,
        { viewModelStore },
        factoryProducer ?: { defaultViewModelProviderFactory }
    )
}

// Использование
class MyFragment : Fragment() {
    val viewModel: MyViewModel by viewModels()
}
```

### Ограничения

1.  **Должна быть inline функция**
2.  **Нельзя использовать в параметрах типа класса**
3.  **Нельзя передать в не-inline функции**
4.  **Увеличивает размер байт-кода** (из-за встраивания)
5.  **Нельзя создать экземпляр** без рефлексии

```kotlin
//  ЗАПРЕЩЕНО
class Container<reified T>  // Нельзя использовать в классе

fun <reified T> create(): T = T()  // Нельзя создать экземпляр

inline fun <reified T> process() {
    nonInlineFunction<T>()  // Нельзя передать в не-inline функцию
}
```

## Related Questions

- [[q-jit-compilation-definition--programming-languages--medium]]
- [[q-extensions-in-java--programming-languages--medium]]
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
