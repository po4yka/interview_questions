---
id: android-611
title: Koin Resolution Internals / Внутренние механизмы Koin
aliases:
- Koin Resolution Internals
- Внутренние механизмы Koin
- Koin Instance Resolution
topic: android
subtopics:
- di-koin
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-koin-fundamentals--android--medium
- q-koin-scope-management--android--medium
- q-koin-testing-strategies--android--medium
- q-koin-vs-hilt-comparison--android--medium
created: 2025-11-02
updated: 2025-11-02
tags:
- android/di-koin
- difficulty/hard
sources:
- url: https://insert-koin.io/docs/reference/koin-core/architecture
  note: Официальный обзор архитектуры Koin
- url: https://github.com/InsertKoinIO/koin/blob/master/core/koin-core/src/main/kotlin/org/koin/core/Koin.kt
  note: Код ядра Koin (ScopeRegistry, DefinitionResolver)
- url: https://blog.insert-koin.io/posts/koin-3-4-deep-dive/
  note: Deep dive по разрешению зависимостей в Koin 3.x
---

# Вопрос (RU)
> Объясните, как Koin разрешает зависимости внутри себя: от DSL-модуля до получения экземпляра. Раскройте работу DefinitionResolver, ScopeRegistry, InstanceContext и стратегию выбора scope.

# Question (EN)
> Describe how Koin resolves dependencies internally—from DSL modules to instance retrieval. Cover DefinitionResolver, ScopeRegistry, InstanceContext, and the scope selection strategy.

---

## Ответ (RU)

Koin — это runtime Service Locator. DSL `module { single { ... } }` разворачивается в `BeanDefinition`, которые регистрируются в `DefinitionRegistry`. При каждом вызове `get()` фреймворк запускает **pipeline разрешения**, комбинируя `DefinitionResolver`, `ScopeRegistry` и `InstanceContext`.

### 1. От DSL к BeanDefinition

```kotlin
val presentationModule = module {
    viewModel { UserViewModel(get(), get()) }
    single(named("api")) { createApi(get()) }
}
```

1. DSL строит `Module` → список `BeanDefinition`.
2. Каждый `BeanDefinition` включает:
   - `qualifier` (тип + optional имя)
  - `kind` (`Single`, `Factory`, `Scoped`, `ViewModel`)
  - `definition: Definition<T>` — suspending lambda, создающая объект
  - `options` (createdAtStart, override, secondaryTypes)
3. При `startKoin` модули попадают в `DefinitionRegistry`, а индексы кэшируются в `BeanRegistry`.

### 2. Pipeline разрешения

```text
InstanceContext(request) ─┐
                          ├── DefinitionResolver.resolveInstance(...)
ScopeRegistry              │
BeanRegistry               │
├─ ScopeDefinition         │
└─ BeanDefinition          ┘
```

1. `InstanceContext` — immutable объект, в котором Koin хранит:
   - `scope` (исходный Scope, откуда вызвали `get()`)
   - `parameters` (`ParametersHolder`)
   - `depth` (для обнаружения циклов)
2. `DefinitionResolver` ищет `BeanDefinition` по ключу: `(KClass, Qualifier)`.
3. `ScopeResolver` определяет, из какого scope брать инстанс:
   - 1) `InstanceContext.scope` (текущий)
   - 2) Родительский scope (`Scope.parent`)
   - 3) Корневой `ScopeRegistry.rootScope`
   - 4) Дополнительные linked scopes (через `linkTo`)
4. Для каждого candidate-инстанса вызывается `resolveValue`, проверяющая кеш `InstanceHolder`.

### 3. Стратегия кэширования

| Kind      | Реализация                    | Хранилище                      |
|-----------|-------------------------------|--------------------------------|
| `Single`  | `SingleInstanceFactory`       | `InstanceHolder` (mutex, lazy) |
| `Factory` | `FactoryInstanceFactory`      | нет кэша, создаёт заново       |
| `Scoped`  | `ScopedInstanceFactory`       | `ScopeDefinition` → `Scope`    |
| `ViewModel` | `ScopedInstanceFactory`     | Tied к `ViewModelStore`        |

- `SingleInstanceFactory` оборачивает `definition` в `synchronized` (через `KoinPlatformTools.synchronized`) и кеширует результат.
- `Scoped` ключ содержит идентификатор scope (`ScopeDefinition.scopeQualifier`). Инстансы лежат в `Scope.instances`.
- При `close()` scope очищает свой map и уведомляет `Koin` об удалении.

### 4. Параметры и secondary types

- `ParametersHolder` — стек `Any` + `DefinitionParameters`. При `get<Repo>(parameters = { parametersOf(userId) })` они прокидываются до `definition`.
- Secondary types позволяют резолвить по интерфейсу и конкретному классу:

```kotlin
singleOf(::SqlUserRepository) {
    bind<UserRepository>()
    bind<AnalyticsSource>()
}
```

