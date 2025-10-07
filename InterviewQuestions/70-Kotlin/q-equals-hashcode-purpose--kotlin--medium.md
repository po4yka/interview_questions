---
tags:
  - kotlin
  - object-comparison
  - hashmap
difficulty: medium
status: draft
---

# Зачем нужны методы equals и hashcode?

**English**: Why are equals and hashCode methods needed?

## Answer

Методы `equals()` и `hashCode()` играют центральную роль в сравнении объектов и управлении ими в коллекциях.

### equals(Object obj)

Определяет равенство объектов по содержимому вместо сравнения ссылок.

**Без переопределения equals()**:

```kotlin
class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // false (сравнение ссылок)
```

**С переопределением equals()** (автоматически в data class):

```kotlin
data class User(val name: String, val age: Int)

val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

println(user1 == user2)  // true (сравнение по содержимому)
```

### hashCode()

Возвращает хеш-код объекта для использования в хеш-таблицах (HashMap, HashSet и т.д.).

**Пример использования в HashMap**:

```kotlin
data class User(val name: String, val age: Int)

val users = HashMap<User, String>()
users[User("Alice", 30)] = "Engineer"

// Поиск работает, потому что hashCode() одинаковый для равных объектов
println(users[User("Alice", 30)])  // "Engineer"
```

### Контракт между equals() и hashCode()

**Критически важно соблюдать**:

1. **Если `a.equals(b)` возвращает true, то `a.hashCode()` должен равняться `b.hashCode()`**

```kotlin
val user1 = User("Alice", 30)
val user2 = User("Alice", 30)

if (user1 == user2) {
    // hashCode() должен быть одинаковым
    assert(user1.hashCode() == user2.hashCode())
}
```

2. **Если `a.equals(b)` возвращает false, hashCode() может быть одинаковым или разным**

3. **Если `a.hashCode() != b.hashCode()`, то `a.equals(b)` должен возвращать false**

### Проблемы при нарушении контракта

**Неправильная реализация**:

```kotlin
class BrokenUser(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is BrokenUser) return false
        return name == other.name && age == other.age
    }

    // НЕ переопределён hashCode()!
}

val map = HashMap<BrokenUser, String>()
val user1 = BrokenUser("Alice", 30)
map[user1] = "Engineer"

val user2 = BrokenUser("Alice", 30)
println(map[user2])  // null ← ОШИБКА! Не найдёт, хотя user1 == user2
```

**Правильная реализация**:

```kotlin
class CorrectUser(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        if (other !is CorrectUser) return false
        return name == other.name && age == other.age
    }

    override fun hashCode(): Int {
        var result = name.hashCode()
        result = 31 * result + age
        return result
    }
}

// Или просто используйте data class:
data class User(val name: String, val age: Int)
// equals() и hashCode() генерируются автоматически
```

### Использование в коллекциях

```kotlin
data class User(val name: String, val age: Int)

// HashSet использует hashCode() для быстрого поиска
val users = hashSetOf<User>()
users.add(User("Alice", 30))
users.add(User("Alice", 30))  // Не добавится (дубликат)
println(users.size)  // 1

// HashMap использует hashCode() для индексации
val userRoles = hashMapOf<User, String>()
userRoles[User("Alice", 30)] = "Engineer"
println(userRoles[User("Alice", 30)])  // "Engineer"
```

**English**: `equals()` defines object equality by content instead of reference comparison. `hashCode()` returns a hash code for use in hash-based collections. The contract is critical: equal objects must have equal hash codes. Data classes automatically implement both correctly.
