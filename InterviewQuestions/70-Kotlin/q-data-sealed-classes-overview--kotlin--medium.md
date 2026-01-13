---
'---id': kotlin-206
title: Data Sealed Classes Overview / Data и Sealed классы обзор
aliases:
- Data Sealed Classes Overview
- Data и Sealed классы обзор
topic: kotlin
subtopics:
- sealed-classes
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-sealed-classes
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
- q-coroutinescope-vs-supervisorscope--kotlin--medium
- q-job-state-machine-transitions--kotlin--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- data-classes
- difficulty/medium
- programming-languages
- sealed-classes
anki_cards:
- slug: q-data-sealed-classes-overview--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-data-sealed-classes-overview--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Что известно о data классах и sealed классах в Kotlin? Каковы их характеристики и применения?

---

# Question (EN)
> What is known about data classes and sealed classes in Kotlin? What are their characteristics and use cases?

## Ответ (RU)

### Data Классы

**Data классы** предназначены для хранения данных и автоматически генерируют несколько полезных методов (на основе объявленных в первичном конструкторе свойств):
- `equals()` - для сравнения по содержимому
- `hashCode()` - для использования в hash-коллекциях
- `toString()` - для строкового представления
- `copy()` - для создания копий с изменёнными свойствами
- `componentN()` - компонентные функции для деструктуризации

**Применение:**
- Модели данных в приложениях
- DTO (Data Transfer Objects)
- POJO/POKO модели
- API response models

**Пример:**
```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
)

fun main() {
    val user1 = User(1, "Alice", "alice@example.com", 30)
    val user2 = User(1, "Alice", "alice@example.com", 30)
    val user3 = User(2, "Bob", "bob@example.com", 25)

    // Автоматический equals()
    println(user1 == user2)  // true (одинаковое содержимое)
    println(user1 == user3)  // false (разное содержимое)

    // Автоматический toString()
    println(user1)  // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Автоматический hashCode()
    val userSet = setOf(user1, user2, user3)
    println(userSet.size)  // 2 (user1 и user2 равны)

    // copy() функция
    val olderUser = user1.copy(age = 31)
    println(olderUser)  // User(id=1, name=Alice, email=alice@example.com, age=31)

    // Деструктуризация с componentN()
    val (id, name, email, age) = user1
    println("$name is $age years old")
}
```

**Пример data класса как DTO/Model:**
```kotlin
// Модель ответа API
data class ApiResponse(
    val success: Boolean,
    val message: String,
    val data: List<User>?
)

data class User(
    val id: Int,
    val username: String,
    val isActive: Boolean
)

fun parseApiResponse(json: String): ApiResponse {
    // Упрощённый пример парсинга JSON
    return ApiResponse(
        success = true,
        message = "Users fetched successfully",
        data = listOf(
            User(1, "alice", true),
            User(2, "bob", false)
        )
    )
}

fun main() {
    val response = parseApiResponse("{}")
    println(response)

    response.data?.forEach { user ->
        println("User: ${user.username}, Active: ${user.isActive}")
    }
}
```

### Sealed Классы

**Sealed классы** ограничивают множество допустимых подклассов и используются для создания типобезопасных иерархий:
- Все разрешённые подклассы известны на этапе компиляции
- Идеальны для представления ограниченных иерархий классов (закрытых наборов вариантов)
- Отлично работают с `when` выражениями (exhaustive checking без `else` при обработке всех вариантов)
- Часто используются для управления состояниями в архитектурных компонентах

Исторически sealed классы позволяли наследование только в том же файле. В более новых версиях Kotlin (и с sealed интерфейсами) правила могут расширяться (например, до одного модуля или пакета для определённых таргетов), но ключевая идея остаётся: набор подклассов замкнут и контролируем компилятором.

**Применение:**
- Управление UI состояниями (Loading, Success, Error)
- Result/Response типы для сетевых запросов
- Навигационные события
- Sealed иерархии команд или действий

**Пример UI состояния:**
```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String, val code: Int) : UiState()
    object Empty : UiState()
}

fun renderUi(state: UiState) {
    when (state) {
        is UiState.Loading -> println("Показываем загрузку...")
        is UiState.Success -> println("Отображаем данные: ${state.data}")
        is UiState.Error -> println("Ошибка ${state.code}: ${state.message}")
        is UiState.Empty -> println("Нет данных")
        // else не нужен - компилятор знает все варианты
    }
}

fun main() {
    renderUi(UiState.Loading)
    renderUi(UiState.Success(listOf("Item 1", "Item 2")))
    renderUi(UiState.Error("Network error", 500))
    renderUi(UiState.Empty)
}
```

