---
id: cs-024
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
related: [q-abstract-factory-pattern--cs--medium, q-adapter-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [creational-patterns, design-patterns, difficulty/medium, object-cloning, prototype]
sources: ["https://refactoring.guru/design-patterns/prototype"]
date created: Saturday, November 1st 2025, 1:27:01 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> Что такое паттерн Prototype? Когда его использовать и как он работает?

# Question (EN)
> What is the Prototype pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Prototype Pattern:**
Prototype — порождающий паттерн, создающий новые объекты путём копирования (клонирования) существующих. Он скрывает сложности создания экземпляров от клиента: существующий объект выступает прототипом и содержит сконфигурированное состояние. Паттерн помогает, когда нужно:
- определять конкретный тип объекта во время выполнения,
- порождать экземпляры динамически загружаемых классов,
- избежать иерархии фабрик, дублирующей иерархию продуктов,
- оптимизировать создание объектов, когда оно дороже/сложнее, чем их клонирование.

См. также: [[c-architecture-patterns]].

**Определение:**

*Теория:* Паттерн Prototype позволяет создавать новые объекты путём копирования существующего объекта-прототипа. Клиент работает с интерфейсом прототипа и запрашивает у него копию, не зная конкретных классов. Решает задачи динамического создания объектов, уменьшения связности с конкретными типами и упрощения конфигурации повторяющихся объектов.

```kotlin
// ✅ Интерфейс прототипа
interface GameCharacterPrototype {
    fun clone(): GameCharacterPrototype
}

// ✅ Конкретный прототип
data class GameCharacter(
    val name: String,
    val weapon: String,
    val level: Int
) : GameCharacterPrototype {
    override fun clone(): GameCharacterPrototype {
        return copy()  // copy() у data class создаёт новый экземпляр с теми же значениями полей
    }
}

// ✅ Использование
fun main() {
    val original = GameCharacter("Knight", "Sword", 5)
    val cloned = original.clone() as GameCharacter
}
```

**Проблемы, которые решает:**

**1. Dynamic Object Creation:**
*Теория:* Создание объектов напрямую внутри классов жёстко привязывает код к конкретным типам на этапе компиляции. Трудно или невозможно выбирать конкретные реализации во время выполнения. Prototype решает это через клонирование заранее зарегистрированных прототипов, что позволяет определять конкретный тип в runtime, а не на этапе компиляции.

```kotlin
// ❌ Жёсткая привязка к типам во время компиляции
class GameManager {
    fun createCharacter(type: String): Character {
        return when(type) {
            "warrior" -> Warrior("Default", 1)
            "mage" -> Mage("Default", 1)
            else -> throw IllegalArgumentException()
        }
    }
}

// ✅ Гибкость во время выполнения с прототипами
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
*Теория:* Иерархия фабрик, дублирующая иерархию продуктов, усложняет дизайн и увеличивает количество классов. Prototype позволяет обойтись без громоздких фабрик, используя клонирование прототипов; прототипы можно регистрировать и изменять во время выполнения.

**3. Expensive Object Creation:**
*Теория:* Если создание объекта существенно дороже, чем его копирование, можно предварительно создать и настроить прототип, а затем клонировать его. Например: сложные конфигурационные объекты, графы объектов с тяжёлой инициализацией. (Важно: прототипы не применяются для ресурсов, которые не должны дублироваться, например реальные подключения к БД, сокеты и т.п.)

```kotlin
// ✅ Пример "дорогой" конфигурации, которую выгодно клонировать
class ExpensiveConfig(val data: Map<String, Any>) : Cloneable {
    public override fun clone(): ExpensiveConfig {
        // Поверхностное копирование Map-ссылки; при необходимости можно сделать глубокое копирование
        return ExpensiveConfig(data)
    }
}

val prototype = ExpensiveConfig(mapOf("key" to "value"))
val clone = prototype.clone()  // Быстрое создание нового объекта на основе уже подготовленных данных
```

**Когда использовать:**

✅ **Используйте Prototype, когда:**
- классы для инстанцирования определяются во время выполнения;
- вы хотите избежать иерархии фабрик, параллельной иерархии продуктов;
- есть преднастроенные объекты с несколькими типичными комбинациями состояния;
- создание объектов дорого по ресурсам/сложно по логике по сравнению с копированием;
- конкретные классы заранее неизвестны (например, плагины, динамическая загрузка);
- нужно настраивать прототипы и затем клонировать их;
- создаёте много похожих объектов с незначительными отличиями.

❌ **Не используйте Prototype, когда:**
- объектов немного, и преимущества переиспользования прототипов не проявляются;
- экземпляры сильно различаются по состоянию, клонирование не даёт выигрыша;
- клонирование сложнее или дороже прямого создания;
- структура объектов слишком сложная, с труднообрабатываемыми связями (глубокое клонирование становится хрупким).

**Глубокое vs Поверхностное клонирование:**

*Теория:*
- Поверхностное (shallow) клонирование — создаёт новый объект, но вложенные объекты копируются по ссылке и остаются общими.
- Глубокое (deep) клонирование — создаёт новые экземпляры для вложенных объектов/структур.

Основная сложность — корректно реализовать глубокое клонирование (особенно при циклических ссылках), часто требуется обход графа объектов и карта уже скопированных элементов.

```kotlin
// ✅ Поверхностное клонирование (общие ссылки)
data class CharacterSettings(val config: MutableMap<String, String>)
data class GameCharacterWithSettings(val settings: CharacterSettings)

val original = GameCharacterWithSettings(CharacterSettings(mutableMapOf("level" to "5")))
val shallowCopy = original.copy() // Копируется только внешний объект, settings — общая ссылка
shallowCopy.settings.config["level"] = "10"
// ❗ original.settings.config["level"] теперь тоже "10" — из-за общей вложенной ссылки

// ✅ Пример глубокого клонирования
interface DeepCloneable<T> {
    fun deepClone(): T
}

class DeepCloneableCharacter(val settings: CharacterSettings) : DeepCloneable<DeepCloneableCharacter> {
    override fun deepClone(): DeepCloneableCharacter {
        return DeepCloneableCharacter(
            CharacterSettings(settings.config.toMutableMap())  // Новый MutableMap и новый Settings
        )
    }
}
```

**Преимущества:**
1. Скрывает сложность создания и конфигурации новых объектов.
2. Снижает количество вспомогательных фабричных классов.
3. Позволяет добавлять/убирать прототипы во время выполнения.
4. Упрощает повторное использование предварительно настроенных объектов.
5. Ослабляет связанность с конкретными классами.

**Недостатки:**
1. Требует аккуратной реализации механизма клонирования.
2. Глубокое клонирование может быть сложным и дорогим.
3. Необходим тщательный контроль циклических ссылок и общих ресурсов.
4. Может скрывать реальные зависимости внутри объекта.

## Answer (EN)

**Prototype Pattern Theory:**
Prototype is a creational pattern that creates new objects by copying (cloning) existing ones. It hides object construction complexity from the client: an existing, fully configured object acts as a prototype and holds the state to be reused. The pattern helps when you need to:
- determine the concrete type at runtime,
- instantiate dynamically loaded classes,
- avoid factory hierarchies parallel to product hierarchies,
- optimize creation of objects that are expensive or complex to build compared to cloning.

See also: [[c-architecture-patterns]].

**Definition:**

*Theory:* The Prototype design pattern enables creating new objects by copying an existing prototype object. The client works with a prototype interface and requests clones without depending on concrete classes. It solves runtime object creation, reduces coupling to concrete implementations, and simplifies reuse of configured objects.

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
        return copy()  // data class copy() creates a new instance with the same field values
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
*Theory:* Creating objects directly inside classes ties you to specific types at compile time, making it hard to decide implementations at runtime. The Prototype pattern solves this by cloning registered prototypes, so concrete types can effectively be chosen at runtime.

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
*Theory:* A factory hierarchy that mirrors the product hierarchy increases complexity and boilerplate. Prototype reduces the need for such factories by using cloning and a registry of prototypes that can be extended or modified at runtime.

**3. Expensive Object Creation:**
*Theory:* When creating an object is significantly more expensive than copying it, you can create and configure a prototype once and then clone it. Typical candidates are complex configuration objects or object graphs with heavy initialization. (Note: prototype is not a good fit for resources that must not be duplicated, such as real DB connections or open sockets.)

```kotlin
// ✅ Example of an "expensive" configuration that is cheaper to clone
class ExpensiveConfig(val data: Map<String, Any>) : Cloneable {
    public override fun clone(): ExpensiveConfig {
        // Shallow copy of the Map reference; use deep copy if needed
        return ExpensiveConfig(data)
    }
}

val prototype = ExpensiveConfig(mapOf("key" to "value"))
val clone = prototype.clone()  // Fast creation of a new object based on prepared data
```

**When to Use:**

✅ **Use Prototype when:**
- the set of classes to instantiate is specified at runtime;
- you want to avoid a factory hierarchy parallel to the product hierarchy;
- you have preconfigured objects with a few common state combinations;
- object creation is expensive/complex compared to cloning;
- concrete classes are not known in advance (e.g., plugins, dynamically loaded types);
- you need to configure prototypes and clone them later;
- you create many similar objects with minor differences.

❌ **Don't use Prototype when:**
- there are only a few instances and reuse doesn’t bring benefits;
- instances differ significantly so cloning gives little advantage;
- cloning is more complex or costly than direct construction;
- object graphs are too complex with tricky relationships (deep cloning becomes fragile).

**Deep vs Shallow Cloning:**

*Theory:*
- Shallow clone: copies the object itself, but nested objects are shared by reference.
- Deep clone: creates new instances for nested objects/structures so that changes are isolated.

The main challenge is implementing deep cloning correctly (especially with cyclic references), which often requires walking the object graph and tracking already-cloned instances.

```kotlin
// ✅ Shallow clone (shared references)
data class CharacterSettings(val config: MutableMap<String, String>)
data class GameCharacterWithSettings(val settings: CharacterSettings)

val original = GameCharacterWithSettings(CharacterSettings(mutableMapOf("level" to "5")))
val shallowCopy = original.copy() // Only outer object is copied; settings is the same reference
shallowCopy.settings.config["level"] = "10"
// ❗ original.settings.config["level"] is now also "10" due to shared nested reference

// ✅ Deep clone example
interface DeepCloneable<T> {
    fun deepClone(): T
}

class DeepCloneableCharacter(val settings: CharacterSettings) : DeepCloneable<DeepCloneableCharacter> {
    override fun deepClone(): DeepCloneableCharacter {
        return DeepCloneableCharacter(
            CharacterSettings(settings.config.toMutableMap())  // New MutableMap and new Settings
        )
    }
}
```

**Advantages:**
1. Hides complexity of constructing and configuring new objects.
2. Reduces the need for separate factory hierarchies.
3. Allows adding/removing prototypes at runtime.
4. Simplifies reuse of preconfigured objects.
5. Decreases coupling to concrete classes.

**Disadvantages:**
1. Requires careful implementation of cloning logic.
2. Deep cloning can be complex and expensive.
3. Needs careful handling of cyclic references and shared resources.
4. Can obscure actual dependencies of the object.

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
- [[q-template-method-pattern--cs--medium]] - Factory Method pattern

### Advanced (Harder)
- Advanced cloning patterns
- Object serialization and cloning
- Registry pattern with prototypes

## References

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gamma et al.
- "Prototype" pattern overview: https://refactoring.guru/design-patterns/prototype
