---
id: kotlin-178
title: Nothing Instances / Экземпляры Nothing
aliases:
- Bottom Type
- Nothing
- Nothing Type
topic: kotlin
subtopics:
- type-system
question_kind: theory
difficulty: easy
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-circuit-breaker-coroutines--kotlin--hard
- q-request-coalescing-deduplication--kotlin--hard
created: 2025-10-15
updated: 2025-11-09
tags:
- bottom-type
- difficulty/easy
- kotlin
- nothing
- type-system
anki_cards:
- slug: kotlin-178-0-en
  language: en
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - type-system
- slug: kotlin-178-0-ru
  language: ru
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - type-system
---
# Вопрос (RU)
> Сколько экземпляров имеет тип Nothing в Kotlin?

---

# Question (EN)
> How many instances does the Nothing type have in Kotlin?

## Ответ (RU)

**Nothing не имеет экземпляров.** Это необитаемый тип (uninhabited type), который невозможно проинстанцировать.

**Ключевые характеристики:**
- Nothing — тип, который не имеет значений
- Является подтипом всех типов (bottom type в теории типов)
- Используется для функций, которые никогда не возвращаются нормально
- Используется для выражений, которые никогда не завершаются
- Часто используется в функциях, которые всегда выбрасывают исключения или выполняются бесконечно

**Когда используется Nothing:**
- Функции, которые всегда выбрасывают исключения (`throw`, `error()`, `TODO()`) — они объявляют `Nothing` как возвращаемый тип, потому что не завершаются нормально
- Функции с бесконечными циклами
- Выражения, которые никогда не производят значение
- Как параметр типа для пустых коллекций

### Примеры Кода

**Функции, возвращающие Nothing (нормально не завершаются):**

```kotlin
// Функция всегда выбрасывает исключение - возвращает Nothing
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

// Функция с бесконечным циклом - возвращает Nothing
fun infiniteLoop(): Nothing {
    while (true) {
        println("Работаю вечно...")
        Thread.sleep(1000)
    }
}

// Встроенные функции, возвращающие Nothing
fun demonstrateBuiltIn() {
    TODO("Ещё не реализовано")  // TODO() всегда выбрасывает NotImplementedError, поэтому его тип Nothing
    error("Что-то пошло не так")  // error() всегда выбрасывает исключение, тип Nothing
}
```

**Nothing в иерархии типов:**

```kotlin
fun processValue(value: String?): Int {
    // Nothing - подтип Int, поэтому выражение компилируется
    val length: Int = value?.length ?: fail("Значение null")
    return length
}

fun getUser(id: Int): User {
    // Nothing - подтип User, поэтому elvis с error() допустим
    return findUser(id) ?: error("Пользователь не найден")
}

data class User(val id: Int, val name: String)

fun findUser(id: Int): User? = null // Заглушка поиска пользователя
```

**Nothing с when-выражениями:**

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
}

fun handleResult(result: Result): Int {
    return when (result) {
        is Result.Success -> result.value
        is Result.Error -> error(result.message)  // Возвращает Nothing, ветка не завершается нормально
    }
}
```

**Nothing в коллекциях:**

```kotlin
// Пустой список по умолчанию имеет тип List<Nothing>
val emptyList: List<Nothing> = emptyList()

// Благодаря тому, что Nothing - подтип всех типов, этот список можно присвоить переменным с более конкретными типами
val strings: List<String> = emptyList  // Работает
val numbers: List<Int> = emptyList     // Работает
val users: List<User> = emptyList      // Работает

// listOf() возвращает List<Nothing>, когда вызывается без аргументов
val empty = listOf()
```

**Nothing? (nullable Nothing):**

```kotlin
// Nothing? может содержать только null
val nothingNullable: Nothing? = null

// Это единственное допустимое значение для Nothing?
// val invalid: Nothing? = something  // Другие значения невозможны

// Можно явно объявить функцию, всегда возвращающую null, как Nothing?
fun alwaysNull(): Nothing? = null
```

**Nothing vs Unit:**

```kotlin
// Unit: Функция завершается нормально, но не возвращает полезного значения
fun printMessage(msg: String): Unit {
    println(msg)
    // Неявно возвращает Unit
}

// Nothing: Функция никогда не завершается нормально
fun failWithError(msg: String): Nothing {
    throw Exception(msg)
    // Никогда не возвращается
}

fun demonstrateDifference() {
    // Unit функция завершается
    printMessage("Hello")  // Печатает и продолжает
    println("После printMessage")

    // Nothing функция никогда не возвращается (нормально)
    // failWithError("Error")  // Выбросит исключение
    // println("После failWithError")  // Недостижимый код
}
```

**Вывод типов с Nothing:**

```kotlin
fun checkValue(value: Int?): Int {
    // Компилятор знает, что если value == null, fail() выбросит исключение (тип Nothing)
    // Поэтому тип результата выражения elvis - Int, а не Int?
    return value ?: fail("Значение не может быть null")
}

fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

**Практическое использование с TODO():**

```kotlin
interface UserRepository {
    fun getUser(id: Int): User
    fun saveUser(user: User)
    fun deleteUser(id: Int): Boolean
}

data class User(val id: Int, val name: String)

class UserRepositoryImpl : UserRepository {
    override fun getUser(id: Int): User {
        TODO("Реализовать запрос к БД")  // TODO() объявлен с типом Nothing: выполнение не продолжится нормально
    }

    override fun saveUser(user: User) {
        TODO("Реализовать операцию сохранения")
    }

    override fun deleteUser(id: Int): Boolean {
        TODO("Реализовать операцию удаления")
    }
}
```

