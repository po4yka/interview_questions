---
id: cs-034
title: "Command Pattern / Паттерн Command"
aliases: ["Command Pattern", "Паттерн Command"]
topic: cs
subtopics: [behavioral-patterns, design-patterns, gof-patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-command-pattern]
created: 2025-10-15
updated: 2025-01-25
tags: [behavioral-patterns, command, design-patterns, difficulty/medium, gof-patterns]
sources: [https://en.wikipedia.org/wiki/Command_pattern]
---

# Вопрос (RU)
> Что такое паттерн Command? Когда и зачем его использовать?

# Question (EN)
> What is the Command pattern? When and why should it be used?

---

## Ответ (RU)

**Теория паттерна Command:**
Command (Команда) - поведенческий паттерн проектирования, который инкапсулирует запрос как объект. Превращает запросы в stand-alone объекты, содержащие всю информацию о запросе. Позволяет параметризовать методы разными запросами, ставить запросы в очередь, логировать их и поддерживать отмену операций (undo/redo).

**Проблемы, которые решает:**

1. **Жёсткая связь** между invoker (вызывающим) и receiver (исполнителем)
2. **Невозможность параметризации** объектов разными запросами
3. **Отсутствие истории** выполненных операций
4. **Невозможность отмены** операций (undo/redo)
5. **Сложность логирования** и аудита операций

**Решение:**

*Теория:* Инкапсулировать запрос в отдельный объект (command). Invoker вызывает метод `execute()` на command объекте, не зная деталей реализации. Receiver выполняет фактическую работу. Command хранит ссылку на receiver и параметры запроса.

**Структура паттерна:**

- **Command** (интерфейс) - объявляет метод `execute()` и опционально `undo()`
- **ConcreteCommand** - реализует `execute()`, хранит receiver и параметры
- **Receiver** - выполняет фактическую работу
- **Invoker** - вызывает `execute()` на command, не зная деталей
- **Client** - создаёт command и связывает с receiver

**Когда использовать:**

✅ **Используйте Command:**
- Нужна отмена операций (undo/redo)
- Нужно логировать операции
- Нужна очередь запросов (queue)
- Нужна отложенная обработка (deferred execution)
- Нужно параметризовать объекты операциями
- Нужна транзакционная система (commit/rollback)

**Пример 1: Управление светом (базовый):**

```kotlin
// ✅ Command интерфейс
interface Command {
    fun execute()
}

// ✅ Concrete Commands
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

// ✅ Receiver
class Light {
    fun turnOn() = println("Light is ON")
    fun turnOff() = println("Light is OFF")
}

// ✅ Invoker
class RemoteControl {
    private var command: Command? = null

    fun setCommand(command: Command) {
        this.command = command
    }

    fun pressButton() {
        command?.execute()
    }
}

// ✅ Client
fun main() {
    val light = Light()
    val remote = RemoteControl()

    remote.setCommand(LightOnCommand(light))
    remote.pressButton()  // Light is ON

    remote.setCommand(LightOffCommand(light))
    remote.pressButton()  // Light is OFF
}
```

**Пример 2: Текстовый редактор с Undo/Redo:**

*Теория:* Для undo/redo нужно хранить историю команд. Каждая команда реализует метод `undo()`, который отменяет действие `execute()`. История хранится в стеке.

```kotlin
// ✅ Command с поддержкой undo
interface TextCommand {
    fun execute()
    fun undo()
}

// ✅ Команда вставки текста
class InsertTextCommand(
    private val editor: TextEditor,
    private val text: String,
    private val position: Int
) : TextCommand {
    override fun execute() {
        editor.insertText(text, position)
    }

    override fun undo() {
        editor.deleteText(position, text.length)
    }
}

// ✅ Команда удаления текста
class DeleteTextCommand(
    private val editor: TextEditor,
    private val position: Int,
    private val length: Int
) : TextCommand {
    private lateinit var deletedText: String

    override fun execute() {
        deletedText = editor.getText(position, length)
        editor.deleteText(position, length)
    }

    override fun undo() {
        editor.insertText(deletedText, position)
    }
}

// ✅ Receiver
class TextEditor {
    private val text = StringBuilder()

    fun insertText(newText: String, position: Int) {
        text.insert(position, newText)
    }

    fun deleteText(position: Int, length: Int) {
        text.delete(position, position + length)
    }

    fun getText(position: Int, length: Int) =
        text.substring(position, position + length)
}

// ✅ Invoker с историей
class CommandManager {
    private val history = ArrayDeque<TextCommand>()
    private val redoStack = ArrayDeque<TextCommand>()

    fun executeCommand(command: TextCommand) {
        command.execute()
        history.addLast(command)
        redoStack.clear()  // Очистить redo при новой команде
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
```

**Пример 3: Макрокоманды (Composite Command):**

*Теория:* Макрокоманда - команда, содержащая несколько команд. Выполняет все команды последовательно. Используется для группировки операций в транзакцию.

```kotlin
// ✅ Макрокоманда
class MacroCommand(private val commands: List<Command>) : Command {
    override fun execute() {
        commands.forEach { it.execute() }
    }
}

// ✅ Использование
fun main() {
    val light = Light()
    val fan = Fan()

    val macro = MacroCommand(listOf(
        LightOnCommand(light),
        FanOnCommand(fan)
    ))

    val remote = RemoteControl()
    remote.setCommand(macro)
    remote.pressButton()  // Включает свет и вентилятор
}
```

**Преимущества:**

1. **Decoupling** - invoker не зависит от receiver
2. **Open/Closed Principle** - можно добавлять новые команды без изменения invoker
3. **Single Responsibility** - команда инкапсулирует одну операцию
4. **Undo/Redo** - легко реализовать отмену операций
5. **Logging** - легко логировать все операции
6. **Queueing** - можно ставить команды в очередь
7. **Composite** - можно комбинировать команды (макрокоманды)

**Недостатки:**

1. **Увеличение количества классов** - каждая операция = отдельный класс
2. **Сложность** - для простых операций может быть избыточным
3. **Memory overhead** - история команд занимает память

**Связанные паттерны:**

- **Memento** - для сохранения состояния для undo
- **Composite** - для макрокоманд
- **Chain of Responsibility** - для передачи команд по цепочке
- **Strategy** - похожая структура, но разные цели

## Answer (EN)

**Command Pattern Theory:**
Command (Action) - behavioral design pattern that encapsulates request as object. Turns requests into stand-alone objects containing all information about request. Allows parameterizing methods with different requests, queueing requests, logging them, and supporting undo operations (undo/redo).

**Problems it Solves:**

1. **Tight coupling** between invoker (caller) and receiver (executor)
2. **Inability to parameterize** objects with different requests
3. **No history** of executed operations
4. **Inability to undo** operations (undo/redo)
5. **Difficult logging** and auditing of operations

**Solution:**

*Theory:* Encapsulate request in separate object (command). Invoker calls `execute()` method on command object, not knowing implementation details. Receiver performs actual work. Command stores reference to receiver and request parameters.

**Pattern Structure:**

- **Command** (interface) - declares `execute()` method and optionally `undo()`
- **ConcreteCommand** - implements `execute()`, stores receiver and parameters
- **Receiver** - performs actual work
- **Invoker** - calls `execute()` on command, not knowing details
- **Client** - creates command and links with receiver

**When to Use:**

✅ **Use Command:**
- Need operation undo (undo/redo)
- Need to log operations
- Need request queue
- Need deferred execution
- Need to parameterize objects with operations
- Need transactional system (commit/rollback)

**Example 1: Light Control (basic):**

```kotlin
// ✅ Command interface
interface Command {
    fun execute()
}

// ✅ Concrete Commands
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

// ✅ Receiver
class Light {
    fun turnOn() = println("Light is ON")
    fun turnOff() = println("Light is OFF")
}

// ✅ Invoker
class RemoteControl {
    private var command: Command? = null

    fun setCommand(command: Command) {
        this.command = command
    }

    fun pressButton() {
        command?.execute()
    }
}

// ✅ Client
fun main() {
    val light = Light()
    val remote = RemoteControl()

    remote.setCommand(LightOnCommand(light))
    remote.pressButton()  // Light is ON

    remote.setCommand(LightOffCommand(light))
    remote.pressButton()  // Light is OFF
}
```

**Example 2: Text Editor with Undo/Redo:**

*Theory:* For undo/redo need to store command history. Each command implements `undo()` method that reverses `execute()` action. History stored in stack.

```kotlin
// ✅ Command with undo support
interface TextCommand {
    fun execute()
    fun undo()
}

// ✅ Insert text command
class InsertTextCommand(
    private val editor: TextEditor,
    private val text: String,
    private val position: Int
) : TextCommand {
    override fun execute() {
        editor.insertText(text, position)
    }

    override fun undo() {
        editor.deleteText(position, text.length)
    }
}

// ✅ Delete text command
class DeleteTextCommand(
    private val editor: TextEditor,
    private val position: Int,
    private val length: Int
) : TextCommand {
    private lateinit var deletedText: String

    override fun execute() {
        deletedText = editor.getText(position, length)
        editor.deleteText(position, length)
    }

    override fun undo() {
        editor.insertText(deletedText, position)
    }
}

// ✅ Receiver
class TextEditor {
    private val text = StringBuilder()

    fun insertText(newText: String, position: Int) {
        text.insert(position, newText)
    }

    fun deleteText(position: Int, length: Int) {
        text.delete(position, position + length)
    }

    fun getText(position: Int, length: Int) =
        text.substring(position, position + length)
}

// ✅ Invoker with history
class CommandManager {
    private val history = ArrayDeque<TextCommand>()
    private val redoStack = ArrayDeque<TextCommand>()

    fun executeCommand(command: TextCommand) {
        command.execute()
        history.addLast(command)
        redoStack.clear()  // Clear redo on new command
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
```

**Example 3: Macro Commands (Composite Command):**

*Theory:* Macro command - command containing multiple commands. Executes all commands sequentially. Used for grouping operations into transaction.

```kotlin
// ✅ Macro command
class MacroCommand(private val commands: List<Command>) : Command {
    override fun execute() {
        commands.forEach { it.execute() }
    }
}

// ✅ Usage
fun main() {
    val light = Light()
    val fan = Fan()

    val macro = MacroCommand(listOf(
        LightOnCommand(light),
        FanOnCommand(fan)
    ))

    val remote = RemoteControl()
    remote.setCommand(macro)
    remote.pressButton()  // Turns on light and fan
}
```

**Advantages:**

1. **Decoupling** - invoker doesn't depend on receiver
2. **Open/Closed Principle** - can add new commands without changing invoker
3. **Single Responsibility** - command encapsulates one operation
4. **Undo/Redo** - easy to implement operation undo
5. **Logging** - easy to log all operations
6. **Queueing** - can queue commands
7. **Composite** - can combine commands (macro commands)

**Disadvantages:**

1. **Increased number of classes** - each operation = separate class
2. **Complexity** - may be overkill for simple operations
3. **Memory overhead** - command history takes memory

**Related Patterns:**

- **Memento** - for saving state for undo
- **Composite** - for macro commands
- **Chain of Responsibility** - for passing commands along chain
- **Strategy** - similar structure, different goals

---

## Follow-ups

- How do you implement undo/redo with Command pattern?
- What is the difference between Command and Strategy patterns?
- How do you handle command validation and error handling?

## Related Questions

### Prerequisites (Easier)
- Basic OOP concepts
