---
id: kotlin-212
title: "Data Sealed Classes Definition / Data и Sealed классы определение"
aliases: [Data Sealed Classes, Data и Sealed классы]
topic: kotlin
subtopics: [sealed-classes]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-sealed-classes, q-kotlin-channels--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [sealed-classes, difficulty/hard, programming-languages]
---
# Вопрос (RU)
> Что такое Data Class и Sealed Classes в Kotlin? Объясните их характеристики, применения и приведите подробные примеры.

---

# Question (EN)
> What are Data Class and Sealed Classes in Kotlin? Explain their characteristics, use cases, and provide comprehensive examples.

## Ответ (RU)

### Data Class

**Data Class** — специальный тип класса, предназначенный для хранения данных. Основная цель — содержать данные; бизнес-логика обычно минимальна и не влияет на то, что класс является `data`. Объявляется с ключевым словом `data`.

**Ключевые особенности data class:**

1. **Автоматическая генерация методов**: Kotlin автоматически генерирует (на основе свойств `val`/`var` в primary constructor):
   - `equals()` — сравнение по содержимому этих свойств
   - `hashCode()` — для hash-коллекций
   - `toString()` — строковое представление
   - `copy()` — создание копий с изменениями
   - `componentN()` — компонентные функции для деструктуризации

2. **Использование**:
   - Передача данных между компонентами программы
   - Модели в MVC или MVVM
   - DTO (Data Transfer Objects)
   - POJO (Plain Old Java Objects)

3. **Требования и ограничения (ключевые)**:
   - Должен иметь primary constructor
   - Должен содержать минимум один параметр в primary constructor
   - Для участия в автогенерации методов параметры должны быть объявлены как `val` или `var`
   - Нельзя объявлять `data` класс как `abstract`, `open`, `sealed` или `inner`
   - Нельзя явно объявлять `component1`, `component2` и `copy` с несовместимой сигнатурой

**Пример data class:**
```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val category: String
)

val laptop = Product(1, "MacBook Pro", 2499.99, "Electronics")

// Автоматический toString()
println(laptop)
// Product(id=1, name=MacBook Pro, price=2499.99, category=Electronics)

// Автоматический equals() - сравнение по содержимому
val laptop2 = Product(1, "MacBook Pro", 2499.99, "Electronics")
println(laptop == laptop2)  // true

// Автоматический hashCode() - корректно работает в hash-коллекциях
val productSet = setOf(laptop, laptop2)
println("Set size: ${productSet.size}")  // 1 (дубликаты удалены)

// copy() метод - создание изменённых копий
val discountedLaptop = laptop.copy(price = 1999.99)
println(discountedLaptop)
// Product(id=1, name=MacBook Pro, price=1999.99, category=Electronics)

// Деструктуризация с componentN()
val (id, name, price, category) = laptop
println("$name стоит $$price")  // MacBook Pro стоит $2499.99
```

**Data class в MVC/MVVM:**
```kotlin
// Model слой
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val isActive: Boolean
) {
    // Дополнительные методы можно добавлять
    fun getFullName() = "$firstName $lastName"
}

// DTO для API
data class CreateUserRequest(
    val username: String,
    val email: String,
    val password: String,
    val firstName: String,
    val lastName: String
)

data class UserResponse(
    val success: Boolean,
    val user: User?,
    val message: String
)

// ViewModel
class UserViewModel {
    private var currentUser: User? = null

    fun createUser(request: CreateUserRequest): UserResponse {
        val newUser = User(
            id = 1,
            username = request.username,
            email = request.email,
            firstName = request.firstName,
            lastName = request.lastName,
            isActive = true
        )
        currentUser = newUser

        return UserResponse(
            success = true,
            user = newUser,
            message = "Пользователь создан успешно"
        )
    }

    fun updateUserEmail(newEmail: String): User? {
        currentUser = currentUser?.copy(email = newEmail)
        return currentUser
    }
}
```

### Sealed Class

**Sealed Class** — класс, который ограничивает множество допустимых реализаций. Он позволяет определять ограниченные иерархии типов, где все возможные подклассы известны (и контролируются) на этапе компиляции. Особенно полезен с `when`, так как компилятор может проверять исчерпывающую обработку.

