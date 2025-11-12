---
id: lang-032
title: "Kotlin Internal Modifier / Модификатор internal в Kotlin"
aliases: [Kotlin Internal Modifier, Модификатор internal в Kotlin]
topic: kotlin
subtopics: [access-control, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-flow-completion-oncompletion--kotlin--medium, q-flow-exception-handling--kotlin--medium, q-inheritance-open-final--kotlin--medium]
created: 2024-10-15
updated: 2025-11-09
tags: [access-modifiers, difficulty/medium, internal, module, programming-languages, visibility]
---
# Вопрос (RU)
> Что известно про `internal`?

# Question (EN)
> What is known about `internal`?

## Ответ (RU)

`internal` — это модификатор видимости с областью для всего модуля.

Модуль в контексте Kotlin — это набор файлов, компилируемых вместе, обычно это отдельный модуль Gradle/Maven или модуль проекта в IntelliJ.

Объявления с модификатором `internal` видны только внутри одного модуля и недоступны из других модулей. Это полезно для сокрытия деталей реализации между слоями или при использовании многомодульной архитектуры.

**Ключевые особенности:**

- Видимость только внутри одного модуля
- Недоступен из других модулей
- «Модуль» = набор файлов, компилируемых вместе (часто модуль Gradle/Maven/IntelliJ)
- Помогает инкапсулировать реализацию между модулями

**Пример:**

```kotlin
// Модуль: :app
internal class DatabaseHelper {
    fun connect() = println("Connected")
}

internal fun log(message: String) {
    println("[LOG] $message")
}

class UserRepository {
    private val db = DatabaseHelper()  // OK - тот же модуль

    fun getUser(id: Int) {
        log("Getting user $id")  // OK - тот же модуль
        db.connect()
    }
}
```

**Пример для многомодульного проекта:**

```
project/
 core/  (module)
    NetworkClient.kt
 app/  (module)
     MainActivity.kt
```

**core/NetworkClient.kt:**
```kotlin
// Видимо только внутри модуля :core
internal class NetworkClient {
    fun makeRequest(url: String): String {
        return "Response from $url"
    }
}

// Публичное API модуля
class ApiService {
    private val client = NetworkClient()  // OK - тот же модуль

    fun getData(): String {
        return client.makeRequest("https://api.example.com")
    }
}
```

**app/MainActivity.kt:**
```kotlin
class MainActivity {
    fun loadData() {
        val api = ApiService()  // OK - public класс
        api.getData()

        // ОШИБКА - NetworkClient является internal в модуле :core
        // val client = NetworkClient()  // Ошибка компиляции: cannot access 'NetworkClient'
    }
}
```

**Сравнение с другими модификаторами:**

| Модификатор | Область видимости                | Применение                    |
|------------|-----------------------------------|-------------------------------|
| private    | Тот же файл/класс                 | Детали реализации             |
| protected  | Класс + подклассы                 | API для наследования          |
| internal   | Тот же модуль                     | Реализация модуля             |
| public     | Везде                             | Публичное API                 |

**Типичные сценарии использования:**

1. Сокрытие реализации внутри модуля:
```kotlin
// Модуль библиотеки
internal class CacheImpl {
    private val cache = mutableMapOf<String, Any>()

    fun get(key: String): Any? = cache[key]
    fun put(key: String, value: Any) {
        cache[key] = value
    }
}

// Публичное API
class CacheManager {
    private val cache = CacheImpl()

    fun getData(key: String): Any? = cache.get(key)
    fun saveData(key: String, value: Any) = cache.put(key, value)
}
```

2. Многомодульная архитектура:
```kotlin
// Модуль :data
internal interface UserLocalDataSource {
    fun getUser(id: Int): User
}

internal class UserDatabase : UserLocalDataSource {
    override fun getUser(id: Int): User {
        // Реализация доступа к базе данных
        TODO("Provide implementation")
    }
}

// Публичный репозиторий
class UserRepository(
    private val localSource: UserLocalDataSource = UserDatabase()
) {
    fun getUser(id: Int): User {
        return localSource.getUser(id)
    }
}
```

