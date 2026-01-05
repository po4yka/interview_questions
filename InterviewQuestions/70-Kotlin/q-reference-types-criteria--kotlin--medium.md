---
id: lang-047
title: "Reference Types Criteria / Критерии типов ссылок"
aliases: [Reference Types Criteria, Критерии типов ссылок]
topic: kotlin
subtopics: [immutability, object-model, type-design]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin]
created: 2025-10-15
updated: 2025-11-09
tags: [best-practices, design, difficulty/medium, immutability, kotlin, programming-languages, reference-types]
---
# Вопрос (RU)
> Каким критериям должны соответствовать ссылочные типы?

---

# Question (EN)
> What criteria should reference types meet?

## Ответ (RU)

В контексте Kotlin (классы и `data class` как ссылочные типы) при проектировании стоит учитывать:

### 1. Неизменяемость (когда Это Соответствует архитектуре)

Используйте неизменяемые типы, когда это возможно и когда доменная модель не требует мутаций:
```kotlin
// Хорошо: неизменяемый data class
data class User(val name: String, val email: String)

// Менее предпочтительно, когда нужна неизменяемость
data class User(var name: String, var email: String)
```

Замечания:
- Полностью неизменяемые объекты (без изменяемых полей и утечек внутреннего состояния) по своей природе потокобезопасны для конкурентного чтения.
- Их проще анализировать и безопаснее передавать между компонентами.
- Такие типы безопасно использовать как ключи в `Map` или элементы в `Set` при условии, что `equals`/`hashCode` согласованы с их состоянием.

### 2. Явная Null-безопасность

Выбирайте nullable или not-null строго по требованиям домена и делайте отсутствие явно выраженным в типах:
```kotlin
// Not-null, если значение всегда присутствует
data class User(
    val id: String,       // Всегда обязателен
    val email: String     // Всегда обязателен
)

// Nullable, если значение может отсутствовать
data class UserProfile(
    val bio: String?,     // Необязательная биография
    val avatar: String?   // Необязательный URL аватара
)
```

Это использует систему типов Kotlin, чтобы сделать nullability явной и проверяемой компилятором.

### 3. Корректная Семантика equals/hashCode/toString

Если экземпляры участвуют в коллекциях или логике, зависящей от равенства, обеспечьте корректное поведение:
```kotlin
// Data class автоматически генерирует:
// - equals()
// - hashCode()
// - toString()
data class Person(val name: String, val age: Int)

// Явная реализация для обычного класса при необходимости
class CustomType(val value: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is CustomType) return false
        return value == other.value
    }

    override fun hashCode(): Int = value.hashCode()

    override fun toString(): String = "CustomType(value=$value)"
}
```

Почему это важно:
```kotlin
val set = setOf(person1, person2)       // Уникальность опирается на equals/hashCode
val map = mapOf(person1 to "data")     // Поиск ключа опирается на equals/hashCode
println(person1)                        // Читаемый toString упрощает отладку
```

Все классы наследуют `equals`, `hashCode` и `toString` из `Any`, но их следует переопределять (или использовать `data class`), когда поведение по ссылочной идентичности не соответствует доменной семантике.

### 4. Легковесность (если Часто Создаётся Или копируется)

Держите типы достаточно компактными и сфокусированными, особенно если они часто создаются или копируются:
```kotlin
// Небольшой, "value-подобный" тип
data class Point(val x: Int, val y: Int)

// Более тяжёлый агрегат
data class HeavyObject(
    val largeArray: IntArray,
    val bigMap: Map<String, String>,
    val complexData: List<ComplexType>
)
```

Рекомендации:
- Избегайте лишних полей в часто используемых типах.
- Помните, что `copy()` у `data class` делает неглубокую (shallow) копию: копируются ссылки на вложенные объекты и коллекции, а не их содержимое.
- При критичных требованиях по производительности профилируйте: большие объектные графы и лишние аллокации могут быть проблемой.

### 5. Управляемое Наследование (final/sealed)

Предпочитайте `final` (по умолчанию) или `sealed`, когда поведение фиксировано или иерархия ограничена:
```kotlin
// По умолчанию: final-класс
data class User(val name: String)  // Нельзя наследовать без явного open

// Sealed: ограниченная иерархия (подклассы в том же файле)
sealed class Result<out T>

data class Success<T>(val data: T) : Result<T>()

data class Error(val message: String) : Result<Nothing>()

// open только при осознанной необходимости расширения
open class BaseEntity {
    open fun validate(): Boolean = true
}
```

Преимущества:
- Предотвращает неожиданное наследование.
- Позволяет исчерпывающие `when` по sealed-иерархиям с проверками на этапе компиляции.
- Может давать компилятору больше возможностей для оптимизаций.

### 6. Осознанная Ссылочная Семантика

Пользовательские классы в Kotlin на JVM и большинстве таргетов имеют ссылочную семантику:
- Коллекции хранят ссылки на объекты, а не копии.
- Мутация изменяемого объекта через одну ссылку видна через все остальные ссылки на этот объект.
- Архитектуру стоит проектировать так, чтобы либо избегать нежелательного aliasing за счёт неизменяемости, либо явно контролировать и документировать возможные эффекты.

### Сводный Чек-лист

