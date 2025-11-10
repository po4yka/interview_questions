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
- architecture-clean
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
updated: 2025-11-10
tags:
- android/di-koin
- android/architecture-clean
- dependency-injection
- koin
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

Koin — это runtime `Service` Locator/DI-контейнер. DSL `module { single { ... } }` разворачивается в `BeanDefinition`, которые регистрируются в `DefinitionRegistry`. При каждом вызове `get()` фреймворк запускает **pipeline разрешения**, комбинируя `DefinitionResolver`, `ScopeRegistry` и `InstanceContext` (часть внутреннего API).

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
   - `kind` (`Single`, `Factory`, `Scoped`, `ViewModel`/Android-specific)
   - `definition: Definition<T>` — лямбда, создающая объект (обычно не `suspend`; при необходимости вы сами вызываете suspend-функции внутри)
   - `options` (`createdAtStart`, `override`, `secondaryTypes`)
3. При `startKoin` модули попадают в `DefinitionRegistry`, а индексы кэшируются в `BeanRegistry` (карта из ключа `(KClass, Qualifier)` в `BeanDefinition`).

### 2. Pipeline разрешения

```text
InstanceContext(request) ─┐
                          ├── DefinitionResolver.resolveInstance(...)
ScopeRegistry              │
BeanRegistry               │
├─ ScopeDefinition         │
└─ BeanDefinition          ┘
```

1. `InstanceContext` — immutable-объект, в котором Koin хранит:
   - `scope` (исходный Scope, откуда вызвали `get()`)
   - `parameters` (`ParametersHolder`)
   - `depth`/служебные поля (для обнаружения циклов и трассировки) — внутренний механизм.
2. `DefinitionResolver` ищет `BeanDefinition` по ключу `(KClass, Qualifier)` в `BeanRegistry`.
3. Стратегия выбора scope при разрешении (упрощённо, в соответствии с внутренней логикой Koin 3.x):
   - 1) Текущий scope из `InstanceContext`.
   - 2) Родительский scope (`Scope.parent`) при наличии.
   - 3) Корневой `ScopeRegistry.rootScope`.
   - 4) Дополнительные linked scopes (через `linkTo`).
   Фактический обход инкапсулирован во внутренних методах `DefinitionResolver`/`ScopeRegistry`, отдельного стабильного `ScopeResolver` класса в публичном API нет.
4. Для найденного `BeanDefinition` вызывается его `InstanceFactory` (через `resolveValue` или аналогичный внутренний метод), который либо берёт значение из кэша, либо создаёт новый экземпляр.

### 3. Стратегия кэширования

| Kind        | Реализация (core)             | Хранилище                               |
|------------|-------------------------------|-----------------------------------------|
| `Single`   | `SingleInstanceFactory`       | `InstanceHolder` (lazy + sync)          |
| `Factory`  | `FactoryInstanceFactory`      | нет кэша, всегда новый экземпляр        |
| `Scoped`   | `ScopedInstanceFactory`       | `Scope.instances`                       |
| `ViewModel`| спец. `ViewModel` definitions | Используют scoped-механику + ViewModelStore |

- `SingleInstanceFactory` оборачивает `definition` в ленивое создание через `InstanceHolder` и синхронизирует доступ (`KoinPlatformTools.synchronized` / double-checked locking) для потокобезопасного singleton.
- Для `Scoped` ключ содержит идентификатор scope (`ScopeDefinition.scopeQualifier`). Инстансы живут в `Scope.instances`, привязанные к конкретному scope.
- При `close()` scope очищает свой map и уведомляет Koin/`ScopeCallback` об удалении экземпляров.

### 4. Параметры и secondary types

- `ParametersHolder` инкапсулирует runtime-аргументы и передаётся до `definition`:

```kotlin
get<Repo> { parametersOf(userId) }
```

- Secondary types позволяют резолвить по интерфейсу и конкретному классу:

```kotlin
singleOf(::SqlUserRepository) {
    bind<UserRepository>()
    bind<AnalyticsSource>()
}
```

`BeanDefinition.secondaryTypes` добавляет дополнительные ключи в `BeanRegistry`, поэтому `get<AnalyticsSource>()` или `get<UserRepository>()` попадут в один и тот же инстанс.

### 5. Внутренняя защита от циклов

Koin не строит compile-time граф; всё разрешение — runtime. Для защиты от циклических зависимостей используется стек/трекер разрешений (`ResolutionStack` и глубина в `InstanceContext` во внутренних реализациях). Если при разрешении повторно встречается тот же ключ, выбрасывается `CyclicDependencyException`.

### 6. Отложенный старт и eager singletons

- `createdAtStart = true` → Koin собирает список таких definitions и создаёт их при `startKoin`.
- Остальные singletons создаются лениво при первом `get()`.
- Это полезно для инфраструктурных сервисов (логгер, crash reporter), но увеличивает время старта, поэтому использовать нужно осознанно.

### 7. ScopeRegistry и жизненный цикл

```kotlin
val featureScope = koin.createScope<FeatureState>("feature_scope", named("feature"))

featureScope.get<FeaturePresenter>()
featureScope.close()
```

- `ScopeRegistry` держит карту `scopeId → Scope`.
- `createScope` использует `ScopeDefinition` из модулей (`module { scope(named("feature")) { ... } }`).
- `Scope` хранит ссылку на механизмы резолвинга и свой кэш инстансов. При закрытии scope вызывает `ScopeCallback` и чистит кэш.
- Linked scopes (`scope.linkTo(parentScope)`) добавляют id в `Scope.links`, что расширяет область поиска зависимостей.

### 8. Потокобезопасность

