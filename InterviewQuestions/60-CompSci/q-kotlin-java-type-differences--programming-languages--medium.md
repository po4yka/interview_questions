---
tags:
  - collections
  - comparison
  - java
  - kotlin
  - null-safety
  - programming-languages
  - type-inference
  - type-system
  - types
difficulty: medium
status: draft
---

# Чем типы в Kotlin отличаются от типов в Java

# Question (EN)
> How do Kotlin types differ from Java types?

# Вопрос (RU)
> Чем типы в Kotlin отличаются от типов в Java

---

## Answer (EN)

| Feature | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Variables cannot be null by default (`String` vs `String?`) | All objects can be null |
| **Collections** | Clear separation: `List` vs `MutableList` | No distinction (all mutable) |
| **Data Classes** | Automatic method generation with `data class` | Manual implementation required |
| **Type Inference** | Extensive: `val x = 10` | Limited (local variables with `var`) |
| **Smart Casts** | Automatic after `is` check | Explicit cast after `instanceof` |
| **Primitive Types** | No primitives (unified type system) | Separate primitives (`int`) and wrappers (`Integer`) |

**Examples:**

```kotlin
// Kotlin
val name: String = "John"        // Cannot be null
val nullable: String? = null     // Explicitly nullable
val list = listOf(1, 2, 3)       // Immutable
val x = 10                       // Type inferred

if (obj is String) {
    println(obj.length)          // Auto-cast
}
```

```java
// Java
String name = "John";             // Can be null
String nullable = null;           // No distinction
List<Integer> list = List.of(1, 2, 3); // Can be modified with reflection
int x = 10;                       // Must specify type

if (obj instanceof String) {
    println(((String) obj).length()); // Explicit cast
}
```

**Key differences:**
1. **Kotlin**: Null safety by default
2. **Kotlin**: Immutable/mutable collections distinction
3. **Kotlin**: Auto-generated methods for data classes
4. **Kotlin**: Better type inference
5. **Kotlin**: Smart casts after type checks

---

## Ответ (RU)

| Особенность | Kotlin | Java |
|---------|--------|------|
| **Null Safety** | Переменные не могут быть null по умолчанию (`String` vs `String?`) | Все объекты могут быть null |
| **Коллекции** | Четкое разделение: `List` vs `MutableList` | Нет различия (все изменяемые) |
| **Data классы** | Автоматическая генерация методов с `data class` | Требуется ручная реализация |
| **Вывод типов** | Обширный: `val x = 10` | Ограниченный (локальные переменные с `var`) |
| **Умные приведения** | Автоматические после проверки `is` | Явное приведение после `instanceof` |
| **Примитивные типы** | Нет примитивов (унифицированная система типов) | Отдельные примитивы (`int`) и обертки (`Integer`) |

**Примеры:**

```kotlin
// Kotlin
val name: String = "John"        // Не может быть null
val nullable: String? = null     // Явно nullable
val list = listOf(1, 2, 3)       // Неизменяемый
val x = 10                       // Тип выводится

if (obj is String) {
    println(obj.length)          // Автоматическое приведение
}
```

```java
// Java
String name = "John";             // Может быть null
String nullable = null;           // Нет различия
List<Integer> list = List.of(1, 2, 3); // Может быть изменен через рефлексию
int x = 10;                       // Нужно указать тип

if (obj instanceof String) {
    println(((String) obj).length()); // Явное приведение
}
```

**Ключевые различия:**
1. **Kotlin**: Null safety по умолчанию
2. **Kotlin**: Разделение изменяемых/неизменяемых коллекций
3. **Kotlin**: Автогенерация методов для data классов
4. **Kotlin**: Лучший вывод типов
5. **Kotlin**: Умные приведения после проверок типов

