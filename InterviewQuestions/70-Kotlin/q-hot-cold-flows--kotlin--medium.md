---
id: kotlin-076
title: "Hot vs Cold Flows / Горячие и холодные потоки"
aliases: ["Hot vs Cold Flows, Горячие и холодные потоки"]

# Classification
topic: kotlin
subtopics:
  - cold-flows
  - coroutines
  - flow
  - hot-flows
  - sharedflow
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Hot Cold Flows Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-kotlin-flow-basics--kotlin--medium, q-sharedin-statein--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [cold-flows, coroutines, difficulty/medium, flow, hot-flows, kotlin]
date created: Saturday, October 18th 2025, 9:34:33 am
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Вопрос (RU)
> В чем разница между горячими и холодными потоками? Объясните Flow (холодный), SharedFlow, StateFlow (горячие), когда использовать каждый и как конвертировать между ними.

---

# Question (EN)
> What's the difference between hot and cold Flows? Explain Flow (cold), SharedFlow, StateFlow (hot), when to use each, and how to convert between them.

## Ответ (RU)

Flow можно категоризировать как "холодные" или "горячие" в зависимости от того, когда они начинают производить значения.

### Холодный Flow

```kotlin
val coldFlow = flow {
    println("Started")
    emit(1)
}
// Запускается при collect(), независим для каждого подписчика
```

### Горячий Flow

```kotlin
val hotFlow = MutableSharedFlow<Int>()
// Всегда активен, общий для всех подписчиков
```

### Когда Использовать

- **Flow (холодный)**: Запросы к базе данных, API вызовы
- **SharedFlow (горячий)**: События, широковещание
- **StateFlow (горячий)**: Состояние UI

---

## Answer (EN)

Flows can be categorized as "cold" or "hot" based on when they start producing values.

### Cold Flow

```kotlin
val coldFlow = flow {
    println("Started")
    emit(1)
}
// Starts on collect(), independent for each collector
```

### Hot Flow

```kotlin
val hotFlow = MutableSharedFlow<Int>()
// Always active, shared between collectors
```

### When to Use

- **Flow (cold)**: Database queries, API calls
- **SharedFlow (hot)**: Events, broadcasts
- **StateFlow (hot)**: UI state

---

## Follow-ups

1. **What is SharingStarted strategy?**
2. **How to convert cold to hot?**

---

## References

- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)

---

## Related Questions

### Related (Medium)
- [[q-cold-vs-hot-flows--kotlin--medium]] - Flow
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

