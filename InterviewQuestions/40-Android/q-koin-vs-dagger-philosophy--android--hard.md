---
id: android-612
title: Koin vs Dagger/Hilt Philosophy / Философия Koin против Dagger/Hilt
aliases:
  - Koin vs Dagger Philosophy
  - Философия Koin и Dagger
  - Runtime vs Compile-Time DI Philosophy
topic: android
subtopics:
  - di-koin
  - di-hilt
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
  - c-dagger
  - c-hilt
  - q-koin-fundamentals--android--medium
  - q-dagger-framework-overview--android--hard
  - q-koin-vs-hilt-comparison--android--medium
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/di-koin
  - android/di-hilt
  - dependency-injection
  - architecture/philosophy
  - difficulty/hard
sources:
  - url: https://github.com/InsertKoinIO/koin/blob/master/README.md#koin-philosophy
    note: Koin design principles
  - url: https://dagger.dev/dev-guide/
    note: Dagger design philosophy and compile-time guarantees
  - url: https://developer.android.com/training/dependency-injection/hilt-android
    note: Hilt documentation on architectural goals
---

# Вопрос (RU)
> Сравните философию DI Koin и Dagger/Hilt: какие цели они решают, как формализуют граф зависимостей, и какие архитектурные компромиссы требуют? Проанализируйте влияние на тестирование, эволюцию продукта и командные практики.

# Question (EN)
> Contrast the dependency-injection philosophy behind Koin and Dagger/Hilt: which problems they optimize for, how they formalize the graph, and which architectural trade-offs they impose. Discuss ramifications for testing, product evolution, and team practices.

---

## Ответ (RU)

### 1. Цели и философия

| Критерий | Koin (Service Locator) | Dagger/Hilt (Compile-time DI) |
|----------|------------------------|------------------------------|
| **Цель** | Ускорить delivery и облегчить bootstrap | Гарантировать типобезопасный граф до запуска |
| **Парадигма** | DSL + runtime регистрация | Аннотации + генерация кода |
| **Гибкость** | Высокая (переопределения на лету) | Жёсткие контракты и валидация |
| **Философия** | «Простой DI для Kotlin, минимальный ceremony» | «Чёткие границы компонентов и scope» |

- Koin принимает компромисс «меньше правил → выше риск». Его философия — **низкий порог** и **конфигурируемость в runtime**. Граф создаётся лениво, ошибки ловятся тестами/продом.
- Dagger/Hilt следует принципу **правильность важнее скорости**: декларативная модель, compile-time proof и строгие компоненты.

### 2. Формализация графа

**Koin:**
- Граф описывается DSL и хранится как набор `BeanDefinition`.
- Связи выявляются при вызове `get()`, поэтому допускает частичную конфигурацию (можно загружать модули динамически).
- Scope — runtime объект, который можно создавать/закрывать по требованию.

**Dagger/Hilt:**
- Граф строится аннотациями `@Module`, `@Component`, `@InstallIn`.
- Нужна полная информация при компиляции, иначе kapt/ksp оборвёт сборку.
- Scope жёстко привязан к компонентам (`SingletonComponent`, `ActivityRetainedComponent`).

### 3. Архитектурные компромиссы

- **Koin**:
  - ✅ Быстрый onboarding команды, можно прототипировать без обширной схемы.
  - ✅ Легче экспериментировать: `loadKoinModules`, `declare` для override.
  - ❌ Нет compile-time «контракта», возможны runtime краши из-за отсутствующих зависимостей.
  - ❌ Сложнее масштабировать граф на тысячи binding-ов без дополнительных практик (`checkModules` обязателен).

- **Dagger/Hilt**:
  - ✅ Гарантирует граф, помогает рефакторить (ошибки ловятся сборкой).
  - ✅ Структурирует архитектуру через компоненты и scope — дисциплинирует команду.
  - ❌ Высокая стоимость обучения, особенно для middle/джун разработчиков.
  - ❌ Overhead на аннотации/генерацию, более медленная сборка.

### 4. Влияние на тестирование

- Koin:
  - Проще мокать через `declare`, `loadKoinModules`.
  - Интеграционные тесты требуют `checkModules`, иначе рискуем пропустить отсутствующие зависимости.
  - Возможен эффект «silent failure»: если binding не найден, можно случайно получить другой (при неправильных qualifiers).

- Dagger/Hilt:
  - Тесты используют `@TestInstallIn`, `@BindValue`, создают alternative modules.
  - Ошибка wiring проявится до запуска тестов (компиляция).
  - Нужно больше boilerplate для динамических override; тестовые компоненты могут быть тяжеловесны.

