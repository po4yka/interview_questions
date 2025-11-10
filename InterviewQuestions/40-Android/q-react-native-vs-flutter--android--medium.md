---
id: android-023
title: "React Native vs Flutter comparison / Сравнение React Native и Flutter"
aliases: ["React Native vs Flutter", "Сравнение React Native и Flutter"]
topic: android
subtopics: [ui-views, ui-compose, kmp]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
sources: ["https://github.com/amitshekhariitbhu/android-interview-questions"]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy]
created: 2025-10-06
updated: 2025-11-10
tags: [android/ui-views, android/ui-compose, android/kmp, difficulty/medium]

---

# Вопрос (RU)

> Сравните React Native и Flutter: архитектуру, производительность, экосистему и сценарии использования.

# Question (EN)

> Compare React Native and Flutter: architecture, performance, ecosystem, and use cases.

---

## Ответ (RU)

**React Native** (Facebook/Meta) и **Flutter** (Google) — ведущие фреймворки для кроссплатформенной разработки. Ключевые различия:

См. также: [[c-cross-platform-development]]

### Архитектура

**React Native:**
- JavaScript-движок (Hermes/JSC) выполняет JS-код и взаимодействует с нативными модулями через механизм межъязыкового взаимодействия (исторически JSON Bridge; в новой архитектуре — JSI + Fabric + TurboModules с более эффективной моделью)
- Использует нативные UI-компоненты платформы (например, `View`, Text, Button на Android/iOS)
- Для доступа к платформенным API требуются нативные модули (Android/iOS), экспортирующие функциональность в JS

```kotlin
// ✅ React Native: нативный модуль для Android (упрощённый пример)
class ToastModule(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName() = "ToastModule"

    @ReactMethod
    fun show(message: String) {
        Toast.makeText(reactApplicationContext, message, Toast.LENGTH_SHORT).show()
    }
}
```

**Flutter:**
- В режиме разработки использует Dart VM с JIT, в релизных сборках для мобильных платформ Dart-код компилируется AOT в нативный код (ARM/x64), без отдельной VM в рантайме
- Графический движок (Skia) рендерит собственные UI-виджеты (Material/Cupertino и др.) поверх холста, не опираясь напрямую на нативные виджеты
- Использует Platform Channels (и другие механизмы, например FFI) для взаимодействия c нативными API

```kotlin
// ✅ Flutter: платформенный канал для Android (упрощённый пример)
class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example/toast"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                if (call.method == "showToast") {
                    val message = call.arguments as? String ?: ""
                    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
                    result.success(null)
                } else {
                    result.notImplemented()
                }
            }
    }
}
```

### Производительность

**React Native:**
- Может обеспечивать 60 FPS для простых и средних по сложности UI при корректном использовании FlatList, мемоизации и оптимизации рендеринга
- Историческая проблема — узкое место "bridge" при частых/объёмных обменах данными JS ↔ Native (анимации, большие списки, gesture events)
- Новая архитектура (JSI + Fabric + TurboModules) снижает накладные расходы и делает взаимодействие более прямым и предсказуемым, уменьшая зависимость от старого сериализованного bridge

**Flutter:**
- Спроектирован для достижения плавных 60/120 FPS при рендеринге, особенно для сложной графики и анимаций, если не блокировать основной изолят и не перегружать кадр
- Нет исторического JS-bridge: UI и логика на Dart взаимодействуют с движком напрямую, а нативные вызовы идут через эффективные канал/FFI механизмы
- Производительность и потребление памяти обычно более предсказуемы, но не гарантированы автоматически — всё зависит от реализации

```dart
// ✅ Flutter: оптимизированный рендеринг списков
ListView.builder(
  itemCount: 10000,
  itemBuilder: (context, index) => ListTile(title: Text('Item $index')),
)
```

