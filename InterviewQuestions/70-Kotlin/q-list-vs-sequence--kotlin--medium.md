---
id: kotlin-216
title: "List Vs Sequence / List против Sequence"
aliases: [Eager Evaluation, Lazy Evaluation, List, List vs Sequence, Sequence]
topic: kotlin
subtopics: [collections, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-sealed-class-sealed-interface--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, difficulty/medium, kotlin, lazy-evaluation, performance, sequence]
date created: Friday, October 31st 2025, 6:29:31 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---

# List Vs Sequence: Жадные И Ленивые Коллекции

# Вопрос (RU)
> В чём разница между `List` и `Sequence` в Kotlin?

---

# Question (EN)
> What is the difference between `List` and `Sequence` in Kotlin?

## Ответ (RU)

**List** — жадная (eager) коллекция, где операции коллекций из стандартной библиотеки по умолчанию выполняются **немедленно** над **всеми** элементами и обычно создают **промежуточные коллекции**. **Sequence** — ленивое (lazy) представление, где промежуточные операции выполняются **по требованию** для элементов и откладываются до терминальной операции, а элементы проходят через цепочку по одному.

### List — Жадная Обработка (Eager)

Большинство операций над `List` (`map`, `filter`, `flatMap` и т.п.) создают **новую коллекцию**, обрабатывая **все** элементы.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .map { it * 2 }       // Создается List[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    .filter { it > 10 }   // Создается List[12, 14, 16, 18, 20]
    .take(2)              // Создается List[12, 14]

println(result)  // [12, 14]

// Всего создано 3 коллекции результата вызовов map/filter/take.
```

**Порядок выполнения:**
1. `map` обрабатывает **все 10 элементов** → создает новый `List` из 10 элементов
2. `filter` обрабатывает **все 10 элементов** → создает новый `List` из 5 элементов
3. `take` берет первые 2 элемента → создает финальный `List` из 2 элементов

**Итого:** 25 элементов обработано (10 + 10 + 5), 3 коллекции-результата созданы.

### Sequence — Ленивая Обработка (Lazy)

Обрабатывает элементы через **всю цепочку** операций по одному, откладывая выполнение до терминальной операции и не создавая больших промежуточных коллекций.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .asSequence()        // Конвертируем в Sequence
    .map { it * 2 }      // НЕ выполняется сразу (lazy)
    .filter { it > 10 }  // НЕ выполняется сразу (lazy)
    .take(2)             // НЕ выполняется сразу (lazy)
    .toList()            // Терминальная операция - ТЕПЕРЬ выполняется

println(result)  // [12, 14]

// Крупных промежуточных коллекций не создано.
```

**Порядок выполнения:**
1. Элемент 1: `map` (1×2=2) → `filter` (2>10? нет) → **отброшен**
2. Элемент 2: `map` (2×2=4) → `filter` (4>10? нет) → **отброшен**
3. ...
4. Элемент 6: `map` (6×2=12) → `filter` (12>10? да) → `take` (первый) → **взят**
5. Элемент 7: `map` (7×2=14) → `filter` (14>10? да) → `take` (второй) → **взят**
6. **Остановка** - `take(2)` получил 2 элемента

**Итого:** обработано только столько элементов, сколько нужно до выполнения условия (`take(2)`), без полного прохода по всем элементам.

### Детальное Сравнение

```kotlin
println("=== LIST (EAGER) ===")
val listResult = (1..5).toList()
    .also { println("После toList: $it") }
    .map {
        println("map: $it")
        it * 2
    }
    .also { println("После map: $it") }
    .filter {
        println("filter: $it")
        it > 4
    }
    .also { println("После filter: $it") }

// Вывод:
// После toList: [1, 2, 3, 4, 5]
// map: 1
// map: 2
// map: 3
// map: 4
// map: 5
// После map: [2, 4, 6, 8, 10]
// filter: 2
// filter: 4
// filter: 6
// filter: 8
// filter: 10
// После filter: [6, 8, 10]

println("\n=== SEQUENCE (LAZY) ===")
val seqResult = (1..5).asSequence()
    .also { println("После asSequence") }
    .map {
        println("map: $it")
        it * 2
    }
    .also { println("После map (описание цепочки, вычисление ленивое)") }
    .filter {
        println("filter: $it")
        it > 4
    }
    .also { println("После filter (описание цепочки, вычисление ленивое)") }
    .toList()
    .also { println("После toList: $it") }

// Вывод:
// После asSequence
// После map (описание цепочки, вычисление ленивое)
// После filter (описание цепочки, вычисление ленивое)
// map: 1
// filter: 2
// map: 2
// filter: 4
// map: 3
// filter: 6
// map: 4
// filter: 8
// map: 5
// filter: 10
// После toList: [6, 8, 10]
```