**Пример сетевого результата:**
```kotlin
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: Exception) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

data class Product(val id: Int, val name: String, val price: Double)

fun fetchProducts(): NetworkResult<List<Product>> {
    return try {
        val products = listOf(
            Product(1, "Laptop", 999.99),
            Product(2, "Mouse", 29.99)
        )
        NetworkResult.Success(products)
    } catch (e: Exception) {
        NetworkResult.Error(e)
    }
}

fun handleResult(result: NetworkResult<List<Product>>) {
    when (result) {
        is NetworkResult.Success -> {
            println("Загружено ${result.data.size} товаров:")
            result.data.forEach { product ->
                println("  ${product.name}: $${product.price}")
            }
        }
        is NetworkResult.Error -> {
            println("Ошибка: ${result.exception.message}")
        }
        is NetworkResult.Loading -> {
            println("Загрузка товаров...")
        }
    }
}

fun main() {
    val result = fetchProducts()
    handleResult(result)
}
```

### Комбинирование Data И Sealed Классов

Очень распространённый паттерн — sealed класс с data подклассами. Это позволяет одновременно:
- Иметь удобные value-объекты с автогенерируемыми методами
- Гарантировать закрытый набор вариантов для исчерпывающих `when`:

```kotlin
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Failure(val error: String) : Result()
}

fun divide(a: Int, b: Int): Result {
    return if (b != 0) {
        Result.Success(a / b)
    } else {
        Result.Failure("Деление на ноль")
    }
}

fun main() {
    val result1 = divide(10, 2)
    val result2 = divide(10, 0)

    when (result1) {
        is Result.Success -> println("Результат: ${result1.value}")
        is Result.Failure -> println("Ошибка: ${result1.error}")
    }

    when (result2) {
        is Result.Success -> println("Результат: ${result2.value}")
        is Result.Failure -> println("Ошибка: ${result2.error}")
    }
}
```

### Android MVVM Пример

**Типичное использование в Android с `ViewModel`:**
```kotlin
// Data класс для данных профиля
data class UserProfile(
    val name: String,
    val email: String,
    val avatarUrl: String
)

// Sealed класс для состояний
sealed class ProfileState {
    object Initial : ProfileState()
    object Loading : ProfileState()
    data class Success(val profile: UserProfile) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

class ProfileViewModel {
    private var state: ProfileState = ProfileState.Initial

    fun loadProfile() {
        state = ProfileState.Loading
        // Симуляция загрузки
        state = ProfileState.Success(
            UserProfile(
                name = "Alice",
                email = "alice@example.com",
                avatarUrl = "https://example.com/avatar.jpg"
            )
        )
    }

    fun getState() = state
}

fun main() {
    val viewModel = ProfileViewModel()

    when (val state = viewModel.getState()) {
        is ProfileState.Initial -> println("Ещё не загружено")
        is ProfileState.Loading -> println("Загрузка...")
        is ProfileState.Success -> println("Пользователь: ${state.profile.name}")
        is ProfileState.Error -> println("Ошибка: ${state.message}")
    }

    viewModel.loadProfile()

    when (val state = viewModel.getState()) {
        is ProfileState.Success -> {
            // Деструктуризация data класса
            val (name, email, avatarUrl) = state.profile
            println("Пользователь: $name, Email: $email")
        }
        else -> println("Неуспешное состояние")
    }
}
```

### Ключевые Различия

| Характеристика | Data класс | Sealed класс |
|----------------|-----------|--------------|
| **Назначение** | Хранение данных | Ограниченная иерархия типов (закрытый набор вариантов) |
| **Автогенерация** | `equals`, `hashCode`, `toString`, `copy`, `componentN` для свойств из первичного конструктора | Нет автогенерации этих методов по умолчанию |
| **Наследование** | Обычный класс, может быть `final`/`open`/`abstract` | Абстрактный, наследование только в контролируемой области (файл/модуль в зависимости от версии/таргета) |
| **Подклассы** | Не ограничены языком | Жёстко ограничены: компилятор знает полный набор подклассов |
| **Применение** | Модели, DTOs, value-объекты | Состояния, результаты, события, sum types |
| **When exhaustiveness** | Не даёт исчерпывающей проверки сам по себе | Позволяет исчерпывающие `when` без `else` при обработке всех подклассов |

## Краткая Версия
**Data классы**: Предназначены для хранения данных. Автоматически генерируют `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` (для свойств из первичного конструктора). Используются для моделей данных, DTOs, API responses.

