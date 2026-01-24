---
id: android-611
title: Koin Resolution Internals / Внутренние механизмы Koin
aliases:
- Koin Instance Resolution
- Koin Resolution Internals
- Внутренние механизмы Koin
topic: android
subtopics:
- architecture-clean
- di-koin
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dependency-injection
- q-koin-fundamentals--android--medium
- q-koin-scope-management--android--medium
- q-koin-testing-strategies--android--medium
- q-koin-vs-dagger-philosophy--android--hard
- q-koin-vs-hilt-comparison--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/architecture-clean
- android/di-koin
- dependency-injection
- difficulty/hard
- koin
anki_cards:
- slug: android-611-0-en
  language: en
  anki_id: 1768396936629
  synced_at: '2026-01-23T16:45:06.067342'
- slug: android-611-0-ru
  language: ru
  anki_id: 1768396936652
  synced_at: '2026-01-23T16:45:06.068368'
sources:
- url: https://insert-koin.io/docs/reference/koin-core/architecture
  note: Официальный обзор архитектуры Koin
- url: https://github.com/InsertKoinIO/koin/blob/master/core/koin-core/src/main/kotlin/org/koin/core/Koin.kt
  note: Код ядра Koin (ScopeRegistry, DefinitionResolver)
- url: https://blog.insert-koin.io/posts/koin-3-4-deep-dive/
  note: Deep dive по разрешению зависимостей в Koin 3.x
---
# Вопрос (RU)
> Объясните, как `Koin` разрешает зависимости внутри себя: от DSL-модуля до получения экземпляра. Раскройте работу DefinitionResolver, ScopeRegistry, InstanceContext и стратегию выбора scope.

# Question (EN)
> Describe how `Koin` resolves dependencies internally—from DSL modules to instance retrieval. Cover DefinitionResolver, ScopeRegistry, InstanceContext, and the scope selection strategy.

---

## Ответ (RU)

`Koin` — это runtime `Service Locator`/DI-контейнер. DSL `module { single { ... } }` разворачивается в `BeanDefinition`, которые регистрируются через модули и становятся доступны для поиска через внутренние реестры (`BeanRegistry`, `ScopeRegistry`). При каждом вызове `get()` фреймворк запускает **pipeline разрешения**, комбинируя `DefinitionResolver`, `ScopeRegistry` и `InstanceContext` (часть внутреннего API).

### 1. От DSL К BeanDefinition

```kotlin
val presentationModule = module {
    viewModel { UserViewModel(get(), get()) }
    single(named("api")) { createApi(get()) }
}
```

1. DSL строит `Module` → набор `BeanDefinition`.
2. Каждый `BeanDefinition` включает:
   - `qualifier` (тип + optional имя)
   - `kind` (`Single`, `Factory`, `Scoped`, `ViewModel`/Android-specific)
   - `definition: Definition<T>` — лямбда, создающая объект (обычно не `suspend`; при необходимости вы сами вызываете suspend-функции внутри)
   - `options` (`createdAtStart`, `override`, `secondaryTypes`)
3. При `startKoin` модули регистрируются внутри `Koin`, а определения попадают в структуры поиска (`BeanRegistry` и связанные индексы), где строятся отображения из ключа `(KClass, Qualifier)` в `BeanDefinition`.

### 2. Pipeline Разрешения

```text
InstanceContext(request) ─┐
                          ├── DefinitionResolver.resolveInstance(...)
ScopeRegistry              │
BeanRegistry               │
├─ ScopeDefinition         │
└─ BeanDefinition          ┘
```

1. `InstanceContext` — immutable-объект, в котором `Koin` хранит:
   - `scope` (исходный Scope, откуда вызвали `get()`),
   - `parameters` (`ParametersHolder`),
   - глубину/служебные поля для обнаружения циклов и трассировки (конкретная реализация — внутренний механизм `Koin` и может меняться).
2. `DefinitionResolver` ищет подходящий `BeanDefinition` по ключу `(KClass, Qualifier)` используя `BeanRegistry` и информацию о доступных `ScopeDefinition`.
3. Стратегия выбора scope при разрешении (упрощённо, в соответствии с `Koin` 3.x):
   - сначала текущий scope из `InstanceContext`;
   - затем связанные scope (linked scopes), если они есть для данного scope;
   - далее глобальные/корневые определения, доступные через `ScopeRegistry`.
   Детальный порядок обхода инкапсулирован во внутренних методах `DefinitionResolver`/`ScopeRegistry`; стабильного отдельного `ScopeResolver` класса в публичном API нет.
