---
id: kotlin-047
title: Anonymous Class in Inline Function / Анонимный класс в inline функции
aliases: [Anonymous Class in Inline Function, Анонимный класс в inline функции]

# Classification
topic: kotlin
subtopics: [anonymous-classes, inline, lambdas]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: ""
source_note: ""

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-coroutine-timeout-withtimeout--kotlin--medium, q-delegates-compilation--kotlin--hard, q-structured-concurrency-kotlin--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [anonymous-classes, difficulty/medium, inline, kotlin, lambdas, object-expressions, performance]
date created: Saturday, November 1st 2025, 12:43:05 pm
date modified: Sunday, November 2nd 2025, 12:05:11 pm
---
# Вопрос (RU)
> Можно ли создать анонимный класс внутри inline функции в Kotlin?

# Question (EN)
> Can you create an anonymous class inside an inline function in Kotlin?

## Ответ (RU)

**Нет**, **inline функции не должны содержать object expressions** (анонимные классы). Если нужно использовать inline, используйте **лямбду вместо анонимного класса**.

Однако есть нюансы: технически можно написать object expression в inline функции, но это **сводит на нет смысл инлайна** и может вызвать **проблемы с производительностью**, так как object expression всегда создает объект.

### Проблема

**Inline функции** предназначены для устранения создания объектов лямбд путем копирования кода лямбды непосредственно в место вызова.

**Анонимные классы** (object expressions) всегда создают экземпляры объектов, что противоречит цели инлайна.

### Ключевые Проблемы

1. **Создает объект** (сводит на нет inline)
2. **Не может захватывать inline лямбда-параметры**
3. **Ухудшает производительность** вместо улучшения

### Правильный Подход: Используйте Лямбды

```kotlin
// - Анонимный класс (создает объект)
inline fun process(action: (Int) -> Unit) {
    val handler = object : Handler {
        override fun handle(value: Int) {
            action(value)  // - Ошибка!
        }
    }
    handler.handle(42)
}

// - Лямбда (без создания объекта с inline)
inline fun process(action: (Int) -> Unit) {
    action(42)  // Инлайнится напрямую
}
```

### Когда Нужны Анонимные Классы

Используйте **обычные функции** (не inline) для анонимных классов:

```kotlin
// - Обычная функция для анонимного класса
fun createHandler(): EventHandler {
    return object : EventHandler {
        override fun onStart() { println("Started") }
        override fun onComplete(result: String) { println("Complete: $result") }
        override fun onError(error: Throwable) { println("Error: ${error.message}") }
    }
}
```

### Обходной Путь: Noinline

Если необходимо смешать:

```kotlin
inline fun process(
    value: Int,
    noinline complexHandler: (Int) -> Unit  // Помечаем как noinline
) {
    val handler = object : Handler {
        override fun handle() {
            complexHandler(value)  // Теперь OK
        }
    }
    handler.handle()
}
```

**Компромисс:** параметр `complexHandler` теряет преимущество inline.

### Резюме

**Можно ли создавать анонимные классы в inline функциях?**

- **Технически:** Иногда да (компилируется)
- **Практически:** Нет, сводит на нет смысл
- **Компилятор:** Часто выдает ошибки при захвате inline параметров

**Решение:**
- Используйте **лямбды** для single-method интерфейсов (SAM)
- Используйте **обычные функции**, когда нужны анонимные классы
- Используйте **noinline** модификатор, если нужно их смешать

**Ключевой принцип:** Inline для **устранения** создания объектов. Анонимные классы **создают** объекты. Они фундаментально несовместимы.

**Best practice:**
- Inline → Используйте лямбды
- Анонимные классы → Используйте обычные функции


---

## Answer (EN)
**No**, **inline functions cannot contain object expressions** (anonymous classes). If you need to use inline, you can pass a **lambda instead of an anonymous class**.

However, there are nuances: while you can technically write an object expression in an inline function, it **defeats the purpose** of inlining and can cause **performance issues** because the object expression creates an actual object allocation.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - Recyclerview

### Related (Medium)
- [[q-inline-classes-value-classes--kotlin--medium]] - Inline Class
- [[q-kotlin-inline-functions--kotlin--medium]] - Inline Functions
- [[q-macrobenchmark-startup--android--medium]] - Performance
- [[q-app-startup-optimization--android--medium]] - Performance

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]] - Jetpack Compose
