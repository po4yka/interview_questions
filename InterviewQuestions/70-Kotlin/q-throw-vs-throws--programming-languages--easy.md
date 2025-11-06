---
id: lang-035
title: "Throw Vs Throws / Throw против Throws"
aliases: [Throw Vs Throws, Throw против Throws]
topic: programming-languages
subtopics: [error-handling, exception-handling, java]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-sealed-vs-enum-classes--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, exceptions, java, kotlin, programming-languages, throw, throws]
---
# Разница Между Throw И Throws

# Вопрос (RU)
> Разница между throw и throws

---

# Question (EN)
> Difference between throw and throws

## Ответ (RU)

Разница между `throw` и `throws` фундаментальна в обработке исключений:

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
- Используется внутри тела метода
- Фактически создает и выбрасывает экземпляр исключения
- Выполнение останавливается в этой точке
- В Java используется с `new`, в Kotlin без `new`

### Ключевое Слово `throws`

**Используется в сигнатуре метода** для объявления что метод может выбросить исключения (только Java):

```java
// Java - должны объявлять checked exceptions
public void readFile(String path) throws IOException, FileNotFoundException {
    // Может выбросить эти исключения
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

**Примечание**: Kotlin **не имеет ключевого слова `throws`**! Все исключения unchecked.

```kotlin
// Kotlin - объявление throws не требуется
fun readFile(path: String) {
    // Может выбросить IOException, но объявление не нужно
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
| **Назначение** | Выбросить исключение | Объявить возможные исключения |
| **Расположение** | Внутри тела метода | Сигнатура метода |
| **Язык** | Java и Kotlin | Только Java (не в Kotlin) |
| **Действие** | Фактически выбрасывает | Только объявляет |
| **Синтаксис** | `throw new Exception()` | `throws Exception` |
| **Обязательность** | Когда нужно выбросить | Для checked exceptions (Java) |

### Пример С Обоими Ключевыми Словами (Java)

```java
// Java - использование обоих throw и throws
public class FileProcessor {
    // throws: объявляет исключение
    public void processFile(String path) throws IOException {
        if (path == null) {
            // throw: фактически выбрасывает исключение
            throw new IllegalArgumentException("Путь не может быть null");
        }

        FileReader reader = new FileReader(path);  // Может выбросить IOException
        // ... обработка файла
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

        val reader = FileReader(path)  // Может выбросить IOException (unchecked)
        // ... обработка файла
    }
}
```

### Аннотация @Throws В Kotlin

Для совместимости с Java, Kotlin имеет аннотацию `@Throws`:

```kotlin
// Kotlin
@Throws(IOException::class, FileNotFoundException::class)
fun readFile(path: String) {
    val reader = FileReader(path)
}

// Java код вызывающий эту Kotlin функцию увидит:
// public void readFile(String path) throws IOException, FileNotFoundException
```

**Когда использовать**:
- Пишете Kotlin библиотеку используемую Java кодом
- Хотите чтобы Java вызывающие обрабатывали конкретные исключения
- В противном случае, не нужно в чистом Kotlin

### Распространенные Ошибки

**1. Использование throws в Kotlin:**
```kotlin
// Неправильно - throws не существует в Kotlin
fun readFile() throws IOException {  // Ошибка компиляции!
}

// Правильно - просто throw если нужно
fun readFile() {
    throw IOException("Ошибка")
}
```

**2. Забыть ключевое слово throw:**
```java
// Неправильно - просто создание исключения, не выбрасывание
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
- Выполняет выбрасывание исключения
- Используется в теле метода
- Оба Java и Kotlin
- Синтаксис: `throw ExceptionInstance`

**`throws`**:
- Объявляет возможные исключения
- Используется в сигнатуре метода
- Только Java (Kotlin использует аннотацию `@Throws` для interop)
- Синтаксис: `throws ExceptionType1, ExceptionType2`

**Ключевое различие**: `throw` - это действие (выбрасывает исключение), `throws` - это декларация (объявляет что метод может выбросить).

### Практические Примеры Использования

**Пример 1: Валидация данных**
```kotlin
// Kotlin
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
// Java - должны объявлять IOException
public String readFileContent(String path) throws IOException {
    if (path == null || path.isEmpty()) {
        throw new IllegalArgumentException("Путь не может быть пустым");
    }

    BufferedReader reader = new BufferedReader(new FileReader(path));
    return reader.readLine();
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

**Пример 3: Кастомные исключения**
```kotlin
// Kotlin - создание собственного исключения
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

**Пример 4: Цепочка исключений**
```kotlin
// Kotlin - обертывание исключений
class DataProcessingException(message: String, cause: Throwable)
    : Exception(message, cause)

fun processData(data: String) {
    try {
        // Некоторая обработка
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

**Пример 5: Multiple exceptions (Java)**
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

// Обработка нескольких исключений
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

1. **Используйте специфичные исключения** - не бросайте общий `Exception`
2. **Добавляйте осмысленные сообщения** - помогите понять причину ошибки
3. **В Kotlin избегайте @Throws** - используйте только для Java interop
4. **Не игнорируйте исключения** - всегда обрабатывайте или логируйте
5. **Создавайте кастомные исключения** - для доменных ошибок
6. **Документируйте исключения** - укажите когда метод может выбросить исключение

## Answer (EN)

The difference between `throw` and `throws` is fundamental in exception handling:

### `throw` Keyword

**Used to actually throw an exception** at a specific place in code:

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
- Used **inside method body**
- Actually creates and throws an exception instance
- Execution stops at that point
- Used with `new` in Java (without `new` in Kotlin)

### `throws` Keyword

**Used in method signature** to declare that method may throw exceptions (Java only):

```java
// Java - must declare checked exceptions
public void readFile(String path) throws IOException, FileNotFoundException {
    // May throw these exceptions
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

**Note:** Kotlin **does not have `throws` keyword**! All exceptions are unchecked.

```kotlin
// Kotlin - no throws declaration needed
fun readFile(path: String) {
    // May throw IOException, but no declaration required
    val reader = FileReader(path)
}

// No forced handling
fun processFile() {
    readFile("data.txt")  // OK, no try-catch required
}
```

### Comparison Table

| Aspect | `throw` | `throws` |
|--------|---------|----------|
| **Purpose** | Throw exception | Declare possible exceptions |
| **Location** | Inside method body | Method signature |
| **Language** | Java & Kotlin | Java only (not in Kotlin) |
| **Action** | Actually throws | Only declares |
| **Syntax** | `throw new Exception()` | `throws Exception` |
| **Mandatory** | When you want to throw | For checked exceptions (Java) |

### Java Example (Both Keywords)

```java
// Java - using both throw and throws
public class FileProcessor {
    // throws: declares exception
    public void processFile(String path) throws IOException {
        if (path == null) {
            // throw: actually throws exception
            throw new IllegalArgumentException("Path cannot be null");
        }

        FileReader reader = new FileReader(path);  // May throw IOException
        // ... process file
    }
}
```

### Kotlin Example (Only throw)

```kotlin
// Kotlin - only throw, no throws
class FileProcessor {
    fun processFile(path: String) {
        if (path.isEmpty()) {
            // throw: actually throws exception
            throw IllegalArgumentException("Path cannot be empty")
        }

        val reader = FileReader(path)  // May throw IOException (unchecked)
        // ... process file
    }
}
```

### Kotlin @Throws Annotation

For Java interoperability, Kotlin has `@Throws` annotation:

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
- Writing Kotlin library used by Java code
- Want Java callers to handle specific exceptions
- Otherwise, not needed in pure Kotlin

### Common Errors

**1. Using throws in Kotlin:**
```kotlin
// - Wrong - throws doesn't exist in Kotlin
fun readFile() throws IOException {  // Compilation error!
}

// - Correct - just throw if needed
fun readFile() {
    throw IOException("Error")
}
```

**2. Forgetting throw keyword:**
```java
// - Wrong - just creating exception, not throwing
if (age < 0) {
    new IllegalArgumentException("Invalid");  // Does nothing!
}

// - Correct - actually throw it
if (age < 0) {
    throw new IllegalArgumentException("Invalid");
}
```

### Summary

**`throw`:**
- Executes an exception throw
- Used in method body
- Both Java and Kotlin
- Syntax: `throw ExceptionInstance`

**`throws`:**
- Declares possible exceptions
- Used in method signature
- Java only (Kotlin uses `@Throws` annotation for interop)
- Syntax: `throws ExceptionType1, ExceptionType2`

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-sealed-vs-enum-classes--programming-languages--medium]]
-
