---
id: kotlin-182
title: "Coroutines Vs Threads / Корутины против потоков"
aliases: [Coroutines vs Threads, Корутины против потоков]
topic: kotlin
subtopics: [coroutines, threading]
question_kind: theory
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-lambda-expressions--kotlin--medium, q-fan-in-fan-out-channels--kotlin--hard, q-abstract-class-vs-interface--kotlin--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - comparison
  - concurrency
  - coroutines
  - java
  - kotlin
  - programming-languages
  - threads
  - difficulty/medium
---
# В чем концептуальное отличие корутинов от потоков в Java

# Question (EN)
> What is the conceptual difference between coroutines and Java threads?

# Вопрос (RU)
> В чём концептуальное отличие корутин от потоков в Java?

---

## Answer (EN)

**Coroutines** are lightweight and managed at the language level, unlike threads which are heavyweight and OS-managed.

**Key differences:**

| Aspect | Coroutines | Threads |
|--------|-----------|---------|
| **Weight** | Lightweight (thousands possible) | Heavyweight (limited by OS) |
| **Management** | Language-level (Kotlin runtime) | OS-level |
| **Cost** | Low memory/CPU overhead | High memory/CPU overhead |
| **Context switching** | Cheap (user space) | Expensive (kernel space) |
| **Blocking** | Suspending (non-blocking) | Blocking |
| **Creation cost** | ~100 bytes | ~1 MB per thread |
| **Scalability** | Can have 100,000+ coroutines | Limited to ~thousands of threads |

**Why coroutines are better for I/O:**
- Threads block while waiting → waste resources
- Coroutines suspend → free the thread for other work
- Code remains sequential and readable with `suspend` functions

**Example:**
```kotlin
// Coroutine - can handle 100,000 concurrent operations
launch {
    val result = api.fetchData() // Suspends, doesn't block
    updateUI(result)
}

// Thread - blocks, limited to ~10,000 concurrent operations
thread {
    val result = api.fetchData() // Blocks the thread
    updateUI(result)
}
```

---

## Ответ (RU)

**Корутины** — легковесные и управляются на уровне языка, в отличие от потоков, которые тяжеловесные и управляются операционной системой.

**Ключевые отличия:**

| Аспект | Корутины | Потоки |
|--------|----------|--------|
| **Вес** | Легковесные (возможны тысячи) | Тяжеловесные (ограничены ОС) |
| **Управление** | Уровень языка (Kotlin runtime) | Уровень ОС |
| **Стоимость** | Низкие затраты памяти/CPU | Высокие затраты памяти/CPU |
| **Переключение контекста** | Дешевое (user space) | Дорогое (kernel space) |
| **Блокировка** | Приостановка (non-blocking) | Блокировка |
| **Стоимость создания** | ~100 байт | ~1 МБ на поток |
| **Масштабируемость** | Можно создать 100,000+ корутин | Ограничено ~тысячами потоков |

**Почему корутины лучше для I/O:**
- Потоки блокируются при ожидании → тратят ресурсы впустую
- Корутины приостанавливаются → освобождают поток для другой работы
- Код остается последовательным и читаемым с `suspend` функциями

**Пример:**
```kotlin
// Корутина - может обрабатывать 100,000 одновременных операций
launch {
    val result = api.fetchData() // Приостанавливается, не блокирует
    updateUI(result)
}

// Поток - блокируется, ограничен ~10,000 одновременных операций
thread {
    val result = api.fetchData() // Блокирует поток
    updateUI(result)
}
```

**Основное преимущество:** корутины позволяют писать асинхронный код так, как будто он синхронный, без callback hell и с меньшими затратами ресурсов.

## Related Questions

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-fan-in-fan-out-channels--kotlin--hard]]
- [[q-abstract-class-vs-interface--kotlin--medium]]
