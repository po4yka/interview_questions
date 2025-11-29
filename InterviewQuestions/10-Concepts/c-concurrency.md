---
id: "20251111-075114"
title: "Concurrency / Concurrency"
aliases: ["Concurrency"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-multithreading, c-coroutines, c-threading, c-structured-concurrency]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
date created: Tuesday, November 11th 2025, 7:51:14 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Concurrency is the ability of a program or system to structure and manage multiple tasks that appear to progress simultaneously, by interleaving their execution or running them in parallel. It is used to keep applications responsive, utilize CPU resources effectively (especially with I/O-bound work), and model real-world interactions between independent components. Concurrency is central in server-side systems, UI applications, distributed systems, and modern languages that provide threads, async/await, coroutines, and actors.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Конкурентность (concurrency) — это способность программы или системы организовывать и выполнять несколько задач, которые логически продвигаются одновременно, за счёт чередования их выполнения или параллельного запуска. Она используется для поддержания отзывчивости приложений, эффективного использования ресурсов процессора (особенно при I/O-операциях) и моделирования взаимодействия независимых компонентов. Конкурентность критически важна для серверных систем, UI-приложений, распределённых систем и современных языков с потоками, async/await, корутинами и акторной моделью.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Distinction from parallelism: Concurrency is about structuring and coordinating multiple tasks; parallelism is about executing tasks at the same time on multiple cores.
- Primitives: Common building blocks include threads, locks, mutexes, semaphores, message queues, async/await, coroutines, and actor-based messaging.
- Shared state and races: Access to shared mutable data can cause race conditions, data races, and visibility issues; requires synchronization (locks, atomics, immutability).
- Safety vs performance: Correct synchronization prevents bugs (deadlocks, livelocks) but can reduce throughput; good design balances safety, simplicity, and performance.
- High-level abstractions: Modern frameworks provide executors, thread pools, futures/promises, reactive streams, and structured concurrency to simplify concurrent code.

## Ключевые Моменты (RU)

- Отличие от параллелизма: Конкурентность описывает организацию и координацию нескольких задач; параллелизм — одновременное выполнение этих задач на нескольких ядрах.
- Примитивы: Основные механизмы — потоки, блокировки, мьютексы, семафоры, очереди сообщений, async/await, корутины и акторная модель.
- Общая память и гонки: Доступ к общей изменяемой памяти может вызывать состояния гонки, data race и проблемы видимости; требуется синхронизация (замки, атомарные операции, неизменяемые структуры).
- Безопасность vs производительность: Корректная синхронизация предотвращает дедлоки, лайвлоки и тонкие баги, но может снижать производительность; важно находить баланс.
- Высокоуровневые абстракции: Современные библиотеки предоставляют пул потоков, executors, futures/promises, реактивные потоки и структурированную конкурентность для упрощения конкурентного кода.

## References

- https://en.wikipedia.org/wiki/Concurrency_(computer_science)
- https://martinfowler.com/articles/parallelProcessing.html
- Official language docs on concurrency primitives (e.g., Java Concurrency, Kotlin coroutines, C++ concurrency support library)
