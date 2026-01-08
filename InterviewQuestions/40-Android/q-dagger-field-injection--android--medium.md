---\
id: android-469
title: Dagger Field Injection / Инъекция полей Dagger
aliases: [Dagger Field Injection, Инъекция полей Dagger]
topic: android
subtopics: [architecture-mvvm, di-hilt]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-dagger, c-dependency-injection, c-hilt, q-dagger-build-time-optimization--android--medium, q-dagger-framework-overview--android--hard, q-dagger-main-elements--android--medium, q-dagger-purpose--android--easy, q-hilt-components-scope--android--medium]
sources: []
created: 2025-10-20
updated: 2025-10-30
tags: [android/architecture-mvvm, android/di-hilt, dagger, dependency-injection, difficulty/medium]

---\
# Вопрос (RU)
> Какие особенности инъекции в поле при помощи `Dagger`?

# Question (EN)
> What are the features of field injection using `Dagger`?

## Ответ (RU)

Field injection в `Dagger` внедряет зависимости в поля класса через `@Inject` **после создания объекта**. Используется для Android-компонентов (`Activity`, `Fragment`, `Service`), где конструктор недоступен для модификации или объект создаётся фреймворком.

### Жизненный Цикл

1. Создание объекта через конструктор по умолчанию / фреймворком
2. Вызов метода `inject()` соответствующего компонента
3. Заполнение помеченных `@Inject` полей зависимостями (код, сгенерированный `Dagger`)
4. После `inject()` поля готовы к использованию

Важно: доступ к `@Inject`-полям до вызова `inject()` приведёт к ошибке (например, `UninitializedPropertyAccessException` для `lateinit`).

```kotlin
// ❌ Неправильно - использование до inject()
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH: поле ещё не инициализировано
    }
}

// ✅ Правильно - inject() перед использованием
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)
        repository.getUser() // OK
    }
}
```

### Требования

**Компонент с методом inject():**
```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Отдельный метод для каждого типа, куда инжектируем поля
}
```

**Ограничения по полям в Kotlin (Dagger/Hilt без reflection):**
```kotlin
@Inject lateinit var repository: UserRepository // ✅ Распространённый вариант
@Inject var repository: UserRepository? = null  // ✅ Допустимо как nullable var
@Inject val repository: UserRepository // ❌ Не компилируется (final / val не может быть проинжектирован)
```

Ключевое требование: поле должно быть доступно для записи (не `val`), чтобы сгенерированный `Dagger`-код смог присвоить зависимость.

### Hilt Упрощение

`Hilt` автоматизирует field injection для Android-компонентов:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // ✅ Hilt сгенерировал и вызвал inject() автоматически до onCreate
    }
}
```

### Применимость

**Используйте для:**
- Android framework компонентов (`Activity`, `Fragment`, `Service`, `BroadcastReceiver` и т.п.)
- Классов, создаваемых системой/фреймворком, где нет контроля над конструктором

**Избегайте для:**
- `ViewModel`, Repository, UseCase → предпочтительна constructor injection
- Тестируемых классов → field injection усложняет подмену зависимостей
- Новых собственных компонентов, где вы контролируете конструктор → предпочтительна constructor injection

### Ограничения

- Менее явный контракт: зависимости не видны в сигнатуре конструктора → сложнее читать и поддерживать
- Потенциальные ошибки жизненного цикла: доступ к полям до вызова `inject()` приведёт к крашу
- Усложняет тестирование: нужно отдельно инициализировать или подменять поля (иногда через тестовый компонент или setter), вместо явной передачи в конструктор
- Чуть больше связность с DI-фреймворком (компонент должен знать о типе для `inject()`)

Важно: `Dagger` и `Hilt` используют кодогенерацию, а не reflection, поэтому field injection не несёт значимого reflection-overhead по сравнению с constructor injection. Отличие в основном в явности зависимостей и рисках порядка инициализации.

## Answer (EN)

Field injection in `Dagger` injects dependencies into class fields via `@Inject` **after the object is created**. It is used for Android components (`Activity`, `Fragment`, `Service`) or other framework-created classes where you cannot modify the constructor.

### Lifecycle

1. Object is created via default/framework constructor
2. The appropriate component's `inject()` method is called
3. Generated `Dagger` code assigns dependencies to `@Inject`-annotated fields
4. After `inject()`, fields are safe to use

Important: accessing `@Inject` fields before `inject()` is called will cause errors (e.g., `UninitializedPropertyAccessException` for `lateinit`).

```kotlin
// ❌ Wrong - using before inject()
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // CRASH: field not initialized yet
    }
}

// ✅ Correct - inject() before usage
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent.inject(this)
        super.onCreate(savedInstanceState)
        repository.getUser() // OK
    }
}
```

### Requirements

**`Component` with inject() method:**
```kotlin
@Component(modules = [AppModule::class])
interface AppComponent {
    fun inject(activity: MainActivity) // ✅ Separate method for each type that receives field injection
}
```

**Field constraints in Kotlin (Dagger/Hilt codegen, no reflection):**
```kotlin
@Inject lateinit var repository: UserRepository // ✅ Common pattern
@Inject var repository: UserRepository? = null  // ✅ Allowed as nullable var
@Inject val repository: UserRepository // ❌ Won't compile (final / val cannot be injected)
```

The key requirement is that the field must be writable (not `val`) so generated `Dagger` code can assign the dependency.

### Hilt Simplification

`Hilt` automates field injection for Android framework components:

```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository.getUser() // ✅ Hilt generates and calls inject() automatically before onCreate
    }
}
```

### Applicability

**Use for:**
- Android framework components (`Activity`, `Fragment`, `Service`, `BroadcastReceiver`, etc.)
- Classes created by the system/framework where you cannot control the constructor

**Avoid for:**
- `ViewModel`, Repository, UseCase → constructor injection preferred
- Testable classes → field injection complicates dependency substitution
- New custom components you own → prefer constructor injection when possible

### Limitations

- Less explicit contract: dependencies are hidden from the constructor signature → harder to reason about
- `Lifecycle` hazards: accessing injected fields before `inject()` causes crashes
- Testing complexity: requires setting up components or manually assigning/mocking fields instead of passing dependencies via constructor
- Tighter coupling to DI setup: the component must know about each type needing field injection via `inject()` methods

Note: `Dagger` and `Hilt` rely on compile-time code generation rather than reflection, so there is no significant reflection-based performance penalty for field injection compared to constructor injection. The main drawbacks are around clarity, lifecycle ordering, and testability.

## Follow-ups

- How does `Hilt` automate inject() calls for Android framework components?
- Why is constructor injection preferred for `ViewModel` and Repository classes?
- What happens if you access an @`Inject` field before calling inject()?
- How does field injection affect unit testing and mocking strategies?
- What are the performance implications of field injection vs constructor injection in Dagger/Hilt?

## References

- [[c-dagger]]
- [[c-dependency-injection]]
- [[c-hilt]]
- [Dagger `Inject` Documentation](https://dagger.dev/api/latest/dagger/Inject.html)
- [Hilt Android Guide](https://developer.android.com/training/dependency-injection/hilt-android)

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-hilt-components-scope--android--medium]]

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]]
- [[q-dagger-multibinding--android--hard]]