---
id: kotlin-236
title: "Visibility Modifiers in Kotlin / Модификаторы видимости в Kotlin"
aliases: ["Visibility Modifiers", "Модификаторы видимости"]
topic: kotlin
subtopics: [visibility-modifiers, access-modifiers, encapsulation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-access-modifiers--kotlin--medium, q-inheritance-open-final--kotlin--medium, q-inner-nested-classes--kotlin--medium]
created: "2025-10-12"
updated: 2025-01-25
tags: [kotlin, visibility-modifiers, access-modifiers, encapsulation, kotlin-features, difficulty/medium]
sources: [https://kotlinlang.org/docs/visibility-modifiers.html]
---

# Вопрос (RU)
> Какие модификаторы видимости есть в Kotlin и чем они отличаются?

# Question (EN)
> What visibility modifiers does Kotlin have and what's the difference?

---

## Ответ (RU)

**Теория модификаторов видимости:**
Kotlin имеет 4 уровня видимости: `private`, `protected`, `internal`, `public`. В отличие от Java, default modifier - `public`, а не `package-private`. `internal` позволяет видеть элемент в пределах одного модуля - основная инкапсуляция для модульных проектов. В Kotlin нет package-private модификатора.

**Уровни видимости:**
- **public**: Видим везде (default модификатор)
- **internal**: Видим внутри модуля
- **protected**: Видим в классе и наследниках (только для members класса)
- **private**: Видим только в пределах объявления

**Базовые примеры:**
```kotlin
// ✅ public (по умолчанию)
class PublicClass {
    fun publicMethod() {} // public
}

// ✅ internal - видим только в модуле
internal class InternalClass {
    internal fun internalMethod() {}
}

// ✅ private - только внутри класса
class Example {
    private fun privateMethod() {}

    fun publicMethod() {
        privateMethod() // ✅ Доступно
    }
}

// ❌ Ошибка - недоступен приватный метод
// val ex = Example()
// ex.privateMethod() // Ошибка!
```

**Protected visibility:**
```kotlin
// ✅ protected - видим в классе и наследниках
open class Base {
    protected val value = 42
    protected fun protectedMethod() {}
}

class Derived : Base() {
    fun accessProtected() {
        println(value) // ✅ Доступно в наследнике
        protectedMethod() // ✅ Доступно в наследнике
    }
}

// ❌ Недоступно снаружи
fun test() {
    val base = Base()
    // base.protectedMethod() // Ошибка!
}
```

**Internal visibility:**
```kotlin
// ✅ internal - модульная инкапсуляция
// Файл: utils/network.kt (модуль A)
internal class NetworkHelper {
    internal fun connect() {}
}

// Файл: main.kt (модуль A)
import utils.*
fun main() {
    val helper = NetworkHelper() // ✅ Доступно
    helper.connect() // ✅ Доступно
}

// Файл: client/app.kt (модуль B)
import utils.*
fun usage() {
    // val helper = NetworkHelper() // ❌ Недоступно - другой модуль
}
```

**Private visibility (вложенные классы):**
```kotlin
// ✅ private классы и функции
class Outer {
    private class Nested // Приватный вложенный класс

    private fun outerMethod() {}

    inner class Inner {
        fun accessOuter() {
            outerMethod() // ✅ Доступ к приватному методу внешнего класса
        }
    }
}

// ❌ Nested недоступен снаружи
// val nested = Outer.Nested() // Ошибка!
```

**Конструкторы и properties:**
```kotlin
// ✅ Приватный конструктор (Singleton pattern)
class Database private constructor() {
    companion object {
        private var instance: Database? = null

        fun getInstance(): Database {
            if (instance == null) {
                instance = Database()
            }
            return instance!!
        }
    }
}

// ❌ Нельзя создать напрямую
// val db = Database() // Ошибка!

// ✅ Приватные setters
class User(val name: String) {
    private var password: String = ""

    fun setPassword(newPassword: String) {
        password = newPassword // ✅ Можно установить
    }

    fun getPassword(): String {
        return "***" // ❌ Нельзя получить реальный пароль
    }
}
```

**Package-level visibility:**
```kotlin
// ✅ Файл: helpers.kt
private fun privateHelper() {} // Приватная функция файла
internal fun internalHelper() {} // Видна в модуле
public fun publicHelper() {} // Видна везде

// Файл: main.kt (тот же модуль)
fun test() {
    // privateHelper() // ❌ Недоступно - другой файл
    internalHelper() // ✅ Доступно - тот же модуль
    publicHelper() // ✅ Доступно
}
```

---

## Answer (EN)

**Visibility Modifiers Theory:**
Kotlin has 4 visibility levels: `private`, `protected`, `internal`, `public`. Unlike Java, default modifier is `public`, not package-private. `internal` allows seeing element within one module - main encapsulation for modular projects. Kotlin has no package-private modifier.

**Visibility Levels:**
- **public**: Visible everywhere (default modifier)
- **internal**: Visible within module
- **protected**: Visible in class and inheritors (only for class members)
- **private**: Visible only within declaring scope

**Basic Examples:**
```kotlin
// ✅ public (default)
class PublicClass {
    fun publicMethod() {} // public
}

// ✅ internal - visible only in module
internal class InternalClass {
    internal fun internalMethod() {}
}

// ✅ private - only inside class
class Example {
    private fun privateMethod() {}

    fun publicMethod() {
        privateMethod() // ✅ Accessible
    }
}

// ❌ Error - private method not accessible
// val ex = Example()
// ex.privateMethod() // Error!
```

**Protected Visibility:**
```kotlin
// ✅ protected - visible in class and inheritors
open class Base {
    protected val value = 42
    protected fun protectedMethod() {}
}

class Derived : Base() {
    fun accessProtected() {
        println(value) // ✅ Accessible in inheritor
        protectedMethod() // ✅ Accessible in inheritor
    }
}

// ❌ Not accessible from outside
fun test() {
    val base = Base()
    // base.protectedMethod() // Error!
}
```

**Internal Visibility:**
```kotlin
// ✅ internal - module-level encapsulation
// File: utils/network.kt (module A)
internal class NetworkHelper {
    internal fun connect() {}
}

// File: main.kt (module A)
import utils.*
fun main() {
    val helper = NetworkHelper() // ✅ Accessible
    helper.connect() // ✅ Accessible
}

// File: client/app.kt (module B)
import utils.*
fun usage() {
    // val helper = NetworkHelper() // ❌ Not accessible - different module
}
```

**Private Visibility (Nested Classes):**
```kotlin
// ✅ private classes and functions
class Outer {
    private class Nested // Private nested class

    private fun outerMethod() {}

    inner class Inner {
        fun accessOuter() {
            outerMethod() // ✅ Access to private method of outer class
        }
    }
}

// ❌ Nested not accessible from outside
// val nested = Outer.Nested() // Error!
```

**Constructors and Properties:**
```kotlin
// ✅ Private constructor (Singleton pattern)
class Database private constructor() {
    companion object {
        private var instance: Database? = null

        fun getInstance(): Database {
            if (instance == null) {
                instance = Database()
            }
            return instance!!
        }
    }
}

// ❌ Cannot create directly
// val db = Database() // Error!

// ✅ Private setters
class User(val name: String) {
    private var password: String = ""

    fun setPassword(newPassword: String) {
        password = newPassword // ✅ Can set
    }

    fun getPassword(): String {
        return "***" // ❌ Cannot get real password
    }
}
```

**Package-level Visibility:**
```kotlin
// ✅ File: helpers.kt
private fun privateHelper() {} // Private file function
internal fun internalHelper() {} // Visible in module
public fun publicHelper() {} // Visible everywhere

// File: main.kt (same module)
fun test() {
    // privateHelper() // ❌ Not accessible - different file
    internalHelper() // ✅ Accessible - same module
    publicHelper() // ✅ Accessible
}
```

## Follow-ups

- When to use internal vs private?
- How does visibility work with sealed classes?
- Visibility in multi-module projects?

## References

- [[c-oop-fundamentals]]
- https://kotlinlang.org/docs/visibility-modifiers.html

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-kotlin-access-modifiers--kotlin--medium]] - Access modifiers
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-inner-nested-classes--kotlin--medium]] - Nested classes

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types
