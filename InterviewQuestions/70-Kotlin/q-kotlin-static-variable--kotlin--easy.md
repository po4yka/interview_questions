---
'---id': lang-093
title: Kotlin Static Variable / Статические переменные в Kotlin
aliases:
- Kotlin Static Variable
- Статические переменные в Kotlin
topic: kotlin
subtopics:
- companion-object
- jvm-interop
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-kotlin-features
- c-variable
- q-enum-class-advanced--kotlin--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- companion-object
- const
- difficulty/easy
- jvmstatic
- kotlin
- static
anki_cards:
- slug: q-kotlin-static-variable--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-static-variable--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Как сделать статическую переменную?

# Question (EN)
> How to create a static variable?

## Ответ (RU)

Kotlin **не имеет** ключевого слова `static`, но есть несколько эквивалентов:

**1. companion object** - Внутри класса (наиболее распространенный)

**2. Top-level объявления** - Вне класса

**3. @JvmField / @JvmStatic** - Java совместимость

**4. const val** - Константы времени компиляции

**5. object** - Синглтон

### 1. Companion Object - Наиболее Распространенный:

```kotlin
class User {
    companion object {
        // Статико-подобная переменная
        var userCount = 0

        // Статико-подобная константа
        const val MAX_AGE = 120

        // Статико-подобная функция
        fun createGuest(): User {
            return User("Guest")
        }
    }

    private val name: String

    constructor(name: String) {
        this.name = name
        userCount++  // Доступ как к статическому
    }
}

// Использование - как статическое
User.userCount = 0
println(User.MAX_AGE)
val guest = User.createGuest()
```

### 2. Top-level Объявления:

```kotlin
// Файл: Constants.kt

// Top-level константа - как статическая
const val API_URL = "https://api.example.com"

// Top-level переменная - как статическая
var requestCount = 0

// Top-level функция - как статическая
fun log(message: String) {
    println("[LOG] $message")
}

// Использование - прямой доступ
println(API_URL)
requestCount++
log("Привет")
```

### 3. @JvmField - Java-совместимое Поле:

```kotlin
class Config {
    companion object {
        // Kotlin доступ: Config.timeout
        // Java доступ: Config.timeout (public static field)
        @JvmField
        var timeout = 30
    }
}
```

### 4. @JvmStatic - Java-совместимый Метод:

```kotlin
class Calculator {
    companion object {
        @JvmStatic
        fun add(a: Int, b: Int) = a + b

        // Без @JvmStatic, Java нужно: Calculator.Companion.multiply(...)
        fun multiply(a: Int, b: Int) = a * b
    }
}

// Kotlin
Calculator.add(2, 3)
Calculator.multiply(2, 3)

// Java
Calculator.add(2, 3);  // Работает с @JvmStatic
Calculator.Companion.multiply(2, 3);  // Без @JvmStatic
```

### 5. Const Val - Константы Времени Компиляции:

```kotlin
class Constants {
    companion object {
        // Должны быть примитивы или String
        const val MAX_SIZE = 100
        const val APP_NAME = "MyApp"
        const val PI = 3.14159

        // Нельзя использовать const с вычисляемыми значениями
        // const val TIMESTAMP = System.currentTimeMillis()  // Ошибка

        // Используйте val вместо этого
        val TIMESTAMP = System.currentTimeMillis()
    }
}
```

### 6. Object - Синглтон Со Статико-подобным Доступом:

```kotlin
object DatabaseConfig {
    var host = "localhost"
    var port = 5432

    fun connect() {
        println("Подключение к $host:$port")
    }
}

// Использование - как статическое
DatabaseConfig.host = "192.168.1.1"
DatabaseConfig.connect()
```

### Java Interop (RU)

```kotlin
// Kotlin
class MyClass {
    companion object {
        const val CONST = "constant"
        @JvmField var field = "field"
        @JvmStatic fun method() = "method"
        fun regularMethod() = "regular"
    }
}
```

