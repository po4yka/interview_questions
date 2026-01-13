---
---
---id: lang-035
title: "Throw Vs Throws / Throw против Throws"
aliases: [Throw Vs Throws, Throw против Throws]
topic: kotlin
subtopics: [exceptions, java]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-aggregation, c-app-signing, c-backend, c-binary-search, c-binary-search-tree, c-binder, c-biometric-authentication, c-bm25-ranking, c-by-type, c-cap-theorem, c-ci-cd, c-ci-cd-pipelines, c-clean-code, c-compiler-optimization, c-compose-modifiers, c-compose-phases, c-compose-semantics, c-computer-science, c-concurrency, c-cross-platform-development, c-cross-platform-mobile, c-cs, c-data-classes, c-data-loading, c-debugging, c-declarative-programming, c-deep-linking, c-density-independent-pixels, c-dimension-units, c-dp-sp-units, c-dsl-builders, c-dynamic-programming, c-espresso-testing, c-event-handling, c-folder, c-functional-programming, c-gdpr-compliance, c-gesture-detection, c-gradle-build-cache, c-gradle-build-system, c-https-tls, c-image-formats, c-inheritance, c-jit-aot-compilation, c-kmm, c-kotlin, c-lambda-expressions, c-lazy-grid, c-lazy-initialization, c-level, c-load-balancing, c-manifest, c-memory-optimization, c-memory-profiler, c-microservices, c-multipart-form-data, c-multithreading, c-mutablestate, c-networking, c-offline-first-architecture, c-oop, c-oop-concepts, c-oop-fundamentals, c-oop-principles, c-play-console, c-play-feature-delivery, c-programming-languages, c-properties, c-real-time-communication, c-references, c-scaling-strategies, c-scoped-storage, c-security, c-serialization, c-server-sent-events, c-shader-programming, c-snapshot-system, c-specific, c-strictmode, c-system-ui, c-test-doubles, c-test-sharding, c-testing-pyramid, c-testing-strategies, c-theming, c-to-folder, c-token-management, c-touch-input, c-turbine-testing, c-two-pointers, c-ui-testing, c-ui-ux-accessibility, c-value-classes, c-variable, c-weak-references, c-windowinsets, c-xml]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, exceptions, java, kotlin, programming-languages, throw, throws]
---
# Throw Vs Throws / Throw Против Throws

# Вопрос (RU)
> Разница между throw и throws

---

# Question (EN)
> Difference between throw and throws

## Ответ (RU)

Разница между `throw` и `throws` фундаментальна в обработке исключений (в первую очередь в Java):

### Ключевое Слово `throw`

**Используется для фактического выбрасывания исключения** в конкретном месте кода:

```java
// Java
public void checkAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Возраст не может быть отрицательным");
    }
}

// Kotlin
fun checkAge(age: Int) {
    if (age < 0) {
        throw IllegalArgumentException("Возраст не может быть отрицательным")
    }
}
```

**Характеристики**:
- Используется внутри тела метода / функции
- Выбрасывает экземпляр исключения (созданный в этот момент или заранее)
- Выполнение текущего потока на этом пути останавливается и управление передается обработчику исключений
- В Java при создании используется `new`, в Kotlin без `new`

### Ключевое Слово `throws`

**Используется в сигнатуре метода** для объявления, что метод может выбросить исключения (только Java, для checked-исключений):

```java
// Java - должны объявлять checked exceptions
public void readFile(String path) throws IOException {
    // Может выбросить IOException (включая его подклассы)
    FileReader reader = new FileReader(path);
}

// Должны обработать или объявить
public void processFile() throws IOException {
    readFile("data.txt");  // Пробрасываем исключение
}

// Или поймать
public void safeProcessFile() {
    try {
        readFile("data.txt");
    } catch (IOException e) {
        System.out.println("Ошибка чтения файла");
    }
}
```

**Примечание**: В Kotlin **нет ключевого слова `throws`**. На уровне языка все исключения ведут себя как unchecked: компилятор не требует объявления или обязательной обработки исключений.

```kotlin
// Kotlin - объявление throws не требуется
fun readFile(path: String) {
    // Может выбросить IOException, но объявления не нужно
    val reader = FileReader(path)
}

// Принудительная обработка не требуется
fun processFile() {
    readFile("data.txt")  // OK, try-catch не обязателен
}
```