```javascript
// ⚠️ React Native: большие списки без оптимизации могут лагать
<FlatList
  data={items}
  renderItem={({ item }) => <Text>{item.title}</Text>}
  // ✅ Базовая оптимизация:
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

### Экосистема

| Критерий | React Native | Flutter |
|----------|-------------|---------|
| **Библиотеки** | NPM (много пакетов, включая RN-специфичные) | pub.dev (десятки тысяч пакетов, ориентированных на Flutter/Dart) |
| **Нативная интеграция** | Через нативные модули/bridged-вызовы к Android/iOS | Через Platform Channels/FFI к Android/iOS |
| **Обновление зависимостей** | Возможны частые изменения API и поддержка не всех пакетов | Сильная централизация экосистемы, относительно предсказуемая семантическая версионность SDK |
| **Сообщество** | Большое, зрелое (старт ~2015) | Быстрорастущее (старт ~2017) |

### Сценарии Использования

**Выбирайте React Native, если:**
- Команда сильна в JavaScript/TypeScript и React
- Нужна интеграция с веб-экосистемой и частичный шаринг логики (не UI) с React web
- Важна возможность быстро прототипировать с использованием знакомой React-парадигмы
- Планируется активное использование существующих RN-библиотек и нативных модулей из NPM

**Выбирайте Flutter, если:**
- Критична высокая и предсказуемая производительность UI/анимаций
- Нужен максимально консистентный pixel-perfect UI на разных платформах
- Важна поддержка мобильных, веб и desktop из одной кодовой базы
- Предпочитаете статически типизированный язык (Dart) и единообразие стека

### Trade-offs

```jsx
// ⚠️ React Native: визуальный вид и стили могут зависеть от нативных компонент платформы,
// требуется учитывать изменения платформенных стилей
<View style={{ backgroundColor: colors.primary }}>
  <Button title="Native Button" />
</View>
```

```dart
// ✅ Flutter: полный контроль над пикселями, UI не зависит от нативных виджетов платформы
Container(
  color: Theme.of(context).primaryColor,
  child: ElevatedButton(child: Text('Flutter Button')),
)
```

**React Native:**
- Быстрый вход для JS/React-разработчиков
- Использует нативные компоненты и даёт платформенный look-and-feel
- Потенциальные сложности при отладке проблем на границе JS ↔ Native
- Разнородное качество и поддержка сторонних пакетов, риски фрагментации

**Flutter:**
- Предсказуемый собственный рендеринг на разных устройствах
- Мощный hot reload/hot restart (особенно удобен в разработке UI)
- Более крупный минимальный размер приложения за счёт движка и рантайма
- Меньше "из коробки" нативных модулей под специфичные платформенные фичи, иногда требуется писать собственные плагины

## Answer (EN)

**React Native** (Facebook/Meta) and **Flutter** (Google) are leading cross-platform frameworks. Key differences:

See also: [[c-cross-platform-development]]

### Architecture

**React Native:**
- A JavaScript engine (Hermes/JSC) executes JS code and communicates with native modules via a cross-language mechanism (historically a serialized JSON bridge; in the new architecture: JSI + Fabric + TurboModules with a more efficient model)
- Uses platform-native UI components (e.g., `View`, Text, Button on Android/iOS)
- Requires native modules (Android/iOS) to expose platform APIs to JS

```kotlin
// ✅ React Native: native module for Android (simplified example)
class ToastModule(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    override fun getName() = "ToastModule"

    @ReactMethod
    fun show(message: String) {
        Toast.makeText(reactApplicationContext, message, Toast.LENGTH_SHORT).show()
    }
}
```

**Flutter:**
- Uses a Dart VM with JIT in development; for mobile release builds Dart code is AOT-compiled to native machine code (ARM/x64), without a separate Dart VM at runtime
- The Skia-based rendering engine draws Flutter's own widgets (Material/Cupertino, etc.) directly to a canvas instead of relying on platform-native widgets
- Uses Platform Channels (and other mechanisms such as FFI) to interact with native APIs

```kotlin
// ✅ Flutter: platform channel for Android (simplified example)
class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example/toast"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
            .setMethodCallHandler { call, result ->
                if (call.method == "showToast") {
                    val message = call.arguments as? String ?: ""
                    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
                    result.success(null)
                } else {
                    result.notImplemented()
                }
            }
    }
}
```

### Performance

**React Native:**
- Can deliver 60 FPS for many UIs when using FlatList, memoization, and avoiding unnecessary re-renders
- Historical bottleneck is the JS ↔ Native bridge for frequent/large data exchanges (animations, large lists, gesture/event floods)
- The new architecture (JSI + Fabric + TurboModules) reduces overhead and dependence on the old serialized bridge model, enabling more direct and efficient interaction

**Flutter:**
- Designed to hit smooth 60/120 FPS rendering, especially for complex graphics and animations, assuming frames are not overloaded
- No traditional JS-style bridge: Dart code talks to the engine directly, and native calls go through efficient channel/FFI mechanisms
- Typically offers more predictable performance characteristics, but not guaranteed automatically — still depends on implementation

```dart
// ✅ Flutter: optimized list rendering
ListView.builder(
  itemCount: 10000,
  itemBuilder: (context, index) => ListTile(title: Text('Item $index')),
)
```

```javascript
// ⚠️ React Native: large lists without optimization can stutter
<FlatList
  data={items}
  renderItem={({ item }) => <Text>{item.title}</Text>}
  // ✅ Basic optimization:
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

