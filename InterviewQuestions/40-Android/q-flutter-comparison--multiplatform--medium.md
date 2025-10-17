---
id: "20251015082237270"
title: "Flutter Comparison / Flutter Сравнение"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [Kotlin, Flutter, Multiplatform, Comparison, difficulty/medium]
---

# KMM vs Flutter - Trade-offs and Decision Making

# Question (EN)

> Compare Kotlin Multiplatform Mobile (KMM) with Flutter for cross-platform development. What are the architectural differences, performance characteristics, and trade-offs? When should you choose KMM over Flutter and vice versa?

## Answer (EN)

KMM and Flutter represent fundamentally different approaches to cross-platform development, each with distinct advantages, trade-offs, and ideal use cases that significantly impact development strategy and long-term maintenance.

#### Architectural Comparison

**1. Technology Stack**

**KMM Architecture**

```

         Platform-Specific UI
   Android: Compose/Views
   iOS: SwiftUI/UIKit

                ↓

      Shared Business Logic
   - Domain Layer (Use Cases)
   - Data Layer (Repositories)
   - Network Layer (Ktor)
   - Database (SQLDelight)
   Written in Kotlin

                ↓

      Platform-Specific APIs
   Android: Android SDK
   iOS: iOS SDK (via Kotlin/Native)

```

**Flutter Architecture**

```

         Flutter Framework
   - Widgets (UI Components)
   - Business Logic (Dart)
   - State Management
   Written in Dart

                ↓

         Flutter Engine
   - Skia Graphics Engine
   - Dart Runtime
   - Platform Channels

                ↓

      Platform-Specific APIs
   Android: Android Embedder
   iOS: iOS Embedder

```

**2. Code Sharing Comparison**

**KMM Project Structure**

```kotlin
// KMM - Shared business logic, platform-specific UI

// shared/commonMain - Business Logic (60-80% shared)
class TaskRepository(
    private val api: TaskApi,
    private val database: TaskDatabase
) {
    suspend fun getTasks(): Result<List<Task>> {
        // Shared across Android & iOS
        return try {
            val remoteTasks = api.fetchTasks()
            database.saveTasks(remoteTasks)
            Result.success(remoteTasks)
        } catch (e: Exception) {
            val localTasks = database.getTasks()
            if (localTasks.isNotEmpty()) {
                Result.success(localTasks)
            } else {
                Result.failure(e)
            }
        }
    }
}

// Android - Platform-specific UI
@Composable
fun TaskListScreen(viewModel: TaskViewModel) {
    val tasks by viewModel.tasks.collectAsState()

    LazyColumn {
        items(tasks) { task ->
            TaskItem(task)  // Material Design
        }
    }
}

// iOS - Platform-specific UI
struct TaskListView: View {
    @StateObject var viewModel: TaskViewModel

    var body: some View {
        List(viewModel.tasks) { task in
            TaskRow(task: task)  // iOS native design
        }
    }
}
```

**Flutter Project Structure**

```dart
// Flutter - Shared UI and business logic (90-95% shared)

// Shared across Android & iOS
class TaskRepository {
  final TaskApi api;
  final TaskDatabase database;

  Future<Result<List<Task>>> getTasks() async {
    try {
      final remoteTasks = await api.fetchTasks();
      await database.saveTasks(remoteTasks);
      return Success(remoteTasks);
    } catch (e) {
      final localTasks = await database.getTasks();
      if (localTasks.isNotEmpty) {
        return Success(localTasks);
      }
      return Failure(e);
    }
  }
}

// Shared UI for Android & iOS
class TaskListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<TaskViewModel>(
      builder: (context, viewModel, child) {
        return ListView.builder(
          itemCount: viewModel.tasks.length,
          itemBuilder: (context, index) {
            return TaskItem(task: viewModel.tasks[index]);
            // Same UI on Android & iOS
          },
        );
      },
    );
  }
}
```

#### Performance Comparison

**1. Startup Time**

```kotlin
// KMM - Native startup
// Android: 300-500ms (typical)
// iOS: 200-400ms (typical)
// Pros: Fast, native performance
// Cons: Separate implementations

// Flutter - Dart VM initialization
// Android: 500-800ms (typical)
// iOS: 400-700ms (typical)
// Pros: Consistent across platforms
// Cons: Extra overhead from Dart VM
```

