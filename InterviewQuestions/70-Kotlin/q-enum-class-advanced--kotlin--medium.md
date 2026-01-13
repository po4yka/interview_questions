---
id: kotlin-231
title: Advanced Enum Class Features in Kotlin / Продвинутые возможности enum классов
aliases:
- Advanced Enum Features
- Продвинутые возможности enum
topic: kotlin
subtopics:
- enums
- kotlin-features
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-data-class-detailed--kotlin--medium
- q-kotlin-enum-classes--kotlin--easy
- q-sealed-class-sealed-interface--kotlin--medium
created: '2024-10-12'
updated: '2025-11-09'
tags:
- advanced-enums
- classes
- difficulty/medium
- enums
- kotlin
- kotlin-features
sources:
- https://kotlinlang.org/docs/enum-classes.html
anki_cards:
- slug: kotlin-231-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - enums
  - kotlin-features
- slug: kotlin-231-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - enums
  - kotlin-features
---
# Вопрос (RU)
> Какие продвинутые возможности есть у enum классов в Kotlin?

# Question (EN)
> What advanced features do enum classes have in Kotlin?

---

## Ответ (RU)

**Теория продвинутых enum:**
Kotlin enum классы поддерживают расширенные возможности: параметры, методы, реализацию интерфейсов, абстрактные методы, companion object. Enum может реализовывать интерфейсы, иметь абстрактные методы для разной реализации в каждом значении, предоставлять общие методы и свойства, а также переопределения для конкретных значений.

Дополнительно у каждого enum значения есть стандартные свойства и функции: `name`, `ordinal`, статические методы `values()` и `valueOf()`, а также `entries` (c 1.9+) для безопасного получения списка значений.

**Параметры enum значений:**
```kotlin
enum class Planet(val mass: Double, val radius: Double) {
    EARTH(5.97e24, 6371.0) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    },
    MARS(6.39e23, 3389.5) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    },
    JUPITER(1.898e27, 69911.0) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    };

    companion object {
        private const val G = 6.67300e-11
    }

    abstract fun surfaceGravity(): Double
}
```

**Реализация интерфейсов и переопределения в значениях:**
```kotlin
interface Clickable {
    fun click(): String
}

enum class ButtonState : Clickable {
    ENABLED {
        override fun click() = "Button clicked"
    },
    DISABLED {
        override fun click() = "Cannot click disabled button"
    },
    LOADING {
        override fun click() = "Button is loading, please wait"
    }
}
```

**Методы и свойства в enum:**
```kotlin
enum class HttpMethod(val requiresBody: Boolean = false) {
    GET(false),
    POST(true),
    PUT(true),
    DELETE(false);

    fun canHaveBody(): Boolean = requiresBody

    fun makeRequest(url: String, body: Any? = null): String {
        return if (requiresBody && body == null) {
            "ERROR: $this requires body"
        } else {
            "Sending $this to $url"
        }
    }
}
```

**Использование `when` с enum:**
```kotlin
enum class Status {
    LOADING, SUCCESS, ERROR
}

fun handleStatus(status: Status) {
    when (status) {
        Status.LOADING -> println("Loading...")
        Status.SUCCESS -> println("Success!")
        Status.ERROR -> println("Error occurred")
    }
}
```

**Companion object для утилитных функций:**
```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    companion object {
        fun fromString(name: String): Color? {
            return values().find { it.name.equals(name, ignoreCase = true) }
        }

        fun hasColor(name: String): Boolean {
            return fromString(name) != null
        }
    }
}

// Usage
val color = Color.fromString("red") // RED
val exists = Color.hasColor("purple") // false
```

## Дополнительные Вопросы (RU)

- Когда использовать `enum` vs `sealed class`?
- Как использовать `enum` с типобезопасной сериализацией?
- Какие особенности производительности у `enum`?

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/enum-classes.html

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-kotlin-enum-classes--kotlin--easy]] - Базовые enum классы

### Похожие (среднего уровня)
- [[q-sealed-class-sealed-interface--kotlin--medium]] - Sealed классы
- [[q-data-class-detailed--kotlin--medium]] - Data классы
- [[q-class-initialization-order--kotlin--medium]] - Порядок инициализации классов

### Продвинутые (сложнее)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified типы

---

## Answer (EN)

**Advanced Enum Theory:**
Kotlin enum classes support extended features: constructor parameters, methods, interface implementation, abstract methods, and companion objects. An enum can implement interfaces, define abstract methods with different implementations per enum constant, provide common methods and properties, and allow per-constant overrides.

Additionally, each enum constant has built-in properties and functions: `name`, `ordinal`, static-like `values()` and `valueOf()`, and `entries` (since 1.9+) for safely obtaining the list of constants.

**Enum Value Parameters:**
```kotlin
enum class Planet(val mass: Double, val radius: Double) {
    EARTH(5.97e24, 6371.0) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    },
    MARS(6.39e23, 3389.5) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    },
    JUPITER(1.898e27, 69911.0) {
        override fun surfaceGravity() = G * mass / (radius * radius)
    };

    companion object {
        private const val G = 6.67300e-11
    }

    abstract fun surfaceGravity(): Double
}
```

**Interface Implementation and Per-Constant Overrides:**
```kotlin
interface Clickable {
    fun click(): String
}

enum class ButtonState : Clickable {
    ENABLED {
        override fun click() = "Button clicked"
    },
    DISABLED {
        override fun click() = "Cannot click disabled button"
    },
    LOADING {
        override fun click() = "Button is loading, please wait"
    }
}
```

**Methods and Properties in Enum:**
```kotlin
enum class HttpMethod(val requiresBody: Boolean = false) {
    GET(false),
    POST(true),
    PUT(true),
    DELETE(false);

    fun canHaveBody(): Boolean = requiresBody

    fun makeRequest(url: String, body: Any? = null): String {
        return if (requiresBody && body == null) {
            "ERROR: $this requires body"
        } else {
            "Sending $this to $url"
        }
    }
}
```

**Using `when` with Enum:**
```kotlin
enum class Status {
    LOADING, SUCCESS, ERROR
}

fun handleStatus(status: Status) {
    when (status) {
        Status.LOADING -> println("Loading...")
        Status.SUCCESS -> println("Success!")
        Status.ERROR -> println("Error occurred")
    }
}
```

**Companion Object for Utility Functions:**
```kotlin
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);

    companion object {
        fun fromString(name: String): Color? {
            return values().find { it.name.equals(name, ignoreCase = true) }
        }

        fun hasColor(name: String): Boolean {
            return fromString(name) != null
        }
    }
}

// Usage
val color = Color.fromString("red") // RED
val exists = Color.hasColor("purple") // false
```

## Follow-ups

- When to use `enum` vs `sealed class`?
- How to use enums with type-safe serialization?
- Enum performance considerations?

## References

- [[c-kotlin]]
- https://kotlinlang.org/docs/enum-classes.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic enum classes

### Related (Medium)
- [[q-sealed-class-sealed-interface--kotlin--medium]] - Sealed classes
- [[q-data-class-detailed--kotlin--medium]] - Data classes
- [[q-class-initialization-order--kotlin--medium]] - Class initialization

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types