**Ключевые особенности:**

1. **Ограниченное наследование**:
   - В классическом виде все непосредственные подклассы должны быть объявлены в том же файле, что и sealed-класс
   - В современных версиях Kotlin для sealed классов и интерфейсов также поддерживается объявление подклассов в том же package при соблюдении правил компилятора (а не в произвольном месте модуля)

2. **Использование с `when`**: Идеально подходят для `when`-выражений, поскольку Kotlin знает полный набор подклассов и может требовать исчерпывающей обработки без ветки `else`

3. **Типобезопасность**: Обеспечивает compile-time безопасность при моделировании конечного (закрытого) набора вариантов

**Пример sealed class:**
```kotlin
// Sealed class иерархия
sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data class Triangle(val base: Double, val height: Double) : Shape()
    object Unknown : Shape()
}

// Расчёт площади - компилятор проверяет все случаи
fun calculateArea(shape: Shape): Double {
    return when (shape) {
        is Shape.Circle -> Math.PI * shape.radius * shape.radius
        is Shape.Rectangle -> shape.width * shape.height
        is Shape.Triangle -> 0.5 * shape.base * shape.height
        Shape.Unknown -> 0.0
        // else не нужен - компилятор знает все подклассы
    }
}

val shapes = listOf(
    Shape.Circle(5.0),
    Shape.Rectangle(4.0, 6.0),
    Shape.Triangle(3.0, 4.0),
    Shape.Unknown
)

shapes.forEach { shape ->
    println("Фигура: $shape")
    println("Площадь: ${calculateArea(shape)}")
}
```

**Sealed class для навигации:**
```kotlin
sealed class Screen {
    object Home : Screen()
    object Profile : Screen()
    data class UserDetails(val userId: Int) : Screen()
    data class Settings(val section: String) : Screen()
    object Login : Screen()
}

// Типобезопасная навигация
fun navigate(screen: Screen) {
    when (screen) {
        Screen.Home -> println("Навигация на главный экран")
        Screen.Profile -> println("Навигация на профиль")
        is Screen.UserDetails -> {
            println("Навигация к пользователю ${screen.userId}")
        }
        is Screen.Settings -> {
            println("Навигация в настройки: ${screen.section}")
        }
        Screen.Login -> println("Навигация на вход")
        // При добавлении нового подкласса sealed-класса компилятор потребует обновить when
    }
}
```

**Продвинутый пример: Sealed class для API ответов:**
```kotlin
// Универсальный sealed class для API результатов
sealed class ApiResponse<out T> {
    data class `Success<T>`(
        val data: T,
        val statusCode: Int = 200,
        val headers: Map<String, String> = emptyMap()
    ) : ApiResponse<T>()

    data class Error(
        val statusCode: Int,
        val message: String,
        val errors: List<String> = emptyList()
    ) : ApiResponse<Nothing>()

    object Loading : ApiResponse<Nothing>()

    object NotAuthenticated : ApiResponse<Nothing>()
}

// Domain модели
data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// API сервис
class ArticleService {
    fun fetchArticles(): ApiResponse<List<Article>> {
        return try {
            val articles = listOf(
                Article(1, "Основы Kotlin", "Изучаем Kotlin...", "Алиса", System.currentTimeMillis()),
                Article(2, "Продвинутый Kotlin", "Глубокое погружение...", "Боб", System.currentTimeMillis())
            )
            ApiResponse.`Success<T>`(
                data = articles,
                statusCode = 200,
                headers = mapOf("Content-Type" to "application/json")
            )
        } catch (e: Exception) {
            ApiResponse.Error(500, "Ошибка сервера", listOf(e.message ?: "Неизвестная ошибка"))
        }
    }
}

// UI обработчик
fun displayArticles(response: ApiResponse<List<Article>>) {
    when (response) {
        is ApiResponse.`Success<T>` -> {
            println("Успешно! Статус: ${response.statusCode}")
            response.data.forEach { article ->
                println("${article.title} от ${article.author}")
            }
        }
        is ApiResponse.Error -> {
            println("Ошибка ${response.statusCode}: ${response.message}")
            response.errors.forEach { println("  - $it") }
        }
        ApiResponse.Loading -> {
            println("Загрузка статей...")
        }
        ApiResponse.NotAuthenticated -> {
            println("Войдите чтобы просмотреть статьи")
        }
    }
}
```

