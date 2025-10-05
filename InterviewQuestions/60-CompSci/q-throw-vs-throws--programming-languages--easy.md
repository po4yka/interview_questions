---
id: 20251003141213
title: throw vs throws / Разница между throw и throws
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, exceptions]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1410
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-exceptions
  - c-java-exceptions

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, java, exceptions, throw, throws, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

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
// ❌ Wrong - throws doesn't exist in Kotlin
fun readFile() throws IOException {  // Compilation error!
}

// ✅ Correct - just throw if needed
fun readFile() {
    throw IOException("Error")
}
```

**2. Forgetting throw keyword:**
```java
// ❌ Wrong - just creating exception, not throwing
if (age < 0) {
    new IllegalArgumentException("Invalid");  // Does nothing!
}

// ✅ Correct - actually throw it
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

## Ответ (RU)

throw используется для генерации исключения в конкретном месте кода. throws указывается в сигнатуре метода и сообщает что метод может выбросить исключение (только в Java, в Kotlin нет throws).

---

## Follow-ups
- What are checked vs unchecked exceptions?
- Why doesn't Kotlin have checked exceptions?
- How to use @Throws annotation in Kotlin?

## References
- [[c-kotlin-exceptions]]
- [[c-java-exceptions]]
- [[moc-kotlin]]

## Related Questions
- [[q-checked-unchecked-exceptions--programming-languages--medium]]
- [[q-exception-handling-kotlin--programming-languages--medium]]
