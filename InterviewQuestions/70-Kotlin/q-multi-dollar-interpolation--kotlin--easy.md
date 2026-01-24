---
anki_cards:
- slug: q-multi-dollar-interpolation--kotlin--easy-0-en
  language: en
  anki_id: 1769173416259
  synced_at: '2026-01-23T17:03:51.529072'
- slug: q-multi-dollar-interpolation--kotlin--easy-0-ru
  language: ru
  anki_id: 1769173416285
  synced_at: '2026-01-23T17:03:51.530072'
---
# Вопрос (RU)
> Объясните multi-dollar интерполяцию строк в Kotlin. Когда и как её использовать?

# Question (EN)
> Explain multi-dollar string interpolation in Kotlin. When and how do you use it?

## Ответ (RU)

**Введено в Kotlin 2.1, стабильно с 2.2**

**Multi-dollar string interpolation** позволяет использовать несколько знаков доллара (`$$`, `$$$` и т.д.) для изменения символа интерполяции. Это упрощает работу со строками, содержащими литеральные доллары.

---

### Синтаксис

```kotlin
// Обычная интерполяция
val name = "World"
println("Hello, $name!")  // Hello, World!

// Multi-dollar интерполяция
val price = 100
println($"Price: $price")           // Price: $price (литерал)
println($$"Price: $$price")         // Price: 100 (интерполяция)
println($$"Cost: $10, Total: $$price")  // Cost: $10, Total: 100
```

---

### Зачем это нужно

**Проблема с обычными строками:**

```kotlin
// Нужно экранировать каждый доллар
val template = "Price: \$100, Tax: \${tax}"
println(template)  // Price: $100, Tax: ${tax}

// В JSON
val json = """{"price": "\$100"}"""
```

**Решение с multi-dollar:**

```kotlin
// Один $ - литерал, $$ - интерполяция
val tax = 10
val template = $$"Price: $100, Tax: $$tax"
println(template)  // Price: $100, Tax: 10
```

---

### Практические примеры

**JSON-шаблоны:**

```kotlin
fun createJsonRequest(userId: Int, action: String): String {
    return $$"""
    {
        "user_id": $$userId,
        "action": "$$action",
        "cost": "$50"
    }
    """
}

println(createJsonRequest(123, "purchase"))
// {
//     "user_id": 123,
//     "action": "purchase",
//     "cost": "$50"
// }
```

**SQL-запросы:**

```kotlin
fun buildQuery(tableName: String): String {
    // $ часто используется в SQL для переменных
    return $$"""
    SELECT * FROM $$tableName
    WHERE price > $100
    """
}
```

**Шаблоны для скриптов:**

```kotlin
fun generateBashScript(envVar: String, value: String): String {
    return $$"""
    #!/bin/bash
    export $HOME="/home/user"
    export $$envVar="$$value"
    echo "Done"
    """
}

println(generateBashScript("MY_VAR", "test"))
// #!/bin/bash
// export $HOME="/home/user"
// export MY_VAR="test"
// echo "Done"
```

---

### Уровни интерполяции

```kotlin
val x = 42

// 1 доллар - всё литерал
$"Value: $x"        // Value: $x

// 2 доллара - $$ для интерполяции
$$"Value: $$x"      // Value: 42
$$"Value: $x"       // Value: $x

// 3 доллара - $$$ для интерполяции
$$$"Value: $$$x"    // Value: 42
$$$"Value: $$x"     // Value: $$x
$$$"Value: $x"      // Value: $x
```

---

### Raw strings (тройные кавычки)

```kotlin
val name = "Kotlin"

// Обычная raw string
val normal = """
    Hello, $name!
    Price: ${'$'}100
"""

// Multi-dollar raw string
val better = $$"""
    Hello, $$name!
    Price: $100
"""

println(better)
// Hello, Kotlin!
// Price: $100
```

---

### Включение функции

