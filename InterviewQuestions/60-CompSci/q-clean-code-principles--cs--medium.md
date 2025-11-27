---
id: cs-001
title: "Clean Code Principles / Принципы чистого кода"
aliases: ["Clean Code Principles", "Принципы чистого кода"]
topic: cs
subtopics: [clean-code, code-quality, software-engineering]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-abstract-class-purpose--cs--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [best-practices, clean-code, code-quality, difficulty/medium, refactoring]
sources: ["https://en.wikipedia.org/wiki/Clean_code"]

date created: Saturday, November 1st 2025, 1:24:22 pm
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Что такое принципы чистого кода? Как писать осмысленные имена, хорошие функции и понятные комментарии? Что такое code smells и как их рефакторить?

# Question (EN)
> What are clean code principles? How do you write meaningful names, good functions, and clear comments? What are code smells and how to refactor them?

---

## Ответ (RU)

**Теория чистого кода:**
Clean Code — код, который легко понять, поддерживать и расширять. Часто опирается на идеи Robert C. Martin (Uncle Bob) и другие признанные практики промышленной разработки. Чистый код читается как хорошо написанная проза, минимизирует когнитивную нагрузку и делает намерения программиста явными.

**1. Осмысленные имена:**

*Теория:* Имена должны раскрывать намерение, быть произносимыми и искомыми. Имена классов — существительные, методов — глаголы. Избегайте дезинформации и магических чисел.

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

*Теория:* Функции должны быть маленькими, делать одно дело, иметь мало аргументов (0–2 желательно; 3+ — повод пересмотреть дизайн). Минимизируйте побочные эффекты. Разделяйте команды (изменяют состояние) и запросы (возвращают данные).

*Принципы:*
- Маленькие (ориентир — до ~20 строк как практическое правило, а не жесткое ограничение)
- Делают одно дело (Single Responsibility)
- Мало аргументов (0–2 обычно достаточно)
- Минимум побочных эффектов
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
fun getUser(id: Long): User?  // Query — только читает, может вернуть null/Option/Result если не найден
fun updateUser(user: User)   // Command — только изменяет
```

**3. Комментарии:**

*Теория:* Объясняйте «почему», не «что». Код по возможности должен быть самодокументируемым. Используйте комментарии для TODO/FIXME/WARNING и сложной доменной логики. Избегайте избыточных комментариев. Не оставляйте закомментированный «мертвый» код в репозитории — его место в системе контроля версий.

*Принципы:*
- Объясняйте «почему», не «что»
- Код должен быть максимально самодокументируемым
- TODO/FIXME/WARNING для заметок
- Не оставляйте закомментированный мертвый код — удаляйте, опирайтесь на git history
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

*Теория:* Вертикальное форматирование — связанные концепции близко друг к другу. Горизонтальное — разумная длина строк (часто 80–120 символов в качестве ориентира). Важен консистентный стиль в проекте. Пустые строки для разделения концепций.

*Принципы:*
- Связанные концепции близко вертикально
- Строки 80–120 символов как практическое правило
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

*Теория:* В прикладном коде обычно предпочтительнее использовать исключения или Result-типы вместо «магических» кодов ошибок. Выносите громоздкий try/catch в отдельные функции. Избегайте неожиданных null: используйте явные nullable-типы, Option/Result и проверку входных данных. Исключения предназначены для действительно исключительных ситуаций, а не для обычного управления потоком.

*Принципы:*
- Вместо неявных кодов ошибок используйте исключения или явные типы результатов (Result/ sealed class)
- Выносите try/catch в отдельные функции для улучшения читаемости
- Избегайте неожиданных null; используйте явный nullable / Option / Result при необходимости
- Не используйте исключения для нормального flow control

```kotlin
// ❌ Плохо: неявные error codes
fun saveUser(user: User): Int {
    if (!isValid(user)) return -1
    if (!database.save(user)) return -2
    return 0
}

// ✅ Лучше: исключения или типизированный результат
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

