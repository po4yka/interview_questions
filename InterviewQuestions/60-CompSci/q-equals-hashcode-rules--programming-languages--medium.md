---
tags:
  - equals
  - hashcode
  - contracts
  - collections
  - easy_kotlin
  - programming-languages
  - kotlin
  - java
  - object-methods
difficulty: medium
---

# Какие существуют правила для методов equals и hashcode?

**English**: What rules exist for equals and hashCode methods?

## Answer

Methods `equals()` and `hashCode()` are important for correct operation of collections such as HashSet, HashMap, and HashTable.

**equals() contract:**
1. **Reflexive**: `x.equals(x)` must return true
2. **Symmetric**: If `x.equals(y)` is true, then `y.equals(x)` must be true
3. **Transitive**: If `x.equals(y)` and `y.equals(z)` are true, then `x.equals(z)` must be true
4. **Consistent**: Multiple calls return same result if no data changes
5. **Null comparison**: `x.equals(null)` must return false

**hashCode() contract:**
1. **Internal consistency**: hashCode must return same value if object hasn't changed
2. **Consistency with equals**: If `x.equals(y)` is true, then `x.hashCode() == y.hashCode()` must be true
3. **Optional distinction**: Different objects may have same hashCode (collisions allowed), but better performance if different

**Golden rule**: When you override `equals()`, you MUST override `hashCode()`!

## Ответ

Методы equals(Object obj) и hashCode() имеют важное значение для корректной работы коллекций...