4. Для найденного `BeanDefinition` вызывается его `InstanceFactory` (через `resolveValue` или аналогичный внутренний метод), который либо берёт значение из кэша, либо создаёт новый экземпляр.

### 3. Стратегия Кэширования

| Kind        | Реализация (core)             | Хранилище                               |
|------------|-------------------------------|-----------------------------------------|
| `Single`   | `SingleInstanceFactory`       | `InstanceHolder` (lazy + sync)          |
| `Factory`  | `FactoryInstanceFactory`      | нет кэша, всегда новый экземпляр        |
| `Scoped`   | `ScopedInstanceFactory`       | `Scope.instances`                       |
| `ViewModel`| спец. `ViewModel` definitions | Интеграция с ViewModelStore/Android API |

- `SingleInstanceFactory` оборачивает `definition` в ленивое создание через `InstanceHolder` и синхронизирует доступ (`KoinPlatformTools.synchronized` / double-checked locking) для потокобезопасного singleton.
- Для `Scoped` ключ содержит идентификатор scope (`ScopeDefinition.scopeQualifier`). Инстансы живут в `Scope.instances`, привязанные к конкретному scope.
- При `close()` scope очищает свой map и уведомляет Koin/`ScopeCallback` об удалении экземпляров.
- Для `ViewModel` используются отдельные фабрики/интеграция (артефакт `koin-androidx-viewmodel` и др.), которые опираются на `Koin` scopes и Android `ViewModelStore`, но не являются просто обычным `ScopedInstanceFactory`.

### 4. Параметры И Secondary Types

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

`BeanDefinition.secondaryTypes` добавляет дополнительные ключи в реестры поиска, поэтому `get<AnalyticsSource>()` или `get<UserRepository>()` попадут в один и тот же инстанс.

### 5. Внутренняя Защита От Циклов

`Koin` не строит compile-time граф; всё разрешение — runtime. Для защиты от циклических зависимостей используется внутреннее отслеживание цепочки разрешений (стек/трекер активных ключей + глубина). Если при разрешении повторно встречается тот же ключ в текущей цепочке, выбрасывается `CyclicDependencyException`. Конкретные имена внутренних структур могут отличаться между версиями, поэтому важно опираться на концепцию, а не на конкретный класс.

### 6. Отложенный Старт И Eager Singletons

- `createdAtStart = true` → `Koin` собирает список таких definitions и создаёт их при `startKoin`.
- Остальные singletons создаются лениво при первом `get()`.
- Это полезно для инфраструктурных сервисов (логгер, crash reporter), но увеличивает время старта, поэтому использовать нужно осознанно.

### 7. ScopeRegistry И Жизненный Цикл

```kotlin
val featureScope = koin.createScope<FeatureState>("feature_scope", named("feature"))

featureScope.get<FeaturePresenter>()
featureScope.close()
```

- `ScopeRegistry` держит карту `scopeId → Scope`.
- `createScope` использует `ScopeDefinition` из модулей (`module { scope(named("feature")) { ... } }`).
- `Scope` хранит ссылку на механизмы резолвинга и свой кэш инстансов. При закрытии scope вызывает `ScopeCallback` и чистит кэш.
- Linked scopes (`scope.linkTo(parentScope)`) добавляют id в `Scope.links`, что расширяет область поиска зависимостей при разрешении.

### 8. Потокобезопасность

- Внутри `InstanceHolder` `Koin` использует платформенно-зависимую синхронизацию через `KoinPlatformTools` (на JVM — synchronized/double-checked locking).
- Операции со `ScopeRegistry` (создание/удаление scope) реализованы потокобезопасно.
- В результате разрешение singletons и scoped-инстансов корректно работает при конкурентных вызовах `get()`.

---

## Answer (EN)

`Koin` acts as a runtime `Service Locator` / DI container. The DSL `module { single { ... } }` is converted into `BeanDefinition` entries via modules and then exposed through the internal registries (`BeanRegistry`, `ScopeRegistry`). Every `get()` call triggers a **resolution pipeline** orchestrated internally by `DefinitionResolver`, `ScopeRegistry`, and `InstanceContext`.

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
  - `definition: Definition<T>` — a lambda that creates the instance (non-suspending by default; you may call suspend APIs from it if needed)
  - `options` (`createdAtStart`, `override`, `secondaryTypes`)
