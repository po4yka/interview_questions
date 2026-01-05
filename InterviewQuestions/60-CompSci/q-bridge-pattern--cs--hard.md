---
id: cs-018
title: "Bridge Pattern / Bridge Паттерн"
aliases: ["Bridge Pattern", "Паттерн Bridge"]
topic: cs
subtopics: [bridge, design-patterns, structural-patterns]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-adapter-pattern, c-architecture-patterns, c-design-patterns]
created: 2025-10-15
updated: 2025-11-11
tags: [abstraction, bridge, design-patterns, difficulty/hard, gof-patterns, structural-patterns]
sources: ["https://refactoring.guru/design-patterns/bridge"]

---
# Вопрос (RU)
> Что такое паттерн Bridge? Когда и зачем его использовать?

# Question (EN)
> What is the Bridge pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Bridge:**
Bridge — структурный паттерн, который разделяет большой класс или набор тесно связанных классов на две отдельные иерархии — абстракцию и реализацию, — которые могут разрабатываться независимо друг от друга. Паттерн ослабляет связь между абстракцией и конкретными классами-реализаторами, делая их независимыми друг от друга и позволяя комбинировать их произвольно.

**Проблема:**
Абстракция и её реализация должны определяться и расширяться независимо друг от друга. Следует избегать жёсткой привязки во время компиляции между абстракцией и реализацией, чтобы реализация могла выбираться или изменяться во время выполнения.

**Решение:**
Создать две иерархии, связанные композицией: абстракция содержит ссылку на реализатор (Implementor). Это позволяет изменять реализацию во время выполнения без изменения абстракции и независимо развивать обе иерархии.

**Ключевые компоненты:**
- **Abstraction** — высокоуровневый интерфейс/абстрактный класс, определяющий поведение с точки зрения клиента.
- **Implementor** — интерфейс/абстрактный класс, определяющий базовые операции для конкретных реализаций.
- **Refined Abstraction** — конкретные варианты абстракции, использующие Implementor.
- **Concrete Implementor** — конкретные реализации интерфейса Implementor.

**Применение:**
```kotlin
// ✅ Implementor
interface Device {
    fun turnOn()
    fun turnOff()
    fun setVolume(volume: Int)
    val isEnabled: Boolean
}

class TV : Device {
    override var isEnabled = false
        private set
    private var volume = 30

    override fun turnOn() {
        isEnabled = true
        println("TV is ON")
    }

    override fun turnOff() {
        isEnabled = false
        println("TV is OFF")
    }

    override fun setVolume(volume: Int) {
        this.volume = volume
        println("TV volume set to $volume")
    }
}

// ✅ Abstraction
open class RemoteControl(protected val device: Device) {
    fun togglePower() {
        if (device.isEnabled) {
            device.turnOff()
        } else {
            device.turnOn()
        }
    }

    fun volumeUp() {
        // пример: меняем реализацию управления громкостью через Implementor
        // в реальном коде могли бы хранить текущее значение; здесь фиксированное значение для простоты
        device.setVolume(50)
    }
}

// ✅ Refined Abstraction
class AdvancedRemote(device: Device) : RemoteControl(device) {
    fun mute() {
        device.setVolume(0)
        println("Muted")
    }
}
```

**Android применение:**
```kotlin
// ✅ Implementor - Rendering API
interface Renderer {
    fun renderCircle(radius: Float)
    fun renderSquare(side: Float)
}

class VectorRenderer : Renderer {
    override fun renderCircle(radius: Float) {
        println("Drawing circle with vector graphics, radius = $radius")
    }

    override fun renderSquare(side: Float) {
        println("Drawing square with vector graphics, side = $side")
    }
}

class RasterRenderer : Renderer {
    override fun renderCircle(radius: Float) {
        println("Drawing circle with raster graphics, radius = $radius pixels")
    }

    override fun renderSquare(side: Float) {
        println("Drawing square with raster graphics, side = $side pixels")
    }
}

// ✅ Abstraction - Shape
abstract class Shape(protected val renderer: Renderer) {
    abstract fun draw()
    abstract fun resize(factor: Float)
}

// ✅ Refined Abstractions
class Circle(renderer: Renderer, private var radius: Float) : Shape(renderer) {
    override fun draw() {
        renderer.renderCircle(radius)
    }

    override fun resize(factor: Float) {
        radius *= factor
    }
}

class Square(renderer: Renderer, private var side: Float) : Shape(renderer) {
    override fun draw() {
        renderer.renderSquare(side)
    }

    override fun resize(factor: Float) {
        side *= factor
    }
}
```

