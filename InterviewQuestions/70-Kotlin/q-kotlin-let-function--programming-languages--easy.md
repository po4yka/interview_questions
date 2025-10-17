---
id: 20251012-154375
title: "Kotlin Let Function / Функция let в Kotlin"
topic: kotlin
difficulty: easy
status: draft
created: 2025-10-15
tags: - kotlin
  - let
  - null-safety
  - programming-languages
  - scope-functions
---
# Для чего нужен let?

# Question (EN)
> What is the `let` function used for in Kotlin?

# Вопрос (RU)
> Для чего нужна функция `let` в Kotlin?

---

## Answer (EN)

`let` is one of several scope functions in Kotlin standard library that provide more convenient value management, especially when working with potentially null values.

**Main purposes:**

1. **Handling nullable values**: Safe work with variables that may be null
```kotlin
nullable?.let {
    // This block executes only if nullable is not null
    println(it.length)
}
```

2. **Reducing scope**: Limiting variable scope to temporary values
```kotlin
val result = computeValue().let { value ->
    // Use value only in this scope
    transformValue(value)
}
```

3. **Call chaining**: Creating method call chains
```kotlin
value
    .let { it.trim() }
    .let { it.uppercase() }
    .let { println(it) }
```

`let` receives the object as `it` parameter and returns the result of lambda.

---

## Ответ (RU)

`let` — это одна из scope-функций в стандартной библиотеке Kotlin, которая обеспечивает более удобное управление значениями, особенно при работе с потенциально null значениями.

**Основные применения:**

1. **Обработка nullable значений**: Безопасная работа с переменными, которые могут быть null
```kotlin
nullable?.let {
    // Этот блок выполняется только если nullable не null
    println(it.length)
}
```

2. **Сокращение области видимости**: Ограничение области видимости переменной временными значениями
```kotlin
val result = computeValue().let { value ->
    // Используем value только в этой области
    transformValue(value)
}
```

3. **Цепочки вызовов**: Создание цепочек вызовов методов
```kotlin
value
    .let { it.trim() }
    .let { it.uppercase() }
    .let { println(it) }
```

**Ключевые особенности:**
- `let` получает объект как параметр `it`
- Возвращает результат лямбды
- Особенно полезна с оператором безопасного вызова `?.let`
- Помогает избежать многократных проверок на null

**Пример:**
```kotlin
// Без let
if (user != null) {
    val name = user.name
    println(name)
}

// С let
user?.let {
    println(it.name)
}
```
