---
anki_cards:
- slug: q-coroutines-vs-threads--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-coroutines-vs-threads--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
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
related: [c-kotlin, q-abstract-class-vs-interface--kotlin--medium, q-kotlin-lambda-expressions--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [comparison, concurrency, coroutines, difficulty/medium, kotlin, programming-languages, threads]
---\
# Вопрос (RU)
> В чём концептуальное отличие корутин от потоков в Java?

# Question (EN)
> What is the conceptual difference between coroutines and Java threads?

## Ответ (RU)

**Корутины** в Kotlin — легковесные единицы конкурентного выполнения, которые реализованы средствами компилятора и библиотеки поверх потоков, и управляются планировщиками в рамках `CoroutineDispatcher`, а не напрямую ОС. **Потоки** же — тяжеловесные сущности, создаваемые и управляемые операционной системой/VM.

См. также: [[c-kotlin]], [[c-coroutines]], [[c-structured-concurrency]].

**Ключевые отличия:**

| Аспект | Корутины | Потоки |
|--------|----------|--------|
| **Вес** | Легковесные (можно создавать десятки и сотни тысяч) | Тяжеловесные (количество ограничено ресурсами ОС/VM) |
| **Управление** | Компилятор + библиотека (`kotlinx.coroutines`), планируются в рамках пулов потоков | Планируются ОС/JVM как системные потоки |
| **Стоимость** | Низкие накладные расходы по памяти/CPU на единицу | Более высокие накладные расходы (стек, переключение контекста) |
| **Переключение контекста** | Дешёвое: переключение между корутинами в пользовательском пространстве внутри потока | Дорогое: переключение между потоками через ядро ОС |
| **Блокировка** | Поддерживают приостановку (`suspend`): не блокируют поток при корректном использовании неблокирующих API | Типичные блокирующие вызовы (I/O, `sleep`, `join`) блокируют поток |
| **Стоимость создания** | Очень низкая (память на состояние и стек — на порядки меньше потока; зависит от реализации) | Сравнительно высокая (стек порядка сотен КБ–МБ на поток, зависит от платформы/настроек JVM) |
| **Масштабируемость** | Можно эффективно обрабатывать 100,000+ корутин на ограниченном числе потоков | Обычно практично работать с числами порядка сотен–тысяч потоков |

**Почему корутины лучше для I/O:**
- При использовании блокирующих вызовов потоки простаивают в ожидании и продолжают занимать ресурсы.
- Корутины при использовании `suspend` и неблокирующих операций просто приостанавливаются, освобождая базовый поток для других задач.
- Код остаётся последовательным и читаемым благодаря `suspend` функциям, без "callback hell".

**Пример:**
```kotlin
// Корутина — может быть одной из сотен тысяч, обрабатывающих конкурентные операции
launch {
    val result = api.fetchData() // Предполагается неблокирующий suspend-вызов, приостанавливает корутину, не блокирует поток
    updateUI(result)
}

// Поток — каждый поток тяжеловесен, обычно используем ограниченный пул
thread {
    val result = api.fetchData() // Если это блокирующий вызов, поток будет заблокирован на время операции
    updateUI(result)
}
```

**Основное преимущество:** корутины позволяют писать асинхронный и конкурентный код в последовательном стиле, уменьшая накладные расходы и избегая избыточного числа потоков, при условии правильного использования неблокирующих/suspend-API.

## Answer (EN)

In Kotlin, **coroutines** are lightweight units of concurrent work implemented via compiler and library support on top of threads, scheduled by `CoroutineDispatcher` rather than directly by the OS. **Threads** are heavyweight entities created and managed by the OS/VM.

See also: [[c-kotlin]], [[c-coroutines]], [[c-structured-concurrency]].

**Key differences:**

| Aspect | Coroutines | Threads |
|--------|-----------|---------|
| **Weight** | Lightweight (you can create tens or hundreds of thousands) | Heavyweight (count limited by OS/VM resources) |
| **Management** | Compiler + library (`kotlinx.coroutines`), scheduled within thread pools | Scheduled by OS/JVM as system threads |
| **Cost** | Low per-unit memory/CPU overhead | Higher overhead (stack, context switching) |
| **`Context` switching** | Cheap: switching between coroutines in user space within a thread | Expensive: switching between threads via the OS kernel |
| **Blocking** | Support suspension (`suspend`): with proper non-blocking APIs they don't block the underlying thread | Typical blocking calls (I/O, `sleep`, `join`) block the thread |
| **Creation cost** | Very low (state + stack footprint orders of magnitude smaller than a thread; implementation-dependent) | Relatively high (stack in the hundreds of KB–MB range per thread, platform/JVM dependent) |
| **Scalability** | Can efficiently run 100,000+ coroutines on a limited number of threads | Practically operate with on the order of hundreds–thousands of threads |

**Why coroutines are better for I/O:**
- With blocking calls, threads wait idly while still consuming resources.
- Coroutines with `suspend` and non-blocking operations just suspend, freeing the underlying thread for other work.
- Code remains sequential and readable with `suspend` functions, avoiding callback hell.

**Example:**
```kotlin
// Coroutine — can be one of hundreds of thousands handling concurrent operations
launch {
    val result = api.fetchData() // Assumed to be a non-blocking suspend call; suspends coroutine without blocking the thread
    updateUI(result)
}

// Thread — each thread is heavyweight; typically you keep their count limited
thread {
    val result = api.fetchData() // If this is blocking, the thread is blocked for the duration of the call
    updateUI(result)
}
```

## Дополнительные Вопросы (RU)

- В чём ключевые отличия корутин в Kotlin от потоков в Java на практике?
- Когда на реальных проектах стоит предпочесть корутины потокам?
- Какие распространённые ошибки и подводные камни при работе с корутинами?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- Документация Kotlin: https://kotlinlang.org/docs/home.html

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-abstract-class-vs-interface--kotlin--medium]]

## Related Questions

- [[q-kotlin-lambda-expressions--kotlin--medium]]
- [[q-abstract-class-vs-interface--kotlin--medium]]
