---
anki_cards:
- slug: q-kotlin-lateinit--kotlin--medium-0-en
  language: en
  anki_id: 1768326290131
  synced_at: '2026-01-23T17:03:51.413800'
- slug: q-kotlin-lateinit--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326290156
  synced_at: '2026-01-23T17:03:51.415814'
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

`Constraints`:
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
