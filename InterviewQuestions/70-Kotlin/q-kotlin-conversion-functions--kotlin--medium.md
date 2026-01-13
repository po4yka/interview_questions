---
anki_cards:
- slug: q-kotlin-conversion-functions--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-kotlin-conversion-functions--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Ответ (RU)

В Kotlin такие функции обычно называют функциями преобразования (conversion functions), которые следуют шаблону `toTargetType()` ("to"-функции), например: `toInt()`, `toLong()`, `toString()`, `toList()` и т.п.

Это обычные функции, часто реализованные как функции-расширения, которые возвращают значение другого типа. Функции-расширения — это механизм, с помощью которого удобно определять такие преобразования, но само понятие — именно "функция преобразования", а не отдельный ключевой тип функции.

Дополнительно иногда используется соглашение именования `asTargetType()` для дешевых или "view"-адаптаций (когда не происходит тяжелого копирования, а создается легкое представление над существующими данными). Это соглашение библиотек, а не правило языка.

### Шаблоны Функций Преобразования

#### 1. Встроенные Функции `toXxx()`

Стандартная библиотека Kotlin предоставляет множество функций `toXxx()`:

```kotlin
// Преобразование чисел
val int = 42
val long = int.toLong()           // Int → Long
val double = int.toDouble()       // Int → Double
val string = int.toString()       // Int → String

// Преобразование строк
val str = "123"
val num = str.toInt()             // String → Int
val numOrNull = str.toIntOrNull() // String → Int? (null, если не число)
val float = str.toFloat()         // String → Float

// Преобразование коллекций
val list = listOf(1, 2, 3)
val set = list.toSet()                  // List → Set
val array = list.toTypedArray()         // List → Array
val mutableList = list.toMutableList()  // List → MutableList
```

#### 2. Функции-расширения Для Кастомных Преобразований

Вы можете определять собственные функции-расширения для преобразований:

```kotlin
// Доменные модели
data class User(val id: Int, val name: String, val email: String)
data class UserDto(val id: Int, val name: String)

// Функция-расширение для преобразования
fun User.toDto(): UserDto {
    return UserDto(
        id = this.id,
        name = this.name
    )
}

// Использование
val user = User(1, "Alice", "alice@example.com")
val dto = user.toDto()  // User → UserDto
```

Рекомендуемый шаблон именования — `toTargetType()`:

```kotlin
fun String.toUser(): User {
    val parts = this.split(",")
    return User(
        id = parts[0].toInt(),
        name = parts[1],
        email = parts[2]
    )
}

val userString = "1,Alice,alice@example.com"
val user = userString.toUser()
```

#### 3. Явное Приведение Типов (casting)

Важно отличать функции преобразования данных (`toXxx()`) от приведения типа ссылки (`as`, `as?`):

```kotlin
// Безопасное приведение (вернет null при неудаче)
val str: String? = obj as? String

// Небезопасное приведение (бросает исключение при неудаче)
val strStrict: String = obj as String

// Проверка типа
if (obj is String) {
    // obj умно приводится к String
    println(obj.length)
}
```

Приведение влияет на то, как компилятор рассматривает ссылку, но не создает новое преобразованное значение, как это делают `toXxx()`.

### Распространенные Паттерны Преобразований

#### Преобразования Чисел

```kotlin
val byte: Byte = 10
val short: Short = byte.toShort()
val int: Int = byte.toInt()
val long: Long = byte.toLong()
val float: Float = byte.toFloat()
val double: Double = byte.toDouble()

// В Kotlin нет автоматического расширяющего приведения
val x: Int = 100
// val y: Long = x  // Ошибка компиляции
val y: Long = x.toLong()  // Требуется явное преобразование
```

#### Преобразования `String`

```kotlin
// В строку
val num = 42
val strNum = num.toString()      // "42"
val hex = num.toString(16)       // "2a" (шестнадцатеричное)
val binary = num.toString(2)     // "101010" (двоичное)

// Из строки
val s = "123"
val intVal = s.toInt()
val longVal = s.toLong()
val doubleVal = s.toDouble()

// Безопасное преобразование
val invalid = "abc"
val num1 = invalid.toIntOrNull() // null (без исключения)
val num2 = invalid.toInt()       // NumberFormatException
```

