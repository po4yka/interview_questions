---
id: 20251012-1227111171
title: "Prototype Pattern / Паттерн Прототип"
aliases: ["Prototype Pattern", "Паттерн Прототип"]
topic: cs
subtopics: [creational-patterns, design-patterns, object-cloning]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-builder-pattern--design-patterns--medium, q-factory-method-pattern--design-patterns--medium, q-singleton-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [creational-patterns, design-patterns, difficulty/medium, object-cloning, prototype]
sources: [https://refactoring.guru/design-patterns/prototype]
date created: Monday, October 6th 2025, 7:33:01 am
date modified: Sunday, October 26th 2025, 1:37:11 pm
---

# Вопрос (RU)
> Что такое паттерн Prototype? Когда его использовать и как он работает?

# Question (EN)
> What is the Prototype pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Prototype Pattern:**
Prototype - creational pattern, creates objects by copying existing ones. Hidden complexity of instantiation from client. Existing object acts as prototype contains state. Solves: determining specific object type at runtime, instantiating dynamically loaded classes, avoiding factory hierarchy parallel to product hierarchy, expensive object creation vs cloning.

**Определение:**

*Теория:* Prototype design pattern enables creating new objects by copying existing object. Allows hiding complexity of making new instances from client. Prototype object returns copy of itself. Client doesn't need to know concrete types, works with prototype interface. Solution для: runtime object creation, dynamic loading, avoiding tight coupling to concrete classes.

```kotlin
// ✅ Prototype interface
interface GameCharacterPrototype {
    fun clone(): GameCharacterPrototype
}

// ✅ Concrete prototype
data class GameCharacter(
    val name: String,
    val weapon: String,
    val level: Int
) : GameCharacterPrototype {
    override fun clone(): GameCharacterPrototype {
        return copy()  // Data class copy()
    }
}

// ✅ Usage
fun main() {
    val original = GameCharacter("Knight", "Sword", 5)
    val cloned = original.clone() as GameCharacter
}
```

**Проблемы, которые решает:**

**1. Dynamic Object Creation:**
*Теория:* Creating objects directly within class commits to particular objects at compile-time. Impossible to specify which objects to create at run-time. Prototype pattern solves by: cloning existing objects, determining type at runtime, not compile-time.

```kotlin
// ❌ Compile-time commitment
class GameManager {
    fun createCharacter(type: String): Character {
        return when(type) {
            "warrior" -> Warrior("Default", 1)
            "mage" -> Mage("Default", 1)
            else -> throw IllegalArgumentException()
        }
    }
}

// ✅ Runtime flexibility with prototypes
class GameManager {
    private val prototypes = mutableMapOf<String, GameCharacterPrototype>()

    fun registerPrototype(name: String, prototype: GameCharacterPrototype) {
        prototypes[name] = prototype
    }

    fun createCharacter(type: String): GameCharacterPrototype {
        return prototypes[type]?.clone() ?: throw IllegalArgumentException()
    }
}
```

**2. Avoiding Factory Hierarchy:**
*Теория:* Building factory hierarchy parallel to product hierarchy is verbose and complex. Prototype eliminates need for factory classes by using cloning. Reduces classes, simplifies design, allows adding/removing prototypes at runtime.

**3. Expensive Object Creation:**
*Теория:* When object creation expensive compared to cloning, use prototypes. Clone pre-instantiated objects instead creating new ones. Examples: database connections, complex configurations, initialized objects with heavy setup.

```kotlin
// ✅ Expensive object creation
class ExpensiveObject {
    init {
        // Heavy initialization
        Thread.sleep(1000)  // Simulate expensive operation
    }
}

// ✅ Prototype avoids re-initialization
val prototype = ExpensiveObject()
val clone = prototype.clone()  // Fast copy, no initialization
```

**Когда использовать:**

✅ **Use Prototype when:**
- Classes to instantiate specified at runtime
- Want avoid factory hierarchy parallel to product hierarchy
- Instances have few different state combinations
- Object creation expensive compared to cloning
- Concrete classes unknown until runtime
- Need configure and clone predefined objects
- Creating similar objects with minor variations

❌ **Don't use Prototype when:**
- Classes have only few instances (no benefit)
- Instances differ significantly (cloning wasteful)
- Cloning more expensive than creating new
- Complex object graphs with circular references

**Глубокое vs Поверхностное клонирование:**

*Теория:* Shallow clone - copies object but shares references to nested objects. Deep clone - creates new objects for all nested structures. Challenge: implementing deep clone correctly, handling circular references. Solution: clone all nested objects recursively, maintain visited objects map.

```kotlin
// ✅ Shallow clone (shared references)
data class CharacterSettings(val config: Map<String, String>)
data class GameCharacter(val settings: CharacterSettings)

val original = GameCharacter(CharacterSettings(mapOf("level" to "5")))
val shallowCopy = original.copy()
shallowCopy.settings.config["level"] = "10"
// ❌ original.settings now also "10" - shared reference!

// ✅ Deep clone
interface DeepCloneable<T> {
    fun deepClone(): T
}

class DeepCloneableCharacter(val settings: CharacterSettings) : DeepCloneable<DeepCloneableCharacter> {
    override fun deepClone(): DeepCloneableCharacter {
        return DeepCloneableCharacter(
            CharacterSettings(settings.config.toMap())  // New map
        )
    }
}
```

**Преимущества:**
1. Hides complexity of instantiating new objects
2. Reduces number of classes
3. Allows adding/removing objects at runtime
4. Configures objects before cloning
5. Reduces subclassing

**Недостатки:**
1. Requires implementing cloning mechanism
2. Deep cloning can be complex
3. Handles circular references carefully
4. Can hide object dependencies

## Answer (EN)

**Prototype Pattern Theory:**
Prototype - creational pattern that creates objects by copying existing ones. Hides complexity of instantiation from client. Existing object acts as prototype and contains state. Solves: determining specific object type at runtime, instantiating dynamically loaded classes, avoiding factory hierarchy parallel to product hierarchy, expensive object creation vs cloning.

**Definition:**

*Theory:* Prototype design pattern enables creating new objects by copying existing object. Allows hiding complexity of making new instances from client. Prototype object returns copy of itself. Client doesn't need to know concrete types, works with prototype interface. Solution for: runtime object creation, dynamic loading, avoiding tight coupling to concrete classes.

```kotlin
// ✅ Prototype interface
interface GameCharacterPrototype {
    fun clone(): GameCharacterPrototype
}

// ✅ Concrete prototype
data class GameCharacter(
    val name: String,
    val weapon: String,
    val level: Int
) : GameCharacterPrototype {
    override fun clone(): GameCharacterPrototype {
        return copy()  // Data class copy()
    }
}

// ✅ Usage
fun main() {
    val original = GameCharacter("Knight", "Sword", 5)
    val cloned = original.clone() as GameCharacter
}
```

**Problems Solved:**

**1. Dynamic Object Creation:**
*Theory:* Creating objects directly within class commits to particular objects at compile-time. Impossible to specify which objects to create at run-time. Prototype pattern solves by: cloning existing objects, determining type at runtime, not compile-time.

```kotlin
// ❌ Compile-time commitment
class GameManager {
    fun createCharacter(type: String): Character {
        return when(type) {
            "warrior" -> Warrior("Default", 1)
            "mage" -> Mage("Default", 1)
            else -> throw IllegalArgumentException()
        }
    }
}

// ✅ Runtime flexibility with prototypes
class GameManager {
    private val prototypes = mutableMapOf<String, GameCharacterPrototype>()

    fun registerPrototype(name: String, prototype: GameCharacterPrototype) {
        prototypes[name] = prototype
    }

    fun createCharacter(type: String): GameCharacterPrototype {
        return prototypes[type]?.clone() ?: throw IllegalArgumentException()
    }
}
```

**2. Avoiding Factory Hierarchy:**
*Theory:* Building factory hierarchy parallel to product hierarchy is verbose and complex. Prototype eliminates need for factory classes by using cloning. Reduces classes, simplifies design, allows adding/removing prototypes at runtime.

**3. Expensive Object Creation:**
*Theory:* When object creation expensive compared to cloning, use prototypes. Clone pre-instantiated objects instead of creating new ones. Examples: database connections, complex configurations, initialized objects with heavy setup.

```kotlin
// ✅ Expensive object creation
class ExpensiveObject {
    init {
        // Heavy initialization
        Thread.sleep(1000)  // Simulate expensive operation
    }
}

// ✅ Prototype avoids re-initialization
val prototype = ExpensiveObject()
val clone = prototype.clone()  // Fast copy, no initialization
```

**When to Use:**

✅ **Use Prototype when:**
- Classes to instantiate specified at runtime
- Want to avoid factory hierarchy parallel to product hierarchy
- Instances have few different state combinations
- Object creation expensive compared to cloning
- Concrete classes unknown until runtime
- Need to configure and clone predefined objects
- Creating similar objects with minor variations

❌ **Don't use Prototype when:**
- Classes have only few instances (no benefit)
- Instances differ significantly (cloning wasteful)
- Cloning more expensive than creating new
- Complex object graphs with circular references

**Deep vs Shallow Cloning:**

*Theory:* Shallow clone - copies object but shares references to nested objects. Deep clone - creates new objects for all nested structures. Challenge: implementing deep clone correctly, handling circular references. Solution: clone all nested objects recursively, maintain visited objects map.

```kotlin
// ✅ Shallow clone (shared references)
data class CharacterSettings(val config: Map<String, String>)
data class GameCharacter(val settings: CharacterSettings)

val original = GameCharacter(CharacterSettings(mapOf("level" to "5")))
val shallowCopy = original.copy()
shallowCopy.settings.config["level"] = "10"
// ❌ original.settings now also "10" - shared reference!

// ✅ Deep clone
interface DeepCloneable<T> {
    fun deepClone(): T
}

class DeepCloneableCharacter(val settings: CharacterSettings) : DeepCloneable<DeepCloneableCharacter> {
    override fun deepClone(): DeepCloneableCharacter {
        return DeepCloneableCharacter(
            CharacterSettings(settings.config.toMap())  // New map
        )
    }
}
```

**Advantages:**
1. Hides complexity of instantiating new objects
2. Reduces number of classes
3. Allows adding/removing objects at runtime
4. Configures objects before cloning
5. Reduces subclassing

**Disadvantages:**
1. Requires implementing cloning mechanism
2. Deep cloning can be complex
3. Needs careful handling of circular references
4. Can hide object dependencies

---

## Follow-ups

- What is the difference between Prototype and Factory patterns?
- How to implement deep cloning in Kotlin?
- When is shallow cloning acceptable vs deep cloning?

## Related Questions

### Prerequisites (Easier)
- Basic design patterns concepts
- Understanding of object creation

### Related (Same Level)
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern
- [[q-builder-pattern--design-patterns--medium]] - Builder pattern
- [[q-singleton-pattern--design-patterns--medium]] - Singleton pattern

### Advanced (Harder)
- Advanced cloning patterns
- Object serialization and cloning
- Registry pattern with prototypes