**Sealed классы**: Ограничивают множество подклассов контролируемой областью. Создают типобезопасные иерархии и позволяют исчерпывающие `when`-проверки. Используются для UI состояний (Loading/Success/Error), Result типов, навигационных событий и иерархий команд/действий.

**В Kotlin и Android**: Data классы широко применяются для моделей данных, sealed классы — для выражения состояний, результатов и событий (особенно во `ViewModel` и других слоях). Часто комбинируются: sealed класс с data подклассами.

## Answer (EN)

### Data Classes

Data classes are designed for holding data and automatically generate several useful methods based on properties declared in the primary constructor:
- `equals()` - for content-based equality comparison
- `hashCode()` - for hash-based collections
- `toString()` - for readable string representation
- `copy()` - for creating copies with modified properties
- `componentN()` - component functions for destructuring declarations

Use cases:
- Data models in applications
- DTOs (Data Transfer Objects)
- POJO/POKO-style models
- API response models

### Sealed Classes

Sealed classes define a restricted hierarchy of subclasses and are used to model closed sets of variants:
- All permitted subclasses are known at compile time
- Great for representing restricted class hierarchies / algebraic sum types
- Work very well with `when` expressions, enabling exhaustive checks without `else` when all cases are covered
- Commonly used for state management in architectural components

Historically, sealed classes restricted inheritance to the same file. In newer Kotlin versions (and with sealed interfaces / platform specifics), rules are extended (e.g., controlled within a module/package for some targets), but the core idea is the same: the set of subclasses is closed and compiler-controlled.

Use cases:
- UI state management (Loading, Success, Error)
- Result/Response types for network calls
- Navigation events
- Sealed hierarchies of commands or actions

Both are heavily used in Kotlin and Android: data classes for models, sealed classes for expressing states, results, and events.

### Code Examples

**Data class example:**
```kotlin
// Simple data class
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val age: Int
)

fun main() {
    val user1 = User(1, "Alice", "alice@example.com", 30)
    val user2 = User(1, "Alice", "alice@example.com", 30)
    val user3 = User(2, "Bob", "bob@example.com", 25)

    // Automatic equals() implementation
    println(user1 == user2)  // true (same content)
    println(user1 == user3)  // false (different content)

    // Automatic toString()
    println(user1)  // User(id=1, name=Alice, email=alice@example.com, age=30)

    // Automatic hashCode()
    val userSet = setOf(user1, user2, user3)
    println(userSet.size)  // 2 (user1 and user2 are equal)

    // copy() function
    val olderUser = user1.copy(age = 31)
    println(olderUser)  // User(id=1, name=Alice, email=alice@example.com, age=31)

    // Destructuring with componentN()
    val (id, name, email, age) = user1
    println("$name is $age years old")  // Alice is 30 years old
}
```

**Data class as DTO/Model:**
```kotlin
// Response model from API
data class ApiResponse(
    val success: Boolean,
    val message: String,
    val data: List<User>?
)

data class User(
    val id: Int,
    val username: String,
    val isActive: Boolean
)

fun parseApiResponse(json: String): ApiResponse {
    // Parse JSON and return (simplified example)
    return ApiResponse(
        success = true,
        message = "Users fetched successfully",
        data = listOf(
            User(1, "alice", true),
            User(2, "bob", false)
        )
    )
}

fun main() {
    val response = parseApiResponse("{}")
    println(response)

    response.data?.forEach { user ->
        println("User: ${user.username}, Active: ${user.isActive}")
    }
}
```

**Sealed class example (UI state):**
```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Success(val data: List<String>) : UiState()
    data class Error(val message: String, val code: Int) : UiState()
    object Empty : UiState()
}

fun renderUi(state: UiState) {
    when (state) {
        is UiState.Loading -> println("Showing loading spinner...")
        is UiState.Success -> println("Displaying data: ${state.data}")
        is UiState.Error -> println("Error ${state.code}: ${state.message}")
        is UiState.Empty -> println("No data available")
        // No else needed - compiler knows all cases are covered
    }
}

fun main() {
    renderUi(UiState.Loading)
    renderUi(UiState.Success(listOf("Item 1", "Item 2")))
    renderUi(UiState.Error("Network error", 500))
    renderUi(UiState.Empty)
}
```

