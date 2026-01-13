---
---
---\
id: lang-022
title: "Kotlin Reflection / Рефлексия в Kotlin"
aliases: [Kotlin Reflection, Рефлексия в Kotlin]
topic: kotlin
subtopics: [c-kotlin, c-kotlin-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-object-companion-object--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, kotlin-reflect, metaprogramming, programming-languages, reflection, runtime]
---\
# Вопрос (RU)
> Что такое рефлексия?

---

# Question (EN)
> What is reflection?

## Ответ (RU)

**Рефлексия** — это механизм, позволяющий программе **исследовать и (в ограничённых случаях) изменять свою собственную структуру** (классы, методы, поля, аннотации) во время выполнения.

Она позволяет (при использовании `kotlin-reflect` и/или Java Reflection API):
- Вызывать private методы
- Создавать экземпляры классов по имени
- Получать доступ/изменять private поля
- Исследовать аннотации

Это мощный инструмент, но при злоупотреблении может быть **опасным для типобезопасности, инкапсуляции и производительности**.

**Настройка:**

```kotlin
// build.gradle.kts
dependencies {
    implementation(kotlin("reflect"))
}
```

(Далее примеры используют Kotlin reflection API из `kotlin-reflect`.)

**Основные применения:**

**1. Получение информации о классе:**

```kotlin
import kotlin.reflect.full.memberProperties

class Person(val name: String, var age: Int) {
    private fun secret() = "Секретный метод"
}

val person = Person("Алиса", 30)

// Получить класс
val kClass = person::class
println(kClass.simpleName)  // "Person"
println(kClass.qualifiedName)  // Полное имя (FQCN) в зависимости от пакета

// Получить свойства
kClass.memberProperties.forEach { prop ->
    println("${prop.name}: ${prop.get(person)}")
}
// Возможный вывод:
// name: Алиса
// age: 30
```

**2. Динамическое создание экземпляров:**

```kotlin
import kotlin.reflect.full.primaryConstructor

// Получить KClass по имени через Java Reflection
val kClass = Class.forName("com.example.Person").kotlin

// Получить конструктор (в реальном коде стоит выбирать primaryConstructor или по сигнатуре)
val constructor = kClass.constructors.first()

// Создать экземпляр
val person = constructor.call("Боб", 25)
```

**3. Доступ к private членам:**

```kotlin
import kotlin.reflect.full.memberFunctions
import kotlin.reflect.full.memberProperties
import kotlin.reflect.jvm.isAccessible

class User(private val password: String) {
    private fun getSecret() = "Секрет: $password"
}

val user = User("12345")

// Доступ к private свойству
val passwordProp = User::class.memberProperties
    .find { it.name == "password" }
passwordProp?.isAccessible = true
val password = passwordProp?.get(user)
println(password)  // "12345"

// Вызов private метода
val secretMethod = User::class.memberFunctions
    .find { it.name == "getSecret" }
secretMethod?.isAccessible = true
val secret = secretMethod?.call(user)
println(secret)  // "Секрет: 12345"
```

(Доступ к закрытым членам через `isAccessible` опирается на механизмы JVM и может быть ограничен или меняться между версиями платформы.)

**4. Исследование аннотаций:**

```kotlin
import kotlin.reflect.full.memberProperties

@Target(AnnotationTarget.CLASS)
annotation class Entity(val tableName: String)

@Target(AnnotationTarget.PROPERTY)
annotation class Column(val name: String)

@Entity("users")
data class User(
    @Column("user_id") val id: Int,
    @Column("user_name") val name: String
)

// Получить аннотацию класса
val entity = User::class.annotations
    .filterIsInstance<Entity>()
    .firstOrNull()
println(entity?.tableName)  // "users"

// Получить аннотации свойств
User::class.memberProperties.forEach { prop ->
    val column = prop.annotations
        .filterIsInstance<Column>()
        .firstOrNull()
    println("${prop.name} -> ${column?.name}")
}
// Вывод:
// id -> user_id
// name -> user_name
```

**5. Динамический вызов функций:**

