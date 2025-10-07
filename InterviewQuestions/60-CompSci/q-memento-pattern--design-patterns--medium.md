---
title: Memento Pattern
topic: design-patterns
subtopics:
  - behavioral-patterns
  - state-management
  - undo-redo
difficulty: medium
related:
  - command-pattern
  - state-pattern
status: draft
---

# Memento Pattern / Паттерн Хранитель

## English

### Definition
The Memento design pattern is a powerful behavioral pattern that provides a way to capture and restore an object's internal state. It allows objects to be saved and restored without violating encapsulation principles.

### Components
The pattern consists of three main components:
- **Originator**. The Originator is the object whose state we want to capture and restore. It creates a Memento object containing a snapshot of its current state or can restore its state from a Memento object
- **Memento**. The Memento is an object that stores the state of the Originator. It provides methods to retrieve the saved state and potentially modify it
- **Caretaker**. The Caretaker is responsible for storing and managing the Memento objects. It interacts with the Originator to save and restore its state using Memento objects

### When to Use
Use the Memento Design Pattern when:
- **Undo functionality**. When your application needs to include an undo function that lets users restore the state of an object after making modifications
- **Snapshotting**. When you need to enable features like versioning or checkpoints by saving an object's state at different times
- **Transaction rollback**. When there are failures or exceptions, like in database transactions, and you need to reverse changes made to an object's state
- **Caching**. When you wish to reduce duplicate calculations or enhance efficiency by caching an object's state

### Implementation Steps
1. Create the `Memento` class to store the internal state of the `Originator`
2. The `Originator` class should have methods to save its state to a memento and restore its state from a memento
3. Implement a `Caretaker` class that maintains a list of mementos for the purpose of undo and redo

### Example in Kotlin

```kotlin
// Step 1: Memento class
data class Memento(val state: String)

// Step 2: Originator class
class Originator(var state: String) {
    fun createMemento(): Memento {
        return Memento(state)
    }

    fun restore(memento: Memento) {
        state = memento.state
    }
}

// Step 3: Caretaker class
class Caretaker {
    private val mementoList = mutableListOf<Memento>()

    fun saveState(originator: Originator) {
        mementoList.add(originator.createMemento())
    }

    fun undo(originator: Originator) {
        if (mementoList.isNotEmpty()) {
            val memento = mementoList.removeAt(mementoList.size - 1)
            originator.restore(memento)
        }
    }

    // More methods like redo can be added similarly
}

// Client Code
fun main() {
    val originator = Originator("Initial State")
    val caretaker = Caretaker()

    caretaker.saveState(originator)
    originator.state = "State #1"

    caretaker.saveState(originator)
    originator.state = "State #2"

    println("Current State: ${originator.state}")

    caretaker.undo(originator)
    println("After undo: ${originator.state}")
}
```

**Output:**
```
Current State: State #2
After undo: State #1
```

**Explanation:**
- The `Memento` captures the internal state of the `Originator` without violating its encapsulation
- The `Originator` can save and restore its state using the memento
- The `Caretaker` provides a mechanism to keep track of multiple mementos, allowing for functionalities like undo and redo

### Advantages
- **Preserves Encapsulation**. Allows an object's internal state to be saved and restored without exposing its implementation details
- **Simple Undo/Redo**. Facilitates the implementation of undo/redo functionality, making the system more robust and user-friendly
- **State History**. Allows maintaining a history of previous states of the object, enabling navigation between different states

### Disadvantages
- **Memory Consumption**. Storing multiple mementos can consume significant memory, especially if the object's state is large
- **Additional Complexity**. Introduces additional complexity to the code, with the need to manage the creation and restoration of mementos
- **Caretaker Responsibility**. The caretaker needs to manage mementos efficiently, which can add responsibility and complexity to the system

---

## Русский

### Определение
Паттерн проектирования Хранитель - это мощный поведенческий паттерн, который предоставляет способ захвата и восстановления внутреннего состояния объекта. Он позволяет сохранять и восстанавливать объекты без нарушения принципов инкапсуляции.

### Компоненты
Паттерн состоит из трех основных компонентов:
- **Создатель (Originator)**. Создатель - это объект, состояние которого мы хотим захватить и восстановить. Он создает объект Memento, содержащий снимок его текущего состояния, или может восстановить свое состояние из объекта Memento
- **Хранитель (Memento)**. Хранитель - это объект, который сохраняет состояние Создателя. Он предоставляет методы для извлечения сохраненного состояния и потенциальной его модификации
- **Опекун (Caretaker)**. Опекун отвечает за хранение и управление объектами Memento. Он взаимодействует с Создателем для сохранения и восстановления его состояния с использованием объектов Memento