**2. Runtime Performance**

**KMM Performance Profile**

```kotlin
// Direct native performance
class ImageProcessor {
    // Compiles to native code on each platform
    fun processImage(bitmap: Bitmap): Bitmap {
        // Android: Uses Android SDK directly
        // iOS: Uses Core Image directly
        // No bridge overhead
        return nativeImageProcessing(bitmap)
    }
}

// Performance metrics:
// - UI: Native (60fps easily)
// - Compute: Native speed
// - Memory: Native memory management
// - Graphics: Platform native (Metal/Vulkan)
```

**Flutter Performance Profile**

```dart
// Compiled to native ARM code (AOT)
class ImageProcessor {
  // Dart code compiled to ARM assembly
  Future<ui.Image> processImage(ui.Image image) async {
    // Uses Skia engine for rendering
    // Bridge required for platform-specific APIs
    return await compute(_processImageIsolate, image);
  }
}

// Performance metrics:
// - UI: 60fps (120fps capable)
// - Compute: Near-native (AOT compilation)
// - Memory: Dart GC (some overhead)
// - Graphics: Skia rendering engine
```

**3. Benchmark Comparison**

```kotlin
// Real-world performance comparison

// Scenario: Process 1000 JSON objects
// KMM (Kotlin/Native): ~85ms
// Flutter (Dart): ~95ms
// Difference: Negligible

// Scenario: Complex UI animations (60fps)
// KMM (Native): 16.67ms/frame (100% native)
// Flutter (Skia): 16.67ms/frame (95%+ native)
// Difference: Imperceptible

// Scenario: App size (release)
// KMM (APK): 15-25MB (uses platform SDKs)
// Flutter (APK): 20-35MB (includes Flutter engine ~10MB)

// Scenario: Memory usage
// KMM: Lower (native memory management)
// Flutter: Higher (Dart VM + Skia engine)
```

#### Development Experience

**1. Team Structure**

**KMM Team**

```kotlin
// Requires mixed skillset

Team Composition:
 Kotlin Developers (Shared logic) - 2-3 devs
 Android Developers (Android UI) - 2-3 devs
 iOS Developers (iOS UI) - 2-3 devs
 Total: 6-9 developers

Skills Required:
- Kotlin (mandatory for shared code)
- Android SDK & Jetpack Compose
- Swift/SwiftUI & iOS SDK
- Platform-specific knowledge

Pros:
 Native expertise for each platform
 Best-in-class platform experiences
 Access to latest platform features immediately

Cons:
 Need developers skilled in multiple platforms
 Coordination overhead between teams
 UI implementation duplicated
```

**Flutter Team**

```dart
// Single skillset team

Team Composition:
 Flutter Developers - 3-5 devs
 Total: 3-5 developers

Skills Required:
- Dart language
- Flutter framework
- Basic platform knowledge (for plugins)

Pros:
 Smaller team size
 Single codebase for UI
 Faster feature development
 Consistent UI across platforms

Cons:
 Less native platform expertise
 May compromise on platform conventions
 Dependency on Flutter community for platform features
```

**2. Development Velocity**

**KMM Development Cycle**

```kotlin
// Feature: User Profile Screen

Timeline:
Day 1-2: Shared business logic
  - ProfileRepository (shared)
  - ProfileUseCase (shared)
  - Profile models (shared)

Day 3-5: Android implementation
  - ProfileViewModel (Android)
  - ProfileScreen (Compose)
  - Platform-specific UI components

Day 6-8: iOS implementation
  - ProfileViewModel (iOS wrapper)
  - ProfileView (SwiftUI)
  - Platform-specific UI components

Total: 8 days
Code reuse: 60-70%
```

**Flutter Development Cycle**

```dart
// Feature: User Profile Screen

Timeline:
Day 1-2: Business logic
  - ProfileRepository (shared)
  - ProfileViewModel (shared)
  - Profile models (shared)

Day 3-4: UI implementation
  - ProfileScreen (shared)
  - UI widgets (shared)
  - Platform adaptations (minimal)

Total: 4 days
Code reuse: 90-95%
```

#### Platform Integration

**1. Native API Access**

**KMM - Direct Platform Access**

