---
id: android-023
title: "React Native vs Flutter comparison / Сравнение React Native и Flutter"
aliases: ["React Native vs Flutter", "Сравнение React Native и Flutter"]

# Classification
topic: android
subtopics: [kmp]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]

# Workflow & relations
status: draft
moc: moc-android
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-28

tags: [android/cross-platform, android/kmp, difficulty/medium]
---

# Вопрос (RU)

> Сравните React Native и Flutter: архитектуру, производительность, экосистему и сценарии использования.

# Question (EN)

> Compare React Native and Flutter: architecture, performance, ecosystem, and use cases.

---

## Ответ (RU)

**React Native** (Facebook) и **Flutter** (Google) — ведущие фреймворки для кроссплатформенной разработки. Ключевые различия:

### Архитектура

**React Native:**
- JavaScript-движок (Hermes/JSC) взаимодействует с нативными модулями через Bridge
- Рендерит нативные UI-компоненты (`Button`, Text, `View`)
- Требует явных нативных модулей для платформенных API

```kotlin
// ✅ React Native: нативный модуль для Android
class ToastModule(reactContext: ReactApplicationContext) :
 ReactContextBaseJavaModule(reactContext) {

 override fun getName() = "ToastModule"

 @ReactMethod
 fun show(message: String) {
 Toast.makeText(reactApplicationContext, message, LENGTH_SHORT).show()
 }
}
```

**Flutter:**
- Dart VM компилируется в нативный код (ARM/x64)
- Skia `Canvas` рендерит собственные UI-виджеты (Material/Cupertino)
- Platform Channels для взаимодействия с нативными API

```kotlin
// ✅ Flutter: платформенный канал для Android
class MainActivity : FlutterActivity() {
 private val CHANNEL = "com.example/toast"

 override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
 MethodChannel(flutterEngine.dartExecutor, CHANNEL).setMethodCallHandler { call, result ->
 if (call.method == "showToast") {
 Toast.makeText(this, call.arguments as String, LENGTH_SHORT).show()
 result.success(null)
 }
 }
 }
}
```

### Производительность

**React Native:**
- 60 FPS для простых UI
- Bridge-узкое место при интенсивном взаимодействии JS ↔ Native
- Новая архитектура (JSI + Fabric) устраняет Bridge

**Flutter:**
- Стабильные 60/120 FPS
- Нет моста — прямые вызовы через FFI
- Меньшее потребление памяти для сложных анимаций

```dart
// ✅ Flutter: оптимизированный рендеринг списков
ListView.builder(
 itemCount: 10000,
 itemBuilder: (context, index) => ListTile(title: Text('Item $index')),
)
```

```javascript
// ❌ React Native: может лагать на больших списках без оптимизации
<FlatList
 data={items}
 renderItem={({item}) => <Text>{item.title}</Text>}
 // ✅ Оптимизация:
 removeClippedSubviews={true}
 maxToRenderPerBatch={10}
/>
```

### Экосистема

| Критерий | React Native | Flutter |
|----------|-------------|---------|
| **Библиотеки** | NPM (2M+ пакетов) | pub.dev (40K+ пакетов) |
| **Нативная интеграция** | Прямой доступ к Android/iOS либам | Через Platform Channels |
| **Обновление зависимостей** | Чаще breaking changes | Стабильная версионность |
| **Сообщество** | Больше (2015) | Быстрорастущее (2017) |

### Сценарии Использования

**Выбирайте React Native:**
- Команда с опытом JavaScript/TypeScript
- Нужна глубокая интеграция с веб-экосистемой (shared-код)
- Прототипирование с существующими React-компонентами
- Требуется множество готовых нативных модулей из NPM

**Выбирайте Flutter:**
- Критична высокая производительность (60+ FPS анимации)
- Нужен pixel-perfect UI, идентичный на всех платформах
- Desktop/Web приложения (одна кодовая база для 6 платформ)
- Предпочтение строгой типизации (Dart) vs динамической (JS)

### Trade-offs

```kotlin
// ❌ React Native: требует синхронизации стилей с нативными изменениями
<View style={{backgroundColor: colors.primary}}>
 <Button title="Native Button" />
</View>
```

```dart
// ✅ Flutter: полный контроль над пикселями, независимость от платформы
Container(
 color: Theme.of(context).primaryColor,
 child: ElevatedButton(child: Text('Flutter Button')),
)
```

**React Native:**
- ➕ Быстрый старт для JS-разработчиков
- ➕ Нативный look-and-feel из коробки
- ➖ Сложность отладки Bridge-проблем
- ➖ Фрагментация версий в экосистеме

**Flutter:**
- ➕ Предсказуемый рендеринг на всех устройствах
- ➕ Hot reload с сохранением состояния
- ➖ Большие размеры APK/IPA (4+ MB минимум)
- ➖ Меньше готовых нативных решений

## Answer (EN)