### Performance Сравнение

```kotlin
fun benchmarkList() {
    val largeList = (1..1_000_000).toList()

    val time = measureTimeMillis {
        val result = largeList
            .map { it * 2 }
            .filter { it > 1_000_000 }
            .take(10)
            .toList() // материализуем, чтобы действительно выполнить цепочку
    }

    println("List: $time ms")
    // Обработано: 1,000,000 (map) + 1,000,000 (filter) операций
    // Память: создаются коллекции-результаты для map и filter.
}

fun benchmarkSequence() {
    val largeList = (1..1_000_000).toList()

    val time = measureTimeMillis {
        val result = largeList
            .asSequence()
            .map { it * 2 }
            .filter { it > 1_000_000 }
            .take(10)
            .toList() // терминальная операция
    }

    println("Sequence: $time ms")
    // Обрабатываются элементы до тех пор, пока не будет найдено 10 подходящих.
    // Память: без больших промежуточных коллекций.
}
```

**Идея**: для цепочек операций и ранней остановки `Sequence` может быть значительно эффективнее как по памяти, так и по времени, но конкретный выигрыш зависит от данных, окружения и реализации.

### Когда Использовать List

**- Используйте `List` когда:**

1. **Маленькие коллекции** (< 100 элементов)

```kotlin
val users = listOf(user1, user2, user3)
    .filter { it.isActive }
    .map { it.name }
// Для небольших коллекций накладные расходы Sequence обычно не оправданы
```

1. **Нужны промежуточные результаты**

```kotlin
val doubled = numbers.map { it * 2 }
println("Doubled: $doubled")  // Можно напечатать

val filtered = doubled.filter { it > 10 }
println("Filtered: $filtered")  // Можно напечатать
```

1. **Операции требуют размера коллекции или индексации**

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.size)         // OK
println(numbers.lastIndex)    // OK
println(numbers[2])           // OK - прямой доступ

val seq = numbers.asSequence()
// seq.size - НЕТ такого метода
// seq[2] - НЕТ прямого доступа по индексу
```

1. **Нет длинной цепочки операций**

```kotlin
val result = numbers.map { it * 2 }  // Одна-две операции - List OK
```

### Когда Использовать Sequence

**- Используйте `Sequence` когда:**

1. **Большие коллекции** (обычно тысячи и более элементов)

```kotlin
val largeData = (1..1_000_000).asSequence()
    .map { expensiveOperation(it) }
    .filter { it.isValid }
    .take(10)
    .toList()
// Будут обработаны только элементы до получения 10 подходящих
```

1. **Длинные цепочки операций** (несколько последовательных шагов трансформации)

```kotlin
val result = users.asSequence()
    .filter { it.isActive }
    .map { it.email }
    .filter { it.endsWith(".com") }
    .sorted()
    .take(5)
    .toList()
```

1. **Ранняя остановка** (`first`, `take`, `any`, и т.п.)

```kotlin
// List-цепочка: map/filter проходят по всем элементам
val firstEvenFromList = (1..1_000_000)
    .map { it * 2 }
    .first { it > 1000 }

// Sequence-цепочка: остановка сразу после нахождения подходящего элемента
val firstEvenFromSeq = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 1000 }
```

1. **Бесконечные последовательности**

```kotlin
val fibonacci = generateSequence(1 to 1) { (a, b) -> b to (a + b) }
    .map { it.first }
    .take(10)
    .toList()

println(fibonacci)  // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

// С List это невозможно (бесконечный источник данных)
```

### Сравнительная Таблица

| Аспект | List | Sequence |
|--------|------|----------|
| **Выполнение** | Жадное (eager) | Ленивое (lazy, до терминальной операции) |
| **Промежуточные коллекции** | Обычно создаются при map/filter и т.п. | Как правило, не создают больших промежуточных коллекций |
| **Память** | Больше при длинных цепочках | Меньше при длинных цепочках |
| **Маленькие данные (<100)** | Часто быстрее/проще | Накладные расходы итераторов |
| **Большие данные (>1000)** | Может быть менее эффективно | Может быть эффективнее |
| **Цепочки операций (3+)** | Может быть менее эффективно | Часто эффективнее |
| **Ранняя остановка** | Обычные операции проходят по всем элементам | Останавливается, как только условие выполнено |
| **Прямой доступ [index]** | Да | Нет |
| **size, lastIndex** | Да | Нет (без материализации) |
| **Бесконечные данные** | Невозможно без собственной ленивой логики | Поддерживается |

### Терминальные И Промежуточные Операции

```kotlin
val numbers = listOf(1, 2, 3, 4, 5).asSequence()