### Таблица Сравнения

| Аспект | `throw` | `throws` |
|--------|---------|----------|
| **Назначение** | Фактически выбросить исключение | Объявить возможные checked-исключения |
| **Расположение** | Внутри тела метода/функции | Сигнатура метода |
| **Язык** | Java и Kotlin | Только Java (нет в Kotlin) |
| **Действие** | Выбрасывает исключение | Только объявляет (для компилятора) |
| **Синтаксис** | `throw new Exception()` (Java), `throw Exception()` (Kotlin) | `throws Exception` |
| **Обязательность** | Когда нужно выбросить | Для checked exceptions в Java (handle-or-declare) |

### Пример С Оба Ключевыми Словами (Java)

```java
// Java - использование обоих throw и throws
public class FileProcessor {
    // throws: объявляет checked-исключение
    public void processFile(String path) throws IOException {
        if (path == null) {
            // throw: фактически выбрасывает исключение
            throw new IllegalArgumentException("Путь не может быть null");
        }

        FileReader reader = new FileReader(path);  // Может выбросить IOException
        // ... обработка файла (упрощенный пример)
    }
}
```

### Пример Kotlin (только throw)

```kotlin
// Kotlin - только throw, нет throws
class FileProcessor {
    fun processFile(path: String) {
        if (path.isEmpty()) {
            // throw: фактически выбрасывает исключение
            throw IllegalArgumentException("Путь не может быть пустым")
        }

        val reader = FileReader(path)  // Может выбросить IOException (как unchecked с точки зрения Kotlin)
        // ... обработка файла (упрощенный пример)
    }
}
```

### Аннотация `@Throws` В Kotlin

Для совместимости с Java, Kotlin имеет аннотацию `@Throws`:

```kotlin
// Kotlin
@Throws(IOException::class, FileNotFoundException::class)
fun readFile(path: String) {
    val reader = FileReader(path)
}

// Java-код, вызывающий эту Kotlin-функцию, увидит сигнатуру:
// public void readFile(String path) throws IOException, FileNotFoundException
```

**Когда использовать**:
- Пишете Kotlin-библиотеку, используемую Java-кодом
- Хотите, чтобы Java-вызывающие явно обрабатывали конкретные исключения
- В чистом Kotlin обычно не требуется

### Распространенные Ошибки

**1. Использование `throws` в Kotlin:**
```kotlin
// Неправильно - ключевого слова throws нет в Kotlin
fun readFile() throws IOException {  // Ошибка компиляции!
}

// Правильно - просто выбросить исключение при необходимости
fun readFile() {
    throw IOException("Ошибка")
}
```

**2. Забыть ключевое слово `throw`:**
```java
// Неправильно - просто создаем исключение, не выбрасывая его
if (age < 0) {
    new IllegalArgumentException("Недопустимо");  // Ничего не делает!
}

// Правильно - фактически выбрасываем
if (age < 0) {
    throw new IllegalArgumentException("Недопустимо");
}
```

### Резюме

**`throw`**:
- Фактически выполняет выбрасывание исключения
- Используется в теле метода/функции
- Работает и в Java, и в Kotlin
- Синтаксис: `throw ExceptionInstance`

**`throws`**:
- Объявляет возможные (как правило checked) исключения
- Используется в сигнатуре метода
- Только Java (в Kotlin вместо этого при необходимости используют аннотацию `@Throws` для interop с Java)
- Синтаксис: `throws ExceptionType1, ExceptionType2`

**Ключевое различие**: `throw` — действие (выбрасывает исключение), `throws` — декларация для компилятора и вызывающего кода (сообщает, что метод может выбросить исключение).

### Практические Примеры Использования

**Пример 1: Валидация данных (Kotlin)**
```kotlin
fun validateAge(age: Int) {
    if (age < 0) {
        throw IllegalArgumentException("Возраст не может быть отрицательным")
    }
    if (age > 150) {
        throw IllegalArgumentException("Возраст слишком большой")
    }
}

// Использование
try {
    validateAge(-5)
} catch (e: IllegalArgumentException) {
    println("Ошибка валидации: ${e.message}")
}
```

