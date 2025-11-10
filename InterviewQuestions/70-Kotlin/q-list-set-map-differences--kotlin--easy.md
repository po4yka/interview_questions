---
id: kotlin-175
title: "List Set Map Differences / Различия List Set и Map"
aliases: [Collection Types, Collections, List vs Set vs Map, Коллекции]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, c-kotlin, q-dispatchers-unconfined--kotlin--medium, q-kotlin-object-companion-object--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, difficulty/easy, kotlin, list, map, set]
---

# Вопрос (RU)
> Расскажите отличия между `List`, `Set` и `Map`. Когда использовать каждый из них?

---

# Question (EN)
> Explain the differences between `List`, `Set`, and `Map`. When should you use each?

## Ответ (RU)

В Kotlin есть три основных типа коллекций с различными характеристиками ([[c-collections]], [[c-kotlin]]):

### List — Упорядоченный Список

**Характеристики:**
- Элементы упорядочены (индексированный доступ)
- Допускаются дубликаты
- Доступ по индексу обычно O(1) для стандартной реализации `ArrayList`
- Сохраняет порядок добавления (для `List` на базе массива / `ArrayList`)

**Когда использовать:**
- Когда важен порядок элементов
- Когда нужен доступ по индексу
- Когда дубликаты допустимы
- Для последовательной обработки данных

**Пример:**
```kotlin
val tasks = listOf("Write code", "Test", "Deploy", "Write code")
println(tasks[0])      // "Write code"
println(tasks.size)    // 4 (дубликаты сохраняются)
```

### Set — Множество Уникальных Элементов

**Характеристики:**
- Элементы уникальны (повторные значения не сохраняются)
- Порядок не гарантирован для общего `Set` (детерминированный порядок, совпадающий с порядком добавления, обеспечивается, например, `LinkedHashSet`)
- Быстрая проверка наличия элемента обычно O(1) для `HashSet`
- Нет доступа по индексу

**Когда использовать:**
- Когда нужна уникальность элементов
- Для быстрой проверки наличия элемента
- Для удаления дубликатов из списка
- Для операций над множествами (объединение, пересечение)

**Пример:**
```kotlin
val uniqueIds = setOf(1, 2, 3, 2, 1)
println(uniqueIds)      // [1, 2, 3] - повторные значения не сохраняются
println(2 in uniqueIds) // true - быстрая проверка

// Удаление дубликатов из списка
val list = listOf(1, 2, 2, 3, 3, 3)
val unique = list.toSet()  // [1, 2, 3]
```

### Map — Коллекция Пар "ключ-значение"

**Характеристики:**
- Каждый ключ уникален
- Каждому ключу соответствует одно значение (последнее присвоенное значению по ключу заменяет предыдущие)
- Быстрый доступ по ключу обычно O(1) для `HashMap`
- Множество ключей образует `Set`, значения могут повторяться
- Общий контракт `Map` не гарантирует порядок; конкретные реализации (например, `LinkedHashMap`, отсортированные карты) могут его задавать

**Когда использовать:**
- Когда нужно связать данные (ключ → значение)
- Для быстрого поиска по ключу
- Для хранения конфигураций, настроек
- Для кэширования данных
- Для подсчета частоты элементов

**Пример:**
```kotlin
// Справочник возрастов
val ages = mapOf(
    "Alice" to 25,
    "Bob" to 30,
    "Charlie" to 25  // значения могут повторяться
)
println(ages["Alice"])  // 25 - быстрый доступ по ключу

// Подсчет частоты слов
val words = listOf("cat", "dog", "cat", "bird", "dog", "cat")
val frequency = words.groupingBy { it }.eachCount()
// {cat=3, dog=2, bird=1}
```

### Сравнительная Таблица

| Характеристика      | List                                | Set                                                | Map                                                                 |
|---------------------|-------------------------------------|----------------------------------------------------|---------------------------------------------------------------------|
| Дубликаты           | Разрешены                           | Запрещены (повторы не сохраняются)                 | Ключи уникальны, значения могут повторяться                         |
| Порядок             | Сохраняется (для стандартных List) | Не гарантирован общим контрактом Set               | Не гарантирован общим контрактом Map (зависит от реализации)        |
| Доступ по индексу   | Да                                  | Нет                                                | Нет (доступ по ключу)                                               |
| Проверка наличия    | O(n) при линейном поиске            | Обычно O(1) для `HashSet`                          | Обычно O(1) для `HashMap` при доступе по ключу                      |
| Главное применение  | Упорядоченные данные                | Уникальность и быстрое членство                    | Ассоциации ключ-значение, быстрый поиск по ключу                    |

