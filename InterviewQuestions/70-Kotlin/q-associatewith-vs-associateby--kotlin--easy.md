---
id: kotlin-140
title: Associatewith Vs Associateby / associateWith против associateBy
aliases:
- associateWith vs associateBy
- associateWith против associateBy
topic: kotlin
subtopics:
- collections
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-collections
- c-kotlin
- q-inline-function-limitations--kotlin--medium
created: 2025-10-15
updated: 2025-11-09
tags:
- collections
- difficulty/easy
- kotlin
- map
- transformation
anki_cards:
- slug: kotlin-140-0-en
  language: en
  anki_id: 1768326279154
  synced_at: '2026-01-23T17:03:50.420339'
- slug: kotlin-140-0-ru
  language: ru
  anki_id: 1768326279179
  synced_at: '2026-01-23T17:03:50.422568'
---
# Вопрос (RU)

> Разница между `associateWith()` и `associateBy()` в Kotlin при создании `Map` из коллекций.

# Question (EN)

> Difference between `associateWith()` and `associateBy()` in Kotlin when creating a `Map` from collections.

## Ответ (RU)

`associateBy()` создает `Map`, где **ключи** вычисляются из элементов, а **значениями** становятся сами элементы: упрощенно `Iterable<T>.associateBy { key } → Map<Key, T>`. `associateWith()` создает `Map`, где элементы становятся **ключами**, а **значения** вычисляются из этих ключей: упрощенно `Iterable<T>.associateWith { value } → Map<T, Value>`.

Обе функции работают с коллекциями/итерируемыми типами Kotlin (например, `Iterable<T>`, `Array<T>`, `List<T>`); ниже для простоты используется `List<T>`.

### associateBy - Элемент Становится Значением

```kotlin
data class User(val id: Int, val name: String)

val users = listOf(
    User(1, "Alice"),
    User(2, "Bob"),
    User(3, "Charlie")
)

// associateBy: key = id, value = весь User
val usersById: Map<Int, User> = users.associateBy { it.id }

println(usersById)
// {1=User(id=1, name=Alice), 2=User(id=2, name=Bob), 3=User(id=3, name=Charlie)}

println(usersById[2])  // User(id=2, name=Bob)
```

Формула (упрощенно): `Iterable<T>.associateBy { key } → Map<Key, T>`

### associateWith - Элемент Становится Ключом

```kotlin
val users = listOf("Alice", "Bob", "Charlie")

// associateWith: key = элемент, value = его длина
val nameLengths: Map<String, Int> = users.associateWith { it.length }

println(nameLengths)
// {Alice=5, Bob=3, Charlie=7}

println(nameLengths["Bob"])  // 3
```

Формула (упрощенно): `Iterable<T>.associateWith { value } → Map<T, Value>`

### Сравнение

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// associateBy: элемент остается значением, вычисляем ключ
val squareToNumber = numbers.associateBy { it * it }
println(squareToNumber)
// {1=1, 4=2, 9=3, 16=4, 25=5}
// Ключ: квадрат, Значение: число

// associateWith: элемент становится ключом, вычисляем значение
val numberToSquare = numbers.associateWith { it * it }
println(numberToSquare)
// {1=1, 2=4, 3=9, 4=16, 5=25}
// Ключ: число, Значение: квадрат
```

### associateBy С Двумя Параметрами

Можно задать отдельно и ключ, и значение:

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = listOf(
    Product(1, "Laptop", 1200.0),
    Product(2, "Mouse", 25.0),
    Product(3, "Keyboard", 75.0)
)

// key = id, value = name
val productNames: Map<Int, String> = products.associateBy(
    keySelector = { it.id },
    valueTransform = { it.name }
)

println(productNames)
// {1=Laptop, 2=Mouse, 3=Keyboard}

println(productNames[1])  // "Laptop"
```

### Практические Примеры

#### Пример 1: Кэш Объектов По ID

```kotlin
data class Article(val id: Int, val title: String, val content: String)

class ArticleRepository {
    private val articles = listOf(
        Article(1, "Kotlin Basics", "Content 1"),
        Article(2, "Android Guide", "Content 2"),
        Article(3, "Compose Tutorial", "Content 3")
    )

    // Быстрый поиск по ID через Map
    private val articlesById = articles.associateBy { it.id }

    fun getArticle(id: Int): Article? {
        return articlesById[id]  // ожидаемый O(1) в среднем для HashMap
    }
}
```

