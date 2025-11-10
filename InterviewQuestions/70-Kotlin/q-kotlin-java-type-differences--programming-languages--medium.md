---
id: lang-051
title: "Kotlin Java Type Differences / Различия типов Kotlin и Java"
aliases: [Kotlin Java Type Differences, Различия типов Kotlin и Java]
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-executor-service-java--kotlin--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [collections, comparison, difficulty/medium, java, null-safety, kotlin, type-inference, type-system]
---
# Вопрос (RU)
> Чем типы в Kotlin отличаются от типов в Java?

---

# Question (EN)
> How do Kotlin types differ from Java types?

## Ответ (RU)

Типы в Kotlin и Java существенно различаются в нескольких ключевых аспектах, что делает Kotlin более безопасным и выразительным языком.

### Основные Различия

| Особенность | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Переменные не могут быть null по умолчанию (`String` vs `String?`) | Объектные ссылки могут быть null, типовая система это не выражает явно |
| **Коллекции** | Четкое различие по типам: `List` (read-only) vs `MutableList` (mutable) | Нет отличия на уровне типов между изменяемыми и неизменяемыми коллекциями |
| **Data классы** | Автоматическая генерация методов с `data class` | Требуется ручная реализация (до `record`), либо использование `record` |
| **Вывод типов** | Обширный: вывод для локальных переменных, выражений, лямбд и простых возвращаемых типов функций | Более ограниченный: `var` только для локальных переменных, большинство сигнатур и полей требуют явных типов |
| **Умные приведения** | Автоматические после проверки `is` | Явное приведение после `instanceof` (частично улучшено pattern matching) |
| **Модель примитивных типов** | Унифицированная модель на уровне языка: примитивы/обертки скрыты, компилятор выбирает представление | Отдельные примитивы (`int`) и обертки (`Integer`) |
| **Функциональные типы** | Встроенные функциональные типы `(A, B) -> R` | Функциональные интерфейсы, нет нативного синтаксиса функциональных типов |

### 1. Null Safety - Безопасность От Null

**Kotlin:**
```kotlin
// Не может быть null (non-nullable)
val name: String = "John"
// name = null  // Ошибка компиляции!

// Явно nullable тип
val nullable: String? = null  // OK
val length = nullable?.length  // Safe call

// Обязательная проверка перед использованием
fun printLength(text: String?) {
    if (text != null) {
        println(text.length)  // Smart cast к String
    }
}

// Elvis оператор для значения по умолчанию
val len = nullable?.length ?: 0

// Non-null assertion (осторожно!)
val forcedLength = nullable!!.length  // NullPointerException если null
```

**Java:**
```java
// Любая объектная переменная может быть null
String name = "John";
name = null;  // OK, но опасно

// Нет различия в типах между nullable и non-nullable
String nullable = null;
// int length = nullable.length();  // NullPointerException!

// Требуется ручная проверка
if (nullable != null) {
    System.out.println(nullable.length());
}

// Аннотации помогают, но не гарантируют
@NonNull String nonNull = "text";
@Nullable String maybeNull = null;
```

**Проблема Java:**
```java
// Java - NullPointerException во время выполнения
public String getUpperCase(String text) {
    return text.toUpperCase();  // Crash если text == null!
}
```

```kotlin
// Kotlin - ошибка компиляции, если в сигнатуре тип non-nullable
fun getUpperCase(text: String): String {
    return text.uppercase()  // Гарантированно не null
}

fun getUpperCaseSafe(text: String?): String? {
    return text?.uppercase()  // Безопасный вызов
}
```

### 2. Коллекции - Изменяемые Vs Read-Only

**Kotlin:**
```kotlin
// Read-only список: интерфейс не позволяет модификацию
val immutableList: List<Int> = listOf(1, 2, 3)
// immutableList.add(4)  // Ошибка компиляции!

// Изменяемый список
val mutableList: MutableList<Int> = mutableListOf(1, 2, 3)
mutableList.add(4)  // OK
mutableList[0] = 10  // OK

// Read-only vs mutable
val readOnlySet: Set<String> = setOf("a", "b")
val mutableSet: MutableSet<String> = mutableSetOf("a", "b")

val readOnlyMap: Map<String, Int> = mapOf("key" to 1)
val mutableMap: MutableMap<String, Int> = mutableMapOf("key" to 1)

// Важно: read-only не гарантирует структурную неизменяемость источника
val list1 = mutableListOf(1, 2, 3)
val list2: List<Int> = list1  // Upcast к read-only интерфейсу
// list2.add(4)  // Ошибка компиляции
list1.add(4)  // OK, исходный список все еще изменяемый
```

