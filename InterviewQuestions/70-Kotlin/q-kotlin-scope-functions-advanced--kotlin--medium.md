---
id: "20251015082236029"
title: "Kotlin Scope Functions Advanced"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags: - kotlin
  - scope-functions
  - let
  - run
  - apply
  - with
  - also
---
# Advanced Scope Functions Usage

**English**: Compare let, run, with, apply, also. When should you use each? Explain return values and context objects.

**Russian**: Сравните let, run, with, apply, also. Когда использовать каждый? Объясните return values и context objects.

## Answer (EN)

Kotlin's scope functions (let, run, with, apply, also) execute code blocks within object context. Choosing the right one depends on context access and return value needs.

### Quick Reference Table

| Function | Context | Returns | Use Case |
|----------|---------|---------|----------|
| **let** | it (argument) | Lambda result | Transform object, null safety |
| **run** | this (receiver) | Lambda result | Object config + compute result |
| **with** | this (receiver) | Lambda result | Group calls on object |
| **apply** | this (receiver) | Context object | Object configuration |
| **also** | it (argument) | Context object | Additional effects, logging |

### let - Transform and Null Safety

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

### run - Initialize and Compute

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

### with - Group Operations

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

### apply - Object Configuration

```kotlin
// Builder pattern
val intent = Intent(context, Activity::class.java).apply {
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

### also - Side Effects

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

// Reference rather than properties
class Builder {
    private val items = mutableListOf<String>()

    fun add(item: String) = also {
        items.add(item)  // Refers to Builder, not items
    }
}
```

### Decision Tree

```
Need to operate on object?

 Want to return the object itself?
   Need object as receiver (this)?
     Use APPLY (configuration)
   Need object as argument (it)?
      Use ALSO (side effects, logging)

 Want to return different result?
    Have object to operate on?
      As receiver (this)?
        Use RUN (init + compute)
      As argument (it)?
         Use LET (transform, null safety)
   
    Object from outside scope?
       Use WITH (group calls)
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
val dialog = AlertDialog.Builder(context).apply {
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

**1. Using wrong context type**:
```kotlin
// WRONG
"text".apply {
    toUpperCase()  // Result ignored
}

// CORRECT
"text".let {
    it.toUpperCase()  // Result used
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

1. **let** for null safety and transformations
2. **run** when initialization + result needed
3. **with** for grouping calls on external object
4. **apply** for object configuration
5. **also** for side effects and logging
6. Avoid deep nesting
7. Use meaningful names instead of `it` when clarity needed
8. Prefer `let` over `run` for nullable receivers
9. Don't overuse - sometimes simple code is better

## Ответ (RU)

Scope-функции Kotlin (let, run, with, apply, also) выполняют блоки кода в контексте объекта. Выбор правильной функции зависит от способа доступа к контексту и требуемого возвращаемого значения.

### Быстрая справка

| Функция | Контекст | Возвращает | Случай использования |
|----------|---------|---------|----------|
| **let** | it (аргумент) | Результат лямбды | Трансформация объекта, null safety |
| **run** | this (receiver) | Результат лямбды | Конфигурация объекта + вычисление результата |
| **with** | this (receiver) | Результат лямбды | Группировка вызовов на объекте |
| **apply** | this (receiver) | Объект контекста | Конфигурация объекта |
| **also** | it (аргумент) | Объект контекста | Дополнительные эффекты, логирование |

### let - Трансформация и Null Safety

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

### run - Инициализация и Вычисление

```kotlin
// Инициализация объекта + вычисление
val result = service.run {
    connect()
    authenticate()
    fetchData()
}

// Блок выражения
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

### with - Группировка Операций

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

### apply - Конфигурация Объекта

```kotlin
// Паттерн Builder
val intent = Intent(context, Activity::class.java).apply {
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

// Множественные apply в цепочке
textView.apply {
    text = "Hello"
    textSize = 16f
}.apply {
    setTextColor(Color.BLACK)
    gravity = Gravity.CENTER
}
```

### also - Побочные Эффекты

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
        items.add(item)  // Ссылается на Builder, а не на items
    }
}
```

### Дерево Решений

```
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

    Объект из внешней области видимости?
       Используйте WITH (группировка вызовов)
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
val dialog = AlertDialog.Builder(context).apply {
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

**1. Использование неправильного типа контекста**:
```kotlin
// НЕПРАВИЛЬНО
"text".apply {
    toUpperCase()  // Результат игнорируется
}

// ПРАВИЛЬНО
"text".let {
    it.toUpperCase()  // Результат используется
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

1. **let** для null safety и трансформаций
2. **run** когда нужна инициализация + результат
3. **with** для группировки вызовов на внешнем объекте
4. **apply** для конфигурации объекта
5. **also** для побочных эффектов и логирования
6. Избегайте глубокой вложенности
7. Используйте осмысленные имена вместо `it` когда нужна ясность
8. Предпочитайте `let` вместо `run` для nullable receivers
9. Не злоупотребляйте - иногда простой код лучше
