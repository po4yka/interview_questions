---\
id: android-080
title: Stack vs Heap Memory In Multithreading / Stack и Heap память для нескольких потоков
aliases: [Stack vs Heap Memory In Multithreading, Stack и Heap память для нескольких потоков]
topic: android
subtopics: [performance-memory, threads-sync]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-memory, android/threads-sync, difficulty/medium]
moc: moc-android
related: [c-android, c-concurrency, q-optimize-memory-usage-android--android--medium, q-tasks-back-stack--android--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
anki_cards:
  - slug: android-080-0-en
    front: "How do Stack and Heap memory work with multiple threads in Android?"
    back: |
      **Stack:**
      - **Each thread has its own stack**
      - Stores local variables, method frames, return addresses
      - More threads = more total stack memory

      **Heap:**
      - **Single shared heap** for all threads in process
      - Max size per process (not per thread)
      - More threads = more allocations = more GC pressure

      ```text
      10 threads: 10 separate stacks + 1 shared heap
      ```

      **Key:** Many threads significantly increase memory due to stack overhead.
    tags:
      - android_general
      - difficulty::medium
  - slug: android-080-0-ru
    front: "Как работают Stack и Heap память с несколькими потоками в Android?"
    back: |
      **Stack:**
      - **У каждого потока свой стек**
      - Хранит локальные переменные, фреймы методов, адреса возврата
      - Больше потоков = больше суммарной памяти под стеки

      **Heap:**
      - **Одна общая куча** для всех потоков процесса
      - Максимальный размер на процесс (не на поток)
      - Больше потоков = больше аллокаций = больше нагрузки на GC

      ```text
      10 потоков: 10 отдельных стеков + 1 общая куча
      ```

      **Важно:** Много потоков значительно увеличивают память из-за накладных расходов на стеки.
    tags:
      - android_general
      - difficulty::medium

---\
# Вопрос (RU)
> `Stack` и Heap память для нескольких потоков

# Question (EN)
> `Stack` vs Heap Memory In Multithreading

---

## Ответ (RU)

В многопоточных Android-приложениях стек и куча ведут себя по-разному относительно потоков.

- У каждого потока свой собственный стек.
- Все потоки внутри одного процесса приложения разделяют одну кучу, управляемую рантаймом (ART).

Итого:
- Общий расход памяти под стеки растёт с количеством потоков (отдельный стек на каждый поток).
- Куча общая; её максимальный размер не зависит от количества потоков, но фактическое использование кучи может расти, если дополнительные потоки создают больше объектов.

**Память стека (`Stack`):**

Каждый поток Java/Kotlin получает собственный стек для:
- локальных переменных
- кадров вызовов методов
- адресов возврата

```kotlin
// Каждый поток имеет свой стек
Thread {
    val localVar = 10  // Локальная переменная этого потока; логически относится к его стеку
    recursiveFunction()  // Использует стек этого потока
}.start()
```

Ключевые моменты:
- Размер стека на поток обычно составляет от сотен КБ до нескольких МБ и может настраиваться; конкретные значения зависят от платформы и конфигурации.
- Больше потоков → больше суммарной памяти, зарезервированной/используемой под стеки.

**Память кучи (Heap):**

Все потоки в одном процессе Android-приложения используют общую кучу:

```kotlin
// Все потоки разделяют одну кучу
val sharedObject = MyObject()  // Выделяется в общей куче

Thread {
    val obj1 = MyObject()  // Также выделяется в той же общей куче
}.start()
```

Ключевые моменты:
- Куча общая для всех потоков процесса.
- Максимальный размер кучи ограничен системой для процесса; он сам по себе не увеличивается только из-за роста числа потоков.
- Однако при появлении дополнительных потоков, которые делают больше выделений, увеличивается фактическое использование кучи и нагрузка на GC/синхронизацию.

**Иллюстративный расчёт памяти (пример):**

Предположим (условные числа только для наглядности, не реальные значения по умолчанию):
- Стек главного потока:     8 MB
- Стек рабочего потока:     1 MB каждый
- Максимальный heap процесса: 512 MB (общий)

Тогда:
```text
1 поток:     8 + 0*1 + (использование heap ≤ 512) MB
10 потоков:  8 + 10*1 + (использование heap ≤ 512) MB
100 потоков: 8 + 100*1 + (использование heap ≤ 512) MB
```

Это демонстрирует:
- Суммарный резерв под стеки растёт линейно с количеством потоков.
- Куча остаётся одной общей областью с фиксированным верхним пределом; фактическое использование зависит от количества выделений, а не от числа потоков напрямую.

**Итог:**

- Стек:
  - Отдельный стек на каждый поток.
  - Больше потоков → больше суммарный расход памяти под стеки.
- Куча:
  - Одна общая куча на процесс (для всех потоков).
  - Максимальный размер не зависит от количества потоков; фактическое использование и нагрузка (GC/синхронизация) могут расти при большем числе потоков и выделений.
- Практическое правило:
  - Каждый OS-поток имеет заметные накладные расходы на стек; большое количество потоков существенно увеличивает потребление памяти.

## Answer (EN)

In a multithreaded Android app, stack and heap behave differently with respect to threads.

- Each thread has its own stack.
- All threads in the same process share a single heap managed by the runtime (ART).

So:
- Total stack usage increases as you create more threads (one stack per thread).
- The process heap is shared; its maximum limit does not depend on the number of threads, but actual heap usage can grow if those threads allocate more objects.

**`Stack` Memory:**

Each Java/Kotlin thread gets its own stack for:
- local variables
- method call frames
- return addresses

```kotlin
// Each thread has its own stack
Thread {
    val localVar = 10  // Local variable for this thread; conceptually lives in its stack
    recursiveFunction()  // Uses this thread's stack frames
}.start()
```

Key points:
- Per-thread stack size is typically on the order of hundreds of KB to a few MB and is configurable; exact values depend on platform and configuration.
- More threads → more total memory reserved/used for stacks.

**Heap Memory:**

All threads within the same Android app process share one heap:

```kotlin
// All threads share the same heap
val sharedObject = MyObject()  // Allocated in the shared heap

Thread {
    val obj1 = MyObject()  // Also allocated in the same shared heap
}.start()
```

Key points:
- Heap is common for all threads in the process.
- The maximum heap size is bounded per process by the system; it does not inherently increase just because you create more threads.
- However, if additional threads allocate objects, overall heap usage (within that fixed limit) increases, and contention/GC pressure can grow.

**Illustrative Memory Calculation (example only):**

Assume (numbers are arbitrary for illustration only, not actual defaults):
- Main thread stack:    8 MB
- `Worker` thread stack:  1 MB each
- Max heap for process: 512 MB (shared)

Then:
```text
1 thread:    8 + 0*1 + (heap usage ≤ 512) MB
10 threads:  8 + 10*1 + (heap usage ≤ 512) MB
100 threads: 8 + 100*1 + (heap usage ≤ 512) MB
```

This shows:
- Total potential stack reservation grows linearly with thread count.
- Heap remains one shared region with a fixed upper bound; actual heap usage depends on allocations, not on the thread count alone.

**Summary:**

- `Stack`:
  - One separate stack per thread.
  - More threads → higher total stack memory usage.
- Heap:
  - Single shared heap per process (for all threads).
  - Max size independent of thread count; actual usage and GC/lock contention may increase with more threads doing allocations.
- Rule of thumb:
  - Each OS thread has non-trivial stack overhead; many threads can significantly increase memory usage.

---

## Дополнительные Вопросы (RU)

- Как использование большого числа потоков влияет на частоту и паузы GC в Android-приложении?
- Какова роль пулинга потоков при оптимизации памяти?
- Какие альтернативы большому количеству потоков существуют в Android (например, [[c-coroutines]])?
- Как подобрать оптимальный размер стека для потоков в Android?
- Как диагностировать чрезмерное потребление heap из-за фоновых потоков?

## Follow-ups

- How does creating many threads affect GC frequency and pause times in an Android app?
- What is the role of thread pools in memory optimization?
- What alternatives to creating many threads exist in Android (for example, [[c-coroutines]])?
- How do you choose an optimal stack size for threads on Android?
- How can you diagnose excessive heap usage caused by background threads?

## Ссылки

- [Memory Management](https://developer.android.com/topic/performance/memory-overview)

## References

- [Memory Management](https://developer.android.com/topic/performance/memory-overview)

## Related Questions

- [[q-android-runtime-art--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-app-lag-analysis--android--medium]]
