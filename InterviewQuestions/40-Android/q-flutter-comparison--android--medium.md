---
id: android-252
title: KMM vs Flutter Comparison / Сравнение KMM и Flutter
aliases: [KMM vs Flutter, Kotlin Multiplatform Mobile vs Flutter, Сравнение KMM и Flutter]
topic: android
subtopics:
 - architecture-clean
 - kmp
question_kind: theory
difficulty: medium
original_language: en
language_tags:
 - en
 - ru
status: reviewed
moc: moc-android
related:
sources:
 - https://flutter.dev/docs
 - https://kotlinlang.org/docs/multiplatform.html
created: 2025-10-15
updated: 2025-11-03
tags: [android/architecture-clean, android/kmp, cross-platform, difficulty/medium, flutter, multiplatform]
---

# Вопрос (RU)

> Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки.

## Краткая Версия

KMM — shared business logic (60-70%) с native UI; Flutter — shared UI + logic (90-95%). KMM для native UX и performance, Flutter для скорости разработки и multi-platform. Trade-offs: KMM выше производительность но требует native expertise.

## Подробная Версия

Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки:

**Архитектурные различия:**
- KMM: Shared business logic + native UI (Jetpack Compose, SwiftUI)
- Flutter: Shared UI + logic с platform channels для native APIs

**Производительность:**
- KMM: 100% native, startup 200-500ms, size 15-25MB
- Flutter: 95-98% native, startup 400-800ms, size 20-35MB

**Trade-offs:**
- KMM: Лучшая производительность и UX, но требует separate UI development
- Flutter: Быстрее разработка и code reuse, но overhead engine

**Когда выбирать:**
- KMM: Native UX критичен, существующее native app, performance-critical
- Flutter: Быстрый MVP, custom UI, маленькая команда, multi-platform

# Question (EN)

> Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development.

## `Short` Version

KMM — shared business logic (60-70%) with native UI; Flutter — shared UI + logic (90-95%). KMM for native UX and performance, Flutter for development speed and multi-platform. Trade-offs: KMM higher performance but requires native expertise.

## Detailed Version

Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development:

**Architectural differences:**
- KMM: Shared business logic + native UI (Jetpack Compose, SwiftUI)
- Flutter: Shared UI + logic with platform channels for native APIs

**Performance:**
- KMM: 100% native, startup 200-500ms, size 15-25MB
- Flutter: 95-98% native, startup 400-800ms, size 20-35MB

**Trade-offs:**
- KMM: Better performance and UX, but requires separate UI development
- Flutter: Faster development and code reuse, but engine overhead

**When to choose:**
- KMM: Native UX critical, existing native app, performance-critical
- Flutter: Rapid MVP, custom UI, small team, multi-platform

## Ответ (RU)

KMM и Flutter представляют два фундаментально разных подхода к кросс-платформенной разработке.

### Теоретические Основы

**Кросс-платформенная разработка** — стратегия создания приложений для multiple платформ с максимальным code reuse. Основные подходы:

**Native Development** — отдельные codebases для каждой платформы, максимальная производительность и UX, но high development cost.

**Cross-platform** — shared codebase с platform-specific адаптациями. Trade-offs между производительностью, UX и development speed.

**Key Considerations:**
- **Platform fragmentation** — Android/iOS имеют разные UI patterns и system APIs
- **Performance requirements** — games/AR vs business apps vs content apps
- **Team composition** — native expertise vs generalist developers
- **Time-to-market** — MVP speed vs long-term maintainability

### Архитектурные Различия

**KMM (Kotlin Multiplatform Mobile)**:
- Shared: Бизнес-логика 60-80% (repositories, use cases, models)
- Platform-specific: Native UI (Jetpack Compose, SwiftUI)
- Технология: Kotlin компилируется в native код для каждой платформы
- Философия: "Native UI with shared logic"

**Flutter**:
- Shared: UI + логика 90-95% (widgets, business logic, state)
- Platform-specific: Минимум 5-10% (platform channels для native APIs)
- Технология: Dart с собственным rendering engine (Skia)
- Философия: "Write once, run anywhere"

```kotlin
// ✅ KMM: Shared business logic
class TaskRepository(
 private val api: TaskApi,
 private val database: TaskDatabase
) {
 suspend fun getTasks(): Result<List<Task>> {
 return try {
 val remote = api.fetchTasks()
 database.saveTasks(remote)
 Result.success(remote)
 } catch (e: Exception) {
 Result.success(database.getTasks())
 }
 }
}

// Android UI (Jetpack Compose)
@Composable
fun TaskList(tasks: List<Task>) {
 LazyColumn {
 items(tasks) { TaskItem(it) } // ✅ Material Design
 }
}

// iOS UI (SwiftUI)
struct TaskList: View {
 var body: some View {
 List(tasks) { TaskRow($0) } // ✅ iOS HIG
 }
}
```

