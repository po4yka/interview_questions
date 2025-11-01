---
id: 20251012-1227111164
title: "Memento Pattern / Паттерн Хранитель"
aliases: ["Memento Pattern", "Паттерн Хранитель"]
topic: cs
subtopics: [behavioral-patterns, design-patterns, state-management, undo-redo]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-command-pattern--design-patterns--medium, q-iterator-pattern--design-patterns--medium, q-state-pattern--design-patterns--medium]
created: 2025-10-15
updated: 2025-01-25
tags: [behavioral-patterns, design-patterns, difficulty/medium, memento, state-management, undo-redo]
sources: [https://refactoring.guru/design-patterns/memento]
date created: Monday, October 6th 2025, 7:34:37 am
date modified: Sunday, October 26th 2025, 12:30:15 pm
---

# Вопрос (RU)
> Что такое паттерн Memento? Когда его использовать и как он работает?

# Question (EN)
> What is the Memento pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Memento Pattern:**
Memento - behavioral design pattern для capture и restore внутреннего state объекта. Решает проблему: нужно сохранять и восстанавливать object state без violation encapsulation. Используется для: undo/redo functionality, snapshotting, transaction rollback, caching. Pattern состоит из 3 components: Originator (объект с состоянием), Memento (хранит состояние), Caretaker (управляет mementos).

**Определение:**

*Теория:* Memento pattern предоставляет way to capture и restore внутреннего state объекта без violation encapsulation principles. Memento - snapshot state в момент времени. Originator создаёт memento и может восстановить state из memento. Caretaker manages mementos для undo/redo functionality.

**Компоненты:**

*Теория:* Three key components: Originator (object с mutable state, создаёт/восстанавливает mementos), Memento (stores snapshot Originator state, может быть immutable), Caretaker (manages history mementos, обеспечивает undo/redo).

```kotlin
// ✅ Basic Memento implementation
data class Memento(val state: String)  // Immutable snapshot

class Originator(var state: String) {
    fun createMemento(): Memento = Memento(state)

    fun restore(memento: Memento) {
        state = memento.state
    }
}

class Caretaker {
    private val history = mutableListOf<Memento>()

    fun saveState(originator: Originator) {
        history.add(originator.createMemento())
    }

    fun undo(originator: Originator) {
        if (history.isNotEmpty()) {
            val memento = history.removeLast()
            originator.restore(memento)
        }
    }
}

// Использование
fun main() {
    val originator = Originator("Initial")
    val caretaker = Caretaker()

    caretaker.saveState(originator)  // State 1
    originator.state = "Modified"

    caretaker.saveState(originator)  // State 2
    originator.state = "Modified Again"

    caretaker.undo(originator)  // Restores to "Modified"
    println(originator.state)
}
```

**Когда использовать:**

*Теория:* Используйте Memento когда: нужно undo/redo functionality (text editors, graphics tools); snapshotting для versioning или checkpoints; transaction rollback при failures; caching для reducing duplicate computations; нужно сохранять history состояний.

✅ **Use Memento when:**
- Нужна undo/redo functionality
- Нужно snapshotting для versioning
- Transaction rollback needed
- Caching состояния объекта

❌ **Don't use Memento when:**
- State слишком large (memory issues)
- Простые use cases (over-engineering)
- Частые state changes (high memory usage)

**Реальный пример: Text Editor с Undo/Redo:**

*Теория:* Text editor использует Memento для сохранения states документа. Каждое изменение сохраняется как memento. Undo восстанавливает previous state, redo восстанавливает forward state. History поддерживается в list.

```kotlin
// ✅ Text Editor с undo/redo
data class DocumentState(val content: String)

class TextEditor {
    private var content: String = ""
    private val history = mutableListOf<DocumentState>()
    private var currentIndex = -1

    fun type(text: String) {
        content += text
        saveState()
    }

    fun undo() {
        if (currentIndex > 0) {
            currentIndex--
            content = history[currentIndex].content
        }
    }

    fun redo() {
        if (currentIndex < history.size - 1) {
            currentIndex++
            content = history[currentIndex].content
        }
    }

    private fun saveState() {
        // Удалить states после currentIndex
        history.subList(currentIndex + 1, history.size).clear()
        history.add(DocumentState(content))
        currentIndex = history.size - 1
    }

    fun getContent() = content
}

// Использование
fun main() {
    val editor = TextEditor()
    editor.type("Hello")
    editor.type(" World")
    println(editor.getContent())  // "Hello World"

    editor.undo()
    println(editor.getContent())  // "Hello"

    editor.redo()
    println(editor.getContent())  // "Hello World"
}
```

**Преимущества:**

1. **Preserves Encapsulation** - сохраняет internal state без exposing implementation
2. **Undo/Redo** - простой способ implement undo/redo
3. **State History** - можно maintain history состояний

**Недостатки:**

1. **Memory Consumption** - хранение mementos может потреблять много памяти
2. **Additional Complexity** - добавляет complexity для management mementos
3. **Caretaker Responsibility** - caretaker должен управлять mementos эффективно

**Ключевые концепции:**

1. **Encapsulation** - state сохраняется без exposing internals
2. **Snapshot Pattern** - memento - это snapshot state
3. **State History** - history позволяет navigate между states
4. **Memory Management** - нужно limit history для memory efficiency
5. **Rollback Capability** - можно откатить к любому previous state

## Answer (EN)

**Memento Pattern Theory:**
Memento - behavioral design pattern for capturing and restoring internal state of object. Solves problem: need to save and restore object state without violating encapsulation. Used for: undo/redo functionality, snapshotting, transaction rollback, caching. Pattern consists of 3 components: Originator (object with state), Memento (stores state), Caretaker (manages mementos).

**Definition:**

*Theory:* Memento pattern provides way to capture and restore internal state of object without violating encapsulation principles. Memento - snapshot of state at point in time. Originator creates memento and can restore state from memento. Caretaker manages mementos for undo/redo functionality.

**Components:**

*Theory:* Three key components: Originator (object with mutable state, creates/restores mementos), Memento (stores snapshot of Originator state, can be immutable), Caretaker (manages history of mementos, provides undo/redo).

```kotlin
// ✅ Basic Memento implementation
data class Memento(val state: String)  // Immutable snapshot

class Originator(var state: String) {
    fun createMemento(): Memento = Memento(state)

    fun restore(memento: Memento) {
        state = memento.state
    }
}

class Caretaker {
    private val history = mutableListOf<Memento>()

    fun saveState(originator: Originator) {
        history.add(originator.createMemento())
    }

    fun undo(originator: Originator) {
        if (history.isNotEmpty()) {
            val memento = history.removeLast()
            originator.restore(memento)
        }
    }
}

// Usage
fun main() {
    val originator = Originator("Initial")
    val caretaker = Caretaker()

    caretaker.saveState(originator)  // State 1
    originator.state = "Modified"

    caretaker.saveState(originator)  // State 2
    originator.state = "Modified Again"

    caretaker.undo(originator)  // Restores to "Modified"
    println(originator.state)
}
```

**When to Use:**

*Theory:* Use Memento when: need undo/redo functionality (text editors, graphics tools); snapshotting for versioning or checkpoints; transaction rollback on failures; caching to reduce duplicate computations; need to save state history.

✅ **Use Memento when:**
- Need undo/redo functionality
- Need snapshotting for versioning
- Transaction rollback needed
- Caching object state

❌ **Don't use Memento when:**
- State too large (memory issues)
- Simple use cases (over-engineering)
- Frequent state changes (high memory usage)

**Real Example: Text Editor with Undo/Redo:**

*Theory:* Text editor uses Memento to save states of document. Each change saved as memento. Undo restores previous state, redo restores forward state. History maintained in list.

```kotlin
// ✅ Text Editor with undo/redo
data class DocumentState(val content: String)

class TextEditor {
    private var content: String = ""
    private val history = mutableListOf<DocumentState>()
    private var currentIndex = -1

    fun type(text: String) {
        content += text
        saveState()
    }

    fun undo() {
        if (currentIndex > 0) {
            currentIndex--
            content = history[currentIndex].content
        }
    }

    fun redo() {
        if (currentIndex < history.size - 1) {
            currentIndex++
            content = history[currentIndex].content
        }
    }

    private fun saveState() {
        // Remove states after currentIndex
        history.subList(currentIndex + 1, history.size).clear()
        history.add(DocumentState(content))
        currentIndex = history.size - 1
    }

    fun getContent() = content
}

// Usage
fun main() {
    val editor = TextEditor()
    editor.type("Hello")
    editor.type(" World")
    println(editor.getContent())  // "Hello World"

    editor.undo()
    println(editor.getContent())  // "Hello"

    editor.redo()
    println(editor.getContent())  // "Hello World"
}
```

**Advantages:**

1. **Preserves Encapsulation** - saves internal state without exposing implementation
2. **Undo/Redo** - simple way to implement undo/redo
3. **State History** - can maintain history of states

**Disadvantages:**

1. **Memory Consumption** - storing mementos may consume significant memory
2. **Additional Complexity** - adds complexity for managing mementos
3. **Caretaker Responsibility** - caretaker must manage mementos efficiently

**Key Concepts:**

1. **Encapsulation** - state saved without exposing internals
2. **Snapshot Pattern** - memento is snapshot of state
3. **State History** - history allows navigating between states
4. **Memory Management** - need to limit history for memory efficiency
5. **Rollback Capability** - can rollback to any previous state

---

## Follow-ups

- How does Memento pattern relate to Command pattern?
- What is the difference between Memento and Prototype pattern?
- How would you limit memory usage when using Memento for undo/redo?

## Related Questions

### Prerequisites (Easier)
- Basic object-oriented programming
- Understanding of state management

### Related (Same Level)
- [[q-command-pattern--design-patterns--medium]] - Command pattern (undo/redo)
- [[q-state-pattern--design-patterns--medium]] - State pattern
- [[q-iterator-pattern--design-patterns--medium]] - Iterator pattern

### Advanced (Harder)
- Memory-optimized Memento implementations
- Advanced undo/redo systems
- Snapshot management strategies