// ✅ Явное поведение при "не найден"
fun findUser(id: Long): User?          // Может вернуть null — это явно видно из сигнатуры
// или
// fun findUser(id: Long): Result<User>

// Исключение — только если отсутствие пользователя является действительно исключительной ситуацией
fun getExistingUser(id: Long): User {
    return findUser(id) ?: throw UserNotFoundException(id)
}
```

**6. Code Smells (Запахи кода):**

*Теория:* Признаки проблемного дизайна, которые указывают на необходимость рефакторинга. Примеры: дублирование, длинные методы/классы, feature envy, primitive obsession, data clumps.

**Основные code smells:**

1. **Дублирование кода** — повторение логики
2. **Длинные методы** (обычно заметно > ~20–30 строк) — трудно понять
3. **Большие классы** (сотни строк, много обязанностей) — делают слишком много
4. **Feature Envy** — метод больше интересуется данными другого класса, чем своими
5. **Primitive Obsession** — использование примитивов вместо объектов для значимых концепций
6. **Data Clumps** — группы данных, которые всегда передаются вместе

```kotlin
// ❌ Code Smell: Feature Envy
class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        // Метод Order подозрительно много знает о деталях Customer
        val discount = customer.loyaltyLevel * customer.discountRate
        return items.sum() * (BigDecimal.ONE - discount)
    }
}

// ✅ Рефакторинг: переместить логику скидки в Customer
class Customer {
    fun calculateDiscount(): BigDecimal {
        return loyaltyLevel * discountRate
    }
}

class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        return items.sum() * (BigDecimal.ONE - customer.calculateDiscount())
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

