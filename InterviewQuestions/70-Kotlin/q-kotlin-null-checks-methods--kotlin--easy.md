---
anki_cards:
- slug: q-kotlin-null-checks-methods--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-null-checks-methods--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Question (EN)
> How to perform null checks?

## Ответ (RU)

Kotlin предлагает несколько операторов и функций для проверки на null:

### 1. Оператор Безопасного Вызова `?.`

Возвращает null если объект null, иначе получает свойство или вызывает метод:

```kotlin
val length: Int? = name?.length  // Возвращает null если name == null

val upper: String? = text?.uppercase()?.trim()  // Цепочка безопасных вызовов
```

### 2. Оператор Элвиса `?:`

Предоставляет значение по умолчанию если выражение null:

```kotlin
val length = name?.length ?: 0  // Возвращает 0 если name == null

val text = nullableText ?: "по умолчанию"

// Может выбрасывать исключение как "значение по умолчанию"
val nonNull = value ?: throw IllegalArgumentException("Значение обязательно")
```

### 3. Явная Проверка С `if`

Традиционная проверка на null с умным приведением типов:

```kotlin
if (name != null) {
    // Smart cast: name это String здесь, не String?
    println(name.length)
}

val length = if (name != null) name.length else 0
```

### 4. `requireNotNull()`

Выбрасывает исключение если аргумент равен null:

```kotlin
val nonNull: String = requireNotNull(nullable) {
    "Значение не может быть null"
}

requireNotNull(user) // Выбрасывает IllegalArgumentException если user == null
```

### 5. Двойной Восклицательный Знак `!!`

Принудительно утверждает, что значение не null; выбрасывает NPE если null:

```kotlin
val length: Int = name!!.length  // NPE если name == null

// Используйте осторожно, только когда на 100% уверены, что значение не null
```

### 6. `let` С Безопасным Вызовом

Выполняет блок только если значение не null:

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

Условное возвращение исходного значения или null:

```kotlin
val positiveNumber = number.takeIf { it > 0 }  // null если number <= 0

val validEmail = email.takeIf { it.contains("@") }
```

**Лучшие практики:**
- Предпочитайте безопасный вызов `?.` и Элвиса `?:` вместо `!!`.
- Используйте `!!` только когда вы абсолютно уверены, что значение не null.
- Используйте `requireNotNull()` для проверок предусловий.
- Комбинируйте операторы и функции для лаконичной и безопасной обработки null.

**Резюме**: Kotlin предоставляет набор операторов и функций для null-безопасности: безопасный вызов `?.`, оператор Элвиса `?:`, явная проверка `if (x != null)`, `requireNotNull()` для выброса исключений, `!!` для принудительного разворачивания (используйте осторожно), `let` для выполнения блоков на non-null значениях и `takeIf`/`takeUnless` для условной логики. Предпочитайте безопасные конструкции `?.` и `?:` для идиоматичного Kotlin-кода.

## Answer (EN)

Kotlin offers several operators and functions for null checking:

### 1. Safe Call Operator `?.`

Returns null if the receiver is null; otherwise accesses the property or calls the function:

```kotlin
val length: Int? = name?.length  // Returns null if name == null

val upper: String? = text?.uppercase()?.trim()  // Chain safe calls
```

### 2. Elvis Operator `?:`

`Provides` a default value if the expression is null:

```kotlin
val length = name?.length ?: 0  // Returns 0 if name == null

val text = nullableText ?: "default"

// Can throw exception as the "default" branch
val nonNull = value ?: throw IllegalArgumentException("Value required")
```

### 3. Explicit Check with `if`

Traditional null check with smart cast:

```kotlin
if (name != null) {
    // Smart cast: name is String here, not String?
    println(name.length)
}

val length = if (name != null) name.length else 0
```

### 4. `requireNotNull()`

Throws an exception if the argument is null:

```kotlin
val nonNull: String = requireNotNull(nullable) {
    "Value cannot be null"
}

requireNotNull(user) // Throws IllegalArgumentException if user == null
```

### 5. Double Bang `!!` Operator

Forces a non-null assertion; throws NPE if the value is null:

```kotlin
val length: Int = name!!.length  // NPE if name == null

// Use sparingly, only when 100% sure the value is not null
```

### 6. `let` With Safe Call

Executes the block only if the value is not null:

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

Conditionally returns the original value or null:

```kotlin
val positiveNumber = number.takeIf { it > 0 }  // null if number <= 0

val validEmail = email.takeIf { it.contains("@") }
```

**Best practices:**
- Prefer safe call `?.` and Elvis `?:` over `!!`.
- Use `!!` only when you're absolutely certain the value is not null.
- Use `requireNotNull()` for precondition checks.
- Combine operators and functions for concise and safe null handling.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия подхода к null-безопасности в Kotlin и Java?
- Когда вы бы использовали эти операторы и функции на практике?
- Каковы распространенные ошибки и подводные камни при работе с null в Kotlin?

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

## Связанные Вопросы (RU)

- [[q-catch-operator-flow--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]

## Related Questions

- [[q-catch-operator-flow--kotlin--medium]]
- [[q-coroutine-scope-basics--kotlin--easy]]
