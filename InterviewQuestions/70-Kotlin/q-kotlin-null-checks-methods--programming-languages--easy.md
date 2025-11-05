---
id: lang-058
title: "Kotlin Null Checks Methods / Методы проверки на null в Kotlin"
aliases: [Kotlin Null Checks Methods, Методы проверки на null в Kotlin]
topic: programming-languages
subtopics: [null-safety, operators]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-catch-operator-flow--kotlin--medium, q-coroutine-scope-basics--kotlin--easy]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/easy, elvis, null-checks, null-safety, operators, programming-languages, safe-call]
date created: Friday, October 31st 2025, 6:30:56 pm
date modified: Saturday, November 1st 2025, 5:43:25 pm
---
# Каким Образом Осуществлять Проверки На Null?

# Вопрос (RU)
> Каким образом осуществлять проверки на null?

---

# Question (EN)
> How to perform null checks?

## Ответ (RU)

Kotlin предлагает несколько операторов и методов для проверки на null:

### 1. Оператор Безопасного Вызова `?.`

Возвращает null если объект null, иначе вызывает метод/свойство:

```kotlin
val length: Int? = name?.length  // Возвращает null если name null

val upper: String? = text?.uppercase()?.trim()  // Цепочка безопасных вызовов
```

### 2. Оператор Элвиса `?:`

Предоставляет значение по умолчанию если выражение null:

```kotlin
val length = name?.length ?: 0  // Возвращает 0 если name null

val text = nullableText ?: "по умолчанию"

// Может выбрасывать исключение как значение по умолчанию
val nonNull = value ?: throw IllegalArgumentException("Значение обязательно")
```

### 3. Явная Проверка С `if`

Традиционная проверка на null:

```kotlin
if (name != null) {
    // Smart cast: name это String здесь, не String?
    println(name.length)
}

val length = if (name != null) name.length else 0
```

### 4. `requireNotNull()`

Выбрасывает исключение если null:

```kotlin
val nonNull: String = requireNotNull(nullable) {
    "Значение не может быть null"
}

requireNotNull(user) // Выбрасывает IllegalArgumentException если null
```

### 5. Двойной Восклицательный Знак `!!`

Гарантирует не-null, выбрасывает NPE если null:

```kotlin
val length: Int = name!!.length  // NPE если name null

// Используйте осторожно, только когда на 100% уверены что значение не null
```

### 6. `let` С Безопасным Вызовом

Выполняет блок только если не null:

```kotlin
name?.let {
    // 'it' это non-null String здесь
    println("Имя: $it")
}

// С кастомным именем параметра
user?.let { u ->
    println("Пользователь: ${u.name}")
}
```

### 7. `takeIf` / `takeUnless`

Условное возвращение:

```kotlin
val positiveNumber = number.takeIf { it > 0 }  // null если <= 0

val validEmail = email.takeIf { it.contains("@") }
```

**Лучшие практики:**
- Предпочитайте безопасный вызов `?.` и Элвиса `?:` вместо `!!`
- Используйте `!!` только когда вы абсолютно уверены что значение не null
- Используйте `requireNotNull()` для проверок предусловий
- Комбинируйте операторы для лаконичной обработки null

**Резюме**: Kotlin предоставляет богатый набор операторов для null-безопасности: безопасный вызов `?.`, оператор Элвиса `?:`, явная проверка `if (x != null)`, `requireNotNull()` для выброса исключений, `!!` для принудительного разворачивания (используйте осторожно), `let` для выполнения блоков на non-null значениях, и `takeIf`/`takeUnless` для условной логики. Предпочитайте безопасные операторы `?.` и `?:` для идиоматичного Kotlin кода.

## Answer (EN)

Kotlin offers several operators and methods for null checking:

### 1. Safe Call Operator `?.`

Returns null if object is null, otherwise calls the method/property:

```kotlin
val length: Int? = name?.length  // Returns null if name is null

val upper: String? = text?.uppercase()?.trim()  // Chain safe calls
```

### 2. Elvis Operator `?:`

Provides default value if expression is null:

```kotlin
val length = name?.length ?: 0  // Returns 0 if name is null

val text = nullableText ?: "default"

// Can throw exception as default
val nonNull = value ?: throw IllegalArgumentException("Value required")
```

### 3. Explicit Check with `if`

Traditional null check:

```kotlin
if (name != null) {
    // Smart cast: name is String here, not String?
    println(name.length)
}

val length = if (name != null) name.length else 0
```

### 4. `requireNotNull()`

Throws exception if null:

```kotlin
val nonNull: String = requireNotNull(nullable) {
    "Value cannot be null"
}

requireNotNull(user) // Throws IllegalArgumentException if null
```

### 5. Double Bang `!!` Operator

Guarantees not-null, throws NPE if null:

```kotlin
val length: Int = name!!.length  // NPE if name is null

// Use sparingly, only when 100% sure value is not null
```

### 6. `let` With Safe Call

Execute block only if not null:

```kotlin
name?.let {
    // 'it' is non-null String here
    println("Name is: $it")
}

// With custom parameter name
user?.let { u ->
    println("User: ${u.name}")
}
```

### 7. `takeIf` / `takeUnless`

Conditional return:

```kotlin
val positiveNumber = number.takeIf { it > 0 }  // null if <= 0

val validEmail = email.takeIf { it.contains("@") }
```

**Best practices:**
- Prefer safe call `?.` and Elvis `?:` over `!!`
- Use `!!` only when you're absolutely certain value is not null
- Use `requireNotNull()` for precondition checks
- Combine operators for concise null handling

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-catch-operator-flow--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