#### Пример 2: Индексация Строк

```kotlin
val words = listOf("apple", "banana", "cherry", "apricot", "blueberry")

// Индексация по первой букве: сохраняется только последнее слово для каждой буквы
val wordsByFirstLetter = words.associateBy { it.first() }
println(wordsByFirstLetter)
// {a=apricot, b=blueberry, c=cherry}
// ВАЖНО: сохраняется только последнее значение для ключа, предыдущие перезаписываются.

// Если нужно сохранить все слова по букве, используйте groupBy
val groupedByFirstLetter = words.groupBy { it.first() }
println(groupedByFirstLetter)
// {a=[apple, apricot], b=[banana, blueberry], c=[cherry]}
```

#### Пример 3: Настройки С Значениями По Умолчанию

```kotlin
enum class Setting { THEME, LANGUAGE, FONT_SIZE }

// associateWith для значений по умолчанию
val defaultSettings = Setting.values().associateWith { setting ->
    when (setting) {
        Setting.THEME -> "Dark"
        Setting.LANGUAGE -> "English"
        Setting.FONT_SIZE -> "Medium"
    }
}

println(defaultSettings)
// {THEME=Dark, LANGUAGE=English, FONT_SIZE=Medium}

// Использование
fun getSetting(key: Setting): String {
    return defaultSettings[key] ?: "Unknown"
}
```

#### Пример 4: Кэширование Вычислений

```kotlin
fun fibonacci(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// Создаем кэш для первых 20 чисел Фибоначчи
val fibCache = (0..20).associateWith { fibonacci(it) }

println(fibCache)
// {0=0, 1=1, 2=1, 3=2, 4=3, 5=5, ..., 20=6765}

// Быстрый доступ; для значений вне кэша — прямой расчет
fun getFib(n: Int): Long = fibCache[n] ?: fibonacci(n)
```

### Коллизии Ключей

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Alice", 28)  // Дубликат имени!
)

// associateBy: при коллизии побеждает последний элемент
val peopleByName = people.associateBy { it.name }
println(peopleByName)
// {Alice=Person(name=Alice, age=28), Bob=Person(name=Bob, age=30)}
// Alice(25) была перезаписана Alice(28)!

// Если нужно сохранить всех — используйте groupBy
val groupedByName = people.groupBy { it.name }
println(groupedByName)
// {Alice=[Person(name=Alice, age=25), Person(name=Alice, age=28)], Bob=[Person(name=Bob, age=30)]}
```

### Associate - Максимальная Гибкость

Создает и ключ, и значение через `Pair`:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Создаем Map: число → строка с квадратом
val numberMap = numbers.associate { n ->
    n to "Number $n squared is ${n * n}"
}

println(numberMap)
// {1=Number 1 squared is 1, 2=Number 2 squared is 4, ...}
```

Эквивалентные шаблоны:
- `associateBy { key }` ≈ `associate { element -> key(element) to element }`
- `associateWith { value }` ≈ `associate { element -> element to value(element) }`

### Таблица Сравнения

| Function | Key | Value | Formula | Use Case |
|---------|------|----------|---------|----------|
| **associateBy** | Вычисляется | Элемент | `Map<Key, T>` | Индексация объектов по ID |
| **associateWith** | Элемент | Вычисляется | `Map<T, Value>` | Маппинг элементов на их свойства |
| **associate** | Вычисляется | Вычисляется | `Map<Key, Value>` | Полная трансформация через `Pair` |
| **groupBy** | Вычисляется | `List<T>` | `Map<Key, List<T>>` | Группировка с сохранением дубликатов |

### Производительность

```kotlin
val largeList = (1..1_000_000).toList()

// associateBy/associateWith - O(n) по времени, O(n) по памяти
val map = largeList.associateWith { it * 2 }

// Доступ по ключу в Map - ожидаемый O(1) в среднем для HashMap
map[50_000]

// Линейный поиск в списке - O(n)
largeList.find { it == 50_000 }
```

### Рекомендации

1. Используйте `associateBy` для быстрого поиска по ключу:

```kotlin
// Правильно: один раз строим индекс, затем O(1) доступы
val usersById = users.associateBy { it.id }
val user = usersById[userId]

// Менее эффективно для повторяющихся поисков: каждый раз O(n)
val userSlow = users.find { it.id == userId }
```

1. Используйте `associateWith` для конфигураций и значений по умолчанию:

```kotlin
val permissions = listOf("READ", "WRITE", "DELETE")
    .associateWith { false }  // все по умолчанию false

// {READ=false, WRITE=false, DELETE=false}
```

1. Учитывайте коллизии ключей:

```kotlin
// Если возможны дубликаты — используйте groupBy
val itemsByCategory = items.groupBy { it.category }

// Если ключи уникальны по дизайну — associateBy
val itemsById = items.associateBy { it.id }
```

Кратко: `associateBy` — когда ключ считается из элемента, а значение — сам элемент; `associateWith` — когда элемент используется как ключ, а значение вычисляется; `associate` — когда нужно полностью контролировать и ключ, и значение.

## Answer (EN)

`associateBy()` creates a `Map` where **keys** are computed from elements, and **values** are the original elements: simplified `Iterable<T>.associateBy { key } → Map<Key, T>`. `associateWith()` creates a `Map` where elements become **keys**, and **values** are computed from those keys: simplified `Iterable<T>.associateWith { value } → Map<T, Value>`.

Both work on Kotlin collections/iterables (e.g. `Iterable<T>`, `Array<T>`, `List<T>`); `List<T>` below is used just for simplicity.

### associateBy - Element Becomes Value

```kotlin
data class User(val id: Int, val name: String)

val users = listOf(
    User(1, "Alice"),
    User(2, "Bob"),
    User(3, "Charlie")
)

// associateBy: key = id, value = entire User
val usersById: Map<Int, User> = users.associateBy { it.id }

println(usersById)
// {1=User(id=1, name=Alice), 2=User(id=2, name=Bob), 3=User(id=3, name=Charlie)}

println(usersById[2])  // User(id=2, name=Bob)
```

Formula (simplified): `Iterable<T>.associateBy { key } → Map<Key, T>`

### associateWith - Element Becomes Key

```kotlin
val users = listOf("Alice", "Bob", "Charlie")

// associateWith: key = element, value = its length
val nameLengths: Map<String, Int> = users.associateWith { it.length }

println(nameLengths)
// {Alice=5, Bob=3, Charlie=7}

println(nameLengths["Bob"])  // 3
```

Formula (simplified): `Iterable<T>.associateWith { value } → Map<T, Value>`

### Comparison

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// associateBy: element stays as value, we compute the key
val squareToNumber = numbers.associateBy { it * it }
println(squareToNumber)
// {1=1, 4=2, 9=3, 16=4, 25=5}
// Key: square, Value: number

// associateWith: element becomes key, we compute the value
val numberToSquare = numbers.associateWith { it * it }
println(numberToSquare)
// {1=1, 2=4, 3=9, 4=16, 5=25}
// Key: number, Value: square
```

### associateBy with Two Parameters

You can specify both key and value separately:

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = listOf(
    Product(1, "Laptop", 1200.0),
    Product(2, "Mouse", 25.0),
    Product(3, "Keyboard", 75.0)
)

// key = id, value = name
val productNames: Map<Int, String> = products.associateBy(
    keySelector = { it.id },
    valueTransform = { it.name }
)

println(productNames)
// {1=Laptop, 2=Mouse, 3=Keyboard}

println(productNames[1])  // "Laptop"
```

### Practical Examples

#### Example 1: Object Cache by ID

```kotlin
data class Article(val id: Int, val title: String, val content: String)

class ArticleRepository {
    private val articles = listOf(
        Article(1, "Kotlin Basics", "Content 1"),
        Article(2, "Android Guide", "Content 2"),
        Article(3, "Compose Tutorial", "Content 3")
    )

    // Fast lookup by ID via Map
    private val articlesById = articles.associateBy { it.id }

    fun getArticle(id: Int): Article? {
        return articlesById[id]  // expected O(1) average for HashMap
    }
}
```

#### Example 2: String Indexing