- During `startKoin`, modules are registered into `Koin`, and their definitions are indexed inside the lookup structures (`BeanRegistry` and related maps) from `(KClass, Qualifier)` to `BeanDefinition`.

### 2. Resolution Pipeline

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
   - an optional `ParametersHolder`,
   - depth/metadata for cycle detection and tracing (actual implementation is internal and may change between versions).
2. `DefinitionResolver` queries `BeanRegistry` for a `(KClass, Qualifier)` and uses scope definitions to locate the right `BeanDefinition`.
3. Scope lookup strategy (simplified to reflect `Koin` 3.x behavior):
   - first, the current scope from `InstanceContext`;
   - then, any linked scopes associated with that scope;
   - finally, global/root definitions available via `ScopeRegistry`.
   The concrete traversal order is encapsulated in internal `DefinitionResolver`/`ScopeRegistry` logic; there is no dedicated stable `ScopeResolver` class in the public API.
4. For the selected `BeanDefinition`, the corresponding `InstanceFactory` is invoked (via `resolveValue` or a similar internal call) to either reuse a cached instance or create a new one.

### 3. Caching Strategy

- `SingleInstanceFactory` uses an `InstanceHolder` with lazy initialization plus synchronized access (`KoinPlatformTools.synchronized` / double-checked locking) to ensure a single instance.
- `FactoryInstanceFactory` never caches; it always creates a fresh instance.
- `ScopedInstanceFactory` stores instances in `Scope.instances`, keyed by definition id and bound to that scope's lifecycle.
- ViewModels are exposed via dedicated `ViewModel` definitions/factories on Android (`koin-androidx-viewmodel` / `koin-androidx-compose` etc.). They leverage `Koin` scopes and integrate with the Android `ViewModelStore` but are not just plain generic `ScopedInstanceFactory` entries.

### 4. Parameters and Secondary Types

- `ParametersHolder` carries runtime parameters and passes them down to the definition lambda:

```kotlin
get<Repo> { parametersOf(userId) }
```

- Secondary bindings (e.g. `bind<Interface>()`) register extra keys pointing to the same `BeanDefinition`, so one instance can satisfy multiple types:

```kotlin
singleOf(::SqlUserRepository) {
    bind<UserRepository>()
    bind<AnalyticsSource>()
}
```

`BeanDefinition.secondaryTypes` adds additional keys into the lookup registries, so `get<AnalyticsSource>()` or `get<UserRepository>()` resolve to the same instance.

### 5. Cycle Detection

- `Koin` handles dependency graphs at runtime only. Cycle detection is implemented using an internal tracking of the active resolution chain (e.g., a stack of keys plus depth counters). If the same key appears again in the current chain, `Koin` throws a `CyclicDependencyException`. Specific internal class names are not stable and should not be relied upon.

### 6. Eager Vs Lazy Singletons

- Definitions with `createdAtStart = true` are instantiated during `startKoin`.
- All other singles are instantiated lazily on first `get()`.
- This is useful for infrastructure services that must be ready early, but it increases startup time and should be used deliberately.

### 7. ScopeRegistry Lifecycle

- `ScopeRegistry` keeps a `scopeId → Scope` map.
- `createScope` uses `ScopeDefinition` declared in modules (`module { scope(named("feature")) { ... } }`).
- Each `Scope` holds resolution helpers and its instance cache. `Scope.close()` clears its cached instances and notifies registered `ScopeCallback`s.
- Linked scopes (`scope.linkTo(parentScope)`) add ids into `Scope.links`, extending the search space during resolution.

### 8. Concurrency Guarantees

- `InstanceHolder` uses platform-specific locking via `KoinPlatformTools` to make singleton initialization thread-safe.
- Scope creation and closing are managed in a thread-safe manner within `ScopeRegistry`.
- As a result, concurrent `get()` calls for the same singleton or scoped definition are handled safely.

---

## Дополнительные Вопросы
- Как `Koin` реализует `qualifier` в multiplatform окружении?
- Какая стратегия у `Koin` при работе с coroutine scopes внутри `Definition`?
- Как оптимизировать разрешение `Koin` при больших графах (например, через `module { includes(...) }`)?
- Что потребуется для миграции этих internals при переходе на `Koin` 4.x?

## Follow-ups
- How does `Koin` implement `qualifier` in a multiplatform environment?
- What strategy does `Koin` use when working with coroutine scopes inside a `Definition`?
- How can you optimize `Koin` resolution for large graphs (e.g., via `module { includes(...) }`)?
- What would be required to adapt these internals when migrating to `Koin` 4.x?

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