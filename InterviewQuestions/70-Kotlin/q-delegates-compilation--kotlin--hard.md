---
id: 20251012-154356
title: "Delegates Compilation / Компиляция делегатов"
topic: kotlin
difficulty: hard
status: draft
created: 2025-10-15
tags: - kotlin
  - delegates
  - compilation
  - bytecode
  - advanced
---
# Как делегаты работают на уровне компиляции?

# Question (EN)
> How do Kotlin delegates work at the compilation level? What bytecode and auxiliary structures are generated?

# Вопрос (RU)
> Как делегаты Kotlin работают на уровне компиляции? Какой bytecode и вспомогательные структуры генерируются?

---

## Answer (EN)

Kotlin property delegates use the `by` keyword to delegate getter/setter logic to another object. At compilation level, the Kotlin compiler generates:

1. **Hidden delegate field** (`property$delegate`) - stores the delegate instance
2. **Property metadata** (`$$delegatedProperties` array) - contains `KProperty` objects with reflection metadata
3. **Accessor methods** (getters/setters) - call `delegate.getValue()` and `delegate.setValue()`

**Example:**
```kotlin
// Kotlin code
class Example {
    var value: String by StringDelegate()
}

// Compiles to (simplified Java):
public final class Example {
    private final StringDelegate value$delegate = new StringDelegate();

    static final KProperty[] $$delegatedProperties = ...;

    public final String getValue() {
        return value$delegate.getValue(this, $$delegatedProperties[0]);
    }

    public final void setValue(String value) {
        value$delegate.setValue(this, $$delegatedProperties[0], value);
    }
}
```

**Common delegates:**
- `lazy`: Creates `Lazy` wrapper with synchronized initialization
- `observable`: Creates `ObservableProperty` with change callback
- `vetoable`: Creates `ObservableProperty` with validation
- Map delegates: Use `MapsKt.getValue()` directly

**Performance:** Delegated properties are ~10ns vs ~1ns for direct field access due to method calls and metadata passing.

---

## Ответ (RU)

Kotlin property delegates (делегированные свойства) используют ключевое слово `by` для делегирования логики геттеров/сеттеров другому объекту. На уровне компиляции в Java компилятор Kotlin генерирует вспомогательные поля, классы и методы доступа.

### Базовый пример делегата

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

### Что генерируется в Java bytecode

```java
// Сгенерированный Java код (примерный)
public final class Example {
    // 1. Скрытое поле для хранения делегата
    private final StringDelegate value$delegate = new StringDelegate();

    // 2. Property metadata
    static final KProperty[] $$delegatedProperties = new KProperty[]{
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

### Компоненты компиляции делегатов

#### 1. Скрытое поле делегата (`$delegate`)

```kotlin
// Kotlin
class User {
    var name: String by observable("") { prop, old, new ->
        println("$old -> $new")
    }
}

// Java (упрощенно)
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

#### 2. Property metadata (KProperty)

```kotlin
// KProperty содержит метаданные о свойстве
interface KProperty<out R> {
    val name: String  // Имя свойства
    val getter: KProperty.Getter<R>
    // ... другие метаданные
}

// Компилятор генерирует PropertyReference
static final KProperty[] $$delegatedProperties = new KProperty[]{
    new PropertyReference1Impl(
        UserКласс.class,  // owner class
        "name",           // property name
        "getName()Ljava/lang/String;",  // getter signature
        0  // flags
    )
};
```

#### 3. Методы доступа (геттеры/сеттеры)

```kotlin
// Kotlin свойство
var value: String by delegate

// Генерируется Java код:
public String getValue() {
    return delegate.getValue(this, $$delegatedProperties[0]);
}

public void setValue(String value) {
    delegate.setValue(this, $$delegatedProperties[0], value);
}
```

### Примеры популярных делегатов

#### `lazy` делегат

```kotlin
// Kotlin
class Example {
    val data: String by lazy {
        expensiveComputation()
    }
}

// Java (примерно)
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

// Класс Lazy содержит:
public interface Lazy<out T> {
    val value: T
    fun isInitialized(): Boolean
}

// SynchronizedLazyImpl реализация
internal class SynchronizedLazyImpl<out T>(
    initializer: () -> T
) : Lazy<T> {
    private var initializer: (() -> T)? = initializer
    private var _value: Any? = UNINITIALIZED_VALUE

    override val value: T
        get() {
            val v1 = _value
            if (v1 !== UNINITIALIZED_VALUE) {
                return v1 as T
            }

            return synchronized(this) {
                val v2 = _value
                if (v2 !== UNINITIALIZED_VALUE) {
                    v2 as T
                } else {
                    val typedValue = initializer!!()
                    _value = typedValue
                    initializer = null
                    typedValue
                }
            }
        }
}
```

#### `observable` делегат

```kotlin
// Kotlin
class User {
    var name: String by Delegates.observable("initial") { prop, old, new ->
        println("$old -> $new")
    }
}

// Java (примерно)
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

// ObservableProperty класс
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

#### `vetoable` делегат

```kotlin
// Kotlin
var age: Int by Delegates.vetoable(0) { prop, old, new ->
    new >= 0  // Разрешить только неотрицательные значения
}

// Java (примерно)
private final ObservableProperty age$delegate = new ObservableProperty(
    0,
    new Function3<KProperty<?>, Integer, Integer, Boolean>() {
        @Override
        public Boolean invoke(KProperty<?> prop, Integer old, Integer newVal) {
            return newVal >= 0;
        }
    }
);
```

### Кастомный делегат - полная компиляция

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

**Сгенерированный Java код:**

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
        System.out.println("Setting " + property.getName() +
            " from " + this.value + " to " + value);
        this.value = value;
    }
}

// Example класс
public final class Example {
    // 1. Делегат поле
    private final LoggingDelegate<String> data$delegate =
        new LoggingDelegate<>("initial");

    // 2. Property metadata
    static final KProperty<Object>[] $$delegatedProperties = new KProperty[]{
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

### provideDelegate - кастомизация создания делегата

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

// Java (примерно)
public final class Example {
    // Вызывается провайдер при инициализации!
    private final ReadWriteProperty<Object, String> resource$delegate;

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

### Map делегаты

```kotlin
// Kotlin
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
}

// Java (примерно)
public final class User {
    private final Map<String, Object> map;

    static final KProperty<Object>[] $$delegatedProperties = new KProperty[]{
        new PropertyReference1Impl(User.class, "name", ...),
        new PropertyReference1Impl(User.class, "age", ...)
    };

    public User(Map<String, Object> map) {
        this.map = map;
    }

    public final String getName() {
        // Map напрямую используется как делегат!
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

### Оптимизации компилятора

```kotlin
// 1. Inline делегаты - встраиваются напрямую
inline operator fun getValue(...): T {
    // Код встраивается вместо вызова метода
}

// 2. Делегаты для локальных переменных
fun example() {
    var x by SomeDelegate()  // Тоже работает!
}

// 3. Extension property delegates
val String.uppercase: String
    by lazy { this.uppercase() }
```

### Performance сравнение

```kotlin
// Обычное свойство
class Normal {
    var value: String = ""  // Прямой доступ к полю
}

// Делегированное свойство
class Delegated {
    var value: String by observable("") { _, _, _ -> }
    // Вызов метода делегата при каждом доступе
}

// Benchmark результаты (примерно):
// Normal.value (get):     ~1 ns
// Delegated.value (get):  ~10 ns (из-за вызова метода + metadata)
```
