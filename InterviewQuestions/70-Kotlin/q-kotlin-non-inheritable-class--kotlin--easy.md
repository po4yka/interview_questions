---
id: lang-091
title: Kotlin Non Inheritable Class / Не наследуемый класс в Kotlin
aliases:
- Kotlin Non Inheritable Class
- Не наследуемый класс в Kotlin
topic: kotlin
subtopics:
- inheritance
- type-system
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-common-coroutine-mistakes--kotlin--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- class-design
- classes
- difficulty/easy
- final
- inheritance
- keywords
- kotlin
- open
anki_cards:
- slug: lang-091-0-en
  language: en
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - inheritance
  - type-system
- slug: lang-091-0-ru
  language: ru
  difficulty: 0.3
  tags:
  - Kotlin
  - difficulty::easy
  - inheritance
  - type-system
---
# Вопрос (RU)
> Как в Kotlin определить класс, который не может быть унаследован?

# Question (EN)
> How to define a class in Kotlin that cannot be inherited?

## Ответ (RU)

В Kotlin, чтобы определить класс, который не может быть унаследован, достаточно объявить его без ключевого слова `open`. По умолчанию все классы в Kotlin являются `final` и не могут быть унаследованы без явного указания `open` (или `abstract`, `sealed` и т.п.). Ключевое слово `final` можно использовать явно, но в определении класса это, как правило, избыточно.

**Поведение по умолчанию (`final`):**
```kotlin
class FinalClass  // Нельзя наследовать (по умолчанию final)

// Попытка наследования вызовет ошибку компиляции:
// class Derived : FinalClass()  // Ошибка: этот тип final и не может быть унаследован
```

**Явное использование `final` (опционально, уже по умолчанию):**
```kotlin
final class ExplicitlyFinalClass  // Избыточно, но допустимо

// То же самое, что:
class ImplicitlyFinalClass  // final по умолчанию
```

**Чтобы разрешить наследование, используйте `open`:**
```kotlin
open class OpenClass  // Может быть унаследован

class Derived : OpenClass()  // OK
```

**Запрещение дальнейшего наследования в иерархии:**
```kotlin
open class Base

open class Middle : Base()  // Можно наследовать дальше

class Final : Middle()  // Нельзя наследовать (final по умолчанию)

// Это не скомпилируется:
// class MoreDerived : Final()  // Ошибка: 'Final' является final и не может быть унаследован
```

**Явное запрещение переопределения унаследованных методов:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Запрещаем дальнейшее переопределение
}

class MoreDerived : Derived() {
    // override fun foo() {}  // Ошибка: foo является final
}
```

**Абстрактные и `sealed` классы (для контекста, не для запрета наследования):**
- `abstract`-классы по определению открыты для наследования и не используются для запрета наследования, а для задания базового контракта.
- `sealed`-классы допускают наследование, но строго ограничивают круг допустимых наследников:
  - наследники должны находиться в той же компиляционной единице (например, в том же модуле/`source set` или, в более старых версиях языка, в том же файле);
  - они не используются как механизм сделать класс полностью не-наследуемым для всех, а как механизм ограниченного и контролируемого наследования.

**Итоговая сводка:**

| Подход | Синтаксис | Наследуемый? |
|--------|-----------|--------------|
| Поведение по умолчанию (`final`) | `class MyClass` | Нет |
| Явный `final` | `final class MyClass` | Нет (избыточно) |
| `open` | `open class MyClass` | Да |
| `abstract` | `abstract class MyClass` | Да (открыт для наследования, не используется для запрета) |
| `sealed` | `sealed class MyClass` | Да, но наследники ограничены областью, определяемой правилами языка (ограниченное наследование) |

## Answer (EN)

In Kotlin, to define a class that cannot be inherited, you simply declare it without the `open` keyword. All classes in Kotlin are `final` by default and thus non-inheritable unless explicitly marked `open` (or `abstract`, `sealed`, etc.). The `final` keyword can be used explicitly, but for classes it's usually redundant.

**Default behavior (final):**
```kotlin
class FinalClass  // Cannot be inherited (final by default)

// Attempting to inherit will cause a compilation error:
// class Derived : FinalClass()  // Error: This type is final and cannot be inherited
```

**Explicit `final` keyword (optional, already default):**
```kotlin
final class ExplicitlyFinalClass  // Redundant, but allowed

// Same as:
class ImplicitlyFinalClass  // final by default
```

**To allow inheritance, use `open`:**
```kotlin
open class OpenClass  // Can be inherited

class Derived : OpenClass()  // OK
```

**Preventing further inheritance down the hierarchy:**
```kotlin
open class Base

open class Middle : Base()  // Can be inherited further

class Final : Middle()  // Cannot be inherited (final by default)

// This will NOT compile:
// class MoreDerived : Final()  // Error: 'Final' is final and cannot be inherited
```

**Explicitly preventing override of inherited methods:**
```kotlin
open class Base {
    open fun foo() {}
}

class Derived : Base() {
    final override fun foo() {}  // Prevent further overriding
}

class MoreDerived : Derived() {
    // override fun foo() {}  // Error: foo is final
}
```

**Abstract and sealed classes (for context, not to forbid inheritance):**
- `abstract` classes are, by definition, open for inheritance and are used to define a base contract, not to make a type non-inheritable.
- `sealed` classes allow inheritance but tightly restrict which classes can inherit from them:
  - inheritors must reside in the same compilation unit (e.g., same module/source set, or in older language versions — the same file);
  - they are a mechanism for controlled/limited inheritance, not for making a class completely non-inheritable.

**Summary:**

| Approach | Syntax | Inheritable? |
|----------|--------|-------------|
| Default (final) | `class MyClass` | No |
| Explicit final | `final class MyClass` | No (redundant) |
| Open | `open class MyClass` | Yes |
| Abstract | `abstract class MyClass` | Yes (open for inheritance; not used to forbid it) |
| Sealed | `sealed class MyClass` | Yes, with inheritors restricted by language rules (limited inheritance) |

**Best practice:**
- To make a class non-inheritable, just omit `open` (rely on the default `final` behavior).
- Use explicit `final` on members when you want to forbid further overriding in subclasses.

---

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия этого поведения от Java?
- Когда на практике стоит запрещать наследование класса?
- Какие распространенные ошибки следует избегать при работе с `final` и `open`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные Вопросы (RU)

- [[q-kotlin-generics--kotlin--hard]]
- [[q-common-coroutine-mistakes--kotlin--medium]]

## Related Questions

- [[q-kotlin-generics--kotlin--hard]]
- [[q-common-coroutine-mistakes--kotlin--medium]]
