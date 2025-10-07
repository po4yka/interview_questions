---
tags:
  - design-patterns
  - structural-patterns
  - bridge
  - gof-patterns
  - abstraction
difficulty: hard
status: draft
---

# Bridge Pattern

**English**: What is the Bridge pattern? When and why should it be used?

## Answer

**Bridge (Мост)** - это структурный паттерн проектирования, который разделяет один или несколько классов на две отдельные иерархии — абстракцию и реализацию, позволяя изменять их независимо друг от друга.

### Определение

Bridge is a structural design pattern that **lets you split a large class or a set of closely related classes into two separate hierarchies—abstraction and implementation—which can be developed independently** of each other.

This pattern involves an interface which acts as a bridge which makes the functionality of concrete classes independent from interface implementer classes. Both types of classes can be altered structurally without affecting each other.

### Проблемы, которые решает

The Bridge design pattern solves problems like:

1. **An abstraction and its implementation should be defined and extended independently from each other**
2. **A compile-time binding between an abstraction and its implementation should be avoided** so that an implementation can be selected at run-time

### Когда использовать?

When to Use Bridge Pattern:

1. **Avoid permanent binding** between abstraction and implementation
2. **Both abstraction and implementation should be extensible** through subclassing
3. **Changes in implementation shouldn't impact clients**
4. **Share implementation among multiple objects** and hide implementation details

## Ключевые компоненты

Key Components:

1. **Abstraction** - High-level interface that defines abstract methods
2. **Implementor** - Interface/abstract class defining methods for concrete implementors
3. **Concrete Abstraction** - Extends Abstraction, uses Implementor
4. **Concrete Implementor** - Implements the Implementor interface

## Пример: Device Remote Control

```kotlin
// Implementor
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

class Radio : Device {
    override var isEnabled = false
        private set
    private var volume = 50

    override fun turnOn() {
        isEnabled = true
        println("Radio is ON")
    }

    override fun turnOff() {
        isEnabled = false
        println("Radio is OFF")
    }

    override fun setVolume(volume: Int) {
        this.volume = volume
        println("Radio volume set to $volume")
    }
}

// Abstraction
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

// Refined Abstraction
class AdvancedRemote(device: Device) : RemoteControl(device) {
    fun mute() {
        device.setVolume(0)
        println("Muted")
    }
}

fun main() {
    val tv = TV()
    val tvRemote = RemoteControl(tv)
    tvRemote.togglePower()
    tvRemote.volumeUp()

    val radio = Radio()
    val advancedRemote = AdvancedRemote(radio)
    advancedRemote.togglePower()
    advancedRemote.mute()
}
```

## Android Example: Drawing Shapes

```kotlin
// Implementor - Rendering API
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

// Abstraction - Shape
abstract class Shape(protected val renderer: Renderer) {
    abstract fun draw()
    abstract fun resize(factor: Float)
}

// Refined Abstractions
class Circle(
    renderer: Renderer,
    private var radius: Float
) : Shape(renderer) {

    override fun draw() {
        renderer.renderCircle(radius)
    }

    override fun resize(factor: Float) {
        radius *= factor
    }
}

class Square(
    renderer: Renderer,
    private var side: Float
) : Shape(renderer) {

    override fun draw() {
        renderer.renderSquare(side)
    }

    override fun resize(factor: Float) {
        side *= factor
    }
}

// Usage
fun main() {
    val vectorCircle = Circle(VectorRenderer(), 5f)
    vectorCircle.draw()

    val rasterSquare = Square(RasterRenderer(), 10f)
    rasterSquare.draw()

    // Easy to combine different abstractions and implementations
    val rasterCircle = Circle(RasterRenderer(), 7f)
    rasterCircle.draw()
}
```

## Kotlin Example: Message Sender