```java
// Java доступ
String constValue = MyClass.CONST;  // Прямой доступ
String fieldValue = MyClass.field;  // Прямой доступ с @JvmField
String methodValue = MyClass.method();  // Прямой доступ с @JvmStatic
String regular = MyClass.Companion.regularMethod();  // Через Companion
```

### Сравнение (RU)

| Метод | Расположение | Java совместимость | Время компиляции |
|-------|--------------|-------------------|-----------------|
| **companion object** | Внутри класса | Companion.field | Нет |
| **@JvmField** | companion object | Static field | Нет |
| **@JvmStatic** | companion object | Static method | Нет |
| **const val** | companion/top-level | Static final | Да |
| **Top-level** | Вне класса | Static | Нет |
| **object** | Автономный | Instance | Нет |

### Полный Пример (RU)

```kotlin
class User(val name: String) {
    companion object {
        // Статическая константа
        const val DEFAULT_ROLE = "user"

        // Статическая переменная
        private var nextId = 1

        // Статическая с @JvmField
        @JvmField
        var allowRegistration = true

        // Статическая с @JvmStatic
        @JvmStatic
        fun generateId(): Int {
            return nextId++
        }

        // Обычный член companion object
        fun createAdmin(name: String): User {
            return User(name)
        }
    }

    val id = generateId()
}

// Использование
println(User.DEFAULT_ROLE)  // "user"
User.allowRegistration = false
val id = User.generateId()
val admin = User.createAdmin("Алиса")
```

### Когда Использовать Каждый Метод (RU)

| Случай использования | Решение |
|---------------------|---------|
| Константы | `const val` или `val` в companion |
| Счетчики, состояние | `var` в companion object |
| Утилитарные функции | Top-level функция или companion object |
| Java совместимость | `@JvmField`, `@JvmStatic` |
| Синглтон | `object` |
| Фабричные методы | companion object |

### Резюме (RU)

- **Нет ключевого слова `static`** в Kotlin
- **companion object** - наиболее распространенный подход
- **Top-level** - для констант/функций уровня файла
- **@JvmField / @JvmStatic** - Java совместимость
- **const val** - константы времени компиляции
- **object** - паттерн синглтон

## Дополнительные Вопросы (RU)

- В чем ключевые отличия от Java-подхода со `static`?
- Когда вы бы использовали каждый из этих подходов на практике?
- Как избежать распространенных ошибок при использовании `companion object`, `const val` и `object`?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-structured-concurrency-patterns--kotlin--hard]]
- [[q-enum-class-advanced--kotlin--medium]]
- [[q-kotlin-java-data-types--kotlin--medium]]

## Answer (EN)

Kotlin **does not have** the `static` keyword, but there are several equivalents:

**1. companion object** - Inside class

**2. Top-level declarations** - Outside class

**3. @JvmField / @JvmStatic** - Java interop

**4. const val** - Compile-time constants

**5. object** - Singleton

**1. companion object - Most Common:**

```kotlin
class User {
    companion object {
        // Static-like variable
        var userCount = 0

        // Static-like constant
        const val MAX_AGE = 120

        // Static-like function
        fun createGuest(): User {
            return User("Guest")
        }
    }

    private val name: String

    constructor(name: String) {
        this.name = name
        userCount++  // Access like static
    }
}

// Usage - like static
User.userCount = 0
println(User.MAX_AGE)
val guest = User.createGuest()
```

**2. Top-level Declarations:**

```kotlin
// File: Constants.kt

// Top-level constant - like static
const val API_URL = "https://api.example.com"

// Top-level variable - like static
var requestCount = 0

// Top-level function - like static
fun log(message: String) {
    println("[LOG] $message")
}

// Usage - direct access
println(API_URL)
requestCount++
log("Hello")
```

**3. @JvmField - Java-compatible field:**

```kotlin
class Config {
    companion object {
        // Kotlin access: Config.timeout
        // Java access: Config.timeout (public static field)
        @JvmField
        var timeout = 30
    }
}
```

