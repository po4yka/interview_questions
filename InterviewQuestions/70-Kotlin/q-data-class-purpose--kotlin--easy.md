---
tags:
  - kotlin
  - data-classes
  - code-generation
difficulty: easy
---

# Для чего нужен data class?

**English**: What is a data class used for?

## Answer

Классы данных предназначены для хранения данных. Основная их задача — упростить создание классов, которые будут использоваться преимущественно для хранения данных, не добавляя при этом лишнего шаблонного кода.

Чтобы определить класс данных, достаточно добавить ключевое слово `data` перед объявлением класса:

```kotlin
data class User(val name: String, val age: Int)
```

### Особенности и преимущества

**Автоматическая генерация функций:**
- `equals()` - сравнение объектов по содержимому
- `hashCode()` - хеш-код для использования в коллекциях
- `toString()` - строковое представление объекта
- `componentN()` - деструктуризация объектов
- `copy()` - создание копии с изменением отдельных полей

```kotlin
val user1 = User("Alice", 30)
val user2 = user1.copy(age = 31)  // Создаём копию с другим возрастом

// Деструктуризация
val (name, age) = user1
println("$name is $age years old")
```

### Использование

- Сокращает количество шаблонного кода
- Упрощает создание моделей данных
- Повышает читабельность кода
- Обеспечивает корректную работу с коллекциями (благодаря equals/hashCode)

**English**: Data classes are designed for storing data. Their main purpose is to simplify the creation of classes primarily used for data storage without adding boilerplate code. Kotlin automatically generates `equals()`, `hashCode()`, `toString()`, `componentN()`, and `copy()` functions for data classes.
