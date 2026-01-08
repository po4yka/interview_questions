---\
id: kotlin-167
title: "Kotlin Scope Functions Advanced / Продвинутые Scope Functions в Kotlin"
aliases: [Kotlin Scope Functions Advanced, Продвинутые Scope Functions в Kotlin]
topic: kotlin
subtopics: [scope-functions]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-flow-performance--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [also, apply, difficulty/medium, kotlin, let, run, scope-functions, with]
---\
# Вопрос (RU)

> Сравните `let`, `run`, `with`, `apply`, `also`. Когда использовать каждый? Объясните return values и context objects.

# Question (EN)

> Compare `let`, `run`, `with`, `apply`, `also`. When should you use each? Explain return values and context objects.

## Ответ (RU)

Scope-функции Kotlin (`let`, `run`, `with`, `apply`, `also`) выполняют блоки кода в контексте объекта. Выбор правильной функции зависит от того, как вы хотите обращаться к контекстному объекту и какое значение нужно получить в результате.

### Быстрая Справка

| Функция | Контекст | Возвращает | Случай использования |
|----------|---------|---------|----------|
| **let** | it (аргумент) | Результат лямбды | Трансформация объекта, null safety |
| **run** | this (receiver) | Результат лямбды | Конфигурация объекта + вычисление результата |
| **with** | this (receiver) | Результат лямбды | Группировка вызовов на существующем объекте |
| **apply** | this (receiver) | Объект контекста | Конфигурация объекта |
| **also** | it (аргумент) | Объект контекста | Дополнительные эффекты, логирование |

### Let - Трансформация И Null Safety

```kotlin
// Null safety
val name: String? = getNullableName()
name?.let {
    println("Name: $it")
    sendEmail(it)
}

// Трансформация результата
val result = getUserId()
    .let { loadUser(it) }
    .let { formatUser(it) }

// Введение локальной переменной
val data = complexCalculation().let { result ->
    println("Result: $result")
    validateResult(result)
    result.transform()
}

// Избежание конфликтов имён
fun process() {
    val value = "outer"
    getValue()?.let { value ->  // Другая переменная
        println(value)  // Внутренняя value
    }
}
```

### Run - Инициализация И Вычисление

```kotlin
// Инициализация объекта + вычисление результата
val result = service.run {
    connect()
    authenticate()
    fetchData()
}

// Блок-выражение
val regex = run {
    val digits = "0-9"
    val letters = "a-zA-Z"
    Regex("[$digits$letters]+")
}

// Ограничение области видимости
run {
    val temp = expensiveCalculation()
    processResult(temp)
    // temp недоступна снаружи
}

// Extension vs non-extension
"text".run {
    println(this)  // Extension: "text" как receiver
}

run {
    println("block")  // Non-extension: нет receiver
}
```

### With - Группировка Операций

```kotlin
// Группировка вызовов без extension
val result = with(stringBuilder) {
    append("Hello")
    append(" ")
    append("World")
    toString()
}

// Конфигурация и возврат результата
val formatted = with(user) {
    "Name: $name, Email: $email, Age: $age"
}

// Вычисления с вспомогательным объектом
with(canvas) {
    drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    drawCircle(centerX, centerY, radius, paint)
}
```

### Apply - Конфигурация Объекта

```kotlin
// Паттерн Builder
val intent = Intent(`Context`, Activity::class.java).apply {
    putExtra("key", "value")
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
    action = Intent.ACTION_VIEW
}

// Цепочка конфигурации
val user = User().apply {
    name = "John"
    email = "john@example.com"
    age = 30
}.also {
    save(it)
}

// Несколько apply в цепочке
textView.apply {
    text = "Hello"
    textSize = 16f
}.apply {
    setTextColor(Color.BLACK)
    gravity = Gravity.CENTER
}
```

### Also - Побочные Эффекты

```kotlin
// Логирование
val numbers = mutableListOf(1, 2, 3)
    .also { println("Initial list: $it") }
    .apply { add(4) }
    .also { println("After adding: $it") }

// Валидация
fun createUser(name: String) = User(name)
    .also { validateUser(it) }
    .also { logCreation(it) }

// Ссылка на объект, а не на свойства
class Builder {
    private val items = mutableListOf<String>()

    fun add(item: String) = also {
        items.add(item)  // Ссылается на Builder как на receiver, а не на локальную переменную 'items'
    }
}
```

### Дерево Решений