```kotlin
import kotlin.reflect.full.memberFunctions

class Calculator {
    fun add(a: Int, b: Int) = a + b
    fun multiply(a: Int, b: Int) = a * b
}

val calc = Calculator()

// Найти функцию по имени
val addFunc = Calculator::class.memberFunctions
    .find { it.name == "add" }

// Вызвать её
val result = addFunc?.call(calc, 5, 3)
println(result)  // 8
```

**6. Изменение свойств:**

```kotlin
import kotlin.reflect.KMutableProperty
import kotlin.reflect.full.memberProperties

class Settings {
    var theme: String = "light"
}

val settings = Settings()

// Получить ссылку на свойство
val themeProp = Settings::class.memberProperties
    .find { it.name == "theme" } as? KMutableProperty<*>

// Изменить его
themeProp?.setter?.call(settings, "dark")
println(settings.theme)  // "dark"
```

**Распространённые случаи использования:**

**Сериализация/Десериализация (упрощённый пример):**
```kotlin
import kotlin.reflect.full.memberProperties

fun <T : Any> toJson(obj: T): String {
    val kClass = obj::class
    val props = kClass.memberProperties

    val json = props.joinToString(", ") { prop ->
        "\"${prop.name}\": \"${prop.get(obj)}\""
    }

    return "{$json}"
}

data class User(val name: String, val age: Int)

val user = User("Алиса", 30)
println(toJson(user))  // {"name": "Алиса", "age": "30"}
```

**Dependency Injection (упрощённый рекурсивный пример, только для демонстрации идеи):**
```kotlin
import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor

class UserService(val repository: UserRepository)
class UserRepository

fun <T : Any> inject(kClass: KClass<T>): T {
    // Найти конструктор
    val constructor = kClass.primaryConstructor
        ?: error("Primary constructor required for ${kClass.simpleName}")

    // Получить зависимости по типам параметров
    val params = constructor.parameters.map { param ->
        val depClass = param.type.classifier as? KClass<*>
            ?: error("Unsupported parameter type: ${param.type}")
        inject(depClass)
    }

    // Создать экземпляр
    @Suppress("UNCHECKED_CAST")
    return constructor.call(*params.toTypedArray()) as T
}

// Использование (только для демонстрации идеи; без кэша/графа зависимостей такой подход не подходит для production-кода)
val service = inject(UserService::class)
```

**Тестирование - доступ к private членам:**
```kotlin
import kotlin.reflect.full.memberFunctions
import kotlin.reflect.jvm.isAccessible

class ViewModel {
    private val repository = UserRepository()

    private fun loadData() {
        // Загрузка данных
    }
}

// В тесте
@Test
fun testLoadData() {
    val viewModel = ViewModel()

    val loadMethod = ViewModel::class.memberFunctions
        .find { it.name == "loadData" }
    loadMethod?.isAccessible = true
    loadMethod?.call(viewModel)

    // Проверки результатов
}
```

**Влияние на производительность:**

```kotlin
class Person(val name: String)

val person = Person("Алиса")

// Прямой доступ — обычно быстрее
val direct = person.name

// Рефлексия — обычно медленнее (часто значительно, из-за дополнительной метаинформации и проверок)
import kotlin.reflect.full.memberProperties

val nameProp = Person::class.memberProperties.find { it.name == "name" }
val viaReflection = nameProp?.get(person)
```

**Плюсы и минусы:**

| Плюсы | Минусы |
|-------|--------|
| Динамическое поведение | Накладные расходы на производительность |
| Универсальные фреймворки | Потеря явной типобезопасности |
| Мощность | Усложнение кода |
| Гибкость | Риски безопасности и нарушения инкапсуляции |

**Когда использовать:**

- **Используйте рефлексию для:**
- Библиотек сериализации (например, библиотеки, использующие `kotlin-reflect`)
- Runtime-based DI фреймворков (например, `Koin`)
- Фреймворков тестирования
- ORM библиотек
- Универсальных утилит, где нужна работа с неизвестными заранее типами

- **С осторожностью относиться к рефлексии для:**
- Критичного по производительности кода
- Простых задач (используйте прямой доступ и обычные вызовы)
- Сценариев, где доступны compile-time альтернативы (kapt/KSP, codegen)
- Операций, критичных для безопасности и инкапсуляции