3. Внутренние утилиты:
```kotlin
// Модуль :utils
internal object StringUtils {
    fun capitalize(str: String): String {
        return str.replaceFirstChar { it.uppercase() }
    }
}

// Публичное API использует internal-утилиты
class TextFormatter {
    fun formatName(name: String): String {
        return StringUtils.capitalize(name)  // OK - тот же модуль
    }
}
```

**internal vs private:**

```kotlin
// Файл: Utils.kt

// private - видно только в этом файле
private fun helperFunction() = "Helper"

// internal - видно во всём модуле
internal fun utilityFunction() = "Utility"

class MyClass {
    // private - видно только внутри этого класса
    private val secret = "Secret"

    // internal - видно во всём модуле
    internal val config = "Config"
}
```

**Java-взаимодействие:**

В байткоде JVM модификатор `internal` компилируется как `public` с модифицированными (mangled) именами. JVM не знает о границах модулей Kotlin и не может их жёстко применять.

```kotlin
// Kotlin (файл: Utils.kt)
internal fun processData() = "Data"
```

```java
// В Java это будет public-метод со специальным (mangled) именем в сгенерированном классе.
// Конкретное имя является деталями реализации компилятора и не должно полагаться как стабильное API.
// Например (упрощённо):
// UtilsKt.processData$internal();
```

Поэтому `internal` не следует рассматривать как надёжный механизм инкапсуляции на уровне байткода для Java-клиентов; это, в первую очередь, языковая конструкция видимости в Kotlin.

**Рекомендации:**

- Используйте `internal`, когда:
  - строите многомодульный проект;
  - хотите скрыть детали реализации от других модулей;
  - разрабатываете библиотеку с чётким публичным API и внутренней реализацией.

- Не полагайтесь на `internal`, когда:
  - проект одномодульный, и достаточно `private`/`protected`;
  - нужна явная видимость между модулями (используйте `public`);
  - требуется жёстко контролировать API для Java/байткод-клиентов — лучше явно проектировать публичное API.

**Итог:**

- `internal` = модульная область видимости;
- видно внутри модуля, недоступно из других модулей в Kotlin-коде;
- модуль = набор файлов, компилируемых вместе (часто модуль Gradle/Maven/IntelliJ);
- полезен в многомодульной архитектуре;
- помогает инкапсулировать детали реализации.

## Answer (EN)

`internal` is an access modifier that provides module-level visibility.

A "module" in Kotlin is a set of files compiled together, typically represented by one Gradle/Maven module or IntelliJ module.

Declarations marked with `internal` are visible only within the same module and are not accessible from other modules. This is useful for hiding implementation details between layers or when using a multi-module architecture.

**Key Features:**

- Visible only within the same module
- Not visible from other modules
- "Module" = a set of files compiled together (commonly a Gradle/Maven/IntelliJ module)
- Supports encapsulation between modules

**Example:**

```kotlin
// Module: :app
internal class DatabaseHelper {
    fun connect() = println("Connected")
}

internal fun log(message: String) {
    println("[LOG] $message")
}

class UserRepository {
    private val db = DatabaseHelper()  // OK - same module

    fun getUser(id: Int) {
        log("Getting user $id")  // OK - same module
        db.connect()
    }
}
```

**Multi-Module Example:**

```
project/
 core/  (module)
    NetworkClient.kt
 app/  (module)
     MainActivity.kt
```

**core/NetworkClient.kt:**
```kotlin
// This is visible only within :core module
internal class NetworkClient {
    fun makeRequest(url: String): String {
        return "Response from $url"
    }
}

// Public API of the module
class ApiService {
    private val client = NetworkClient()  // OK - same module

    fun getData(): String {
        return client.makeRequest("https://api.example.com")
    }
}
```

**app/MainActivity.kt:**
```kotlin
class MainActivity {
    fun loadData() {
        val api = ApiService()  // OK - public class
        api.getData()

        // ERROR - NetworkClient is internal to :core module
        // val client = NetworkClient()  // Compilation error: cannot access 'NetworkClient'
    }
}
```