```dart
// ✅ Flutter: Shared UI + logic
class TaskRepository {
 Future<Result<List<Task>>> getTasks() async {
 try {
 final remote = await api.fetchTasks();
 await database.saveTasks(remote);
 return Success(remote);
 } catch (e) {
 return Success(await database.getTasks());
 }
 }
}

// Single UI for both platforms
class TaskList extends StatelessWidget {
 Widget build(context) {
 return ListView.builder(
 itemBuilder: (_, i) => TaskItem(tasks[i]) // ❌ Same UI everywhere
 );
 }
}
```

### Производительность

**Startup Time**:
- KMM: 200-500ms (native)
- Flutter: 400-800ms (Dart VM init + engine)

**Runtime Performance**:
- KMM: 100% native (прямой доступ к Metal/Vulkan)
- Flutter: 95-98% native (AOT компиляция, Skia rendering)

**App Size**:
- KMM: 15-25MB (использует platform SDKs)
- Flutter: 20-35MB (включает Flutter engine ~10MB)

**Memory**:
- KMM: Ниже (native memory management)
- Flutter: Выше (Dart VM + Skia engine overhead)

### Development Experience

**Team Size & Skills**:
- KMM: 6-9 разработчиков (Kotlin devs, Android devs, iOS devs)
- Flutter: 3-5 разработчиков (Flutter devs)

**Development Speed** (feature: User Profile Screen):
- KMM: 8 дней (2 дня shared logic + 3 дня Android + 3 дня iOS)
- Flutter: 4 дня (2 дня logic + 2 дня shared UI)

**Code Reuse**:
- KMM: 60-70%
- Flutter: 90-95%

### Platform Integration

**KMM**:
```kotlin
// ✅ Direct native API access (zero overhead)
class LocationManager(context: Context) {
 private val client = LocationServices
 .getFusedLocationProviderClient(context)

 suspend fun getLocation(): Location? {
 return client.lastLocation.await() // ✅ Direct Android SDK
 }
}
```

**Flutter**:
```dart
// ❌ Platform channel bridge (serialization overhead)
class LocationManager {
 static const platform = MethodChannel('location');

 Future<Map?> getLocation() async {
 return await platform.invokeMethod('getLocation'); // ❌ Bridge
 }
}
```

### Use Cases

**Выбирайте KMM когда**:
- Native UX критичен (banking, health apps)
- Существующее native приложение (постепенная миграция)
- Performance-critical (games, AR/VR, image processing)
- Immediate access к новым platform features
- Команда с native expertise

**Выбирайте Flutter когда**:
- Быстрый MVP (стартапы, prototypes)
- Consistent brand experience (custom UI design)
- Маленькая команда / ограниченный budget
- Multi-platform (Web + Desktop + Mobile)
- Custom animations и pixel-perfect UI

### Cost Analysis

**Initial Development**:
- KMM: Выше (duplicate UI)
- Flutter: Ниже (shared UI)

**Maintenance**:
- KMM: Средний (separate UIs)
- Flutter: Ниже (single codebase)

**`Long`-term**:
- KMM: Platform updates immediate, future-proof
- Flutter: Depends on Flutter SDK updates

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Performance Critical** → KMM
**Small Team/Budget** → Flutter

### Лучшие Практики

- **Пилотный проект** — начните с small feature для оценки подхода перед full commitment
- **Platform expertise** — сохраняйте native разработчиков для platform-specific требований
- **Architecture alignment** — выбирайте подход соответствующий existing team skills и architecture
- **Performance monitoring** — измеряйте реальные метрики перед/после выбора технологии
- **Migration strategy** — планируйте gradual adoption с rollback планом

### Типичные Ошибки

- **Игнорирование UX differences** — Android/iOS имеют разные interaction patterns
- **Performance assumptions** — Flutter performance достаточна для большинства apps
- **Team composition mismatch** — native-only команда не подходит для Flutter
- **Over-engineering** — KMM для simple CRUD apps увеличивает complexity
- **Ignoring platform evolution** — технологии развиваются, reassess периодически

## Answer (EN)

KMM and Flutter represent two fundamentally different approaches to cross-platform development.

### Theoretical Foundations

**Cross-platform development** — strategy for building apps across multiple platforms with maximum code reuse. Main approaches:

**Native Development** — separate codebases per platform, maximum performance and UX, but high development cost.

**Cross-platform** — shared codebase with platform-specific adaptations. Trade-offs between performance, UX, and development speed.

**Key Considerations:**
- **Platform fragmentation** — Android/iOS have different UI patterns and system APIs
- **Performance requirements** — games/AR vs business apps vs content apps
- **Team composition** — native expertise vs generalist developers
- **Time-to-market** — MVP speed vs long-term maintainability

### Architectural Differences

**KMM (Kotlin Multiplatform Mobile)**:
- Shared: Business logic 60-80% (repositories, use cases, models)
- Platform-specific: Native UI (Jetpack Compose, SwiftUI)
- Technology: Kotlin compiles to native code per platform
- Philosophy: "Native UI with shared logic"

