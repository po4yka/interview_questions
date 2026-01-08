---id: cs-026
title: "Delegates Java Compilation / Компиляция делегатов в Java"
aliases: ["Delegates Java Compilation", "Компиляция делегатов в Java"]
topic: cs
subtopics: [compilation, delegates, kotlin]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml]
created: 2025-10-15
updated: 2025-11-11
tags: [compilation, delegates, delegation, difficulty/hard, kotlin, kotlin-compiler, programming-languages]
sources: ["https://kotlinlang.org/docs/delegated-properties.html"]

---
# Вопрос (RU)
> Как делегаты Kotlin компилируются в Java? Что генерирует компилятор для property delegation?

# Question (EN)
> How do Kotlin delegates compile to Java? What does the compiler generate for property delegation?

---

## Ответ (RU)

**Теория компиляции делегатов:**
Kotlin `by` delegation позволяет переопределять поведение свойств, делегируя его другим объектам. На байткод-уровне (и в сгенерированном Java-псевдокоде) компилятор Kotlin разворачивает `by` в обычные поля и вызовы методов. Для делегированного свойства создаётся приватное поле-хранилище делегата (`<имя>$delegate`), а `getter`/`setter` преобразуются в вызовы `getValue`/`setValue` делегата. Это чистый syntactic sugar: дополнительного скрытого интерфейса или универсального helper-класса специально под конкретное свойство не генерируется (используются уже существующие типы делегатов вроде `Lazy`, `ObservableProperty` и т.п.).

**Property Delegation Compilation:**

*Теория:* Ключевое слово `by` — syntactic sugar. Для каждого делегированного свойства компилятор:
- создаёт приватное поле `<propertyName>$delegate` типа делегата;
- генерирует `getter`/`setter`, которые вызывают `delegate.getValue(thisRef, property)` / `delegate.setValue(thisRef, property, value)`.

```kotlin
// Kotlin исходный код
class Example {
    val name by lazy { "Hello" }
    var age by Delegates.observable(0) { _, _, _ -> }
}

// Компилятор генерирует (упрощённый псевдокод на Java-стиле):
class Example {
    private final Lazy<String> name$delegate = kotlin.LazyKt.lazy(() -> "Hello");
    private final ObservableProperty<Integer> age$delegate =
        Delegates.observable(0, (prop, old, new) -> { /* ... */ });

    public String getName() {
        return name$delegate.getValue(this, /* KProperty для name */);
    }

    public int getAge() {
        return age$delegate.getValue(this, /* KProperty для age */);
    }

    public void setAge(int value) {
        age$delegate.setValue(this, /* KProperty для age */, value);
    }
}
```

(Использование `::name` в псевдокоде отражает передачу `KProperty`, фактически компилятор генерирует соответствующие статические дескрипторы `KProperty`.)

**Property Delegate Interface:**

*Теория:* Любой тип, для которого доступны функции `operator fun getValue` и (для `var`) `operator fun setValue` с подходящими сигнатурами, может использоваться как делегат. Компилятор ищет эти operator-функции по делегату и его расширениям. Для `val` достаточно `getValue`, для `var` требуются оба. Сигнатуры определены конвенцией; компилятор строго проверяет их наличие и совместимость типов.

```kotlin
// Официальный интерфейс (упрощённо)
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

*Теория:* `lazy { ... }` создаёт объект `Lazy<T>`, который хранит лямбда-инициализатор и кэшированное значение. При первом вызове `getValue` инициализатор выполняется и результат кэшируется, последующие вызовы возвращают кэш. По умолчанию используется потокобезопасный режим `SYNCHRONIZED` (можно переопределить через `lazy(mode, initializer)`).

```kotlin
// Lazy delegation
class Example {
    val expensive: String by lazy {
        println("Computing...")
        "Expensive Result"
    }
}

// Компилятор (упрощённо) генерирует поле делегата и геттер:
class Example {
    private final Lazy<String> expensive$delegate = kotlin.LazyKt.lazy(() -> {
        System.out.println("Computing...");
        return "Expensive Result";
    });

    public String getExpensive() {
        return expensive$delegate.getValue(this, /* KProperty для expensive */);
    }
}

// Упрощённая идея потокобезопасной реализации (псевдокод):
final class SynchronizedLazyImpl<T>(initializer: () -> T) : Lazy<T> {
    @Volatile private var _value: Any? = UNINITIALIZED