## Краткая Версия
Nothing имеет **ноль экземпляров**. Это необитаемый тип (bottom type), который:
- Не может быть проинстанцирован
- Является подтипом всех типов
- Используется для функций и выражений, которые никогда не завершаются нормально (`throw`, `error()`, `TODO()` и т.п.)
- Используется в типовом выводе для пустых коллекций (`emptyList()` без явного типа возвращает `List<Nothing>`)

Nothing? может иметь только одно значение: `null`.

## Answer (EN)

**Nothing has no instances.** It is an uninhabited type (bottom type) that cannot be instantiated.

**Key characteristics:**
- Nothing is a type that has no values
- It is the subtype of all types (bottom type)
- Used to represent functions that never return normally
- Used to represent expressions that never complete normally
- Commonly used with functions that always throw exceptions or run infinite loops

**When Nothing is used:**
- Functions that always throw exceptions (`throw`, `error()`, `TODO()`) — they declare `Nothing` as the return type because they do not complete normally
- Functions with infinite loops
- Expressions that never produce a value
- As a type parameter for empty collections

### Code Examples

**Functions that return Nothing (do not complete normally):**

```kotlin
// Function that always throws - returns Nothing
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

// Function with infinite loop - returns Nothing
fun infiniteLoop(): Nothing {
    while (true) {
        println("Running forever...")
        Thread.sleep(1000)
    }
}

// Built-in functions that return Nothing
fun demonstrateBuiltIn() {
    TODO("Not implemented yet")  // TODO() always throws NotImplementedError, so its type is Nothing
    error("Something went wrong")  // error() always throws, type Nothing
}
```

**Nothing in type hierarchy:**

```kotlin
fun processValue(value: String?): Int {
    // Nothing is a subtype of Int, so this expression compiles
    val length: Int = value?.length ?: fail("Value is null")
    return length
}

fun getUser(id: Int): User {
    // Nothing is a subtype of User, so using error() in elvis is valid
    return findUser(id) ?: error("User not found")
}

data class User(val id: Int, val name: String)

fun findUser(id: Int): User? = null  // Stub for user lookup
```

**Nothing with when expressions:**

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Error(val message: String) : Result()
}

fun handleResult(result: Result): Int {
    return when (result) {
        is Result.Success -> result.value
        is Result.Error -> error(result.message)  // Returns Nothing, branch does not complete normally
    }
}
```

**Nothing in collections:**

```kotlin
// Empty list has type List<Nothing> by default
val emptyList: List<Nothing> = emptyList()

// Because Nothing is a subtype of all types, this list can be assigned to variables with more specific element types
val strings: List<String> = emptyList  // Works
val numbers: List<Int> = emptyList     // Works
val users: List<User> = emptyList      // Works

// listOf() returns List<Nothing> when called without arguments
val empty = listOf()
```

**Nothing? (nullable Nothing):**

```kotlin
// Nothing? can only hold null
val nothingNullable: Nothing? = null

// This is the only valid value for Nothing?
// val invalid: Nothing? = something  // No other value possible

// You can explicitly declare a function that always returns null as Nothing?
fun alwaysNull(): Nothing? = null
```

**Nothing vs Unit:**

```kotlin
// Unit: Function completes normally, returns no meaningful value
fun printMessage(msg: String): Unit {
    println(msg)
    // Implicitly returns Unit
}

// Nothing: Function never completes normally
fun failWithError(msg: String): Nothing {
    throw Exception(msg)
    // Never returns
}

fun demonstrateDifference() {
    // Unit function completes
    printMessage("Hello")  // Prints and continues
    println("After printMessage")

    // Nothing function never returns (normally)
    // failWithError("Error")  // Would throw and never reach next line
    // println("After failWithError")  // Unreachable code
}
```

**Type inference with Nothing:**

```kotlin
fun checkValue(value: Int?): Int {
    // Compiler knows that if value is null, fail() throws (type Nothing)
    // So the resulting type of the elvis expression is Int, not Int?
    return value ?: fail("Value cannot be null")
}

fun fail(message: String): Nothing {
    throw IllegalArgumentException(message)
}
```

**Practical usage with TODO():**

```kotlin
interface UserRepository {
    fun getUser(id: Int): User
    fun saveUser(user: User)
    fun deleteUser(id: Int): Boolean
}

data class User(val id: Int, val name: String)

class UserRepositoryImpl : UserRepository {
    override fun getUser(id: Int): User {
        TODO("Implement database query")  // TODO() has return type Nothing: execution does not continue normally
    }

    override fun saveUser(user: User) {
        TODO("Implement save operation")
    }

    override fun deleteUser(id: Int): Boolean {
        TODO("Implement delete operation")
    }
}
```

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого подхода от Java?
- Когда вы бы использовали Nothing на практике?
- Какие распространённые ошибки стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-circuit-breaker-coroutines--kotlin--hard]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-request-coalescing-deduplication--kotlin--hard]]

## Related Questions

- [[q-circuit-breaker-coroutines--kotlin--hard]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-request-coalescing-deduplication--kotlin--hard]]
