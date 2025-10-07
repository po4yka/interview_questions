---
id: 20251005-234502
title: "map() vs flatMap() in Kotlin / map() против flatMap() в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [collections, map, flatmap, higher-order-functions, transformations]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-/Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: reviewed
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [kotlin, collections, map, flatmap, higher-order-functions, difficulty/medium]
---
## Question (EN)
> What is the difference between map() and flatMap() in Kotlin?
## Вопрос (RU)
> В чем разница между map() и flatMap() в Kotlin?

---

## Answer (EN)

### map()

`map()` returns a list containing the results of applying the given transform function to each element in the original array.

```kotlin
val numbers = listOf(1, 2, 3)
println(numbers.map { it * it })
// Output: [1, 4, 9]
```

### flatMap()

`flatMap()` returns a single list of all elements yielded from results of transform function being invoked on each element of original array.

```kotlin
val list = listOf("123", "45")
println(list.flatMap { it.toList() })
// Output: [1, 2, 3, 4, 5]
```

### Key Difference: Flattening Nested Collections

The main difference becomes clear when working with nested collections. `flatMap()` merges nested collections into a single flat list, while `map()` preserves the nested structure.

#### Detailed Example

Consider this example with teams and players:

```kotlin
// Create Player class
data class Player(val name: String)

// Create Team class with list of players
data class Team(val players: List<Player>)

fun main() {
    val tournament = listOf(
        Team(listOf(
            Player("Team1 first player"),
            Player("Team1 second player")
        )),
        Team(listOf(
            Player("Team2 first player"),
            Player("Team2 second player")
        ))
    )

    // flatMap - flattens the nested structure
    val flatMapResult = tournament.flatMap { it.players }
    println(flatMapResult)

    // map - preserves the nested structure
    val mapResult = tournament.map { it.players }
    println(mapResult)
}
```

**Output:**

```kotlin
// flatMap result - single flat list of all players
[Player(name=Team1 first player), Player(name=Team1 second player),
 Player(name=Team2 first player), Player(name=Team2 second player)]

// map result - list of lists (nested structure preserved)
[[Player(name=Team1 first player), Player(name=Team1 second player)],
 [Player(name=Team2 first player), Player(name=Team2 second player)]]
```

### When to Use Each

#### Use map() when:
- You want to transform each element but keep the same structure
- Each element transforms to exactly one result
- You don't need to flatten nested collections

```kotlin
val prices = listOf(100, 200, 300)
val withTax = prices.map { it * 1.2 }
// [120.0, 240.0, 360.0]

val users = listOf("alice", "bob", "charlie")
val emails = users.map { "$it@example.com" }
// [alice@example.com, bob@example.com, charlie@example.com]
```

#### Use flatMap() when:
- Your transform returns a collection for each element
- You want to flatten nested collections into a single list
- You need to "expand" elements (one element becomes multiple)

```kotlin
// Each word becomes a list of characters, then flattened
val words = listOf("hi", "bye")
val chars = words.flatMap { it.toList() }
// [h, i, b, y, e]

// Each range expands to multiple numbers
val ranges = listOf(1..3, 5..7)
val numbers = ranges.flatMap { it.toList() }
// [1, 2, 3, 5, 6, 7]

// Get all tags from all posts (flattened)
data class Post(val tags: List<String>)
val posts = listOf(
    Post(listOf("kotlin", "android")),
    Post(listOf("java", "kotlin"))
)
val allTags = posts.flatMap { it.tags }
// [kotlin, android, java, kotlin]
```

### Visual Comparison

```kotlin
val data = listOf(listOf(1, 2), listOf(3, 4))

// map - transforms but keeps structure
data.map { it }
// Result: [[1, 2], [3, 4]] - still nested

// flatMap - transforms AND flattens
data.flatMap { it }
// Result: [1, 2, 3, 4] - flattened into single list
```

### Performance Consideration

`flatMap()` has slightly more overhead than `map()` because it needs to flatten the results. Only use it when you actually need the flattening behavior.

**English Summary**: `map()` transforms each element one-to-one and preserves collection structure. `flatMap()` transforms each element to a collection and then flattens all results into a single list. Use `map()` for simple transformations, `flatMap()` when you need to flatten nested collections or expand elements.

## Ответ (RU)

### map()

`map()` возвращает список, содержащий результаты применения заданной функции преобразования к каждому элементу в исходном массиве.

```kotlin
val numbers = listOf(1, 2, 3)
println(numbers.map { it * it })
// Вывод: [1, 4, 9]
```

### flatMap()

