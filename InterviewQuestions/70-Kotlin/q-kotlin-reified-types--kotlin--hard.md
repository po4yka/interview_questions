---
id: kotlin-198
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
related: [c-kotlin, q-coroutinescope-vs-supervisorscope--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/hard, generics, inline, kotlin, reified, type-parameters]
date created: Friday, October 31st 2025, 6:32:17 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)

> Объясните `reified` type parameters. Реализуйте type-safe builders и factories, используя `reified`. Каковы ограничения?

# Question (EN)

> Explain reified type parameters. Implement type-safe builders and factories using reified. What are the limitations?

## Ответ (RU)

`reified` параметры типа в [[c-kotlin]] могут использоваться только в `inline` функциях (включая inline-аксессоры и inline extension properties).

Из-за встраивания (inlining) тело такой функции разворачивается в месте вызова, и конкретный аргумент типа становится известен внутри этого кода. Это не "отключает" стирание типов JVM глобально, но позволяет компилятору подставить реальный тип там, где он нужен в заинлайненном коде.

Это позволяет:
- Делать проверки типов с учётом аргумента типа: `value is T`.
- Делать безопасные приведения: `value as T` / `value as? T` (после проверки).
- Получать `KClass`/`Class` для аргумента типа: `T::class`, `T::class.java`.

Типичные use cases:
- Типобезопасные JSON-хелперы: `inline fun <reified T> String.fromJson(): T`.
- Обобщённые фабрики/билдеры: например, `inline fun <reified T> createWith(...)`, использующие `T::class`.
- Типобезопасные Android-хелперы: например, `inline fun <reified A : Activity> Context.startActivity(...)`.
- Утилиты рефлексии и DSL, которым нужен фактический аргумент типа.

### Проблема: Стирание Типов (Type Erasure)

```kotlin
// Не работает — тип T стёрт во время выполнения
fun <T> isInstance(value: Any): Boolean {
    return value is T  // Ошибка компиляции: Cannot check for instance of erased type
}

// Обходной путь без reified: явно передать Class/KClass
fun <T> isInstance(value: Any, clazz: Class<T>): Boolean {
    return clazz.isInstance(value)
}
```

### Решение: Reified

```kotlin
// Reified — конкретный тип доступен в заинлайненном коде
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  // Работает
}

// Использование
isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false
```

### Типобезопасный Парсинг JSON

```kotlin
inline fun <reified T> String.parseJson(): T {
    return Json.decodeFromString<T>(this)
}

// Использование
val user: User = jsonString.parseJson()
val users: List<User> = jsonString.parseJson()
```

(Здесь `Json.decodeFromString` подразумевает реализацию/библиотеку, умеющую работать с `reified` типами; конкретный JSON-движок опущен.)

### Типобезопасные Фабрики / Android-хелперы (упрощённо)

```kotlin
// Пример упрощённого фабричного метода для Fragment.
// На практике рекомендуется использовать newInstance()/конструкторы без логики
// и учитывать API-ограничения; этот пример иллюстративный.
inline fun <reified T : Fragment> newFragment(args: Bundle? = null): T {
    val fragment = T::class.java.newInstance() // Требует публичного no-arg конструктора; не рекомендуется в боевом коде
    return fragment.apply { arguments = args }
}

// Использование
val fragment = newFragment<UserFragment>()

// Типобезопасный helper для Intent
inline fun <reified T : Activity> Context.startActivity(extras: Bundle? = null) {
    val intent = Intent(this, T::class.java).apply {
        extras?.let { putExtras(it) }
    }
    startActivity(intent)
}

// Использование
context.startActivity<MainActivity>()
```

### Фабрика `ViewModel` (упрощённый пример)

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

1. `reified` можно объявить только у параметров типа `inline` функций (включая их inline-аксессоры/extension properties), а не у обычных функций.
2. Нельзя объявить `reified` параметр типа у класса/интерфейса/свойства.
3. Нельзя "передать reified как есть" в не-inline функцию: чтобы использовать тип дальше, нужно явно передать `T::class` / `T::class.java` или результат вычислений на их основе.
4. Чрезмерное использование `inline` + `reified` может привести к росту байткода и ухудшить читаемость.
5. Нельзя полагаться на `reified` для обхода ограничений стирания типов за пределами заинлайненного участка: вся "видимость" реального типа существует только в результирующем сгенерированном коде.
6. Нельзя просто написать `T()` без соответствующих ограничений: обычно для создания экземпляра требуется рефлексия, известный конструктор или переданный фабричный метод.