**React Native** (Facebook) and **Flutter** (Google) are leading cross-platform frameworks. Key differences:

### Architecture

**React Native:**
- JavaScript engine (Hermes/JSC) communicates with native modules via Bridge
- Renders native UI components (`Button`, Text, `View`)
- Requires explicit native modules for platform APIs

```kotlin
// ✅ React Native: native module for Android
class ToastModule(reactContext: ReactApplicationContext) :
 ReactContextBaseJavaModule(reactContext) {

 override fun getName() = "ToastModule"

 @ReactMethod
 fun show(message: String) {
 Toast.makeText(reactApplicationContext, message, LENGTH_SHORT).show()
 }
}
```

**Flutter:**
- Dart VM compiles to native code (ARM/x64)
- Skia `Canvas` renders custom UI widgets (Material/Cupertino)
- Platform Channels for native API interaction

```kotlin
// ✅ Flutter: platform channel for Android
class MainActivity : FlutterActivity() {
 private val CHANNEL = "com.example/toast"

 override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
 MethodChannel(flutterEngine.dartExecutor, CHANNEL).setMethodCallHandler { call, result ->
 if (call.method == "showToast") {
 Toast.makeText(this, call.arguments as String, LENGTH_SHORT).show()
 result.success(null)
 }
 }
 }
}
```

### Performance

**React Native:**
- 60 FPS for simple UIs
- Bridge bottleneck during intensive JS ↔ Native communication
- New architecture (JSI + Fabric) eliminates Bridge

**Flutter:**
- Consistent 60/120 FPS
- No bridge — direct FFI calls
- Lower memory footprint for complex animations

```dart
// ✅ Flutter: optimized list rendering
ListView.builder(
 itemCount: 10000,
 itemBuilder: (context, index) => ListTile(title: Text('Item $index')),
)
```

```javascript
// ❌ React Native: can lag on large lists without optimization
<FlatList
 data={items}
 renderItem={({item}) => <Text>{item.title}</Text>}
 // ✅ Optimization:
 removeClippedSubviews={true}
 maxToRenderPerBatch={10}
/>
```

### Ecosystem

| Criterion | React Native | Flutter |
|-----------|-------------|---------|
| **Libraries** | NPM (2M+ packages) | pub.dev (40K+ packages) |
| **Native integration** | Direct access to Android/iOS libs | Via Platform Channels |
| **Dependency updates** | More breaking changes | Stable versioning |
| **Community** | Larger (since 2015) | Rapidly growing (since 2017) |

### Use Cases

**Choose React Native:**
- Team with JavaScript/TypeScript expertise
- Deep integration with web ecosystem (shared code)
- Prototyping with existing React components
- Need many ready-made native modules from NPM

**Choose Flutter:**
- High performance critical (60+ FPS animations)
- Pixel-perfect UI identical across platforms
- Desktop/Web apps (single codebase for 6 platforms)
- Preference for strong typing (Dart) vs dynamic (JS)

### Trade-offs

```kotlin
// ❌ React Native: requires style sync with native changes
<View style={{backgroundColor: colors.primary}}>
 <Button title="Native Button" />
</View>
```

```dart
// ✅ Flutter: full pixel control, platform-independent
Container(
 color: Theme.of(context).primaryColor,
 child: ElevatedButton(child: Text('Flutter Button')),
)
```

**React Native:**
- ➕ Fast start for JS developers
- ➕ Native look-and-feel out of the box
- ➖ Bridge debugging complexity
- ➖ Ecosystem version fragmentation

**Flutter:**
- ➕ Predictable rendering across devices
- ➕ Hot reload with state preservation
- ➖ Larger APK/IPA sizes (4+ MB minimum)
- ➖ Fewer ready-made native solutions

---

## Follow-ups

- How does React Native's new architecture (JSI + Fabric + TurboModules) compare to Flutter's architecture?
- What are the CI/CD considerations for React Native vs Flutter projects?
- How do developer tools (debuggers, profilers, IDEs) compare between the two?
- What's the strategy for migrating an existing native Android app to React Native or Flutter?
- How do both frameworks handle platform-specific code sharing and conditional compilation?

## References

- 
- 
- [React Native New Architecture](https://reactnative.dev/docs/the-new-architecture/landing-page)
- [Flutter Architecture Overview](https://docs.flutter.dev/resources/architectural-overview)
- [Performance Comparison Study](https://medium.com/swlh/flutter-vs-react-native-vs-native-deep-performance-comparison)

## Related Questions

### Prerequisites (Easier)
- - Native vs cross-platform trade-offs
- - Android UI fundamentals

### Related (Medium)
- [[q-kotlin-multiplatform-overview--kotlin--hard]] - Kotlin Multiplatform approach
- - UI toolkit comparison within Android
- - Hybrid approaches

### Advanced (Harder)
- - Flutter rendering pipeline
- - Bridge performance tuning
- - Security in cross-platform frameworks
