---
id: "20251015082237078"
title: "Garbage Collector Basics / Garbage Collector Основы"
topic: computer-science
difficulty: medium
status: draft
created: 2025-10-15
tags: - garbage-collector
  - gc
  - java
  - kotlin
  - memory-management
  - performance
  - programming-languages
---
# Что такое сборщик мусора?

# Question (EN)
> What is garbage collector?

# Вопрос (RU)
> Что такое сборщик мусора?

---

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