### Примеры Использования

```kotlin
// List - задачи в порядке выполнения
val todoList = mutableListOf("Buy milk", "Write code", "Buy milk")
println(todoList)  // [Buy milk, Write code, Buy milk] - порядок и дубликаты

// Set - уникальные теги
val tags = mutableSetOf("kotlin", "android", "kotlin", "java")
println(tags)  // [kotlin, android, java] - только уникальные значения, порядок реализации-зависим

// Map - конфигурация приложения
val config = mapOf(
    "api_url" to "https://api.example.com",
    "timeout" to "30",
    "retries" to "3"
)
println(config["timeout"])  // "30"
```

### Mutable Vs Immutable

```kotlin
// Read-only views (immutable интерфейсы коллекций)
val list = listOf(1, 2, 3)          // List<Int>
val set = setOf("a", "b", "c")      // Set<String>
val map = mapOf(1 to "one")         // Map<Int, String>

// Mutable коллекции
val mutableList = mutableListOf(1, 2, 3)      // MutableList<Int>
mutableList.add(4)

val mutableSet = mutableSetOf("a", "b")       // MutableSet<String>
mutableSet.add("c")

val mutableMap = mutableMapOf(1 to "one")     // MutableMap<Int, String>
mutableMap[2] = "two"
```

### Реальные Примеры

```kotlin
// 1. List - история действий пользователя
val userActions = mutableListOf<String>()
userActions.add("Opened app")
userActions.add("Clicked button")
userActions.add("Opened app")  // дубликат допустим
println(userActions)  // показывает последовательность действий

// 2. Set - уникальные посетители
val visitors = mutableSetOf<String>()
visitors.add("user123")
visitors.add("user456")
visitors.add("user123")  // повтор добавляемого значения не меняет множество
println("Unique visitors: ${visitors.size}")  // 2

// 3. Map - кэш данных
val cache = mutableMapOf<String, Data>()
val userId = "user123"
val data = cache[userId] ?: fetchData(userId).also { cache[userId] = it }
```

### Когда Что Использовать - Краткая Памятка

**Используйте `List`, если:**
- Важен порядок элементов
- Нужен доступ по индексу
- Дубликаты допустимы и важны

**Используйте `Set`, если:**
- Нужна гарантия уникальности
- Часто проверяете наличие элемента
- Порядок не важен (или используете конкретную реализацию с нужным порядком)
- Нужно удалить дубликаты

**Используйте `Map`, если:**
- Нужно связать ключи со значениями
- Часто ищете данные по ключу
- Строите справочники, словари, кэши
- Подсчитываете частоту элементов

## Answer (EN)

Kotlin has three main collection types with distinct characteristics ([[c-collections]], [[c-kotlin]]):

### List — Ordered list

- Elements are ordered and index-based.
- Duplicates are allowed.
- Index access is typically O(1) for the standard `ArrayList` implementation.
- Standard list implementations (like `ArrayList`) preserve insertion order.

Use `List` when:
- Order matters.
- You need index-based access.
- Duplicates are allowed and may be meaningful.

**Example:**
```kotlin
val tasks = listOf("Write code", "Test", "Deploy", "Write code")
println(tasks[0])      // "Write code"
println(tasks.size)    // 4 (duplicates are preserved)
```

### Set — Collection of unique elements

- Elements are unique (repeated values are not stored).
- Order is not guaranteed by the `Set` interface; specific implementations (e.g., `LinkedHashSet`) can preserve insertion order.
- Membership checks are typically O(1) for `HashSet`.
- No index-based access.

Use `Set` when:
- You need uniqueness.
- You frequently check whether an element is present.
- You want to remove duplicates from a list.
- You perform set operations (union, intersection, difference).

**Example:**
```kotlin
val uniqueIds = setOf(1, 2, 3, 2, 1)
println(uniqueIds)      // [1, 2, 3]
println(2 in uniqueIds) // true

val list = listOf(1, 2, 2, 3, 3, 3)
val unique = list.toSet()  // [1, 2, 3]
```

### Map — Key-value pairs

- Each key is unique.
- Each key maps to exactly one value; assigning the same key again replaces the previous value.
- Key-based lookup is typically O(1) for `HashMap`.
- Keys form a `Set`; values may contain duplicates.
- The `Map` interface does not guarantee ordering; specific implementations (e.g., `LinkedHashMap`, sorted maps) may define an order.

Use `Map` when:
- You need to associate keys with values.
- You need fast lookup by key.
- You store configs, dictionaries, caches, or frequency counts.