**4. @JvmStatic - Java-compatible method:**

```kotlin
class Calculator {
    companion object {
        @JvmStatic
        fun add(a: Int, b: Int) = a + b

        // Without @JvmStatic, Java needs: Calculator.Companion.multiply(...)
        fun multiply(a: Int, b: Int) = a * b
    }
}

// Kotlin
Calculator.add(2, 3)
Calculator.multiply(2, 3)

// Java
Calculator.add(2, 3);  // Works with @JvmStatic
Calculator.Companion.multiply(2, 3);  // Without @JvmStatic
```

**5. const val - Compile-time Constants:**

```kotlin
class Constants {
    companion object {
        // Must be primitive or String
        const val MAX_SIZE = 100
        const val APP_NAME = "MyApp"
        const val PI = 3.14159

        // Cannot use const with computed values
        // const val TIMESTAMP = System.currentTimeMillis()  // Error

        // Use val instead
        val TIMESTAMP = System.currentTimeMillis()
    }
}
```

**6. object - Singleton with static-like access:**

```kotlin
object DatabaseConfig {
    var host = "localhost"
    var port = 5432

    fun connect() {
        println("Connecting to $host:$port")
    }
}

// Usage - like static
DatabaseConfig.host = "192.168.1.1"
DatabaseConfig.connect()
```

**Java Interop:**

```kotlin
// Kotlin
class MyClass {
    companion object {
        const val CONST = "constant"
        @JvmField var field = "field"
        @JvmStatic fun method() = "method"
        fun regularMethod() = "regular"
    }
}
```

```java
// Java access
String constValue = MyClass.CONST;  // Direct
String fieldValue = MyClass.field;  // Direct with @JvmField
String methodValue = MyClass.method();  // Direct with @JvmStatic
String regular = MyClass.Companion.regularMethod();  // Through Companion
```

**Comparison:**

| Method | Location | Java Interop | Compile-time |
|--------|----------|--------------|--------------|
| **companion object** | Inside class | Companion.field | No |
| **@JvmField** | companion object | Static field | No |
| **@JvmStatic** | companion object | Static method | No |
| **const val** | companion/top-level | Static final | Yes |
| **Top-level** | Outside class | Static | No |
| **object** | Standalone | Instance | No |

**Complete Example:**

```kotlin
class User(val name: String) {
    companion object {
        // Static constant
        const val DEFAULT_ROLE = "user"

        // Static variable
        private var nextId = 1

        // Static with @JvmField
        @JvmField
        var allowRegistration = true

        // Static with @JvmStatic
        @JvmStatic
        fun generateId(): Int {
            return nextId++
        }

        // Regular companion object member
        fun createAdmin(name: String): User {
            return User(name)
        }
    }

    val id = generateId()
}

// Usage
println(User.DEFAULT_ROLE)  // "user"
User.allowRegistration = false
val id = User.generateId()
val admin = User.createAdmin("Alice")
```

**When to Use Each:**

| Use Case | Solution |
|----------|----------|
| Constants | `const val` or `val` in companion |
| Counters, state | `var` in companion object |
| Utility functions | Top-level function or companion object |
| Java interop | `@JvmField`, `@JvmStatic` |
| Singleton | `object` |
| Factory methods | companion object |

**Summary:**

- **No `static` keyword** in Kotlin
- **companion object** - most common approach
- **Top-level** - for file-level constants/functions
- **@JvmField / @JvmStatic** - Java interop
- **const val** - compile-time constants
- **object** - singleton pattern

## Follow-ups

- What are the key differences between this and Java?
- When would you use each of these approaches in practice?
- What are common pitfalls when using `companion object`, `const val`, and `object`?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-structured-concurrency-patterns--kotlin--hard]]
- [[q-enum-class-advanced--kotlin--medium]]
- [[q-kotlin-java-data-types--kotlin--medium]]
