---
id: 20251012-12271111123
title: "Kotlin Delegation By Restriction / Ограничения делегирования в Kotlin"
aliases: []
topic: computer-science
subtopics: [functions, access-modifiers, class-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-sequences-detailed--kotlin--medium, q-kotlin-init-block--kotlin--easy, q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Можно ли после by вызвать функцию или конструктор?

# Question (EN)
> Can you call a function or constructor after `by`?

# Вопрос (RU)
> Можно ли после by вызвать функцию или конструктор?

---

## Answer (EN)

**No**, you cannot call functions or constructors after `by`. The `by` keyword expects a **ready object** that implements an interface or delegates a property.

**Why this restriction:**

The `by` keyword requires an **instance**, not an expression that creates an instance.

- **Incorrect - Cannot call constructor:**
```kotlin
interface Printer {
    fun print()
}

class ConsolePrinter : Printer {
    override fun print() = println("Printing...")
}

// - ERROR: Cannot call constructor
class Document : Printer by ConsolePrinter()  // Compilation error
```

- **Correct - Pass an instance:**
```kotlin
// Option 1: Pass as constructor parameter
class Document(printer: Printer) : Printer by printer

val doc = Document(ConsolePrinter())
doc.print()

// Option 2: Use default value
class Document(printer: Printer = ConsolePrinter()) : Printer by printer

val doc2 = Document()
doc2.print()

// Option 3: Create instance separately
class Document : Printer by printerInstance {
    companion object {
        private val printerInstance = ConsolePrinter()
    }
}
```

**Property Delegation - Same Rule:**

- **Cannot call function:**
```kotlin
// - ERROR
val name: String by lazy()  // Compilation error
```

- **Correct - lazy is a function that returns delegate:**
```kotlin
// - CORRECT - lazy{} returns ReadOnlyProperty delegate
val name: String by lazy { "Alice" }

// - CORRECT - observable() returns delegate
var age: Int by Delegates.observable(0) { _, old, new ->
    println("Age changed from $old to $new")
}
```

**How Delegation Works:**

```kotlin
// Interface delegation
interface Base {
    fun doSomething()
}

class BaseImpl : Base {
    override fun doSomething() = println("Doing something")
}

// by expects an object implementing Base
class Derived(b: Base) : Base by b

// Usage
val base = BaseImpl()
val derived = Derived(base)  // Pass instance
derived.doSomething()
```

**Property Delegation Pattern:**

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

// Custom delegate
class LoggedProperty<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} = $value")
        this.value = value
    }
}

class User {
    // by expects delegate instance
    var name: String by LoggedProperty("Unknown")
}

val user = User()
user.name = "Alice"  // Setting name = Alice
println(user.name)    // Getting name = Alice
```

**Common Delegates:**

```kotlin
class Example {
    // - lazy - returns delegate
    val lazyValue: String by lazy { "Computed once" }

    // - observable - returns delegate
    var observedValue: Int by Delegates.observable(0) { _, old, new ->
        println("Changed from $old to $new")
    }

    // - vetoable - returns delegate
    var vetoableValue: Int by Delegates.vetoable(0) { _, old, new ->
        new > old  // Only allow increases
    }

    // - notNull - returns delegate
    var notNullValue: String by Delegates.notNull()

    // - Custom delegate instance
    var customValue: String by LoggedProperty("Initial")
}
```

**Workaround for Constructor Call:**

```kotlin
// If you must construct, use a factory function
fun createPrinter(): Printer = ConsolePrinter()

class Document : Printer by createPrinter()

// Or use object expression
class Document : Printer by object : Printer {
    override fun print() = println("Printing...")
}
```

**Summary:**

- **Cannot**: `by ConstructorCall()` or `by functionCall()`
- **Must**: `by existingInstance` or `by delegateFunction { ... }`
- **Reason**: `by` expects a delegate **instance**, not a creation expression
- **Exception**: Functions like `lazy {}` return delegates, so `by lazy {}` works

---

## Ответ (RU)

**Нет**, после `by` нельзя вызывать функции или конструкторы. Ключевое слово `by` ожидает **готовый объект**, который реализует интерфейс или делегирует свойство.

**Почему это ограничение:**

Ключевое слово `by` требует **экземпляр**, а не выражение, которое создаёт экземпляр.

- **Неправильно - Нельзя вызывать конструктор:**
```kotlin
interface Printer {
    fun print()
}

