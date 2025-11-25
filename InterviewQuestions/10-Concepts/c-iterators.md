---
id: "20251110-032402"
title: "Iterators / Iterators"
aliases: ["Iterators"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Monday, November 10th 2025, 7:48:48 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Iterators are objects or constructs that provide a standard way to traverse elements of a collection or sequence one-by-one without exposing its underlying representation. They decouple iteration logic from data storage, making code more generic, composable, and easier to maintain. Iterators are central to many language features and libraries (e.g., for-each loops, streams, generators) and are frequently tested in interviews when discussing collections, loops, and algorithm design.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Итераторы — это объекты или механизмы, предоставляющие стандартный способ последовательного обхода элементов коллекции или последовательности без раскрытия внутреннего устройства структуры данных. Они отделяют логику обхода от хранения данных, делая код более обобщённым, составным и поддерживаемым. Итераторы лежат в основе многих языковых конструкций (например, for-each, генераторы, потоки) и часто встречаются на собеседованиях при обсуждении коллекций и алгоритмов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Abstraction: Iterators expose a minimal interface (e.g., `hasNext`/`next`, `moveNext`/`Current`, `__iter__`/`__next__`) to access elements sequentially without revealing collection internals.
- Decoupling: The same iteration code (e.g., for-each loop) can work with different collection types as long as they provide an iterator, enabling polymorphism and generic algorithms.
- Safety and correctness: Iterators help avoid off-by-one and index errors common with manual index-based loops, and can enforce bounds checking internally.
- Laziness and streaming: Many iterators produce values on demand (lazy evaluation), which is useful for large data sets, streams, or infinite sequences.
- Mutability and concurrency considerations: Some iterators allow safe removal during traversal or detect concurrent modification; understanding these behaviors is important in languages like Java, C++, and Kotlin.

## Ключевые Моменты (RU)

- Абстракция: Итераторы предоставляют минимальный интерфейс (например, `hasNext`/`next`, `moveNext`/`Current`, `__iter__`/`__next__`) для последовательного доступа к элементам без раскрытия внутренней структуры коллекции.
- Разделение обязанностей: Один и тот же код обхода (например, for-each) может работать с разными типами коллекций, если они предоставляют итератор, что упрощает полиморфизм и обобщённые алгоритмы.
- Безопасность и корректность: Итераторы помогают избегать ошибок с индексами (off-by-one) и выходом за границы массива, инкапсулируя проверки внутри себя.
- Ленивость и потоки: Многие итераторы генерируют элементы по запросу (ленивое вычисление), что удобно для больших коллекций, потоков данных или потенциально бесконечных последовательностей.
- Мутируемость и конкуренция: Некоторые итераторы позволяют безопасное удаление элементов во время обхода или отслеживают конкурентные изменения; понимание этих особенностей важно в таких языках, как Java, C++ и Kotlin.

## References

- Java Iterator interface: https://docs.oracle.com/javase/8/docs/api/java/util/Iterator.html
- C++ Iterators (cppreference): https://en.cppreference.com/w/cpp/iterator
- Python Iterator Protocol: https://docs.python.org/3/library/stdtypes.html#typeiter