### Комбинирование Data Class И Sealed Class

**Очень распространённый паттерн - sealed class с data подклассами:**
```kotlin
// Управление состоянием формы
data class FormData(
    val username: String = "",
    val email: String = "",
    val password: String = ""
)

sealed class FormState {
    object Initial : FormState()
    data class Editing(val data: FormData) : FormState()
    data class Validating(val data: FormData) : FormState()
    data class Valid(val data: FormData) : FormState()
    data class Invalid(val data: FormData, val errors: List<String>) : FormState()
    data class Submitting(val data: FormData) : FormState()
    data class Submitted(val data: FormData, val userId: Int) : FormState()
}

fun validateForm(data: FormData): FormState {
    val errors = mutableListOf<String>()

    if (data.username.length < 3) {
        errors.add("Имя пользователя должно быть не менее 3 символов")
    }
    if (!data.email.contains("@")) {
        errors.add("Неверный email адрес")
    }
    if (data.password.length < 8) {
        errors.add("Пароль должен быть не менее 8 символов")
    }

    return if (errors.isEmpty()) {
        FormState.Valid(data)
    } else {
        FormState.Invalid(data, errors)
    }
}

fun handleFormState(state: FormState) {
    when (state) {
        FormState.Initial -> {
            println("Форма готова к вводу")
        }
        is FormState.Editing -> {
            println("Редактирование формы: ${state.data.username}")
        }
        is FormState.Validating -> {
            println("Валидация формы...")
        }
        is FormState.Valid -> {
            println("Форма валидна! Готова к отправке")
        }
        is FormState.Invalid -> {
            println("Ошибки в форме:")
            state.errors.forEach { println("  - $it") }
        }
        is FormState.Submitting -> {
            println("Отправка формы для ${state.data.username}...")
        }
        is FormState.Submitted -> {
            println("Форма отправлена! ID пользователя: ${state.userId}")
        }
    }
}
```

### Сравнительная Таблица

| Характеристика | Data Class | Sealed Class |
|----------------|-----------|--------------|
| **Назначение** | Хранение и перенос данных | Ограниченная (закрытая) иерархия типов |
| **Автогенерация** | `equals`, `hashCode`, `toString`, `copy`, `componentN` для свойств из primary constructor | Нет автогенерации, обычные правила классов |
| **Наследование** | По умолчанию `final`, можно сделать `open`; `data` нельзя сочетать с `abstract`/`sealed`/`inner` | Наследование ограничено: новые подклассы могут быть объявлены только в разрешённом контексте (файл/пакет по правилам sealed) |
| **Подклассы** | Не ограничены самим фактом `data` | Жёстко ограничены местом объявления (контролируемый набор вариантов) |
| **Применение** | Модели, DTO, значения, ответы API | Состояния, результаты, события, вариации доменных моделей |
| **When exhaustive** | Не даёт специальных гарантий; обычные классы | Да, для `when` над sealed-иерархией возможна проверка исчерпывающей обработки |
| **Деструктуризация** | Да, через `componentN()` для свойств из primary constructor | Только если подкласс сам (обычно `data`) её предоставляет |
| **copy()** | Да, для data class | Только если реализовано вручную или подкласс — data class |

### Краткий Ответ

