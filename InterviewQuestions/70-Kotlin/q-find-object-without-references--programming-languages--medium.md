---
id: lang-071
title: "Find Object Without References / Поиск объектов без ссылок"
aliases: [Find Object Without References, Поиск объектов без ссылок]
topic: programming-languages
subtopics: [debugging, memory-management, profiling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-debugging, c-memory-management, q-garbage-collector-basics--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [debugging, difficulty/medium, memory-management, memory-profiler, profiling, programming-languages]
date created: Friday, October 31st 2025, 6:30:13 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---
# Как Найти Объект, Если На Него Нет Ссылок?

# Вопрос (RU)
> Как найти объект, если на него нет ссылок?

---

# Question (EN)
> How to find an object if there are no references to it?

## Ответ (RU)

Создайте дамп памяти в Android Studio ("Dump Java heap"). Используйте Memory Analyzer Tool (MAT) для анализа. Ищите "Unreachable objects" и "Dominators". LeakCanary автоматически обнаруживает утечки.

## Answer (EN)

Finding objects without references is challenging because they're normally garbage collected. However, you can analyze them using **memory profiling tools**.

**Methods:**

**1. Heap Dump (Android Studio)**

```
1. Open Android Profiler
2. Select Memory tab
3. Click "Dump Java heap"
4. Wait for heap dump to load
```

**2. Analyze with Android Studio**

- View "Unreachable objects"
- Check "Shallow Size" and "Retained Size"
- Inspect object instances
- Find objects that should have been GC'd

**3. Memory Analyzer Tool (MAT)**

```bash

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
-
-