```kotlin
// Implementor - Sending mechanism
interface MessageSender {
    fun sendMessage(message: String, recipient: String)
}

class EmailSender : MessageSender {
    override fun sendMessage(message: String, recipient: String) {
        println("Sending email to $recipient: $message")
    }
}

class SmsSender : MessageSender {
    override fun sendMessage(message: String, recipient: String) {
        println("Sending SMS to $recipient: $message")
    }
}

class PushNotificationSender : MessageSender {
    override fun sendMessage(message: String, recipient: String) {
        println("Sending push notification to $recipient: $message")
    }
}

// Abstraction - Message
abstract class Message(protected val sender: MessageSender) {
    abstract fun send(recipient: String)
}

// Refined Abstractions
class TextMessage(
    sender: MessageSender,
    private val content: String
) : Message(sender) {
    override fun send(recipient: String) {
        sender.sendMessage(content, recipient)
    }
}

class EncryptedMessage(
    sender: MessageSender,
    private val content: String
) : Message(sender) {
    override fun send(recipient: String) {
        val encrypted = encrypt(content)
        sender.sendMessage(encrypted, recipient)
    }

    private fun encrypt(text: String) = "ENCRYPTED[$text]"
}

// Usage
fun main() {
    val emailMessage = TextMessage(EmailSender(), "Hello World")
    emailMessage.send("user@example.com")

    val encryptedSms = EncryptedMessage(SmsSender(), "Secret message")
    encryptedSms.send("+1234567890")
}
```

### Объяснение

**Explanation**:

- **Implementor** (Device, Renderer, MessageSender) defines implementation interface
- **Abstraction** (RemoteControl, Shape, Message) contains reference to implementor
- **Concrete implementors** provide actual implementations
- **Refined abstractions** extend base abstraction with more features
- **Decoupling** allows changing implementations without affecting abstractions

## Преимущества и недостатки

### Pros (Преимущества)

1. **Decoupling** - Abstraction and implementation are independent
2. **Improved Extensibility** - Extend hierarchies independently
3. **Enhanced Flexibility** - Change implementation without modifying abstraction
4. **Runtime binding** - Can switch implementations at runtime
5. **Open/Closed Principle** - Open for extension, closed for modification

### Cons (Недостатки)

1. **Increased complexity** - More classes and interfaces
2. **Indirection** - Extra layer of abstraction
3. **Design overhead** - Requires careful design upfront

## Best Practices

```kotlin
// ✅ DO: Use when you have multiple dimensions of variation
interface StorageBackend {
    fun save(data: String)
    fun load(): String
}

abstract class DataManager(protected val storage: StorageBackend) {
    abstract fun process(data: String)
}

class UserDataManager(storage: StorageBackend) : DataManager(storage) {
    override fun process(data: String) {
        // Process user data
        storage.save(data)
    }
}

// ✅ DO: Allow runtime selection of implementation
class ConfigurableShape(renderer: Renderer) {
    private var currentRenderer = renderer

    fun setRenderer(renderer: Renderer) {
        currentRenderer = renderer
    }

    fun draw() {
        currentRenderer.renderCircle(10f)
    }
}

// ✅ DO: Use for platform-specific implementations
interface Platform {
    fun showNotification(message: String)
}

class AndroidPlatform : Platform {
    override fun showNotification(message: String) {
        // Android-specific notification
    }
}

class IOSPlatform : Platform {
    override fun showNotification(message: String) {
        // iOS-specific notification
    }
}

// ❌ DON'T: Use for single implementation
// ❌ DON'T: Create unnecessary abstractions
// ❌ DON'T: Couple abstraction to concrete implementation
```

**English**: **Bridge** is a structural pattern that separates abstraction from implementation, allowing independent development. **Problem**: Want to avoid permanent binding between abstraction and implementation. **Solution**: Create two hierarchies connected by composition - abstraction holds reference to implementor. **Use when**: (1) Abstraction and implementation should vary independently, (2) Need runtime selection of implementation, (3) Avoid class explosion from multiple dimensions. **Android**: Rendering engines, platform-specific code, storage backends. **Pros**: decoupling, flexibility, extensibility. **Cons**: complexity, indirection. **Examples**: Remote controls, rendering APIs, message senders, storage backends.

## Links

- [Bridge pattern](https://en.wikipedia.org/wiki/Bridge_pattern)
- [Bridge Design Pattern in Kotlin](https://www.javaguides.net/2023/10/bridge-design-pattern-in-kotlin.html)
- [Bridge Method Design Pattern in Java](https://www.geeksforgeeks.org/bridge-method-design-pattern-in-java/)

## Further Reading

- [Bridge](https://refactoring.guru/design-patterns/bridge)
- [Bridge Design Pattern](https://sourcemaking.com/design_patterns/bridge)

---
*Source: Kirchhoff Android Interview Questions*