```kotlin
// ЗАПРЕЩЕНО / НЕВОЗМОЖНО
class Container<reified T> // Ошибка: Only type parameters of inline functions can be reified

fun <reified T> create(): T = T() // Ошибка: Cannot use 'T' as constructor; нет информации о конструкторе

inline fun <reified T> process() {
    // Нельзя ожидать, что не-inline функция "увидит" reified напрямую
    // нужно передавать, например, T::class в качестве аргумента
}
```

## Answer (EN)

In Kotlin, a type parameter can be marked as `reified` only in an `inline` function (including inline accessors and inline extension properties).

Because the function is inlined at call sites, the concrete type argument used at each call site becomes available in the function body. On the JVM this does not "turn off" Java's type erasure globally, but it lets the compiler substitute the real type where needed inside the inlined code.

This enables:
- Runtime type checks with the type argument: `value is T`.
- Safe casts using the type argument: `value as T` / `value as? T` (with proper checks).
- Accessing `KClass`/`Class` for the type argument: `T::class`, `T::class.java`.

Typical use cases:
- Type-safe JSON parsing helpers: `inline fun <reified T> String.fromJson(): T`.
- Generic factories/builders: e.g., `inline fun <reified T> createWith(...)` that use `T::class`.
- Type-safe Android helpers: e.g., `inline fun <reified A : Activity> Context.startActivity(...)`.
- Safer reflection utilities and DSLs that depend on the actual type argument.

### Problem: Type Erasure

```kotlin
// Does not work — T is erased at runtime
fun <T> isInstance(value: Any): Boolean {
    return value is T  // Compilation error: Cannot check for instance of erased type
}

// Workaround without reified: explicitly pass Class/KClass
fun <T> isInstance(value: Any, clazz: Class<T>): Boolean {
    return clazz.isInstance(value)
}
```

### Solution: Reified

```kotlin
// Reified — concrete type is available in inlined code
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  // Works
}

// Usage
isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false
```

### Type-safe JSON Parsing

```kotlin
inline fun <reified T> String.parseJson(): T {
    return Json.decodeFromString<T>(this)
}

// Usage
val user: User = jsonString.parseJson()
val users: List<User> = jsonString.parseJson()
```

(Here `Json.decodeFromString` stands for a JSON implementation that can leverage `reified` type information; the concrete library is omitted.)

### Type-safe Factories / Android Helpers (simplified)

```kotlin
// Simplified factory method for Fragment.
// In real code you should rely on recommended patterns (e.g., newInstance) and
// respect constructor/API constraints; this is illustrative only.
inline fun <reified T : Fragment> newFragment(args: Bundle? = null): T {
    val fragment = T::class.java.newInstance() // Requires public no-arg constructor; not recommended in production
    return fragment.apply { arguments = args }
}

// Usage
val fragment = newFragment<UserFragment>()

// Type-safe helper for Intent
inline fun <reified T : Activity> Context.startActivity(extras: Bundle? = null) {
    val intent = Intent(this, T::class.java).apply {
        extras?.let { putExtras(it) }
    }
    startActivity(intent)
}

// Usage
context.startActivity<MainActivity>()
```

### ViewModel Factory (simplified example)

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

// Usage
class MyFragment : Fragment() {
    val viewModel: MyViewModel by viewModels()
}
```

### Limitations

1. `reified` is allowed only on type parameters of `inline` functions (including their inline accessors/extension properties), not on regular non-inline functions.
2. You cannot declare `reified` type parameters on classes/interfaces/properties.
3. You cannot "export" a `reified` parameter directly to non-inline code; pass `T::class` / `T::class.java` or derived values instead.
4. Excessive use of `inline` + `reified` can increase bytecode size and hurt readability.
5. You cannot rely on `reified` to bypass type erasure beyond the inlined site: visibility of the actual type exists only in the resulting expanded code.
6. You generally cannot just call `T()` without proper constraints; you usually need reflection, a known constructor, or a provided factory.

```kotlin
// FORBIDDEN / IMPOSSIBLE
class Container<reified T> // Error: Only type parameters of inline functions can be reified

fun <reified T> create(): T = T() // Error: Cannot use 'T' as constructor; no constructor info

inline fun <reified T> process() {
    // Non-inline functions cannot "see" reified directly;
    // pass T::class (or similar) if you need the type elsewhere.
}
```

## Follow-ups

- What are the key differences between this and Java's handling of generics and type erasure?
- When would you use this in practice, and when is it overkill?
- What are common pitfalls (e.g., over-inlining, misuse in Android `Fragment`/`ViewModel` creation)?

## References

- https://kotlinlang.org/docs/inline-functions.html#reified-type-parameters

## Related Questions

- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