**Java:**
```java
// Тип List не различает изменяемые и неизменяемые реализации
List<Integer> list = new ArrayList<>(List.of(1, 2, 3));
list.add(4);  // OK (конкретная реализация mutable)

// Фабрики Java 9+ возвращают неизменяемые реализации
List<Integer> immutable = List.of(1, 2, 3);
// immutable.add(4);  // UnsupportedOperationException во время выполнения!

// Collections.unmodifiableList - обертка над исходной коллекцией
List<Integer> wrapped = Collections.unmodifiableList(list);
// wrapped.add(5);  // Runtime exception
list.add(5);  // Изменяет содержимое wrapped тоже, так как это view

// На уровне типов нет разделения
List<String> list1 = new ArrayList<>();      // Изменяемая реализация
List<String> list2 = List.of("a", "b");   // Неизменяемая реализация
// Оба имеют тип List<String>, поведение определяется реализацией
```

### 3. Data Классы - Автогенерация Методов

**Kotlin:**
```kotlin
// Data class - автоматическая генерация
data class User(
    val id: Int,
    val name: String,
    val email: String
)

// Автоматически генерируются:
// - equals() / hashCode()
// - toString()
// - copy()
// - componentN() для деструктуризации

val user1 = User(1, "Alice", "alice@example.com")
val user2 = User(1, "Alice", "alice@example.com")

println(user1 == user2)  // true (equals по значению)
println(user1)  // User(id=1, name=Alice, email=alice@example.com)

// Copy с изменением полей
val user3 = user1.copy(name = "Bob")
println(user3)  // User(id=1, name=Bob, email=alice@example.com)

// Деструктуризация
val (id, name, email) = user1
println("ID: $id, Name: $name")
```

**Java:**
```java
// До records требовалась ручная реализация всех методов
public class User {
    private final int id;
    private final String name;
    private final String email;

    public User(int id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    // Геттеры
    public int getId() { return id; }
    public String getName() { return name; }
    public String getEmail() { return email; }

    // equals
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return id == user.id &&
               Objects.equals(name, user.name) &&
               Objects.equals(email, user.email);
    }

    // hashCode
    @Override
    public int hashCode() {
        return Objects.hash(id, name, email);
    }

    // toString
    @Override
    public String toString() {
        return "User{id=" + id + ", name='" + name + "', email='" + email + "'}";
    }

    // Copy метод (ручная реализация)
    public User copy(Integer id, String name, String email) {
        return new User(
            id != null ? id : this.id,
            name != null ? name : this.name,
            email != null ? email : this.email
        );
    }
}

// Records в Java 14+ упрощают, но синтаксис все равно отличается от Kotlin data class
public record UserRecord(int id, String name, String email) {}
```

### 4. Вывод Типов - Type Inference

**Kotlin:**
```kotlin
// Обширный вывод типов
val number = 42                     // Int
val pi = 3.14                       // Double
val text = "Hello"                  // String
val list = listOf(1, 2, 3)          // List<Int>
val map = mapOf("a" to 1, "b" to 2) // Map<String, Int>

// Лямбды
val sum = { a: Int, b: Int -> a + b }  // (Int, Int) -> Int
val numbers = listOf(1, 2, 3, 4, 5)
val evenNumbers = numbers.filter { it % 2 == 0 }  // List<Int>

// Обобщенные функции
fun <T> firstOrNull(list: List<T>): T? = list.firstOrNull()
val first = firstOrNull(listOf(1, 2, 3))  // Int? (выведен тип T = Int)

// Возвращаемый тип можно опустить для простых функций
fun add(a: Int, b: Int) = a + b  // Тип Int выводится

// Сложные выражения
val result = when {
    number > 0 -> "positive"
    number < 0 -> "negative"
    else -> "zero"
}  // String
```

**Java:**
```java
// Ограниченный вывод типов (Java 10+)
var number = 42;           // int
var text = "Hello";        // String
var list = List.of(1, 2);  // List<Integer>

// Нужно указывать типы обобщений
List<Integer> numbers = new ArrayList<>();  // <> diamond operator
Map<String, Integer> map = new HashMap<>();

// Лямбды требуют контекста
Function<Integer, Integer> square = x -> x * x;
// var square = x -> x * x;  // Ошибка! Нужен тип-таргет (функциональный интерфейс)

// Методы требуют явного возвращаемого типа
public int add(int a, int b) {  // Нельзя опустить int
    return a + b;
}

// var нельзя использовать для полей класса
public class Example {
    // var field = 10;  // Ошибка!
    private int field = 10;  // OK
}
```

