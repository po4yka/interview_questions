---
id: kotlin-233
title: "Inner vs Nested Classes in Kotlin / Внутренние и вложенные классы в Kotlin"
aliases: ["Inner vs Nested Classes", "Внутренние vs вложенные классы"]
topic: kotlin
subtopics: [classes, kotlin-features, scoping]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-initialization-order--kotlin--medium, q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [classes, difficulty/medium, inner-classes, kotlin, kotlin-features, nested-classes]
sources: [https://kotlinlang.org/docs/nested-classes.html]
---

# Вопрос (RU)
> В чём разница между внутренними (inner) и вложенными (nested) классами в Kotlin?

# Question (EN)
> What's the difference between inner and nested classes in Kotlin?

---

## Ответ (RU)

**Теория вложенных и внутренних классов:**
В Kotlin есть два типа классов внутри другого класса: вложенные (nested) и внутренние (inner). Nested класс не имеет доступа к членам внешнего класса. Inner класс имеет доступ к членам внешнего класса. Ключевое отличие: inner класс хранит ссылку на экземпляр внешнего класса.

**Основные различия:**
- **Nested класс**: Как static внутренний класс в Java - без доступа к внешнему классу
- **Inner класс**: Имеет доступ к членам внешнего класса, хранит ссылку на экземпляр
- **Память**: Inner класс увеличивает размер объекта из-за хранения ссылки на внешний класс

**Nested классы:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Вложенный класс - не имеет доступа к Outer
    class Nested {
        fun describe() = "Nested class"
        // ❌ нельзя получить outerValue здесь
    }
}

// Usage
val nested = Outer.Nested() // Можно создать без экземпляра Outer
```

**Inner классы:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Внутренний класс - имеет доступ к Outer
    inner class Inner {
        fun describe() = "Inner class, outerValue: ${outerValue}"
        // ✅ можно получить outerValue
    }
}

// Usage
val outer = Outer()
val inner = outer.Inner() // Нужен экземпляр Outer
```

**Явная ссылка на внешний класс:**
```kotlin
class Outer {
    val value = "Outer"

    inner class Inner {
        val value = "Inner"

        fun printValues() {
            println(value) // Inner
            println(this@Outer.value) // Outer
        }
    }
}
```

**Практическое применение:**
```kotlin
class ViewHolder(private val view: View) {
    private val data = "ViewHolder Data"

    // ✅ Nested класс для вспомогательных типов
    class Builder {
        fun create(activity: Activity): ViewHolder {
            return ViewHolder(activity.findViewById(R.id.view))
        }
    }

    // ✅ Inner класс для доступа к ViewHolder
    inner class Loader {
        fun loadContent() {
            println(data) // ✅ Доступ к data из ViewHolder
        }
    }
}

// Usage
val holder = ViewHolder.Builder().create(activity)
val loader = holder.Loader() // Нужен экземпляр holder
loader.loadContent()
```

**Избегание утечек памяти:**
```kotlin
class Activity {
    private val data = "Important data"

    // ❌ ПЛОХО: Inner класс держит ссылку на Activity
    inner class Callback {
        fun onComplete() {
            println(data) // Ссылка на Activity
        }
    }

    // ✅ ХОРОШО: Nested класс не держит ссылку
    class SafeCallback {
        fun onComplete(data: String) {
            println(data)
        }
    }
}
```

---

## Answer (EN)

**Nested vs Inner Class Theory:**
Kotlin has two types of classes inside another class: nested and inner. Nested class has no access to outer class members. Inner class has access to outer class members. Key difference: inner class holds reference to outer class instance.

**Key Differences:**
- **Nested class**: Like static inner class in Java - no access to outer class
- **Inner class**: Has access to outer class members, holds reference to instance
- **Memory**: Inner class increases object size due to holding reference to outer class

**Nested Classes:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Nested class - no access to Outer
    class Nested {
        fun describe() = "Nested class"
        // ❌ cannot access outerValue here
    }
}

// Usage
val nested = Outer.Nested() // Can create without Outer instance
```

**Inner Classes:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Inner class - has access to Outer
    inner class Inner {
        fun describe() = "Inner class, outerValue: ${outerValue}"
        // ✅ can access outerValue
    }
}

// Usage
val outer = Outer()
val inner = outer.Inner() // Need Outer instance
```

**Explicit Reference to Outer Class:**
```kotlin
class Outer {
    val value = "Outer"

    inner class Inner {
        val value = "Inner"

        fun printValues() {
            println(value) // Inner
            println(this@Outer.value) // Outer
        }
    }
}
```

**Practical Application:**
```kotlin
class ViewHolder(private val view: View) {
    private val data = "ViewHolder Data"

    // ✅ Nested class for helper types
    class Builder {
        fun create(activity: Activity): ViewHolder {
            return ViewHolder(activity.findViewById(R.id.view))
        }
    }

    // ✅ Inner class for access to ViewHolder
    inner class Loader {
        fun loadContent() {
            println(data) // ✅ Access to data from ViewHolder
        }
    }
}

// Usage
val holder = ViewHolder.Builder().create(activity)
val loader = holder.Loader() // Need holder instance
loader.loadContent()
```

**Avoiding Memory Leaks:**
```kotlin
class Activity {
    private val data = "Important data"

    // ❌ BAD: Inner class holds reference to Activity
    inner class Callback {
        fun onComplete() {
            println(data) // Reference to Activity
        }
    }

    // ✅ GOOD: Nested class doesn't hold reference
    class SafeCallback {
        fun onComplete(data: String) {
            println(data)
        }
    }
}
```

## Follow-ups

- When to use nested vs inner classes?
- How to avoid memory leaks with inner classes?
- Performance implications of inner classes?

## References

- [[c-oop-fundamentals]]
- https://kotlinlang.org/docs/nested-classes.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-class-initialization-order--kotlin--medium]] - Class initialization
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-data-class-detailed--kotlin--medium]] - Data classes

### Advanced (Harder)
- [[q-delegation-by-keyword--kotlin--medium]] - Class delegation
