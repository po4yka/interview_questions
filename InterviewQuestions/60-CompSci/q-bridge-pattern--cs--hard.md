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
related: [c-adapter-pattern, c-decorator-pattern, c-design-patterns]
created: 2025-10-15
updated: 2025-01-25
tags: [abstraction, bridge, design-patterns, difficulty/hard, gof-patterns, structural-patterns]
sources: [https://refactoring.guru/design-patterns/bridge]
---

# Вопрос (RU)
> Что такое паттерн Bridge? Когда и зачем его использовать?

# Question (EN)
> What is the Bridge pattern? When and why should it be used?

---

## Ответ (RU)

**Теория Bridge:**
Bridge - структурный паттерн, который разделяет большой класс или набор тесно связанных классов на две отдельные иерархии - абстракцию и реализацию, которые могут разрабатываться независимо друг от друга. Делает функциональность конкретных классов независимой от классов-реализаторов интерфейса.

**Проблема:**
Абстракция и её реализация должны определяться и расширяться независимо друг от друга. Следует избегать привязки во время компиляции между абстракцией и реализацией, чтобы реализация могла выбираться во время выполнения.

**Решение:**
Создать две иерархии, связанные композицией - абстракция содержит ссылку на реализатор. Это позволяет изменять реализацию во время выполнения без влияния на абстракцию.

**Ключевые компоненты:**
- **Abstraction** - высокоуровневый интерфейс, определяющий абстрактные методы
- **Implementor** - интерфейс/абстрактный класс, определяющий методы для конкретных реализаторов
- **Concrete Abstraction** - расширяет Abstraction, использует Implementor
- **Concrete Implementor** - реализует интерфейс Implementor

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
- Разделение абстракции и реализации
- Улучшенная расширяемость - иерархии расширяются независимо
- Повышенная гибкость - изменение реализации без влияния на абстракцию
- Привязка во время выполнения - можно переключать реализации
- Принцип открытости/закрытости

**Недостатки:**
- Увеличенная сложность - больше классов и интерфейсов
- Косвенность - дополнительный уровень абстракции
- Накладные расходы на проектирование

---

## Answer (EN)

**Bridge Theory:**
Bridge is a structural design pattern that lets you split a large class or a set of closely related classes into two separate hierarchies - abstraction and implementation - which can be developed independently of each other. Makes functionality of concrete classes independent from interface implementer classes.

**Problem:**
An abstraction and its implementation should be defined and extended independently from each other. A compile-time binding between an abstraction and its implementation should be avoided so that an implementation can be selected at runtime.

**Solution:**
Create two hierarchies connected by composition - abstraction holds reference to implementor. This allows changing implementation at runtime without affecting abstraction.

**Key Components:**
- **Abstraction** - high-level interface that defines abstract methods
- **Implementor** - interface/abstract class defining methods for concrete implementors
- **Concrete Abstraction** - extends Abstraction, uses Implementor
- **Concrete Implementor** - implements the Implementor interface

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
- Decoupling abstraction from implementation
- Improved extensibility - hierarchies extend independently
- Enhanced flexibility - change implementation without affecting abstraction
- Runtime binding - can switch implementations
- Open/Closed Principle

**Disadvantages:**
- Increased complexity - more classes and interfaces
- Indirection - extra layer of abstraction
- Design overhead

## Follow-ups

- Bridge vs Adapter pattern differences?
- When to use composition vs inheritance?
- Platform-specific implementations with Bridge?

## References

- [[c-design-patterns]]
- https://refactoring.guru/design-patterns/bridge

## Related Questions

### Prerequisites (Easier)
- [[q-design-patterns-fundamentals--software-engineering--hard]] - Design patterns overview

### Related (Medium)
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern
- [[q-decorator-pattern--design-patterns--medium]] - Decorator pattern

### Advanced (Harder)
- [[q-interpreter-pattern--design-patterns--hard]] - Interpreter pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern
