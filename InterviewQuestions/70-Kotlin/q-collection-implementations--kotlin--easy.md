---
id: kotlin-202
title: "Collection Implementations / Реализации коллекций"
aliases: [Collection Implementations, Реализации коллекций]
topic: kotlin
subtopics: [collections]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-collections, q-fan-in-fan-out-channels--kotlin--hard, q-globalscope-antipattern--kotlin--easy, q-kotlin-generics--kotlin--hard]
created: 2025-10-15
updated: 2025-11-09
tags: [collections, difficulty/easy, implementations, kotlin, list, map, programming-languages, set]
date created: Friday, October 31st 2025, 6:30:09 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Какие Есть Реализации Коллекций?

# Вопрос (RU)
> Какие реализации коллекций доступны в Kotlin (на JVM)?

---

# Question (EN)
> What collection implementations are available in Kotlin (on the JVM)?

## Ответ (RU)

Kotlin (на JVM) использует реализации коллекций Java (`java.util`) под капотом для стандартных коллекций `List` / `Set` / `Map`. Основные реализации:

(На других платформах Kotlin (JS/Native) конкретные реализации могут отличаться, но API коллекций остаётся единым.)

### `List` (Списки)

- `ArrayList` - динамический массив (реализация по умолчанию для `mutableListOf` на JVM)
  - Быстрый доступ по индексу: O(1)
  - Быстрое добавление в конец (амортизированно O(1))
  - Медленная вставка/удаление в середине: O(n)

- `LinkedList` - двусвязный список (редко нужен в Kotlin-коде)
  - Вставка/удаление по уже известной ссылке/итератору: O(1)
  - Быстрая работа с началом/концом как очередью/деком
  - Медленный доступ по индексу и поиск элемента: O(n)
  - Больше накладных расходов по памяти (ссылки prev/next)

### `Set` (Множества)

- `HashSet` - хеш-таблица, без гарантий порядка
  - Ожидаемые (средние) операции add/remove/contains по элементу: O(1), в худшем случае O(n)
  - Требуется корректная реализация `hashCode`/`equals` для элементов

- `LinkedHashSet` - хеш-таблица + связный список (реализация по умолчанию для `mutableSetOf` на JVM)
  - Ожидаемые (средние) операции O(1), в худшем случае O(n)
  - Сохраняет порядок вставки

- `TreeSet` - на базе сбалансированного дерева (обычно красно-черного), отсортированное
  - Операции add/remove/contains: O(log n)
  - Элементы автоматически поддерживаются в отсортированном порядке (по natural order или заданному `Comparator`)

### `Map` (Словари)

- `HashMap` - хеш-таблица для пар ключ-значение
  - Ожидаемые (средние) операции get/put/remove по ключу: O(1), в худшем случае O(n)
  - Нет гарантий порядка
  - Требуется корректная реализация `hashCode`/`equals` для ключей

- `LinkedHashMap` - хеш-таблица + связный список (реализация по умолчанию для `mutableMapOf` на JVM)
  - Ожидаемые (средние) операции O(1), в худшем случае O(n)
  - Сохраняет порядок вставки

- `TreeMap` - на базе сбалансированного дерева (обычно красно-черного), отсортированного по ключам
  - Операции get/put/remove по ключу: O(log n)
  - Ключи автоматически сортируются (по natural order или заданному `Comparator`)

### Когда Что Использовать (RU)

**Списки (`List`):**
- `ArrayList` — выбор по умолчанию для списков, когда важны быстрый доступ по индексу и эффективная итерация.
- `LinkedList` — нишевый вариант; в идиоматичном Kotlin почти не используется, применять только если реально нужны операции очереди/дека с особыми требованиями.

**Множества (`Set`):**
- `HashSet` — по умолчанию, когда порядок не важен; требует хорошей реализации `hashCode`/`equals`.
- `LinkedHashSet` — когда нужен порядок вставки при тех же ожидаемых O(1) средних операциях.
- `TreeSet` — когда нужны отсортированные уникальные элементы; элементы должны быть `Comparable` или нужен `Comparator`.

**Отображения (`Map`):**
- `HashMap` — выбор по умолчанию, когда порядок ключей не важен; требует корректной реализации `hashCode`/`equals` для ключей.
- `LinkedHashMap` — когда нужен стабильный порядок вставки ключей.
- `TreeMap` — когда нужны отсортированные ключи; ключи должны быть `Comparable` или должен быть предоставлен `Comparator`.

### Сводная Таблица (RU)

| Интерфейс | Реализация      | Порядок           | Скорость (типично) | Когда использовать |
|----------|-----------------|-------------------|--------------------|--------------------|
| `List`   | `ArrayList`     | Порядок вставки   | Быстрый доступ по индексу | Список по умолчанию |
|          | `LinkedList`    | Порядок вставки   | Быстрые вставки/удаления через итератор/на концах | Очереди/деки, редкие специфичные случаи |
| `Set`    | `HashSet`       | Нет               | Ожидаемое O(1), худший O(n) | Множество по умолчанию |
|          | `LinkedHashSet` | Порядок вставки   | Ожидаемое O(1), худший O(n) | Нужен порядок вставки |
|          | `TreeSet`       | Отсортирован      | O(log n)           | Отсортированные уникальные элементы |
| `Map`    | `HashMap`       | Нет               | Ожидаемое O(1), худший O(n) | `Map` по умолчанию |
|          | `LinkedHashMap` | Порядок вставки   | Ожидаемое O(1), худший O(n) | Нужен порядок вставки |
|          | `TreeMap`       | Отсортированные ключи | O(log n)       | Поиск по отсортированным ключам |

### Фабричные Функции Kotlin (RU)

```kotlin
// Read-only view (интерфейсы только для чтения; не гарантируют глубокой неизменяемости)
val list = listOf(1, 2, 3)
val set = setOf("a", "b")
val map = mapOf("key" to "value")

// Mutable (изменяемые коллекции) — описание для JVM
val mutableList = mutableListOf(1, 2)      // ArrayList под капотом на JVM
val mutableSet = mutableSetOf("a")        // LinkedHashSet под капотом на JVM
val mutableMap = mutableMapOf("k" to "v") // LinkedHashMap под капотом на JVM

// Прямое создание конкретных реализаций (JVM)
val arrayList = ArrayList<Int>()
val hashSet = HashSet<String>()
val hashMap = HashMap<String, Int>()
val linkedList = LinkedList<String>()
val treeSet = TreeSet<Int>()
val treeMap = TreeMap<Int, String>()
```

### Сравнение Производительности (RU)

(Сложности относятся к типичным средним операциям над отдельными элементами для этих реализаций.)

| Операция                | `ArrayList` | `LinkedList`              | `HashSet`          | `TreeSet` |
|-------------------------|------------|---------------------------|--------------------|-----------|
| Добавление в конец      | O(1)*      | O(1)                      | O(1) ожидаемо      | O(log n)  |
| Добавление в начало     | O(n)       | O(1)                      | O(1) ожидаемо      | O(log n)  |
| Доступ по индексу       | O(1)       | O(n)                      | Н/Д                | Н/Д       |
| Проверка contains       | O(n)       | O(n)                      | O(1) ожидаемо      | O(log n)  |
| Удаление по элементу    | O(n)       | O(1)** при удалении по итератору/узлу | O(1) ожидаемо | O(log n)  |

* Амортизированная сложность для добавления в конец `ArrayList`.

** O(1), если элемент уже найден и удаляется через итератор или известный узел; O(n), если нужно сначала искать по значению/индексу.

## Answer (EN)

On the JVM, Kotlin standard `List` / `Set` / `Map` collections are backed by Java `java.util` implementations. Here are the main implementations:

(On other Kotlin targets like JS/Native, concrete implementations differ, but the collection APIs are consistent.)

### `List` Interface

**`ArrayList`** - Resizable array implementation (default for `mutableListOf` on JVM):
```kotlin
val list = ArrayList<String>()      // Explicit
val list2 = mutableListOf("a", "b")  // Uses ArrayList under the hood on JVM

// Properties:
// + Fast random access: O(1)
// + Fast iteration
// + Amortized O(1) append at end
// - Slow insertion/deletion in the middle: O(n)
// - Occasional resize/reallocation when growing
```

**`LinkedList`** - Doubly-linked list (rarely needed in idiomatic Kotlin):
```kotlin
val list = LinkedList<String>()

// Properties:
// + O(1) insertion/deletion when you already have a node/iterator
// + Efficient add/remove at beginning/end (deque/queue usage)
// - Slow random access by index: O(n)
// - Search by value is O(n)
// - Higher memory overhead per element (prev/next pointers)
```

**When to use:**
- `ArrayList`: Default choice, frequent index access and iteration.
- `LinkedList`: Niche; mainly when specifically using it as a deque/queue with special constraints.

### `Set` Interface

**`HashSet`** - Hash table implementation:
```kotlin
val set = HashSet<String>()      // Explicit

// Properties:
// + Expected O(1) add/remove/contains by element; worst-case O(n)
// - No ordering guarantee
// - Requires a good hashCode/equals implementation
```

**`LinkedHashSet`** - Hash table + linked list (default backing for `mutableSetOf` on JVM):
```kotlin
val set = LinkedHashSet<String>()
val set2 = mutableSetOf("a", "b")  // Uses LinkedHashSet under the hood on JVM

// Properties:
// + Expected O(1) operations; worst-case O(n)
// + Maintains insertion order
// - Slightly more memory than HashSet
```