**Data Class**: Специальный класс для хранения и переноса данных. Автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` для свойств из primary constructor. Требует primary constructor с минимум одним параметром. Параметры, объявленные как `val`/`var`, участвуют в автогенерации. Используется для моделей данных, DTO, ответов API, сущностей в MVC/MVVM.

**Sealed Class**: Ограничивает возможные наследники контролируемым набором (тот же файл или разрешённый контекст / тот же package в современных версиях Kotlin). Позволяет строить типобезопасные иерархии, для которых `when` может быть исчерпывающим без `else`. Все допустимые варианты известны на этапе компиляции. Используется для UI состояний (Loading/Success/Error), Result-типов, навигационных событий, команд.

**Комбинирование**: Частый паттерн — sealed класс с data-подклассами для представления состояний с данными (например, `sealed class UiState` с `data class Success<T>(val data: T)`).

## Answer (EN)

### Data Class

A data class is a special kind of class primarily intended for holding and transferring data. Declared using the `data` keyword. Business logic can exist, but these classes are optimized for representing values.

**Key features of data class:**
- Automatic generation of:
  - `equals()` / `hashCode()` based on properties declared with `val`/`var` in the primary constructor
  - `toString()` including those properties
  - `copy()` for cloning with modifications
  - `componentN()` functions for destructuring declarations
- Typical usage: data transfer between components, MVC/MVVM models, DTOs, POJOs.
- Requirements and constraints:
  - Must have a primary constructor
  - Must have at least one parameter in the primary constructor
  - Only `val`/`var` parameters in the primary constructor participate in generated methods
  - Cannot be `abstract`, `open`, `sealed`, or `inner`
  - Must not declare `copy`/`componentN` with incompatible signatures

### Sealed Class

A sealed class restricts which classes can inherit from it, defining a closed hierarchy where all permitted subclasses are known and controlled at compile time. This is especially powerful with `when` expressions, because the compiler can enforce exhaustive handling.

**Key features:**
- Restricted inheritance:
  - Traditionally, all direct subclasses must be in the same file as the sealed class
  - In modern Kotlin, sealed classes/interfaces may also have subclasses in the same package under specific compiler rules; subclasses still cannot be defined arbitrarily anywhere in the module
- Excellent with `when`:
  - Enables exhaustive `when` without an `else` when all subclasses are covered
- Type safety:
  - Strong compile-time guarantees when modeling a fixed/closed set of variants

### Code Examples

(Each snippet is standalone and illustrative.)

**Data Class example:**
```kotlin
data class Product(
    val id: Int,
    val name: String,
    val price: Double,
    val category: String
)

val laptop = Product(1, "MacBook Pro", 2499.99, "Electronics")

println(laptop)
// Product(id=1, name=MacBook Pro, price=2499.99, category=Electronics)

val laptop2 = Product(1, "MacBook Pro", 2499.99, "Electronics")
println(laptop == laptop2)  // true

val productSet = setOf(laptop, laptop2)
println("Set size: ${productSet.size}")  // 1

val discountedLaptop = laptop.copy(price = 1999.99)
println(discountedLaptop)

val (id, name, price, category) = laptop
println("$name costs $$price")
```

**Data class in MVC/MVVM:**
```kotlin
data class User(
    val id: Int,
    val username: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val isActive: Boolean
) {
    fun getFullName() = "$firstName $lastName"
}

data class CreateUserRequest(
    val username: String,
    val email: String,
    val password: String,
    val firstName: String,
    val lastName: String
)

data class UserResponse(
    val success: Boolean,
    val user: User?,
    val message: String
)

class UserViewModel {
    private var currentUser: User? = null

    fun createUser(request: CreateUserRequest): UserResponse {
        val newUser = User(
            id = 1,
            username = request.username,
            email = request.email,
            firstName = request.firstName,
            lastName = request.lastName,
            isActive = true
        )
        currentUser = newUser

        return UserResponse(
            success = true,
            user = newUser,
            message = "User created successfully"
        )
    }

    fun updateUserEmail(newEmail: String): User? {
        currentUser = currentUser?.copy(email = newEmail)
        return currentUser
    }
}
```

**Sealed Class example:**
```kotlin
sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data class Triangle(val base: Double, val height: Double) : Shape()
    object Unknown : Shape()
}

fun calculateArea(shape: Shape): Double = when (shape) {
    is Shape.Circle -> Math.PI * shape.radius * shape.radius
    is Shape.Rectangle -> shape.width * shape.height
    is Shape.Triangle -> 0.5 * shape.base * shape.height
    Shape.Unknown -> 0.0
}
```

**Sealed class for navigation:**
```kotlin
sealed class Screen {
    object Home : Screen()
    object Profile : Screen()
    data class UserDetails(val userId: Int) : Screen()
    data class Settings(val section: String) : Screen()
    object Login : Screen()
}