#### Преобразования Коллекций

```kotlin
val listNums = listOf(1, 2, 3, 2, 1)
val setNums = listNums.toSet()           // [1, 2, 3]
val arrayNums = listNums.toTypedArray()  // Array<Int>
val intArray = listNums.toIntArray()     // IntArray

// Изменяемость
val immutableList = listOf(1, 2, 3)
val mutableList2 = immutableList.toMutableList()
mutableList2.add(4)

val mutableSet = mutableSetOf(1, 2)
val immutableSet2 = mutableSet.toSet()
```

#### Преобразования `Map`

```kotlin
val users = listOf(
    User(1, "Alice", "alice@example.com"),
    User(2, "Bob", "bob@example.com")
)

val userMap = users.associateBy { it.id }
// Map: {1=User(...), 2=User(...)}

val map = mapOf(1 to "one", 2 to "two")
val listPairs = map.toList()               // List<Pair<Int, String>>
val entries = map.entries.toList()         // List<Map.Entry<Int, String>>
```

#### Кастомные Доменные Преобразования

```kotlin
data class UserEntity(
    val id: Int,
    val firstName: String,
    val lastName: String,
    val email: String,
    val passwordHash: String
)

data class UserResponse(
    val id: Int,
    val fullName: String,
    val email: String
)

fun UserEntity.toResponse(): UserResponse {
    return UserResponse(
        id = this.id,
        fullName = "$firstName $lastName",
        email = this.email
    )
}

val entity = UserEntity(1, "Alice", "Smith", "alice@example.com", "hash123")
val response = entity.toResponse()
```

#### Преобразования в/из JSON (через библиотеки)

```kotlin
// Используем kotlinx.serialization
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class User(val name: String, val age: Int)

val userJson = User("Alice", 30)
val json = Json.encodeToString(userJson)              // User → JSON String
val decodedUser = Json.decodeFromString<User>(json)   // JSON String → User
```

Это функции преобразования, предоставляемые библиотеками, а не автоматические преобразования на уровне языка.

### Рекомендации (Best Practices)

1. Явное и понятное именование:

```kotlin
// Хорошо
fun User.toDto(): UserDto
fun UserDto.toEntity(): User
fun String.toBase64(): String
fun ByteArray.toHexString(): String

// Плохо
fun User.convert(): UserDto
fun transform(user: User): UserDto
```

1. Учитывайте null-безопасность:

```kotlin
val age = ageString.toIntOrNull() ?: 0
// вместо потенциально опасного
// val age2 = ageString.toInt()
```

1. Используйте функции-расширения для доменных преобразований, чтобы вызовы читались естественно:

```kotlin
fun Order.toOrderResponse(): OrderResponse {
    return OrderResponse(/* ... */)
}

val responseOrder = order.toOrderResponse()
```

1. Для коллекций используйте пакетные преобразования:

```kotlin
val usersListEn: List<User> = /* ... */
val dtoListEn: List<UserDto> = usersListEn.map { it.toDto() }

fun List<User>.toDtos(): List<UserDto> = map { it.toDto() }

val dtoList2En = usersListEn.toDtos()
```

---

## Answer (EN)

In Kotlin, such functions are commonly called conversion functions and typically follow the naming pattern `toTargetType()` ("to"-functions), for example: `toInt()`, `toLong()`, `toString()`, `toList()`, etc.

These conversion functions are regular functions, often implemented as extension functions, that return a value of another type. Extension functions are a mechanism frequently used to define conversions, but the concept is "conversion function", not a special keyworded language construct.

Additionally, by convention, `asTargetType()` is sometimes used for cheap or "view"-style adaptations (where no heavy copying is done, just a lightweight view over existing data). This is a library convention, not a language rule.

## Conversion Function Patterns

### 1. Built-in Conversion Functions

Kotlin's standard library provides many `toXxx()` conversion functions:

```kotlin
// Number conversions
val int = 42
val long = int.toLong()           // Int → Long
val double = int.toDouble()       // Int → Double
val string = int.toString()       // Int → String

// String conversions
val str = "123"
val num = str.toInt()             // String → Int
val numOrNull = str.toIntOrNull() // String → Int? (null if invalid)
val float = str.toFloat()         // String → Float

// Collection conversions
val list = listOf(1, 2, 3)
val set = list.toSet()            // List → Set
val array = list.toTypedArray()   // List → Array
val mutableList = list.toMutableList()  // List → MutableList
```

---

### 2. Extension Functions for Custom Conversions

You can create custom conversion extension functions:

```kotlin
// Domain models
data class User(val id: Int, val name: String, val email: String)
data class UserDto(val id: Int, val name: String)

// Extension function for conversion
fun User.toDto(): UserDto {
    return UserDto(
        id = this.id,
        name = this.name
    )
}

// Usage
val user = User(1, "Alice", "alice@example.com")
val dto = user.toDto()  // User → UserDto
```

Naming convention: use `toTargetType()` for conversions:

```kotlin
fun String.toUser(): User {
    val parts = this.split(",")
    return User(
        id = parts[0].toInt(),
        name = parts[1],
        email = parts[2]
    )
}

val userString = "1,Alice,alice@example.com"
val user = userString.toUser()
```

---

### 3. Explicit Type Conversion (Casting)

For type casting (not data conversion), Kotlin uses different operators:

```kotlin
// Safe cast (returns null if fails)
val str: String? = obj as? String

// Unsafe cast (throws exception if fails)
val strStrict: String = obj as String

// Type check
if (obj is String) {
    // obj is smart-cast to String
    println(obj.length)
}
```

Casting changes how the compiler treats the reference; it does not create a new converted value like `toXxx()` functions do.

---

## Common Conversion Patterns

### Number Conversions

```kotlin
val byte: Byte = 10
val short: Short = byte.toShort()
val int: Int = byte.toInt()
val long: Long = byte.toLong()
val float: Float = byte.toFloat()
val double: Double = byte.toDouble()

// No automatic widening in Kotlin
val x: Int = 100
// val y: Long = x  // Compilation error
val y: Long = x.toLong()  // Explicit conversion required
```

---

### `String` Conversions

```kotlin
// To String
val num = 42
val str = num.toString()        // "42"
val hex = num.toString(16)      // "2a" (hexadecimal)
val binary = num.toString(2)    // "101010" (binary)

// From String
val s = "123"
val int = s.toInt()             // 123
val long = s.toLong()           // 123L
val double = s.toDouble()       // 123.0

// Safe conversion
val invalid = "abc"
val num1 = invalid.toIntOrNull()     // null (doesn't throw)
val num2 = invalid.toInt()           // NumberFormatException
```

---

### Collection Conversions

```kotlin
// To different collection types
val list = listOf(1, 2, 3, 2, 1)
val set = list.toSet()              // [1, 2, 3] (duplicates removed)
val array = list.toTypedArray()     // Array<Int>
val intArray = list.toIntArray()    // IntArray (primitive)

// Mutability conversions
val immutableList = listOf(1, 2, 3)
val mutableList = immutableList.toMutableList()
mutableList.add(4)  // Now can modify

val mutableSet = mutableSetOf(1, 2)
val immutableSet = mutableSet.toSet()  // Immutable copy
```

---

### `Map` Conversions

```kotlin
// List to Map
val users = listOf(
    User(1, "Alice", "alice@example.com"),
    User(2, "Bob", "bob@example.com")
)

val userMap = users.associateBy { it.id }
// Map: {1=User(1, Alice, alice@example.com), 2=User(2, Bob, bob@example.com)}

// Map to List
val map = mapOf(1 to "one", 2 to "two")
val listPairs = map.toList()                 // List<Pair<Int, String>>
val entries = map.entries.toList()           // List of Map.Entry
```

---

### Custom Domain Conversions

```kotlin
// Entity to DTO
data class UserEntity(
    val id: Int,
    val firstName: String,
    val lastName: String,
    val email: String,
    val passwordHash: String
)

data class UserResponse(
    val id: Int,
    val fullName: String,
    val email: String
)

fun UserEntity.toResponse(): UserResponse {
    return UserResponse(
        id = this.id,
        fullName = "$firstName $lastName",
        email = this.email
    )
}

// Usage
val entity = UserEntity(1, "Alice", "Smith", "alice@example.com", "hash123")
val response = entity.toResponse()
```