class ConsolePrinter : Printer {
    override fun print() = println("Печать...")
}

// - ОШИБКА: Нельзя вызывать конструктор
class Document : Printer by ConsolePrinter()  // Ошибка компиляции
```

- **Правильно - Передать экземпляр:**
```kotlin
// Вариант 1: Передать как параметр конструктора
class Document(printer: Printer) : Printer by printer

val doc = Document(ConsolePrinter())
doc.print()

// Вариант 2: Использовать значение по умолчанию
class Document(printer: Printer = ConsolePrinter()) : Printer by printer

val doc2 = Document()
doc2.print()

// Вариант 3: Создать экземпляр отдельно
class Document : Printer by printerInstance {
    companion object {
        private val printerInstance = ConsolePrinter()
    }
}
```

**Делегирование свойств - То же правило:**

- **Нельзя вызывать функцию:**
```kotlin
// - ОШИБКА
val name: String by lazy()  // Ошибка компиляции
```

- **Правильно - lazy это функция, которая возвращает делегат:**
```kotlin
// - ПРАВИЛЬНО - lazy{} возвращает ReadOnlyProperty делегат
val name: String by lazy { "Алиса" }

// - ПРАВИЛЬНО - observable() возвращает делегат
var age: Int by Delegates.observable(0) { _, old, new ->
    println("Возраст изменился с $old на $new")
}
```

**Как работает делегирование:**

```kotlin
// Делегирование интерфейса
interface Base {
    fun doSomething()
}

class BaseImpl : Base {
    override fun doSomething() = println("Делаю что-то")
}

// by ожидает объект, реализующий Base
class Derived(b: Base) : Base by b

// Использование
val base = BaseImpl()
val derived = Derived(base)  // Передаём экземпляр
derived.doSomething()
```

**Паттерн делегирования свойств:**

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

// Пользовательский делегат
class LoggedProperty<T>(private var value: T) : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Получение ${property.name} = $value")
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Установка ${property.name} = $value")
        this.value = value
    }
}

class User {
    // by ожидает экземпляр делегата
    var name: String by LoggedProperty("Неизвестно")
}

val user = User()
user.name = "Алиса"  // Установка name = Алиса
println(user.name)    // Получение name = Алиса
```

**Общие делегаты:**

```kotlin
class Example {
    // - lazy - возвращает делегат
    val lazyValue: String by lazy { "Вычислено однажды" }

    // - observable - возвращает делегат
    var observedValue: Int by Delegates.observable(0) { _, old, new ->
        println("Изменено с $old на $new")
    }

    // - vetoable - возвращает делегат
    var vetoableValue: Int by Delegates.vetoable(0) { _, old, new ->
        new > old  // Разрешить только увеличение
    }

    // - notNull - возвращает делегат
    var notNullValue: String by Delegates.notNull()

    // - Пользовательский экземпляр делегата
    var customValue: String by LoggedProperty("Начальное")
}
```

**Обходной путь для вызова конструктора:**

```kotlin
// Если нужно вызвать конструктор, используйте фабричную функцию
fun createPrinter(): Printer = ConsolePrinter()

class Document : Printer by createPrinter()

// Или используйте объектное выражение
class Document : Printer by object : Printer {
    override fun print() = println("Печать...")
}
```

**Резюме:**

- **Нельзя**: `by ConstructorCall()` или `by functionCall()`
- **Нужно**: `by existingInstance` или `by delegateFunction { ... }`
- **Причина**: `by` ожидает **экземпляр** делегата, а не выражение создания
- **Исключение**: Функции типа `lazy {}` возвращают делегаты, поэтому `by lazy {}` работает

## Related Questions

- [[q-sequences-detailed--kotlin--medium]]
- [[q-kotlin-init-block--kotlin--easy]]
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]]
