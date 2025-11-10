---
id: lang-073
title: "Kotlin Lateinit / lateinit в Kotlin"
aliases: [Kotlin Lateinit, lateinit в Kotlin]
topic: kotlin
subtopics: [null-safety, type-system]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, q-kotlin-advantages-for-android--kotlin--easy, q-kotlin-map-flatmap--kotlin--medium]
created: 2025-10-15
updated: 2025-11-09
tags: [dependency-injection, difficulty/medium, initialization, lateinit, programming-languages, properties]
---
# Вопрос (RU)
> Что известно о `lateinit`?

## Ответ (RU)

`lateinit` используется для отложенной инициализации свойств в Kotlin.

Ключевые моменты:

1. Только для `var`-свойств: нельзя использовать с `val`.
2. Только для ненулевых ссылочных типов: нельзя использовать с типами вида `String?`.
3. Только для свойств: разрешён для топ-левел свойств и свойств классов/объектов; нельзя использовать для локальных переменных и параметров первичного конструктора.
4. Должно быть проинициализировано до первого чтения, иначе будет выброшено `UninitializedPropertyAccessException`.
5. Позволяет избежать nullable-типов, когда вы гарантированно знаете, что значение будет присвоено до использования (DI, тесты, жизненный цикл Android-компонентов).

Синтаксис (отложенная инициализация в классе):
```kotlin
class MyClass {
    lateinit var name: String

    fun initialize() {
        name = "John"  // Инициализируем позже
    }

    fun use() {
        println(name)  // К этому моменту свойство должно быть инициализировано
    }
}
```

Типичные случаи использования:

1. Dependency Injection: свойство инициализируется DI-фреймворком.
```kotlin
class MyActivity : Activity() {
    @Inject lateinit var repository: Repository
}
```

2. Тесты: инициализация в `@Before` методах.
```kotlin
class MyTest {
    lateinit var subject: SubjectUnderTest

    @Before
    fun setUp() {
        subject = SubjectUnderTest()
    }
}
```

3. Android: вьюхи или binding-объекты, инициализируемые в колбэках жизненного цикла.
```kotlin
class MyFragment : Fragment() {
    lateinit var binding: FragmentBinding

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentBinding.bind(view)
    }
}
```

Проверка, инициализировано ли свойство:
```kotlin
if (::name.isInitialized) {
    println(name)
}
```

Ограничения:
- Нельзя использовать с nullable-типами.
- Нельзя использовать в параметрах первичного конструктора.
- Нельзя использовать для локальных переменных.

---

# Question (EN)
> What do you know about `lateinit`?

## Answer (EN)

`lateinit` is used for deferred initialization of properties in Kotlin.

Key characteristics:

1. Only for `var`: Cannot be used with `val`.
2. Only non-null reference types: Cannot be used with nullable types like `String?`.
3. Properties only: Allowed for top-level properties and member properties of classes/objects; not allowed for local variables or primary constructor parameters.
4. Must be initialized before use: Accessing it before initialization throws `UninitializedPropertyAccessException`.
5. Avoids nullable overhead: Useful when you know a property will be initialized later and should not be nullable.

Syntax:
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

Common use cases:

1. Dependency Injection: Properties initialized by DI framework
```kotlin
class MyActivity : Activity() {
    @Inject lateinit var repository: Repository
}
```

2. Testing: Properties initialized in setUp methods
```kotlin
class MyTest {
    lateinit var subject: SubjectUnderTest

    @Before
    fun setUp() {
        subject = SubjectUnderTest()
    }
}
```

3. Android: Views or bindings initialized in lifecycle callbacks
```kotlin
class MyFragment : Fragment() {
    lateinit var binding: FragmentBinding

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentBinding.bind(view)
    }
}
```

Checking if initialized:
```kotlin
if (::name.isInitialized) {
    println(name)
}
```

Constraints:
- Cannot be used with nullable types.
- Cannot be used in primary constructor parameters.
- Cannot be used with local variables.

---

## Дополнительные вопросы (RU)

- В чем ключевые отличия от подхода в Java?
- Когда вы бы использовали `lateinit` на практике?
- Какие распространенные ошибки при использовании `lateinit`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-kotlin-advantages-for-android--kotlin--easy]]

## Related Questions

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-kotlin-advantages-for-android--kotlin--easy]]