### 5. Эволюция продукта и команда

- Команда с быстрыми итерациями, фичами-пилотами чаще выбирает Koin → легко добавить временный binding или Feature-toggle-модуль.
- Enterprise/large scale предпочитает Dagger/Hilt:
  - Кодовая база переживает ротации команды.
  - Dependency graph служит документацией.
  - Возможен tooling: graphviz, `dagger.spi`.
- Смешанные команды иногда стартуют с Koin, затем мигрируют на Hilt, когда граф стабилизируется.

### 6. Философские выводы

- **Service Locator против DI**: Koin сознательно смещает ответственность на разработчика/тесты → философия «простота > безопасность». Dagger/Hilt напротив: «безопасность графа > скорость» и продвигают «dependency inversion как контракт».
- **Declarative vs Imperative**: Hilt описывает граф декларативно (аннотации), Koin — исполняемым DSL.
- **Переопределение зависимостей**: Koin считает override часть философии; Dagger/Hilt требует явных компонентов/модулей, чтобы избежать неявных подмен.

---

## Answer (EN)

### 1. Goals and philosophy

| Dimension | Koin (Service Locator) | Dagger/Hilt (Compile-time DI) |
|-----------|------------------------|-------------------------------|
| **Primary goal** | Reduce ceremony, speed up delivery | Guarantee a type-safe graph pre-runtime |
| **Paradigm** | Kotlin DSL + runtime registry | Annotations + generated code |
| **Flexibility** | High (overrides at runtime) | Strict contracts and validation |
| **Philosophy** | “Pragmatic DI for Kotlin” | “Graph correctness and explicit boundaries” |

- Koin embraces “fewer rules, more agility”. Graph materializes lazily; runtime checks and tests bear the risk.
- Dagger/Hilt favors “correctness over convenience”, mandating declarative components and compile-time proofs.

### 2. Graph formalization

- **Koin** stores `BeanDefinition` objects populated from DSL modules; dependencies resolve on demand, allowing partial/dynamic graphs.
- **Dagger/Hilt** builds the graph at compile time from `@Module`/`@Component`/`@InstallIn`; missing bindings fail the build. Scopes map directly to generated components.

### 3. Architectural trade-offs

- **Koin**
  - ✅ Fast onboarding, easy prototyping, hot-swappable modules.
  - ❌ Lacks compile-time guarantees; large graphs need discipline (`checkModules`, naming qualifiers).
- **Dagger/Hilt**
  - ✅ Compile-time enforcement, predictable refactoring, tooling support.
  - ❌ Learning curve and build-time cost; dynamic overrides require explicit test components.

### 4. Testing impact

- Koin simplifies overrides (`declare`, `loadKoinModules`); integration tests must run `checkModules` to catch missing bindings.
- Dagger/Hilt uses generated test components (`@TestInstallIn`, `@BindValue`); misconfigurations fail during compilation but require more boilerplate.

### 5. Product evolution & team dynamics

- Fast-moving teams or feature spikes benefit from Koin’s runtime flexibility.
- Large/long-lived products lean on Dagger/Hilt for maintainability and knowledge transfer; the graph acts as living documentation.
- Hybrid strategies (start with Koin, migrate to Hilt) surface when an app scales beyond the comfort zone of runtime DI.

### 6. Philosophical takeaways

- **Service Locator vs DI**: Koin intentionally trades strict DI purity for simplicity; Dagger/Hilt enforces dependency inversion contracts.
- **Declarative vs Imperative**: Hilt’s declarative annotations contrast with Koin’s imperative DSL.
- **Override semantics**: Koin treats overrides as first-class, while Dagger/Hilt requires structured modules/components to avoid ambiguous substitutions.

---

## Follow-ups
- Какие риски возникают при смешанном использовании Koin и Hilt в одном приложении?
- Как объяснить junior-разработчику, почему Hilt сложнее, но безопаснее?
- Какие метрики (build time, crash rate) стоит отслеживать при выборе DI-фреймворка?
- Возможно ли построить compile-time валидацию поверх Koin (например, через codegen)?

## References

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]
- https://github.com/InsertKoinIO/koin/blob/master/README.md#koin-philosophy
- https://dagger.dev/dev-guide/
- [Hilt](https://developer.android.com/training/dependency-injection/hilt-android)


## Related Questions

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- [[q-koin-fundamentals--android--medium]]
- [[q-dagger-framework-overview--android--hard]]
- [[q-koin-vs-hilt-comparison--android--medium]]