```text
Нужно работать с объектом?

 Хотите вернуть сам объект?
   Нужен объект как receiver (this)?
     Используйте APPLY (конфигурация)
   Нужен объект как аргумент (it)?
      Используйте ALSO (побочные эффекты, логирование)

 Хотите вернуть другой результат?
    Есть объект для работы?
      Как receiver (this)?
        Используйте RUN (инициализация + вычисление)
      Как аргумент (it)?
         Используйте LET (трансформация, null safety)

    Объект приходит из внешней области видимости?
       Используйте WITH (группировка вызовов на нём)
```

### Распространённые Паттерны

**Безопасные вызовы с let**:
```kotlin
user?.let {
    updateUI(it.name)
    saveToDatabase(it)
}
```

**Конфигурация с apply**:
```kotlin
val dialog = AlertDialog.Builder(`Context`).apply {
    setTitle("Title")
    setMessage("Message")
    setPositiveButton("OK") { _, _ -> }
}.create()
```

**Логирование с also**:
```kotlin
repository.getUser(id)
    .also { Log.d("TAG", "User loaded: $it") }
    .let { user -> updateUI(user) }
```

**Сложная инициализация с run**:
```kotlin
val config = Config().run {
    loadSettings()
    applyDefaults()
    validate()
    this
}
```

### Распространённые Ошибки

**1. Неправильный выбор функции относительно результата**:
```kotlin
// НЕУДАЧНЫЙ ВЫБОР apply: вам важен результат лямбды, но apply возвращает receiver
"text".apply {
    uppercase()  // Результат игнорируется, всё выражение возвращает "text"
}

// ЛУЧШЕ: используйте let (или run), когда нужен результат лямбды
val upper = "text".let {
    it.uppercase()
}
```

**2. Ненужная вложенность**:
```kotlin
// НЕПРАВИЛЬНО
user?.let {
    it.email?.let { email ->
        sendEmail(email)
    }
}

// ПРАВИЛЬНО
user?.email?.let { email ->
    sendEmail(email)
}
```

### Лучшие Практики

1. **let** для null safety и трансформаций.
2. **run** когда нужна инициализация + вычисление результата.
3. **with** для группировки вызовов на уже существующем объекте.
4. **apply** для конфигурации объекта и возврата самого объекта.
5. **also** для побочных эффектов и логирования при сохранении объекта.
6. Избегайте глубокой вложенности scope-функций.
7. Используйте осмысленные имена вместо `it`, когда это повышает читаемость.
8. Предпочитайте (по соглашению) `let` вместо `run` для nullable receiver'ов, когда важно явно подчеркнуть обработку null; это рекомендация стиля, а не жёсткое правило.
9. Не злоупотребляйте scope-функциями — простой прямой код часто лучше.

## Answer (EN)

Kotlin's scope functions (`let`, `run`, `with`, `apply`, `also`) execute code blocks within an object context. Choosing the right one depends on how you want to access the context object and what value you need as the result.

### Quick Reference Table

| Function | `Context` | Returns | Use Case |
|----------|---------|---------|----------|
| **let** | it (argument) | Lambda result | Transform object, null safety |
| **run** | this (receiver) | Lambda result | Object config + compute result |
| **with** | this (receiver) | Lambda result | Group calls on existing object |
| **apply** | this (receiver) | `Context` object | Object configuration |
| **also** | it (argument) | `Context` object | Additional effects, logging |

### Let - Transform and Null Safety

```kotlin
// Null safety
val name: String? = getNullableName()
name?.let {
    println("Name: $it")
    sendEmail(it)
}

// Transform result
val result = getUserId()
    .let { loadUser(it) }
    .let { formatUser(it) }

// Introduce local variable
val data = complexCalculation().let { result ->
    println("Result: $result")
    validateResult(result)
    result.transform()
}

// Avoid naming conflicts
fun process() {
    val value = "outer"
    getValue()?.let { value ->  // Different variable
        println(value)  // Inner value
    }
}
```

### Run - Initialize and Compute

```kotlin
// Object init + computation
val result = service.run {
    connect()
    authenticate()
    fetchData()
}

// Expression block
val regex = run {
    val digits = "0-9"
    val letters = "a-zA-Z"
    Regex("[$digits$letters]+")
}

// Scope limitation
run {
    val temp = expensiveCalculation()
    processResult(temp)
    // temp not accessible outside
}

// Extension vs non-extension
"text".run {
    println(this)  // Extension: "text" as receiver
}

run {
    println("block")  // Non-extension: no receiver
}
```

### With - Group Operations

