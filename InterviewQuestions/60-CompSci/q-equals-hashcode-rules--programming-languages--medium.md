---
id: 20251003140907
title: equals and hashCode rules / Правила equals и hashCode
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, java, object-methods]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/150
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-object-methods
  - c-collections

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [equals, hashcode, contracts, collections, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What rules exist for equals and hashCode methods

# Вопрос (RU)
> Какие существуют правила для методов equals и hashcode

---

## Answer (EN)

Methods `equals()` and `hashCode()` are important for correct operation of collections such as HashSet, HashMap, and HashTable.

**equals() contract:**
1. **Reflexive**: `x.equals(x)` must return true
2. **Symmetric**: If `x.equals(y)` is true, then `y.equals(x)` must be true
3. **Transitive**: If `x.equals(y)` and `y.equals(z)` are true, then `x.equals(z)` must be true
4. **Consistent**: Multiple calls return same result if no data changes
5. **Null comparison**: `x.equals(null)` must return false

**hashCode() contract:**
1. **Internal consistency**: hashCode must return same value if object hasn't changed
2. **Consistency with equals**: If `x.equals(y)` is true, then `x.hashCode() == y.hashCode()` must be true
3. **Optional distinction**: Different objects may have same hashCode (collisions allowed), but better performance if different

**Golden rule**: When you override `equals()`, you MUST override `hashCode()`!

## Ответ (RU)

Методы equals(Object obj) и hashCode() имеют важное значение для корректной работы коллекций...

---

## Follow-ups
- What happens if you override equals but not hashCode?
- How are data classes implemented in terms of equals/hashCode?
- What are best practices for implementing these methods?

## References
- [[c-object-methods]]
- [[c-collections]]
- [[moc-kotlin]]

## Related Questions
- [[q-hashmap-how-it-works--programming-languages--medium]]
