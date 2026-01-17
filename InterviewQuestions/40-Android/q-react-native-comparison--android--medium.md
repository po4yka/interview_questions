---\
id: android-169
title: KMM vs React Native / KMM против React Native
aliases: [KMM vs React Native, KMM против React Native, React Native Comparison, React Native Сравнение]
topic: android
subtopics: [architecture-mvvm, kmp]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-mvvm, q-how-does-jetpackcompose-work--android--medium, q-kmm-dependency-injection--android--medium, q-kmm-ktor-networking--android--medium, q-play-app-signing--android--medium, q-react-native-vs-flutter--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/kmp, difficulty/medium, javascript, kmp, kotlin, multiplatform, reactnative]
anki_cards:
  - slug: android-169-0-en
    front: "What are the key differences between KMM and React Native?"
    back: |
      **Architecture:**
      - **React Native:** JS layer -> JS Bridge -> Native -> Platform SDK
      - **KMM:** Native UI -> Shared Kotlin -> Platform SDK (no JS bridge)

      **Code Sharing:**
      - RN: ~90%+ (including UI)
      - KMM: ~50-80% (business logic, separate native UIs)

      **Type Safety:** KMM has full compile-time safety; RN relies on TypeScript with runtime bridge risks.

      **Performance:** KMM closer to native (no bridge overhead).
    tags:
      - android_general
      - difficulty::medium
  - slug: android-169-0-ru
    front: "В чём ключевые различия между KMM и React Native?"
    back: |
      **Архитектура:**
      - **React Native:** JS слой -> JS Bridge -> Native -> Platform SDK
      - **KMM:** Нативный UI -> Shared Kotlin -> Platform SDK (без JS bridge)

      **Шаринг кода:**
      - RN: ~90%+ (включая UI)
      - KMM: ~50-80% (бизнес-логика, отдельные нативные UI)

      **Типобезопасность:** KMM имеет полную compile-time безопасность; RN полагается на TypeScript с runtime рисками на bridge.

      **Производительность:** KMM ближе к нативной (без overhead bridge).
    tags:
      - android_general
      - difficulty::medium

---\
# Вопрос (RU)
>
Сравните Kotlin Multiplatform Mobile с React Native. Каковы архитектурные различия, bridge overhead и зрелость экосистемы? Чем отличается JavaScript vs Kotlin/Native подход?

# Question (EN)
>
Compare Kotlin Multiplatform Mobile with React Native. What are the architectural differences, bridge overhead, and ecosystem maturity? How do they differ in terms of JavaScript vs Kotlin/Native approach?

## Ответ (RU)

### Архитектурные Различия

**React Native**: JavaScript-слой → JS Bridge → Native модули → Platform SDK
- UI в JSX/TSX, логика в JavaScript/TypeScript
- Взаимодействие с нативным слоем через bridge (marshalling/serialization параметров и результатов)
- JavaScriptCore/Hermes runtime

**KMM**: Native UI → Shared Kotlin (multiplatform) → Platform SDK
- UI нативный (Android Views/Compose, iOS UIKit/SwiftUI)
- Общая бизнес-логика на Kotlin, компилируется в JVM-байткод на Android и в native бинарники (Kotlin/Native) на iOS и других платформах
- Нет JavaScript-bridge; используется прямой interop с нативными API (FFI/генерируемые биндинги), overhead обычно существенно ниже, чем при JS-bridge

### Bridge Overhead

**React Native**:
```javascript
// ❌ Пример с ощутимым bridge overhead: сериализация + переход через bridge + десериализация
const result = await NativeModules.DataProcessor
  .processData(JSON.stringify(data));
const parsed = JSON.parse(result);
// Фактические задержки зависят от объёма данных, частоты вызовов и реализации,
// но частые/тяжёлые обмены через bridge могут становиться bottleneck.
```

**KMM**:
```kotlin
// ✅ Прямой вызов общей логики без JS-bridge
class DataProcessor {
    fun processData(): List<Item> = /* ... */
}

val result = DataProcessor().processData()  // Нет JSON-сериализации между слоями UI и shared-кодом
// Есть накладные расходы обычного вызова/interop, но они близки к нативным.
```

