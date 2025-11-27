---
id: kotlin-032
title: "map() vs flatMap() in Kotlin / map() против flatMap() в Kotlin"
aliases: ["map() vs flatMap() in Kotlin", "map() против flatMap() в Kotlin"]

# Classification
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/Kirchhoff-/Android-Interview-Questions"
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-collections, c-kotlin, q-kotlin-immutable-collections--programming-languages--easy]

# Timestamps
created: 2025-10-05
updated: 2025-11-10

tags: [collections, difficulty/medium, flatmap, higher-order-functions, kotlin, map]
date created: Sunday, October 12th 2025, 12:27:47 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> В чем разница между `map()` и `flatMap()` в Kotlin?

# Question (EN)
> What is the difference between `map()` and `flatMap()` in Kotlin?

## Ответ (RU)

### map()

`map()` возвращает новый список (или другую коллекцию того же типа, если это возможно), содержащий результаты применения заданной функции преобразования к каждому элементу исходной коллекции.

```kotlin
val numbers = listOf(1, 2, 3)
println(numbers.map { it * it })
// Вывод: [1, 4, 9]
```

### flatMap()

`flatMap()` применяет функцию преобразования к каждому элементу исходной коллекции. Эта функция должна возвращать коллекцию (Iterable) для каждого элемента. Затем `flatMap()` объединяет ("выравнивает") все полученные коллекции в один плоский список.

```kotlin
val list = listOf("123", "45")
println(list.flatMap { it.toList() })
// Вывод: [1, 2, 3, 4, 5]
```

### Ключевое Различие: Выравнивание Вложенных Коллекций

Основное различие становится ясным при работе с вложенными коллекциями. `map()` преобразует элементы и сохраняет вложенную структуру (вы получаете коллекцию коллекций), в то время как `flatMap()` сначала делает преобразование в коллекцию для каждого элемента, а затем объединяет вложенные коллекции в один плоский список.

#### Подробный Пример

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

### Когда Использовать Каждую Функцию

#### Используйте `map()` Когда:
- Вы хотите преобразовать каждый элемент, но сохранить структуру коллекции
- Каждый элемент преобразуется ровно в одно значение
- Вам не нужно выравнивать вложенные коллекции

```kotlin
val prices = listOf(100, 200, 300)
val withTax = prices.map { it * 1.2 }
// [120.0, 240.0, 360.0]

val users = listOf("alice", "bob", "charlie")
val emails = users.map { "$it@example.com" }
// [alice@example.com, bob@example.com, charlie@example.com]
```

#### Используйте `flatMap()` Когда:
- Ваша функция преобразования возвращает коллекцию для каждого элемента
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

### Визуальное Сравнение

```kotlin
val data = listOf(listOf(1, 2), listOf(3, 4))

// map - преобразует, но сохраняет структуру
val mapped = data.map { it }
// Результат: [[1, 2], [3, 4]] - всё ещё вложенный список

// flatMap - (при возвращении самой вложенной коллекции) выравнивает
val flattened = data.flatMap { it }
// Результат: [1, 2, 3, 4] - выровнен в один список
```

### Соображения Производительности

`flatMap()` выполняет те же операции преобразования, что и `map()`, но дополнительно объединяет (конкатенирует) результаты, поэтому при прочих равных имеет немного больше накладных расходов. Это не критично в большинстве случаев, но используйте `flatMap()` по назначению — когда действительно нужно выравнивание/объединение коллекций.

**Краткое содержание**: `map()` преобразует каждый элемент один-к-одному и сохраняет структуру коллекции. `flatMap()` ожидает, что каждый элемент будет преобразован в коллекцию, и выравнивает все результаты в один список. Используйте `map()` для простых преобразований, `flatMap()` — когда нужно выровнять вложенные коллекции или расширить элементы.

## Ответы На Дополнительные Вопросы (RU)

- В чем ключевые отличия реализации и использования по сравнению с Java Streams?
- В каких практических сценариях в Kotlin-коде вы чаще всего используете `flatMap()`?
- Какие типичные ошибки допускают при использовании `flatMap()` вместо `map()` и наоборот?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]

## Answer (EN)

### map()

`map()` returns a new list (or another collection of the same kind when possible) containing the results of applying the given transform function to each element in the original collection.

```kotlin
val numbers = listOf(1, 2, 3)
println(numbers.map { it * it })
// Output: [1, 4, 9]
```

### flatMap()

`flatMap()` applies the transform function to each element of the original collection. That function must return a collection (Iterable) for each element. Then `flatMap()` concatenates (flattens) all resulting collections into a single list.

```kotlin
val list = listOf("123", "45")
println(list.flatMap { it.toList() })
// Output: [1, 2, 3, 4, 5]
```

### Key Difference: Flattening Nested Collections

The main difference becomes clear when working with nested collections. With `map()`, you transform elements and keep the nested structure (you get a collection of collections). With `flatMap()`, you both transform each element into a collection and then merge those nested collections into a single flat list.

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

#### Use `map()` When:
- You want to transform each element but keep the collection structure
- Each element transforms to exactly one value
- You don't need to flatten nested collections

```kotlin
val prices = listOf(100, 200, 300)
val withTax = prices.map { it * 1.2 }
// [120.0, 240.0, 360.0]

val users = listOf("alice", "bob", "charlie")
val emails = users.map { "$it@example.com" }
// [alice@example.com, bob@example.com, charlie@example.com]
```

#### Use `flatMap()` When:
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
val mapped = data.map { it }
// Result: [[1, 2], [3, 4]] - still nested list

// flatMap - (when returning the nested collection itself) transforms AND flattens
val flattened = data.flatMap { it }
// Result: [1, 2, 3, 4] - flattened into single list
```

### Performance Consideration

`flatMap()` performs the same per-element transformation work as `map()`, but it also concatenates the resulting collections, which introduces some extra overhead. In most cases this is negligible; just use `flatMap()` when you specifically need its flattening behavior.

**English Summary**: `map()` transforms each element one-to-one and preserves collection structure. `flatMap()` expects each element to be transformed into a collection and flattens all results into a single list. Use `map()` for simple transformations, `flatMap()` when you need to flatten nested collections or expand elements.

## Follow-ups

- What are the key differences in implementation and usage compared to Java Streams?
- In which practical Kotlin code scenarios do you most often use `flatMap()`?
- What common mistakes do developers make when using `flatMap()` instead of `map()` and vice versa?

## References

- [[c-kotlin]]
- [[c-collections]]
- [map() - Kotlin Collections API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/map.html)
- [flatMap() - Kotlin Collections API](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/flat-map.html)
- [StackOverflow: Use case for flatMap vs map](https://stackoverflow.com/questions/52078207/what-is-the-use-case-for-flatmap-vs-map-in-kotlin)
- [Medium: flatMap vs map in Kotlin](https://medium.com/@sachinkmr375/flatmap-vs-map-in-kotlin-aef771a4dae4)

## Related Questions

- [[q-kotlin-collections--kotlin--medium]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]