**Sealed class for network result:**
```kotlin
sealed class NetworkResult<out T> {
    data class Success<out T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: Exception) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

data class Product(val id: Int, val name: String, val price: Double)

fun fetchProducts(): NetworkResult<List<Product>> {
    return try {
        // Simulate API call
        val products = listOf(
            Product(1, "Laptop", 999.99),
            Product(2, "Mouse", 29.99)
        )
        NetworkResult.Success(products)
    } catch (e: Exception) {
        NetworkResult.Error(e)
    }
}

fun handleResult(result: NetworkResult<List<Product>>) {
    when (result) {
        is NetworkResult.Success -> {
            println("Fetched ${result.data.size} products:")
            result.data.forEach { product ->
                println("  ${product.name}: $${product.price}")
            }
        }
        is NetworkResult.Error -> {
            println("Error: ${result.exception.message}")
        }
        is NetworkResult.Loading -> {
            println("Loading products...")
        }
    }
}

fun main() {
    val result = fetchProducts()
    handleResult(result)
}
```

**Combining data classes with sealed classes:**
```kotlin
// Sealed class with data class subclasses
sealed class Result {
    data class Success(val value: Int) : Result()
    data class Failure(val error: String) : Result()
}

fun divide(a: Int, b: Int): Result {
    return if (b != 0) {
        Result.Success(a / b)
    } else {
        Result.Failure("Division by zero")
    }
}

fun main() {
    val result1 = divide(10, 2)
    val result2 = divide(10, 0)

    when (result1) {
        is Result.Success -> println("Result: ${result1.value}")
        is Result.Failure -> println("Error: ${result1.error}")
    }

    when (result2) {
        is Result.Success -> println("Result: ${result2.value}")
        is Result.Failure -> println("Error: ${result2.error}")
    }
}
```

**Android `ViewModel` state example:**
```kotlin
// Typical usage in Android MVVM
data class UserProfile(
    val name: String,
    val email: String,
    val avatarUrl: String
)

sealed class ProfileState {
    object Initial : ProfileState()
    object Loading : ProfileState()
    data class Success(val profile: UserProfile) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

class ProfileViewModel {
    private var state: ProfileState = ProfileState.Initial

    fun loadProfile() {
        state = ProfileState.Loading
        // Simulate loading
        state = ProfileState.Success(
            UserProfile(
                name = "Alice",
                email = "alice@example.com",
                avatarUrl = "https://example.com/avatar.jpg"
            )
        )
    }

    fun getState() = state
}

fun main() {
    val viewModel = ProfileViewModel()

    when (val state = viewModel.getState()) {
        is ProfileState.Initial -> println("Not loaded yet")
        is ProfileState.Loading -> println("Loading...")
        is ProfileState.Success -> println("User: ${state.profile.name}")
        is ProfileState.Error -> println("Error: ${state.message}")
    }

    viewModel.loadProfile()

    when (val state = viewModel.getState()) {
        is ProfileState.Success -> {
            val (name, email, avatarUrl) = state.profile
            println("Name: $name, Email: $email")
        }
        else -> println("Not successful")
    }
}
```

### Key Differences

| Aspect | Data class | Sealed class |
|--------|-----------|--------------|
| Purpose | Storing and representing data | Restricted type hierarchy (closed set of variants) |
| Auto-generated members | `equals`, `hashCode`, `toString`, `copy`, `componentN` for primary-constructor properties | No such auto-generation by default |
| Inheritance | Regular class, may be `final`/`open`/`abstract` | Abstract, allows subclasses only in a controlled scope (file/module depending on version/target) |
| Subclasses | Not restricted by language | Strictly limited; compiler knows all subclasses |
| Typical usage | Models, DTOs, value objects | States, results, events, sum types |
| `when` exhaustiveness | Does not itself enable exhaustive `when` | Enables exhaustive `when` without `else` when all subclasses are covered |

## Short Version
- Data classes: For representing data with automatically generated utility methods; ideal for models, DTOs, and API responses.
- Sealed classes: For defining a closed set of variants; ideal for UI states (Loading/Success/Error), Result types, navigation events, and command/action hierarchies with exhaustive `when` handling.
- In Kotlin and Android: Data classes are widely used for data models, sealed classes for representing states, results, and events (especially in `ViewModel` and other layers); they are often combined as sealed hierarchies with data subclasses.

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия от подхода в Java?
- Когда вы бы использовали такие конструкции на практике?
- Каких типичных ошибок при работе с data и sealed классами следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-sealed-classes]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-sealed-classes]]

## Связанные Вопросы (RU)

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]

## Related Questions

- [[q-job-state-machine-transitions--kotlin--medium]]
- [[q-coroutinescope-vs-supervisorscope--kotlin--medium]]
