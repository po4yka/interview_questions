---
id: cs-026
title: "Delegates Java Compilation / Компиляция делегатов в Java"
aliases: ["Delegates Java Compilation", "Компиляция делегатов в Java"]
topic: cs
subtopics: [compilation, delegates, kotlin, programming-languages]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: []
created: 2025-10-15
updated: 2025-01-25
tags: [compilation, delegates, delegation, difficulty/hard, kotlin, kotlin-compiler, programming-languages]
sources: [https://kotlinlang.org/docs/delegated-properties.html]
date created: Friday, October 3rd 2025, 4:39:28 pm
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Как делегаты Kotlin компилируются в Java? Что генерирует компилятор для property delegation?

# Question (EN)
> How do Kotlin delegates compile to Java? What does the compiler generate for property delegation?

---

## Ответ (RU)

**Теория компиляции делегатов:**
Kotlin `by` delegation позволяет переопределять поведение properties, делегируя их другим объектам. На уровне компиляции Java Kotlin компилятор генерирует helper classes и accessor methods. Delegation pattern реализуется через syntactic sugar - компилятор разворачивает delegation в regular method calls. Создаются внутренние классы для хранения delegate объектов.

**Property Delegation Compilation:**

*Теория:* Ключевое слово `by` - syntactic sugar. Компилятор разворачивает его в Java code с helper classes. Для каждого delegated property генерируется: helper class для хранения delegate, getter/setter методы, которые используют helper.

```kotlin
// ✅ Kotlin source code
class Example {
    val name by lazy { "Hello" }
    var age by Delegates.observable(0) { _, _, _ -> }
}

// Компилятор генерирует (псевдокод):
class Example {
    private val name$delegate: Lazy<String> = /* lazy initialization */
    private var age$delegate: ObservableProperty<Int> = /* observable setup */

    fun getName(): String = name$delegate.getValue(this, ::name)
    fun getAge(): Int = age$delegate.getValue(this, ::age)
    fun setAge(value: Int) = age$delegate.setValue(this, ::age, value)
}
```

**Property Delegate Interface:**

*Теория:* Любой класс с `getValue`/`setValue` может быть delegate. Компилятор ищет эти operator functions. Для `val` достаточно `getValue`, для `var` нужны оба. Сигнатуры определяются конвенцией, компилятор проверяет их existence.

```kotlin
// ✅ Delegate interface (упрощённо)
interface ReadWriteProperty<in R, T> {
    operator fun getValue(thisRef: R, property: KProperty<*>): T
    operator fun setValue(thisRef: R, property: KProperty<*>, value: T)
}

// Реализация
class MyDelegate<T> : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return /* value */
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        /* store value */
    }
}
```

**Standard Delegates - Lazy:**

*Теория:* `lazy` initialization создаёт Lazy object, который хранит lambda и cached value. Первый вызов execute lambda и cache result, последующие возвращают cached value. Thread-safe по умолчанию (использует synchronization).

```kotlin
// ✅ Lazy delegation
class Example {
    val expensive: String by lazy {
        println("Computing...")
        "Expensive Result"
    }
}

// Компилятор генерирует:
class Example {
    private val expensive$delegate: Lazy<String> = lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        println("Computing...")
        "Expensive Result"
    }

    fun getExpensive(): String = expensive$delegate.getValue(this, ::expensive)
}

// Синхронный код:
LazyImpl(initializer, SYNCHRONIZED) {
    @Nullable
    private volatile Object _value;

    synchronized {
        if (_value == null) {
            _value = initializer.invoke()
        }
        return _value
    }
}
```

**Standard Delegates - Observable:**

*Теория:* `Delegates.observable` создаёт ObservableProperty, который хранит value и onChange callback. При setValue вызывается callback с old и new values. Позволяет отслеживать изменения properties.

```kotlin
// ✅ Observable delegation
class Example {
    var name: String by Delegates.observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Компилятор генерирует:
class Example {
    private val name$delegate = object : ObservableProperty<String>("") {
        override fun afterChange(property: KProperty<*>, oldValue: String, newValue: String) {
            println("$oldValue -> $newValue")
        }
    }

    fun getName(): String = name$delegate.getValue(this, ::name)
    fun setName(value: String) {
        name$delegate.setValue(this, ::name, value)
    }
}
```

**Standard Delegates - Vetoable:**

*Теория:* `Delegates.vetoable` позволяет vetoing changes. callback возвращает Boolean - если false, изменение отклоняется. Полезно для validation.

```kotlin
// ✅ Vetoable delegation
class Example {
    var age: Int by Delegates.vetoable(0) { _, old, new ->
        new >= 0  // Валидация: age >= 0
    }
}

// Компилятор генерирует beforeChange callback:
ObservableProperty<T> {
    fun setValue(thisRef: R, property: KProperty<*>, value: T) {
        if (beforeChange.invoke(property, oldValue, value)) {
            _value = value
            afterChange(property, oldValue, value)
        } else {
            // Change vetoed
        }
    }
}
```

**Custom Delegates:**

*Теория:* Можно создавать custom delegates, реализуя `getValue`/`setValue`. Компилятор ищет эти operator functions для pattern matching. Supports extension functions для delegation к property другой object.

```kotlin
// ✅ Custom delegate
class CustomDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        this.value = value
    }
}

class Example {
    var name: String by CustomDelegate("default")
}

// Компилятор ищет операторные функции
// getValue/setValue в scope

// ✅ Extension delegation
class Example {
    val map: Map<String, String> = mapOf("key" to "value")
    val name by map  // Делегирует к map.get("name")
}

// Компилятор генерирует:
fun getName(): String = map.getValue(this, ::name)
// map.getValue проверяет наличие key в map
```

**Delegate Selection Process:**

*Теория:* Компилятор выбирает delegate через operator overloading resolution. Ищет `getValue`/`setValue` functions с правильными signatures. Precedence: implicit receiver > explicit receiver > extension functions. Может использовать reflection для KProperty metadata.

**Ключевые концепции:**

1. **Syntactic Sugar** - `by` keyword разворачивается в method calls
2. **Helper Classes** - генерируются внутренние классы для storage
3. **Operator Functions** - getValue/setValue определяют delegate contracts
4. **Lazy Thread-Safety** - по умолчанию SYNCHRONIZED
5. **Delegation Pattern** - позволяет reuse behavior без inheritance

## Answer (EN)

**Delegate Compilation Theory:**
Kotlin `by` delegation allows overriding property behavior, delegating it to other objects. At Java compilation level, Kotlin compiler generates helper classes and accessor methods. Delegation pattern implemented through syntactic sugar - compiler unwraps delegation into regular method calls. Creates internal classes for storing delegate objects.

**Property Delegation Compilation:**

*Theory:* `by` keyword - syntactic sugar. Compiler unwraps it into Java code with helper classes. For each delegated property generates: helper class for storing delegate, getter/setter methods that use helper.

```kotlin
// ✅ Kotlin source code
class Example {
    val name by lazy { "Hello" }
    var age by Delegates.observable(0) { _, _, _ -> }
}

// Compiler generates (pseudo-code):
class Example {
    private val name$delegate: Lazy<String> = /* lazy initialization */
    private var age$delegate: ObservableProperty<Int> = /* observable setup */

    fun getName(): String = name$delegate.getValue(this, ::name)
    fun getAge(): Int = age$delegate.getValue(this, ::age)
    fun setAge(value: Int) = age$delegate.setValue(this, ::age, value)
}
```

**Property Delegate Interface:**

*Theory:* Any class with `getValue`/`setValue` can be delegate. Compiler looks for these operator functions. For `val` only `getValue` needed, for `var` both needed. Signatures defined by convention, compiler checks their existence.

```kotlin
// ✅ Delegate interface (simplified)
interface ReadWriteProperty<in R, T> {
    operator fun getValue(thisRef: R, property: KProperty<*>): T
    operator fun setValue(thisRef: R, property: KProperty<*>, value: T)
}

// Implementation
class MyDelegate<T> : ReadWriteProperty<Any?, T> {
    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return /* value */
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        /* store value */
    }
}
```

**Standard Delegates - Lazy:**

*Theory:* `lazy` initialization creates Lazy object storing lambda and cached value. First call executes lambda and caches result, subsequent calls return cached value. Thread-safe by default (uses synchronization).

```kotlin
// ✅ Lazy delegation
class Example {
    val expensive: String by lazy {
        println("Computing...")
        "Expensive Result"
    }
}

// Compiler generates:
class Example {
    private val expensive$delegate: Lazy<String> = lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        println("Computing...")
        "Expensive Result"
    }

    fun getExpensive(): String = expensive$delegate.getValue(this, ::expensive)
}

// Synchronized code:
LazyImpl(initializer, SYNCHRONIZED) {
    @Nullable
    private volatile Object _value;

    synchronized {
        if (_value == null) {
            _value = initializer.invoke()
        }
        return _value
    }
}
```

**Standard Delegates - Observable:**

*Theory:* `Delegates.observable` creates ObservableProperty storing value and onChange callback. On setValue calls callback with old and new values. Allows tracking property changes.

```kotlin
// ✅ Observable delegation
class Example {
    var name: String by Delegates.observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Compiler generates:
class Example {
    private val name$delegate = object : ObservableProperty<String>("") {
        override fun afterChange(property: KProperty<*>, oldValue: String, newValue: String) {
            println("$oldValue -> $newValue")
        }
    }

    fun getName(): String = name$delegate.getValue(this, ::name)
    fun setName(value: String) {
        name$delegate.setValue(this, ::name, value)
    }
}
```

**Standard Delegates - Vetoable:**

*Theory:* `Delegates.vetoable` allows vetoing changes. Callback returns Boolean - if false, change rejected. Useful for validation.

```kotlin
// ✅ Vetoable delegation
class Example {
    var age: Int by Delegates.vetoable(0) { _, old, new ->
        new >= 0  // Validation: age >= 0
    }
}

// Compiler generates beforeChange callback:
ObservableProperty<T> {
    fun setValue(thisRef: R, property: KProperty<*>, value: T) {
        if (beforeChange.invoke(property, oldValue, value)) {
            _value = value
            afterChange(property, oldValue, value)
        } else {
            // Change vetoed
        }
    }
}
```

**Custom Delegates:**

*Theory:* Can create custom delegates implementing `getValue`/`setValue`. Compiler looks for these operator functions for pattern matching. Supports extension functions for delegating to property of another object.

```kotlin
// ✅ Custom delegate
class CustomDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        this.value = value
    }
}

class Example {
    var name: String by CustomDelegate("default")
}

// Compiler looks for operator functions
// getValue/setValue in scope

// ✅ Extension delegation
class Example {
    val map: Map<String, String> = mapOf("key" to "value")
    val name by map  // Delegates to map.get("name")
}

// Compiler generates:
fun getName(): String = map.getValue(this, ::name)
// map.getValue checks for key presence in map
```

**Delegate Selection Process:**

*Theory:* Compiler selects delegate through operator overloading resolution. Looks for `getValue`/`setValue` functions with correct signatures. Precedence: implicit receiver > explicit receiver > extension functions. Can use reflection for KProperty metadata.

**Key Concepts:**

1. **Syntactic Sugar** - `by` keyword unwraps into method calls
2. **Helper Classes** - internal classes generated for storage
3. **Operator Functions** - getValue/setValue define delegate contracts
4. **Lazy Thread-Safety** - default SYNCHRONIZED mode
5. **Delegation Pattern** - allows reusing behavior without inheritance

---

## Follow-ups

- How does lazy initialization work with synchronization?
- Can you create delegates for functions, not just properties?
- What is the performance impact of property delegation?

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin properties
- Kotlin operator overloading

### Related (Same Level)
- [[q-kotlin-delegates--kotlin--medium]] - Delegates overview
- [[q-lazy-delegation--kotlin--medium]] - Lazy initialization

### Advanced (Harder)
- [[q-property-delegation--kotlin--hard]] - Advanced delegation patterns
- Kotlin compiler internals
- Bytecode generation