**`TreeSet`** - Red-black tree (sorted):
```kotlin
val set = TreeSet<Int>()

// Properties:
// + Elements kept sorted (natural or custom order)
// + O(log n) add/remove/contains
// - Slower than HashSet for basic operations
// - Elements must be Comparable or a Comparator must be provided
```

**When to use:**
- `HashSet`: Default choice when order does not matter.
- `LinkedHashSet`: When you need insertion order.
- `TreeSet`: When you need elements sorted.

### `Map` Interface

**`HashMap`** - Hash table for key-value pairs:
```kotlin
val map = HashMap<String, Int>()

// Properties:
// + Expected O(1) get/put/remove by key; worst-case O(n)
// - No ordering guarantee
// - Requires good hashCode/equals for keys
```

**`LinkedHashMap`** - Hash table + linked list (default backing for `mutableMapOf` on JVM):
```kotlin
val map = LinkedHashMap<String, Int>()    // Explicit
val map2 = mutableMapOf("a" to 1)        // Uses LinkedHashMap under the hood on JVM

// Properties:
// + Expected O(1) operations; worst-case O(n)
// + Maintains insertion order
// - Slightly more memory overhead
```

**`TreeMap`** - Red-black tree (sorted by keys):
```kotlin
val map = TreeMap<Int, String>()

// Properties:
// + Keys kept sorted
// + O(log n) get/put/remove by key
// - Slower than HashMap for basic operations
// - Keys must be Comparable or require a Comparator
```

**When to use:**
- `HashMap`: Default choice when no ordering is needed.
- `LinkedHashMap`: When you need insertion order.
- `TreeMap`: When you need sorted keys.

### Summary Table (EN)

| Interface | Implementation | Ordering | Speed (typical) | Use Case |
|-----------|----------------|----------|-----------------|----------|
| `List` | `ArrayList` | Insertion order | Fast random access | Default list |
|  | `LinkedList` | Insertion order | Fast insert/delete via iterator/ends | Queues/deques, rare specific cases |
| `Set` | `HashSet` | None | Expected O(1), worst-case O(n) | Default set |
|  | `LinkedHashSet` | Insertion order | Expected O(1), worst-case O(n) | Preserve insertion order |
|  | `TreeSet` | Sorted | O(log n) | Sorted unique elements |
| `Map` | `HashMap` | None | Expected O(1), worst-case O(n) | Default map |
|  | `LinkedHashMap` | Insertion order | Expected O(1), worst-case O(n) | Preserve insertion order |
|  | `TreeMap` | Sorted keys | O(log n) | Sorted key lookups |

### Kotlin Factory Functions

```kotlin
// Read-only views (interfaces expose only read operations;
// underlying collection may or may not be truly immutable)
val list = listOf(1, 2, 3)
val set = setOf("a", "b")
val map = mapOf("key" to "value")

// Mutable collections (backed by specific implementations on JVM)
val mutableList = mutableListOf(1, 2)       // Backed by ArrayList on JVM
val mutableSet = mutableSetOf("a")         // Backed by LinkedHashSet on JVM
val mutableMap = mutableMapOf("k" to "v")  // Backed by LinkedHashMap on JVM

// Specific implementations (JVM)
val arrayList = ArrayList<Int>()
val hashSet = HashSet<String>()
val hashMap = HashMap<String, Int>()
val linkedList = LinkedList<String>()
val treeSet = TreeSet<Int>()
val treeMap = TreeMap<Int, String>()
```

### Performance Comparison (EN)

(Complexities refer to typical average-case per-element operations for these implementations.)

| Operation | `ArrayList` | `LinkedList` | `HashSet` | `TreeSet` |
|-----------|-----------|------------|---------|---------|
| Add at end | O(1)* | O(1) | O(1) expected | O(log n) |
| Add at beginning | O(n) | O(1) | O(1) expected | O(log n) |
| Get by index | O(1) | O(n) | N/A | N/A |
| Contains (by element) | O(n) | O(n) | O(1) expected | O(log n) |
| Remove (by element) | O(n) | O(1)** | O(1) expected | O(log n) |

* Amortized for `ArrayList` append.

** O(1) when removing via iterator/known node; O(n) when searching by value or index first.

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия реализаций коллекций в Kotlin и Java на практике (особенно с учетом мультиплатформенности)?
- Когда вы бы выбрали конкретную реализацию в реальных задачах?
- Какие типичные ошибки при выборе и использовании реализаций коллекций?

## Follow-ups

- What are the key differences between this and Java (including multiplatform nuances)?
- When would you use specific implementations in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-collections]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-collections]]

## Связанные Вопросы (RU)

- [[q-globalscope-antipattern--kotlin--easy]]
- [[q-fan-in-fan-out-channels--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]

## Related Questions

- [[q-globalscope-antipattern--kotlin--easy]]
- [[q-fan-in-fan-out-channels--kotlin--hard]]
- [[q-kotlin-generics--kotlin--hard]]
