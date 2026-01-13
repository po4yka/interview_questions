---
id: kotlin-160
title: ArrayList LinkedList Vector Difference / Разница ArrayList LinkedList и Vector
anki_cards:
- slug: q-arraylist-linkedlist-vector-difference-0-en
  language: en
- slug: q-arraylist-linkedlist-vector-difference-0-ru
  language: ru
aliases:
- ArrayList LinkedList Vector Difference
- Разница ArrayList LinkedList Vector
topic: kotlin
subtopics:
- collections
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-collections
- q-coroutine-resource-cleanup--kotlin--medium
- q-kotlin-enum-classes--kotlin--easy
created: 2025-10-15
updated: 2025-11-09
tags:
- collections
- data-structures
- difficulty/medium
- kotlin
---
# Вопрос (RU)
> В чем разница между `ArrayList`, `LinkedList` и `Vector`?

# Question (EN)
> What is the difference between `ArrayList`, `LinkedList`, and `Vector`?

## Ответ (RU)
Это три разные реализации интерфейса `List` из Java, доступные в Kotlin (через Java interop). Идиоматичный Kotlin обычно использует интерфейсы `List`/`MutableList` и выбирает конкретную реализацию по необходимости.

### ArrayList

Реализация: динамический (расширяемый) массив.

Характеристики:
- Быстрый доступ по индексу: O(1)
- Быстрая итерация
- Медленные вставки/удаления в середине: O(n), так как элементы нужно сдвигать
- Автоматическое увеличение емкости при переполнении (амортизированная сложность добавления в конец — O(1))
- Не синхронизирован (не потокобезопасен)

Лучше всего подходит для:
- Частого доступа по индексу
- Итерации по элементам
- Добавления в конец
- Ситуаций без частых вставок/удалений в середине больших списков

```kotlin
val arrayList = ArrayList<String>()
arrayList.add("Item 1")        // Быстрое добавление в конец O(1)*
arrayList.add("Item 2")
arrayList.get(0)               // Быстрый доступ O(1)
arrayList.add(1, "Middle")     // O(n) — сдвиг элементов
arrayList.remove("Item 1")     // O(n) — сдвиг элементов

// *Амортизированное O(1) — иногда требуется переразмеривание внутреннего массива
```

### LinkedList

Реализация: двусвязный список (каждый элемент хранит ссылки на предыдущий и следующий).

Характеристики:
- Медленный произвольный доступ по индексу: O(n) (нужно проходить от начала или конца)
- Быстрые вставки/удаления: O(1), если уже есть ссылка на узел
- Быстрое добавление/удаление в начале и в конце: O(1)
- Более высокий расход памяти на элемент (хранит ссылки prev/next)
- Не синхронизирован (не потокобезопасен)
- Реализует интерфейсы `List` и `Deque`

Лучше всего подходит для:
- Частых вставок/удалений в начале/конце
- Операций очереди/дека
- Вставок/удалений рядом с уже известными позициями/узлами
- Не подходит для частого случайного доступа по индексу в больших списках

```kotlin
val linkedList = LinkedList<String>()
linkedList.add("Item 1")           // O(1)
linkedList.addFirst("First")       // O(1)
linkedList.addLast("Last")         // O(1)
linkedList.get(0)                  // O(n)
linkedList.removeFirst()           // O(1)
linkedList.removeLast()            // O(1)

// Подходит для queue/deque
linkedList.offer("Element")        // Добавление в конец
linkedList.poll()                  // Удаление из начала
```

### Vector

Реализация: синхронизированный динамический массив (наследие Java 1.0).

Характеристики:
- Внутренне похож на `ArrayList`
- Многие методы синхронизированы (пер-операционная потокобезопасность)
- Медленнее `ArrayList` из-за накладных расходов на синхронизацию
- Обычно растет, увеличивая емкость на фиксированный коэффициент (часто в 2 раза)
- Исторически считается устаревшим (legacy) и не рекомендуется для нового кода, хотя формально не помечен как `@Deprecated`

Важно: синхронизация методов `Vector`/`Collections.synchronizedList` делает отдельные операции атомарными, но не защищает сложные последовательности действий (итерация + модификация и т.п.) без дополнительной внешней синхронизации.

Лучше всего подходит для:
- Поддержки легаси-кода на Java
- Для нового кода на Kotlin предпочтительнее `Collections.synchronizedList(ArrayList())` или конкурентные коллекции

```kotlin
val vector = Vector<String>()
vector.add("Item 1")        // Синхронизировано — потокобезопаснее по отдельным операциям, но медленнее
vector.get(0)               // Синхронизировано

// Современная альтернатива:
val syncList = Collections.synchronizedList(ArrayList<String>())
// Или использовать CopyOnWriteArrayList для конкурентного доступа (особенно при частых чтениях и редких изменениях)
```

### Сравнение Производительности

| Операция                   | `ArrayList` | `LinkedList`      | Vector |
|----------------------------|----------:|----------------:|-------:|
| get(index)                 | O(1)      | O(n)            | O(1)   |
| add(element)               | O(1)*     | O(1)            | O(1)*  |
| add(index, element)        | O(n)      | O(n)**          | O(n)   |
| remove(index)              | O(n)      | O(n)**          | O(n)   |
| contains(element)          | O(n)      | O(n)            | O(n)   |
| Потокобезопасность         | Нет       | Нет             | Да***  |
| Накладные расходы по памяти| Низкие    | Высокие         | Низкие |

*Амортизированное значение.

**Вставка/удаление сами по себе O(1), если узел уже найден; поиск по индексу — O(n).

***Методы синхронизированы, но для композиции операций и безопасной итерации требуется внешняя синхронизация.

### Когда Что Использовать

`ArrayList`:
- Выбор по умолчанию в большинстве случаев (через интерфейсы `List`/`MutableList`)
- Частый доступ по индексу
- Итерация и добавление в конец

`LinkedList`:
- Частые вставки/удаления в начале/конце
- Реализация структур `Queue`/`Deque`
- Операции около уже известных узлов

`Vector`:
- Не использовать в новом коде
- Только для совместимости с существующим Java-кодом
- Вместо него — `Collections.synchronizedList()` или `CopyOnWriteArrayList` (+ другие конкурентные коллекции при необходимости)

### Примеры Кода

```kotlin
// ArrayList — лучше для случайного доступа
val fruits = ArrayList<String>()
fruits.add("Apple")
fruits.add("Banana")
fruits.add("Cherry")
println(fruits[1])  // Быстро: O(1)

// LinkedList — удобно для очередей
val queue = LinkedList<String>()
queue.offer("Task 1")
queue.offer("Task 2")
queue.offer("Task 3")
println(queue.poll())  // Удаляет и возвращает первый элемент

// Vector — легаси, избегать в новом коде
val legacyVector = Vector<Int>()
legacyVector.add(1)
legacyVector.add(2)
// Предпочтительно: Collections.synchronizedList(ArrayList()) или другие современные коллекции
```

### Современные Альтернативы

Вместо `Vector` используйте:
- `Collections.synchronizedList(ArrayList())` — простой потокобезопасный список (с учётом необходимости внешней синхронизации при итерации)
- `CopyOnWriteArrayList` — для сценариев с частыми чтениями и редкими записями
- `ConcurrentLinkedQueue` — для конкурентных операций очереди

```kotlin
// Потокобезопасные альтернативы Vector
val syncList = Collections.synchronizedList(ArrayList<String>())
val cowList = CopyOnWriteArrayList<String>()
val concurrentQueue = ConcurrentLinkedQueue<String>()
```

## Answer (EN)
These are three different Java `List` implementations with distinct characteristics that you can use from Kotlin (via Java interop). Idiomatic Kotlin code usually targets the `List`/`MutableList` interfaces and chooses a concrete implementation as needed.

### ArrayList

Implementation: dynamic array (resizable array).

Characteristics:
- Fast random access by index: O(1)
- Fast iteration
- Slow insertion/deletion in middle: O(n) (requires shifting elements)
- Automatically grows when capacity is exceeded (append is amortized O(1))
- Not synchronized (not thread-safe)

Best for:
- Frequent access by index
- Iteration
- Append operations
- Avoid frequent insertions/deletions in the middle of large lists

```kotlin
val arrayList = ArrayList<String>()
arrayList.add("Item 1")        // Fast append O(1)*
arrayList.add("Item 2")
arrayList.get(0)               // Fast access O(1)
arrayList.add(1, "Middle")     // O(n) - shifts elements
arrayList.remove("Item 1")     // O(n) - shifts elements

// *Amortized O(1) - occasionally needs to resize the internal array
```

### LinkedList

Implementation: doubly-linked list (each element has prev/next pointers).

Characteristics:
- Slow random access: O(n) (must traverse from head or tail)
- Fast insertion/deletion at a position: O(1) if you already have the node reference
- Fast add/remove at beginning or end: O(1)
- More memory overhead per element (stores prev/next references)
- Not synchronized (not thread-safe)
- Implements both `List` and `Deque` interfaces

Best for:
- Frequent insertions/deletions at the beginning/end
- `Queue` or `Deque` operations
- Frequent insertions/deletions near already-known positions/nodes
- Avoid for random access by index on large lists

