---
id: "20251111-100505"
title: "Binary Search / Binary Search"
aliases: ["Binary Search"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-algorithms, c-binary-search-tree, c-data-structures, c-sorting-algorithms]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 10:05:05 am
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Binary search is an efficient algorithm for finding a target value in a sorted array or search space by repeatedly halving the range of possible positions. It runs in O(log n) time, making it significantly faster than linear search for large datasets. It is widely used in standard library search functions, database indexing, and solving algorithmic problems involving monotonic predicates or answer ranges.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Бинарный поиск — это эффективный алгоритм поиска значения в отсортированном массиве или пространстве значений путём многократного деления диапазона пополам. Он работает за O(log n), что делает его значительно быстрее линейного поиска на больших наборах данных. Широко используется в стандартных библиотечных функциях поиска, индексах баз данных и задачах с монотонными условиями или поиском по диапазону ответов.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Requires sorted data: Binary search only works correctly on collections sorted by the same key and order used for comparison.
- Logarithmic time: Each comparison halves the remaining search range, leading to O(log n) time complexity and O(1) extra space in the classic iterative implementation.
- Correct mid calculation: Use safe mid computation (e.g., `mid = left + (right - left) / 2`) to avoid integer overflow in some languages.
- Boundary handling: Off-by-one errors are common; clearly define invariants (e.g., [left, right] inclusive vs [left, right) half-open) and update them consistently.
- Beyond arrays: The idea extends to searching over implicit/answer spaces (e.g., minimal feasible value) when the predicate is monotonic.

## Ключевые Моменты (RU)

- Требуется отсортированность: Бинарный поиск корректно работает только на коллекциях, отсортированных по тому же ключу и в том же порядке, что и при сравнении.
- Логарифмическое время: Каждый шаг делит оставшийся диапазон пополам, обеспечивая сложность O(log n) и O(1) дополнительной памяти в классической итеративной реализации.
- Корректный расчёт mid: Используйте безопасную формулу `mid = left + (right - left) / 2`, чтобы избежать переполнения целых чисел в некоторых языках.
- Работа с границами: Частая ошибка — смещение на один индекс; важно чётко задать инварианты (например, [left, right] включительно или [left, right) полуинтервал) и последовательно их поддерживать.
- За пределами массивов: Идея обобщается на поиск по неявным/ответным пространствам (например, минимальное подходящее значение), если предикат монотонный.

## References

- Binary search (CLRS / "Introduction to Algorithms")
- Official language library docs for binary/ordered search utilities (e.g., Java `Arrays.binarySearch`, C++ `std::binary_search`, Kotlin `binarySearch`)