**Резюме:**

- **Рефлексия**: Исследование/частичное изменение структуры программы во время выполнения
- **Мощная**: Доступ к закрытым членам, динамическое создание экземпляров, обработка аннотаций
- **Затратная**: Накладные расходы на производительность, потеря явной типобезопасности, нарушение инкапсуляции
- **Применения**: Сериализация, DI, тестирование, ORM и другие фреймворки
- **Зависимость**: Для Kotlin runtime reflection часто требуется библиотека `kotlin-reflect`

## Answer (EN)

**Reflection** is a mechanism that allows a program to **inspect and (in limited cases) modify its own structure** (classes, methods, fields, annotations) at runtime.

In Kotlin (using `kotlin-reflect` and/or Java Reflection API), it allows you to:
- `Call` private methods
- Create class instances by name
- Access/modify private fields
- Inspect annotations

It is powerful, but heavy use can harm **type safety, encapsulation, and performance**.

**Setup:**

```kotlin
// build.gradle.kts
dependencies {
    implementation(kotlin("reflect"))
}
```

(The following examples use the Kotlin reflection API from `kotlin-reflect`.)

**Key Uses:**

**1. Get Class Information:**

```kotlin
import kotlin.reflect.full.memberProperties

class Person(val name: String, var age: Int) {
    private fun secret() = "Secret method"
}

val person = Person("Alice", 30)

// Get class
val kClass = person::class
println(kClass.simpleName)  // "Person"
println(kClass.qualifiedName)  // Fully qualified name depending on package

// Get properties
kClass.memberProperties.forEach { prop ->
    println("${prop.name}: ${prop.get(person)}")
}
// Possible output:
// name: Alice
// age: 30
```

**2. Create Instances Dynamically:**

```kotlin
import kotlin.reflect.full.primaryConstructor

// Get KClass by name via Java Reflection
val kClass = Class.forName("com.example.Person").kotlin

// Get constructor (in real code prefer selecting primaryConstructor or by signature)
val constructor = kClass.constructors.first()

// Create instance
val person = constructor.call("Bob", 25)
```

**3. Access Private Members:**

```kotlin
import kotlin.reflect.full.memberFunctions
import kotlin.reflect.full.memberProperties
import kotlin.reflect.jvm.isAccessible

class User(private val password: String) {
    private fun getSecret() = "Secret: $password"
}

val user = User("12345")

// Access private property
val passwordProp = User::class.memberProperties
    .find { it.name == "password" }
passwordProp?.isAccessible = true
val password = passwordProp?.get(user)
println(password)  // "12345"

// Call private method
val secretMethod = User::class.memberFunctions
    .find { it.name == "getSecret" }
secretMethod?.isAccessible = true
val secret = secretMethod?.call(user)
println(secret)  // "Secret: 12345"
```

(Accessing private members via `isAccessible` relies on JVM internals and may be restricted or behave differently across platform versions.)

**4. Inspect Annotations:**

```kotlin
import kotlin.reflect.full.memberProperties

@Target(AnnotationTarget.CLASS)
annotation class Entity(val tableName: String)

@Target(AnnotationTarget.PROPERTY)
annotation class Column(val name: String)

@Entity("users")
data class User(
    @Column("user_id") val id: Int,
    @Column("user_name") val name: String
)

// Get class annotation
val entity = User::class.annotations
    .filterIsInstance<Entity>()
    .firstOrNull()
println(entity?.tableName)  // "users"

// Get property annotations
User::class.memberProperties.forEach { prop ->
    val column = prop.annotations
        .filterIsInstance<Column>()
        .firstOrNull()
    println("${prop.name} -> ${column?.name}")
}
// Output:
// id -> user_id
// name -> user_name
```

**5. Invoke Functions Dynamically:**

```kotlin
import kotlin.reflect.full.memberFunctions

class Calculator {
    fun add(a: Int, b: Int) = a + b
    fun multiply(a: Int, b: Int) = a * b
}

val calc = Calculator()

// Find function by name
val addFunc = Calculator::class.memberFunctions
    .find { it.name == "add" }

// Call it
val result = addFunc?.call(calc, 5, 3)
println(result)  // 8
```