    override fun getValue(): T {
        val v1 = _value
        if (v1 !== UNINITIALIZED) return v1 as T
        return synchronized(this) {
            val v2 = _value
            if (v2 !== UNINITIALIZED) v2 as T
            else {
                val typed = initializer()
                _value = typed
                typed
            }
        }
    }
}
```

**Standard Delegates - `Observable`:**

*Теория:* `Delegates.observable` создаёт `ObservableProperty`, который хранит значение и callback. При `setValue` вызывается callback с `KProperty`, старым и новым значением; после callback (если не vetoable) значение обновляется. Это реализуется конкретным классом в стандартной библиотеке; компилятор лишь вызывает его `getValue`/`setValue`.

```kotlin
// Observable delegation
class Example {
    var name: String by Delegates.observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Компилятор генерирует делегат и аксессоры (псевдокод):
class Example {
    private final ObservableProperty<String> name$delegate =
        Delegates.observable("", (prop, oldValue, newValue) -> {
            System.out.println(oldValue + " -> " + newValue);
        });

    public String getName() {
        return name$delegate.getValue(this, /* KProperty для name */);
    }

    public void setName(String value) {
        name$delegate.setValue(this, /* KProperty для name */, value);
    }
}
```

**Standard Delegates - Vetoable:**

*Теория:* `Delegates.vetoable` использует callback `beforeChange`, который возвращает `Boolean`. Если `false`, изменение отклоняется. Внутри стандартной реализации проверка делается до обновления значения.

```kotlin
// Vetoable delegation
class Example {
    var age: Int by Delegates.vetoable(0) { _, old, new ->
        new >= 0  // Валидация: age >= 0
    }
}

// Упрощённая структура реализации в stdlib (псевдокод):
abstract class ObservableProperty<T>(initialValue: T) : ReadWriteProperty<Any?, T> {
    protected open fun beforeChange(property: KProperty<*>, oldValue: T, newValue: T): Boolean = true
    protected open fun afterChange(property: KProperty<*>, oldValue: T, newValue: T) {}

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val oldValue = /* текущее значение */
        if (beforeChange(property, oldValue, value)) {
            // обновить значение
            afterChange(property, oldValue, value)
        }
    }
}
```

**Custom Delegates:**

*Теория:* Можно создавать свои делегаты, реализуя `operator getValue`/`setValue` как члены или extension-функции. Компилятор при разборе `by` ищет подходящие operator-функции для типа делегата в соответствии с обычными правилами разрешения перегрузок.

```kotlin
// Custom delegate
class CustomDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        this.value = value
    }
}

class Example {
    var name: String by CustomDelegate("default")
}

// Компилятор разворачивает name в поле name$delegate и вызывает
// name$delegate.getValue(this, property) / setValue(...)

// Делегирование к Map через extension-делегаты стандартной библиотеки
class Example {
    private val map: Map<String, String> = mapOf("name" to "value")
    val name: String by map  // Делегат ищется через extension fun Map.getValue
}

// Упрощённо (идея, не точный байткод):
operator fun <V> Map<String, V>.getValue(thisRef: Any?, property: KProperty<*>): V =
    get(property.name) ?: throw NoSuchElementException("Key ${property.name} is missing in the map.")

class Example {
    private final Map<String, String> map = ...;
    private final Map<String, String> name$delegate = map;

