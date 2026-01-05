---
id: concept-002
title: Equality / Равенство объектов
aliases: [Equality, Equals, HashCode, Равенство, Сравнение объектов]
kind: concept
summary: Mechanisms for comparing objects for equality, including structural equality (equals/==) and referential equality (===), and the contract between equals() and hashCode().
links: []
created: 2025-11-05
updated: 2025-11-05
tags: [concept, equality, java, kotlin, oop]
---

# Summary (EN)

**Equality** in object-oriented programming refers to mechanisms for comparing whether two objects are considered "equal". There are two main types:

**Structural Equality (equals / ==)**:
- Compares the content/state of objects
- In Java: `obj1.equals(obj2)` method
- In Kotlin: `==` operator (calls `equals()` under the hood)
- Can be customized by overriding `equals()`

**Referential Equality (===)**:
- Compares whether two references point to the same object in memory
- In Java: `==` operator
- In Kotlin: `===` operator
- Cannot be overridden

**equals() and hashCode() Contract**:
When overriding `equals()`, you MUST also override `hashCode()` to maintain the contract:
- If `a.equals(b)` returns true, then `a.hashCode() == b.hashCode()` MUST be true
- If two objects are equal, their hash codes must be equal
- If two objects are not equal, their hash codes MAY be equal (collision) but SHOULD be different for performance

Violating this contract breaks hash-based collections (HashMap, HashSet).

# Сводка (RU)

**Равенство** в объектно-ориентированном программировании — это механизмы сравнения объектов на "равенство". Существует два основных типа:

**Структурное равенство (equals / ==)**:
- Сравнивает содержимое/состояние объектов
- В Java: метод `obj1.equals(obj2)`
- В Kotlin: оператор `==` (вызывает `equals()` внутри)
- Можно настроить через переопределение `equals()`

**Референциальное равенство (===)**:
- Сравнивает, указывают ли две ссылки на один и тот же объект в памяти
- В Java: оператор `==`
- В Kotlin: оператор `===`
- Переопределить нельзя

**Контракт equals() и hashCode()**:
При переопределении `equals()` НЕОБХОДИМО также переопределить `hashCode()` для соблюдения контракта:
- Если `a.equals(b)` возвращает true, то `a.hashCode() == b.hashCode()` ДОЛЖНО быть true
- Если два объекта равны, их хеш-коды должны быть равны
- Если два объекта не равны, их хеш-коды МОГУТ быть равны (коллизия), но ДОЛЖНЫ различаться для производительности

Нарушение этого контракта ломает коллекции на основе хеша (HashMap, HashSet).

## Use Cases / Trade-offs

**When to override equals()**:
- Value objects / data classes: Objects representing values (Point, Person, Money)
- Collections membership: Need to use object as HashMap key or HashSet element
- Business logic: Domain-specific equality (two Users are equal if they have same ID)

**Default behavior** (if not overridden):
- `equals()` defaults to referential equality (`this == other`)
- Only objects that are the same instance are considered equal

**Trade-offs**:
- **Performance**: Custom `equals()` can be expensive for deep object graphs
- **Correctness**: Must maintain equals/hashCode contract or break collections
- **Immutability**: Changing object state after adding to HashSet/HashMap causes bugs

**Best practices**:
- Use IDE generation or Kotlin `data class` to ensure correct implementation
- Include all fields used in `equals()` in `hashCode()`
- Make value objects immutable to avoid hash-based collection bugs

## References

- [Effective Java, Item 10: Obey the general contract when overriding equals](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [Kotlin Equality Documentation](https://kotlinlang.org/docs/equality.html)
- [Java Object.equals() Specification](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html#equals(java.lang.Object))
- [Wikipedia: Object Equality](https://en.wikipedia.org/wiki/Relational_operator#Equality)