// Промежуточные операции (Intermediate) - lazy, возвращают Sequence
val seq1 = numbers.map { it * 2 }        // Sequence
val seq2 = seq1.filter { it > 5 }        // Sequence
val seq3 = seq2.sorted()                 // Sequence

// До терминальной операции вычисления не происходят.

// Терминальные операции (Terminal) - запускают выполнение
val list = seq3.toList()          // Выполнение
val first = seq3.first()          // Повторное ленивое выполнение цепочки
val sum = seq3.sum()              // Повторное ленивое выполнение цепочки
seq3.forEach { println(it) }      // Повторное ленивое выполнение цепочки
```

**Промежуточные**: `map`, `filter`, `flatMap`, `distinct`, `sorted`, `drop`, `take`, и др.

**Терминальные**: `toList`, `toSet`, `first`, `last`, `sum`, `count`, `forEach`, `any`, `all`, и др.

### Практические Примеры

#### Пример 1: Обработка Файла

```kotlin
// List - загрузит весь файл в память
fun processFileEager(file: File): List<String> {
    return file.readLines()                  // Весь файл в памяти
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }
}

// Sequence - обрабатывает построчно
fun processFileLazy(file: File): List<String> {
    return file.bufferedReader()
        .lineSequence()                      // Ленивое чтение
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }
        .toList()
}
```

#### Пример 2: API Pagination

```kotlin
class UserRepository {
    // List - загрузит все страницы сразу
    suspend fun getAllUsersEager(): List<User> {
        val allUsers = mutableListOf<User>()
        var page = 1

        while (true) {
            val users = api.getUsers(page)
            if (users.isEmpty()) break
            allUsers.addAll(users)
            page++
        }

        return allUsers.filter { it.isActive }  // Фильтрация после загрузки всех
    }

    // Ленивая загрузка страниц с использованием Sequence НА ОСНОВЕ уже полученных данных.
    // ВАЖНО: sequence/generateSequence не поддерживают suspend напрямую.
    fun getAllUsersLazy(fetchPage: (Int) -> List<User>): Sequence<User> {
        return generateSequence(1) { it + 1 }
            .map { page -> fetchPage(page) }
            .takeWhile { it.isNotEmpty() }
            .flatMap { it.asSequence() }
            .filter { it.isActive }
    }
}

// Использование
val activeUsers = repository.getAllUsersLazy { page -> api.getUsersBlocking(page) }
    .take(100)
    .toList()
```

#### Пример 3: Поиск В Большой Коллекции

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = (1..1_000_000).map {
    Product(it, "Product $it", Random.nextDouble(10.0, 1000.0))
}

// List-цепочка: filter/map выполняются для всех элементов до first()
val expensiveProductList = products
    .filter { it.price > 900 }
    .map { it.name }
    .first()

// Sequence: остановится при первом совпадении
val expensiveProductSeq = products.asSequence()
    .filter { it.price > 900 }
    .map { it.name }
    .first()
```

### Конвертация Между List И Sequence

```kotlin
val list = listOf(1, 2, 3, 4, 5)

// List → Sequence
val sequence = list.asSequence()

// Sequence → List
val backToList = sequence.toList()

// Sequence → Set
val set = sequence.toSet()

// Sequence → Map
val map = sequence.associateWith { it * 2 }
```

### Распространенные Ошибки

**- Ошибка 1: Конвертация Sequence → List в середине**

```kotlin
// НЕПРАВИЛЬНО - потеря преимущества Sequence
val resultWrong = largeList.asSequence()
    .map { it * 2 }
    .toList()                // Преждевременная материализация
    .filter { it > 1000 }
    .take(10)

// ПРАВИЛЬНО - toList только в конце
val resultRight = largeList.asSequence()
    .map { it * 2 }
    .filter { it > 1000 }
    .take(10)
    .toList()                // Материализация в конце
```

**- Ошибка 2: Sequence для маленьких коллекций**

```kotlin
// НЕОПТИМАЛЬНО - накладные расходы Sequence для 5 элементов
val resultSeq = listOf(1, 2, 3, 4, 5).asSequence()
    .map { it * 2 }
    .toList()

// ПРОСТО - List для маленьких коллекций
val resultList = listOf(1, 2, 3, 4, 5)
    .map { it * 2 }
```

**- Ошибка 3: Повторное выполнение Sequence**