**Comparison with Other Modifiers:**

| Modifier  | Visibility           | Example                    |
|-----------|----------------------|----------------------------|
| private   | Same file/class only | Implementation details     |
| protected | Class + subclasses   | Inheritance API            |
| internal  | Same module only     | Module implementation      |
| public    | Everywhere           | Public API                 |

**Use Cases:**

**1. Hide Implementation:**
```kotlin
// Library module
internal class CacheImpl {
    private val cache = mutableMapOf<String, Any>()

    fun get(key: String): Any? = cache[key]
    fun put(key: String, value: Any) {
        cache[key] = value
    }
}

// Public API
class CacheManager {
    private val cache = CacheImpl()

    fun getData(key: String): Any? = cache.get(key)
    fun saveData(key: String, value: Any) = cache.put(key, value)
}
```

**2. Multi-Module Architecture:**
```kotlin
// :data module
internal interface UserLocalDataSource {
    fun getUser(id: Int): User
}

internal class UserDatabase : UserLocalDataSource {
    override fun getUser(id: Int): User {
        // Database implementation
        TODO("Provide implementation")
    }
}

// Public repository
class UserRepository(
    private val localSource: UserLocalDataSource = UserDatabase()
) {
    fun getUser(id: Int): User {
        return localSource.getUser(id)
    }
}
```

**3. Internal Utilities:**
```kotlin
// :utils module
internal object StringUtils {
    fun capitalize(str: String): String {
        return str.replaceFirstChar { it.uppercase() }
    }
}

// Public API uses internal utils
class TextFormatter {
    fun formatName(name: String): String {
        return StringUtils.capitalize(name)  // OK - same module
    }
}
```

**internal vs private:**

```kotlin
// File: Utils.kt

// private - visible only in this file
private fun helperFunction() = "Helper"

// internal - visible in entire module
internal fun utilityFunction() = "Utility"

class MyClass {
    // private - visible only in this class
    private val secret = "Secret"

    // internal - visible in entire module
    internal val config = "Config"
}
```

**Java Interoperability:**

In Java, Kotlin `internal` declarations are compiled as `public` members with mangled names. The JVM does not know about Kotlin module boundaries and cannot enforce them.

```kotlin
// Kotlin (file: Utils.kt)
internal fun processData() = "Data"
```

```java
// In Java this appears as a public method with a compiler-generated (mangled) name
// in the corresponding generated class. The exact name is an implementation detail
// and must not be relied upon as a stable API.
// For example (simplified):
// UtilsKt.processData$internal();
```

Because of this, `internal` should not be relied upon as a strict encapsulation mechanism for Java consumers at the bytecode level; it is primarily a Kotlin-language visibility construct.

**Best Practices:**

- Use `internal` when:
  - Building a multi-module project
  - You want to hide implementation details from other modules
  - Creating a library with a clear public API and internal implementation surface

- Avoid relying on `internal` when:
  - You have a single-module project where `private`/`protected` is sufficient
  - You intentionally need visibility across modules (use `public`)
  - You must provide a stable, clearly enforced API surface for Java/bytecode consumers (design explicit public API instead)

**Summary:**

- `internal` = module-level visibility
- Visible within a module, inaccessible from other modules in Kotlin source
- Module = a set of files compiled together (often a Gradle/Maven/IntelliJ module)
- Useful for multi-module architecture
- Helps encapsulate implementation details

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия от модификаторов в Java?
- Когда вы бы использовали `internal` на практике?
- Какие типичные ошибки стоит избегать при использовании `internal`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-inheritance-open-final--kotlin--medium]]
- [[q-flow-completion-oncompletion--kotlin--medium]]
- [[q-flow-exception-handling--kotlin--medium]]

## Related Questions

- [[q-inheritance-open-final--kotlin--medium]]
- [[q-flow-completion-oncompletion--kotlin--medium]]
- [[q-flow-exception-handling--kotlin--medium]]
