---
id: kotlin-169
title: "Delegates Compilation / Компиляция делегатов"
aliases: [Delegates Compilation, Компиляция делегатов]
topic: kotlin
subtopics: [delegation]
question_kind: theory
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-flow-backpressure--kotlin--hard, q-kotlin-delegation-detailed--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [advanced, bytecode, compilation, delegates, difficulty/hard, kotlin]
---
# Вопрос (RU)
> Как делегаты Kotlin работают на уровне компиляции? Какой bytecode и вспомогательные структуры генерируются?

---

# Question (EN)
> How do Kotlin delegates work at the compilation level? What bytecode and auxiliary structures are generated?

## Ответ (RU)

Kotlin property delegates (делегированные свойства) используют ключевое слово `by` для делегирования логики геттеров/сеттеров другому объекту. На уровне компиляции для свойств (class / top-level / extension in companion) компилятор Kotlin генерирует скрытое поле-делегат, массив метаданных `KProperty` и методы доступа, которые вызывают операторы `getValue`/`setValue` делегата.

### Базовый Пример Делегата

```kotlin
// Kotlin код
class Example {
    var value: String by StringDelegate()
}

class StringDelegate {
    private var storedValue = ""

    operator fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return storedValue
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        storedValue = value
    }
}
```

### Что Генерируется В Java Bytecode

```java
// Сгенерированный Java код (упрощенный, близкий к реальному)
public final class Example {
    // 1. Скрытое поле для хранения делегата
    private final StringDelegate value$delegate = new StringDelegate();

    // 2. Property metadata (массив делегированных свойств)
    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]
        new PropertyReference1Impl(
            Example.class,
            "value",
            "getValue()Ljava/lang/String;",
            0
        )
    };

    // 3. Getter вызывает delegate.getValue()
    public final String getValue() {
        return this.value$delegate.getValue(
            this,
            $$delegatedProperties[0]
        );
    }

    // 4. Setter вызывает delegate.setValue()
    public final void setValue(String value) {
        this.value$delegate.setValue(
            this,
            $$delegatedProperties[0],
            value
        );
    }
}
```

### Компоненты Компиляции Делегатов

#### 1. Скрытое Поле Делегата (`$delegate`)

```kotlin
// Kotlin
class User {
    var name: String by observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Java (упрощенно, схематично)
public final class User {
    // Скрытое поле с суффиксом $delegate
    private final ObservableProperty name$delegate;

    public User() {
        this.name$delegate = new ObservableProperty(
            "",
            // lambda для обработки изменений
        );
    }
}
```

(Типы `ObservableProperty`/`VetoableProperty` и точные сигнатуры в stdlib могут отличаться; пример иллюстративный.)

#### 2. Property Metadata (`KProperty`)

```kotlin
// KProperty содержит метаданные о свойстве
interface KProperty<out R> {
    val name: String  // Имя свойства
    val getter: KProperty.Getter<R>
    // ... другие метаданные
}

// Компилятор генерирует ссылку на свойство
static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
    new PropertyReference1Impl(
        User.class,              // owner class
        "name",                 // property name
        "getName()Ljava/lang/String;",  // getter signature
        0                        // flags
    )
};
```

#### 3. Методы Доступа (геттеры/сеттеры)

```kotlin
// Kotlin свойство
var value: String by delegate

// Генерируется Java код (упрощенно):
public String getValue() {
    return delegate.getValue(this, $$delegatedProperties[0]);
}

public void setValue(String value) {
    delegate.setValue(this, $$delegatedProperties[0], value);
}
```

### Примеры Популярных Делегатов

#### `lazy` Делегат