**Преимущества:**
- Разделение абстракции и реализации.
- Улучшенная расширяемость — иерархии расширяются независимо.
- Повышенная гибкость — можно изменять реализации без изменения абстракции.
- Связывание во время выполнения — можно переключать реализации.
- Соответствие принципу открытости/закрытости.

**Недостатки:**
- Увеличенная сложность — больше классов и интерфейсов.
- Дополнительный уровень косвенности — сложнее понимать структуру.
- Накладные расходы на проектирование.

---

## Answer (EN)

**Bridge Theory:**
Bridge is a structural design pattern that splits a large class or a set of closely related classes into two separate hierarchies — abstraction and implementation — which can be developed independently. It decouples the abstraction from its concrete implementor classes so that both can vary independently and be combined flexibly.

**Problem:**
An abstraction and its implementation should be defined and extended independently from each other. A rigid compile-time binding between an abstraction and its implementation should be avoided so that an implementation can be selected or changed at runtime.

**Solution:**
Create two hierarchies connected via composition: the abstraction holds a reference to the implementor. This allows changing the implementation at runtime without modifying the abstraction and lets both hierarchies evolve independently.

**Key Components:**
- **Abstraction** - high-level interface/abstract class that defines behavior from the client perspective.
- **Implementor** - interface/abstract class that defines low-level operations for concrete implementors.
- **Refined Abstraction** - concrete variants of the abstraction that delegate to an Implementor.
- **Concrete Implementor** - concrete classes that implement the Implementor interface.

**Application:**
```kotlin
// ✅ Implementor
interface Device {
    fun turnOn()
    fun turnOff()
    fun setVolume(volume: Int)
    val isEnabled: Boolean
}

class TV : Device {
    override var isEnabled = false
        private set
    private var volume = 30

    override fun turnOn() {
        isEnabled = true
        println("TV is ON")
    }

    override fun turnOff() {
        isEnabled = false
        println("TV is OFF")
    }

    override fun setVolume(volume: Int) {
        this.volume = volume
        println("TV volume set to $volume")
    }
}

// ✅ Abstraction
open class RemoteControl(protected val device: Device) {
    fun togglePower() {
        if (device.isEnabled) {
            device.turnOff()
        } else {
            device.turnOn()
        }
    }

    fun volumeUp() {
        // example: delegate volume control through Implementor;
        // using a fixed value here keeps the snippet simple
        device.setVolume(50)
    }
}

// ✅ Refined Abstraction
class AdvancedRemote(device: Device) : RemoteControl(device) {
    fun mute() {
        device.setVolume(0)
        println("Muted")
    }
}
```

**Android Application:**
```kotlin
// ✅ Implementor - Rendering API
interface Renderer {
    fun renderCircle(radius: Float)
    fun renderSquare(side: Float)
}

class VectorRenderer : Renderer {
    override fun renderCircle(radius: Float) {
        println("Drawing circle with vector graphics, radius = $radius")
    }

    override fun renderSquare(side: Float) {
        println("Drawing square with vector graphics, side = $side")
    }
}

class RasterRenderer : Renderer {
    override fun renderCircle(radius: Float) {
        println("Drawing circle with raster graphics, radius = $radius pixels")
    }

    override fun renderSquare(side: Float) {
        println("Drawing square with raster graphics, side = $side pixels")
    }
}

// ✅ Abstraction - Shape
abstract class Shape(protected val renderer: Renderer) {
    abstract fun draw()
    abstract fun resize(factor: Float)
}

// ✅ Refined Abstractions
class Circle(renderer: Renderer, private var radius: Float) : Shape(renderer) {
    override fun draw() {
        renderer.renderCircle(radius)
    }

    override fun resize(factor: Float) {
        radius *= factor
    }
}

class Square(renderer: Renderer, private var side: Float) : Shape(renderer) {
    override fun draw() {
        renderer.renderSquare(side)
    }

    override fun resize(factor: Float) {
        side *= factor
    }
}
```

**Advantages:**
- Decouples abstraction from implementation.
- Improved extensibility — hierarchies can evolve independently.
- Enhanced flexibility — implementations can be changed without affecting the abstraction.
- Runtime binding — implementations can be switched at runtime.
- Aligns with the Open/Closed Principle.

**Disadvantages:**
- Increased complexity — more classes and interfaces.
- Extra indirection — structure is harder to follow.
- Design overhead.

## Follow-ups

- Bridge vs Adapter pattern differences?
- When to use composition vs inheritance?
- Platform-specific implementations with Bridge?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/bridge

## Related Questions

### Prerequisites (Easier)
- Design patterns overview

### Related (Medium)
- Adapter pattern
- Decorator pattern

### Advanced (Harder)
- Visitor pattern
