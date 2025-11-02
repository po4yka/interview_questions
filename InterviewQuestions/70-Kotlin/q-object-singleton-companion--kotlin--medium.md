---
id: kotlin-234
title: "Object, Companion Object, and Singleton Pattern / object, companion object и паттерн Singleton"
aliases: ["Object Singleton Companion", "Объект Singleton Companion"]
topic: kotlin
subtopics: [companion-object, object-keyword, singleton-pattern]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-initialization-order--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-inner-nested-classes--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [companion-object, difficulty/medium, kotlin, kotlin-features, object-keyword, singleton-pattern]
sources: [https://kotlinlang.org/docs/object-declarations.html]
date created: Saturday, November 1st 2025, 12:42:09 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Вопрос (RU)
> Как работают object, companion object и паттерн singleton в Kotlin?

# Question (EN)
> How do object, companion object, and singleton pattern work in Kotlin?

---

## Ответ (RU)

**Теория object и companion object:**
В Kotlin `object` ключевое слово создаёт singleton - единственный экземпляр класса, инициализируемый лениво при первом доступе. `companion object` - специальный `object` внутри класса, доступ к которому идёт через имя класса. Используются для реализации singleton-паттерна, утилитных функций и factory методов.

**Основные концепции:**
- **object**: Создаёт singleton объект
- **companion object**: Объект внутри класса, доступный через имя класса
- **Ленивая инициализация**: Инициализируется при первом доступе
- **Thread-safe**: Автоматически потокобезопасный

**Object Singleton:**
```kotlin
// ✅ object создаёт singleton
object DatabaseManager {
    private val connection = "Connected"

    fun connect() {
        println(connection)
    }

    fun disconnect() {
        println("Disconnected")
    }
}

// Usage: обращение как к единственному экземпляру
DatabaseManager.connect() // Connected
DatabaseManager.disconnect() // Disconnected

// ❌ не может создать экземпляр
// val db = DatabaseManager() // Ошибка!
```

**Companion Object:**
```kotlin
class MyClass {
    private val instanceData = "Instance data"

    // ✅ companion object доступен через имя класса
    companion object {
        private const val CONSTANT = "Constant value"

        fun factory(): MyClass {
            return MyClass()
        }
    }
}

// Usage
val instance = MyClass.factory() // Доступ через имя класса
```

**Companion с интерфейсами:**
```kotlin
interface Factory {
    fun create(): Any
}

class User {
    companion object : Factory {
        override fun create() = User()
    }
}

// ✅ Можно использовать имя companion
val user = User.create() // Через интерфейс Factory
```

**Практическое применение:**
```kotlin
// ✅ Singleton для настроек
object SettingsManager {
    private var theme: String = "light"

    fun setTheme(theme: String) {
        this.theme = theme
    }

    fun getTheme(): String = theme
}

// ✅ Factory методы в companion
class User private constructor(val name: String) {
    companion object {
        fun create(name: String): User {
            return User(name)
        }

        fun createAdmin(): User {
            return User("Admin")
        }
    }
}
```

**Избегание проблем singleton:**
```kotlin
// ❌ ПЛОХО: Глобальное состояние
object GlobalState {
    var counter = 0
}

// ✅ ХОРОШО: Инкапсулированное состояние
object Logger {
    private val logs = mutableListOf<String>()

    fun log(message: String) {
        logs.add(message)
    }

    fun getLogs(): List<String> = logs.toList()
}
```

---

## Answer (EN)

**Object and Companion Object Theory:**
In Kotlin, the `object` keyword creates a singleton - a single instance of a class, initialized lazily on first access. `companion object` is a special `object` inside a class, accessible through the class name. Used for implementing singleton pattern, utility functions, and factory methods.

**Core Concepts:**
- **object**: Creates a singleton object
- **companion object**: Object inside class, accessible through class name
- **Lazy initialization**: Initialized on first access
- **Thread-safe**: Automatically thread-safe

**Object Singleton:**
```kotlin
// ✅ object creates singleton
object DatabaseManager {
    private val connection = "Connected"

    fun connect() {
        println(connection)
    }

    fun disconnect() {
        println("Disconnected")
    }
}

// Usage: access as single instance
DatabaseManager.connect() // Connected
DatabaseManager.disconnect() // Disconnected

// ❌ cannot create instance
// val db = DatabaseManager() // Error!
```

**Companion Object:**
```kotlin
class MyClass {
    private val instanceData = "Instance data"

    // ✅ companion object accessible through class name
    companion object {
        private const val CONSTANT = "Constant value"

        fun factory(): MyClass {
            return MyClass()
        }
    }
}

// Usage
val instance = MyClass.factory() // Access through class name
```

**Companion with Interfaces:**
```kotlin
interface Factory {
    fun create(): Any
}

class User {
    companion object : Factory {
        override fun create() = User()
    }
}

// ✅ Can use companion name
val user = User.create() // Through Factory interface
```

**Practical Application:**
```kotlin
// ✅ Singleton for settings
object SettingsManager {
    private var theme: String = "light"

    fun setTheme(theme: String) {
        this.theme = theme
    }

    fun getTheme(): String = theme
}

// ✅ Factory methods in companion
class User private constructor(val name: String) {
    companion object {
        fun create(name: String): User {
            return User(name)
        }

        fun createAdmin(): User {
            return User("Admin")
        }
    }
}
```

**Avoiding Singleton Problems:**
```kotlin
// ❌ BAD: Global state
object GlobalState {
    var counter = 0
}

// ✅ GOOD: Encapsulated state
object Logger {
    private val logs = mutableListOf<String>()

    fun log(message: String) {
        logs.add(message)
    }

    fun getLogs(): List<String> = logs.toList()
}
```

## Follow-ups

- When to use object vs class with private constructor?
- How to test code with object singletons?
- Performance implications of lazy initialization?

## References

- https://kotlinlang.org/docs/object-declarations.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-class-initialization-order--kotlin--medium]] - Class initialization
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-inner-nested-classes--kotlin--medium]] - Inner/Nested classes

### Advanced (Harder)
- [[q-delegation-by-keyword--kotlin--medium]] - Class delegation
