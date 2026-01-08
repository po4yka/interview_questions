---\
id: "20251110-134646"
title: "Threading / Threading"
aliases: ["Threading"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-multithreading", "c-concurrency", "c-kotlin-coroutines", "c-main-thread", "c-anr"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

Threading is a concurrency model where a process is divided into multiple independently scheduled execution flows (threads) that share the same memory space. It is used to perform tasks in parallel or asynchronously, improving responsiveness (e.g., UI apps) and throughput (e.g., servers) on multi-core systems. Threading is fundamental for building scalable, non-blocking, and high-performance applications but introduces complexity around synchronization and correctness.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Threading (многопоточность) — это модель конкуренции, при которой один процесс разделяется на несколько потоков исполнения, независимо планируемых, но разделяющих общее адресное пространство. Она используется для параллельного или асинхронного выполнения задач, повышая отзывчивость (например, UI-приложений) и пропускную способность (например, серверов) на мульти-ядерных системах. Многопоточность является основой масштабируемых, неблокирующих и высокопроизводительных приложений, но добавляет сложность синхронизации и обеспечения корректности.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Shared memory: Threads within the same process share heap and static data, enabling fast communication but increasing the risk of race conditions.
- Concurrency vs parallelism: Threading supports overlapping work (concurrency) and can exploit multiple CPU cores for true parallel execution.
- Synchronization: Correct use of locks, atomic operations, and memory visibility guarantees is required to avoid data races and inconsistent state.
- `Context` switching and overhead: Excessive threads lead to scheduling overhead, contention, and potential performance degradation.
- High-level abstractions: Modern languages/frameworks often wrap raw threads with thread pools, executors, async/await, and coroutines to simplify concurrent programming.

## Ключевые Моменты (RU)

- Общая память: Потоки одного процесса разделяют кучу и статические данные, что ускоряет обмен данными, но повышает риск гонок данных.
- Конкурентность и параллелизм: Многопоточность позволяет перекрывать выполнение задач (конкурентность) и использовать несколько ядер CPU для настоящего параллелизма.
- Синхронизация: Для избежания гонок и неконсистентного состояния необходимы блокировки, атомарные операции и гарантии видимости памяти.
- Переключение контекста и накладные расходы: Чрезмерное число потоков приводит к overhead планировщика, конкуренции за ресурсы и просадке производительности.
- Высокоуровневые абстракции: Современные языки/фреймворки поверх «сырых» потоков предоставляют пул потоков, executors, async/await и корутины для упрощения конкурентного кода.

## References

- https://docs.oracle.com/javase/tutorial/essential/concurrency/
- https://learn.microsoft.com/dotnet/standard/threading/
