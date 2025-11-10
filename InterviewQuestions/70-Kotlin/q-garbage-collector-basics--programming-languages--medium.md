---
id: lang-015
title: "Garbage Collector Basics / Основы сборки мусора"
aliases: [Garbage Collector Basics, Основы сборки мусора]
topic: kotlin
subtopics: [garbage-collection, memory-management, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-definition--programming-languages--easy, q-garbage-collector-roots--programming-languages--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/medium, garbage-collection, java, kotlin, memory-management, performance, programming-languages]
---
# Вопрос (RU)
> Что такое сборщик мусора?

# Question (EN)
> What is garbage collector?

## Ответ (RU)

**Сборщик мусора (Garbage Collector, GC)** — это механизм управления памятью, который автоматически пытается освобождать память, занятую объектами, которые стали недостижимы из набора корневых ссылок (GC roots) и поэтому больше не могут быть использованы программой.

**Как это работает:**

1. **Отслеживает достижимость объектов**: Определяет, какие объекты всё ещё достижимы из корней (стек, статические поля, и т.п.)
2. **Идентифицирует мусор**: Недостижимые объекты считаются мусором
3. **Освобождает память**: Освобождает память, занятую недостижимыми объектами
4. **Работает в фоне**: Обычно выполняется автоматически без явного управления разработчиком

**В Kotlin/Java:**
- GC автоматически работает в фоне на JVM
- Нет необходимости вручную освобождать память (в отличие от C/C++)
- Помогает уменьшить количество утечек памяти, связанных с забытым освобождением
- Делает управление памятью безопаснее и проще, но логические утечки (например, из-за удержания ненужных ссылок) по-прежнему возможны

**Преимущества:**
- Автоматическое управление памятью
- Снижает риск утечек памяти из-за отсутствия освобождения
- Уменьшает ошибки программиста
- Повышает продуктивность разработчика

**Что следует учитывать:**
- Паузы GC могут влиять на производительность
- Нет точного контроля над тем, когда именно запускается GC
- Объекты остаются в памяти до тех пор, пока GC не определит их как недостижимые и не освободит

**Пример освобождения памяти (кандидат на сборку, не гарантированный момент):**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Объект создан
    // ... используем obj
}  // После выхода из функции obj становится недостижимым, объект становится кандидатом для GC (но сборка не гарантируется немедленно)
```

## Answer (EN)

**Garbage Collector (GC)** is a memory management mechanism that automatically attempts to reclaim memory occupied by objects that have become unreachable from the set of GC roots and therefore can no longer be used by the program.

**How it works:**

1. **Tracks reachability of objects**: Determines which objects are still reachable from roots (stack, static fields, etc.)
2. **Identifies garbage**: Unreachable objects are considered garbage
3. **Reclaims memory**: Frees memory occupied by unreachable objects
4. **Runs automatically**: Typically runs automatically without explicit control from the developer

**In Kotlin/Java:**
- GC runs automatically in the background on the JVM
- No need to manually free memory (unlike in C/C++)
- Helps reduce memory leaks caused by missing deallocation
- Makes memory management safer and simpler, but logical leaks (e.g., retaining unnecessary references) are still possible

**Benefits:**
- Automatic memory management
- Reduces the risk of memory leaks due to missing frees
- Reduces programmer errors
- Improves developer productivity

**Considerations:**
- GC pauses can affect performance
- No precise control over when GC runs
- Objects remain in memory until GC identifies them as unreachable and reclaims them

**Example of memory reclamation (eligible for collection; timing is not deterministic):**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Object created
    // ... use obj
}  // After the function returns, obj becomes unreachable; the object is eligible for GC (but collection is not guaranteed immediately)
```

---

## Follow-ups

- How does the JVM determine which objects are reachable (GC roots)?
- How does this differ from manual memory management in languages like C/C++?
- What are common pitfalls that still cause memory issues even with GC?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-garbage-collection]]

## Related Questions

- [[q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]]
- [[q-linkedlist-arraylist-insert-behavior--programming-languages--medium]]
- [[q-reference-types-criteria--programming-languages--medium]]