```kotlin
// Android - Direct Android SDK access
class LocationManager(private val context: Context) {
    private val fusedLocationClient = LocationServices
        .getFusedLocationProviderClient(context)

    suspend fun getCurrentLocation(): Location? {
        // Direct access to Android APIs
        return fusedLocationClient.lastLocation.await()
    }
}

// iOS - Direct iOS SDK access via Kotlin/Native
actual class LocationManager {
    actual suspend fun getCurrentLocation(): Location? {
        // Direct access to Core Location
        val locationManager = CLLocationManager()
        locationManager.requestWhenInUseAuthorization()

        return withContext(Dispatchers.Main) {
            suspendCoroutine { continuation ->
                locationManager.requestLocation()
                // Direct CoreLocation API
            }
        }
    }
}

// Pros:
//  Zero overhead
//  Immediate access to new platform features
//  Full control over implementation
//  Type-safe platform APIs

// Cons:
//  Need to implement twice
//  Requires platform expertise
```

**Flutter - Platform Channels**

```dart
// Flutter - Platform channel bridge

// Dart side
class LocationManager {
  static const platform = MethodChannel('com.app/location');

  Future<Map<String, double>?> getCurrentLocation() async {
    try {
      // Goes through platform channel
      final result = await platform.invokeMethod('getLocation');
      return Map<String, double>.from(result);
    } catch (e) {
      return null;
    }
  }
}

// Android side - Platform-specific implementation
class LocationPlugin : FlutterPlugin, MethodCallHandler {
  override fun onMethodCall(call: MethodCall, result: Result) {
    when (call.method) {
      "getLocation" -> {
        // Android implementation
        val location = getLocation()
        result.success(mapOf("lat" to location.latitude))
      }
    }
  }
}

// iOS side - Platform-specific implementation
class LocationPlugin: NSObject, FlutterPlugin {
  func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    if call.method == "getLocation" {
      // iOS implementation
      let location = getLocation()
      result(["lat": location.coordinate.latitude])
    }
  }
}

// Pros:
//  Consistent API from Dart
//  Single implementation for most features

// Cons:
//  Serialization overhead
//  Delayed access to new platform features
//  Type safety lost across bridge
//  Need platform channels for native features
```

**2. Third-Party Libraries**

**KMM Ecosystem**

```kotlin
// Native libraries work directly
dependencies {
    // Android
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("androidx.camera:camera-core:1.3.1")

    // iOS (Cocoapods)
    // pod 'Alamofire'
    // pod 'SDWebImage'

    // Multiplatform
    implementation("io.ktor:ktor-client:2.3.7")
    implementation("com.squareup.sqldelight:runtime:2.0.0")
}

// Pros:
//  Access to entire Android/iOS ecosystems
//  No wrapper needed for platform libraries
//  Use best-of-breed libraries per platform

// Cons:
//  May need separate libraries per platform
//  Different APIs to learn
```

**Flutter Ecosystem**

```dart
// Flutter pub packages
dependencies:
  http: ^1.1.0
  sqflite: ^2.3.0
  camera: ^0.10.5
  image_picker: ^1.0.5

  # Many packages are cross-platform
  # Single API for both platforms

// Pros:
//  Large pub.dev ecosystem (40,000+ packages)
//  Single package for both platforms
//  Consistent APIs

// Cons:
//  Some native libraries not available
//  Quality varies across packages
//  May lag behind platform features
```

#### Use Case Decision Matrix

**Choose KMM When:**

1. **Native Experience is Critical**

```kotlin
// Banking app, health apps, productivity tools
// Example: Banking App

Priorities:
- Platform-native UI/UX (Material You, iOS HIG)
- Access to latest platform features (Wallet, HealthKit)
- Maximum security (platform-provided)
- Integration with platform services

KMM Advantage:
 True native UI
 Immediate platform API access
 Platform security features
 Familiar to platform users
```

2. **Existing Native Apps**

```kotlin
// Gradual migration scenario
// Example: Large existing Android app

Current State:
- 200k+ lines of Android code
- Established user base
- Native UI expectations

Migration Strategy:
1. Extract business logic to KMM
2. Keep existing Android UI
3. Add iOS app sharing logic
4. Gradual, low-risk migration

KMM Advantage:
 Incremental adoption
 Keep existing Android code
 Share only business logic
 No UI rewrite needed
```