1. **Boy Scout Rule** — оставляйте код чище, чем нашли
2. **DRY** (Don't Repeat Yourself) — избегайте дублирования
3. **KISS** (Keep It Simple, Stupid) — простота важнее излишней сложности
4. **YAGNI** (You Aren't Gonna Need It) — не пишите код «на будущее» без реальной потребности
5. **Single Responsibility** — у модуля должна быть одна причина для изменения

---

## Answer (EN)

**Clean Code Theory:**
Clean code is code that is easy to understand, maintain, and extend. It is strongly influenced by Robert C. Martin (Uncle Bob) and other widely accepted industry practices. Clean code reads like well-written prose, minimizes cognitive load, and makes the programmer's intentions explicit.

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

*Theory:* Functions should be small, do one thing, and have few parameters (0–2 is usually enough; 3+ is a design smell to re-evaluate). Minimize side effects. Separate commands (change state) and queries (return data).

*Principles:*
- Small (roughly up to ~20 lines as a heuristic, not a hard rule)
- Do one thing (Single Responsibility)
- Few parameters (0–2 typical)
- Minimize side effects
- Command-Query Separation

```kotlin
// ❌ Bad: does many things, long, many parameters
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
fun getUser(id: Long): User?  // Query — only reads; may return null/Option/Result if not found
fun updateUser(user: User)   // Command — only changes state
```

**3. Comments:**

*Theory:* Explain "why", not "what". Code should be as self-documenting as reasonably possible. Use comments for TODO/FIXME/WARNING and for clarifying non-obvious domain or algorithmic decisions. Avoid redundant comments. Do not leave large blocks of commented-out dead code — rely on version control.

*Principles:*
- Explain "why", not (obvious) "what"
- Code should be as self-documenting as practical
- TODO/FIXME/WARNING for notes
- Don't keep commented-out dead code; delete it and rely on git history
- Avoid redundant comments

```kotlin
// ❌ Bad: redundant comment (what)
// Increment counter by 1
counter++

// ✅ Good: explains "why"
// Use exponential backoff for retry to avoid overloading the server
val delay = baseDelay * (2.0.pow(retryCount))

// ✅ Good: TODO for deferred work
// TODO: Add caching after DB optimization
fun getUserData(id: Long): User

// ❌ Bad: commented-out old implementation
// val oldResult = calculateOldWay(data)
val result = calculateNewWay(data)

// ✅ Good: delete, use git history
val result = calculateNewWay(data)
```

**4. Formatting:**

*Theory:* Vertical formatting: keep related concepts close together. Horizontal formatting: use reasonable line length (often 80–120 characters as a guideline). Maintain a consistent style across the project. Use blank lines to separate logical sections.

*Principles:*
- Related concepts close vertically
- Lines of 80–120 characters as a practical guideline
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

*Theory:* In typical application/business code, prefer exceptions or explicit result types over ad-hoc error codes. Extract heavy try/catch blocks into separate functions for readability. Avoid unexpected nulls: use explicit nullable types, Option/Result, and input validation. Use exceptions for truly exceptional situations, not for normal control flow (e.g., a routinely missing record).

*Principles:*
- Prefer exceptions or typed results over magic error codes
- Extract try/catch into helper functions when it improves clarity
- Avoid unexpected null; use explicit nullable / Option / Result instead
- Don't use exceptions for normal flow control

```kotlin
// ❌ Bad: magic error codes
fun saveUser(user: User): Int {
    if (!isValid(user)) return -1
    if (!database.save(user)) return -2
    return 0
}

// ✅ Better: exceptions or typed result
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

// ✅ Explicit behavior for "not found"
fun findUser(id: Long): User?          // May return null — explicit in signature
// or
// fun findUser(id: Long): Result<User>

// Throw only if absence is exceptional in this context
fun getExistingUser(id: Long): User {
    return findUser(id) ?: throw UserNotFoundException(id)
}
```

**6. Code Smells (Запахи кода):**

*Theory:* Signs of problematic design that indicate the need for refactoring. Examples: duplication, long methods/classes, feature envy, primitive obsession, data clumps.

**Main code smells:**

1. **Code Duplication** — repeated logic
2. **Long Methods** (commonly noticeable > ~20–30 lines) — hard to understand
3. **Large Classes** (hundreds of lines, many responsibilities) — do too much
4. **Feature Envy** — a method is more interested in another class's data than its own
5. **Primitive Obsession** — using primitives for rich domain concepts instead of dedicated types
6. **Data Clumps** — groups of data that are always passed together

```kotlin
// ❌ Code Smell: Feature Envy
class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        // Order method suspiciously depends on Customer internals
        val discount = customer.loyaltyLevel * customer.discountRate
        return items.sum() * (BigDecimal.ONE - discount)
    }
}

// ✅ Refactoring: move discount logic to Customer
class Customer {
    fun calculateDiscount(): BigDecimal {
        return loyaltyLevel * discountRate
    }
}

class Order {
    fun calculateTotal(customer: Customer): BigDecimal {
        return items.sum() * (BigDecimal.ONE - customer.calculateDiscount())
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

1. **Boy Scout Rule** — leave the code cleaner than you found it
2. **DRY** (Don't Repeat Yourself) — avoid duplication
3. **KISS** (Keep It Simple, Stupid) — favor simplicity over unnecessary complexity
4. **YAGNI** (You Aren't Gonna Need It) — don't build for hypothetical future needs without evidence
5. **Single Responsibility** — a module should have one reason to change

---

## Дополнительные Вопросы (RU)

- В чем разница между связностью (cohesion) и зацеплением (coupling)?
- Как refactorить длинные методы?
- Что такое принципы SOLID?

## Follow-ups

- What is the difference between cohesion and coupling?
- How do you refactor long methods?
- What are SOLID principles?

## Связанные Вопросы (RU)

### Предпосылки (более простые)
- Базовые концепции программирования
- Объектно-ориентированное программирование

## Related Questions

### Prerequisites (Easier)
- Basic programming concepts
- Object-oriented programming

## References (RU)

- Статья "Clean Code" на Википедии: https://ru.wikipedia.org/wiki/Clean_Code

## References

- [Clean Code (Wikipedia)](https://en.wikipedia.org/wiki/Clean_code)
