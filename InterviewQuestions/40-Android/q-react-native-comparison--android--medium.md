---
id: android-169
title: "KMM vs React Native / KMM против React Native"
aliases: ["KMM vs React Native", "KMM против React Native", "React Native Comparison", "React Native Сравнение"]
topic: android
subtopics: [kmp, architecture-mvvm]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-how-does-jetpackcompose-work--android--medium, q-play-app-signing--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [kotlin, reactnative, multiplatform, javascript, kmp, android/kmp, android/architecture-mvvm, difficulty/medium]
---
# Вопрос (RU)
>
Сравните Kotlin Multiplatform Mobile с React Native. Каковы архитектурные различия, bridge overhead и зрелость экосистемы? Чем отличается JavaScript vs Kotlin/Native подход?

# Question (EN)
>
Compare Kotlin Multiplatform Mobile with React Native. What are the architectural differences, bridge overhead, and ecosystem maturity? How do they differ in terms of JavaScript vs Kotlin/Native approach?

## Ответ (RU)

### Архитектурные различия

**React Native**: JavaScript-слой → JS Bridge → Native модули → Platform SDK
- UI в JSX, логика в JavaScript
- Все данные через bridge (serialization/deserialization)
- JavaScriptCore/Hermes runtime

**KMM**: Native UI → Shared Kotlin → Platform SDK
- UI native (Compose/SwiftUI)
- Логика в Kotlin, компилируется в native код
- Нет bridge, прямой доступ

### Bridge Overhead

**React Native**:
```javascript
// ❌ Bridge overhead: JSON serialization + crossing + deserialization
const result = await NativeModules.DataProcessor
  .processData(JSON.stringify(data));  // 50-130ms overhead
const parsed = JSON.parse(result);
```

**KMM**:
```kotlin
// ✅ Direct native call, zero overhead
class DataProcessor {
    fun processData(): List<Item> = /* ... */  // 5-15ms
}
val result = DataProcessor().processData()  // No serialization
```

**Performance**: KMM 10x faster for data-intensive operations.

### Type Safety

**React Native**:
```javascript
// ❌ Type safety lost across bridge
const jsonResult = await taskModule.getTasks();  // Returns string
const tasks: Task[] = JSON.parse(jsonResult);    // Runtime parsing
// Risk: runtime errors if structure changes
```

**KMM**:
```kotlin
// ✅ Full compile-time type safety
@Serializable
data class Task(val id: String, val title: String)

class TaskRepository {
    suspend fun getTasks(): List<Task> = api.fetchTasks()
}
// Refactoring safe, IDE autocomplete, no manual parsing
```

### Code Sharing

**React Native**: 90-95% code reuse (including UI)
- Single JSX UI for both platforms
- Hot reload for fast iteration
- Requires bridge calls for data

**KMM**: 60-70% code reuse (business logic only)
- Separate native UI (Compose/SwiftUI)
- Direct access to shared code
- Platform-specific UI development

### Performance Benchmarks

| Metric | React Native | KMM |
|--------|--------------|-----|
| **Startup** | 1.5-2.5s (JS bundle load) | 0.5-0.8s (native) |
| **Animations** | 45-58fps (JS bottleneck) | 60fps+ (native) |
| **Memory** | Higher (JS VM overhead) | Lower (native) |
| **List Rendering** | 300-500ms, occasional jank | 150-250ms, smooth 60fps |

### Developer Experience

**React Native**:
- ✅ Hot reload (instant updates)
- ✅ Large JavaScript ecosystem (npm)
- ✅ React knowledge transferable
- ❌ Bridge debugging complexity
- ❌ Type safety lost across bridge

**KMM**:
- ✅ Full type safety
- ✅ No bridge complexity
- ✅ Gradual adoption (existing apps)
- ❌ Slower builds (30-80s)
- ❌ Separate UI implementations

### Ecosystem Maturity

**React Native**: Very mature (2015, Meta-backed)
- 15,000+ specific packages
- Large community, abundant jobs
- Popular: react-navigation, react-native-firebase

**KMM**: Maturing (stable since 2020, JetBrains/Google)
- 500+ multiplatform libraries
- Growing community and adoption
- Popular: Ktor, SQLDelight, Koin, kotlinx.serialization

### Platform Feature Access

**React Native**: 4-16 week delay waiting for community modules
**KMM**: Day-zero access via Kotlin/Native interop

### When to Choose

**React Native**: JavaScript/React team, fast MVP, hot reload critical, cross-platform UI acceptable
**KMM**: Kotlin expertise, native UX critical, performance/type-safety important, existing Android app

