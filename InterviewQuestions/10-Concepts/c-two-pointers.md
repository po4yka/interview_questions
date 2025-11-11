---
id: "20251111-100536"
title: "Two Pointers / Two Pointers"
aliases: ["Two Pointers"]
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
created: "2025-11-11"
updated: "2025-11-11"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Two Pointers is an array/string traversal technique where two indices move through the data structure according to specific rules to solve problems efficiently. It reduces time and/or space complexity by exploiting ordering or structure (e.g., sorted arrays, contiguous ranges) without using extra data structures. Common in coding interviews for tasks like pair sums, removing duplicates, merging intervals, palindrome checks, and window-like scans.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Two Pointers — это техника обхода массивов и строк, при которой два индекса двигаются по структуре данных по заданным правилам для эффективного решения задач. Она уменьшает временную и/или дополнительную пространственную сложность, используя упорядоченность или структуру данных (например, отсортированные массивы, непрерывные диапазоны) без лишних вспомогательных структур. Часто используется на собеседованиях для задач о суммах пар, удалении дубликатов, слиянии интервалов, проверке палиндромов и сканирования участков данных.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Two main patterns: (1) opposite ends (e.g., start/end of sorted array to find target sums) and (2) same-direction (fast/slow pointers to scan or detect conditions).
- Efficient for sorted arrays and contiguous sequences, often reducing brute-force O(n²) solutions to O(n).
- Classic use cases: two-sum in sorted array, move zeros to the end, remove duplicates in-place, reverse/validate strings, compare subsequences.
- Fast/slow (tortoise-hare) variant is used to detect cycles in linked lists or to find the middle node without extra memory.
- Typically operates in-place with O(1) extra space, but requires careful pointer movement and boundary checks to avoid bugs.

## Ключевые Моменты (RU)

- Два основных паттерна: (1) навстречу друг другу (с начала и конца массива, например, для поиска суммы) и (2) в одном направлении (быстрый/медленный указатель для сканирования и проверки условий).
- Эффективна для отсортированных массивов и непрерывных последовательностей, часто сокращая решения O(n²) до O(n).
- Классические задачи: two-sum в отсортированном массиве, перенос нулей в конец, удаление дубликатов на месте, разворот/проверка строк, сравнение подпоследовательностей.
- Вариант с быстрым/медленным указателем (tortoise-hare) используется для обнаружения циклов в связных списках и поиска середины списка без дополнительной памяти.
- Обычно работает in-place с O(1) доп. памятью, но требует аккуратного управления индексами и проверок границ, чтобы избежать ошибок.

## References

- "Two Pointers Technique" — common topic in algorithm interview guides (e.g., LeetCode Explore / Patterns, educative.io patterns on two pointers).