### 5. Умные Приведения - Smart Casts

**Kotlin:**
```kotlin
// Автоматическое приведение после проверки типа
fun printLength(obj: Any) {
    if (obj is String) {
        // Автоматически приведен к String
        println(obj.length)  // Не нужен (obj as String).length
        println(obj.uppercase())
    }
}

// Работает с различными проверками
fun process(value: Any?) {
    // После null-check
    if (value != null) {
        println(value.toString())  // Smart cast к Any
    }

    // После is-check
    when (value) {
        is Int -> println(value + 1)  // Smart cast к Int
        is String -> println(value.length)  // Smart cast к String
        is List<*> -> println(value.size)  // Smart cast к List<*>
    }

    // В выражениях
    val length = if (value is String) value.length else 0
}

// Отрицательная проверка
fun processNotNull(value: Any?) {
    if (value !is String) return
    // Здесь value уже String
    println(value.uppercase())
}

// Комбинация условий
fun example(obj: Any?) {
    if (obj is String && obj.isNotEmpty()) {
        println(obj[0])  // Smart cast работает
    }
}
```

**Java:**
```java
// Требуется явное приведение (до pattern matching)
public void printLength(Object obj) {
    if (obj instanceof String) {
        String str = (String) obj;  // Явное приведение
        System.out.println(str.length());
        System.out.println(str.toUpperCase());
    }
}

// Java 16+ Pattern Matching улучшает ситуацию
public void printLengthModern(Object obj) {
    if (obj instanceof String str) {  // Объявление переменной
        System.out.println(str.length());
    }
}

// Switch expressions (Java 14+)
public String process(Object value) {
    return switch (value) {
        case Integer i -> "Number: " + i;
        case String s -> "Text: " + s;
        case null -> "Null value";
        default -> "Unknown";
    };
}

// Но система приведения и pattern matching все еще менее гибкая, чем smart casts в Kotlin
```

### 6. Примитивные Типы

**Kotlin:**
```kotlin
// Унифицированная система типов на уровне языка
val number: Int = 42
println(number.toString())  // Методы доступны
println(number.plus(8))

// Компилятор сам выбирает представление для JVM
val x: Int = 10        // Обычно компилируется в int (примитив)
val y: Int? = 10       // Компилируется в Integer (объект)
val list: List<Int> = listOf(1, 2)  // Использует Integer внутри

// == всегда сравнивает значения, === — ссылки
val a: Int = 1000
val b: Int = 1000
println(a == b)   // true (сравнение значений)
println(a === b)  // зависит от боксинга/оптимизаций

// Специальные массивы для производительности
val primitiveArray: IntArray = intArrayOf(1, 2, 3)  // компилируется в int[]
val objectArray: Array<Int> = arrayOf(1, 2, 3)      // компилируется в Integer[]
```

**Java:**
```java
// Разделение примитивов и объектов
int primitive = 42;
Integer object = 42;  // Autoboxing

// primitive.toString();  // Нельзя напрямую
object.toString();  // OK

// Autoboxing проблемы
Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false (разные объекты)
System.out.println(a.equals(b)); // true (значения равны)

// Кэширование Integer (-128 до 127)
Integer x = 100;
Integer y = 100;
System.out.println(x == y);  // true (кэш)

// Нельзя использовать примитивы как параметры типа
List<Integer> list = new ArrayList<>();  // Нельзя List<int>
int[] primitiveArray = {1, 2, 3};
Integer[] objectArray = {1, 2, 3};
```

### 7. Функциональные Типы

**Kotlin:**
```kotlin
// Функции — объекты первого класса
val operation: (Int, Int) -> Int = { a, b -> a + b }
val result = operation(5, 3)  // 8

// Функциональные типы с receiver
val append: String.() -> String = { this + "!" }
val text = "Hello".append()  // "Hello!"

// Nullable функциональные типы
val nullableFunc: ((Int) -> Int)? = null
val res = nullableFunc?.invoke(5)

// Функции высшего порядка
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    return this.filter(predicate)
}
```

**Java:**
```java
// Функциональные интерфейсы
Function<Integer, Integer> operation = x -> x * 2;
int result = operation.apply(5);  // 10

// Использование стандартных функциональных интерфейсов
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
Predicate<String> isEmpty = String::isEmpty;
Consumer<String> print = System.out::println;

// Или создание своих
@FunctionalInterface
interface MyFunction {
    int apply(int a, int b);
}

MyFunction multiply = (a, b) -> a * b;
```