**6. Modify Properties:**

```kotlin
import kotlin.reflect.KMutableProperty
import kotlin.reflect.full.memberProperties

class Settings {
    var theme: String = "light"
}

val settings = Settings()

// Get property reference
val themeProp = Settings::class.memberProperties
    .find { it.name == "theme" } as? KMutableProperty<*>

// Modify it
themeProp?.setter?.call(settings, "dark")
println(settings.theme)  // "dark"
```

**Common Use Cases:**

**Serialization/Deserialization (simplified):**
```kotlin
import kotlin.reflect.full.memberProperties

fun <T : Any> toJson(obj: T): String {
    val kClass = obj::class
    val props = kClass.memberProperties

    val json = props.joinToString(", ") { prop ->
        "\"${prop.name}\": \"${prop.get(obj)}\""
    }

    return "{$json}"
}

data class User(val name: String, val age: Int)

val user = User("Alice", 30)
println(toJson(user))  // {"name": "Alice", "age": "30"}
```

**Dependency Injection (simplified recursive example, for demonstration only):**
```kotlin
import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor

class UserService(val repository: UserRepository)
class UserRepository

fun <T : Any> inject(kClass: KClass<T>): T {
    // Find constructor
    val constructor = kClass.primaryConstructor
        ?: error("Primary constructor required for ${kClass.simpleName}")

    // Resolve dependencies by parameter types
    val params = constructor.parameters.map { param ->
        val depClass = param.type.classifier as? KClass<*>
            ?: error("Unsupported parameter type: ${param.type}")
        inject(depClass)
    }

    // Create instance
    @Suppress("UNCHECKED_CAST")
    return constructor.call(*params.toTypedArray()) as T
}

// Usage (for demonstration only; without caching/graph this is not suitable for production DI)
val service = inject(UserService::class)
```

**Testing - Access Private Members:**
```kotlin
import kotlin.reflect.full.memberFunctions
import kotlin.reflect.jvm.isAccessible

class ViewModel {
    private val repository = UserRepository()

    private fun loadData() {
        // Load data
    }
}

// In test
@Test
fun testLoadData() {
    val viewModel = ViewModel()

    val loadMethod = ViewModel::class.memberFunctions
        .find { it.name == "loadData" }
    loadMethod?.isAccessible = true
    loadMethod?.call(viewModel)

    // Assert results
}
```

**Performance Impact:**

```kotlin
class Person(val name: String)

val person = Person("Alice")

// Direct access — typically faster
val direct = person.name

// Reflection — typically slower (often significantly, due to extra metadata and checks)
import kotlin.reflect.full.memberProperties

val nameProp = Person::class.memberProperties.find { it.name == "name" }
val viaReflection = nameProp?.get(person)
```

**Pros & Cons:**

| Pros | Cons |
|---------|---------|
| Dynamic behavior | Performance overhead |
| Enables generic frameworks | Loss of explicit type safety |
| Powerful | More complex code |
| Flexibility | Security and encapsulation risks |

**When to Use:**

- **Use reflection for:**
- Serialization libraries that rely on runtime introspection
- Runtime-based DI frameworks (e.g., `Koin`)
- Testing frameworks
- ORM libraries
- Generic utilities that must work with unknown types

- **Be cautious with reflection for:**
- Performance-critical code
- Simple tasks (prefer direct access and normal calls)
- Cases where compile-time/codegen alternatives exist (kapt/KSP, annotation processing)
- Security- or encapsulation-critical operations

**Summary:**

- **Reflection**: Inspect / (partially) modify program structure at runtime
- **Powerful**: Access private members, create instances dynamically, process annotations
- **Costly**: Performance overhead, loss of explicit type safety, encapsulation risks
- **Use cases**: Serialization, DI, testing, ORMs, and other frameworks
- **Dependency**: `kotlin-reflect` library is commonly required for runtime reflection

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-object-companion-object--kotlin--medium]]
- [[q-kotlin-serialization--kotlin--easy]]