**Examples:**
```kotlin
// Config map
val config = mapOf(
    "api_url" to "https://api.example.com",
    "timeout" to "30",
    "retries" to "3"
)
println(config["timeout"])  // "30"

// Counting frequencies
val words = listOf("cat", "dog", "cat", "bird", "dog", "cat")
val frequency = words.groupingBy { it }.eachCount()
// {cat=3, dog=2, bird=1}

// User ages
val ages = mapOf(
    "Alice" to 25,
    "Bob" to 30,
    "Charlie" to 25
)
println(ages["Alice"]) // 25
```

### Comparative Table

| Characteristic      | `List`                                      | `Set`                                             | `Map`                                                              |
|---------------------|---------------------------------------------|---------------------------------------------------|--------------------------------------------------------------------|
| Duplicates          | Allowed                                     | Not allowed (duplicates are not stored)           | Keys are unique, values may repeat                                 |
| Order               | Preserved (for standard `List`/`ArrayList`) | Not guaranteed by `Set` contract                  | Not guaranteed by `Map` contract (depends on implementation)       |
| Index-based access  | Yes                                         | No                                                | No (key-based access instead)                                      |
| Membership check    | O(n) with linear search                     | Typically O(1) for `HashSet`                      | Typically O(1) for `HashMap` key lookup                            |
| Primary use case    | Ordered data                                | Uniqueness and fast membership checks             | Key-value associations and fast lookups by key                     |

### Usage Examples

```kotlin
// List - tasks in execution order
val todoList = mutableListOf("Buy milk", "Write code", "Buy milk")
println(todoList)  // [Buy milk, Write code, Buy milk] - order and duplicates preserved

// Set - unique tags
val tags = mutableSetOf("kotlin", "android", "kotlin", "java")
println(tags)  // [kotlin, android, java] - only unique values, order is implementation-dependent

// Map - app configuration
val configMap = mapOf(
    "api_url" to "https://api.example.com",
    "timeout" to "30",
    "retries" to "3"
)
println(configMap["timeout"])  // "30"
```

### Mutable vs read-only

```kotlin
// Read-only views
val list = listOf(1, 2, 3)          // List<Int>
val set = setOf("a", "b", "c")      // Set<String>
val map = mapOf(1 to "one")         // Map<Int, String>

// Mutable collections
val mutableList = mutableListOf(1, 2, 3)      // MutableList<Int>
mutableList.add(4)

val mutableSet = mutableSetOf("a", "b")       // MutableSet<String>
mutableSet.add("c")

val mutableMap = mutableMapOf(1 to "one")     // MutableMap<Int, String>
mutableMap[2] = "two"
```

### Real-world Examples

```kotlin
// 1. List - user action history
val userActions = mutableListOf<String>()
userActions.add("Opened app")
userActions.add("Clicked button")
userActions.add("Opened app")  // duplicate is allowed
println(userActions)  // shows the sequence of actions

// 2. Set - unique visitors
val visitors = mutableSetOf<String>()
visitors.add("user123")
visitors.add("user456")
visitors.add("user123")  // duplicate add does not change the set
println("Unique visitors: ${visitors.size}")  // 2

// 3. Map - data cache
val cache = mutableMapOf<String, Data>()
val userId = "user123"
val data = cache[userId] ?: fetchData(userId).also { cache[userId] = it }
```

### When to Use What - Quick Cheat Sheet

Use `List` when:
- Order matters.
- You need index-based access.
- Duplicates are acceptable and may carry meaning.

Use `Set` when:
- You need uniqueness guarantees.
- You often check whether an element exists.
- Order is not important (or you pick a specific implementation for desired ordering).
- You want to remove duplicates from a collection.

Use `Map` when:
- You need to associate keys with values.
- You frequently look up data by key.
- You build dictionaries, configuration maps, caches, or frequency maps.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия коллекций Kotlin от коллекций Java?
- В каких реальных сценариях вы бы использовали каждый из этих типов коллекций?
- Какие подводные камни при работе с изменяемыми и только для чтения коллекциями?

## Follow-ups

- What are the key differences between Kotlin collections and Java collections?
- When would you use each of these collection types in real projects?
- What are common pitfalls to avoid when working with mutable vs read-only collections?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные вопросы (RU)

- [[q-kotlin-object-companion-object--programming-languages--easy]]
- [[q-dispatchers-unconfined--kotlin--medium]]

## Related Questions

- [[q-kotlin-object-companion-object--programming-languages--easy]]
- [[q-dispatchers-unconfined--kotlin--medium]]