```kotlin
val sequenceOnce = (1..5).asSequence()
    .map {
        println("Processing $it")
        it * 2
    }

sequenceOnce.toList()  // Processing 1, 2, 3, 4, 5
sequenceOnce.toList()  // Processing 1, 2, 3, 4, 5 - ЕЩЕ РАЗ!

// Sequence не кэширует результаты - используйте List, если нужно многократное использование без пересчета
val listCached = sequenceOnce.toList()
listCached.forEach { }
listCached.forEach { }
```

### Best Practices

**1. Используйте Sequence для файлов**

```kotlin
// ПРАВИЛЬНО
File("large.txt").useLines { lines ->
    lines
        .filter { it.contains("ERROR") }
        .map { it.substringAfter(":") }
        .take(10)
        .toList()
}
```

**2. Используйте Sequence для больших данных + цепочки**

```kotlin
// ПРИМЕР
val result = largeDataset.asSequence()
    .filter { it.isValid }
    .map { it.transform() }
    .flatMap { it.items.asSequence() }
    .distinctBy { it.id }
    .take(100)
    .toList()
```

**3. Используйте List для простых случаев**

```kotlin
// ПРИМЕР - простой map без сложной цепочки
val names = users.map { it.name }
```

## Answer (EN)

`List` is an eager collection: standard collection operations like `map`/`filter`/`flatMap` are evaluated immediately over all elements and typically create intermediate collections. `Sequence` is a lazy view: intermediate operations are deferred until a terminal operation is called, elements go through the whole chain one by one, and large intermediate collections are usually avoided.

### List — Eager Processing

Most operations on a `List` create new collections and process all elements:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .map { it * 2 }
    .filter { it > 10 }
    .take(2)

println(result) // [12, 14]
```

Execution:
- `map` runs for all 10 elements → new `List` of 10
- `filter` runs for all 10 elements → new `List` of 5
- `take(2)` creates final `List` of 2

Total: 25 element operations, several intermediate collections.

### Sequence — Lazy Processing

`Sequence` processes items element-by-element through the whole pipeline and runs only when a terminal operation is invoked:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .asSequence()
    .map { it * 2 }
    .filter { it > 10 }
    .take(2)
    .toList() // terminal

println(result) // [12, 14]
```

Execution trace idea:
- Elements 1..5 → filtered out
- 6 → 12 → passes filter → taken as 1st
- 7 → 14 → passes filter → taken as 2nd
- `take(2)` stops the pipeline; rest are never processed.

### Detailed Comparison (Execution Trace)

```kotlin
println("=== LIST (EAGER) ===")
val listResult = (1..5).toList()
    .also { println("After toList: $it") }
    .map {
        println("map: $it")
        it * 2
    }
    .also { println("After map: $it") }
    .filter {
        println("filter: $it")
        it > 4
    }
    .also { println("After filter: $it") }

println("\n=== SEQUENCE (LAZY) ===")
val seqResult = (1..5).asSequence()
    .also { println("After asSequence") }
    .map {
        println("map: $it")
        it * 2
    }
    .also { println("After map (chain defined, still lazy)") }
    .filter {
        println("filter: $it")
        it > 4
    }
    .also { println("After filter (chain defined, still lazy)") }
    .toList()
    .also { println("After toList: $it") }
```

Shows that `List` work is done step-by-step per collection, while `Sequence` does work per element through the whole chain only when terminal operation is called.

### Performance Comparison

```kotlin
fun benchmarkList() {
    val largeList = (1..1_000_000).toList()

    val time = measureTimeMillis {
        val result = largeList
            .map { it * 2 }
            .filter { it > 1_000_000 }
            .take(10)
            .toList()
    }

    println("List: $time ms")
}

fun benchmarkSequence() {
    val largeList = (1..1_000_000).toList()

    val time = measureTimeMillis {
        val result = largeList
            .asSequence()
            .map { it * 2 }
            .filter { it > 1_000_000 }
            .take(10)
            .toList()
    }

    println("Sequence: $time ms")
}
```

Takeaway: for long pipelines with early termination, `Sequence` can reduce both memory and work; actual benefit depends on data and environment.

### When To Use List

Use `List` when:

1. Collections are small (e.g., < 100 elements):

```kotlin
val users = listOf(user1, user2, user3)
    .filter { it.isActive }
    .map { it.name }
```

1. You need intermediate results:

```kotlin
val doubled = numbers.map { it * 2 }
println("Doubled: $doubled")

val filtered = doubled.filter { it > 10 }
println("Filtered: $filtered")
```

