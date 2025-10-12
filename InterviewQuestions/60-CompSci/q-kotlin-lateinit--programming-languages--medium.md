---
tags:
  - dependency-injection
  - initialization
  - kotlin
  - lateinit
  - programming-languages
  - properties
difficulty: medium
status: draft
---

# Что известно о lateinit?

# Question (EN)
> What do you know about lateinit?

# Вопрос (RU)
> Что известно о lateinit?

---

## Answer (EN)

`lateinit` is used for **deferred initialization** of properties in Kotlin.

**Key characteristics:**

1. **Only for `var`**: Cannot be used with `val`
2. **Only reference types**: Cannot be used with primitives (Int, Boolean, etc.)
3. **Must initialize before use**: Throws `UninitializedPropertyAccessException` if accessed before initialization
4. **No null overhead**: Better than nullable types for deferred initialization

**Syntax:**
```kotlin
class MyClass {
    lateinit var name: String

    fun initialize() {
        name = "John"  // Initialize later
    }

    fun use() {
        println(name)  // Must be initialized by now!
    }
}
```

**Common use cases:**

1. **Dependency Injection**: Properties initialized by DI framework
```kotlin
class MyActivity : Activity() {
    @Inject lateinit var repository: Repository
}
```

2. **Testing**: Properties initialized in setUp methods
```kotlin
class MyTest {
    lateinit var subject: SubjectUnderTest

    @Before
    fun setUp() {
        subject = SubjectUnderTest()
    }
}
```

3. **Android**: Views initialized in onCreate/onViewCreated
```kotlin
class MyFragment : Fragment() {
    lateinit var binding: FragmentBinding

    override fun onViewCreated(...) {
        binding = FragmentBinding.bind(view)
    }
}
```

**Checking if initialized:**
```kotlin
if (::name.isInitialized) {
    println(name)
}
```

**Constraints:**
- Cannot be used with nullable types
- Cannot be used in primary constructor
- Cannot be used with primitive types

---

## Ответ (RU)

1. lateinit используется для откладывания инициализации переменных (только для var и только ссылочных типов). 2. Поле помечается как lateinit и должно быть инициализировано до первого использования, иначе выбрасывается UninitializedPropertyAccessException. 3. Это полезно в случаях, когда инициализация зависит от внешних условий (например, DI или тестирование).

