---
tags:
  - design-patterns
  - behavioral-patterns
  - command
  - gof-patterns
  - action-pattern
difficulty: medium
status: draft
---

# Command Pattern

# Question (EN)
> What is the Command pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Command? Когда и зачем его использовать?

---

## Answer (EN)


**Command (Команда)** - это поведенческий паттерн проектирования, который превращает запросы в объекты, позволяя передавать их как аргументы при вызове методов, ставить запросы в очередь, логировать их, а также поддерживать отмену операций.

### Definition


The Command Pattern is a behavioral design pattern that **turns a request into a stand-alone object that contains all the information about the request**. This transformation allows you to parameterize methods with different requests, queue requests, log their execution, and support undo operations. It decouples the object that invokes an action from the object that performs the action.

### Problems it Solves


Using the command design pattern can solve these problems:

1. **Coupling the invoker of a request to a particular request should be avoided** - Hard-wired requests should be avoided
2. **It should be possible to configure an object (that invokes a request) with a request**
3. **Implementing a request directly into a class is inflexible** - Couples the class to a particular request at compile-time

### Solution


Using the command design pattern describes the following solution:

- Define separate **(command) objects that encapsulate a request**
- A class **delegates a request to a command object** instead of implementing a particular request directly

This enables one to configure a class with a command object that is used to perform a request. The class is no longer coupled to a particular request and has no knowledge of how the request is carried out.

### When is it especially useful?


The Command Pattern is especially useful for:

1. **Decoupling** - Decouples the object that requests an operation (invoker) from the one that performs it (receiver)
2. **Reusability** - Commands can be reused and combined in complex scenarios
3. **History and Undo** - Allows for history and undo features (crucial in text editors, drawing apps)
4. **Logging** - Commands can be logged for debugging and auditing purposes
5. **Queueing** - Commands can be queued and executed later

## Пример: Light Control

```kotlin
// Step 1: Command Interface
interface Command {
    fun execute()
}

// Step 2: Concrete Command Classes
class LightOnCommand(private val light: Light) : Command {
    override fun execute() {
        light.turnOn()
    }
}

class LightOffCommand(private val light: Light) : Command {
    override fun execute() {
        light.turnOff()
    }
}

// Receiver Class
class Light {
    fun turnOn() {
        println("Light is ON")
    }

    fun turnOff() {
        println("Light is OFF")
    }
}

// Step 3: Invoker
class RemoteControl(private val command: Command) {
    fun pressButton() {
        command.execute()
    }
}

// Test the implementation
fun main() {
    val light = Light()
    val lightOnCommand = LightOnCommand(light)
    val lightOffCommand = LightOffCommand(light)

    val remote = RemoteControl(lightOnCommand)
    remote.pressButton()

    val remote2 = RemoteControl(lightOffCommand)
    remote2.pressButton()
}
```

**Output**:
```
Light is ON
Light is OFF
```

## Android Example: Undo/Redo in Text Editor