**Производительность**: при вычислительно и data-intensive задачах общая логика в KMM обычно ближе к нативной по скорости,
так как избегает частых JS-bridge переходов. Конкретный выигрыш зависит от профиля нагрузки и реализации и не является гарантированным «10x» во всех случаях.

### Type Safety

**React Native**:
```javascript
// ❌ Без строгой типизации и контрактов через bridge повышен риск runtime-ошибок
const jsonResult = await taskModule.getTasks();  // Возвращает строку
const tasks = JSON.parse(jsonResult);            // Проверка структуры только в runtime
```
- При использовании TypeScript/`Flow` можно получить сильную статическую типизацию JS-слоя,
  но контракты поверх native bridge по-прежнему требуют внимательного согласования и остаются уязвимыми к рассинхронизации типов.

**KMM**:
```kotlin
// ✅ Полная статическая типизация в общем Kotlin-коде
@Serializable
data class Task(val id: String, val title: String)

class TaskRepository {
    suspend fun getTasks(): List<Task> = api.fetchTasks()
}
// Безопасное рефакторингом пространство, автодополнение, строгие сигнатуры между модулями.
```

### Code Sharing

**React Native**: потенциально 90%+ reuse (включая UI)
- Единый JSX/TSX UI для обеих платформ
- Быстрая итерация (fast refresh)
- Доступ к нативным возможностям через bridge (готовые модули или собственные)

**KMM**: обычно 50-80% reuse (бизнес-логика, data layer, общие модули)
- Отдельные нативные UI (Compose/Views на Android, SwiftUI/UIKit на iOS)
- Прямой доступ к общему коду из нативных слоёв
- Платформенно-специфичная реализация UI и отдельных API

### Performance Benchmarks

| Metric | React Native | KMM |
|--------|--------------|-----|
| **Startup** | Чаще выше накладные расходы из-за загрузки JS bundle и инициализации VM | Ближе к нативному startup, т.к. общая логика интегрируется в нативное приложение |
| **Animations** | Возможны задержки при heavy JS-логике или частых bridge-вызовах; modern RN (Fabric/JSTurbo/JSI, Reanimated) снижает проблему | Нативный рендеринг (Compose/SwiftUI и др.), обычно стабильные 60fps при корректной реализации |
| **Memory** | Выше за счёт JS VM и дополнительных слоёв | Как правило ниже, ближе к нативным приложениям |
| **`List` Rendering** | При больших списках и тяжёлых JS-обработках возможен jank из-за bridge/JS нагрузки | Нативные списки с доступом к общему коду дают предсказуемое поведение и лучшую устойчивость |

(Числовые значения сильно зависят от конкретного приложения и реализации; важно объяснить принципы, а не опираться на жёсткие универсальные цифры.)

### Developer Experience

**React Native**:
- ✅ Fast Refresh / hot reload
- ✅ Большая экосистема JavaScript/TypeScript (npm)
- ✅ Переносимость знаний React
- ❌ Потенциальная сложность отладки bridge и различий платформенных модулей
- ❌ Типобезопасность интерфейсов native ↔ JS требует дисциплины и инструментов

**KMM**:
- ✅ Статическая типизация Kotlin и общая модель для бизнес-логики
- ✅ Отсутствие JS-bridge, привычный для Android-разработчиков стек инструментов
- ✅ Плавное внедрение в существующие нативные приложения (начиная с отдельных модулей)
- ❌ Более тяжёлые сборки и настройка мультиплатформенного проекта
- ❌ Необходимость поддержки отдельных нативных UI-команд или экспертизы

### Ecosystem Maturity

**React Native**: зрелая экосистема (c 2015, поддерживается Meta)
- Множество плагинов и библиотек, большая community
- Популярные решения: react-navigation, react-native-firebase и др.

**KMM**: активно развивающаяся экосистема (Kotlin Multiplatform стабилизируется постепенно; поддержка JetBrains, участие Google)
- Сотни multiplatform-библиотек
- Примеры: Ktor, SQLDelight, `Koin`, kotlinx.serialization, kotlinx.coroutines

### Platform Feature Access

**React Native**:
- Доступ к платформенным возможностям возможен сразу через собственные native-модули
- На популярные функции часто можно полагаться на community-пакеты, но иногда приходится ждать обновлений или писать обвязку самостоятельно

**KMM**:
- Day-zero доступ к платформенным API через Kotlin/Native interop и expect/actual
- Нет зависимости от наличия JS-обёрток; platform-specific код можно реализовать напрямую

### When to Choose

**React Native**:
- Сильная команда JavaScript/React
- Быстрый MVP и shared UI — приоритет
- Быстрая итерация и наличие готовых UI-компонентов критичны

**KMM**:
- Сильная Kotlin/Android-компетенция
- Критичны нативный UX, производительность и типобезопасность
- Уже есть нативные приложения, в которые нужно добавить общий слой логики без замены UI

**Examples**:
- React Native: используется в продуктах Meta, Discord, Shopify и др.
- KMM: используется в продакшене рядом компаний (включая крупные), часто для общих SDK/модулей между Android и iOS.

## Answer (EN)

### Architectural Differences

**React Native**: JavaScript layer → JS Bridge → Native modules → Platform SDK
- UI in JSX/TSX, logic in JavaScript/TypeScript
- Interaction with native layer via bridge (parameter/result marshalling/serialization)
- JavaScriptCore/Hermes runtime

**KMM**: Native UI → Shared Kotlin (multiplatform) → Platform SDK
- Native UI (Android Views/Compose, iOS UIKit/SwiftUI)
- Shared business logic in Kotlin; compiled to JVM bytecode on Android and native binaries (Kotlin/Native) on iOS/other targets
- No JavaScript bridge; uses direct interop with platform APIs (FFI/generated bindings), with overhead typically much lower than a JS bridge

### Bridge Overhead

**React Native**:
```javascript
// ❌ Example with noticeable bridge overhead: serialization + crossing + deserialization
const result = await NativeModules.DataProcessor
  .processData(JSON.stringify(data));
const parsed = JSON.parse(result);
// Actual latency depends on payload size, call frequency, and implementation,
// but heavy/very frequent bridge traffic can become a bottleneck.
```

**KMM**:
```kotlin
// ✅ Direct call into shared logic without a JS bridge
class DataProcessor {
    fun processData(): List<Item> = /* ... */
}

val result = DataProcessor().processData()  // No JSON serialization between UI and shared layer
// There is normal call/interop overhead, but it's close to native function calls.
```

**Performance**: for compute- and data-intensive operations, KMM shared logic usually behaves closer to fully native implementations
because it avoids frequent JS bridge crossings. Any "X times faster" claim is highly workload-dependent and should not be treated as universal.

### Type Safety

**React Native**:
```javascript
// ❌ Without strong typing and explicit contracts over the bridge, runtime errors are more likely
const jsonResult = await taskModule.getTasks();  // Returns string
const tasks = JSON.parse(jsonResult);            // Structure validated only at runtime
```
- With TypeScript or `Flow` you can have strong static typing on the JavaScript side,
  but native ↔ JS bridge contracts still require discipline and tooling to keep types in sync.

**KMM**:
```kotlin
// ✅ Strong compile-time type safety in shared Kotlin code
@Serializable
data class Task(val id: String, val title: String)

class TaskRepository {
    suspend fun getTasks(): List<Task> = api.fetchTasks()
}
// Safer refactoring, IDE support, and strict signatures between modules.
```

### Code Sharing

**React Native**: potentially 90%+ reuse (including UI)
- Single JSX/TSX UI for both platforms
- Fast Refresh for rapid iteration
- Uses bridge calls (community or custom native modules) for native capabilities

**KMM**: typically around 50-80% reuse (business logic, data, shared modules)
- Separate native UIs (Compose/Views on Android, SwiftUI/UIKit on iOS)
- Direct access to shared code from platform UI layers
- UI and some APIs remain platform-specific by design

### Performance Benchmarks

| Metric | React Native | KMM |
|--------|--------------|-----|
| **Startup** | Often higher overhead due to JS bundle loading and VM initialization | Closer to native startup; shared code is integrated into a native app |
| **Animations** | May suffer when heavy JS work or frequent bridge calls are on the critical path; newer RN stack (Fabric/JSI/Reanimated) mitigates this | Native rendering (Compose/SwiftUI/etc.), typically smooth 60fps when implemented correctly |
| **Memory** | Generally higher due to JS VM and extra layers | Generally lower, closer to native |
| **`List` Rendering** | Large lists with complex JS logic can jank if constrained by JS/bridge | Native list components with shared logic give more predictable performance |

(Numeric values are highly app-specific; focus on principles rather than treating any specific numbers as universal.)

### Developer Experience

**React Native**:
- ✅ Fast Refresh/hot reload
- ✅ Large JavaScript/TypeScript ecosystem (npm)
- ✅ React skills are directly applicable
- ❌ Bridge and platform-specific modules can complicate debugging
- ❌ Strong typing across the native bridge requires careful contracts and tooling

**KMM**:
- ✅ Strong static typing with Kotlin and a unified model for business logic
- ✅ No JS bridge, familiar tooling for Kotlin/Android developers
- ✅ Gradual adoption into existing native apps (start with shared modules)
- ❌ Heavier build setup and configuration for multiplatform projects
- ❌ Separate native UI implementations to design, build, and maintain

### Ecosystem Maturity

**React Native**: mature ecosystem (since 2015, backed by Meta)
- Many libraries and integrations
- Large community and hiring pool
- Popular libraries: react-navigation, react-native-firebase, etc.

**KMM**: growing ecosystem (Kotlin Multiplatform stabilizing; led by JetBrains with Google involvement)
- Hundreds of multiplatform libraries
- Common choices: Ktor, SQLDelight, `Koin`, kotlinx.serialization, kotlinx.coroutines

### Platform Feature Access

**React Native**:
- Native capabilities available immediately via custom native modules
- For many features you can rely on community packages; sometimes you wait for updates or write/maintain your own wrappers

**KMM**:
- Day-zero access to platform APIs through Kotlin/Native interop and expect/actual mechanisms
- No dependency on JS wrappers; platform-specific implementations can be written directly in Kotlin or native languages

### When to Choose

**React Native**:
- Strong JavaScript/React team
- Need for rapid cross-platform UI delivery and fast iteration
- Willingness to accept some overhead/complexity of the bridge for higher UI code reuse

**KMM**:
- Strong Kotlin/Android expertise
- Native UX/performance and type safety are high priorities
- Existing native apps where you want to share business logic without replacing the UI tech stack

**Examples**:
- React Native: used in products by Meta, Discord, Shopify, and others.
- KMM: adopted in production by several companies (including large ones), often for shared modules/SDKs across Android and iOS.

## Follow-ups

- How would you architect a hybrid native/KMM codebase for gradual migration?
- What are the trade-offs when choosing to share UI code vs keeping it platform-specific?
- How do you handle platform-specific features in shared KMM code?
- What are the debugging challenges with React Native bridge issues?
- How does Compose Multiplatform compare to KMM's approach?

## References

- [Kotlin Multiplatform documentation](https://kotlinlang.org/docs/multiplatform.html)
- [React Native official documentation](https://reactnative.dev/docs/getting-started)

## Related Questions

### Prerequisites / Concepts

- [[c-mvvm]]

### Prerequisites
- Basic understanding of Kotlin and JavaScript
- Familiarity with mobile app development

### Related
- [[q-how-does-jetpackcompose-work--android--medium]]
- [[q-play-app-signing--android--medium]]

### Advanced
- Advanced KMM architecture patterns
- Platform-specific interop strategies
