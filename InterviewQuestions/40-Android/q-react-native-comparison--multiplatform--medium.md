---
id: 20251012-12271176
title: "React Native Comparison / React Native Сравнение"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-does-jetpackcompose-work--android--medium, q-play-app-signing--android--medium, q-privacy-sandbox-attribution--privacy--medium]
created: 2025-10-15
tags: [Kotlin, ReactNative, Multiplatform, JavaScript, difficulty/medium]
---
# KMM vs React Native - Technical Comparison

# Question (EN)
> 
Compare Kotlin Multiplatform Mobile with React Native. What are the architectural differences, bridge overhead, and ecosystem maturity? How do they differ in terms of JavaScript vs Kotlin/Native approach?

## Answer (EN)
KMM and React Native represent contrasting philosophies: native-first with shared logic (KMM) versus JavaScript-driven with native components (React Native), each offering distinct trade-offs in performance, developer experience, and platform integration.

#### Architectural Comparison

**React Native Architecture**
```

      JavaScript Layer (React)        
   - UI Components (JSX)              
   - Business Logic                   
   - State Management (Redux/MobX)   
   Running in JavaScriptCore/Hermes  

                ↓
       
          JS Bridge    ← Performance bottleneck
       
                ↓

      Native Modules                  
   Android: Java/Kotlin modules       
   iOS: Objective-C/Swift modules     

                ↓

      Platform SDKs                   
   Android SDK / iOS SDK              

```

**KMM Architecture** (Already covered, for comparison)
```

      Native UI Layer                 
   Android: Compose/Views             
   iOS: SwiftUI/UIKit                 
   No bridge - direct platform code   

                ↓

      Shared Kotlin Code              
   - Business Logic                   
   - Data Layer                       
   Compiles to native code            

```

#### Bridge Overhead Analysis

**React Native Bridge Performance**
```javascript
// React Native - Data crossing JS bridge

// JavaScript side
const processLargeDataset = async () => {
  const startTime = performance.now();

  // Data serialization to JSON
  const data = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`,
    value: Math.random() * 100
  }));

  // Cross bridge - serialization overhead
  const result = await NativeModules.DataProcessor
    .processData(JSON.stringify(data));  // ← Serialize

  // Cross bridge back - deserialization
  const parsed = JSON.parse(result);  // ← Deserialize

  const endTime = performance.now();
  console.log(`Time: ${endTime - startTime}ms`);
  // Typical: 50-150ms overhead for bridge crossing
};

// Native Android module
class DataProcessorModule(reactContext: ReactApplicationContext) :
    ReactContextBaseJavaModule(reactContext) {

    @ReactMethod
    fun processData(jsonData: String, promise: Promise) {
        try {
            // Deserialize from JSON
            val data = Gson().fromJson(jsonData, Array<Item>::class.java)

            // Process data
            val result = data.map { it.copy(value = it.value * 2) }

            // Serialize back to JSON
            val resultJson = Gson().toJson(result)

            promise.resolve(resultJson)
        } catch (e: Exception) {
            promise.reject("ERROR", e.message)
        }
    }
}

// Performance impact:
// - JSON serialization: 20-50ms
// - Bridge crossing: 10-30ms
// - JSON deserialization: 20-50ms
// Total overhead: 50-130ms
```

**KMM No-Bridge Performance**
```kotlin
// KMM - No bridge, direct native code

// Shared code - compiles to native
class DataProcessor {
    fun processLargeDataset(): List<Item> {
        val data = List(10000) { i ->
            Item(
                id = i,
                name = "Item $i",
                value = Random.nextDouble() * 100
            )
        }

        // Direct native processing - no serialization
        return data.map { it.copy(value = it.value * 2) }
    }
}

// Android usage - direct call
val processor = DataProcessor()
val result = processor.processLargeDataset()
// No bridge overhead: 5-15ms

// iOS usage - direct call
let processor = DataProcessor()
let result = processor.processLargeDataset()
// No bridge overhead: 5-15ms

// Performance advantage:
// KMM: 5-15ms (10x faster)
// React Native: 50-130ms (bridge overhead)
```

#### Type Safety Comparison

**React Native Type Safety**
```javascript
// React Native with TypeScript

// Type definitions (not enforced at runtime)
interface Task {
  id: string;
  title: string;
  completed: boolean;
}

// Native module interface (type safety lost here)
interface NativeTaskModule {
  getTasks(): Promise<string>;  // Returns JSON string
  createTask(taskJson: string): Promise<string>;
}

// Usage
const taskModule = NativeModules.TaskModule as NativeTaskModule;

const getTasks = async (): Promise<Task[]> => {
  const jsonResult = await taskModule.getTasks();

  // Manual parsing required
  // Type safety lost across bridge
  const tasks: Task[] = JSON.parse(jsonResult);

  // Runtime errors possible if structure doesn't match
  return tasks;
};