    public String getName() {
        return MapsKt.getValue(name$delegate, this, /* KProperty для name */);
    }
}
```

**Delegate Selection Process:**

*Теория:* При компиляции `val/var x by expr` компилятор:
- вычисляет тип делегата `D` как тип `expr`;
- ищет `operator fun D.getValue(thisRef, property)` и (для `var`) `operator fun D.setValue(...)` как членские или extension-функции;
- применяет стандартные правила разрешения перегрузок Kotlin (учитываются видимость, implicit/explicit receivers и расширения). Если подходящих функций нет или сигнатуры не совпадают, это ошибка компиляции.

Метаданные `KProperty` могут использоваться делегатом (например, для имени свойства), но сама передача `KProperty` — это деталь сгенерированного кода, не «reflection на каждом шаге» в смысле полного рефлексивного поиска.

**Ключевые концепции:**

1. `by` — syntactic sugar: разворачивается в хранение делегата и вызовы `getValue`/`setValue`.
2. Делегат хранится в приватном поле `<name>$delegate`; специальных helper-классов под каждое свойство не создаётся.
3. Контракт делегата задаётся operator-функциями `getValue`/`setValue` (членами или extension-функциями) с фиксированными сигнатурами.
4. `lazy` по умолчанию потокобезопасен (`SYNCHRONIZED`), но режим настраивается.
5. Механизм свойств-делегатов реализует шаблон delegation без наследования и прозрачно для вызова кода.

## Answer (EN)

**Delegate Compilation Theory:**
Kotlin `by` delegation lets you customize property behavior by delegating it to another object. At the bytecode (and decompiled Java) level, the Kotlin compiler expands `by` into regular fields and method calls. For a delegated property, it generates a private delegate field (`<name>$delegate`), and the property accessors (`get`/`set`) call the delegate's `getValue`/`setValue`. This is pure syntactic sugar: no special per-property helper interface/class is invented; existing delegate types like `Lazy`, `ObservableProperty`, etc. are used.

**Property Delegation Compilation:**

*Theory:* The `by` keyword is syntactic sugar. For each delegated property the compiler:
- creates a private `<propertyName>$delegate` field of the delegate type;
- generates `getter`/`setter` that call `delegate.getValue(thisRef, property)` / `delegate.setValue(thisRef, property, value)`.

```kotlin
// Kotlin source code
class Example {
    val name by lazy { "Hello" }
    var age by Delegates.observable(0) { _, _, _ -> }
}

// Compiler generates (simplified Java-style pseudocode):
class Example {
    private final Lazy<String> name$delegate = kotlin.LazyKt.lazy(() -> "Hello");
    private final ObservableProperty<Integer> age$delegate =
        Delegates.observable(0, (prop, old, new) -> { /* ... */ });

    public String getName() {
        return name$delegate.getValue(this, /* KProperty for name */);
    }

    public int getAge() {
        return age$delegate.getValue(this, /* KProperty for age */);
    }

    public void setAge(int value) {
        age$delegate.setValue(this, /* KProperty for age */, value);
    }
}
```

(Using `::name` in pseudocode is shorthand for passing the corresponding `KProperty`; in actual bytecode the compiler uses generated `KProperty` references.)

**Property Delegate Interface:**

*Theory:* Any type for which appropriate `operator fun getValue` and (for `var`) `operator fun setValue` functions are available can serve as a delegate. The compiler looks for these operator functions (member or extension). For `val`, only `getValue` is required; for `var`, both are required. Signatures are defined by convention and are strictly validated.

```kotlin
// Official interface (simplified)
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

*Theory:* `lazy { ... }` creates a `Lazy<T>` object holding an initializer lambda and a cached value. On first `getValue` call, the lambda runs and the result is cached; subsequent calls return the cached value. By default it uses a thread-safe `SYNCHRONIZED` mode (configurable via `lazy(mode, initializer)`).

```kotlin
// Lazy delegation
class Example {
    val expensive: String by lazy {
        println("Computing...")
        "Expensive Result"
    }
}

// Compiler (simplified) generates a delegate field and getter:
class Example {
    private final Lazy<String> expensive$delegate = kotlin.LazyKt.lazy(() -> {
        System.out.println("Computing...");
        return "Expensive Result";
    });

    public String getExpensive() {
        return expensive$delegate.getValue(this, /* KProperty for expensive */);
    }
}

// Simplified idea of synchronized implementation (pseudocode):
final class SynchronizedLazyImpl<T>(initializer: () -> T) : Lazy<T> {
    @Volatile private var _value: Any? = UNINITIALIZED

    override fun getValue(): T {
        val v1 = _value
        if (v1 !== UNINITIALIZED) return v1 as T
        return synchronized(this) {
            val v2 = _value
            if (v2 !== UNINITIALIZED) v2 as T
            else {
                val typed = initializer()
                _value = typed
                typed
            }
        }
    }
}
```

**Standard Delegates - `Observable`:**