---

### JSON Conversions (with libraries)

```kotlin
// Using kotlinx.serialization
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class User(val name: String, val age: Int)

val user = User("Alice", 30)
val json = Json.encodeToString(user)  // User → JSON String
val decodedUser = Json.decodeFromString<User>(json)  // JSON String → User
```

These are library-provided conversion functions, not built-in language-level automatic conversions.

---

## Best Practices

### 1. Use Descriptive Names

```kotlin
// GOOD - Clear intent
fun User.toDto(): UserDto
fun UserDto.toEntity(): User
fun String.toBase64(): String
fun ByteArray.toHexString(): String

// BAD - Unclear
fun User.convert(): UserDto
fun transform(user: User): UserDto
```

### 2. Null Safety with Conversions

```kotlin
// GOOD - Use xxxOrNull for safe conversions
val age = ageString.toIntOrNull() ?: 0

// RISKY - Can throw exception
val age2 = ageString.toInt()  // NumberFormatException if invalid
```

### 3. Extension Functions for Domain Conversions

```kotlin
// GOOD - Extension function
fun Order.toOrderResponse(): OrderResponse {
    return OrderResponse(/* ... */)
}

// Usage reads naturally
val responseGood = order.toOrderResponse()

// Less natural - utility function
fun convertOrderToResponse(order: Order): OrderResponse {
    return OrderResponse(/* ... */)
}

val response2 = convertOrderToResponse(order)
```

### 4. Batch Conversions

```kotlin
// Convert collections
val usersListEn: List<User> = /* ... */
val dtoListEn: List<UserDto> = usersListEn.map { it.toDto() }

// Or create extension
fun List<User>.toDtos(): List<UserDto> = map { it.toDto() }

val dtoList2En = usersListEn.toDtos()
```

---

## Summary (RU)

Функции преобразования в Kotlin:

1. Встроенные преобразования: `toInt()`, `toLong()`, `toString()`, `toList()` и т.д.
2. Кастомные функции-расширения `toXxx()` для доменных преобразований.
3. Операторы приведения `as`, `as?` для изменения типа ссылки (не преобразуют значение).

Соглашения именования:
- `toTargetType()` — для преобразований, создающих значение другого типа.
- `asTargetType()` — иногда используется для дешевых "view"-адаптаций без тяжелого копирования (зависит от библиотеки, не правило языка).

Типичные случаи использования:
- Преобразования числовых типов.
- Парсинг `String`.
- Трансформации коллекций.
- Доменные преобразования (`Entity` ↔ DTO).
- Сериализация (объект ↔ JSON/XML) через библиотеки.

Рекомендуется использовать понятные `toXxx()`-имена и функции-расширения, не путать приведение типов с преобразованием значений и не создавать ложного ощущения неявных преобразований, которых в Kotlin нет.

---

## Summary

Conversion functions in Kotlin:

1. Built-in conversions: `toInt()`, `toLong()`, `toString()`, `toList()`, etc.
2. Custom extension functions: `toXxx()` methods for domain conversions.
3. Casting operators: `as`, `as?` for type casts (not value-transforming conversions).

Naming pattern:
- `toTargetType()` for conversions that create a value in another type.
- `asTargetType()` is sometimes used by convention for "view"-style or cheap adaptations that don't perform heavy copying (library-specific, not enforced by the language).

Common uses:
- Number type conversions.
- `String` parsing.
- `Collection` transformations.
- Domain model conversions (`Entity` ↔ DTO).
- Serialization (Object ↔ JSON/XML) via libraries.

Best practice: Use clear `toXxx()` naming and extension functions where it improves readability; avoid conflating casting with data conversion or implying implicit conversions that Kotlin does not support.

---

## Дополнительные Вопросы (RU)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-property-delegates--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## Follow-ups

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-property-delegates--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## Связанные Вопросы (RU)

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-property-delegates--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

## Related Questions

- [[q-coroutine-cancellation-mechanisms--kotlin--medium]]
- [[q-kotlin-property-delegates--kotlin--medium]]
- [[q-coroutine-dispatchers--kotlin--medium]]