Критерий | Рекомендация | Причина
-------- | ------------ | -------
Неизменяемость | Предпочитать `val` и отсутствие изменяемого состояния, когда это возможно | Потокобезопасность (для полностью неизменяемых), предсказуемость
Null-безопасность | Явно выбирать nullable vs not-null | Безопасность типов, ясное намерение
`equals`/`hashCode` | Использовать `data class` или переопределять при значимой семантике | Корректная работа `Set`/`Map`, логическое равенство
`toString` | Делать представление читаемым | Удобство отладки и логирования
Размер | Держать типы разумно компактными при частом создании/копировании | Производительность
Наследование | Предпочитать final/sealed; `open` — только осознанно | Контроль иерархии, исчерпывающие проверки, меньше неожиданностей

Также см.: [[c-kotlin]]

## Answer (EN)

Reference types in Kotlin should meet the following criteria for good design:

### 1. Immutability (When Required by Architecture)

Use immutable types when possible and when the domain model does not require mutation:
```kotlin
// Good: Immutable data class
data class User(val name: String, val email: String)

// Less preferred when immutability is desired
data class User(var name: String, var email: String)
```

Notes:
- Objects that are fully immutable (no mutable fields, no exposed mutable internal state) are inherently thread-safe for concurrent reads.
- Immutable objects are easier to reason about and safer to share.
- Such types are safe to use as `Map` keys or in `Set`, assuming `equals`/`hashCode` are defined consistently with their state.

### 2. Nullability (`nullable` or `not-null`)

Choose based on domain requirements and make absence explicit:
```kotlin
// Not-null when value is always present
data class User(
    val id: String,         // Always required
    val email: String       // Always required
)

// Nullable when value may be absent
data class UserProfile(
    val bio: String?,       // Optional bio
    val avatar: String?     // Optional avatar URL
)
```

This leverages Kotlin's type system to make nullability explicit and enforced by the compiler.

### 3. Implement Core Methods (for Collections and Debugging)

When instances participate in collections or equality-sensitive logic, ensure semantics of equality and hashing are correct:
```kotlin
// Data classes auto-generate:
// - equals()
// - hashCode()
// - toString()
data class Person(val name: String, val age: Int)

// Manual implementation for non-data classes when needed
class CustomType(val value: Int) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is CustomType) return false
        return value == other.value
    }

    override fun hashCode(): Int = value.hashCode()

    override fun toString(): String = "CustomType(value=$value)"
}
```

Why it matters:
```kotlin
val set = setOf(person1, person2)       // Relies on equals/hashCode for uniqueness
val map = mapOf(person1 to "data")     // Relies on equals/hashCode for key lookup
println(person1)                        // Readable toString helps debugging
```

All classes inherit `equals`, `hashCode`, and `toString` from `Any`, but you should override them (or use data classes) when the default identity-based behavior is not appropriate.

### 4. Lightweight (If Frequently Created or Copied)

Keep types reasonably small and focused, especially if they are created or copied often:
```kotlin
// Small, focused value-like type
data class Point(val x: Int, val y: Int)

// Heavier aggregate
data class HeavyObject(
    val largeArray: IntArray,
    val bigMap: Map<String, String>,
    val complexData: List<ComplexType>
)
```

Consider:
- Avoid unnecessary fields in frequently used types.
- Understand that `data class` `copy()` performs a shallow copy: it copies references to nested objects and collections, not their contents.
- Profile if performance is critical; large object graphs or excessive allocations can be problematic.

### 5. Final or Sealed (If Behavior is Fixed)

Prefer `final` (the default) or `sealed` when you want a controlled type hierarchy:
```kotlin
// Default: final class
data class User(val name: String)  // Cannot be inherited by default

// Sealed: restricted hierarchy (subclasses must be in the same file)
sealed class Result<out T>

data class Success<T>(val data: T) : Result<T>()

data class Error(val message: String) : Result<Nothing>()

// Open only when inheritance is explicitly intended
open class BaseEntity {
    open fun validate(): Boolean = true
}
```

Benefits:
- Prevents unexpected subclassing.
- Enables exhaustive `when` expressions with sealed hierarchies (in the same module or with proper visibility).
- Can enable better compiler checks and optimizations.

### 6. Reference Semantics Awareness

Kotlin classes (including `data class`) are reference types on the JVM and most common targets:
- Collections store references to objects, not copies.
- Mutating a mutable object through one reference is visible through all references to that object.
- Design your API so this aliasing either does not happen (immutability) or is controlled and documented.

### Summary Checklist

Criterion | Guideline | Reason
-------- | --------- | ------
Immutability | Prefer `val` and no mutable state when possible | Thread-safety (for fully immutable), predictability
Nullability | Use nullable vs not-null explicitly | Type safety, clear intent
`equals`/`hashCode` | Use data classes or override when semantics matter | Correct `Set`/`Map` behavior, logical equality
`toString` | Provide readable representation | Debugging, logging
Size | Keep types reasonable if created/copied often | Performance
Inheritance | Prefer final/sealed; use open intentionally | Prevent unwanted subclassing, enable checks

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этих критериев от подхода в Java?
- Когда вы бы применили эти критерии на практике?
- Каковы распространённые ошибки, которых следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-interface-vs-abstract-class--kotlin--medium]]
- [[q-linkedlist-arraylist-insert-behavior--kotlin--medium]]

## Related Questions

- [[q-interface-vs-abstract-class--kotlin--medium]]
- [[q-linkedlist-arraylist-insert-behavior--kotlin--medium]]