```kotlin
// Command interface with undo support
interface TextCommand {
    fun execute()
    fun undo()
}

// Concrete commands
class InsertTextCommand(
    private val textEditor: TextEditor,
    private val text: String,
    private val position: Int
) : TextCommand {
    override fun execute() {
        textEditor.insertText(text, position)
    }

    override fun undo() {
        textEditor.deleteText(position, text.length)
    }
}

class DeleteTextCommand(
    private val textEditor: TextEditor,
    private val position: Int,
    private val length: Int
) : TextCommand {
    private lateinit var deletedText: String

    override fun execute() {
        deletedText = textEditor.getText(position, length)
        textEditor.deleteText(position, length)
    }

    override fun undo() {
        textEditor.insertText(deletedText, position)
    }
}

// Receiver
class TextEditor {
    private val text = StringBuilder()

    fun insertText(newText: String, position: Int) {
        text.insert(position, newText)
        println("Text inserted: $text")
    }

    fun deleteText(position: Int, length: Int) {
        text.delete(position, position + length)
        println("Text deleted: $text")
    }

    fun getText(position: Int, length: Int) =
        text.substring(position, position + length)
}

// Invoker with history
class CommandManager {
    private val history = ArrayDeque<TextCommand>()
    private val redoStack = ArrayDeque<TextCommand>()

    fun executeCommand(command: TextCommand) {
        command.execute()
        history.addLast(command)
        redoStack.clear()
    }

    fun undo() {
        if (history.isNotEmpty()) {
            val command = history.removeLast()
            command.undo()
            redoStack.addLast(command)
        }
    }

    fun redo() {
        if (redoStack.isNotEmpty()) {
            val command = redoStack.removeLast()
            command.execute()
            history.addLast(command)
        }
    }
}

// Usage
fun main() {
    val editor = TextEditor()
    val manager = CommandManager()

    manager.executeCommand(InsertTextCommand(editor, "Hello", 0))
    manager.executeCommand(InsertTextCommand(editor, " World", 5))
    manager.undo()  // Removes " World"
    manager.redo()  // Re-adds " World"
}
```

## Android ViewModel Example: User Actions

```kotlin
// Command interface
interface UserAction {
    suspend fun execute(): Result<Unit>
}

// Concrete commands
class LoginCommand(
    private val repository: UserRepository,
    private val email: String,
    private val password: String
) : UserAction {
    override suspend fun execute(): Result<Unit> {
        return repository.login(email, password)
    }
}

class LogoutCommand(
    private val repository: UserRepository
) : UserAction {
    override suspend fun execute(): Result<Unit> {
        return repository.logout()
    }
}

class UpdateProfileCommand(
    private val repository: UserRepository,
    private val profile: UserProfile
) : UserAction {
    override suspend fun execute(): Result<Unit> {
        return repository.updateProfile(profile)
    }
}

// ViewModel as invoker
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val commandQueue = Channel<UserAction>(Channel.UNLIMITED)

    init {
        processCommands()
    }

    private fun processCommands() {
        viewModelScope.launch {
            commandQueue.consumeAsFlow().collect { command ->
                command.execute()
            }
        }
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            commandQueue.send(LoginCommand(repository, email, password))
        }
    }

    fun logout() {
        viewModelScope.launch {
            commandQueue.send(LogoutCommand(repository))
        }
    }
}
```

### Explanation


**Explanation**:

- **Command interface** declares `execute()` method
- **Concrete commands** encapsulate action and receiver
- **Invoker** (RemoteControl, CommandManager) executes commands
- **Receiver** (Light, TextEditor) performs the actual work
- **Android**: Useful for undo/redo, action queuing, transaction management

## Применение в реальных системах

Real Life Examples:

1. **GUI applications** - Button clicks create command objects
2. **Text editors** - Undo/redo functionality
3. **Remote controls** - Each button is a command
4. **Job scheduling** - Commands queued and executed
5. **Transaction management** - Database operations as commands

## Преимущества и недостатки

### Pros (Преимущества)


1. **Decoupling** - Separates invoker from receiver
2. **Reusability** - Commands can be reused and combined
3. **Undo/Redo** - Easy to implement undo/redo
4. **Logging** - Commands can be logged for auditing
5. **Queueing** - Commands can be queued and executed later
6. **Macro commands** - Combine multiple commands

### Cons (Недостатки)


1. **Increased classes** - Each command needs a class
2. **Complexity** - More complex for simple operations
3. **Memory overhead** - Storing command history uses memory
4. **Indirection** - Extra layer of indirection

## Best Practices