**Пример 2: Работа с файлами (Java)**
```java
// Java - объявляем IOException
public String readFileContent(String path) throws IOException {
    if (path == null || path.isEmpty()) {
        throw new IllegalArgumentException("Путь не может быть пустым");
    }

    BufferedReader reader = new BufferedReader(new FileReader(path));
    return reader.readLine();  // Упрощенный пример, без закрытия ресурса
}

// Вызывающий код должен обработать исключение
public void processFile() {
    try {
        String content = readFileContent("data.txt");
        System.out.println(content);
    } catch (IOException e) {
        System.err.println("Ошибка чтения файла: " + e.getMessage());
    }
}
```

**Пример 3: Кастомные исключения (Kotlin)**
```kotlin
class InsufficientBalanceException(
    val balance: Double,
    val amount: Double
) : Exception("Недостаточно средств. Баланс: $balance, требуется: $amount")

class BankAccount(private var balance: Double) {
    fun withdraw(amount: Double) {
        if (amount > balance) {
            throw InsufficientBalanceException(balance, amount)
        }
        balance -= amount
    }
}

// Использование
val account = BankAccount(100.0)
try {
    account.withdraw(150.0)
} catch (e: InsufficientBalanceException) {
    println(e.message)
    println("Баланс: ${e.balance}, попытка снять: ${e.amount}")
}
```

**Пример 4: Цепочка исключений (Kotlin)**
```kotlin
class DataProcessingException(message: String, cause: Throwable)
    : Exception(message, cause)

fun processData(data: String) {
    try {
        val result = data.toInt()
    } catch (e: NumberFormatException) {
        throw DataProcessingException(
            "Не удалось обработать данные: $data",
            e
        )
    }
}

// Использование
try {
    processData("abc")
} catch (e: DataProcessingException) {
    println("Ошибка: ${e.message}")
    println("Причина: ${e.cause?.message}")
}
```

**Пример 5: Несколько исключений (Java)**
```java
// Java - объявление нескольких исключений
public void connectToDatabase(String url)
    throws SQLException, ClassNotFoundException {

    if (url == null) {
        throw new IllegalArgumentException("URL не может быть null");
    }

    Class.forName("com.mysql.jdbc.Driver");
    DriverManager.getConnection(url);
}

// Обработка нескольких типов исключений
public void initDatabase() {
    try {
        connectToDatabase("jdbc:mysql://localhost/db");
    } catch (SQLException e) {
        System.err.println("Ошибка БД: " + e.getMessage());
    } catch (ClassNotFoundException e) {
        System.err.println("Драйвер не найден: " + e.getMessage());
    }
}
```

### Лучшие Практики

1. Используйте специфичные типы исключений — не бросайте общий `Exception` без необходимости.
2. Добавляйте осмысленные сообщения — помогайте понять причину ошибки.
3. В Kotlin используйте `@Throws` только для interop с Java, а не в чисто Kotlin-коде.
4. Не игнорируйте исключения — обрабатывайте или логируйте их.
5. Создавайте кастомные исключения для доменных ошибок при необходимости.
6. Документируйте важные исключения в комментариях/документации, даже если Kotlin не требует `throws`.

## Answer (EN)

The difference between `throw` and `throws` is fundamental in exception handling (primarily in Java):

### `throw` Keyword

**Used to actually throw an exception** at a specific point in code:

```java
// Java
public void checkAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Age cannot be negative");
    }
}

// Kotlin
fun checkAge(age: Int) {
    if (age < 0) {
        throw IllegalArgumentException("Age cannot be negative")
    }
}
```

**Characteristics:**
- Used inside a method/function body
- Throws an exception instance (created at that moment or earlier)
- Control flow for that path stops and is transferred to exception handling
- Uses `new` when creating in Java; no `new` in Kotlin

### `throws` Keyword

**Used in a method signature** to declare that the method may throw exceptions (Java only, for checked exceptions):

```java
// Java - must declare checked exceptions
public void readFile(String path) throws IOException {
    // May throw IOException (including its subclasses)
    FileReader reader = new FileReader(path);
}

// Must handle or declare
public void processFile() throws IOException {
    readFile("data.txt");  // Propagate exception
}

// Or catch
public void safeProcessFile() {
    try {
        readFile("data.txt");
    } catch (IOException e) {
        System.out.println("Error reading file");
    }
}
```