```kotlin
// Group calls without extension
val result = with(stringBuilder) {
    append("Hello")
    append(" ")
    append("World")
    toString()
}

// Configure and return result
val formatted = with(user) {
    "Name: $name, Email: $email, Age: $age"
}

// Helper object computation
with(canvas) {
    drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
    drawCircle(centerX, centerY, radius, paint)
}
```

### Apply - Object Configuration

```kotlin
// Builder pattern
val intent = Intent(`Context`, Activity::class.java).apply {
    putExtra("key", "value")
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
    action = Intent.ACTION_VIEW
}

// Chain configuration
val user = User().apply {
    name = "John"
    email = "john@example.com"
    age = 30
}.also {
    save(it)
}

// Multiple apply in chain
textView.apply {
    text = "Hello"
    textSize = 16f
}.apply {
    setTextColor(Color.BLACK)
    gravity = Gravity.CENTER
}
```

### Also - Side Effects

```kotlin
// Logging
val numbers = mutableListOf(1, 2, 3)
    .also { println("Initial list: $it") }
    .apply { add(4) }
    .also { println("After adding: $it") }

// Validation
fun createUser(name: String) = User(name)
    .also { validateUser(it) }
    .also { logCreation(it) }

// Reference to the receiver object rather than its properties
class Builder {
    private val items = mutableListOf<String>()

    fun add(item: String) = also {
        items.add(item)  // Refers to Builder as receiver, not to a local 'items' variable
    }
}
```

### Decision Tree

```text
Need to operate on an object?

 Want to return the object itself?
   Need object as receiver (this)?
     Use APPLY (configuration)
   Need object as argument (it)?
      Use ALSO (side effects, logging)

 Want to return a different result?
    Have an object to operate on?
      As receiver (this)?
        Use RUN (init + compute)
      As argument (it)?
         Use LET (transform, null safety)

    Object comes from outside scope?
       Use WITH (group calls on it)
```

### Common Patterns

**Safe calls with let**:
```kotlin
user?.let {
    updateUI(it.name)
    saveToDatabase(it)
}
```

**Configuration with apply**:
```kotlin
val dialog = AlertDialog.Builder(`Context`).apply {
    setTitle("Title")
    setMessage("Message")
    setPositiveButton("OK") { _, _ -> }
}.create()
```

**Logging with also**:
```kotlin
repository.getUser(id)
    .also { Log.d("TAG", "User loaded: $it") }
    .let { user -> updateUI(user) }
```

**Complex initialization with run**:
```kotlin
val config = Config().run {
    loadSettings()
    applyDefaults()
    validate()
    this
}
```

### Common Mistakes

**1. Misusing context and return values**:
```kotlin
// MISUSING apply: you care about the lambda result, but apply returns the receiver
"text".apply {
    uppercase()  // Result ignored, the whole expression is still "text"
}

// BETTER: use let (or run) when you need the lambda result
val upper = "text".let {
    it.uppercase()
}
```

**2. Unnecessary nesting**:
```kotlin
// WRONG
user?.let {
    it.email?.let { email ->
        sendEmail(email)
    }
}

// CORRECT
user?.email?.let { email ->
    sendEmail(email)
}
```

### Best Practices

1. **let** for null safety and transformations.
2. **run** when you need initialization + a computed result.
3. **with** for grouping multiple calls on an existing object.
4. **apply** for configuring and returning the receiver.
5. **also** for side effects and logging while returning the receiver.
6. Avoid deep nesting of scope functions.
7. Use meaningful names instead of `it` when clarity is needed.
8. Prefer `let` (by convention) over `run` for nullable receivers when you want to make null-handling explicit; it's a style guideline, not a strict rule.
9. Don't overuse scope functions—simple, direct code is often clearer.

## Дополнительные Вопросы (RU)

- В чём ключевые отличия подхода с scope-функциями в Kotlin от Java-кода без них?
- Когда вы будете использовать эти функции на практике?
- Какие типичные ошибки при использовании scope-функций нужно избегать?

## Follow-ups

- What are the key differences between using scope functions in Kotlin and typical Java-style code?
- When would you use these functions in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [[c-kotlin]]
- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-flow-performance--kotlin--hard]]
- [[q-kotlin-null-safety--kotlin--medium]]
- [[q-kotlin-sam-conversions--kotlin--medium]]

## Related Questions

- [[q-flow-performance--kotlin--hard]]
- [[q-kotlin-null-safety--kotlin--medium]]
- [[q-kotlin-sam-conversions--kotlin--medium]]
