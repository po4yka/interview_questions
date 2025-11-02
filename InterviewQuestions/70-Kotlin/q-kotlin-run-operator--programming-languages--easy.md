---
id: lang-017
title: "Kotlin Run Operator / Оператор run в Kotlin"
aliases: [Kotlin Run Operator, Оператор run в Kotlin]
topic: programming-languages
subtopics: [functional-programming, scope-functions]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-compose-side-effects-coroutines--kotlin--medium, q-kotlin-reified-types--kotlin--hard, q-kotlin-sealed-when-exhaustive--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [also, apply, difficulty/easy, let, programming-languages, run, scope-functions, with]
date created: Friday, October 31st 2025, 6:32:17 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Какой Оператор В Kotlin Исполняет Блок Кода И Возвращает Его Значение?

# Question (EN)
> Which operator in Kotlin executes a block of code and returns its value?

# Вопрос (RU)
> Какой оператор в Kotlin исполняет блок кода и возвращает его значение?

---

## Answer (EN)


The `run` function is a scope function that executes a block of code and returns the result. It's useful for executing multiple operations on an object.

### Basic Usage
```kotlin
val result = "Hello".run {
    println(length)  // Access properties via 'this'
    uppercase()       // Returns transformation
}
println(result)  // "HELLO"
```

### Common Patterns

**1. Object Configuration**
```kotlin
val person = Person().run {
    name = "Alice"
    age = 25
    address = "123 Main St"
    this  // Return configured object
}
```

**2. Null Safety**
```kotlin
val result = value?.run {
    transform()
} ?: defaultValue
```

**3. Scoped Computation**
```kotlin
val formatted = run {
    val first = getName()
    val last = getLastName()
    "$first $last"
}
```

**vs let, apply, also:**
- `run`: Has `this`, returns lambda result
- `let`: Has `it`, returns lambda result
- `apply`: Has `this`, returns receiver
- `also`: Has `it`, returns receiver

---
---

## Ответ (RU)


Функция `run` - это scope function которая выполняет блок кода и возвращает результат. Полезна для выполнения нескольких операций над объектом.

### Базовое Использование
```kotlin
val result = "Hello".run {
    println(length)  // Доступ к свойствам через 'this'
    uppercase()       // Возвращает трансформацию
}
println(result)  // "HELLO"
```

### Распространенные Паттерны

**1. Конфигурация объекта**
```kotlin
val person = Person().run {
    name = "Alice"
    age = 25
    address = "123 Main St"
    this  // Вернуть сконфигурированный объект
}
```

**2. Null безопасность**
```kotlin
val result = value?.run {
    transform()
} ?: defaultValue
```

**3. Вычисления в scope**
```kotlin
val formatted = run {
    val first = getName()
    val last = getLastName()
    "$first $last"
}
```

**vs let, apply, also:**
- `run`: Имеет `this`, возвращает результат лямбды
- `let`: Имеет `it`, возвращает результат лямбды
- `apply`: Имеет `this`, возвращает receiver
- `also`: Имеет `it`, возвращает receiver

---
---

## Варианты Использования Run

### 1. Object.run (Extension-функция)

```kotlin
data class User(var name: String, var age: Int)

val user = User("Alice", 25)

val greeting = user.run {
    // 'this' ссылается на user
    age += 1  // Изменяем user
    "Hello, $name! You are now $age years old."  // Возвращаемое значение
}

println(greeting)  // "Hello, Alice! You are now 26 years old."
println(user.age)  // 26 (изменен)
```

**Характеристики:**
- Контекстный объект: `this`
- Возвращает: Результат лямбды
- Применение: Трансформация объекта с возвратом результата

### 2. Run (Автономная функция)

```kotlin
val result = run {
    val x = 10
    val y = 20
    val z = x + y
    z * 2  // Возвращает 60
}

println(result)  // 60
```

**Характеристики:**
- Нет контекстного объекта
- Возвращает: Результат лямбды
- Применение: Выполнение блока с возвратом результата

---

## Сравнение С Другими Scope-функциями

| Функция | Ссылка на объект | Возвращаемое значение | Применение |
|---------|------------------|----------------------|------------|
| **run** | `this` | Результат лямбды | Трансформация и возврат |
| **let** | `it` | Результат лямбды | Проверка null, трансформация |
| **apply** | `this` | Контекстный объект | Конфигурация объекта |
| **also** | `it` | Контекстный объект | Побочные эффекты |
| **with** | `this` | Результат лямбды | Множественные вызовы на объекте |

---

## Примеры Использования Run

### 1. Вычисление И Возврат Результата

```kotlin
val result = user.run {
    val fullName = "$firstName $lastName"
    val age = calculateAge(birthDate)
    "$fullName ($age years old)"  // Возвращается
}
```

### 2. Null-безопасность С Run

```kotlin
val length = str?.run {
    trim()
    uppercase()
    length  // Возвращается, если str не null
} ?: 0  // Значение по умолчанию, если str null
```

### 3. Инициализация И Конфигурация

```kotlin
val db = Database().run {
    connect()
    migrate()
    this  // Возвращаем сконфигурированную БД
}
```

