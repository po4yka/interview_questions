---
id: kotlin-233
title: "Inner vs Nested Classes in Kotlin / Внутренние и вложенные классы в Kotlin"
aliases: ["Inner vs Nested Classes", "Внутренние vs вложенные классы"]
topic: kotlin
subtopics: [classes, scoping]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-class-initialization-order--kotlin--medium, q-data-class-detailed--kotlin--medium, q-inheritance-open-final--kotlin--medium]
created: "2025-10-12"
updated: "2025-11-11"
tags: [difficulty/medium, kotlin/classes, kotlin/inner-classes, kotlin/nested-classes]
sources: ["https://kotlinlang.org/docs/nested-classes.html"]

---
# Вопрос (RU)
> В чём разница между внутренними (inner) и вложенными (nested) классами в Kotlin?

# Question (EN)
> What's the difference between inner and nested classes in Kotlin?

---

## Ответ (RU)

**Теория вложенных и внутренних классов:**
В Kotlin есть два типа классов внутри другого класса: вложенные (nested) и внутренние (inner).
По умолчанию класс, объявленный внутри другого, является вложенным (nested) и не имеет доступа к экземпляру внешнего класса. Внутренний (inner) класс явно помечается ключевым словом `inner` и имеет доступ к членам экземпляра внешнего класса. Ключевое отличие: inner класс хранит ссылку на экземпляр внешнего класса.

**Основные различия:**
- **Nested класс**: Как `static` вложенный класс в Java — не имеет доступа к экземпляру внешнего класса.
- **Inner класс**: Имеет доступ к членам экземпляра внешнего класса, хранит ссылку на его экземпляр.
- **Память**: Ссылка на внешний класс хранится в экземпляре inner класса (увеличивает размер объекта inner класса, но не объекта внешнего класса).

**Nested классы:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Вложенный класс (по умолчанию) - не имеет доступа к экземпляру Outer
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

    // ✅ Внутренний класс - имеет доступ к экземпляру Outer
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

    // ✅ Inner класс для доступа к членам ViewHolder
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

    // ✅ ХОРОШО: Nested класс не держит ссылку на Activity
    class SafeCallback {
        fun onComplete(data: String) {
            println(data)
        }
    }
}
```

## Дополнительные Вопросы (RU)

- Когда использовать вложенные (nested) vs внутренние (inner) классы?
- Как избежать утечек памяти при использовании inner классов?
- Каковы последствия для производительности при использовании inner классов?

## Ссылки (RU)

- [[c-kotlin]]
- https://kotlinlang.org/docs/nested-classes.html

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-kotlin-enum-classes--kotlin--easy]] - Базовые классы

### Связанные (средней сложности)
- [[q-class-initialization-order--kotlin--medium]] - Порядок инициализации классов
- [[q-inheritance-open-final--kotlin--medium]] - Наследование
- [[q-data-class-detailed--kotlin--medium]] - Data-классы

### Продвинутые (сложнее)
- [[q-delegation-by-keyword--kotlin--medium]] - Делегирование классов

---

## Answer (EN)

**Nested vs Inner Class Theory:**
Kotlin has two types of classes inside another class: nested and inner.
By default, a class declared inside another is a nested class and has no access to the outer class instance. An inner class is explicitly marked with the `inner` keyword and has access to the outer class instance members. Key difference: an inner class holds a reference to an instance of the outer class.

**Key Differences:**
- **Nested class**: Like a `static` nested class in Java — no access to the outer class instance.
- **Inner class**: Has access to outer class instance members, holds a reference to its instance.
- **Memory**: The reference to the outer class is stored in the inner class instance (increasing the size of the inner object, not the outer object).

**Nested Classes:**
```kotlin
class Outer {
    private val outerValue = "Outer"

    // ✅ Nested class (default) - no access to Outer instance
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

    // ✅ Inner class - has access to Outer instance
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

    // ✅ Inner class for access to ViewHolder members
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

    // ✅ GOOD: Nested class doesn't hold reference to Activity
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

- [[c-kotlin]]
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
