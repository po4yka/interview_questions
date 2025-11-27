---
id: cs-012
title: "Memento Pattern / Паттерн Хранитель"
aliases: ["Memento Pattern", "Паттерн Хранитель"]
topic: cs
subtopics: [design-patterns, behavioral, memento, state-management, undo-redo]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-architecture-patterns
related: [c-architecture-patterns, q-memento-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral-patterns, design-patterns, difficulty/medium, memento, state-management, undo-redo]
sources: ["https://refactoring.guru/design-patterns/memento"]
date created: Saturday, November 1st 2025, 1:26:36 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Что такое паттерн Memento? Когда его использовать и как он работает?

# Question (EN)
> What is the Memento pattern? When to use it and how does it work?

---

## Ответ (RU)

**Теория Memento Pattern:**
Memento — поведенческий (behavioral) паттерн проектирования для сохранения (capture/externalize) и восстановления внутреннего состояния объекта. Он решает проблему: нужно сохранять и восстанавливать состояние объекта, не нарушая инкапсуляцию — код, использующий снимки (Caretaker), не должен зависеть от внутренних деталей этого состояния. Используется для: undo/redo функциональности, snapshotting, checkpoints, transaction rollback, истории состояний. Паттерн состоит из 3 компонентов: Originator (объект с состоянием), Memento (хранит снимок состояния), Caretaker (управляет mementos, не заглядывая внутрь них).

**Определение:**

*Теория:* Паттерн Memento предоставляет способ захватить и внешне сохранить внутреннее состояние объекта так, чтобы позже можно было восстановить его без нарушения принципов инкапсуляции. Memento — это snapshot состояния в момент времени. Originator создаёт memento и может восстановить состояние из memento. Caretaker управляет mementos (историей состояний) для реализации undo/redo, при этом не работает напрямую с внутренним содержимым memento.

**Компоненты:**

*Теория:* Три ключевых компонента:
- Originator — объект с изменяемым состоянием, создаёт mementos и восстанавливает состояние из них.
- Memento — хранит снимок состояния Originator, обычно делается неизменяемым и инкапсулирует детали.
- Caretaker — управляет историей mementos (undo/redo), но не зависит от внутренней структуры memento.

```kotlin
// ✅ Упрощённая реализация Memento (демонстрационная, без строгой инкапсуляции)
data class Memento(val state: String)  // Immutable snapshot (но публичное поле)

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
        // Один из возможных вариантов политики undo: откат к последнему сохранённому состоянию
        if (history.isNotEmpty()) {
            val memento = history.removeLast()
            originator.restore(memento)
        }
    }
}

// Использование (пример поведения, а не строгий эталон паттерна)
fun main() {
    val originator = Originator("Initial")
    val caretaker = Caretaker()

    caretaker.saveState(originator)  // State 1
    originator.state = "Modified"

    caretaker.saveState(originator)  // State 2
    originator.state = "Modified Again"

    caretaker.undo(originator)  // Restores to "Modified" (по текущей политике)
    println(originator.state)
}
```

**Когда использовать:**

*Теория:* Используйте Memento, когда:
- нужна undo/redo функциональность (текстовые редакторы, графические редакторы);
- требуется snapshotting для версионирования или checkpoint'ов;
- нужен rollback транзакций при ошибках;
- требуется хранение истории состояний объектов.

✅ **Use Memento when:**
- Нужна undo/redo функциональность.
- Нужно snapshotting для versioning/checkpoints.
- Требуется transaction rollback.
- Нужно сохранять историю состояний без раскрытия внутренних деталей.

❌ **Don't use Memento when:**
- Состояние слишком велико (проблемы с памятью).
- Случай слишком простой (будет over-engineering).
- Состояние меняется слишком часто (высокие накладные расходы по памяти/хранению).

**Реальный пример: Text Editor с Undo/Redo:**

*Теория:* Text editor может использовать Memento для сохранения состояний документа. Каждое значимое изменение сохраняется как memento. Undo восстанавливает предыдущее состояние, redo — более позднее состояние. History поддерживается в списке; при этом внешние компоненты работают с mementos как с непрозрачными объектами.

