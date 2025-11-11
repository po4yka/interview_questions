---
id: cs-005
title: "Kotlin Delegation By Restriction / Ограничения делегирования в Kotlin"
aliases: []
topic: kotlin
subtopics: [functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c--kotlin--medium, q-kotlin-init-block--kotlin--easy, q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium, q-sequences-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [difficulty/medium, kotlin/functions]
---

# Вопрос (RU)
> Можно ли после `by` вызвать функцию или конструктор?

# Question (EN)
> Can you call a function or constructor after `by`?

---

## Ответ (RU)

Да. После `by` можно указывать любое выражение, тип которого соответствует ожидаемому делегату:
- для делегирования классов: выражение типа интерфейса (или суперкласса), которому делегируем;
- для делегирования свойств: выражение типа, в котором объявлены нужные оператор-функции `getValue`/`setValue`.

Таким выражением могут быть:
- уже существующий экземпляр (переменная, свойство);
- вызов конструктора (`ConsolePrinter()`);
- вызов функции, возвращающей нужный тип;
- объектное выражение.

Путаница обычно возникает из-за некорректных примеров или когда функция/конструктор возвращает неправильный тип.

**Правильно - Вызов конструктора разрешён:**
```kotlin
interface Printer {
    fun print()
}

class ConsolePrinter : Printer {
    override fun print() = println("Печать...")
}

// OK: ConsolePrinter() — выражение типа Printer
class Document : Printer by ConsolePrinter()
```

**Правильно - Передать как параметр конструктора:**
```kotlin
class Document(printer: Printer) : Printer by printer

val doc = Document(ConsolePrinter())
doc.print()
```

**Правильно - Значение по умолчанию:**
```kotlin
class Document(printer: Printer = ConsolePrinter()) : Printer by printer

val doc2 = Document()
doc2.print()
```

**Правильно - Создать экземпляр отдельно:**
```kotlin
class Document : Printer by printerInstance {
    companion object {
        private val printerInstance = ConsolePrinter()
    }
}
```

**Делегирование свойств - Тот же принцип:**

После `by` указывается выражение, тип которого имеет подходящие `operator fun getValue` (и при необходимости `setValue`). Вызов функции допускается, если она возвращает корректный делегат.

- **Неправильный пример (но по другой причине):**
```kotlin
// ОШИБКА: lazy() требует лямбда-аргумент; такой вызов не подходит ни под одну перегрузку
val name: String by lazy()  // Ошибка компиляции
```
Ошибка здесь из-за неверного вызова `lazy()`, а не из-за запрета функций после `by`.

- **Правильно - `lazy` это функция, которая возвращает делегат:**
```kotlin
// lazy { ... } возвращает Lazy<T>, который выступает делегатом
val name: String by lazy { "Алиса" }

// observable() возвращает делегат
import kotlin.properties.Delegates

var age: Int by Delegates.observable(0) { _, old, new ->
    println("Возраст изменился с $old на $new")
}
```

**Как работает делегирование классов:**

```kotlin
// Делегирование интерфейса
interface Base {
    fun doSomething()
}

class BaseImpl : Base {
    override fun doSomething() = println("Делаю что-то")
}

// `by` ожидает выражение типа Base
class Derived(b: Base) : Base by b

// Использование
val base = BaseImpl()
val derived = Derived(base)
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
    // после by указываем выражение, вычисляющееся в экземпляр делегата
    var name: String by LoggedProperty("Неизвестно")
}

val user = User()
user.name = "Алиса"  // Установка name = Алиса
println(user.name)    // Получение name = Алиса
```

**Общие делегаты:**

```kotlin
import kotlin.properties.Delegates

class Example {
    // lazy { ... } возвращает делегат
    val lazyValue: String by lazy { "Вычислено однажды" }

    // observable(...) возвращает делегат
    var observedValue: Int by Delegates.observable(0) { _, old, new ->
        println("Изменено с $old на $new")
    }

    // vetoable(...) возвращает делегат
    var vetoableValue: Int by Delegates.vetoable(0) { _, old, new ->
        new > old  // Разрешаем только увеличение
    }

    // notNull() возвращает делегат
    var notNullValue: String by Delegates.notNull<String>()

    // Пользовательский экземпляр делегата
    var customValue: String by LoggedProperty("Начальное")
}
```

**Примеры с фабрикой / объектным выражением:**

Этот вариант также корректен, так как `createPrinter()` — выражение, возвращающее `Printer`:
```kotlin
fun createPrinter(): Printer = ConsolePrinter()

class Document : Printer by createPrinter()
```

И объектное выражение тоже корректно:
```kotlin
class Document : Printer by object : Printer {
    override fun print() = println("Печать...")
}
```

**Резюме:**

- Разрешено: `by` с любым выражением требуемого типа делегата, включая `ConstructorCall()` и `functionCall()`.
- Не разрешено: выражения, тип которых не удовлетворяет требованиям делегирования (например, некорректный вызов `lazy()`).
- Ключевая идея: `by` использует значение выражения как делегат; вызовы функций и конструкторов не запрещены сами по себе.

## Answer (EN)

Yes. After `by` you can use any expression whose type matches the expected delegate:
- for class delegation: an expression of the interface (or superclass) type you delegate to;
- for property delegation: an expression of a type that provides the required `getValue`/`setValue` operator functions.

That expression may be:
- an existing instance (variable, property);
- a constructor call (`ConsolePrinter()`);
- a function call that returns the correct type;
- an object expression.

The common confusion comes from misreading examples or from using a function/constructor with an incorrect type or signature.

**Correct - Constructor call is allowed:**
```kotlin
interface Printer {
    fun print()
}

class ConsolePrinter : Printer {
    override fun print() = println("Printing...")
}

// OK: ConsolePrinter() is an expression of type Printer
class Document : Printer by ConsolePrinter()
```

**Correct - Pass as constructor parameter:**
```kotlin
class Document(printer: Printer) : Printer by printer

val doc = Document(ConsolePrinter())
doc.print()
```

**Correct - Use default value:**
```kotlin
class Document(printer: Printer = ConsolePrinter()) : Printer by printer

val doc2 = Document()
doc2.print()
```

**Correct - Create instance separately:**
```kotlin
class Document : Printer by printerInstance {
    companion object {
        private val printerInstance = ConsolePrinter()
    }
}
```

**Property Delegation - Same Principle:**

After `by` you provide an expression whose type has appropriate `operator fun getValue` (and optionally `setValue`). That expression can be a function call as long as its return type is a valid delegate.

- **Incorrect example (but for the right reason):**
```kotlin
// ERROR: lazy() requires a lambda argument; this call does not match any overload
val name: String by lazy()  // Compilation error
```
The error here is due to calling `lazy()` without the required lambda, not because calling a function is forbidden after `by`.

- **Correct - `lazy` is a function that returns a delegate:**
```kotlin
// lazy { ... } returns a Lazy<T> that acts as a delegate
val name: String by lazy { "Alice" }

// observable() returns a delegate
import kotlin.properties.Delegates

var age: Int by Delegates.observable(0) { _, old, new ->
    println("Age changed from $old to $new")
}
```

**How Class Delegation Works:**

```kotlin
// Interface delegation
interface Base {
    fun doSomething()
}

class BaseImpl : Base {
    override fun doSomething() = println("Doing something")
}

// `by` expects an expression of type Base
class Derived(b: Base) : Base by b

// Usage
val base = BaseImpl()
val derived = Derived(base)
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
    // by expects an expression that evaluates to a delegate instance
    var name: String by LoggedProperty("Unknown")
}

val user = User()
user.name = "Alice"  // Setting name = Alice
println(user.name)    // Getting name = Alice
```

**Common Delegates:**

```kotlin
import kotlin.properties.Delegates

class Example {
    // lazy(...) returns a delegate
    val lazyValue: String by lazy { "Computed once" }

    // observable(...) returns a delegate
    var observedValue: Int by Delegates.observable(0) { _, old, new ->
        println("Changed from $old to $new")
    }

    // vetoable(...) returns a delegate
    var vetoableValue: Int by Delegates.vetoable(0) { _, old, new ->
        new > old  // Only allow increases
    }

    // notNull() returns a delegate
    var notNullValue: String by Delegates.notNull<String>()

    // Custom delegate instance
    var customValue: String by LoggedProperty("Initial")
}
```

**Workaround / Factory Examples:**

This pattern is also valid because `createPrinter()` is an expression returning a `Printer`:
```kotlin
fun createPrinter(): Printer = ConsolePrinter()

class Document : Printer by createPrinter()
```

And an object expression is valid as well:
```kotlin
class Document : Printer by object : Printer {
    override fun print() = println("Printing...")
}
```

**Summary:**

- Allowed: `by` followed by any expression of the required delegate type, including `ConstructorCall()` or `functionCall()`.
- Not allowed: using an expression whose type does not satisfy the delegation requirements (e.g., wrong type, wrong `lazy()` usage).
- Key idea: `by` uses the value of the expression as the delegate; it does not forbid function or constructor calls.

## Дополнительные вопросы (RU)

- Как компилятор разворачивает синтаксис делегирования под капотом в Kotlin?
- Каковы накладные расходы и особенности производительности при использовании делегирования по сравнению с прямой реализацией?
- Как внутренне устроены делегаты свойств `lazy`, `observable` и `vetoable`?

## Follow-ups

- How does the compiler rewrite delegation syntax under the hood in Kotlin?
- What are the performance implications of using delegation vs direct implementation?
- How do property delegates like `lazy`, `observable`, and `vetoable` work internally?

## Ссылки (RU)

- [[c--kotlin--medium]]
- [[q-kotlin-init-block--kotlin--easy]]
- [[q-sequences-detailed--kotlin--medium]]
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]]

## References

- [[c--kotlin--medium]]
- [[q-kotlin-init-block--kotlin--easy]]
- [[q-sequences-detailed--kotlin--medium]]
- [[q-lifecycle-scopes-viewmodelscope-lifecyclescope--kotlin--medium]]