**Flutter**:
- Shared: UI + logic 90-95% (widgets, business logic, state)
- Platform-specific: Minimal 5-10% (platform channels for native APIs)
- Technology: Dart with custom rendering engine (Skia)
- Philosophy: "Write once, run anywhere"

```kotlin
// ✅ KMM: Shared business logic
class TaskRepository(
 private val api: TaskApi,
 private val database: TaskDatabase
) {
 suspend fun getTasks(): Result<List<Task>> {
 return try {
 val remote = api.fetchTasks()
 database.saveTasks(remote)
 Result.success(remote)
 } catch (e: Exception) {
 Result.success(database.getTasks())
 }
 }
}

// Android UI (Jetpack Compose)
@Composable
fun TaskList(tasks: List<Task>) {
 LazyColumn {
 items(tasks) { TaskItem(it) } // ✅ Material Design
 }
}

// iOS UI (SwiftUI)
struct TaskList: View {
 var body: some View {
 List(tasks) { TaskRow($0) } // ✅ iOS HIG
 }
}
```

```dart
// ✅ Flutter: Shared UI + logic
class TaskRepository {
 Future<Result<List<Task>>> getTasks() async {
 try {
 final remote = await api.fetchTasks();
 await database.saveTasks(remote);
 return Success(remote);
 } catch (e) {
 return Success(await database.getTasks());
 }
 }
}

// Single UI for both platforms
class TaskList extends StatelessWidget {
 Widget build(context) {
 return ListView.builder(
 itemBuilder: (_, i) => TaskItem(tasks[i]) // ❌ Same UI everywhere
 );
 }
}
```

### Performance

**Startup Time**:
- KMM: 200-500ms (native)
- Flutter: 400-800ms (Dart VM init + engine)

**Runtime Performance**:
- KMM: 100% native (direct Metal/Vulkan access)
- Flutter: 95-98% native (AOT compilation, Skia rendering)

**App Size**:
- KMM: 15-25MB (uses platform SDKs)
- Flutter: 20-35MB (includes Flutter engine ~10MB)

**Memory**:
- KMM: Lower (native memory management)
- Flutter: Higher (Dart VM + Skia engine overhead)

### Development Experience

**Team Size & Skills**:
- KMM: 6-9 developers (Kotlin devs, Android devs, iOS devs)
- Flutter: 3-5 developers (Flutter devs)

**Development Speed** (feature: User Profile Screen):
- KMM: 8 days (2 days shared logic + 3 days Android + 3 days iOS)
- Flutter: 4 days (2 days logic + 2 days shared UI)

**Code Reuse**:
- KMM: 60-70%
- Flutter: 90-95%

### Platform Integration

**KMM**:
```kotlin
// ✅ Direct native API access (zero overhead)
class LocationManager(context: Context) {
 private val client = LocationServices
 .getFusedLocationProviderClient(context)

 suspend fun getLocation(): Location? {
 return client.lastLocation.await() // ✅ Direct Android SDK
 }
}
```

**Flutter**:
```dart
// ❌ Platform channel bridge (serialization overhead)
class LocationManager {
 static const platform = MethodChannel('location');

 Future<Map?> getLocation() async {
 return await platform.invokeMethod('getLocation'); // ❌ Bridge
 }
}
```

### Use Cases

**Choose KMM when**:
- Native UX is critical (banking, health apps)
- Existing native app (incremental migration)
- Performance-critical (games, AR/VR, image processing)
- Immediate access to new platform features
- Team has native expertise

**Choose Flutter when**:
- Rapid MVP (startups, prototypes)
- Consistent brand experience (custom UI design)
- Small team / limited budget
- Multi-platform (Web + Desktop + Mobile)
- Custom animations and pixel-perfect UI

### Cost Analysis

**Initial Development**:
- KMM: Higher (duplicate UI)
- Flutter: Lower (shared UI)

**Maintenance**:
- KMM: Medium (separate UIs)
- Flutter: Lower (single codebase)

**`Long`-term**:
- KMM: Platform updates immediate, future-proof
- Flutter: Depends on Flutter SDK updates

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Performance Critical** → KMM
**Small Team/Budget** → Flutter

### Best Practices

- **Pilot project** — start with small feature to evaluate approach before full commitment
- **Platform expertise** — maintain native developers for platform-specific requirements
- **Architecture alignment** — choose approach matching existing team skills and architecture
- **Performance monitoring** — measure real metrics before/after technology choice
- **Migration strategy** — plan gradual adoption with rollback plan

### Common Pitfalls

- **Ignoring UX differences** — Android/iOS have different interaction patterns
- **Performance assumptions** — Flutter performance sufficient for most apps
- **Team composition mismatch** — native-only team doesn't fit Flutter
- **Over-engineering** — KMM for simple CRUD apps increases complexity
- **Ignoring platform evolution** — technologies evolve, reassess periodically

## References

- https://kotlinlang.org/docs/multiplatform.html - KMM official documentation
- https://flutter.dev/docs - Flutter official documentation
- https://developer.android.com/kotlin/multiplatform - Android KMM guide

## Follow-ups

- 

## Related Questions

- 

