---
id: "20251015082237125"
title: "Throw Vs Throws / Throw против Throws"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - exceptions
  - java
  - kotlin
  - programming-languages
  - throw
  - throws
---
# Разница между throw и throws

# Question (EN)
> Difference between throw and throws

# Вопрос (RU)
> Разница между throw и throws

---

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

## Ответ (RU)

Разница между `throw` и `throws` фундаментальна в обработке исключений:

### Ключевое слово `throw`

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

### Ключевое слово `throws`

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

### Таблица сравнения

| Аспект | `throw` | `throws` |
|--------|---------|----------|
| **Назначение** | Выбросить исключение | Объявить возможные исключения |
| **Расположение** | Внутри тела метода | Сигнатура метода |
| **Язык** | Java и Kotlin | Только Java (не в Kotlin) |
| **Действие** | Фактически выбрасывает | Только объявляет |
| **Синтаксис** | `throw new Exception()` | `throws Exception` |
| **Обязательность** | Когда нужно выбросить | Для checked exceptions (Java) |

### Аннотация @Throws в Kotlin

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

### Распространенные ошибки

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