Для Kotlin 2.1:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xmulti-dollar-interpolation")
    }
}
```

В Kotlin 2.2+ функция стабильна и флаг не нужен.

---

### Сравнение подходов

| Подход | Синтаксис | Читаемость |
|--------|-----------|------------|
| Escape | `"\$100"` | Сложно при многих $ |
| `${'$'}` | `"${'\$'}100"` | Громоздко |
| Multi-dollar | `$$"$100 = $$x"` | Чисто |

---

## Answer (EN)

**Introduced in Kotlin 2.1, stable since 2.2**

**Multi-dollar string interpolation** allows using multiple dollar signs (`$$`, `$$$`, etc.) to change the interpolation character. This simplifies working with strings containing literal dollars.

---

### Syntax

```kotlin
// Normal interpolation
val name = "World"
println("Hello, $name!")  // Hello, World!

// Multi-dollar interpolation
val price = 100
println($"Price: $price")           // Price: $price (literal)
println($$"Price: $$price")         // Price: 100 (interpolation)
println($$"Cost: $10, Total: $$price")  // Cost: $10, Total: 100
```

---

### Why It's Needed

**Problem with regular strings:**

```kotlin
// Need to escape every dollar
val template = "Price: \$100, Tax: \${tax}"
println(template)  // Price: $100, Tax: ${tax}

// In JSON
val json = """{"price": "\$100"}"""
```

**Solution with multi-dollar:**

```kotlin
// Single $ - literal, $$ - interpolation
val tax = 10
val template = $$"Price: $100, Tax: $$tax"
println(template)  // Price: $100, Tax: 10
```

---

### Practical Examples

**JSON Templates:**

```kotlin
fun createJsonRequest(userId: Int, action: String): String {
    return $$"""
    {
        "user_id": $$userId,
        "action": "$$action",
        "cost": "$50"
    }
    """
}

println(createJsonRequest(123, "purchase"))
// {
//     "user_id": 123,
//     "action": "purchase",
//     "cost": "$50"
// }
```

**SQL Queries:**

```kotlin
fun buildQuery(tableName: String): String {
    // $ is often used in SQL for variables
    return $$"""
    SELECT * FROM $$tableName
    WHERE price > $100
    """
}
```

**Script Templates:**

```kotlin
fun generateBashScript(envVar: String, value: String): String {
    return $$"""
    #!/bin/bash
    export $HOME="/home/user"
    export $$envVar="$$value"
    echo "Done"
    """
}

println(generateBashScript("MY_VAR", "test"))
// #!/bin/bash
// export $HOME="/home/user"
// export MY_VAR="test"
// echo "Done"
```

---

### Interpolation Levels

```kotlin
val x = 42

// 1 dollar - everything literal
$"Value: $x"        // Value: $x

// 2 dollars - $$ for interpolation
$$"Value: $$x"      // Value: 42
$$"Value: $x"       // Value: $x

// 3 dollars - $$$ for interpolation
$$$"Value: $$$x"    // Value: 42
$$$"Value: $$x"     // Value: $$x
$$$"Value: $x"      // Value: $x
```

---

### Raw Strings (Triple Quotes)

```kotlin
val name = "Kotlin"

// Normal raw string
val normal = """
    Hello, $name!
    Price: ${'$'}100
"""

// Multi-dollar raw string
val better = $$"""
    Hello, $$name!
    Price: $100
"""

println(better)
// Hello, Kotlin!
// Price: $100
```

---

### Enabling the Feature

For Kotlin 2.1:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xmulti-dollar-interpolation")
    }
}
```

In Kotlin 2.2+, the feature is stable and requires no flag.

---

### Approach Comparison

| Approach | Syntax | Readability |
|----------|--------|-------------|
| Escape | `"\$100"` | Hard with many $ |
| `${'$'}` | `"${'\$'}100"` | Verbose |
| Multi-dollar | `$$"$100 = $$x"` | Clean |

---

## Follow-ups

- Can you mix different interpolation levels in one file?
- How does multi-dollar work with nested expressions?
- What about IDE support for syntax highlighting?

## Related Questions

- [[q-kotlin-lambda-expressions--kotlin--medium]]

## References

- https://kotlinlang.org/docs/whatsnew21.html#multi-dollar-string-interpolation
- https://kotlinlang.org/docs/strings.html
