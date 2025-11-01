---
id: 20251012-122730
title: "Equals Hashcode Rules / Правила equals и hashCode"
aliases: [Equals Hashcode Rules, Правила equals и hashCode]
topic: programming-languages
subtopics: [object-methods, collections, equality]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [c-equality, q-equals-hashcode-contracts--programming-languages--medium, q-equals-hashcode-purpose--programming-languages--hard]
created: 2025-10-15
updated: 2025-10-31
tags: [programming-languages, object-methods, equality, collections, contracts, difficulty/medium]
---

# Какие Существуют Правила Для Методов Equals И Hashcode?

# Question (EN)
> What rules exist for equals and hashCode methods?

# Вопрос (RU)
> Какие существуют правила для методов equals и hashcode?

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

---

## Ответ (RU)

Методы `equals()` и `hashCode()` имеют важное значение для корректной работы коллекций, таких как HashSet, HashMap и HashTable.

**Контракт equals():**
1. **Рефлексивность**: `x.equals(x)` должен возвращать true
2. **Симметричность**: Если `x.equals(y)` возвращает true, то `y.equals(x)` должен возвращать true
3. **Транзитивность**: Если `x.equals(y)` и `y.equals(z)` возвращают true, то `x.equals(z)` должен возвращать true
4. **Согласованность**: Множественные вызовы возвращают одинаковый результат, если данные не изменились
5. **Сравнение с null**: `x.equals(null)` должен возвращать false

**Контракт hashCode():**
1. **Внутренняя согласованность**: hashCode должен возвращать одно и то же значение, если объект не изменился
2. **Согласованность с equals**: Если `x.equals(y)` возвращает true, то `x.hashCode() == y.hashCode()` должен быть true
3. **Необязательное различие**: Разные объекты могут иметь одинаковый hashCode (коллизии допустимы), но лучшая производительность достигается при разных значениях

**Золотое правило**: Когда вы переопределяете `equals()`, вы ДОЛЖНЫ переопределить `hashCode()`!

## Related Questions

- [[q-interpreter-pattern--design-patterns--hard]]
- [[q-coroutine-context-essence--programming-languages--medium]]
- [[q-oop-principles-deep-dive--computer-science--medium]]