3. **Performance-Critical Apps**

```kotlin
// Games, media processing, AR/VR
// Example: Photo Editing App

Requirements:
- Complex image processing
- Real-time filters
- Hardware acceleration
- Minimal latency

KMM Advantage:
 Direct Metal/Vulkan access
 Zero bridge overhead
 Platform-optimized algorithms
 Native memory management
```

**Choose Flutter When:**

1. **Rapid MVP Development**

```dart
// Startups, prototypes, MVPs
// Example: Social Media Startup

Priorities:
- Fast time-to-market
- Consistent UI across platforms
- Small team
- Limited budget

Flutter Advantage:
 Single codebase for UI
 Hot reload for fast iteration
 Rich widget library
 Smaller team needed
```

2. **Consistent Brand Experience**

```dart
// Custom-designed apps
// Example: Retail/E-commerce App

Requirements:
- Unique brand identity
- Consistent look across platforms
- Custom animations
- Designer-driven UI

Flutter Advantage:
 Pixel-perfect custom UI
 Same UI on all platforms
 Advanced animation system
 No platform UI constraints
```

3. **Multi-Platform Beyond Mobile**

```dart
// Web, Desktop, Mobile
// Example: Productivity Suite

Target Platforms:
- Android, iOS
- Web
- Windows, Mac, Linux

Flutter Advantage:
 Single codebase for 6+ platforms
 Consistent experience everywhere
 Web support out of box
 Desktop support stable
```

#### Migration Scenarios

**1. Migrating from Native to KMM**

```kotlin
// Incremental adoption path

Phase 1: Extract data layer
shared/
   data/
       repository/
       network/
       database/

Phase 2: Extract domain layer
shared/
   domain/
       model/
       usecase/

Phase 3: Share ViewModels (optional)
shared/
   presentation/
       viewmodel/

Keep Native:
- UI components
- Navigation
- Platform integrations

Time: 3-6 months for gradual migration
Risk: Low (native UI unchanged)
Code Reuse: 60-70%
```

**2. Migrating from Native to Flutter**

```dart
// Big bang approach (typically)

Phase 1: Rewrite in Flutter
- Complete UI rewrite
- Business logic rewrite
- Platform integration via channels

Keep Native:
- Complex platform features (via plugins)
- Performance-critical code

Time: 6-12 months for complete rewrite
Risk: High (everything changes)
Code Reuse: 90-95%
```

#### Best Practices Comparison

**KMM Best Practices**

```kotlin
// 1. Minimize expect/actual declarations
// 2. Keep shared layer thin
// 3. Platform-specific UI is okay
// 4. Use Koin for DI
// 5. Test shared logic thoroughly

// Example: Clean separation
commonMain/
   domain/  // Pure business logic
androidMain/
   ui/      // Android-specific UI
iosMain/
   ui/      // iOS-specific UI
```

**Flutter Best Practices**

```dart
// 1. Use platform-adaptive widgets
// 2. Leverage existing packages
// 3. Platform-specific code in plugins
// 4. State management (Riverpod/Bloc)
// 5. Golden tests for UI

// Example: Platform adaptation
Widget buildButton() {
  if (Platform.isIOS) {
    return CupertinoButton(...);
  }
  return ElevatedButton(...);
}
```

#### Cost Analysis

**Development Cost**

```
KMM:
- Initial: Higher (2 UI implementations)
- Maintenance: Medium (separate UIs)
- Team: Larger (native expertise)
- Timeline: Longer for MVP

Flutter:
- Initial: Lower (single UI)
- Maintenance: Lower (one codebase)
- Team: Smaller (Flutter devs)
- Timeline: Faster for MVP
```

**Long-Term TCO**

```
KMM:
- Platform updates: Immediate
- Native features: Free
- Performance: Best
- Future-proof: Very (native)

Flutter:
- Platform updates: Depends on Flutter
- Native features: Wait for plugins
- Performance: Excellent
- Future-proof: Good (Google-backed)
```

### Summary

**KMM Strengths:**

-   True native UI/UX
-   Direct platform API access
-   Best performance
-   Incremental adoption
-   Familiar to native developers

**KMM Weaknesses:**

-   Duplicate UI code
-   Requires platform expertise
-   Slower initial development
-   Larger team needed

