---
id: lang-085
title: Kotlin Java Equality Operators / Операторы равенства Kotlin и Java
aliases:
- Kotlin Java Equality Operators
- Операторы равенства Kotlin и Java
topic: kotlin
subtopics:
- operators
- type-system
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-equality
- c-kotlin
created: 2025-10-15
updated: 2025-11-10
tags:
- comparison
- difficulty/medium
- equality
- java
- kotlin
- operators
anki_cards:
- slug: lang-085-0-en
  language: en
  anki_id: 1768326290681
  synced_at: '2026-01-23T17:03:51.463444'
- slug: lang-085-0-ru
  language: ru
  anki_id: 1768326290706
  synced_at: '2026-01-23T17:03:51.465017'
---
# Вопрос (RU)
> Чем отличаются двойное равно в Java и Kotlin?

# Question (EN)
> What is the difference between double equals in Java and Kotlin?

## Ответ (RU)

Kotlin имеет два оператора равенства: `==` для структурного равенства и `===` для ссылочного равенства. В отличие от Java, оператор `==` в Kotlin ведет себя как null-safe обертка над `equals()` для ссылочных типов.

См. также: [[c-kotlin]], [[c-equality]].

### Структурное Равенство (`==`)
Сравнивает значения (для ссылочных типов вызывает безопасно `equals()`):
```kotlin
val a = "Hello"
val b = "Hello"
println(a == b)  // true (одинаковое содержимое)

data class Person(val name: String)
val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 == p2)  // true (data классы авто-реализуют equals)
```

Для ссылочных типов выражение `a == b` компилируется в `a?.equals(b) ?: (b === null)`, поэтому оно:
- не выбрасывает NPE при `a == null`;
- корректно обрабатывает сравнение с `null`.

### Ссылочное Равенство (`===`)
Сравнивает ссылки (тот же объект):
```kotlin
val a = "Hello"
val b = "Hello"
println(a === b)  // может быть true из-за интернирования строк, но это деталь реализации, а не гарантия языка

val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 === p2)  // false (разные объекты)

val p3 = p1
println(p1 === p3)  // true (та же ссылка)
```

### Сравнение С Java

| Операция | Kotlin | Java |
|----------|--------|------|
| Равенство значений | `==` (null-safe, вызывает `equals()` для ссылочных типов) | `.equals()` |
| Равенство ссылок | `===` | `==` |
| Null-safe сравнение | `==` | Ручная проверка null |

### Java Interop
```kotlin
// Java код
String s1 = new String("Hello");
String s2 = new String("Hello");

// В Kotlin
s1 == s2   // true (вызывает equals())
s1 === s2  // false (разные объекты)

// В Java
s1.equals(s2)  // true
s1 == s2       // false
```

### Null Безопасность
```kotlin
val a: String? = null
val b: String? = null

a == b   // true (оба null)
a === b  // true (оба null ссылка)

a == "text"  // false (null-safe, не выбрасывает NPE)
```

### Лучшие Практики
- Используйте `==` для сравнения значений.
- Используйте `===` только когда нужно равенство ссылок.
- Для коллекций `==` сравнивает содержимое.
- Data классы предоставляют структурное равенство автоматически.

## Answer (EN)

Kotlin has two equality operators: `==` for structural equality and `===` for referential equality. Unlike Java, the `==` operator in Kotlin acts as a null-safe wrapper around `equals()` for reference types.

See also: [[c-kotlin]], [[c-equality]].

### Structural Equality (`==`)
Compares values (for reference types safely calls `equals()`):
```kotlin
val a = "Hello"
val b = "Hello"
println(a == b)  // true (same content)

data class Person(val name: String)
val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 == p2)  // true (data classes auto-implement equals)
```

For reference types, `a == b` is compiled to `a?.equals(b) ?: (b === null)`, so it:
- does not throw NPE when `a` is null;
- correctly handles comparison with `null`.

### Referential Equality (`===`)
Compares references (same object):
```kotlin
val a = "Hello"
val b = "Hello"
println(a === b)  // may be true due to string interning, but this is an implementation detail, not a language guarantee

val p1 = Person("Alice")
val p2 = Person("Alice")
println(p1 === p2)  // false (different objects)

val p3 = p1
println(p1 === p3)  // true (same reference)
```

### Comparison with Java

| Operation | Kotlin | Java |
|-----------|--------|------|
| Value equality | `==` (null-safe, calls `equals()` for reference types) | `.equals()` |
| Reference equality | `===` | `==` |
| Null-safe comparison | `==` | Manual null check |

### Java Interop
```kotlin
// Java code
String s1 = new String("Hello");
String s2 = new String("Hello");

// In Kotlin
s1 == s2   // true (calls equals())
s1 === s2  // false (different objects)

// In Java
s1.equals(s2)  // true
s1 == s2       // false
```

### Null Safety
```kotlin
val a: String? = null
val b: String? = null

a == b   // true (both null)
a === b  // true (both null reference)

a == "text"  // false (null-safe, doesn't throw NPE)
```

### Best Practices
- Use `==` for value comparison.
- Use `===` only when you need reference equality.
- For collections, `==` compares contents.
- Data classes provide structural equality automatically.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого поведения от Java?
- Когда вы бы использовали это на практике?
- Каких типичных ошибок следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- [[q-kotlin-partition-function--kotlin--easy]]
- [[q-kotlin-null-checks-methods--kotlin--easy]]
- [[q-kotlin-non-inheritable-class--kotlin--easy]]

## Related Questions

- [[q-kotlin-partition-function--kotlin--easy]]
- [[q-kotlin-null-checks-methods--kotlin--easy]]
- [[q-kotlin-non-inheritable-class--kotlin--easy]]