`BeanDefinition.secondaryTypes` добавляет дополнительные ключи в `BeanRegistry`, поэтому `get<AnalyticsSource>()` попадёт в тот же инстанс.

### 5. Внутренняя защита от циклов

`InstanceContext.depth` + `ResolutionStack` отслеживают цепочку ключей. Если при разрешении встречается тот же key, выбрасывается `CyclicDependencyException`. Koin не строит compile-time граф, поэтому обнаружение происходит только в runtime в момент запроса.

### 6. Отложенный старт и eager singletons

- `createdAtStart = true` → Koin собирает список таких definitions и прогревает их на `startKoin`.
- Остальные singletons создаются лениво при первом `get()`.
- Это важно для модулей инфраструктуры (логгер, crash reporter), где нужно раннее создание.

### 7. ScopeRegistry и жизненный цикл

```kotlin
val featureScope = koin.createScope<FeatureState>("feature_scope", named("feature"))

featureScope.get<FeaturePresenter>()
featureScope.close()
```

- `ScopeRegistry` держит карту `scopeId → Scope`.
- `createScope` вешает `ScopeDefinition` (из `module { scope(named("feature")) { ... } }`).
- `Scope` хранит ссылку на `DefinitionResolver`. При закрытии scope вызывает `ScopeCallback`s и чистит кэш.
- Linked scopes (`scope.linkTo(parentScope)`) добавляют id в `Scope.links`, что расширяет поиск зависимостей.

### 8. Потокобезопасность

- Внутри `InstanceHolder` Koin использует `Mutex` (JVM) или `Synchronized`.
- Для multiplatform `KoinPlatformTools` абстрагирует блокировки.
- Scope-операции (create/close) синхронизированы через `ScopeRegistry`.

---

## Answer (EN)

Koin acts as a runtime Service Locator. The DSL `module { single { ... } }` expands into `BeanDefinition` objects registered in the `DefinitionRegistry`. Every `get()` call triggers a **resolution pipeline** orchestrated by `DefinitionResolver`, `ScopeRegistry`, and `InstanceContext`.

### 1. From DSL to BeanDefinition

- Each DSL entry builds a `BeanDefinition` with qualifier, kind (`Single`, `Factory`, `Scoped`, `ViewModel`), creation lambda, and options.
- During `startKoin`, modules register definitions inside the `DefinitionRegistry`; lookup tables live in `BeanRegistry`.

### 2. Resolution pipeline

1. `InstanceContext` packages the active scope, optional parameters, and depth.
2. `DefinitionResolver` searches `BeanRegistry` for a key `(KClass, Qualifier)`.
3. Scope lookup sequence: caller scope → parent → root → linked scopes.
4. `resolveValue` delegates to the matching `InstanceFactory`, which may reuse or create the instance.

### 3. Caching strategy

- `SingleInstanceFactory` keeps a synchronized `InstanceHolder`.
- `FactoryInstanceFactory` skips caching entirely.
- `ScopedInstanceFactory` stores instances inside the `Scope.instances` map keyed by definition id.
- ViewModels piggyback on `ScopedInstanceFactory` but bind to `ViewModelStore`.

### 4. Parameters and secondary types

- `ParametersHolder` forwards runtime arguments (`parametersOf(...)`) to the definition lambda.
- Secondary bindings (`bind<Interface>()`) push additional keys into the registry, so the same instance satisfies multiple types.

### 5. Cycle detection

- `ResolutionStack` and depth counters detect when the same key appears twice in the active chain and throw `CyclicDependencyException`.
- Because the graph is runtime-only, cycles emerge only when the offending resolution happens.

### 6. Eager vs lazy singletons

- Definitions marked `createdAtStart` are instantiated during `startKoin`.
- All other singles are lazy, which keeps startup light but requires runtime null-safety in first access.

### 7. ScopeRegistry lifecycle

- `ScopeRegistry` stores `scopeId → Scope`.
- `createScope` binds a `ScopeDefinition` from the module and wires callbacks.
- `Scope.close()` clears cached instances and notifies registered listeners; linked scopes widen lookup during resolution.

### 8. Concurrency guarantees

- `InstanceHolder` synchronizes singletons using platform-specific locks.
- Scope creation/destruction is serialized within `ScopeRegistry`.
- The pipeline stays thread-safe even under concurrent `get()` calls on the same singleton.

---

## Follow-ups
- Как Koin реализует `qualifier` в multiplatform окружении?
- Какая стратегия у Koin при работе с coroutine scopes внутри Definition?
- Как оптимизировать разрешение Koin при больших графах (например, через `module { includes(...) }`)?
- Что потребуется для миграции этих internals при переходе на Koin 4.x?

## References
- [[c-dependency-injection]]
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-scope-management--android--medium]]
- [[q-koin-testing-strategies--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]

## Related Questions

- [[c-dependency-injection]]
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-scope-management--android--medium]]
- [[q-koin-testing-strategies--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]