`flatMap()` возвращает единый список всех элементов, полученных из результатов вызова функции преобразования для каждого элемента исходного массива.

```kotlin
val list = listOf("123", "45")
println(list.flatMap { it.toList() })
// Вывод: [1, 2, 3, 4, 5]
```

### Ключевое различие: Выравнивание вложенных коллекций

Основное различие становится ясным при работе с вложенными коллекциями. `flatMap()` объединяет вложенные коллекции в один плоский список, в то время как `map()` сохраняет вложенную структуру.

#### Подробный пример

Рассмотрим этот пример с командами и игроками:

```kotlin
// Создаём класс Player
data class Player(val name: String)

// Создаём класс Team со списком игроков
data class Team(val players: List<Player>)

fun main() {
    val tournament = listOf(
        Team(listOf(
            Player("Team1 first player"),
            Player("Team1 second player")
        )),
        Team(listOf(
            Player("Team2 first player"),
            Player("Team2 second player")
        ))
    )

    // flatMap - выравнивает вложенную структуру
    val flatMapResult = tournament.flatMap { it.players }
    println(flatMapResult)

    // map - сохраняет вложенную структуру
    val mapResult = tournament.map { it.players }
    println(mapResult)
}
```

**Вывод:**

```kotlin
// Результат flatMap - один плоский список всех игроков
[Player(name=Team1 first player), Player(name=Team1 second player),
 Player(name=Team2 first player), Player(name=Team2 second player)]

// Результат map - список списков (вложенная структура сохранена)
[[Player(name=Team1 first player), Player(name=Team1 second player)],
 [Player(name=Team2 first player), Player(name=Team2 second player)]]
```

### Когда использовать каждую функцию

#### Используйте map() когда:
- Вы хотите преобразовать каждый элемент, но сохранить ту же структуру
- Каждый элемент преобразуется ровно в один результат
- Вам не нужно выравнивать вложенные коллекции

```kotlin
val prices = listOf(100, 200, 300)
val withTax = prices.map { it * 1.2 }
// [120.0, 240.0, 360.0]

val users = listOf("alice", "bob", "charlie")
val emails = users.map { "$it@example.com" }
// [alice@example.com, bob@example.com, charlie@example.com]
```

#### Используйте flatMap() когда:
- Ваше преобразование возвращает коллекцию для каждого элемента
- Вы хотите выровнять вложенные коллекции в один список
- Вам нужно "расширить" элементы (один элемент становится несколькими)

```kotlin
// Каждое слово становится списком символов, затем выравнивается
val words = listOf("hi", "bye")
val chars = words.flatMap { it.toList() }
// [h, i, b, y, e]

// Каждый диапазон расширяется до нескольких чисел
val ranges = listOf(1..3, 5..7)
val numbers = ranges.flatMap { it.toList() }
// [1, 2, 3, 5, 6, 7]

// Получить все теги из всех постов (выровненные)
data class Post(val tags: List<String>)
val posts = listOf(
    Post(listOf("kotlin", "android")),
    Post(listOf("java", "kotlin"))
)
val allTags = posts.flatMap { it.tags }
// [kotlin, android, java, kotlin]
```

### Визуальное сравнение

```kotlin
val data = listOf(listOf(1, 2), listOf(3, 4))

// map - преобразует, но сохраняет структуру
data.map { it }
// Результат: [[1, 2], [3, 4]] - всё ещё вложенный

// flatMap - преобразует И выравнивает
data.flatMap { it }
// Результат: [1, 2, 3, 4] - выровнен в один список
```

### Соображения производительности

`flatMap()` имеет немного больше накладных расходов, чем `map()`, потому что ему нужно выравнивать результаты. Используйте его только тогда, когда вам действительно нужно поведение выравнивания.

**Краткое содержание**: `map()` преобразует каждый элемент один-к-одному и сохраняет структуру коллекции. `flatMap()` преобразует каждый элемент в коллекцию, а затем выравнивает все результаты в один список. Используйте `map()` для простых преобразований, `flatMap()` когда нужно выровнять вложенные коллекции или расширить элементы.

---

## References
- [map() - Kotlin Collections API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/map.html)
- [flatMap() - Kotlin Collections API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/flat-map.html)
- [StackOverflow: Use case for flatMap vs map](https://stackoverflow.com/questions/52078207/what-is-the-use-case-for-flatmap-vs-map-in-kotlin)
- [Medium: flatMap vs map in Kotlin](https://medium.com/@sachinkmr375/flatmap-vs-map-in-kotlin-aef771a4dae4)

## Related Questions
- [[q-kotlin-collections--kotlin--medium]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