### 4. Сложные Вычисления

```kotlin
val price = product.run {
    val basePrice = this.basePrice
    val discount = this.discount
    val tax = (basePrice - discount) * 0.2
    basePrice - discount + tax  // Финальная цена
}
```

---

## Run Vs Другие Scope-функции

### Run Vs Let

```kotlin
// run - использует 'this'
val result1 = user.run {
    println(name)  // Прямой доступ
    age
}

// let - использует 'it'
val result2 = user.let {
    println(it.name)  // Нужно использовать 'it'
    it.age
}
```

**Используйте `run` когда:**
- Нужен `this` вместо `it`
- Множественный доступ к свойствам без повторения `it`

**Используйте `let` когда:**
- Null-безопасность с `?.let`
- Нужно явное имя параметра

### Run Vs Apply

```kotlin
// run - возвращает результат лямбды
val length = StringBuilder().run {
    append("Hello")
    append(" World")
    length  // Возвращает Int (длину)
}

// apply - возвращает сам объект
val builder = StringBuilder().apply {
    append("Hello")
    append(" World")
}  // Возвращает StringBuilder
```

**Используйте `run` когда:**
- Нужно вернуть вычисленное значение

**Используйте `apply` когда:**
- Нужно вернуть сконфигурированный объект

### Run Vs with

```kotlin
// run - extension-функция
val result1 = user.run {
    "$name is $age years old"
}

// with - обычная функция
val result2 = with(user) {
    "$name is $age years old"
}
```

**Используйте `run` когда:**
- Объект может быть null (`user?.run`)
- Цепочка операций

**Используйте `with` когда:**
- Объект точно не null
- Предпочитаете синтаксис вызова функции

---

## Практические Примеры

### Пример 1: Запрос К Базе Данных

```kotlin
val users = database.run {
    connect()
    val query = "SELECT * FROM users WHERE active = true"
    executeQuery(query)
    mapToUsers(resultSet)  // Возвращается
}
```

### Пример 2: Конфигурация

```kotlin
val config = Config().run {
    setHost("localhost")
    setPort(8080)
    setTimeout(30)
    validate()  // Возвращает Boolean
}

if (config) {
    startServer()
}
```

### Пример 3: Null-безопасность

```kotlin
val userInfo = user?.run {
    "Name: $name\nAge: $age\nEmail: $email"
} ?: "User not found"
```

### Пример 4: Множественные Трансформации

```kotlin
val processed = data
    .filter { it.isValid }
    .run {
        // 'this' - отфильтрованный список
        if (isEmpty()) {
            emptyList()
        } else {
            map { it.process() }
        }
    }
```

### Пример 5: Управление Ресурсами

```kotlin
val content = File("data.txt").run {
    if (exists()) {
        readText()
    } else {
        createNewFile()
        ""
    }
}
```

---

## Распространенные Паттерны

### Паттерн 1: Ограниченные Вычисления

```kotlin
val result = run {
    val a = computeA()
    val b = computeB()
    val c = computeC()
    a + b + c  // Переменные в области видимости, возврат суммы
}
```

### Паттерн 2: Условные Операции

```kotlin
val value = obj.run {
    when (type) {
        Type.A -> processAsA()
        Type.B -> processAsB()
        else -> processDefault()
    }
}
```

### Паттерн 3: Паттерн Builder

```kotlin
val request = HttpRequest().run {
    url = "https://api.example.com"
    method = "POST"
    headers["Content-Type"] = "application/json"
    body = jsonBody
    build()  // Возвращает собранный запрос
}
```

---

## Когда Использовать Run

- **Используйте `run` когда:**
- Нужно выполнить блок и вернуть результат
- Работаете с контекстом `this` (а не `it`)
- Выполняете трансформации
- Null-безопасность с `?.run`
- Ограничиваете область видимости промежуточных переменных

- **Избегайте `run` когда:**
- Хотите вернуть сам объект (используйте `apply`)
- Нужен явный параметр (используйте `let`)
- Трансформация не нужна (используйте `also` для побочных эффектов)

---

## Резюме

**Оператор `run`:**
- Исполняет лямбда-блок
- Возвращает **результат лямбды** (последнее выражение)
- Контекстный объект доступен как `this`
- Может вызываться как extension (`obj.run`) или автономно (`run`)

**Ключевые характеристики:**
- Ссылка на объект: `this`
- Возвращаемое значение: Результат лямбды
- Null-безопасность: Да (`?.run`)

**Основные сценарии применения:**
- Вычисление и возврат значения
- Трансформация объекта
- Ограниченные вычисления
- Цепочки с null-безопасностью

**Сравнение:**
- `run`: Возвращает результат, использует `this`
- `let`: Возвращает результат, использует `it`
- `apply`: Возвращает объект, использует `this`
- `also`: Возвращает объект, использует `it`
- `with`: Возвращает результат, использует `this` (не extension)

## Related Questions

- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]]
- [[q-compose-side-effects-coroutines--kotlin--medium]]
- [[q-kotlin-reified-types--kotlin--hard]]
