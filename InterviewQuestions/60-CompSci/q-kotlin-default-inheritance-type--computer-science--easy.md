---
id: 20251012-12271111121
title: "Kotlin Default Inheritance Type / Тип наследования по умолчанию в Kotlin"
aliases: []
topic: computer-science
subtopics: [functions, type-system, class-features]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-coroutine-context-explained--kotlin--medium, q-repeatonlifecycle-android--kotlin--medium, q-java-kotlin-abstract-classes-difference--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/easy
---
# Какой тип наследования по умолчанию используется для классов в Kotlin?

# Question (EN)
> What is the default inheritance type for classes in Kotlin?

# Вопрос (RU)
> Какой тип наследования по умолчанию используется для классов в Kotlin?

---

## Answer (EN)

In Kotlin, **all classes are `final` by default**, meaning they cannot be inherited. To make a class inheritable, you must explicitly mark it with the **`open` keyword**.

**Default (final):**
```kotlin
class FinalClass  // Cannot be inherited

// This will NOT compile:
// class Derived : FinalClass()  // Error: This type is final, so it cannot be inherited from
```

**Open for inheritance:**
```kotlin
open class BaseClass  // Can be inherited

class Derived : BaseClass()  // OK
```

**Why final by default?**

1. **Effective Java recommendation**: "Design for inheritance or prohibit it"
2. **Safety**: Prevents unexpected behavior from inheritance
3. **Performance**: Final classes allow compiler optimizations
4. **Explicit intent**: Forces developers to explicitly design for inheritance

**Comparison with Java:**

| Language | Default | To allow inheritance |
|----------|---------|---------------------|
| Kotlin | `final` (closed) | Mark with `open` |
| Java | Open (can be inherited) | Mark with `final` to prevent |

**Methods also follow this rule:**
```kotlin
open class Base {
    fun finalMethod() {}  // Cannot be overridden (final by default)

    open fun openMethod() {}  // Can be overridden
}

class Derived : Base() {
    // override fun finalMethod() {}  // Error

    override fun openMethod() {}  // OK
}
```

**Abstract classes are always open:**
```kotlin
abstract class AbstractBase  // No need for 'open' keyword

class Derived : AbstractBase()  // OK
```

**Sealed classes (restricted inheritance):**
```kotlin
sealed class Result  // Subclasses must be in same file/package

class Success : Result()
class Error : Result()
```

**Best practice:**
- Keep classes `final` by default
- Use `open` only when inheritance is intentional
- Consider `sealed` for controlled hierarchies
- Use `abstract` when subclasses must implement behavior

---

## Ответ (RU)

В Kotlin **все классы по умолчанию являются `final`**, то есть они не могут быть унаследованы. Чтобы сделать класс наследуемым, необходимо явно пометить его ключевым словом **`open`**.

**По умолчанию (final):**
```kotlin
class FinalClass  // Не может быть унаследован

// Это НЕ скомпилируется:
// class Derived : FinalClass()  // Ошибка: Этот тип final, поэтому его нельзя наследовать
```

**Открыт для наследования:**
```kotlin
open class BaseClass  // Может быть унаследован

class Derived : BaseClass()  // OK
```

**Почему final по умолчанию?**

1. **Рекомендация Effective Java**: "Проектируйте для наследования или запрещайте его"
2. **Безопасность**: Предотвращает неожиданное поведение от наследования
3. **Производительность**: Final классы позволяют компилятору делать оптимизации
4. **Явное намерение**: Заставляет разработчиков явно проектировать для наследования

**Сравнение с Java:**

| Язык | По умолчанию | Для разрешения наследования |
|----------|---------|---------------------|
| Kotlin | `final` (закрыт) | Пометить как `open` |
| Java | Открыт (можно наследовать) | Пометить как `final` для предотвращения |

**Методы также следуют этому правилу:**
```kotlin
open class Base {
    fun finalMethod() {}  // Не может быть переопределён (final по умолчанию)

    open fun openMethod() {}  // Может быть переопределён
}

class Derived : Base() {
    // override fun finalMethod() {}  // Ошибка

    override fun openMethod() {}  // OK
}
```

**Abstract классы всегда открыты:**
```kotlin
abstract class AbstractBase  // Не нужно ключевое слово 'open'

class Derived : AbstractBase()  // OK
```

**Sealed классы (ограниченное наследование):**
```kotlin
sealed class Result  // Подклассы должны быть в том же файле/пакете

class Success : Result()
class Error : Result()
```

**Лучшие практики:**
- Оставляйте классы `final` по умолчанию
- Используйте `open` только когда наследование намеренно
- Рассмотрите `sealed` для контролируемых иерархий
- Используйте `abstract` когда подклассы должны реализовать поведение

## Related Questions

- [[q-coroutine-context-explained--kotlin--medium]]
- [[q-repeatonlifecycle-android--kotlin--medium]]
- [[q-java-kotlin-abstract-classes-difference--programming-languages--medium]]
