---
id: 20251012-122714
title: "KMM vs Flutter Comparison / Сравнение KMM и Flutter"
aliases: ["KMM vs Flutter", "Kotlin Multiplatform Mobile vs Flutter", "Сравнение KMM и Flutter"]
topic: android
subtopics: [kmp, architecture-clean]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/kmp, android/architecture-clean, cross-platform, multiplatform, difficulty/medium]
date created: Tuesday, October 28th 2025, 7:40:08 am
date modified: Thursday, October 30th 2025, 12:47:52 pm
---

# Вопрос (RU)

> Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки. Каковы архитектурные различия, характеристики производительности и trade-offs? Когда выбирать KMM вместо Flutter и наоборот?

# Question (EN)

> Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development. What are the architectural differences, performance characteristics, and trade-offs? When should you choose KMM over Flutter and vice versa?

## Ответ (RU)

KMM и Flutter представляют два фундаментально разных подхода к кросс-платформенной разработке.

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

**Long-term**:
- KMM: Platform updates immediate, future-proof
- Flutter: Depends on Flutter SDK updates

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Performance Critical** → KMM
**Small Team/Budget** → Flutter

## Answer (EN)

KMM and Flutter represent two fundamentally different approaches to cross-platform development.

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

**Long-term**:
- KMM: Platform updates immediate, future-proof
- Flutter: Depends on Flutter SDK updates

### Decision Framework

**Native Experience Priority** → KMM
**Speed to Market Priority** → Flutter
**Existing Native App** → KMM (incremental adoption)
**Multi-platform (Web/Desktop)** → Flutter
**Performance Critical** → KMM
**Small Team/Budget** → Flutter

## Follow-ups

- How do you migrate an existing native Android app to KMM vs Flutter?
- What are the performance implications of platform channels in Flutter?
- How does KMM handle expect/actual declarations for platform-specific code?
- Can you combine KMM for logic with Compose Multiplatform for UI?
- What are the testing strategies for KMM vs Flutter?

## References

- https://kotlinlang.org/docs/multiplatform.html - KMM official documentation
- https://flutter.dev/docs - Flutter official documentation
- https://developer.android.com/kotlin/multiplatform - Android KMM guide

## Related Questions

### Prerequisites
- Native Android development fundamentals
- Kotlin language basics
- Cross-platform development concepts

### Related
- Compose Multiplatform for shared UI (when available)
- Platform-specific API integration patterns
- Mobile architecture patterns (MVVM, MVI, Clean Architecture)

### Advanced
- KMM architecture and best practices
- Cross-platform performance optimization
- Migration strategies from native to cross-platform