fun navigate(screen: Screen) {
    when (screen) {
        Screen.Home -> println("Navigating to Home screen")
        Screen.Profile -> println("Navigating to Profile screen")
        is Screen.UserDetails -> println("Navigating to User Details for user ${screen.userId}")
        is Screen.Settings -> println("Navigating to Settings: ${screen.section}")
        Screen.Login -> println("Navigating to Login screen")
    }
}
```

**Sealed class for API responses:**
```kotlin
sealed class ApiResponse<out T> {
    data class `Success<T>`(
        val data: T,
        val statusCode: Int = 200,
        val headers: Map<String, String> = emptyMap()
    ) : ApiResponse<T>()

    data class Error(
        val statusCode: Int,
        val message: String,
        val errors: List<String> = emptyList()
    ) : ApiResponse<Nothing>()

    object Loading : ApiResponse<Nothing>()

    object NotAuthenticated : ApiResponse<Nothing>()
}

data class Article(
    val id: Int,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

class ArticleService {
    fun fetchArticles(): ApiResponse<List<Article>> {
        return try {
            val articles = listOf(
                Article(1, "Kotlin Basics", "Learn Kotlin...", "Alice", System.currentTimeMillis()),
                Article(2, "Advanced Kotlin", "Deep dive...", "Bob", System.currentTimeMillis())
            )
            ApiResponse.`Success<T>`(
                data = articles,
                statusCode = 200,
                headers = mapOf("Content-Type" to "application/json")
            )
        } catch (e: Exception) {
            ApiResponse.Error(500, "Server error", listOf(e.message ?: "Unknown error"))
        }
    }
}

fun displayArticles(response: ApiResponse<List<Article>>) {
    when (response) {
        is ApiResponse.`Success<T>` -> {
            println("Success! Status: ${response.statusCode}")
            response.data.forEach { article ->
                println("${article.title} by ${article.author}")
            }
        }
        is ApiResponse.Error -> {
            println("Error ${response.statusCode}: ${response.message}")
            response.errors.forEach { println("  - $it") }
        }
        ApiResponse.Loading -> println("Loading articles...")
        ApiResponse.NotAuthenticated -> println("Please log in to view articles")
    }
}
```

### Comparison Table

| Characteristic | Data Class | Sealed Class |
|----------------|-----------|--------------|
| Purpose | Holding and transferring data | Restricted (closed) type hierarchy |
| Auto-generation | `equals`, `hashCode`, `toString`, `copy`, `componentN` for primary-constructor properties | No special auto-generation beyond normal rules |
| Inheritance | `final` by default; cannot be `abstract`/`sealed`/`inner` as `data` | Subclasses restricted to allowed contexts (same file / same package per sealed rules) |
| Subclasses | Not restricted by being `data` | Strictly controlled set of subclasses |
| Use cases | Models, DTOs, value objects, API responses | States, results, events, domain variants |
| When exhaustive | No special guarantees | Enables exhaustive `when` over the sealed hierarchy |
| Destructuring | Yes, via generated `componentN()` | Only if specific subclasses (often `data`) define it |
| `copy()` | Provided for data classes | Only if implemented manually or subclass is a data class |

### Short Answer

- Data classes: concise value types with generated `equals`/`hashCode`/`toString`/`copy`/`componentN`, ideal for models, DTOs, and API payloads.
- Sealed classes: define a closed set of subclasses (same file or, in modern Kotlin, same package under rules), ideal for modeling states, results, and events with exhaustive `when`.
- Common pattern: use sealed class as the closed hierarchy and data subclasses to carry structured data for each variant (for example, `sealed class UiState` with `data class Success<T>(val data: T)`).

---

## Дополнительные вопросы (RU)

- Каковы ключевые отличия от реализации похожих концепций в Java?
- Когда на практике стоит использовать data и sealed классы?
- Какие типичные ошибки и подводные камни при работе с этими классами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-kotlin-sam-conversions--programming-languages--medium]]
- [[q-sequences-vs-collections-performance--kotlin--medium]]
- [[q-kotlin-channels--kotlin--medium]]

## Related Questions

- [[q-kotlin-sam-conversions--programming-languages--medium]]
- [[q-sequences-vs-collections-performance--kotlin--medium]]
- [[q-kotlin-channels--kotlin--medium]]

## Концепты (RU)

- [[c-kotlin]]
- [[c-sealed-classes]]

## Concepts

- [[c-kotlin]]
- [[c-sealed-classes]]