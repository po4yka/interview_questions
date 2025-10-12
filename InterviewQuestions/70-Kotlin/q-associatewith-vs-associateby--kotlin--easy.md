---
topic: kotlin
tags:
  - kotlin
  - collections
  - map
  - transformation
difficulty: easy
status: draft
---

# associateWith() vs associateBy(): создание Map из коллекций

**English**: Difference between associateWith() and associateBy()

## Answer (EN)
`associateBy()` создает `Map`, где **ключи** вычисляются из элементов, а **значениями** становятся сами элементы. `associateWith()` делает наоборот — элементы становятся **ключами**, а **значения** вычисляются.

### associateBy — элемент становится значением

```kotlin
data class User(val id: Int, val name: String)

val users = listOf(
    User(1, "Alice"),
    User(2, "Bob"),
    User(3, "Charlie")
)

// associateBy: ключ = id, значение = весь User
val usersById: Map<Int, User> = users.associateBy { it.id }

println(usersById)
// {1=User(id=1, name=Alice), 2=User(id=2, name=Bob), 3=User(id=3, name=Charlie)}

println(usersById[2])  // User(id=2, name=Bob)
```

**Формула**: `List<T>.associateBy { key } → Map<Key, T>`

### associateWith — элемент становится ключом

```kotlin
val users = listOf("Alice", "Bob", "Charlie")

// associateWith: ключ = имя, значение = длина
val nameLengths: Map<String, Int> = users.associateWith { it.length }

println(nameLengths)
// {Alice=5, Bob=3, Charlie=7}

println(nameLengths["Bob"])  // 3
```

**Формула**: `List<T>.associateWith { value } → Map<T, Value>`

### Сравнение

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// associateBy: элемент → значение, вычисляем ключ
val squareToNumber = numbers.associateBy { it * it }
println(squareToNumber)
// {1=1, 4=2, 9=3, 16=4, 25=5}
// Ключ: квадрат, Значение: число

// associateWith: элемент → ключ, вычисляем значение
val numberToSquare = numbers.associateWith { it * it }
println(numberToSquare)
// {1=1, 2=4, 3=9, 4=16, 5=25}
// Ключ: число, Значение: квадрат
```

### associateBy с двумя параметрами

Можно указать и ключ, и значение отдельно:

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = listOf(
    Product(1, "Laptop", 1200.0),
    Product(2, "Mouse", 25.0),
    Product(3, "Keyboard", 75.0)
)

// Ключ = id, Значение = name
val productNames: Map<Int, String> = products.associateBy(
    keySelector = { it.id },
    valueTransform = { it.name }
)

println(productNames)
// {1=Laptop, 2=Mouse, 3=Keyboard}

println(productNames[1])  // "Laptop"
```

### Практические примеры

#### Пример 1: Кэш объектов по ID

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
        return articlesById[id]  // O(1) вместо O(n)
    }
}
```

#### Пример 2: Индексация строк

```kotlin
val words = listOf("apple", "banana", "cherry", "apricot", "blueberry")

// Группировка по первой букве
val wordsByFirstLetter = words.associateBy { it.first() }
println(wordsByFirstLetter)
// {a=apricot, b=blueberry, c=cherry}
// WARNING: Последнее значение выигрывает при коллизии!

// Альтернатива с groupBy (сохраняет все)
val groupedByFirstLetter = words.groupBy { it.first() }
println(groupedByFirstLetter)
// {a=[apple, apricot], b=[banana, blueberry], c=[cherry]}
```

#### Пример 3: Настройки с дефолтными значениями

```kotlin
enum class Setting { THEME, LANGUAGE, FONT_SIZE }

// associateWith для дефолтных значений
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

#### Пример 4: Кэширование вычислений

```kotlin
fun fibonacci(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// Создаем кэш для первых 20 чисел Фибоначчи
val fibCache = (0..20).associateWith { fibonacci(it) }

println(fibCache)
// {0=0, 1=1, 2=1, 3=2, 4=3, 5=5, ..., 20=6765}

// Быстрый доступ
fun getFib(n: Int): Long = fibCache[n] ?: fibonacci(n)
```

### Коллизии ключей

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(
    Person("Alice", 25),
    Person("Bob", 30),
    Person("Alice", 28)  // Дубликат имени!
)

// associateBy: последний выигрывает
val peopleByName = people.associateBy { it.name }
println(peopleByName)
// {Alice=Person(name=Alice, age=28), Bob=Person(name=Bob, age=30)}
// Alice(25) была перезаписана Alice(28)!

// Если нужно сохранить все - используйте groupBy
val groupedByName = people.groupBy { it.name }
println(groupedByName)
// {Alice=[Person(Alice, 25), Person(Alice, 28)], Bob=[Person(Bob, 30)]}
```

### associate — максимальная гибкость

Создает и ключ, и значение через `Pair`:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Создаем Map: число → строка + квадрат
val numberMap = numbers.associate { n ->
    n to "Number $n squared is ${n * n}"
}

println(numberMap)
// {1=Number 1 squared is 1, 2=Number 2 squared is 4, ...}
```

Эквивалентно:
- `associateBy { key }` = `associate { it -> key(it) to it }`
- `associateWith { value }` = `associate { it -> it to value(it) }`

### Сравнительная таблица

| Функция | Ключ | Значение | Формула | Use Case |
|---------|------|----------|---------|----------|
| **associateBy** | Вычисляется | Элемент | `Map<Key, T>` | Индексация объектов по ID |
| **associateWith** | Элемент | Вычисляется | `Map<T, Value>` | Свойства элементов |
| **associate** | Вычисляется | Вычисляется | `Map<Key, Value>` | Полная трансформация |
| **groupBy** | Вычисляется | `List<T>` | `Map<Key, List<T>>` | Группировка с дубликатами |

### Performance

```kotlin
val largeList = (1..1_000_000).toList()

// associateBy/associateWith - O(n) времени, O(n) памяти
val map = largeList.associateWith { it * 2 }  // ~200ms, ~80MB

// Поиск в Map - O(1)
map[50000]  // <1ms

// Поиск в List - O(n)
largeList.find { it == 50000 }  // ~10ms
```

### Best Practices

**1. Используйте associateBy для быстрого доступа по ключу**

```kotlin
// - ПРАВИЛЬНО
val usersById = users.associateBy { it.id }
val user = usersById[userId]  // O(1)

// - НЕПРАВИЛЬНО
val user = users.find { it.id == userId }  // O(n)
```

**2. Используйте associateWith для создания конфигураций**

```kotlin
// - ПРАВИЛЬНО
val permissions = listOf("READ", "WRITE", "DELETE")
    .associateWith { false }  // Все по умолчанию false

// {READ=false, WRITE=false, DELETE=false}
```

**3. Учитывайте коллизии ключей**

```kotlin
// Если возможны дубликаты - используйте groupBy
val itemsByCategory = items.groupBy { it.category }

// Если дубликаты невозможны - associateBy
val itemsById = items.associateBy { it.id }
```

**English**: `associateBy()` creates `Map` where **keys** are computed from elements, **values** are elements themselves: `List<T>.associateBy { key } → Map<Key, T>`. `associateWith()` does opposite - elements become **keys**, **values** are computed: `List<T>.associateWith { value } → Map<T, Value>`. `associateBy` useful for indexing objects by ID (fast O(1) lookup). `associateWith` useful for mapping elements to their properties. On key collision, last value wins. Use `groupBy` to keep all values. `associate` for full flexibility with Pair creation.

