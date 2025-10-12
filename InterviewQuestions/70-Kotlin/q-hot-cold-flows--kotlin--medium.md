---
id: 20251012-140017
title: "Hot vs Cold Flows / Горячие и холодные потоки"
aliases: []

# Classification
topic: kotlin
subtopics: [coroutines, flow, hot-flows, cold-flows, sharedflow, stateflow]
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
related: [q-kotlin-flow-basics--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium, q-sharedin-statein--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, flow, hot-flows, cold-flows, difficulty/medium]
---
# Question (EN)
> What's the difference between hot and cold Flows? Explain Flow (cold), SharedFlow, StateFlow (hot), when to use each, and how to convert between them.

# Вопрос (RU)
> В чем разница между горячими и холодными потоками? Объясните Flow (холодный), SharedFlow, StateFlow (горячие), когда использовать каждый и как конвертировать между ними.

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

## Ответ (RU)

**Холодный Flow**: Начинает работу при подписке
**Горячий Flow**: Работает всегда, независимо от подписчиков

---

## Follow-up Questions

1. **What is SharingStarted strategy?**
2. **How to convert cold to hot?**

---

## References

- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)

---

## Related Questions

- [[q-kotlin-flow-basics--kotlin--medium]]
- [[q-sharedin-statein--kotlin--medium]]