```kotlin
// Kotlin
class Example {
    val data: String by lazy {
        expensiveComputation()
    }
}

// Java (примерно, схематично)
public final class Example {
    private final Lazy data$delegate = LazyKt.lazy(
        new Function0<String>() {
            @Override
            public String invoke() {
                return expensiveComputation();
            }
        }
    );

    public final String getData() {
        return (String) data$delegate.getValue();
    }
}

// Упрощенная версия интерфейса Lazy (для понимания идеи)
public interface Lazy<T> {
    T getValue();
    boolean isInitialized();
}

// Упрощенная версия реализации SynchronizedLazyImpl
internal class SynchronizedLazyImpl<T>(
    initializer: () -> T
) : Lazy<T> {
    private var initializer: (() -> T)? = initializer
    private var _value: Any? = UNINITIALIZED_VALUE

    override fun getValue(): T {
        val v1 = _value
        if (v1 !== UNINITIALIZED_VALUE) {
            @Suppress("UNCHECKED_CAST")
            return v1 as T
        }

        return synchronized(this) {
            val v2 = _value
            if (v2 !== UNINITIALIZED_VALUE) {
                @Suppress("UNCHECKED_CAST")
                v2 as T
            } else {
                val typedValue = initializer!!()
                _value = typedValue
                initializer = null
                typedValue
            }
        }
    }

    override fun isInitialized(): Boolean = _value !== UNINITIALIZED_VALUE
}
```

(Реальные реализации в stdlib немного отличаются и включают аннотации/оптимизации; здесь показана концепция.)

#### `observable` Делегат

```kotlin
// Kotlin
class User {
    var name: String by Delegates.observable("initial") { prop, old, new ->
        println("$old -> $new")
    }
}

// Java (примерно, схематично)
public final class User {
    private final ObservableProperty name$delegate;

    public User() {
        this.name$delegate = new ObservableProperty(
            "initial",  // initialValue
            new Function3<KProperty<?>, String, String, Unit>() {
                @Override
                public Unit invoke(KProperty<?> prop, String old, String newVal) {
                    System.out.println(old + " -> " + newVal);
                    return Unit.INSTANCE;
                }
            }
        );
    }

    public String getName() {
        return name$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public void setName(String value) {
        name$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}

// Упрощенный вариант ObservableProperty
open class ObservableProperty<T>(
    initialValue: T,
    private val onChange: (property: KProperty<*>, oldValue: T, newValue: T) -> Unit
) : ReadWriteProperty<Any?, T> {

    private var value = initialValue

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return value
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val oldValue = this.value
        this.value = value
        onChange(property, oldValue, value)
    }
}
```

(В stdlib используются внутренние типы и generics; пример иллюстрирует схему.)

#### `vetoable` Делегат

```kotlin
// Kotlin
var age: Int by Delegates.vetoable(0) { prop, old, new ->
    new >= 0  // Разрешить только неотрицательные значения
}

// Java (примерно, схематично)
private final ReadWriteProperty<Object, Integer> age$delegate =
    new VetoableProperty(
        0,
        new Function3<KProperty<?>, Integer, Integer, Boolean>() {
            @Override
            public Boolean invoke(KProperty<?> prop, Integer old, Integer newVal) {
                return newVal >= 0;
            }
        }
    );
```

(Название `VetoableProperty` здесь условное; в stdlib используется своя внутренняя реализация.)

### Кастомный Делегат - Полная Компиляция

```kotlin
// Kotlin
class LoggingDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} from ${this.value} to $value")
        this.value = value
    }
}

class Example {
    var data: String by LoggingDelegate("initial")
}
```

**Сгенерированный Java код (упрощенный):**

```java
// LoggingDelegate класс
public final class LoggingDelegate<T> {
    private T value;

    public LoggingDelegate(T value) {
        this.value = value;
    }

    public final T getValue(
        Object thisRef,
        KProperty<?> property
    ) {
        System.out.println("Getting " + property.getName() + " = " + value);
        return value;
    }

    public final void setValue(
        Object thisRef,
        KProperty<?> property,
        T value
    ) {
        System.out.println(
            "Setting " + property.getName() +
            " from " + this.value + " to " + value
        );
        this.value = value;
    }
}

// Example класс
public final class Example {
    // 1. Поле-делегат
    private final LoggingDelegate<String> data$delegate =
        new LoggingDelegate<>("initial");

    // 2. Property metadata
    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(
            Example.class,
            "data",
            "getData()Ljava/lang/String;",
            0
        )
    };

    // 3. Getter
    public final String getData() {
        return (String) data$delegate.getValue(
            this,
            $$delegatedProperties[0]
        );
    }

    // 4. Setter
    public final void setData(String value) {
        data$delegate.setValue(
            this,
            $$delegatedProperties[0],
            value
        );
    }
}
```

### `provideDelegate` - Кастомизация Создания Делегата

