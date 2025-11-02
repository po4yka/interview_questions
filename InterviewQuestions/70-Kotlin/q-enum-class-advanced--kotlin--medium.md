---
id: kotlin-231
title: "Advanced Enum Class Features in Kotlin / Продвинутые возможности enum классов"
aliases: ["Advanced Enum Features", "Продвинутые возможности enum"]
topic: kotlin
subtopics: [classes, enums, kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-data-class-detailed--kotlin--medium, q-kotlin-enum-classes--kotlin--easy, q-sealed-class-sealed-interface--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [advanced-enums, classes, difficulty/medium, enums, kotlin, kotlin-features]
sources: [https://kotlinlang.org/docs/enum-classes.html]
date created: Sunday, October 12th 2025, 1:58:08 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Вопрос (RU)
> Какие продвинутые возможности есть у enum классов в Kotlin?

# Question (EN)
> What advanced features do enum classes have in Kotlin?

---

## Ответ (RU)

**Теория продвинутых enum:**
Kotlin enum классы поддерживают множество продвинутых возможностей: параметры, методы, интерфейсы, абстрактные методы, companion object, property delegation. Enum может реализовывать интерфейсы, иметь абстрактные методы для разной реализации в каждом enum значении, предоставлять общие методы и свойства.

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

**Реализация интерфейсов:**
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

**Использование when с enum:**
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

---

## Answer (EN)

**Advanced Enum Theory:**
Kotlin enum classes support many advanced features: parameters, methods, interfaces, abstract methods, companion object, property delegation. Enum can implement interfaces, have abstract methods for different implementations in each enum value, provide common methods and properties.

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

**Interface Implementation:**
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

**Using when with Enum:**
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

- When to use enum vs sealed class?
- How to use enums with type-safe serialization?
- Enum performance considerations?

## References

- [[c-oop-fundamentals]]
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