**Flutter Strengths:**

-   Maximum code reuse (90-95%)
-   Faster development
-   Consistent UI
-   Smaller team
-   Hot reload

**Flutter Weaknesses:**

-   Custom UI (not platform-native)
-   Platform channel overhead
-   Delayed platform features
-   Larger app size

**Decision Framework:**

-   Native UX critical? → KMM
-   Rapid MVP? → Flutter
-   Existing native app? → KMM
-   Multi-platform (Web/Desktop)? → Flutter
-   Performance-critical? → KMM
-   Small team? → Flutter

---

# Вопрос (RU)

> Сравните Kotlin Multiplatform Mobile (KMM) с Flutter для кросс-платформенной разработки. Каковы архитектурные различия, характеристики производительности и trade-offs? Когда выбирать KMM вместо Flutter и наоборот?

## Ответ (RU)

KMM и Flutter представляют фундаментально разные подходы к кросс-платформенной разработке, каждый с уникальными преимуществами, компромиссами и идеальными use cases.

#### Архитектурное сравнение

**KMM**:

-   Shared: Бизнес-логика (60-80%)
-   Platform-specific: UI (20-40%)
-   Технология: Kotlin для shared, native UI

**Flutter**:

-   Shared: UI + логика (90-95%)
-   Platform-specific: Минимум (5-10%)
-   Технология: Dart для всего, Skia для рендеринга

#### Производительность

**Startup Time**:

-   KMM: Быстрее (native)
-   Flutter: Медленнее (Dart VM init)

**Runtime Performance**:

-   KMM: 100% native
-   Flutter: 95-98% native (AOT компиляция)

**App Size**:

-   KMM: Меньше (использует platform SDKs)
-   Flutter: Больше (включает Flutter engine ~10MB)

**Memory**:

-   KMM: Ниже (native управление)
-   Flutter: Выше (Dart VM + Skia)

#### Development Experience

**Team Size**:

-   KMM: Больше (6-9 разработчиков)
    -   Kotlin devs
    -   Android devs
    -   iOS devs
-   Flutter: Меньше (3-5 разработчиков)
    -   Flutter devs

**Development Speed**:

-   KMM: Медленнее (duplicate UI)
-   Flutter: Быстрее (shared UI)

**Code Reuse**:

-   KMM: 60-70%
-   Flutter: 90-95%

#### Platform Integration

**KMM**:

-   Прямой доступ к native APIs
-   Zero overhead
-   Мгновенный доступ к новым features
-   Нужно реализовывать дважды

**Flutter**:

-   Единый API из Dart
-   Consistent interface
-   Platform channel overhead
-   Задержка с новыми platform features

#### Use Cases

**Выбирайте KMM когда**:

-   Native UX критичен
-   Существующее native приложение
-   Performance-critical app
-   Доступ к latest platform features
-   Команда с native expertise

**Выбирайте Flutter когда**:

-   Быстрый MVP
-   Consistent brand experience
-   Маленькая команда
-   Multi-platform (Web/Desktop)
-   Custom UI design

#### Cost Analysis

**KMM**:

-   Начальная стоимость: Выше
-   Maintenance: Средний
-   Timeline: Дольше
-   Команда: Больше

**Flutter**:

-   Начальная стоимость: Ниже
-   Maintenance: Ниже
-   Timeline: Быстрее
-   Команда: Меньше

### Резюме

**KMM = Native Experience + Code Sharing**

-   Лучший выбор для native UX, performance, existing apps

**Flutter = Maximum Code Reuse + Fast Development**

-   Лучший выбор для MVPs, consistent UI, small teams

---

## Follow-ups

-   How do you migrate an existing native Android app to KMM vs Flutter?
-   What are the performance implications of using KMM vs Flutter for CPU-intensive applications?
-   How do you handle platform-specific features and native integrations in both approaches?

## References

-   `https://kotlinlang.org/docs/multiplatform.html` — Kotlin Multiplatform Mobile
-   `https://flutter.dev/docs` — Flutter documentation
-   `https://developer.android.com/kotlin/multiplatform` — Android KMM guide

## Related Questions

### Related (Medium)

-   [[q-kmm-networking--multiplatform--medium]] - KMM networking
-   [[q-flutter-state-management--multiplatform--medium]] - Flutter state management