### Когда Использовать
Используйте паттерн Хранитель, когда:
- **Функциональность отмены**. Когда вашему приложению нужна функция отмены, которая позволяет пользователям восстановить состояние объекта после внесения изменений
- **Создание снимков состояния**. Когда вам нужно включить такие функции, как версионирование или контрольные точки, сохраняя состояние объекта в разные моменты времени
- **Откат транзакций**. Когда есть сбои или исключения, например, в транзакциях базы данных, и вам нужно отменить изменения, внесенные в состояние объекта
- **Кэширование**. Когда вы хотите уменьшить дублирующие вычисления или повысить эффективность путем кэширования состояния объекта

### Шаги Реализации
1. Создать класс `Memento` для хранения внутреннего состояния `Originator`
2. Класс `Originator` должен иметь методы для сохранения своего состояния в хранитель и восстановления состояния из хранителя
3. Реализовать класс `Caretaker`, который поддерживает список хранителей для целей отмены и повтора

### Пример на Kotlin

```kotlin
// Шаг 1: Класс Memento
data class Memento(val state: String)

// Шаг 2: Класс Originator
class Originator(var state: String) {
    fun createMemento(): Memento {
        return Memento(state)
    }

    fun restore(memento: Memento) {
        state = memento.state
    }
}

// Шаг 3: Класс Caretaker
class Caretaker {
    private val mementoList = mutableListOf<Memento>()

    fun saveState(originator: Originator) {
        mementoList.add(originator.createMemento())
    }

    fun undo(originator: Originator) {
        if (mementoList.isNotEmpty()) {
            val memento = mementoList.removeAt(mementoList.size - 1)
            originator.restore(memento)
        }
    }

    // Дополнительные методы, такие как redo, могут быть добавлены аналогично
}

// Клиентский код
fun main() {
    val originator = Originator("Initial State")
    val caretaker = Caretaker()

    caretaker.saveState(originator)
    originator.state = "State #1"

    caretaker.saveState(originator)
    originator.state = "State #2"

    println("Current State: ${originator.state}")

    caretaker.undo(originator)
    println("After undo: ${originator.state}")
}
```

**Вывод:**
```
Current State: State #2
After undo: State #1
```

**Объяснение:**
- `Memento` захватывает внутреннее состояние `Originator` без нарушения его инкапсуляции
- `Originator` может сохранять и восстанавливать свое состояние, используя хранитель
- `Caretaker` предоставляет механизм для отслеживания множественных хранителей, позволяя реализовать функциональность отмены и повтора

### Преимущества
- **Сохраняет инкапсуляцию**. Позволяет сохранять и восстанавливать внутреннее состояние объекта без раскрытия деталей его реализации
- **Простая отмена/повтор**. Облегчает реализацию функциональности отмены/повтора, делая систему более надежной и удобной для пользователя
- **История состояний**. Позволяет поддерживать историю предыдущих состояний объекта, обеспечивая навигацию между различными состояниями

### Недостатки
- **Потребление памяти**. Хранение множественных хранителей может потреблять значительную память, особенно если состояние объекта большое
- **Дополнительная сложность**. Вносит дополнительную сложность в код, с необходимостью управления созданием и восстановлением хранителей
- **Ответственность опекуна**. Опекун должен эффективно управлять хранителями, что может добавить ответственность и сложность системе

---

## References
- [Memento Design Pattern - NeatCode](https://neatcode.org/memento-pattern/)
- [Memento Design Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/memento-design-pattern/)
- [Memento Design Pattern in Kotlin](https://www.javaguides.net/2023/10/memento-design-pattern-in-kotlin.html)
- [Understanding the Memento Design Pattern in Java](https://dev.to/diegosilva13/understanding-the-memento-design-pattern-in-java-2c72)
- [Memento Design Pattern - SourceMaking](https://sourcemaking.com/design_patterns/memento)
- [Memento - Refactoring Guru](https://refactoring.guru/design-patterns/memento)
- [Memento Software Pattern Kotlin Examples](https://softwarepatterns.com/kotlin/memento-software-pattern-kotlin-example)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository
