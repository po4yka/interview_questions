---
id: android-612
title: Koin vs Dagger/Hilt Philosophy / Философия Koin против Dagger/Hilt
aliases:
- Koin vs Dagger Philosophy
- Runtime vs Compile-Time DI Philosophy
- Философия Koin и Dagger
topic: android
subtopics:
- architecture-clean
- di-hilt
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
- c-dagger
- c-dependency-injection
- c-hilt
- q-dagger-build-time-optimization--android--medium
- q-dagger-framework-overview--android--hard
- q-hilt-entry-points--android--medium
- q-koin-fundamentals--android--medium
- q-koin-vs-hilt-comparison--android--medium
created: 2025-11-02
updated: 2025-11-11
tags:
- android/architecture-clean
- android/di-hilt
- android/di-koin
- architecture/philosophy
- dependency-injection
- difficulty/hard
anki_cards:
- slug: android-612-0-en
  language: en
  anki_id: 1768397114577
  synced_at: '2026-01-23T16:45:05.531458'
- slug: android-612-0-ru
  language: ru
  anki_id: 1768397114601
  synced_at: '2026-01-23T16:45:05.533337'
sources:
- https://dagger.dev/dev-guide/
- https://developer.android.com/training/dependency-injection/hilt-android
- https://github.com/InsertKoinIO/koin/blob/master/README.md#koin-philosophy
---
# Вопрос (RU)
> Сравните философию DI `Koin` и Dagger/Hilt: какие цели они решают, как формализуют граф зависимостей, и какие архитектурные компромиссы требуют? Проанализируйте влияние на тестирование, эволюцию продукта и командные практики.

# Question (EN)
> Contrast the dependency-injection philosophy behind `Koin` and Dagger/Hilt: which problems they optimize for, how they formalize the graph, and which architectural trade-offs they impose. Discuss ramifications for testing, product evolution, and team practices.

---

## Ответ (RU)
`Koin` и Dagger/Hilt решают одну задачу — управление зависимостями и композицию объекта графа — но с принципиально разной философией и компромиссами.

- `Koin`: runtime DI с акцентом на простоту, гибкость и скорость итераций; меньше ceremony и более мягкие правила ценой отсутствия compile-time валидации графа.
- Dagger/Hilt: compile-time DI с акцентом на корректность, явные границы компонентов и масштабируемость; строгие контракты и генерация кода ценой сложности и более высокой стоимости обучения.

Эти различия влияют на:
- архитектуру (runtime-реестр против строго типизированного графа с компонентами и scope);
- тестирование (легкие подмены и `checkModules` в `Koin` против compile-time гарантий и тестовых модулей в `Hilt`);
- эволюцию продукта (`Koin` удобен для быстрых изменений и экспериментов, Dagger/Hilt — для долгоживущих и крупных кодовых баз);
- командные практики (`Koin` снижает порог входа, но требует дисциплины; Dagger/Hilt дисциплинирует через структуру, но сложнее для новичков).

## Answer (EN)
`Koin` and Dagger/Hilt target the same core problem—dependency management and object graph composition—but follow fundamentally different philosophies and trade-offs.

- `Koin`: runtime DI focused on simplicity, flexibility, and fast iteration; less ceremony and looser rules at the cost of missing compile-time graph validation.
- Dagger/Hilt: compile-time DI focused on correctness, explicit component/scope boundaries, and scalability; strong contracts and code generation at the cost of higher complexity and learning curve.

These differences impact:
- architecture (runtime registry vs strongly typed generated graph with components and scopes);
- testing (easy overrides and `checkModules` in `Koin` vs compile-time guarantees and dedicated test modules in `Hilt`);
- product evolution (`Koin` favors rapid changes and experiments, Dagger/Hilt favors large, long-lived codebases);
- team practices (`Koin` lowers entry barrier but needs discipline, Dagger/Hilt enforces structure but is harder for juniors).

## Follow-ups
- Какие риски возникают при смешанном использовании `Koin` и `Hilt` в одном приложении?
- Как объяснить junior-разработчику, почему `Hilt` сложнее, но безопаснее?
- Какие метрики (build time, crash rate) стоит отслеживать при выборе DI-фреймворка?
- Возможно ли построить compile-time валидацию поверх `Koin` (например, через codegen)?

## References

- [[c-dependency-injection]]
- [[c-dagger]]
- [[c-hilt]]
- [[q-koin-fundamentals--android--medium]]
- [[q-dagger-framework-overview--android--hard]]
- https://github.com/InsertKoinIO/koin/blob/master/README.md#koin-philosophy
- https://dagger.dev/dev-guide/
- https://developer.android.com/training/dependency-injection/hilt-android

## Related Questions

- [[c-dagger]]
- [[c-dependency-injection]]
- [[c-hilt]]
- [[q-dagger-build-time-optimization--android--medium]]
- [[q-dagger-framework-overview--android--hard]]
- [[q-hilt-entry-points--android--medium]]
- [[q-koin-fundamentals--android--medium]]
- [[q-koin-vs-hilt-comparison--android--medium]]

## Краткая Версия
- `Koin`: runtime DI, гибкость и низкий порог входа ценой меньших compile-time гарантий.
- Dagger/Hilt: compile-time DI, строгий контракт и масштабируемость ценой сложности и ceremony.

## Подробная Версия
### 1. Цели И Философия
| Критерий | `Koin` (runtime DI / registry-style) | Dagger/Hilt (compile-time DI) |
|----------|------------------------------------|-------------------------------|
| **Цель** | Ускорить delivery и облегчить bootstrap | Гарантировать типобезопасный граф до запуска |
| **Парадигма** | DSL + runtime регистрация | Аннотации + генерация кода |
| **Гибкость** | Высокая (переопределения на лету) | Жёсткие контракты и валидация |
| **Философия** | «Простой DI для Kotlin, минимальный ceremony» | «Чёткие границы компонентов и scope» |
- `Koin` принимает компромисс «меньше правил → выше риск». Его философия — низкий порог, конфигурируемость в runtime и возможность динамически загружать/перегружать модули. Граф создаётся лениво при разрешении зависимостей; риски ловятся тестами (в том числе через `checkModules`) и рантаймом.
- Dagger/Hilt следует принципу «правильность важнее скорости»: декларативная модель, compile-time proof и строгие компоненты.
### 2. Формализация Графа
**`Koin`:**
- Граф описывается DSL и хранится как набор `BeanDefinition`.
- Связи выявляются при вызове `get()` (или инъекциях), что позволяет частичную конфигурацию и динамическую загрузку модулей.
- Scope — runtime-объект, который можно создавать/закрывать по требованию.
**Dagger/Hilt:**
- Граф строится аннотациями `@Module`, `@Component`, `@InstallIn`.
- Нужна полная (или достаточно полная) информация для генерации кода при компиляции; при отсутствии binding-ов kapt/ksp оборвёт сборку.
- Scope жёстко привязан к компонентам (`SingletonComponent`, `ActivityRetainedComponent` и т.д.).
### 3. Архитектурные Компромиссы
- **`Koin`**:
  - ✅ Быстрый onboarding команды, можно прототипировать без обширной схемы.
  - ✅ Легче экспериментировать: `loadKoinModules`, `declare` для override.
  - ✅ Гибкая работа с runtime scope-ами.
  - ❌ Нет compile-time контракта, возможны runtime-краши из-за отсутствующих зависимостей или конфликтующих определений.
  - ❌ Сложнее масштабировать граф на тысячи binding-ов без дополнительных практик (`checkModules`, строгая политика qualifiers).
- **Dagger/Hilt**:
  - ✅ Гарантирует корректность графа и помогает рефакторить (ошибки ловятся сборкой).
  - ✅ Структурирует архитектуру через компоненты и scope — дисциплинирует команду.
  - ❌ Высокая стоимость обучения, особенно для middle/джун разработчиков.
  - ❌ Overhead на аннотации/генерацию, более медленная сборка.
### 4. Влияние На Тестирование
- **`Koin`**:
  - Проще мокать через `declare`, `loadKoinModules` и тестовые модули.
  - Рекомендуется использовать `checkModules` в тестах, чтобы валидировать наличие всех зависимостей и не полагаться только на runtime-обнаружение.
  - Ошибки разрешения (отсутствие или неоднозначность определения) приводят к явным исключениям; при неправильном использовании qualifiers и override возможны конфликтующие/неоднозначные определения.
- **Dagger/Hilt**:
  - Тесты используют `@TestInstallIn`, `@BindValue` и альтернативные модули.
  - Ошибка wiring проявится до запуска тестов (на этапе генерации/компиляции).
  - Нужно больше boilerplate для динамических override; тестовые компоненты могут быть тяжеловесны.
### 5. Эволюция Продукта И Команда
- Команда с быстрыми итерациями и пилотами чаще выбирает `Koin`: легко добавить временный binding или feature-toggle-модуль.
- Enterprise/large scale предпочитает Dagger/Hilt:
  - Кодовая база переживает ротации команды.
  - Dependency graph служит документацией.
  - Возможен tooling: визуализация графа, `dagger.spi`.
- Смешанные команды иногда стартуют с `Koin`, затем мигрируют на `Hilt`, когда граф стабилизируется.
### 6. Философские Выводы
- Runtime registry / `Service` Locator-подход против жёсткого compile-time DI: `Koin` использует runtime-реестр определений и ленивое разрешение, смещая часть гарантий на разработчика и тесты; Dagger/Hilt обеспечивают строгие compile-time гарантии графа.
- Declarative vs Imperative: `Hilt` описывает граф декларативно (аннотации), `Koin` — исполняемым DSL.
- Переопределение зависимостей: `Koin` считает override частью философии (для тестов и фич-флагов); Dagger/Hilt требуют явных модулей/компонентов для подмен.

## Short Version
- `Koin`: runtime DI focused on simplicity, flexibility, and fast iteration at the cost of weaker compile-time guarantees.
- Dagger/Hilt: compile-time DI focused on correctness, explicit structure, and scalability at the cost of complexity and ceremony.

## Detailed Version
### 1. Goals and Philosophy
| Dimension | `Koin` (runtime DI / registry-style) | Dagger/Hilt (compile-time DI) |
|-----------|------------------------------------|-------------------------------|
| **Primary goal** | Reduce ceremony, speed up delivery | Guarantee a type-safe graph pre-runtime |
| **Paradigm** | Kotlin DSL + runtime registry | Annotations + generated code |
| **Flexibility** | High (runtime overrides, dynamic modules) | Strict contracts and validation |
| **Philosophy** | "Simple, pragmatic DI for Kotlin with minimal ceremony" | "Graph correctness and explicit component/scope boundaries" |
- `Koin` embraces "fewer rules, more agility": low entry barrier, runtime configurability, dynamic module loading/overrides. The graph materializes lazily on resolution; risks are mitigated via tests (including `checkModules`) and runtime behavior.
- Dagger/Hilt favors "correctness over convenience", with declarative components and compile-time guarantees.
### 2. Graph Formalization
- **`Koin`**:
  - Describes the graph via a DSL and stores definitions as `BeanDefinition` objects.
  - Resolves dependencies on demand (`get()` / injections), enabling partial configuration and dynamic module loading.
  - Scopes are runtime entities created and closed explicitly.
- **Dagger/Hilt**:
  - Builds the graph at compile time from `@Module`, `@Component`, `@InstallIn`.
  - Missing or inconsistent bindings fail code generation/compilation.
  - Scopes map directly to generated components (e.g., `SingletonComponent`, `ActivityRetainedComponent`).
### 3. Architectural Trade-offs
- **`Koin`**
  - ✅ Fast onboarding, easy prototyping, hot-swappable modules.
  - ✅ Flexible runtime scopes and overrides.
  - ❌ No compile-time contract; missing or conflicting definitions cause runtime failures.
  - ❌ Large graphs require discipline (`checkModules`, clear qualifier strategy) to stay maintainable.
- **Dagger/Hilt**
  - ✅ Compile-time enforcement, safer refactoring, strong tooling support.
  - ✅ Component/scope structure enforces architectural boundaries.
  - ❌ Steeper learning curve, especially for less experienced developers.
  - ❌ Annotation/codegen overhead, slower builds; dynamic overrides are more involved.
### 4. Testing Impact
- **`Koin`**
  - Simplifies overrides via `declare`, `loadKoinModules`, and dedicated test modules.
  - `checkModules` is recommended in test suites to validate the graph and catch missing bindings early.
  - Resolution errors surface as explicit exceptions; the risk lies in ambiguous/overlapping definitions or misused qualifiers, not in silently resolving to an arbitrary binding.
- **Dagger/Hilt**
  - Uses `@TestInstallIn`, `@BindValue`, and alternative modules to wire test graphs.
  - Misconfigurations are caught during generation/compilation before tests run.
  - Requires more boilerplate and explicit configuration for overrides; test components can become heavy.
### 5. Product Evolution & Team Dynamics
- Fast-moving teams or feature spikes can benefit from `Koin`'s runtime flexibility and lower initial overhead.
- Large/long-lived products tend to rely on Dagger/Hilt for maintainability and resilience to team changes:
  - The dependency graph acts as living documentation.
  - Tooling (e.g., graph visualization, SPI integrations) supports deeper analysis.
- Some teams start with `Koin` and later migrate to `Hilt` once the architecture and dependency graph stabilize.
### 6. Philosophical Takeaways
- Runtime registry / `Service`-Locator-style vs strict compile-time DI: `Koin`'s runtime registry and lazy resolution trade strict compile-time guarantees for simplicity and flexibility. Dagger/Hilt enforce dependency inversion contracts and graph safety at compile time.
- Declarative vs Imperative: `Hilt` uses declarative annotations; `Koin` uses an imperative, executable DSL.
- Override semantics: `Koin` treats overrides as first-class (including for tests and experiments). Dagger/Hilt requires explicit, structured modules/components for substitutions to avoid ambiguous overrides.