// Problems:
//  No compile-time type checking across bridge
//  Manual JSON parsing/serialization
//  Runtime type errors
//  Refactoring nightmare
```

**KMM Type Safety**
```kotlin
// KMM - Full type safety

// Shared model
@Serializable
data class Task(
    val id: String,
    val title: String,
    val completed: Boolean
)

// Shared repository
class TaskRepository {
    suspend fun getTasks(): List<Task> {
        // Return strongly-typed objects
        return api.fetchTasks()
    }

    suspend fun createTask(task: Task): Task {
        // Accept strongly-typed objects
        return api.createTask(task)
    }
}

// Android usage - compile-time type safety
val repository = TaskRepository()
val tasks: List<Task> = repository.getTasks()
tasks.forEach { task: Task ->
    println(task.title)  // Autocomplete works
}

// iOS usage - compile-time type safety
let repository = TaskRepository()
let tasks: [Task] = repository.getTasks()
tasks.forEach { (task: Task) in
    print(task.title)  // Autocomplete works
}

// Benefits:
//  Compile-time type checking
//  No manual parsing
//  Safe refactoring
//  IDE autocomplete everywhere
```

#### UI Development Comparison

**React Native UI**
```javascript
// React Native - JavaScript-driven UI

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator
} from 'react-native';

const TaskListScreen = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    setLoading(true);
    // Bridge call to native
    const result = await NativeModules.TaskModule.getTasks();
    setTasks(JSON.parse(result));
    setLoading(false);
  };

  const toggleTask = async (taskId) => {
    // Bridge call to native
    await NativeModules.TaskModule.toggleTask(taskId);
    loadTasks();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <FlatList
      data={tasks}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.taskItem}
          onPress={() => toggleTask(item.id)}
        >
          <Text style={styles.taskTitle}>{item.title}</Text>
          <Text>{item.completed ? '' : ''}</Text>
        </TouchableOpacity>
      )}
    />
  );
};

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  taskItem: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd'
  },
  taskTitle: {
    flex: 1,
    fontSize: 16
  }
});

// Characteristics:
// - Single UI codebase (95% shared)
// - Bridge calls for data
// - Not fully native (emulated components)
// - Hot reload for fast development
```

**KMM UI**
```kotlin
// Android - Jetpack Compose (Native)
@Composable
fun TaskListScreen(viewModel: TaskViewModel = hiltViewModel()) {
    val tasks by viewModel.tasks.collectAsState()
    val loading by viewModel.loading.collectAsState()

    if (loading) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
    } else {
        LazyColumn {
            items(tasks, key = { it.id }) { task ->
                TaskItem(
                    task = task,
                    onClick = { viewModel.toggleTask(task.id) }
                )
            }
        }
    }
}

@Composable
fun TaskItem(task: Task, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = task.title,
            style = MaterialTheme.typography.bodyLarge
        )
        Text(text = if (task.completed) "" else "")
    }
}

// iOS - SwiftUI (Native)
struct TaskListView: View {
    @StateObject var viewModel: TaskViewModel

    var body: some View {
        if viewModel.loading {
            ProgressView()
        } else {
            List(viewModel.tasks) { task in
                TaskRow(task: task) {
                    viewModel.toggleTask(id: task.id)
                }
            }
            .listStyle(.plain)
        }
    }
}

struct TaskRow: View {
    let task: Task
    let onTap: () -> Void

    var body: some View {
        HStack {
            Text(task.title)
                .font(.body)
            Spacer()
            Text(task.completed ? "" : "")
        }
        .padding()
        .onTapGesture(perform: onTap)
    }
}

// Characteristics:
// - Platform-native UI (separate implementations)
// - No bridge calls (direct data access)
// - 100% native components
// - Platform-specific development
```

#### Performance Benchmarks

**Real-World Scenarios**

**1. List Rendering Performance**
```javascript
// Scenario: Render 1000-item list

React Native:
- Initial render: 300-500ms
- Scroll performance: 50-58fps (occasional jank)
- Memory usage: ~80MB
- Bridge calls for data: 50-100ms overhead

KMM:
- Android initial render: 150-250ms
- iOS initial render: 120-200ms
- Scroll performance: 60fps (buttery smooth)
- Memory usage: ~50MB
- No bridge overhead: 0ms
```

**2. Complex Animations**
```javascript
// Scenario: Animated transitions with gestures

React Native:
- Animation FPS: 45-58fps (JS thread bottleneck)
- Gesture lag: 16-50ms
- Reanimated 2 required for smooth animations
- CPU usage: 25-40%

KMM:
- Android FPS: 60fps (120Hz on supported devices)
- iOS FPS: 60fps (120Hz ProMotion)
- Gesture lag: <5ms
- CPU usage: 15-25%
```

**3. Startup Time**
```javascript
// Cold start to interactive

React Native:
- Android: 1.5-2.5s
  - JS bundle load: 500-800ms
  - JS execution: 400-700ms
  - Bridge initialization: 300-500ms
- iOS: 1.2-2.0s

KMM:
- Android: 500-800ms (native)
- iOS: 400-600ms (native)

Advantage: KMM 2-3x faster startup
```

#### Developer Experience

**React Native DX**
```javascript
// Pros:
//  Hot reload (instant UI updates)
//  Large JavaScript ecosystem (npm)
//  React knowledge transferable
//  Chrome DevTools debugging
//  Widely adopted (mature)

// Cons:
//  Bridge debugging complexity
//  Native module development required
//  Type safety issues across bridge
//  "JS fatigue" (package churn)
//  Upgrading can break apps

// Example: Hot reload
// Save file → Instant UI update (1-2s)
// No app rebuild needed
```

**KMM DX**
```kotlin
// Pros:
//  Type-safe across platforms
//  Native IDE support (Android Studio, Xcode)
//  No bridge complexity
//  Kotlin language features (coroutines, null safety)
//  Gradual adoption possible

// Cons:
//  Slower build times (native compilation)
//  Separate UI implementations
//  Smaller ecosystem (growing)
//  Need iOS/Android expertise
//  More complex project setup

// Example: Code change
// Save file → Full rebuild (30-60s Android, 40-80s iOS)
// Slower iteration than React Native
```

#### Ecosystem Maturity

**React Native Ecosystem**
```javascript
// npm packages: 2,000,000+
// React Native specific: 15,000+

Popular packages:
- react-navigation: 20k+ stars
- react-native-vector-icons: 17k+ stars
- react-native-firebase: 11k+ stars
- react-native-camera: 10k+ stars

Community size: Very large
- GitHub stars: 114k+
- Weekly npm downloads: 800k+
- Job market: Abundant

Maturity: Very mature (2015, 9+ years)
Corporate backing: Meta (Facebook)
```

**KMM Ecosystem**
```kotlin
// Multiplatform libraries: 500+

Popular libraries:
- Ktor: HTTP client (11k+ stars)
- SQLDelight: Database (5.5k+ stars)
- Koin: DI (8k+ stars)
- kotlinx.serialization: Official (4.5k+ stars)

Community size: Growing
- GitHub org stars: Kotlin 45k+
- Adoption: Early majority
- Job market: Growing

Maturity: Maturing (2020 stable, 4+ years)
Corporate backing: JetBrains + Google
```

#### Platform Feature Access

**React Native - Delayed Access**
```javascript
// New iOS feature announced (e.g., iOS 17 widgets)

Timeline:
Week 0: Apple releases iOS 17
Week 4-8: Community creates native module
Week 12-16: Module stabilizes
Week 20+: Production ready

// During this time, you cannot use the feature
// Must wait for community or build yourself

Example: iOS 16 Live Activities
- iOS 16 released: Sept 2022
- React Native support: Jan 2023 (4 months later)
```

**KMM - Immediate Access**
```kotlin
// New iOS feature announced

Timeline:
Week 0: Apple releases iOS 17
Week 0: Write Kotlin/Native code using new API

// iosMain/SwiftInterop.kt
actual fun createLiveActivity() {
    // Direct access to new iOS APIs
    val activity = ActivityKt.request(
        attributes = WidgetAttributes(),
        content = ActivityContent()
    )
}

// Advantage: Day-zero access to platform features
```

#### Migration Paths

**React Native → KMM**
```kotlin
// Challenging migration (complete rewrite)

Step 1: Rewrite UI
- React → Jetpack Compose (Android)
- React → SwiftUI (iOS)

Step 2: Rewrite business logic
- JavaScript → Kotlin

Step 3: Rewrite native modules
- Bridge modules → Shared Kotlin code

Effort: High (6-12 months)
Risk: High (complete rewrite)
Benefits: Better performance, type safety
```

**Native → KMM**
```kotlin
// Incremental migration (low risk)

Step 1: Extract business logic to KMM
- Keep existing UI
- Share repositories, use cases

Step 2: Gradually expand shared code
- Add new features in shared code
- Refactor old code when needed

Effort: Medium (3-6 months)
Risk: Low (incremental)
Benefits: Immediate code sharing
```

**Native → React Native**
```javascript
// Partial migration possible

Step 1: Integrate React Native
- Add React Native to existing app
- Create new screens in React Native

Step 2: Gradually move screens
- Migrate screen by screen
- Bridge to native when needed

Effort: Medium (4-8 months)
Risk: Medium (mixed stack)
Benefits: Faster new feature development
```

#### When to Choose Each

**Choose React Native:**
```javascript
 Team expertise in JavaScript/React
 Need very fast prototyping/MVPs
 Hot reload essential for productivity
 Web version planned (React Native Web)
 Consistent UI across platforms acceptable
 Large JavaScript ecosystem valuable
 Mature solution needed today

 Performance-critical application
 Need latest platform features immediately
 Type safety critical
 Complex native integrations