### Итоговое Сравнение

1. **Null Safety**: Kotlin выражает nullability в системе типов и предотвращает часть NPE на этапе компиляции.
2. **Коллекции**: Явное различие read-only/mutable интерфейсов.
3. **Data классы**: Автоматическая генерация boilerplate-кода.
4. **Вывод типов**: Меньше явных деклараций типов при сохранении читаемости.
5. **Smart Casts**: Автоматическое приведение типов после проверок.
6. **Упрощенная модель примитивных типов**: Примитивы и объекты объединены на уровне языка, детали JVM скрыты.
7. **Функциональные типы**: Встроенная поддержка функциональных типов и функций высшего порядка.

### Практический пример

```kotlin
// Kotlin - краткий и безопасный
data class Person(val name: String, val age: Int)

fun findAdult(people: List<Person>): Person? {
    return people.firstOrNull { it.age >= 18 }
}

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 17)
)

val adult = findAdult(people)
adult?.let { println("Found: ${it.name}") }
```

```java
// Java - более многословный пример
public class Person {
    private final String name;
    private final int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public int getAge() { return age; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person person = (Person) o;
        return age == person.age && Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

public Person findAdult(List<Person> people) {
    for (Person person : people) {
        if (person.getAge() >= 18) {
            return person;
        }
    }
    return null;  // Может быть null
}

List<Person> people = List.of(
    new Person("Alice", 25),
    new Person("Bob", 17)
);

Person adult = findAdult(people);
if (adult != null) {
    System.out.println("Found: " + adult.getName());
}
```

## Answer (EN)

Kotlin and Java type systems differ in several fundamental ways that impact safety, expressiveness, and boilerplate.

### Overview

| Feature | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Non-null by default; explicit nullable types (`String?`) | Any reference can be null; nullability is mostly by convention/annotations |
| **Collections** | Type-level split: `List` (read-only) vs `MutableList` (mutable); same for `Set`/`Map` | One `List` type; mutability depends on implementation/wrappers |
| **Data Classes** | `data class` auto-generates `equals`/`hashCode`/`toString`/`copy`/`componentN` | Manual boilerplate or `record` (newer Java); different syntax/semantics |
| **Type Inference** | Wide: locals, expressions, lambdas, simple function return types | Narrower: `var` for locals (Java 10+), explicit types for members and returns |
| **Smart Casts** | Automatic after `is`/null checks | Traditionally explicit casts; pattern matching improves but still less integrated |
| **Primitive Types** | Unified model at language level; boxing details mostly hidden | Distinct primitives vs wrapper types; autoboxing pitfalls |
| **Functional Types** | First-class function types `(A, B) -> R`, receivers, HOFs | Functional interfaces (`Function`, `Predicate`, etc.), no native function type syntax |

### 1. Null Safety

```kotlin
val name: String = "John"              // Cannot be null
val nullable: String? = null            // Explicitly nullable
val length = nullable?.length           // Safe call
val len = nullable?.length ?: 0         // Elvis

fun getUpperCase(text: String): String = text.uppercase()
fun getUpperCaseSafe(text: String?): String? = text?.uppercase()
```

```java
String name = "John";
name = null;                             // Allowed
String nullable = null;
// nullable.length();                    // NPE if not checked

@NonNull String nonNull = "text";       // Convention-only
@Nullable String maybeNull = null;
```

Kotlin encodes nullability in types and forces compile-time checks; Java mostly relies on discipline and annotations.

### 2. Collections: Mutable vs Read-Only

```kotlin
val list: List<Int> = listOf(1, 2, 3)          // Read-only interface
// list.add(4)                                 // Compile error

val mutableList: MutableList<Int> = mutableListOf(1, 2, 3)
mutableList.add(4)                             // OK

val list1 = mutableListOf(1, 2, 3)
val list2: List<Int> = list1                   // Read-only view
list1.add(4)                                   // Mutates underlying data
```

```java
List<Integer> list = new ArrayList<>(List.of(1, 2, 3));
list.add(4);                                   // OK (mutable implementation)

List<Integer> immutable = List.of(1, 2, 3);
// immutable.add(4);                          // Runtime exception

List<Integer> wrapped = Collections.unmodifiableList(list);
// wrapped.add(5);                            // Runtime exception
list.add(5);                                   // Reflected via wrapped
```

Kotlin distinguishes read-only vs mutable via types (without guaranteeing deep immutability); Java exposes mutability only via runtime behavior.

