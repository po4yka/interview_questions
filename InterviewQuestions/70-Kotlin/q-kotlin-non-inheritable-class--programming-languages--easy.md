---
id: lang-091
title: "Kotlin Non Inheritable Class / Не наследуемый класс в Kotlin"
aliases: [Kotlin Non Inheritable Class, Не наследуемый класс в Kotlin]
topic: kotlin
subtopics: [inheritance, type-system]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-common-coroutine-mistakes--kotlin--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [class-design, classes, difficulty/easy, final, inheritance, keywords, open, kotlin]
---
# Вопрос (RU)
> Как в Kotlin определить класс, который не может быть унаследован?

# Question (EN)
> How to define a class in Kotlin that cannot be inherited?

## Ответ (RU)

В Kotlin, чтобы определить класс, который не может быть унаследован, достаточно объявить его без ключевого слова `open`. По умолчанию все классы в Kotlin являются `final` и не могут быть унаследованы без явного указания `open`. Ключевое слово `final` можно использовать явно, но в определении класса это, как правило, избыточно.

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

**Абстрактные и `sealed` классы:**
- `abstract`-классы по определению открыты для наследования и не используются для запрета наследования, а для задания базового контракта.
- `sealed`-классы допускают наследование, но строго ограничивают круг допустимых наследников областью, определяемой версией языка (например, тем же файлом или модулем/компиляционной единицей).

**Итоговая сводка:**

| Подход | Синтаксис | Наследуемый? |
|--------|-----------|--------------|
| Поведение по умолчанию (`final`) | `class MyClass` | Нет |
| Явный `final` | `final class MyClass` | Нет (избыточно) |
| `open` | `open class MyClass` | Да |
| `abstract` | `abstract class MyClass` | Да (абстрактные классы открыты для наследования) |
| `sealed` | `sealed class MyClass` | Да, но наследники ограничены допустимой областью (например, тем же файлом или модулем/компиляционной единицей) |

## Answer (EN)

In Kotlin, to define a class that cannot be inherited, you simply declare it without the `open` keyword. All classes in Kotlin are `final` by default and thus non-inheritable unless explicitly marked `open` (or `abstract`, etc.). The `final` keyword can be used explicitly, but for classes it's usually redundant.

**Default behavior (final):**
```kotlin
class FinalClass  // Cannot be inherited (final by default)

// Attempting to inherit will cause a compilation error:
// class Derived : FinalClass()  // Error: This type is final
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

**Summary:**

| Approach | Syntax | Inheritable? |
|----------|--------|-------------|
| Default (final) | `class MyClass` | No |
| Explicit final | `final class MyClass` | No (redundant) |
| Open | `open class MyClass` | Yes |
| Abstract | `abstract class MyClass` | Yes (abstract classes are open for inheritance) |
| Sealed | `sealed class MyClass` | Yes, but inheritors are restricted to the allowed scope defined by the language version (e.g. same file or same compilation unit/module) |

**Best practice:**
- To make a class non-inheritable, just omit `open` (rely on the default `final` behavior).
- Use explicit `final` on members when you want to forbid further overriding in subclasses.

---

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

- [[q-kotlin-generics--kotlin--hard]]
- [[q-common-coroutine-mistakes--kotlin--medium]]

## Related Questions

- [[q-kotlin-generics--kotlin--hard]]
- [[q-common-coroutine-mistakes--kotlin--medium]]