```kotlin
// ✅ Text Editor с undo/redo (упрощённо, демонстрирует идею истории состояний)
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
        // Удалить состояния после currentIndex при новом вводе
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

1. **Сохранение инкапсуляции** — позволяет сохранять внутреннее состояние без раскрытия реализации (если Memento инкапсулирован).
2. **Поддержка Undo/Redo** — упрощает реализацию механизма отмены/повтора.
3. **История состояний** — удобно хранить последовательность снимков.

**Недостатки:**

1. **Потребление памяти** — хранение множества mementos может быть дорогим.
2. **Дополнительная сложность** — нужен код для управления жизненным циклом mementos.
3. **Ответственность Caretaker** — необходимо продумывать политику очистки/ограничения истории.

**Ключевые концепции:**

1. **Инкапсуляция** — состояние сохраняется без раскрытия внутренних деталей клиентскому коду.
2. **Snapshot** — memento — это снимок состояния.
3. **История состояний** — возможность навигации между предыдущими состояниями.
4. **Управление памятью** — ограничение/очистка истории для эффективности.
5. **Rollback** — возможность отката к ранее сохранённому состоянию.

## Answer (EN)

**Memento Pattern Theory:**
Memento is a behavioral design pattern for capturing (externalizing) and restoring an object's internal state. It solves the problem of saving and restoring state without violating encapsulation — clients that store mementos (Caretakers) should not depend on the originator's internals. It is used for undo/redo functionality, snapshotting, checkpoints, transaction rollback, and maintaining state history. The pattern consists of 3 components: Originator (object with the state), Memento (stores a state snapshot), Caretaker (manages mementos without inspecting their internals).

**Definition:**

*Theory:* The Memento pattern provides a way to capture and externalize an object's internal state so that it can be restored later without violating encapsulation principles. A Memento is a snapshot of state at a specific point in time. The Originator creates mementos and can restore its state from them. The Caretaker manages mementos (state history) for undo/redo, while treating them as opaque objects.

**Components:**

*Theory:* Three key components:
- Originator: object with mutable state; creates and restores from mementos.
- Memento: stores a snapshot of the Originator's state; typically immutable and encapsulates details.
- Caretaker: manages the history of mementos (undo/redo) without depending on their internal structure.

```kotlin
// ✅ Simplified Memento implementation (demonstrational, not enforcing full encapsulation)
data class Memento(val state: String)  // Immutable snapshot (but public field)

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
        // One possible undo policy: revert to the last saved state
        if (history.isNotEmpty()) {
            val memento = history.removeLast()
            originator.restore(memento)
        }
    }
}

// Usage (behavior demonstration, not a complete production design)
fun main() {
    val originator = Originator("Initial")
    val caretaker = Caretaker()

    caretaker.saveState(originator)  // State 1
    originator.state = "Modified"

    caretaker.saveState(originator)  // State 2
    originator.state = "Modified Again"

    caretaker.undo(originator)  // Restores to "Modified" with this policy
    println(originator.state)
}
```

**When to Use:**

*Theory:* Use Memento when you:
- need undo/redo functionality (text editors, graphics tools);
- need snapshotting for versioning or checkpoints;
- need transaction rollback on failures;
- need to maintain history of object states without exposing internals.

✅ **Use Memento when:**
- Need undo/redo functionality.
- Need snapshotting for versioning/checkpoints.
- Need transaction rollback.
- Need state history while preserving encapsulation.

❌ **Don't use Memento when:**
- State is too large (memory issues).
- Use case is simple (over-engineering).
- State changes extremely frequently (high memory/storage overhead).

**Real Example: Text Editor with Undo/Redo:**

*Theory:* A text editor can use Memento to store document states. Each significant change is stored as a memento. Undo restores the previous state; redo restores a later state. History is maintained in a list; external code treats mementos as opaque snapshots.

```kotlin
// ✅ Text Editor with undo/redo (simplified, illustrates state history concept)
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
        // Remove states after currentIndex when new input appears
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

1. **Preserves Encapsulation** (when implemented properly) — saves internal state without exposing implementation.
2. **Undo/Redo Support** — straightforward way to implement undo/redo behavior.
3. **State History** — convenient for maintaining a sequence of snapshots.

**Disadvantages:**

1. **Memory Consumption** — storing many mementos can be expensive.
2. **Additional Complexity** — requires management of memento lifecycle.
3. **Caretaker Responsibility** — must define policies for cleanup/limiting history.

**Key Concepts:**

1. **Encapsulation** — state is saved without exposing internal details to clients.
2. **Snapshot Pattern** — memento represents a snapshot of state.
3. **State History** — ability to navigate between previous states.
4. **Memory Management** — limit/clean history for efficiency.
5. **Rollback Capability** — can rollback to previously saved states.

---

## Follow-ups

- How does Memento pattern relate to Command pattern?
- What is the difference between Memento and Prototype pattern?
- How would you limit memory usage when using Memento for undo/redo?

## References

- [[c-architecture-patterns]]
- "Design Patterns: Elements of Reusable Object-Oriented Software"
- [Refactoring.Guru – Memento](https://refactoring.guru/design-patterns/memento)

## Related Questions

### Prerequisites (Easier)
- Basic object-oriented programming
- Understanding of state management

### Related (Same Level)
- [[q-state-pattern--cs--medium]] - State pattern

### Advanced (Harder)
- Memory-optimized Memento implementations
- Advanced undo/redo systems
- Snapshot management strategies
