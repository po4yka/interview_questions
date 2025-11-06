---
id: cs-001
title: "Clean Code Principles / Принципы чистого кода"
aliases: ["Clean Code Principles", "Принципы чистого кода"]
topic: cs
subtopics: [best-practices, clean-code, code-quality, software-engineering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-clean-code]
created: 2025-10-12
updated: 2025-01-25
tags: [best-practices, clean-code, code-quality, difficulty/medium, refactoring]
sources: [https://en.wikipedia.org/wiki/Clean_code]
---

# Вопрос (RU)
> Что такое принципы чистого кода? Как писать осмысленные имена, хорошие функции и понятные комментарии? Что такое code smells и как их рефакторить?

# Question (EN)
> What are clean code principles? How do you write meaningful names, good functions, and clear comments? What are code smells and how to refactor them?

---

## Ответ (RU)

**Теория чистого кода:**
Clean Code - код, который легко понять, поддерживать и расширять. Основан на принципах Robert C. Martin (Uncle Bob). Чистый код читается как хорошо написанная проза, минимизирует когнитивную нагрузку и делает намерения программиста явными.

**1. Осмысленные имена:**

*Теория:* Имена должны раскрывать намерение, быть произносимыми и искомыми. Имена классов - существительные, методов - глаголы. Избегайте дезинформации и магических чисел.

*Принципы:*
- Раскрывают намерение (intention-revealing)
- Произносимы (pronounceable)
- Искомы (searchable)
- Классы = существительные, методы = глаголы
- Избегайте дезинформации

```kotlin
// ❌ Плохо: непонятное намерение
val d = 5
val list1 = listOf<Account>()

// ✅ Хорошо: ясное намерение
val elapsedTimeInDays = 5
val activeAccounts = listOf<Account>()

// ❌ Плохо: непроизносимо
data class DtaRcrd102(val genymdhms: Long)

// ✅ Хорошо: произносимо
data class Customer(val generationTimestamp: Long)

// ✅ Классы = существительные, методы = глаголы
class UserRepository {
    fun findById(id: Long): User
    fun save(user: User)
    fun delete(id: Long)
}
```

**2. Функции:**

*Теория:* Функции должны быть маленькими (< 20 строк), делать одно дело, иметь мало аргументов (0-2 идеально, избегайте 3+). Без побочных эффектов. Разделение команд (изменяют состояние) и запросов (возвращают данные).

*Принципы:*
- Маленькие (< 20 строк)
- Делают одно дело (Single Responsibility)
- Мало аргументов (0-2 идеально)
- Без побочных эффектов
- Command-Query Separation

```kotlin
// ❌ Плохо: делает много, длинная, много аргументов
fun processUserData(name: String, email: String, age: Int, address: String, phone: String) {
    validateEmail(email)
    saveToDatabase(name, email, age)
    sendWelcomeEmail(email)
    logActivity(name)
}

// ✅ Хорошо: маленькие функции, одно дело
fun registerUser(user: User) {
    validateUser(user)
    saveUser(user)
    notifyUser(user)
}

fun validateUser(user: User) {
    require(user.email.isValidEmail()) { "Invalid email" }
}

fun saveUser(user: User) {
    userRepository.save(user)
}

// ✅ Command-Query Separation
fun getUser(id: Long): User  // Query - только читает
fun updateUser(user: User)   // Command - только изменяет
```

**3. Комментарии:**

*Теория:* Объясняйте "почему", не "что". Код должен быть самодокументируемым. Комментарии для TODO/FIXME/WARNING. Избегайте избыточных комментариев. Не комментируйте плохой код - перепишите его.

*Принципы:*
- Объясняйте "почему", не "что"
- Код должен быть самодокументируемым
- TODO/FIXME/WARNING для заметок
- Не комментируйте код - удаляйте его
- Избегайте избыточных комментариев

```kotlin
// ❌ Плохо: избыточный комментарий (что)
// Увеличить счетчик на 1
counter++

// ✅ Хорошо: объясняет "почему"
// Используем exponential backoff для retry, чтобы не перегружать сервер
val delay = baseDelay * (2.0.pow(retryCount))

// ✅ Хорошо: TODO для отложенной работы
// TODO: Добавить кеширование после оптимизации БД
fun getUserData(id: Long): User

// ❌ Плохо: закомментированный код
// val oldResult = calculateOldWay(data)
val result = calculateNewWay(data)

// ✅ Хорошо: удалите, используйте git history
val result = calculateNewWay(data)
```

**4. Форматирование:**

*Теория:* Вертикальное форматирование - связанные концепции близко друг к другу. Горизонтальное - строки 80-120 символов. Консистентный стиль в проекте. Пустые строки для разделения концепций.

*Принципы:*
- Связанные концепции близко вертикально
- Строки 80-120 символов
- Консистентный стиль
- Пустые строки разделяют концепции

```kotlin
// ✅ Хорошо: вертикальное форматирование
class UserService(
    private val userRepository: UserRepository,
    private val emailService: EmailService
) {
    // Группа: публичные методы
    fun registerUser(user: User) {
        validateUser(user)
        saveUser(user)
        notifyUser(user)
    }

    fun deleteUser(id: Long) {
        userRepository.delete(id)
    }

    // Группа: приватные методы
    private fun validateUser(user: User) { }
    private fun saveUser(user: User) { }
    private fun notifyUser(user: User) { }
}
```

**5. Обработка ошибок:**

*Теория:* Используйте exceptions вместо error codes. Извлекайте try/catch в отдельные функции. Не возвращайте null - используйте Optional/Result. Exceptions для исключительных ситуаций, не для flow control.

*Принципы:*
- Exceptions вместо error codes
- Извлекайте try/catch в отдельные функции
- Не возвращайте null
- Exceptions для исключительных ситуаций

```kotlin
// ❌ Плохо: error codes
fun saveUser(user: User): Int {
    if (!isValid(user)) return -1
    if (!database.save(user)) return -2
    return 0
}

// ✅ Хорошо: exceptions
fun saveUser(user: User) {
    require(isValid(user)) { "Invalid user" }
    database.save(user)
}

// ✅ Извлечение try/catch
fun deleteUser(id: Long) {
    try {
        deleteUserInternal(id)
    } catch (e: Exception) {
        logError(e)
        throw UserDeletionException(id, e)
    }
}

// ✅ Не возвращайте null
fun findUser(id: Long): User?  // Явно nullable
fun getUser(id: Long): User    // Бросает exception если не найден
```

**6. Code Smells (Запахи кода):**

*Теория:* Признаки плохого дизайна, которые указывают на необходимость рефакторинга. Дублирование, длинные методы/классы, feature envy, primitive obsession, data clumps.

**Основные code smells:**

1. **Дублирование кода** - повторение логики
2. **Длинные методы** (> 20 строк) - трудно понять
3. **Большие классы** (> 300 строк) - делают слишком много
4. **Feature Envy** - метод больше интересуется другим классом
5. **Primitive Obsession** - использование примитивов вместо объектов
6. **Data Clumps** - группы данных, которые всегда вместе

```kotlin
// ❌ Code Smell: Feature Envy
class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        // Метод Order больше интересуется Customer
        val discount = customer.loyaltyLevel * customer.discountRate
        return items.sum() * (1 - discount)
    }
}

// ✅ Рефакторинг: переместить логику в Customer
class Customer {
    fun calculateDiscount(): BigDecimal {
        return loyaltyLevel * discountRate
    }
}

class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        return items.sum() * (1 - customer.calculateDiscount())
    }
}

// ❌ Code Smell: Primitive Obsession
fun createUser(email: String, age: Int)

// ✅ Рефакторинг: использовать value objects
data class Email(val value: String) {
    init { require(value.contains("@")) }
}
data class Age(val value: Int) {
    init { require(value in 0..150) }
}
fun createUser(email: Email, age: Age)
```

**Ключевые правила:**

1. **Boy Scout Rule** - оставляйте код чище, чем нашли
2. **DRY** (Don't Repeat Yourself) - избегайте дублирования
3. **KISS** (Keep It Simple, Stupid) - простота важнее сложности
4. **YAGNI** (You Aren't Gonna Need It) - не пишите код "на будущее"
5. **Single Responsibility** - одна причина для изменения

## Answer (EN)

**Clean Code Theory:**
Clean Code - code that is easy to understand, maintain, and extend. Based on Robert C. Martin (Uncle Bob) principles. Clean code reads like well-written prose, minimizes cognitive load, and makes programmer's intentions explicit.

**1. Meaningful Names:**

*Theory:* Names should reveal intent, be pronounceable and searchable. Class names are nouns, method names are verbs. Avoid disinformation and magic numbers.

*Principles:*
- Reveal intent (intention-revealing)
- Pronounceable
- Searchable
- Classes = nouns, methods = verbs
- Avoid disinformation

```kotlin
// ❌ Bad: unclear intent
val d = 5
val list1 = listOf<Account>()

// ✅ Good: clear intent
val elapsedTimeInDays = 5
val activeAccounts = listOf<Account>()

// ❌ Bad: unpronounceable
data class DtaRcrd102(val genymdhms: Long)

// ✅ Good: pronounceable
data class Customer(val generationTimestamp: Long)

// ✅ Classes = nouns, methods = verbs
class UserRepository {
    fun findById(id: Long): User
    fun save(user: User)
    fun delete(id: Long)
}
```

**2. Functions:**

*Theory:* Functions should be small (< 20 lines), do one thing, have few arguments (0-2 ideal, avoid 3+). No side effects. Separate commands (change state) and queries (return data).

*Principles:*
- Small (< 20 lines)
- Do one thing (Single Responsibility)
- Few arguments (0-2 ideal)
- No side effects
- Command-Query Separation

```kotlin
// ❌ Bad: does many things, long, many arguments
fun processUserData(name: String, email: String, age: Int, address: String, phone: String) {
    validateEmail(email)
    saveToDatabase(name, email, age)
    sendWelcomeEmail(email)
    logActivity(name)
}

// ✅ Good: small functions, one thing
fun registerUser(user: User) {
    validateUser(user)
    saveUser(user)
    notifyUser(user)
}

fun validateUser(user: User) {
    require(user.email.isValidEmail()) { "Invalid email" }
}

fun saveUser(user: User) {
    userRepository.save(user)
}

// ✅ Command-Query Separation
fun getUser(id: Long): User  // Query - only reads
fun updateUser(user: User)   // Command - only changes
```

**3. Comments:**

*Theory:* Explain "why", not "what". Code should be self-documenting. Comments for TODO/FIXME/WARNING. Avoid redundant comments. Don't comment bad code - rewrite it.

*Principles:*
- Explain "why", not "what"
- Code should be self-documenting
- TODO/FIXME/WARNING for notes
- Don't comment code - delete it
- Avoid redundant comments

```kotlin
// ❌ Bad: redundant comment (what)
// Increment counter by 1
counter++

// ✅ Good: explains "why"
// Use exponential backoff for retry to avoid overloading server
val delay = baseDelay * (2.0.pow(retryCount))

// ✅ Good: TODO for deferred work
// TODO: Add caching after DB optimization
fun getUserData(id: Long): User

// ❌ Bad: commented code
// val oldResult = calculateOldWay(data)
val result = calculateNewWay(data)

// ✅ Good: delete, use git history
val result = calculateNewWay(data)
```

**4. Formatting:**

*Theory:* Vertical formatting - related concepts close together. Horizontal - lines 80-120 characters. Consistent style in project. Blank lines separate concepts.

*Principles:*
- Related concepts close vertically
- Lines 80-120 characters
- Consistent style
- Blank lines separate concepts

```kotlin
// ✅ Good: vertical formatting
class UserService(
    private val userRepository: UserRepository,
    private val emailService: EmailService
) {
    // Group: public methods
    fun registerUser(user: User) {
        validateUser(user)
        saveUser(user)
        notifyUser(user)
    }

    fun deleteUser(id: Long) {
        userRepository.delete(id)
    }

    // Group: private methods
    private fun validateUser(user: User) { }
    private fun saveUser(user: User) { }
    private fun notifyUser(user: User) { }
}
```

**5. Error Handling:**

*Theory:* Use exceptions instead of error codes. Extract try/catch into separate functions. Don't return null - use Optional/Result. Exceptions for exceptional situations, not for flow control.

*Principles:*
- Exceptions instead of error codes
- Extract try/catch into separate functions
- Don't return null
- Exceptions for exceptional situations

```kotlin
// ❌ Bad: error codes
fun saveUser(user: User): Int {
    if (!isValid(user)) return -1
    if (!database.save(user)) return -2
    return 0
}

// ✅ Good: exceptions
fun saveUser(user: User) {
    require(isValid(user)) { "Invalid user" }
    database.save(user)
}

// ✅ Extract try/catch
fun deleteUser(id: Long) {
    try {
        deleteUserInternal(id)
    } catch (e: Exception) {
        logError(e)
        throw UserDeletionException(id, e)
    }
}

// ✅ Don't return null
fun findUser(id: Long): User?  // Explicitly nullable
fun getUser(id: Long): User    // Throws exception if not found
```

**6. Code Smells:**

*Theory:* Signs of bad design indicating need for refactoring. Duplication, long methods/classes, feature envy, primitive obsession, data clumps.

**Main code smells:**

1. **Code Duplication** - repeated logic
2. **Long Methods** (> 20 lines) - hard to understand
3. **Large Classes** (> 300 lines) - do too much
4. **Feature Envy** - method more interested in another class
5. **Primitive Obsession** - using primitives instead of objects
6. **Data Clumps** - groups of data always together

```kotlin
// ❌ Code Smell: Feature Envy
class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        // Order method more interested in Customer
        val discount = customer.loyaltyLevel * customer.discountRate
        return items.sum() * (1 - discount)
    }
}

// ✅ Refactoring: move logic to Customer
class Customer {
    fun calculateDiscount(): BigDecimal {
        return loyaltyLevel * discountRate
    }
}

class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        return items.sum() * (1 - customer.calculateDiscount())
    }
}

// ❌ Code Smell: Primitive Obsession
fun createUser(email: String, age: Int)

// ✅ Refactoring: use value objects
data class Email(val value: String) {
    init { require(value.contains("@")) }
}
data class Age(val value: Int) {
    init { require(value in 0..150) }
}
fun createUser(email: Email, age: Age)
```

**Key Rules:**

1. **Boy Scout Rule** - leave code cleaner than you found it
2. **DRY** (Don't Repeat Yourself) - avoid duplication
3. **KISS** (Keep It Simple, Stupid) - simplicity over complexity
4. **YAGNI** (You Aren't Gonna Need It) - don't write code "for future"
5. **Single Responsibility** - one reason to change

---

## Follow-ups

- What is the difference between cohesion and coupling?
- How do you refactor long methods?
- What are SOLID principles?

## Related Questions

### Prerequisites (Easier)
- Basic programming concepts
- Object-oriented programming

