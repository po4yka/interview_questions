---
id: 20251012-154381
title: "List Vs Sequence / List против Sequence"
topic: kotlin
difficulty: medium
status: draft
moc: moc-kotlin
related: [q-lambdas-java-kotlin-syntax--programming-languages--medium, q-stateflow-purpose--programming-languages--medium, q-sealed-class-sealed-interface--kotlin--medium]
created: 2025-10-15
tags:
  - kotlin
  - collections
  - sequence
  - performance
  - lazy-evaluation
---
# List vs Sequence: жадные и ленивые коллекции

# Question (EN)
> What is the difference between List and Sequence in Kotlin?

# Вопрос (RU)
> В чём разница между List и Sequence в Kotlin?

---

## Answer (EN)

**List** is an eager collection where operations execute immediately on all elements, creating intermediate collections. **Sequence** is a lazy collection where operations execute per-element through the entire chain without intermediate collections.

**Key differences:**

| Aspect | List | Sequence |
|--------|------|----------|
| **Execution** | Eager (immediate) | Lazy (on-demand) |
| **Intermediate collections** | Created | Not created |
| **Memory** | More | Less |
| **Small data (<100)** | Faster | Slower (overhead) |
| **Large data (>1000)** | Slower | Faster |
| **Operation chains (3+)** | Slower | Faster |
| **Early termination** | Processes all | Stops early |

**Use List for:**
- Small collections (<100 elements)
- Single operations
- Need intermediate results
- Require size/indexing

**Use Sequence for:**
- Large collections (>1000 elements)
- Operation chains (3+ operations)
- Early termination (first, take, any)
- File processing
- Infinite data (generateSequence)

**Performance example:**
```kotlin
// List - processes ALL 1M elements
(1..1_000_000)
    .map { it * 2 }      // 1M operations
    .filter { it > 1000 } // 1M operations
    .take(10)

// Sequence - processes only ~500 elements
(1..1_000_000).asSequence()
    .map { it * 2 }
    .filter { it > 1000 }
    .take(10)             // Stops after finding 10
    .toList()
```

Sequence is ~30-40x faster for large data with early stops. Terminal operations (toList, first, sum) trigger execution. Avoid converting Sequence to List mid-chain.

---

## Ответ (RU)

**List** — жадная (eager) коллекция, где операции выполняются **немедленно** над **всеми** элементами сразу. **Sequence** — ленивая (lazy) коллекция, где операции выполняются **по требованию** для каждого элемента через цепочку. List создает промежуточные коллекции, Sequence обрабатывает элементы один за другим.

### List — жадная обработка (Eager)

Каждая операция создает **новую коллекцию**, обрабатывая **все** элементы.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .map { it * 2 }       // Создается List[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    .filter { it > 10 }   // Создается List[12, 14, 16, 18, 20]
    .take(2)              // Создается List[12, 14]

println(result)  // [12, 14]

// Всего создано 3 промежуточные коллекции!
```

**Порядок выполнения:**
1. `map` обрабатывает **все 10 элементов** → создает новый List из 10 элементов
2. `filter` обрабатывает **все 10 элементов** → создает новый List из 5 элементов
3. `take` берет первые 2 элемента → создает финальный List из 2 элементов

**Итого:** 25 элементов обработано (10 + 10 + 5), 3 промежуточных коллекции созданы.

### Sequence — ленивая обработка (Lazy)

Обрабатывает **каждый элемент** через **всю цепочку** операций сразу, не создавая промежуточных коллекций.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

val result = numbers
    .asSequence()        // Конвертируем в Sequence
    .map { it * 2 }      // НЕ выполняется сразу (lazy)
    .filter { it > 10 }  // НЕ выполняется сразу (lazy)
    .take(2)             // НЕ выполняется сразу (lazy)
    .toList()            // Терминальная операция - ТЕПЕРЬ выполняется

println(result)  // [12, 14]

// Промежуточных коллекций не создано!
```

**Порядок выполнения:**
1. Элемент 1: `map` (1×2=2) → `filter` (2>10? нет) → **отброшен**
2. Элемент 2: `map` (2×2=4) → `filter` (4>10? нет) → **отброшен**
3. ...
4. Элемент 6: `map` (6×2=12) → `filter` (12>10? да) → `take` (первый) → **взят**
5. Элемент 7: `map` (7×2=14) → `filter` (14>10? да) → `take` (второй) → **взят**
6. **Остановка** - `take(2)` получил 2 элемента

**Итого:** 7 элементов обработано, 0 промежуточных коллекций.

### Детальное сравнение

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
    .also { println("После map (lazy)") }
    .filter {
        println("filter: $it")
        it > 4
    }
    .also { println("После filter (lazy)") }
    .toList()
    .also { println("После toList: $it") }

// Вывод:
// После asSequence
// После map (lazy)
// После filter (lazy)
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

### Performance сравнение

```kotlin
fun benchmarkList() {
    val largeList = (1..1_000_000).toList()

    val time = measureTimeMillis {
        val result = largeList
            .map { it * 2 }
            .filter { it > 1_000_000 }
            .take(10)
    }

    println("List: $time ms")
    // ~150-200 ms
    // Обработано: 1,000,000 (map) + 1,000,000 (filter) = 2,000,000 операций
    // Память: 2 промежуточных List по 1,000,000 элементов
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
    // ~0-5 ms
    // Обработано: ~500,010 элементов (map + filter до получения 10 результатов)
    // Память: 0 промежуточных коллекций
}
```

**Результат**: Sequence в ~30-40 раз быстрее для больших коллекций с ранней остановкой.

### Когда использовать List

**- Используйте List когда:**

1. **Маленькие коллекции** (< 100 элементов)

```kotlin
val users = listOf(user1, user2, user3)
    .filter { it.isActive }
    .map { it.name }
// Производительность идентична, List проще
```

2. **Нужны промежуточные результаты**

```kotlin
val doubled = numbers.map { it * 2 }
println("Doubled: $doubled")  // Можно напечатать

val filtered = doubled.filter { it > 10 }
println("Filtered: $filtered")  // Можно напечатать
```

3. **Операции требуют размера коллекции**

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.size)         // OK
println(numbers.lastIndex)    // OK
println(numbers[2])           // OK - прямой доступ

val seq = numbers.asSequence()
// seq.size - НЕТ такого метода
// seq[2] - НЕТ прямого доступа
```

4. **Нет цепочки операций**

```kotlin
val result = numbers.map { it * 2 }  // Одна операция - List OK
```

### Когда использовать Sequence

**- Используйте Sequence когда:**

1. **Большие коллекции** (> 1000 элементов)

```kotlin
val largeData = (1..1_000_000).asSequence()
    .map { expensiveOperation(it) }
    .filter { it.isValid }
    .take(10)
    .toList()
// Sequence обработает только ~10-20 элементов вместо миллиона
```

2. **Цепочки операций** (3+ операции)

```kotlin
val result = users.asSequence()
    .filter { it.isActive }         // Операция 1
    .map { it.email }               // Операция 2
    .filter { it.endsWith(".com") } // Операция 3
    .sorted()                       // Операция 4
    .take(5)                        // Операция 5
    .toList()
```

3. **Ранняя остановка** (first, take, any, etc.)

```kotlin
// - List - обработает ВСЕ миллион элементов
val firstEven = (1..1_000_000)
    .map { it * 2 }
    .first { it > 1000 }

// - Sequence - остановится на ~500 элементе
val firstEven = (1..1_000_000).asSequence()
    .map { it * 2 }
    .first { it > 1000 }
```

4. **Бесконечные последовательности**

```kotlin
val fibonacci = generateSequence(1 to 1) { (a, b) -> b to (a + b) }
    .map { it.first }
    .take(10)
    .toList()

println(fibonacci)  // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

// С List это невозможно (бесконечный цикл)
```

### Сравнительная таблица

| Аспект | List | Sequence |
|--------|------|----------|
| **Выполнение** | Жадное (eager) | Ленивое (lazy) |
| **Промежуточные коллекции** | Создаются | Не создаются |
| **Память** | Больше | Меньше |
| **Маленькие данные (<100)** |  Быстрее |  Медленнее (overhead) |
| **Большие данные (>1000)** |  Медленнее |  Быстрее |
| **Цепочки операций (3+)** |  Медленнее |  Быстрее |
| **Ранняя остановка** | - Обрабатывает все | - Останавливается |
| **Прямой доступ [index]** | - Да | - Нет |
| **size, lastIndex** | - Да | - Нет |
| **Бесконечные данные** | - Невозможно | - Да |

### Терминальные и промежуточные операции

```kotlin
val numbers = listOf(1, 2, 3, 4, 5).asSequence()

// Промежуточные операции (Intermediate) - lazy, возвращают Sequence
val seq1 = numbers.map { it * 2 }        // Sequence
val seq2 = seq1.filter { it > 5 }        // Sequence
val seq3 = seq2.sorted()                 // Sequence

// Ничего не выполнилось!

// Терминальные операции (Terminal) - запускают выполнение
val list = seq3.toList()          // Выполнение!
val first = seq3.first()          // Выполнение!
val sum = seq3.sum()              // Выполнение!
seq3.forEach { println(it) }      // Выполнение!
```

**Промежуточные**: `map`, `filter`, `flatMap`, `distinct`, `sorted`, `drop`, `take`
**Терминальные**: `toList`, `toSet`, `first`, `last`, `sum`, `count`, `forEach`, `any`, `all`

### Практические примеры

#### Пример 1: Обработка файла

```kotlin
// - List - загрузит весь файл в память
fun processFileBad(file: File): List<String> {
    return file.readLines()                  // Вся файл в память!
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }
}

// - Sequence - обрабатывает построчно
fun processFileGood(file: File): List<String> {
    return file.bufferedReader()
        .lineSequence()                      // Ленивое чтение
        .filter { it.isNotBlank() }
        .map { it.trim() }
        .filter { it.startsWith("ERROR") }
        .toList()
}
```

#### Пример 2: API pagination

```kotlin
class UserRepository {
    // - List - загрузит все страницы сразу
    suspend fun getAllUsersBad(): List<User> {
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

    // - Sequence - ленивая загрузка страниц
    suspend fun getAllUsersGood(): Sequence<User> {
        return generateSequence(1) { it + 1 }
            .map { page -> api.getUsers(page) }
            .takeWhile { it.isNotEmpty() }
            .flatten()
            .filter { it.isActive }
    }
}

// Использование
val activeUsers = repository.getAllUsersGood()
    .take(100)  // Загрузит только нужные страницы
    .toList()
```

#### Пример 3: Поиск в большой коллекции

```kotlin
data class Product(val id: Int, val name: String, val price: Double)

val products = (1..1_000_000).map {
    Product(it, "Product $it", Random.nextDouble(10.0, 1000.0))
}

// - List - обработает ВСЕ миллион, даже если найдет в начале
val expensiveProductList = products
    .filter { it.price > 900 }
    .map { it.name }
    .first()

// - Sequence - остановится при первом совпадении
val expensiveProductSeq = products.asSequence()
    .filter { it.price > 900 }
    .map { it.name }
    .first()
```

### Конвертация между List и Sequence

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

### Распространенные ошибки

**- Ошибка 1: Конвертация Sequence → List в середине**

```kotlin
// - НЕПРАВИЛЬНО - потеря преимущества Sequence
val result = largeList.asSequence()
    .map { it * 2 }
    .toList()                // Преждевременная материализация!
    .filter { it > 1000 }
    .take(10)

// - ПРАВИЛЬНО - toList только в конце
val result = largeList.asSequence()
    .map { it * 2 }
    .filter { it > 1000 }
    .take(10)
    .toList()                // Материализация в конце
```

**- Ошибка 2: Sequence для маленьких коллекций**

```kotlin
// - НЕПРАВИЛЬНО - overhead Sequence для 5 элементов
val result = listOf(1, 2, 3, 4, 5).asSequence()
    .map { it * 2 }
    .toList()

// - ПРАВИЛЬНО - List для маленьких коллекций
val result = listOf(1, 2, 3, 4, 5)
    .map { it * 2 }
```

**- Ошибка 3: Повторное выполнение Sequence**

```kotlin
val sequence = (1..5).asSequence()
    .map {
        println("Processing $it")
        it * 2
    }

sequence.toList()  // Processing 1, 2, 3, 4, 5
sequence.toList()  // Processing 1, 2, 3, 4, 5 - ЕЩЕ РАЗ!

// Sequence не кэширует результаты - используйте List если нужно повторное использование
val list = sequence.toList()  // Один раз
list.forEach { }              // Без повторного вычисления
list.forEach { }              // Без повторного вычисления
```

### Best Practices

**1. Используйте Sequence для файлов**

```kotlin
// - ПРАВИЛЬНО
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
// - ПРАВИЛЬНО
val result = largeDataset.asSequence()
    .filter { it.isValid }
    .map { it.transform() }
    .flatMap { it.items }
    .distinctBy { it.id }
    .take(100)
    .toList()
```

**3. Используйте List для простых случаев**

```kotlin
// - ПРАВИЛЬНО - простой map без цепочки
val names = users.map { it.name }
```

## Related Questions

- [[q-lambdas-java-kotlin-syntax--programming-languages--medium]]
- [[q-stateflow-purpose--programming-languages--medium]]
- [[q-sealed-class-sealed-interface--kotlin--medium]]