1. You require indexing / `size` / `lastIndex`:

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.size)
println(numbers.lastIndex)
println(numbers[2])
```

1. You have 1–2 simple operations; `Sequence` overhead is not justified.

### When To Use Sequence

Use `Sequence` when:

1. Large collections or expensive computations:

```kotlin
val largeData = (1..1_000_000).asSequence()
    .map { expensiveOperation(it) }
    .filter { it.isValid }
    .take(10)
    .toList()
```

1. Long transformation chains:

```kotlin
val result = users.asSequence()
    .filter { it.isActive }
    .map { it.email }
    .filter { it.endsWith(".com") }
    .sorted()
    .take(5)
    .toList()
```

1. Early termination with `first`/`take`/`any`/etc.:

```kotlin
val firstEvenFromSeq = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 1000 }
```

1. Potentially infinite/streaming sources (e.g. `generateSequence`, `lineSequence`).

### Comparison Table

| Aspect | List | Sequence |
|-------|------|----------|
| Evaluation | Eager | Lazy (until terminal op) |
| Intermediates | Usually materialized | Usually avoided |
| Memory | Higher for long chains | Lower for long chains |
| Small data | Often simpler/faster | Iterator overhead |
| Large data | Can be inefficient | Often more efficient |
| Early termination | Still processes collections eagerly | Stops as soon as condition met |
| Random access | Yes (`[index]`) | No |
| `size`, `lastIndex` | Direct | Require materialization |
| Infinite data | Not suitable | Supported |

### Terminal Vs Intermediate Operations

Intermediate (lazy, return `Sequence`): `map`, `filter`, `flatMap`, `distinct`, `sorted`, `drop`, `take`, etc.

Terminal (trigger execution): `toList`, `toSet`, `first`, `last`, `sum`, `count`, `forEach`, `any`, `all`, etc.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5).asSequence()
val seq = numbers
    .map { it * 2 }
    .filter { it > 5 }
    .sorted()

val list = seq.toList()   // executes pipeline
val first = seq.first()   // would re-run pipeline
```

### Practical Examples

1. File processing:

```kotlin
fun processFileEager(file: File): List<String> =
    file.readLines()
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }

fun processFileLazy(file: File): List<String> =
    file.bufferedReader()
        .lineSequence()
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }
        .toList()
```

1. API pagination (non-suspending wrapper over page fetch):

```kotlin
fun getAllUsersLazy(fetchPage: (Int) -> List<User>): Sequence<User> =
    generateSequence(1) { it + 1 }
        .map { page -> fetchPage(page) }
        .takeWhile { it.isNotEmpty() }
        .flatMap { it.asSequence() }
        .filter { it.isActive }
```

1. Large collection search:

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = (1..1_000_000).map {
    Product(it, "Product $it", Random.nextDouble(10.0, 1000.0))
}

val expensiveProductList = products
    .filter { it.price > 900 }
    .map { it.name }
    .first()

val expensiveProductSeq = products.asSequence()
    .filter { it.price > 900 }
    .map { it.name }
    .first()
```

### Conversion Between List and Sequence

```kotlin
val list = listOf(1, 2, 3, 4, 5)
val sequence = list.asSequence()
val backToList = sequence.toList()
val set = sequence.toSet()
val map = sequence.associateWith { it * 2 }
```

### Common Mistakes

1. Premature `toList`:

```kotlin
val wrong = largeList.asSequence()
    .map { it * 2 }
    .toList()        // loses laziness
    .filter { it > 1000 }

val right = largeList.asSequence()
    .map { it * 2 }
    .filter { it > 1000 }
    .toList()
```

1. Using `Sequence` for tiny collections (iterator overhead, less readable).

2. Assuming `Sequence` caches results:

```kotlin
val seq = (1..5).asSequence()
    .map {
        println("Processing $it")
        it * 2
    }

seq.toList() // runs
seq.toList() // runs again
```

### Best Practices

- Prefer `List`:
  - Small collections.
  - Simple or single-step operations.
  - When you need random access or to reuse results.
- Prefer `Sequence`:
  - Long pipelines on large/expensive data.
  - Need early termination.
  - Working with streaming or infinite sources.
- Materialize once at the boundary (a single `toList`/`toSet`) after all lazy steps.

## Follow-ups

- What are the key differences between this and Java streams?
- When would you use this in practice in Kotlin codebases?
- What are common pitfalls when using `Sequence` (recomputation, mixing eager/lazy, premature `toList`)?

## References

- [Kotlin Collections and Sequences](https://kotlinlang.org/docs/sequences.html)
- [[c-kotlin]]

## Related Questions

- [[q-sealed-class-sealed-interface--kotlin--medium]]
