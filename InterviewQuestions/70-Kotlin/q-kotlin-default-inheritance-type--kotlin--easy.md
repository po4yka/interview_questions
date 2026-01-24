---
'---id': lang-215
title: Kotlin Default Inheritance Type / Тип наследования по умолчанию в Kotlin
aliases: []
topic: kotlin
subtopics:
- classes
- functions
- types
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-inheritance
- c-kotlin
- q-abstract-class-vs-interface--kotlin--medium
created: 2025-10-15
updated: 2025-11-11
tags:
- difficulty/easy
- kotlin/classes
anki_cards:
- slug: q-kotlin-default-inheritance-type--kotlin--easy-0-en
  language: en
  anki_id: 1768326288732
  synced_at: '2026-01-23T17:03:51.299217'
- slug: q-kotlin-default-inheritance-type--kotlin--easy-0-ru
  language: ru
  anki_id: 1768326288756
  synced_at: '2026-01-23T17:03:51.301222'
---
# Вопрос (RU)
> Какой тип наследования по умолчанию используется для классов в Kotlin?

# Question (EN)
> What is the default inheritance type for classes in Kotlin?

---

## Ответ (RU)

В Kotlin **все классы по умолчанию являются `final`**, то есть они не могут быть унаследованы. Чтобы сделать класс наследуемым, необходимо явно пометить его ключевым словом **`open`**.

**По умолчанию (`final`):**
```kotlin
class FinalClass  // Не может быть унаследован

// Это НЕ скомпилируется:
// class Derived : FinalClass()  // Ошибка: Этот тип final, поэтому его нельзя наследовать
```

**Открыт для наследования (`open`):**
```kotlin
open class BaseClass  // Может быть унаследован

class Derived : BaseClass()  // OK
```

**Почему `final` по умолчанию?**

1. Рекомендация "Effective Java": "Проектируйте для наследования или запрещайте его".
2. Безопасность: предотвращает неожиданное поведение при наследовании.
3. Производительность: `final`-классы позволяют компилятору выполнять оптимизации.
4. Явное намерение: заставляет явно проектировать классы для наследования.

**Сравнение с Java:**

| Язык | По умолчанию | Для разрешения наследования |
|------|--------------|-----------------------------|
| Kotlin | `final` (закрыт) | Пометить как `open` |
| Java | Открыт (можно наследовать) | Пометить как `final` для предотвращения |

**Методы также следуют этому правилу:**
```kotlin
open class Base {
    fun finalMethod() {}  // Не может быть переопределён (`final` по умолчанию)

    open fun openMethod() {}  // Может быть переопределён
}

class Derived : Base() {
    // override fun finalMethod() {}  // Ошибка

    override fun openMethod() {}  // OK
}
```

**Абстрактные классы всегда открыты для наследования:**
```kotlin
abstract class AbstractBase  // Не нужно ключевое слово `open`

class Derived : AbstractBase()  // OK
```

**`sealed`-классы (ограниченное наследование):**
```kotlin
sealed class Result  // Подклассы ограничены тем же пакетом (JVM) или модулем (другие таргеты)

class Success : Result()
class Error : Result()
```

**Лучшие практики:**
- Оставляйте классы `final` по умолчанию.
- Используйте `open` только когда наследование намеренно.
- Рассматривайте `sealed` для контролируемых, закрытых иерархий.
- Используйте `abstract`, когда подклассы должны реализовать поведение.

## Answer (EN)

In Kotlin, **all classes are `final` by default**, meaning they cannot be inherited. To make a class inheritable, you must explicitly mark it with the **`open` keyword**.

**Default (`final`):**
```kotlin
class FinalClass  // Cannot be inherited

// This will NOT compile:
// class Derived : FinalClass()  // Error: This type is final, so it cannot be inherited from
```

**Open for inheritance (`open`):**
```kotlin
open class BaseClass  // Can be inherited

class Derived : BaseClass()  // OK
```

**Why `final` by default?**

1. Effective Java recommendation: "Design for inheritance or prohibit it".
2. Safety: prevents unexpected behavior from inheritance.
3. Performance: `final` classes allow compiler optimizations.
4. Explicit intent: forces developers to explicitly design for inheritance.

**Comparison with Java:**

| Language | Default | To allow inheritance |
|----------|---------|---------------------|
| Kotlin | `final` (closed) | Mark with `open` |
| Java | Open (can be inherited) | Mark with `final` to prevent |

**Methods also follow this rule:**
```kotlin
open class Base {
    fun finalMethod() {}  // Cannot be overridden (`final` by default)

    open fun openMethod() {}  // Can be overridden
}

class Derived : Base() {
    // override fun finalMethod() {}  // Error

    override fun openMethod() {}  // OK
}
```

**Abstract classes are always open to inheritance:**
```kotlin
abstract class AbstractBase  // No need for `open`

class Derived : AbstractBase()  // OK
```

**Sealed classes (restricted inheritance):**
```kotlin
sealed class Result  // Subclasses are restricted to the same package (JVM) or module (other targets)

class Success : Result()
class Error : Result()
```

**Best practice:**
- Keep classes `final` by default.
- Use `open` only when inheritance is intentional.
- Consider `sealed` for controlled, closed hierarchies.
- Use `abstract` when subclasses must implement behavior.

## Дополнительные Вопросы (RU)

- В чём разница между `abstract` и `interface` в Kotlin?
- Почему `sealed`-иерархии помогают делать исчерпывающие `when`-выражения?
- Какие ещё способы ограничения наследования предоставляет Kotlin (например, `sealed interface`)?
- Как `final` по умолчанию влияет на проектирование библиотек?
- В чём отличие подхода Kotlin от Java с точки зрения безопасности API?

## Follow-ups

- What is the difference between `abstract` and `interface` in Kotlin?
- Why do `sealed` hierarchies help with exhaustive `when` expressions?
- What other ways to restrict inheritance does Kotlin provide (e.g., `sealed interface`)?
- How does `final` by default influence library API design?
- How does Kotlin's approach differ from Java in terms of API safety?

## Related Questions

- [[q-abstract-class-vs-interface--kotlin--medium]]

## Ссылки (RU)

- [[q-abstract-class-vs-interface--kotlin--medium]]

## References

- [[q-abstract-class-vs-interface--kotlin--medium]]