**Note:** Kotlin **does not have a `throws` keyword**. At the language level, all exceptions are treated as unchecked: the compiler does not require you to declare or catch them.

```kotlin
// Kotlin - no throws declaration needed
fun readFile(path: String) {
    // May throw IOException, but no declaration required
    val reader = FileReader(path)
}

// No forced handling
fun processFile() {
    readFile("data.txt");  // OK, no try-catch required
}
```

### Comparison Table

| Aspect | `throw` | `throws` |
|--------|---------|----------|
| **Purpose** | Actually throw an exception | Declare possible checked exceptions |
| **Location** | Inside method/function body | Method signature |
| **Language** | Java & Kotlin | Java only (not in Kotlin) |
| **Action** | Performs the throw | Declaration for compiler/callers |
| **Syntax** | `throw new Exception()` (Java), `throw Exception()` (Kotlin) | `throws Exception` |
| **Mandatory** | When you want to throw | For checked exceptions in Java (handle-or-declare) |

### Java Example (Both Keywords)

```java
// Java - using both throw and throws
public class FileProcessor {
    // throws: declares a checked exception
    public void processFile(String path) throws IOException {
        if (path == null) {
            // throw: actually throws an exception
            throw new IllegalArgumentException("Path cannot be null");
        }

        FileReader reader = new FileReader(path);  // May throw IOException
        // ... process file (simplified)
    }
}
```

### Kotlin Example (Only throw)

```kotlin
// Kotlin - only throw, no throws
class FileProcessor {
    fun processFile(path: String) {
        if (path.isEmpty()) {
            // throw: actually throws an exception
            throw IllegalArgumentException("Path cannot be empty")
        }

        val reader = FileReader(path);  // May throw IOException (treated as unchecked in Kotlin)
        // ... process file (simplified)
    }
}
```

### Kotlin `@Throws` Annotation

For Java interoperability, Kotlin has the `@Throws` annotation:

```kotlin
// Kotlin
@Throws(IOException::class, FileNotFoundException::class)
fun readFile(path: String) {
    val reader = FileReader(path)
}

// Java code calling this Kotlin function will see:
// public void readFile(String path) throws IOException, FileNotFoundException
```

**When to use:**
- Writing a Kotlin library consumed by Java code
- You want Java callers to be forced/encouraged to handle specific exceptions
- Otherwise usually not needed in pure Kotlin code

### Common Errors

**1. Using `throws` in Kotlin:**
```kotlin
// Wrong - 'throws' keyword doesn't exist in Kotlin
fun readFile() throws IOException {  // Compilation error!
}

// Correct - just throw when needed
fun readFile() {
    throw IOException("Error")
}
```

**2. Forgetting the `throw` keyword:**
```java
// Wrong - just creating an exception, not throwing it
if (age < 0) {
    new IllegalArgumentException("Invalid");  // Does nothing!
}

// Correct - actually throw it
if (age < 0) {
    throw new IllegalArgumentException("Invalid");
}
```

### Summary

**`throw`:**
- Performs the actual throwing of an exception
- Used inside method/function body
- Available in both Java and Kotlin
- Syntax: `throw ExceptionInstance`

**`throws`:**
- Declares possible (typically checked) exceptions
- Used in method signature
- Java only (Kotlin uses `@Throws` for Java interop when needed)
- Syntax: `throws ExceptionType1, ExceptionType2`

**Key difference:** `throw` is an action (throws an exception), `throws` is a declaration for the compiler and callers (states that a method may throw exceptions).

---

## Дополнительные Вопросы (RU)

- Как это связано с проверяемыми (`checked`) и непроверяемыми (`unchecked`) исключениями в Java?
- В каких случаях стоит использовать `throws` в Java вместо того, чтобы полагаться только на непроверяемые исключения?
- Какие подводные камни возникают при смешанном использовании Kotlin и Java с разной моделью обработки исключений?

## Follow-ups

- How does this relate to Java's checked vs unchecked exceptions?
- When would you use `throws` in Java vs relying on unchecked exceptions?
- What are common pitfalls when mixing Kotlin and Java exception handling?

## Ссылки (RU)

- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-sealed-vs-enum-classes--kotlin--medium]]

## Related Questions

- [[q-sealed-vs-enum-classes--kotlin--medium]]
