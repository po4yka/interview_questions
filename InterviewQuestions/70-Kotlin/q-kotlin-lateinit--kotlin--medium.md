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
updated: 2025-11-11
tags: [dependency-injection, difficulty/medium, initialization, lateinit, programming-languages, properties]
date created: Friday, October 31st 2025, 6:30:30 pm
date modified: Tuesday, November 25th 2025, 8:53:50 pm
---
# Вопрос (RU)
> Что известно о `lateinit`?

# Question (EN)
> What do you know about `lateinit`?

## Ответ (RU)

`lateinit` используется для отложенной инициализации свойств в Kotlin, когда вы гарантированно знаете, что значение будет присвоено до первого чтения, и не хотите использовать nullable-тип.

Ключевые моменты:

1. Только для `var`-свойств: нельзя использовать с `val`.
2. Только для ненулевых ссылочных типов: нельзя использовать с типами вида `String?` и с примитивами вроде `Int` (для них используются `Int?` или делегаты).
3. Только для свойств и локальных переменных:
   - Разрешён для топ-левел свойств и свойств классов/объектов.
   - Разрешён для локальных переменных (начиная с Kotlin 1.2).
   - Нельзя использовать в параметрах первичного конструктора.
4. Должно быть проинициализировано до первого чтения, иначе будет выброшено `UninitializedPropertyAccessException`.
5. Смещает проверку инициализации на рантайм: помогает избежать nullable-типов в API, но при ошибке вы получаете исключение во время выполнения, а не ошибку компиляции.

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
- Нельзя использовать с `val`.

---

## Answer (EN)

`lateinit` is used for deferred initialization of properties in Kotlin when you know the value will be assigned before first read and you don't want the property type to be nullable.

Key characteristics:

1. Only for `var`: Cannot be used with `val`.
2. Only non-null reference types: Cannot be used with nullable types like `String?` or with primitive value types like `Int` (for those you use `Int?` or delegates instead).
3. For properties and local variables only:
   - Allowed for top-level and member properties of classes/objects.
   - Allowed for local variables (since Kotlin 1.2).
   - Not allowed for primary constructor parameters.
4. Must be initialized before use: Accessing it before initialization throws `UninitializedPropertyAccessException`.
5. Shifts checks to runtime: It keeps the property non-nullable in the type system, but incorrect usage will fail at runtime instead of compile time.

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
- Cannot be used with `val`.

---

## Дополнительные Вопросы (RU)

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

## Связанные Вопросы (RU)

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-kotlin-advantages-for-android--kotlin--easy]]

## Related Questions

- [[q-kotlin-map-flatmap--kotlin--medium]]
- [[q-kotlin-advantages-for-android--kotlin--easy]]