```kotlin
// Kotlin
class ResourceDelegate<T> : ReadWriteProperty<Any?, T> {
    private var value: T? = null

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        return value ?: throw IllegalStateException("Not initialized")
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        this.value = value
    }
}

class ResourceProvider {
    operator fun provideDelegate(
        thisRef: Any?,
        prop: KProperty<*>
    ): ReadWriteProperty<Any?, String> {
        // Логика при создании делегата
        println("Creating delegate for ${prop.name}")
        return ResourceDelegate<String>()
    }
}

class Example {
    var resource: String by ResourceProvider()
}

// Java (примерно, схематично)
public final class Example {
    // Вызывается провайдер при инициализации!
    private final ReadWriteProperty<Object, String> resource$delegate;

    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(
            Example.class,
            "resource",
            "getResource()Ljava/lang/String;",
            0
        )
    };

    public Example() {
        ResourceProvider provider = new ResourceProvider();
        this.resource$delegate = provider.provideDelegate(
            this,
            $$delegatedProperties[0]
        );
    }

    public String getResource() {
        return resource$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public void setResource(String value) {
        resource$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

### `Map` Делегаты

```kotlin
// Kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
}

// Java (примерно, схематично)
public final class User {
    private final Map<String, Object> map;

    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(User.class, "name", "getName()Ljava/lang/String;", 0),
        new PropertyReference1Impl(User.class, "age", "getAge()I", 0)
    };

    public User(Map<String, Object> map) {
        this.map = map;
    }

    public final String getName() {
        // `Map` напрямую используется как делегат через extension-функцию MapsKt.getValue
        return (String) MapsKt.getValue(
            map,
            $$delegatedProperties[0]
        );
    }

    public final int getAge() {
        return (Integer) MapsKt.getValue(
            map,
            $$delegatedProperties[1]
        );
    }
}
```

### Оптимизации Компилятора и Особенности

```kotlin
// 1. Inline делегаты
inline operator fun <T> Foo.getValue(thisRef: Any?, property: KProperty<*>): T { /* ... */ }
// Тело может быть встроено (inlined), уменьшая накладные расходы вызова.

// 2. Делегаты для локальных переменных
fun example() {
    var x by SomeDelegate()  // Компилятор также генерирует для этого вспомогательные вызовы
}
// Реализация на bytecode отличается от свойств класса; пример концептуальный.

// 3. Делегаты поддерживаются для:
//    - свойств классов
//    - top-level свойств
//    - свойств в объектах/companion-объектах
// Делегаты для extension-свойств без receiver-холдера не поддерживают собственный backing field.
```

### Performance Сравнение

```kotlin
// Обычное свойство
class Normal {
    var value: String = ""  // Прямой доступ к полю (через геттер/сеттер, но без делегата)
}

// Делегированное свойство
class Delegated {
    var value: String by observable("") { _, _, _ -> }
    // Вызов методов делегата и передача metadata при каждом доступе
}

// Оценочно (для понимания порядка величин, не как гарантированный benchmark):
// Normal.value (get):     ~1 ns
// Delegated.value (get):  ~10 ns (из-за вызова метода делегата + работы с metadata)
```

## Answer (EN)

Kotlin property delegates use the `by` keyword to delegate getter/setter logic to another object. At the compilation level (for class / top-level / object/companion properties), the Kotlin compiler generates the same core artifacts as described in the Russian section:
- a hidden delegate field;
- a `KProperty` metadata array (`$$delegatedProperties`);
- accessors that call `getValue` / `setValue` on the delegate.

All examples below are simplified/approximate and focus on the compilation pattern, not exact stdlib/internal implementations.

### Basic delegate example

```kotlin
// Kotlin
class Example {
    var value: String by StringDelegate()
}

class StringDelegate {
    private var storedValue = ""

    operator fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return storedValue
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        storedValue = value
    }
}
```

Compiled (simplified Java-like code):

```java
public final class Example {
    // 1. Hidden field for the delegate
    private final StringDelegate value$delegate = new StringDelegate();

