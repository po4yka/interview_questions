---
id: 20251012-154380
title: "List Set Map Differences / Различия List Set и Map"
aliases: [Collections, List vs Set vs Map, Collection Types, Коллекции]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-object-companion-object--programming-languages--easy, q-dispatchers-unconfined--kotlin--medium, q-coroutines-vs-threads--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - kotlin
  - collections
  - list
  - set
  - map
  - difficulty/easy
---
# рассказать отличия и в каких случаях их использовать list set map

# Question (EN)
> Explain the differences between List, Set, and Map. When should you use each?

# Вопрос (RU)
> Расскажите отличия между List, Set и Map. Когда использовать каждый из них?

---

## Answer (EN)

Kotlin has three main collection types with distinct characteristics:

**List**: Ordered collection that allows duplicates. Elements accessed by index (0-based). Use for: ordered data, when duplicates are allowed, when you need indexed access.

**Set**: Unordered collection of unique elements. No duplicates allowed. Use for: ensuring uniqueness, membership testing, removing duplicates.

**Map**: Collection of key-value pairs. Each key is unique and maps to exactly one value. Use for: associating data (lookups), storing configurations, caching.

**Example:**
```kotlin
val numbers = listOf(1, 2, 2, 3)       // [1, 2, 2, 3] - duplicates allowed
val uniqueNumbers = setOf(1, 2, 2, 3)  // [1, 2, 3] - duplicates removed
val ages = mapOf("Alice" to 25, "Bob" to 30) // key-value pairs
```

---

## Ответ (RU)

В Kotlin есть три основных типа коллекций с различными характеристиками:

### List — упорядоченный список

**Характеристики:**
- Элементы упорядочены (имеют индекс)
- Допускаются дубликаты
- Доступ по индексу O(1)
- Сохраняет порядок добавления

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

### Set — множество уникальных элементов

**Характеристики:**
- Элементы уникальны (дубликаты автоматически удаляются)
- Порядок не гарантирован (кроме LinkedHashSet)
- Быстрая проверка наличия элемента O(1) для HashSet
- Нет доступа по индексу

**Когда использовать:**
- Когда нужна уникальность элементов
- Для быстрой проверки наличия элемента
- Для удаления дубликатов из списка
- Для операций над множествами (объединение, пересечение)

**Пример:**
```kotlin
val uniqueIds = setOf(1, 2, 3, 2, 1)
println(uniqueIds)     // [1, 2, 3] - дубликаты удалены
println(2 in uniqueIds) // true - быстрая проверка

// Удаление дубликатов из списка
val list = listOf(1, 2, 2, 3, 3, 3)
val unique = list.toSet()  // [1, 2, 3]
```

### Map — коллекция пар "ключ-значение"

**Характеристики:**
- Каждый ключ уникален
- Каждому ключу соответствует одно значение
- Быстрый доступ по ключу O(1) для HashMap
- Ключи образуют Set, значения могут повторяться

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

### Сравнительная таблица

| Характеристика | List | Set | Map |
|----------------|------|-----|-----|
| Дубликаты | Разрешены | Запрещены | Ключи уникальны, значения могут повторяться |
| Порядок | Сохраняется | Не гарантирован | Не гарантирован |
| Доступ по индексу | Да | Нет | Нет (по ключу) |
| Проверка наличия | O(n) | O(1) HashSet | O(1) HashMap |
| Главное применение | Упорядоченные данные | Уникальность | Ассоциации ключ-значение |

### Примеры использования

```kotlin
// List - задачи в порядке выполнения
val todoList = mutableListOf("Buy milk", "Write code", "Buy milk")
println(todoList)  // [Buy milk, Write code, Buy milk] - порядок и дубликаты

// Set - уникальные теги
val tags = mutableSetOf("kotlin", "android", "kotlin", "java")
println(tags)  // [kotlin, android, java] - только уникальные

// Map - конфигурация приложения
val config = mapOf(
    "api_url" to "https://api.example.com",
    "timeout" to "30",
    "retries" to "3"
)
println(config["timeout"])  // "30"
```

### Mutable vs Immutable

```kotlin
// Immutable (read-only)
val list = listOf(1, 2, 3)          // List<Int>
val set = setOf("a", "b", "c")      // Set<String>
val map = mapOf(1 to "one")         // Map<Int, String>

// Mutable
val mutableList = mutableListOf(1, 2, 3)      // MutableList<Int>
mutableList.add(4)

val mutableSet = mutableSetOf("a", "b")       // MutableSet<String>
mutableSet.add("c")

val mutableMap = mutableMapOf(1 to "one")     // MutableMap<Int, String>
mutableMap[2] = "two"
```

### Реальные примеры

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
visitors.add("user123")  // игнорируется
println("Unique visitors: ${visitors.size}")  // 2

// 3. Map - кэш данных
val cache = mutableMapOf<String, Data>()
val userId = "user123"
val data = cache[userId] ?: fetchData(userId).also { cache[userId] = it }
```

### Когда что использовать - краткая памятка

**Используйте List, если:**
- Важен порядок элементов
- Нужен доступ по индексу
- Дубликаты допустимы и важны

**Используйте Set, если:**
- Нужна гарантия уникальности
- Часто проверяете наличие элемента
- Порядок не важен
- Нужно удалить дубликаты

**Используйте Map, если:**
- Нужно связать ключи со значениями
- Часто ищете данные по ключу
- Строите справочники, словари, кэши
- Подсчитываете частоту элементов

## Related Questions

- [[q-kotlin-object-companion-object--programming-languages--easy]]
- [[q-dispatchers-unconfined--kotlin--medium]]
- [[q-coroutines-vs-threads--programming-languages--medium]]
