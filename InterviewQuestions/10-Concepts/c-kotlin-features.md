---
id: concept-003
title: Kotlin Language Features / Особенности языка Kotlin
aliases: [Kotlin Features, Kotlin язык, Особенности Kotlin]
kind: concept
summary: Overview of key Kotlin language features that distinguish it from Java, including null safety, extension functions, coroutines, data classes, and more.
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [concept, kotlin, language-features, programming-languages]
date created: Wednesday, November 5th 2025, 6:30:35 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

**Kotlin** is a modern, statically-typed programming language that runs on the JVM (and compiles to JavaScript or native code). It was designed by JetBrains to address Java's limitations while maintaining 100% interoperability.

**Key Language Features**:

**1. Null Safety**:
- Nullable (`String?`) vs non-nullable (`String`) types enforced at compile time
- Safe call operator `?.`, Elvis operator `?:`, non-null assertion `!!`
- Eliminates most NullPointerExceptions at compile time

**2. Extension Functions**:
- Add methods to existing classes without inheritance
- `fun String.removeWhitespace(): String = this.replace(" ", "")`

**3. Data Classes**:
- Automatic `equals()`, `hashCode()`, `toString()`, `copy()` generation
- `data class User(val name: String, val age: Int)`

**4. Coroutines**:
- Built-in support for asynchronous, non-blocking programming
- `suspend` functions, structured concurrency, Flow API

**5. Smart Casts**:
- Automatic type casting after null or type checks
- `if (x is String) { x.length }` — no explicit cast needed

**6. Sealed Classes**:
- Restricted class hierarchies for exhaustive when expressions
- Compile-time guarantee that all cases are handled

**7. Concise Syntax**:
- Type inference: `val name = "John"` (infers String)
- Single-expression functions: `fun double(x: Int) = x * 2`
- Named and default parameters

**8. Functional Programming**:
- First-class functions, lambdas, higher-order functions
- Collection operators: `map`, `filter`, `reduce`, `fold`

**9. Property Delegates**:
- Delegate property implementation to another object
- `by lazy`, `by observable`, custom delegates

**10. Operator Overloading**:
- Define custom behavior for operators (+, -, *, etc.)
- `operator fun plus(other: Vector) = Vector(x + other.x, y + other.y)`

# Сводка (RU)

**Kotlin** — это современный статически типизированный язык программирования, работающий на JVM (и компилируемый в JavaScript или нативный код). Он был разработан JetBrains для устранения недостатков Java при сохранении 100% совместимости.

**Ключевые возможности языка**:

**1. Null Safety (безопасность от null)**:
- Nullable (`String?`) и non-nullable (`String`) типы проверяются на этапе компиляции
- Безопасный вызов `?.`, Elvis-оператор `?:`, ненулевое утверждение `!!`
- Устраняет большинство NullPointerException на этапе компиляции

**2. Функции-расширения**:
- Добавление методов к существующим классам без наследования
- `fun String.removeWhitespace(): String = this.replace(" ", "")`

**3. Data-классы**:
- Автоматическая генерация `equals()`, `hashCode()`, `toString()`, `copy()`
- `data class User(val name: String, val age: Int)`

**4. Корутины**:
- Встроенная поддержка асинхронного неблокирующего программирования
- `suspend`-функции, структурированная конкурентность, Flow API

**5. Умные касты (Smart Casts)**:
- Автоматическое приведение типов после проверки на null или тип
- `if (x is String) { x.length }` — явный каст не нужен

**6. Sealed-классы**:
- Ограниченные иерархии классов для исчерпывающих when-выражений
- Гарантия на этапе компиляции, что все случаи обработаны

**7. Лаконичный синтаксис**:
- Вывод типов: `val name = "John"` (выводит String)
- Однострочные функции: `fun double(x: Int) = x * 2`
- Именованные параметры и параметры по умолчанию

**8. Функциональное программирование**:
- Функции первого класса, лямбды, функции высшего порядка
- Операторы коллекций: `map`, `filter`, `reduce`, `fold`

**9. Делегаты свойств**:
- Делегирование реализации свойства другому объекту
- `by lazy`, `by observable`, пользовательские делегаты

**10. Перегрузка операторов**:
- Определение пользовательского поведения операторов (+, -, *, и т.д.)
- `operator fun plus(other: Vector) = Vector(x + other.x, y + other.y)`

## Use Cases / Trade-offs

**When to use Kotlin**:
- Android development: Official Google-recommended language since 2019
- Server-side development: Spring Boot, Ktor frameworks
- Multiplatform projects: Kotlin Multiplatform (KMM) for shared code
- Existing Java codebases: Gradual migration due to 100% interoperability

**Advantages**:
- **Conciseness**: 40% less boilerplate than Java
- **Safety**: Null safety eliminates NPEs, smart casts reduce ClassCastExceptions
- **Tooling**: Excellent IDE support (IntelliJ IDEA, Android Studio)
- **Modern features**: Coroutines for async, extension functions for API design

**Trade-offs**:
- **Learning curve**: Requires learning new concepts (coroutines, sealed classes, etc.)
- **Compilation speed**: Slightly slower than Java in some cases
- **Library ecosystem**: Most JVM libraries are Java-first
- **Team adoption**: May require team training and migration planning

## References

- [Kotlin Official Documentation](https://kotlinlang.org/docs/home.html)
- [Kotlin for Android Developers](https://developer.android.com/kotlin)
- [Kotlin Koans (Interactive Tutorial)](https://play.kotlinlang.org/koans/)
- [Effective Kotlin by Marcin Moskała](https://kt.academy/book/effectivekotlin)