- Внутри `InstanceHolder` Koin использует платформенно-зависимую синхронизацию через `KoinPlatformTools` (на JVM — synchronized/double-checked locking).
- Операции со `ScopeRegistry` (создание/удаление scope) выполняются потокобезопасно.
- В результате разрешение singletons и scoped-инстансов корректно работает при конкурентных вызовах `get()`.

---

## Answer (EN)

Koin acts as a runtime `Service` Locator / DI container. The DSL `module { single { ... } }` is converted into `BeanDefinition` objects which are registered in the `DefinitionRegistry`. Every `get()` call triggers a **resolution pipeline** orchestrated internally by `DefinitionResolver`, `ScopeRegistry`, and `InstanceContext`.

### 1. From DSL to BeanDefinition

```kotlin
val presentationModule = module {
    viewModel { UserViewModel(get(), get()) }
    single(named("api")) { createApi(get()) }
}
```

- Each DSL entry builds a `BeanDefinition` with:
  - `qualifier` (type + optional name)
  - `kind` (`Single`, `Factory`, `Scoped`, `ViewModel`/Android-specific)
  - `definition: Definition<T>` — a lambda that creates the instance (non-suspending by default; you can call suspend APIs from it as needed)
  - `options` (`createdAtStart`, `override`, `secondaryTypes`)
- During `startKoin`, modules register their definitions inside `DefinitionRegistry`, and `BeanRegistry` holds lookup maps from `(KClass, Qualifier)` to `BeanDefinition`.

### 2. Resolution pipeline

```text
InstanceContext(request) ─┐
                          ├── DefinitionResolver.resolveInstance(...)
ScopeRegistry              │
BeanRegistry               │
├─ ScopeDefinition         │
└─ BeanDefinition          ┘
```

1. `InstanceContext` carries:
   - the active scope from which `get()` was called,
   - optional `ParametersHolder`,
   - depth/metadata for cycle detection and tracing (internal details).
2. `DefinitionResolver` queries `BeanRegistry` for a `(KClass, Qualifier)` key.
3. Scope lookup strategy (simplified to match Koin 3.x behavior):
   - caller scope in `InstanceContext`;
   - its parent scope (if any);
   - the root scope in `ScopeRegistry`;
   - linked scopes added via `scope.linkTo(parentScope)` (these links are stored in `Scope.links` and extend the search space).
   The actual traversal is implemented inside `DefinitionResolver`/`ScopeRegistry`; there is no separate stable `ScopeResolver` public API.
4. For the selected `BeanDefinition`, the corresponding `InstanceFactory` is invoked (via `resolveValue` or similar internal call) to either reuse a cached instance or create a new one.

### 3. Caching strategy

- `SingleInstanceFactory` uses an `InstanceHolder` with lazy initialization plus synchronized access (`KoinPlatformTools.synchronized` / double-checked locking) to ensure a single instance.
- `FactoryInstanceFactory` never caches; it always creates a fresh instance.
- `ScopedInstanceFactory` stores instances in `Scope.instances`, keyed by definition id and bound to that scope's lifecycle.
- ViewModels are handled via dedicated `ViewModel` definitions/factories on Android; they build on scoped mechanics and integrate with `ViewModelStore` rather than being plain generic `ScopedInstanceFactory` entries.

### 4. Parameters and secondary types

- `ParametersHolder` carries runtime parameters:

```kotlin
get<Repo> { parametersOf(userId) }
```

  and forwards them down to the definition lambda.

- Secondary bindings (e.g. `bind<Interface>()`) register extra keys pointing to the same `BeanDefinition`, so one instance can satisfy multiple types:

```kotlin
singleOf(::SqlUserRepository) {
    bind<UserRepository>()
    bind<AnalyticsSource>()
}
```

`BeanDefinition.secondaryTypes` adds additional keys into `BeanRegistry`, so `get<AnalyticsSource>()` or `get<UserRepository>()` resolves to the same instance.

### 5. Cycle detection

- Koin is purely runtime in its graph handling. Cycle detection is implemented via internal resolution tracking (e.g. a resolution stack plus depth counters). If the same key appears again in the active chain, Koin throws `CyclicDependencyException`.

### 6. Eager vs lazy singletons

- Definitions with `createdAtStart = true` are instantiated during `startKoin`.
- All other singles are instantiated lazily on first `get()`.
- This is useful for infrastructure services that must be ready early but increases startup cost and should be used deliberately.

### 7. ScopeRegistry lifecycle

- `ScopeRegistry` keeps a `scopeId → Scope` map.
- `createScope` attaches a `ScopeDefinition` declared in modules and wires callbacks.
- `Scope` holds resolution helpers and its instance cache. `Scope.close()` clears its cached instances and notifies registered `ScopeCallback`s.
- Linked scopes (`scope.linkTo(parentScope)`) add ids into `Scope.links`, extending the search space during resolution.

### 8. Concurrency guarantees

- `InstanceHolder` uses platform-specific locking via `KoinPlatformTools` to make singleton initialization thread-safe.
- Scope creation and closing are managed in a thread-safe manner within `ScopeRegistry`.
- As a result, concurrent `get()` calls for the same singleton or scoped definition are handled safely.

---

## Дополнительные вопросы
- Как Koin реализует `qualifier` в multiplatform окружении?
- Какая стратегия у Koin при работе с coroutine scopes внутри `Definition`?
- Как оптимизировать разрешение Koin при больших графах (например, через `module { includes(...) }`)?
- Что потребуется для миграции этих internals при переходе на Koin 4.x?

## Follow-ups
- How does Koin implement `qualifier` in a multiplatform environment?
- What strategy does Koin use when working with coroutine scopes inside a `Definition`?
- How can you optimize Koin resolution for large graphs (e.g., via `module { includes(...) }`)?
- What would be required to adapt these internals when migrating to Koin 4.x?

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