    // 2. Property metadata array
    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(
            Example.class,
            "value",
            "getValue()Ljava/lang/String;",
            0
        )
    };

    // 3. Accessors call delegate
    public final String getValue() {
        return this.value$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public final void setValue(String value) {
        this.value$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

### Delegate compilation components

#### 1. Hidden `$delegate` field

For a property declared with `by`, the compiler generates a hidden field to store the delegate instance.

```kotlin
class User {
    var name: String by observable("") { _, old, new ->
        println("$old -> $new")
    }
}
```

```java
public final class User {
    // Hidden field with $delegate suffix
    private final ObservableProperty name$delegate;

    public User() {
        this.name$delegate = new ObservableProperty(
            "",
            // lambda handling changes (simplified)
        );
    }
}
```

(Names/types are illustrative; real stdlib implementations differ.)

#### 2. Property metadata (`KProperty`)

The compiler creates a `$$delegatedProperties` array containing `KProperty` instances (e.g. `PropertyReference1Impl`) describing each delegated property.

```java
static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
    new PropertyReference1Impl(
        User.class,
        "name",
        "getName()Ljava/lang/String;",
        0
    )
};
```

This metadata is passed into `getValue` / `setValue` so delegates can know which property they serve and enable reflection.

#### 3. Accessor methods

Accessors are rewritten to call the delegate's operators with `thisRef` and the corresponding `KProperty`.

```kotlin
var value: String by delegate
```

```java
public String getValue() {
    return delegate.getValue(this, $$delegatedProperties[0]);
}

public void setValue(String value) {
    delegate.setValue(this, $$delegatedProperties[0], value);
}
```

### Built-in delegates

#### `lazy`

The `lazy` delegate compiles to a hidden `Lazy` instance. Accessors call its `getValue`.

```kotlin
class Example {
    val data: String by lazy {
        expensiveComputation()
    }
}
```

```java
public final class Example {
    private final Lazy data$delegate = LazyKt.lazy(
        new Function0<String>() {
            @Override
            public String invoke() {
                return expensiveComputation();
            }
        }
    );

    public final String getData() {
        return (String) data$delegate.getValue();
    }
}
```

Conceptual `Lazy`/`SynchronizedLazyImpl` shape (approximate):

```kotlin
interface Lazy<T> {
    fun getValue(): T
    fun isInitialized(): Boolean
}

internal class SynchronizedLazyImpl<T>(
    initializer: () -> T
) : Lazy<T> {
    private var initializer: (() -> T)? = initializer
    private var _value: Any? = UNINITIALIZED_VALUE

    override fun getValue(): T { /* same pattern as RU example */ }
    override fun isInitialized(): Boolean = _value !== UNINITIALIZED_VALUE
}
```

#### `observable`

`Delegates.observable` uses an `ObservableProperty`-like delegate that stores the value and invokes a callback.

```kotlin
class User {
    var name: String by Delegates.observable("initial") { prop, old, new ->
        println("$old -> $new")
    }
}
```

```java
public final class User {
    private final ObservableProperty name$delegate;

    public User() {
        this.name$delegate = new ObservableProperty(
            "initial",
            new Function3<KProperty<?>, String, String, Unit>() {
                @Override
                public Unit invoke(KProperty<?> prop, String old, String newVal) {
                    System.out.println(old + " -> " + newVal);
                    return Unit.INSTANCE;
                }
            }
        );
    }

    public String getName() {
        return name$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public void setName(String value) {
        name$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

Approximate delegate shape:

```kotlin
open class ObservableProperty<T>(
    initialValue: T,
    private val onChange: (KProperty<*>, T, T) -> Unit
) : ReadWriteProperty<Any?, T> {
    private var value = initialValue

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val oldValue = this.value
        this.value = value
        onChange(property, oldValue, value)
    }
}
```

#### `vetoable`

`Delegates.vetoable` is similar to `observable`, but the lambda can reject the new value.

```kotlin
var age: Int by Delegates.vetoable(0) { prop, old, new ->
    new >= 0
}
```

```java
private final ReadWriteProperty<Object, Integer> age$delegate =
    new VetoableProperty(
        0,
        new Function3<KProperty<?>, Integer, Integer, Boolean>() {
            @Override
            public Boolean invoke(KProperty<?> prop, Integer old, Integer newVal) {
                return newVal >= 0;
            }
        }
    );
```

Again, this is schematic; real internal classes differ.

### Custom delegate example (LoggingDelegate)

```kotlin
class LoggingDelegate<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Getting ${property.name} = $value")
        return value
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        println("Setting ${property.name} from ${this.value} to $value")
        this.value = value
    }
}