**Examples**: React Native (Meta, Discord, Shopify), KMM (Netflix SDK, Cash App, VMware)

## Answer (EN)

### Architectural Differences

**React Native**: JavaScript layer → JS Bridge → Native modules → Platform SDK
- UI in JSX, logic in JavaScript
- All data through bridge (serialization/deserialization)
- JavaScriptCore/Hermes runtime

**KMM**: Native UI → Shared Kotlin → Platform SDK
- Native UI (Compose/SwiftUI)
- Logic in Kotlin, compiles to native
- No bridge, direct access

### Bridge Overhead

**React Native**:
```javascript
// ❌ Bridge overhead: JSON serialization + crossing + deserialization
const result = await NativeModules.DataProcessor
  .processData(JSON.stringify(data));  // 50-130ms overhead
const parsed = JSON.parse(result);
```

**KMM**:
```kotlin
// ✅ Direct native call, zero overhead
class DataProcessor {
    fun processData(): List<Item> = /* ... */  // 5-15ms
}
val result = DataProcessor().processData()  // No serialization
```

**Performance**: KMM 10x faster for data-intensive operations.

### Type Safety

**React Native**:
```javascript
// ❌ Type safety lost across bridge
const jsonResult = await taskModule.getTasks();  // Returns string
const tasks: Task[] = JSON.parse(jsonResult);    // Runtime parsing
// Risk: runtime errors if structure changes
```

**KMM**:
```kotlin
// ✅ Full compile-time type safety
@Serializable
data class Task(val id: String, val title: String)

class TaskRepository {
    suspend fun getTasks(): List<Task> = api.fetchTasks()
}
// Refactoring safe, IDE autocomplete, no manual parsing
```

### Code Sharing

**React Native**: 90-95% code reuse (including UI)
- Single JSX UI for both platforms
- Hot reload for fast iteration
- Requires bridge calls for data

**KMM**: 60-70% code reuse (business logic only)
- Separate native UI (Compose/SwiftUI)
- Direct access to shared code
- Platform-specific UI development

### Performance Benchmarks

| Metric | React Native | KMM |
|--------|--------------|-----|
| **Startup** | 1.5-2.5s (JS bundle load) | 0.5-0.8s (native) |
| **Animations** | 45-58fps (JS bottleneck) | 60fps+ (native) |
| **Memory** | Higher (JS VM overhead) | Lower (native) |
| **List Rendering** | 300-500ms, occasional jank | 150-250ms, smooth 60fps |

### Developer Experience

**React Native**:
- ✅ Hot reload (instant updates)
- ✅ Large JavaScript ecosystem (npm)
- ✅ React knowledge transferable
- ❌ Bridge debugging complexity
- ❌ Type safety lost across bridge

**KMM**:
- ✅ Full type safety
- ✅ No bridge complexity
- ✅ Gradual adoption (existing apps)
- ❌ Slower builds (30-80s)
- ❌ Separate UI implementations

### Ecosystem Maturity

**React Native**: Very mature (2015, Meta-backed)
- 15,000+ specific packages
- Large community, abundant jobs
- Popular: react-navigation, react-native-firebase

**KMM**: Maturing (stable since 2020, JetBrains/Google)
- 500+ multiplatform libraries
- Growing community and adoption
- Popular: Ktor, SQLDelight, Koin, kotlinx.serialization

### Platform Feature Access

**React Native**: 4-16 week delay waiting for community modules
**KMM**: Day-zero access via Kotlin/Native interop

### When to Choose

**React Native**: JavaScript/React team, fast MVP, hot reload critical, cross-platform UI acceptable
**KMM**: Kotlin expertise, native UX critical, performance/type-safety important, existing Android app

**Examples**: React Native (Meta, Discord, Shopify), KMM (Netflix SDK, Cash App, VMware)

## Follow-ups

- How would you architect a hybrid native/KMM codebase for gradual migration?
- What are the trade-offs when choosing to share UI code vs keeping it platform-specific?
- How do you handle platform-specific features in shared KMM code?
- What are the debugging challenges with React Native bridge issues?
- How does Compose Multiplatform compare to KMM's approach?

## References

- Kotlin Multiplatform documentation
- React Native official documentation

## Related Questions

### Prerequisites
- Basic understanding of Kotlin and JavaScript
- Familiarity with mobile app development

### Related
- [[q-how-does-jetpackcompose-work--android--medium]]
- [[q-play-app-signing--android--medium]]

### Advanced
- Advanced KMM architecture patterns
- Platform-specific interop strategies