### Ecosystem

| Criterion | React Native | Flutter |
|-----------|-------------|---------|
| **Libraries** | NPM (a huge ecosystem, including RN-specific packages) | pub.dev (tens of thousands of Dart/Flutter packages) |
| **Native integration** | Via native modules/bridged calls to Android/iOS | Via Platform Channels/FFI to Android/iOS |
| **Dependency updates** | Potential for breaking changes and uneven package maintenance | Strongly curated core SDK, relatively predictable semantic versioning |
| **Community** | Large, mature (since ~2015) | Rapidly growing (since ~2017) |

### Use Cases

**Choose React Native if:**
- Your team is strong in JavaScript/TypeScript and React
- You need integration with the web ecosystem and partial logic sharing (not UI) with React web
- You want fast prototyping using the familiar React paradigm
- You plan to leverage existing RN libraries and native modules from NPM

**Choose Flutter if:**
- High and predictable UI/animation performance is critical
- You need a highly consistent, pixel-perfect UI across platforms
- You target mobile, web, and desktop from a single codebase
- You prefer a statically typed language (Dart) and a unified stack

### Trade-offs

```jsx
// ⚠️ React Native: visual appearance and styles depend on platform-native components,
// so you must account for platform style changes
<View style={{ backgroundColor: colors.primary }}>
  <Button title="Native Button" />
</View>
```

```dart
// ✅ Flutter: full pixel-level control; UI is independent of platform-native widgets
Container(
  color: Theme.of(context).primaryColor,
  child: ElevatedButton(child: Text('Flutter Button')),
)
```

**React Native:**
- Fast onboarding for JS/React developers
- Uses native components, providing a platform-consistent look-and-feel
- Potential debugging complexity at the JS ↔ Native boundary
- Ecosystem quality/maintenance can be inconsistent; risk of fragmentation

**Flutter:**
- Predictable, engine-controlled rendering across devices
- Powerful hot reload/hot restart (especially for rapid UI iteration)
- Larger minimum app size due to bundling the engine/runtime
- Fewer ready-made plugins for very niche native integrations; sometimes you must write your own

---

## Follow-ups

- How does React Native's new architecture (JSI + Fabric + TurboModules) compare to Flutter's architecture?
- What are the CI/CD considerations for React Native vs Flutter projects?
- How do developer tools (debuggers, profilers, IDEs) compare between the two?
- What's the strategy for migrating an existing native Android app to React Native or Flutter?
- How do both frameworks handle platform-specific code sharing and conditional compilation?

## References

- [React Native New Architecture](https://reactnative.dev/docs/the-new-architecture/landing-page)
- [Flutter Architecture Overview](https://docs.flutter.dev/resources/architectural-overview)
- [Performance Comparison Study](https://medium.com/swlh/flutter-vs-react-native-vs-native-deep-performance-comparison)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Android app components overview

### Related (Medium)
- [[q-android-architectural-patterns--android--medium]] - Android architectural patterns overview