### 3. Data Classes

```kotlin
data class User(val id: Int, val name: String, val email: String)

val u1 = User(1, "Alice", "alice@example.com")
val u2 = User(1, "Alice", "alice@example.com")
println(u1 == u2)                             // true (value equality)
println(u1.copy(name = "Bob"))               // copy with modification
val (id, name, email) = u1                    // destructuring
```

```java
public class User {
    // fields, constructor, getters, equals, hashCode, toString, etc.
}

public record UserRecord(int id, String name, String email) {}
```

Kotlin `data class` is built-in for value objects; Java uses manual code or records (newer JDKs).

### 4. Type Inference

```kotlin
val number = 42                  // Int
val list = listOf(1, 2, 3)       // List<Int>
val sum = { a: Int, b: Int -> a + b }

fun add(a: Int, b: Int) = a + b  // Return type inferred
```

```java
var number = 42;                  // int
var list = List.of(1, 2);         // List<Integer>

List<Integer> nums = new ArrayList<>();
Function<Integer, Integer> square = x -> x * x;

public int add(int a, int b) { return a + b; }
```

Kotlin infers more (including many return types); Java keeps method signatures explicit and uses `var` only for locals.

### 5. Smart Casts

```kotlin
fun printLength(obj: Any) {
    if (obj is String) {
        println(obj.length)      // Smart cast to String
    }
}

fun process(value: Any?) {
    if (value != null) {
        println(value.toString())
    }

    when (value) {
        is Int -> println(value + 1)
        is String -> println(value.length)
        is List<*> -> println(value.size)
    }
}
```

```java
public void printLength(Object obj) {
    if (obj instanceof String) {
        String s = (String) obj; // Explicit cast
        System.out.println(s.length());
    }
}

public void printLengthModern(Object obj) {
    if (obj instanceof String s) { // Pattern matching
        System.out.println(s.length());
    }
}
```

Kotlin flow analysis performs smart casts automatically; Java pattern matching narrows types but is less integrated.

### 6. Primitive Types

```kotlin
val x: Int = 10                  // Usually primitive on JVM
val y: Int? = 10                 // Boxed
val arr: IntArray = intArrayOf(1, 2, 3)

val a = 1000
val b = 1000
println(a == b)                  // Value equality
println(a === b)                 // Reference equality
```

```java
int primitive = 42;
Integer object = 42;

Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false
System.out.println(a.equals(b)); // true
```

Kotlin exposes a simpler, unified number model while compiling efficiently to JVM primitives and wrappers; Java exposes primitives vs wrappers directly.

### 7. Functional Types

```kotlin
val operation: (Int, Int) -> Int = { a, b -> a + b }
val r = operation(5, 3)

val withReceiver: String.() -> String = { this + "!" }
val text = "Hi".withReceiver()

fun <T> List<T>.customFilter(pred: (T) -> Boolean): List<T> =
    this.filter(pred)
```

```java
Function<Integer, Integer> op = x -> x * 2;
BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;

@FunctionalInterface
interface MyFunction { int apply(int a, int b); }

MyFunction mul = (a, b) -> a * b;
```

Kotlin has native function types and extension functions; Java uses functional interfaces.

### Key Takeaways

1. Kotlin encodes nullability in the type system, reducing accidental NPEs.
2. Kotlin separates read-only and mutable collections at the type level.
3. Kotlin `data class` and function types reduce boilerplate and improve expressiveness.
4. Kotlin offers broader type inference and built-in smart casts.
5. Kotlin simplifies working with primitives vs wrappers while remaining efficient.

---

## Дополнительные вопросы (RU)

- В чем практические преимущества null safety в Kotlin по сравнению с Java?
- Как различие в работе с коллекциями влияет на дизайн API?
- Когда уместно предпочесть Java-подход Kotlin-подходу (и наоборот) в существующей JVM-кодовой базе?

## Follow-ups

- What are the practical benefits of Kotlin's null safety compared to Java?
- How does the difference in collection mutability handling affect API design?
- When is it reasonable to prefer a Java-style approach over Kotlin's (and vice versa) in an existing JVM codebase?

## Ссылки (RU)

- [[c-kotlin]]
- Документация Kotlin: https://kotlinlang.org/docs/home.html
- Java Language Specification: https://docs.oracle.com/javase/specs/

## References

- [[c-kotlin]]
- Kotlin Documentation: https://kotlinlang.org/docs/home.html
- Java Language Specification: https://docs.oracle.com/javase/specs/

## Related Questions

- [[q-executor-service-java--kotlin--medium]]