```

**Choose KMM:**
```kotlin
 Team expertise in Kotlin/Native
 Native UI/UX critical
 Performance critical (animations, media)
 Type safety important
 Existing Android app to expand to iOS
 Want gradual adoption
 Need immediate platform feature access

 Very small team (<3 devs)
 Need fastest possible MVP
 JavaScript/React expertise only
 Consistent UI across platforms required
```

#### Real-World Examples

**React Native Success Stories:**
- Facebook, Instagram (Meta apps)
- Discord, Shopify, Uber Eats
- Bloomberg, Walmart

**KMM Adoption:**
- Netflix (Android SDK)
- VMware, Philips
- Cash App (Square)
- 9GAG, Autodesk

### Summary

**React Native:**
- **Approach:** JavaScript-driven with native bridge
- **Code Reuse:** 90-95% (including UI)
- **Performance:** Good (bridge overhead exists)
- **Type Safety:** Limited across bridge
- **Maturity:** Very mature (9+ years)
- **Best For:** Fast MVPs, React teams, consistent UI

**KMM:**
- **Approach:** Native-first with shared logic
- **Code Reuse:** 60-70% (business logic only)
- **Performance:** Excellent (no bridge)
- **Type Safety:** Full compile-time safety
- **Maturity:** Maturing (4+ years stable)
- **Best For:** Native UX, performance, existing native apps

**Key Difference:** React Native maximizes code sharing (including UI) with acceptable performance, while KMM prioritizes native experience and performance by sharing only business logic.

---

# Вопрос (RU)
> 
Сравните Kotlin Multiplatform Mobile с React Native. Каковы архитектурные различия, overhead от bridge и зрелость экосистемы? Чем отличается JavaScript vs Kotlin/Native подход?

## Ответ (RU)
KMM и React Native представляют контрастные философии: native-first с shared логикой (KMM) versus JavaScript-driven с native компонентами (React Native).

#### Bridge Overhead

**React Native**:
- Все данные через JS Bridge
- JSON serialization/deserialization
- Overhead: 50-130ms на операцию
- Bottleneck для performance-critical кода

**KMM**:
- Нет bridge
- Прямой native код
- Zero overhead
- Native performance

#### Type Safety

**React Native**:
- TypeScript в JS layer
- Потеря type safety на bridge
- Manual parsing/serialization
- Runtime errors

**KMM**:
- Full compile-time type safety
- End-to-end type checking
- No manual parsing
- Refactoring безопасен

#### Development Experience

**React Native**:
-  Hot reload (instant)
-  Large ecosystem (npm)
-  React knowledge
-  Bridge complexity
-  Native module development

**KMM**:
-  Type-safe
-  Native IDEs
-  No bridge
-  Slower builds
-  Separate UI implementations

#### Performance

**Startup Time**:
- React Native: 1.5-2.5s (JS bundle load)
- KMM: 0.5-0.8s (native)

**Runtime**:
- React Native: 45-58fps (JS thread)
- KMM: 60fps+ (native)

**Memory**:
- React Native: Выше (JS VM)
- KMM: Ниже (native)

#### Ecosystem

**React Native**:
- 9+ лет зрелости
- 15,000+ специфичных пакетов
- Очень большое комьюнити
- Meta (Facebook) backing

**KMM**:
- 4+ года stable
- 500+ multiplatform библиотек
- Растущее комьюнити
- JetBrains + Google backing

#### Platform Features

**React Native**:
- Задержка 4-16 недель
- Ждать community modules
- Или писать native modules

**KMM**:
- Day-zero доступ
- Прямой доступ к native APIs
- Kotlin/Native interop

#### Use Cases

**Выбирайте React Native**:
- JavaScript/React expertise
- Очень быстрый MVP
- Hot reload critical
- Web version planned
- Consistent UI acceptable

**Выбирайте KMM**:
- Kotlin/Native expertise
- Native UX critical
- Performance critical
- Type safety important
- Existing Android app
- Gradual adoption

### Резюме

**React Native = Maximum Code Reuse + Fast Development**
- 90-95% code sharing (including UI)
- Bridge overhead существует
- JavaScript ecosystem
- Mature solution

**KMM = Native Performance + Type Safety**
- 60-70% code sharing (logic only)
- No bridge, native performance
- Kotlin ecosystem
- Maturing solution

Выбор: React Native для скорости разработки, KMM для native experience и производительности.

## Related Questions

- [[q-how-does-jetpackcompose-work--android--medium]]
- [[q-play-app-signing--android--medium]]
- [[q-privacy-sandbox-attribution--privacy--medium]]