class Example {
    var data: String by LoggingDelegate("initial")
}
```

```java
public final class Example {
    private final LoggingDelegate<String> data$delegate =
        new LoggingDelegate<>("initial");

    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(
            Example.class,
            "data",
            "getData()Ljava/lang/String;",
            0
        )
    };

    public final String getData() {
        return (String) data$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public final void setData(String value) {
        data$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

This matches the same delegate compilation protocol: hidden field, `KProperty` metadata, accessor forwarding.

### `provideDelegate` – delegate creation hook

If a type defines `operator fun provideDelegate(thisRef, prop)`, the compiler uses it during initialization. Conceptually, the Kotlin:

```kotlin
class ResourceDelegate<T> : ReadWriteProperty<Any?, T> { /* as in RU section */ }

class ResourceProvider {
    operator fun provideDelegate(
        thisRef: Any?,
        prop: KProperty<*>
    ): ReadWriteProperty<Any?, String> { /* logging/validation */ }
}

class Example {
    var resource: String by ResourceProvider()
}
```

is compiled roughly into:

```java
public final class Example {
    private final ReadWriteProperty<Object, String> resource$delegate;

    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(
            Example.class,
            "resource",
            "getResource()Ljava/lang/String;",
            0
        )
    };

    public Example() {
        ResourceProvider provider = new ResourceProvider();
        this.resource$delegate = provider.provideDelegate(
            this,
            $$delegatedProperties[0]
        );
    }

    public String getResource() {
        return resource$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public void setResource(String value) {
        resource$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

So `provideDelegate` controls how the delegate instance is constructed and allows validation based on `KProperty` at compile-time binding.

### `Map` delegates

For `Map`-backed delegates, the map itself is the delegate; the compiler wires calls to extension functions like `MapsKt.getValue`.

```kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
}
```

```java
public final class User {
    private final Map<String, Object> map;

    private static final KProperty<?>[] $$delegatedProperties = new KProperty<?>[]{
        new PropertyReference1Impl(User.class, "name", "getName()Ljava/lang/String;", 0),
        new PropertyReference1Impl(User.class, "age", "getAge()I", 0)
    };

    public User(Map<String, Object> map) {
        this.map = map;
    }

    public final String getName() {
        // `Map` is used directly as delegate via MapsKt.getValue
        return (String) MapsKt.getValue(
            map,
            $$delegatedProperties[0]
        );
    }

    public final int getAge() {
        return (Integer) MapsKt.getValue(
            map,
            $$delegatedProperties[1]
        );
    }
}
```

### Optimizations and supported use-cases

- Inline delegates: `inline` `getValue`/`setValue` can be inlined, reducing call overhead.
- Local variable delegates: `var x by SomeDelegate()` in a function compiles to helper calls (protocol is similar, layout differs from fields).
- Delegates are supported for:
  - member properties;
  - top-level properties;
  - properties in `object` / `companion object`.
- Extension properties use the delegate protocol but typically do not introduce a separate backing field on the receiver.

### Performance comparison

Illustratively:
- A normal field-backed property access is very cheap (single field read/write plus simple accessor).
- A delegated property adds:
  - one extra object (the delegate instance),
  - an extra call indirection,
  - `KProperty` metadata construction/usage.

This often makes delegated accesses roughly an order of magnitude slower in microbenchmarks (for example, `~1 ns` vs `~10 ns`), but actual numbers depend on the platform, JIT, and possible inlining.

## Дополнительные вопросы (RU)

- Чем это принципиально отличается от подхода в Java (ручные геттеры/сеттеры, Lombok)?
- В каких случаях уместно использовать делегаты, а в каких лучше обойтись обычными свойствами?
- Какие типичные ошибки и накладные расходы при использовании делегатов нужно учитывать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Официальная документация Kotlin: https://kotlinlang.org/docs/delegated-properties.html
- [[c-kotlin]]

## References

- https://kotlinlang.org/docs/delegated-properties.html
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-flow-backpressure--kotlin--hard]]
- [[q-kotlin-delegation-detailed--kotlin--medium]]

## Related Questions

- [[q-flow-backpressure--kotlin--hard]]
- [[q-kotlin-delegation-detailed--kotlin--medium]]
