---
id: lang-015
title: "Garbage Collector Basics / Основы сборки мусора"
aliases: [Garbage Collector Basics, Основы сборки мусора]
topic: programming-languages
subtopics: [garbage-collection, memory-management, performance]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-garbage-collection, q-garbage-collector-definition--programming-languages--easy, q-garbage-collector-roots--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, garbage-collection, java, kotlin, memory-management, performance, programming-languages]
---
# Что Такое Сборщик Мусора?

# Вопрос (RU)
> Что такое сборщик мусора?

---

# Question (EN)
> What is garbage collector?

## Ответ (RU)

**Сборщик мусора (Garbage Collector, GC)** — это механизм управления памятью, который автоматически освобождает неиспользуемую память, занятую объектами, к которым больше нет ссылок.

**Как это работает:**

1. **Отслеживает ссылки на объекты**: Мониторит, какие объекты все еще достижимы из программы
2. **Идентифицирует мусор**: Объекты без ссылок считаются мусором
3. **Освобождает память**: Освобождает память, занятую недостижимыми объектами
4. **Работает в фоне**: Выполняется периодически без ручного вмешательства

**В Kotlin/Java:**
- GC работает в фоне автоматически
- Устраняет необходимость вручную освобождать память (в отличие от C/C++)
- Помогает предотвратить утечки памяти
- Делает управление памятью безопаснее и проще

**Преимущества:**
- Автоматическое управление памятью
- Предотвращает утечки памяти
- Уменьшает ошибки программиста
- Повышает продуктивность разработчика

**Что следует учитывать:**
- Паузы GC могут влиять на производительность
- Нет контроля над тем, когда запускается GC
- Объекты остаются в памяти до запуска GC

**Пример освобождения памяти:**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Объект создан
    // ... используем obj
}  // obj становится недостижимым здесь, подходит для GC
```

## Answer (EN)

**Garbage Collector (GC)** is a memory management mechanism that automatically frees unused memory occupied by objects to which there are no more references.

**How it works:**

1. **Tracks object references**: Monitors which objects are still reachable from program
2. **Identifies garbage**: Objects with no references are considered garbage
3. **Reclaims memory**: Frees memory occupied by unreachable objects
4. **Runs in background**: Executes periodically without manual intervention

**In Kotlin/Java:**
- GC works in the background automatically
- Eliminates need to manually free memory (unlike C/C++)
- Helps prevent memory leaks
- Makes memory management safer and simpler

**Benefits:**
- Automatic memory management
- Prevents memory leaks
- Reduces programmer errors
- Improves developer productivity

**Considerations:**
- GC pauses can affect performance
- No control over when GC runs
- Objects remain in memory until GC runs

**Example of memory reclamation:**
```kotlin
fun createObject() {
    val obj = LargeObject()  // Object created
    // ... use obj
}  // obj becomes unreachable here, eligible for GC
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-how-system-knows-weakreference-can-be-cleared--programming-languages--medium]]
- [[q-linkedlist-arraylist-insert-behavior--programming-languages--medium]]
- [[q-reference-types-criteria--programming-languages--medium]]