```kotlin
// - DO: Use for undo/redo functionality
interface UndoableCommand {
    fun execute()
    fun undo()
}

// - DO: Queue commands for batch processing
class BatchProcessor {
    private val commands = mutableListOf<Command>()

    fun addCommand(command: Command) {
        commands.add(command)
    }

    fun executeBatch() {
        commands.forEach { it.execute() }
        commands.clear()
    }
}

// - DO: Use coroutines for async commands
interface AsyncCommand {
    suspend fun execute(): Result<Unit>
}

// - DO: Macro commands for complex operations
class MacroCommand(private val commands: List<Command>) : Command {
    override fun execute() {
        commands.forEach { it.execute() }
    }
}

// - DON'T: Use for simple method calls
// - DON'T: Store large data in commands
// - DON'T: Make commands stateful
```

**English**: **Command** is a behavioral pattern that encapsulates requests as objects, allowing parameterization, queuing, logging, and undo operations. **Problem**: Need to decouple request sender from receiver. **Solution**: Encapsulate requests as command objects with execute() method. **Use when**: (1) Need undo/redo, (2) Queue/log operations, (3) Decouple invoker from receiver. **Android**: Undo/redo in editors, action queuing in ViewModels. **Pros**: decoupling, undo/redo support, command queuing. **Cons**: many classes, complexity. **Examples**: Text editor undo/redo, remote controls, transaction management.

## Links

- [Command Pattern in Kotlin](https://codesignal.com/learn/courses/behavioral-design-patterns-2/lessons/command-pattern-in-kotlin)
- [Command pattern](https://en.wikipedia.org/wiki/Command_pattern)
- [Command Design Pattern in Kotlin](https://www.javaguides.net/2023/10/command-design-pattern-in-kotlin.html)

## Further Reading

- [Command](https://refactoring.guru/design-patterns/command)
- [Command Pattern in Kotlin](https://swiderski.tech/kotlin-command-pattern/)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение


The Command Pattern is a behavioral design pattern that **turns a request into a stand-alone object that contains all the information about the request**. This transformation allows you to parameterize methods with different requests, queue requests, log their execution, and support undo operations. It decouples the object that invokes an action from the object that performs the action.

### Проблемы, которые решает


Using the command design pattern can solve these problems:

1. **Coupling the invoker of a request to a particular request should be avoided** - Hard-wired requests should be avoided
2. **It should be possible to configure an object (that invokes a request) with a request**
3. **Implementing a request directly into a class is inflexible** - Couples the class to a particular request at compile-time

### Решение


Using the command design pattern describes the following solution:

- Define separate **(command) objects that encapsulate a request**
- A class **delegates a request to a command object** instead of implementing a particular request directly

This enables one to configure a class with a command object that is used to perform a request. The class is no longer coupled to a particular request and has no knowledge of how the request is carried out.

### When is it especially useful?


The Command Pattern is especially useful for:

1. **Decoupling** - Decouples the object that requests an operation (invoker) from the one that performs it (receiver)
2. **Reusability** - Commands can be reused and combined in complex scenarios
3. **History and Undo** - Allows for history and undo features (crucial in text editors, drawing apps)
4. **Logging** - Commands can be logged for debugging and auditing purposes
5. **Queueing** - Commands can be queued and executed later

### Объяснение


**Explanation**:

- **Command interface** declares `execute()` method
- **Concrete commands** encapsulate action and receiver
- **Invoker** (RemoteControl, CommandManager) executes commands
- **Receiver** (Light, TextEditor) performs the actual work
- **Android**: Useful for undo/redo, action queuing, transaction management

### Pros (Преимущества)


1. **Decoupling** - Separates invoker from receiver
2. **Reusability** - Commands can be reused and combined
3. **Undo/Redo** - Easy to implement undo/redo
4. **Logging** - Commands can be logged for auditing
5. **Queueing** - Commands can be queued and executed later
6. **Macro commands** - Combine multiple commands

### Cons (Недостатки)


1. **Increased classes** - Each command needs a class
2. **Complexity** - More complex for simple operations
3. **Memory overhead** - Storing command history uses memory
4. **Indirection** - Extra layer of indirection
