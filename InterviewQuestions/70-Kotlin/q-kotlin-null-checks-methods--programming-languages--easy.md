---
id: "20251015082237171"
title: "Kotlin Null Checks Methods / Методы проверки на null в Kotlin"
topic: computer-science
difficulty: easy
status: draft
created: 2025-10-15
tags: - elvis
  - kotlin
  - null-checks
  - null-safety
  - operators
  - programming-languages
  - safe-call
---
# Каким образом осуществлять проверки на null?

# Question (EN)
> How to perform null checks?

# Вопрос (RU)
> Каким образом осуществлять проверки на null?

---

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

### 6. `let` with Safe Call

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

## Ответ (RU)

Kotlin предлагает несколько операторов и методов для проверки на null:

### 1. Оператор безопасного вызова `?.`

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

### 3. Явная проверка с `if`

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

### 5. Двойной восклицательный знак `!!`

Гарантирует не-null, выбрасывает NPE если null:

```kotlin
val length: Int = name!!.length  // NPE если name null

// Используйте осторожно, только когда на 100% уверены что значение не null
```

### 6. `let` с безопасным вызовом

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