```kotlin
val words = listOf("apple", "banana", "cherry", "apricot", "blueberry")

// Indexing by first letter: only the last word for each letter is kept
val wordsByFirstLetter = words.associateBy { it.first() }
println(wordsByFirstLetter)
// {a=apricot, b=blueberry, c=cherry}
// WARNING: Only the last value for each key is stored; previous ones are overwritten.

// If you need to keep all words per letter, use groupBy
val groupedByFirstLetter = words.groupBy { it.first() }
println(groupedByFirstLetter)
// {a=[apple, apricot], b=[banana, blueberry], c=[cherry]}
```

#### Example 3: Settings with Default Values

```kotlin
enum class Setting { THEME, LANGUAGE, FONT_SIZE }

// associateWith for default values
val defaultSettings = Setting.values().associateWith { setting ->
    when (setting) {
        Setting.THEME -> "Dark"
        Setting.LANGUAGE -> "English"
        Setting.FONT_SIZE -> "Medium"
    }
}

println(defaultSettings)
// {THEME=Dark, LANGUAGE=English, FONT_SIZE=Medium}

// Usage
fun getSetting(key: Setting): String {
    return defaultSettings[key] ?: "Unknown"
}
```

#### Example 4: Computation Caching

```kotlin
fun fibonacci(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// Create cache for the first 20 Fibonacci numbers
val fibCache = (0..20).associateWith { fibonacci(it) }

println(fibCache)
// {0=0, 1=1, 2=1, 3=2, 4=3, 5=5, ..., 20=6765}

// Fast access; falls back to direct computation for values outside cache
fun getFib(n: Int): Long = fibCache[n] ?: fibonacci(n)
```

### Key Collisions

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Alice", 28)  // Duplicate name!
)

// associateBy: last one wins when keys collide
val peopleByName = people.associateBy { it.name }
println(peopleByName)
// {Alice=Person(name=Alice, age=28), Bob=Person(name=Bob, age=30)}
// Alice(25) was overwritten by Alice(28)!

// If you need to keep all - use groupBy
val groupedByName = people.groupBy { it.name }
println(groupedByName)
// {Alice=[Person(name=Alice, age=25), Person(name=Alice, age=28)], Bob=[Person(name=Bob, age=30)]}
```

### Associate - Maximum Flexibility

Creates both key and value via `Pair`:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Create Map: number → string + square
val numberMap = numbers.associate { n ->
    n to "Number $n squared is ${n * n}"
}

println(numberMap)
// {1=Number 1 squared is 1, 2=Number 2 squared is 4, ...}
```

Equivalent patterns:
- `associateBy { key }` ≈ `associate { element -> key(element) to element }`
- `associateWith { value }` ≈ `associate { element -> element to value(element) }`

### Comparison Table

| Function | Key | Value | Formula | Use Case |
|---------|------|----------|---------|----------|
| **associateBy** | Computed | Element | `Map<Key, T>` | Indexing objects by ID |
| **associateWith** | Element | Computed | `Map<T, Value>` | Mapping elements to their properties |
| **associate** | Computed | Computed | `Map<Key, Value>` | Full transformation via `Pair` |
| **groupBy** | Computed | `List<T>` | `Map<Key, List<T>>` | Grouping while keeping duplicates |

### Performance

```kotlin
val largeList = (1..1_000_000).toList()

// associateBy/associateWith - O(n) time, O(n) additional memory
val map = largeList.associateWith { it * 2 }

// Map lookup - expected O(1) average for hash-based map
map[50_000]

// Linear search in list - O(n)
largeList.find { it == 50_000 }
```

### Best Practices

1. Use `associateBy` for fast key lookup

```kotlin
// Correct: build index once, then O(1) lookups
val usersById = users.associateBy { it.id }
val user = usersById[userId]

// Less efficient for repeated lookups: O(n) each time
val userSlow = users.find { it.id == userId }
```

1. Use `associateWith` for creating configurations

```kotlin
val permissions = listOf("READ", "WRITE", "DELETE")
    .associateWith { false }  // All default to false

// {READ=false, WRITE=false, DELETE=false}
```

1. Account for key collisions

```kotlin
// If duplicates are possible - use groupBy
val itemsByCategory = items.groupBy { it.category }

// If keys are unique (by design) - associateBy
val itemsById = items.associateBy { it.id }
```

In short: `associateBy` when key is derived and value is the element; `associateWith` when element is key and value is derived; `associate` for full control.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-kotlin-reflection--kotlin--medium]]