```kotlin
val linkedList = LinkedList<String>()
linkedList.add("Item 1")           // O(1)
linkedList.addFirst("First")       // O(1)
linkedList.addLast("Last")         // O(1)
linkedList.get(0)                  // O(n)
linkedList.removeFirst()           // O(1)
linkedList.removeLast()            // O(1)

// Good for queue/deque
linkedList.offer("Element")        // Add to end
linkedList.poll()                  // Remove from beginning
```

### Vector

Implementation: synchronized dynamic array (legacy from Java 1.0).

Characteristics:
- Internally similar to `ArrayList`
- Many methods are synchronized (per-operation thread safety)
- Slower than `ArrayList` due to synchronization overhead
- Typically grows by increasing capacity with a fixed factor (often doubling)
- Considered a legacy class and not recommended for new code, although not formally annotated as `@Deprecated`

Important: synchronization in `Vector`/`Collections.synchronizedList` makes individual operations atomic, but does not automatically make compound actions (e.g., iteration + modification) safe without additional external synchronization.

Best for:
- Legacy Java interop only
- In new Kotlin code prefer `Collections.synchronizedList(ArrayList())` or appropriate concurrent collections instead

```kotlin
val vector = Vector<String>()
vector.add("Item 1")        // Synchronized — safer per operation in multi-threaded use, but slower
vector.get(0)               // Synchronized

// Modern alternative:
val syncList = Collections.synchronizedList(ArrayList<String>())
// Or use CopyOnWriteArrayList for concurrent access (especially read-heavy scenarios)
```

### Performance Comparison

| Operation           | `ArrayList` | `LinkedList` | Vector |
|---------------------|----------:|-----------:|-------:|
| get(index)          | O(1)      | O(n)       | O(1)   |
| add(element)        | O(1)*     | O(1)       | O(1)*  |
| add(index, element) | O(n)      | O(n)**     | O(n)   |
| remove(index)       | O(n)      | O(n)**     | O(n)   |
| contains(element)   | O(n)      | O(n)       | O(n)   |
| `Thread` Safety       | No        | No         | Yes*** |
| Memory Overhead     | Low       | High       | Low    |

*Amortized.

**Insertion/deletion is O(1) once the node is found; locating by index is O(n).

***Methods are synchronized, but compound operations and safe iteration still require external synchronization.

### When to Use What

`ArrayList`:
- Default choice for most use cases
- Frequent access by index
- Iteration over elements
- Append operations

`LinkedList`:
- Frequent insertions/deletions at beginning/end
- `Queue` or `Deque` operations
- Frequent insertions/deletions near already-known positions/nodes

`Vector`:
- Do not use in new code
- Only for legacy Java code compatibility
- Prefer `Collections.synchronizedList()` or `CopyOnWriteArrayList` (or other concurrent collections) instead

### Code Examples

```kotlin
// ArrayList - best for random access
val fruits = ArrayList<String>()
fruits.add("Apple")
fruits.add("Banana")
fruits.add("Cherry")
println(fruits[1])  // Fast: O(1)

// LinkedList - best for queue operations
val queue = LinkedList<String>()
queue.offer("Task 1")
queue.offer("Task 2")
queue.offer("Task 3")
println(queue.poll())  // Removes and returns first element

// Vector - legacy, avoid in new code
val legacyVector = Vector<Int>()
legacyVector.add(1)
legacyVector.add(2)
// Prefer: Collections.synchronizedList(ArrayList()) or other modern concurrent collections
```

### Modern Alternatives

Instead of `Vector`, use:
- `Collections.synchronizedList(ArrayList())` for simple thread-safety (remember to synchronize externally when iterating)
- `CopyOnWriteArrayList` for read-heavy concurrent access
- `ConcurrentLinkedQueue` for concurrent queue operations

```kotlin
// Thread-safe alternatives to Vector
val syncList = Collections.synchronizedList(ArrayList<String>())
val cowList = CopyOnWriteArrayList<String>()
val concurrentQueue = ConcurrentLinkedQueue<String>()
```

## Дополнительные Вопросы (RU)

- В чем практическая разница для кода на Kotlin по сравнению с чистой Java?
- В каких реальных сценариях вы бы выбрали каждую из этих реализаций?
- Какие типичные ошибки при выборе реализации встречаются на практике?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-collections]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]
- [[c-collections]]

## Связанные Вопросы (RU)

- [[q-kotlin-enum-classes--kotlin--easy]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]
- [[q-coroutine-exception-handler--kotlin--medium]]

## Related Questions

- [[q-kotlin-enum-classes--kotlin--easy]]
- [[q-coroutine-resource-cleanup--kotlin--medium]]
- [[q-coroutine-exception-handler--kotlin--medium]]