*Theory:* `Delegates.observable` creates an `ObservableProperty` that stores the value and an `onChange` callback. Its `setValue` calls the callback with the `KProperty`, old, and new values; then the value is updated (unless it's a vetoable variant). The compiler just uses this delegate type; it does not inject custom change-tracking logic.

```kotlin
// Observable delegation
class Example {
    var name: String by Delegates.observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Compiler generates delegate field and accessors (pseudocode):
class Example {
    private final ObservableProperty<String> name$delegate =
        Delegates.observable("", (prop, oldValue, newValue) -> {
            System.out.println(oldValue + " -> " + newValue);
        });

    public String getName() {
        return name$delegate.getValue(this, /* KProperty for name */);
    }

    public void setName(String value) {
        name$delegate.setValue(this, /* KProperty for name */, value);
    }
}
```

**Standard Delegates - Vetoable:**

*Theory:* `Delegates.vetoable` uses a `beforeChange` callback that returns a `Boolean`. If it returns `false`, the change is rejected; if `true`, the value is updated and `afterChange` can be run. This logic is implemented in the stdlib delegate, not by the compiler.

```kotlin
// Vetoable delegation
class Example {
    var age: Int by Delegates.vetoable(0) { _, old, new ->
        new >= 0  // Validation: age >= 0
    }
}

// Simplified structure in stdlib (pseudocode):
abstract class ObservableProperty<T>(initialValue: T) : ReadWriteProperty<Any?, T> {
    protected open fun beforeChange(property: KProperty<*>, oldValue: T, newValue: T): Boolean = true
    protected open fun afterChange(property: KProperty<*>, oldValue: T, newValue: T) {}

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val oldValue = /* current value */
        if (beforeChange(property, oldValue, value)) {
            // update value
            afterChange(property, oldValue, value)
        }
    }
}
```

**Custom Delegates:**

*Theory:* You can implement your own delegates by providing `operator getValue`/`setValue` as member or extension functions. When compiling `by`, the compiler performs normal overload resolution to find suitable operator functions for the delegate type.

```kotlin
// Custom delegate
class CustomDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        this.value = value
    }
}

class Example {
    var name: String by CustomDelegate("default")
}

// The compiler expands this to a name$delegate field and calls
// name$delegate.getValue(this, property) / setValue(...)

// Delegation to Map via stdlib extension delegates
class Example {
    private val map: Map<String, String> = mapOf("name" to "value")
    val name: String by map  // Uses Map.getValue extension delegate
}

// Conceptual implementation:
operator fun <V> Map<String, V>.getValue(thisRef: Any?, property: KProperty<*>): V =
    get(property.name) ?: throw NoSuchElementException("Key ${property.name} is missing in the map.")

class Example {
    private final Map<String, String> map = ...;
    private final Map<String, String> name$delegate = map;

    public String getName() {
        return MapsKt.getValue(name$delegate, this, /* KProperty for name */);
    }
}
```

**Delegate Selection Process:**

*Theory:* For `val/var x by expr` the compiler:
- infers delegate type `D` from `expr`;
- searches for suitable `operator getValue`/`setValue` for `D` (member first, then extensions),
  using standard Kotlin overload resolution (visibility, receivers, imports, etc.);
- if none match the required signatures, compilation fails.

`KProperty` parameters provide metadata (e.g., property name) to delegates; this is part of the generated code and does not imply an extra reflective lookup beyond what the delegate implementation itself does.

**Key Concepts:**

1. `by` is syntactic sugar: it becomes a delegate field and `getValue`/`setValue` calls.
2. The delegate is stored in a private `<name>$delegate` field; no extra per-property helper classes are generated.
3. Delegate contracts are defined by `getValue`/`setValue` operator functions (member or extension) with conventional signatures.
4. `lazy` is thread-safe by default (`SYNCHRONIZED`), configurable via `LazyThreadSafetyMode`.
5. Property delegation realizes the delegation pattern without inheritance and compiles down to straightforward bytecode.

---

## Дополнительные Вопросы (RU)

- Как работает ленившая инициализация (`lazy`) с точки зрения синхронизации?
- Можно ли создавать делегаты не только для свойств, но и для других конструкций?
- Каково влияние механизма делегирования свойств на производительность?

## Follow-ups

- How does lazy initialization work with synchronization?
- Can you create delegates for functions, not just properties?
- What is the performance impact of property delegation?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые свойства в Kotlin
- Перегрузка операторов в Kotlin

### Связанные (тот Же уровень)
- Обзор делегатов в Kotlin
- Ленивая инициализация через `lazy`

### Продвинутое (сложнее)
- Продвинутые паттерны делегирования свойств в Kotlin
- Внутреннее устройство компилятора Kotlin
- Генерация байткода

## Related Questions

### Prerequisites (Easier)
- Basic Kotlin properties
- Kotlin operator overloading

### Related (Same Level)
- Delegates overview
- Lazy initialization

### Advanced (Harder)
- Advanced delegation patterns
- Kotlin compiler internals
- Bytecode generation

## References

- [[c-computer-science]]
- [[c-compiler-optimization]]
