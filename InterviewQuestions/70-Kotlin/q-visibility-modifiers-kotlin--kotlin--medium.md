---
id: kotlin-236
title: Visibility Modifiers in Kotlin / Модификаторы видимости в Kotlin
aliases:
- Visibility Modifiers
- Модификаторы видимости
topic: kotlin
subtopics:
- visibility-modifiers
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- q-access-modifiers--kotlin--medium
- q-inheritance-open-final--kotlin--medium
created: '2025-10-12'
updated: '2025-11-11'
tags:
- difficulty/medium
- kotlin
- visibility-modifiers
sources:
- https://kotlinlang.org/docs/visibility-modifiers.html
anki_cards:
- slug: kotlin-236-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - visibility-modifiers
- slug: kotlin-236-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
  - visibility-modifiers
---
# Вопрос (RU)
> Какие модификаторы видимости есть в Kotlin и чем они отличаются?

# Question (EN)
> What visibility modifiers does Kotlin have and what's the difference?

---

## Ответ (RU)

**Теория модификаторов видимости:**
Kotlin имеет 4 уровня видимости: `private`, `protected`, `internal`, `public`. В отличие от Java, default modifier — `public`, а не package-private. `internal` позволяет видеть элемент в пределах одного модуля (module) — удобно для инкапсуляции деталей внутри модуля; элементы с `internal` не видны за пределами модуля. В Kotlin нет отдельного package-private модификатора.

См. также: [[c-kotlin]].

**Уровни видимости:**
- **public**: Видим везде (default модификатор).
- **internal**: Видим внутри одного модуля.
- **protected**: Видим в классе и наследниках (только для членов класса и его наследников; для top-level деклараций `protected` недоступен).
- **private**: Видим только в пределах области объявления или файла (для top-level деклараций — в пределах файла; для членов класса — в пределах этого класса; для конструкторов и аксессоров можно задавать модификатор отдельно).

**Базовые примеры:**
```kotlin
// ✅ public (по умолчанию)
class PublicClass {
    fun publicMethod() {} // public
}

// ✅ internal — видим только в модуле
internal class InternalClass {
    internal fun internalMethod() {}
}

// ✅ private — только внутри класса
class Example {
    private fun privateMethod() {}

    fun publicMethod() {
        privateMethod() // ✅ Доступно
    }
}

// ❌ Ошибка — недоступен приватный метод
// val ex = Example()
// ex.privateMethod() // Ошибка!
```

**Protected visibility:**
```kotlin
// ✅ protected — видим в классе и наследниках
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
// ✅ internal — модульная инкапсуляция
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
    // val helper = NetworkHelper() // ❌ Недоступно — другой модуль
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

// ✅ Инкапсуляция через приватное хранилище
class User(val name: String) {
    private var password: String = ""

    fun setPassword(newPassword: String) {
        password = newPassword // ✅ Управляем изменением изнутри
    }

    fun getMaskedPassword(): String {
        return "***" // ✅ Не раскрываем внутреннее значение вовне
    }
}
```

**Package-level visibility:**
```kotlin
// ✅ Файл: helpers.kt
private fun privateHelper() {} // Приватная функция этого файла
internal fun internalHelper() {} // Видна в модуле
public fun publicHelper() {} // Видна везде

// Файл: main.kt (тот же модуль)
fun test() {
    // privateHelper() // ❌ Недоступно — другой файл (file-private область)
    internalHelper() // ✅ Доступно — тот же модуль
    publicHelper() // ✅ Доступно
}
```

## Answer (EN)

**Visibility Modifiers Theory:**
Kotlin has 4 visibility levels: `private`, `protected`, `internal`, `public`. Unlike Java, the default modifier is `public`, not package-private. `internal` makes a declaration visible within a single module — useful for encapsulating implementation details inside that module; declarations marked `internal` are not visible outside that module. Kotlin has no dedicated package-private modifier.

See also: [[c-kotlin]].

**Visibility Levels:**
- **public**: Visible everywhere (default modifier).
- **internal**: Visible within the same module.
- **protected**: Visible in the class and its subclasses (only for class members; not allowed for top-level declarations).
- **private**: Visible only within the declaring scope or file (for top-level declarations — within the file; for class members — within that class; constructors and property accessors can declare their own visibility modifiers).

**Basic Examples:**
```kotlin
// ✅ public (default)
class PublicClass {
    fun publicMethod() {} // public
}

// ✅ internal — visible only in the module
internal class InternalClass {
    internal fun internalMethod() {}
}

// ✅ private — only inside the class
class Example {
    private fun privateMethod() {}

    fun publicMethod() {
        privateMethod() // ✅ Accessible
    }
}

// ❌ Error — private method not accessible
// val ex = Example()
// ex.privateMethod() // Error!
```

**Protected Visibility:**
```kotlin
// ✅ protected — visible in class and inheritors
open class Base {
    protected val value = 42
    protected fun protectedMethod() {}
}

class Derived : Base() {
    fun accessProtected() {
        println(value) // ✅ Accessible in subclass
        protectedMethod() // ✅ Accessible in subclass
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
// ✅ internal — module-level encapsulation
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
    // val helper = NetworkHelper() // ❌ Not accessible — different module
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

// ✅ Encapsulation via private backing storage
class User(val name: String) {
    private var password: String = ""

    fun setPassword(newPassword: String) {
        password = newPassword // ✅ Control modifications internally
    }

    fun getMaskedPassword(): String {
        return "***" // ✅ Do not expose the internal value directly
    }
}
```

**Package-level Visibility:**
```kotlin
// ✅ File: helpers.kt
private fun privateHelper() {} // Private to this file
internal fun internalHelper() {} // Visible in the module
public fun publicHelper() {} // Visible everywhere

// File: main.kt (same module)
fun test() {
    // privateHelper() // ❌ Not accessible — different file (file-private scope)
    internalHelper() // ✅ Accessible — same module
    publicHelper() // ✅ Accessible
}
```

## Дополнительные Вопросы (RU)

- Когда использовать `internal` vs `private`?
- Как работает видимость с `sealed` классами?
- Как управлять видимостью в multi-module проектах?

## Follow-ups

- When to use internal vs private?
- How does visibility work with sealed classes?
- Visibility in multi-module projects?

## Ссылки (RU)

- https://kotlinlang.org/docs/visibility-modifiers.html

## References

- https://kotlinlang.org/docs/visibility-modifiers.html

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-kotlin-enum-classes--kotlin--easy]] - Базовые классы

### Связанные (средней сложности)
- [[q-access-modifiers--kotlin--medium]] - Модификаторы доступа
- [[q-inheritance-open-final--kotlin--medium]] - Наследование
- [[q-inner-nested-classes--kotlin--medium]] - Внутренние и вложенные классы

### Продвинутое (сложнее)
- [[q-kotlin-reified-types--kotlin--hard]] - Обобщения с reified типами

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-enum-classes--kotlin--easy]] - Basic classes

### Related (Medium)
- [[q-access-modifiers--kotlin--medium]] - Access modifiers
- [[q-inheritance-open-final--kotlin--medium]] - Inheritance
- [[q-inner-nested-classes--kotlin--medium]] - Nested classes

### Advanced (Harder)
- [[q-kotlin-reified-types--kotlin--hard]] - Reified types
