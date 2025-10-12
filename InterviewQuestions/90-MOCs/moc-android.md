---
id: ivm-20251012-140000
title: Android — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/android]
---

# Android — Map of Content

## Overview
This MOC covers Android development topics including framework fundamentals, Jetpack Compose, architecture components, dependency injection, testing, performance optimization, security, and best practices for building Android applications.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Jetpack Compose

**Key Questions** (Curated Learning Path):

#### Compose Basics
- [[q-jetpack-compose-basics--android--medium]] - Introduction to Jetpack Compose
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works under the hood
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-jetpack-compose-lazy-column--android--easy]] - LazyColumn for lists
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - RecyclerView equivalent in Compose

#### State Management
- [[q-mutable-state-compose--android--medium]] - MutableState and state management
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--jetpack-compose--medium]] - Derived state patterns
- [[q-state-hoisting-compose--android--medium]] - State hoisting principles
- [[q-pomogaet-li-state-sdelannyy-v-compose-izbezhat-sostoyaniya-gonki--android--medium]] - State and race conditions

#### Recomposition & Performance
- [[q-recomposition-compose--android--medium]] - Understanding recomposition
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability and skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations in depth
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table and recomposition
- [[q-compose-performance-optimization--android--hard]] - Performance optimization strategies
- [[q-compose-lazy-layout-optimization--jetpack-compose--hard]] - Lazy layout optimization

#### Side Effects
- [[q-compose-side-effects-launchedeffect-disposableeffect--android--hard]] - LaunchedEffect & DisposableEffect
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Advanced side effect patterns

#### UI & Layouts
- [[q-compose-modifier-system--android--medium]] - Modifier system
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Modifier order and performance
- [[q-compose-custom-layout--jetpack-compose--hard]] - Custom layouts
- [[q-kak-risuet-compose-na-ekrane--android--hard]] - How Compose draws on screen

#### Animations & Gestures
- [[q-compose-custom-animations--jetpack-compose--medium]] - Custom animations
- [[q-animated-visibility-vs-content--jetpack-compose--medium]] - AnimatedVisibility vs AnimatedContent
- [[q-shared-element-transitions--jetpack-compose--hard]] - Shared element transitions
- [[q-compose-gesture-detection--jetpack-compose--medium]] - Gesture detection

#### Advanced Topics
- [[q-compositionlocal-compose--android--hard]] - CompositionLocal basics
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Advanced CompositionLocal patterns
- [[q-compose-compiler-plugin--jetpack-compose--hard]] - Compose compiler plugin
- [[q-view-composition-strategy-compose--android--medium]] - View composition strategies
- [[q-compose-semantics--android--medium]] - Semantics for accessibility
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Advanced navigation patterns

#### Testing & Migration
- [[q-compose-testing--android--medium]] - Testing Compose UI
- [[q-testing-compose-ui--android--medium]] - UI testing strategies
- [[q-compose-ui-testing-advanced--testing--hard]] - Advanced UI testing
- [[q-migration-to-compose--android--medium]] - Migration strategies

**All Compose Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "compose") OR contains(tags, "jetpack-compose") OR contains(tags, "compose")
SORT difficulty ASC, file.name ASC
```

### Dependency Injection

**Key Questions**:

#### Hilt Basics
- [[q-what-is-hilt--android--medium]] - Introduction to Hilt
- [[q-koin-vs-hilt-comparison--dependency-injection--medium]] - Koin vs Hilt comparison

**All DI Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "dagger") OR contains(file.name, "hilt") OR contains(tags, "dagger") OR contains(tags, "hilt") OR contains(tags, "dependency-injection")
SORT difficulty ASC, file.name ASC
```

### Testing

**Key Questions**:

#### Testing Strategies
- [[q-android-testing-strategies--android--medium]] - Android testing overview
- [[q-robolectric-vs-instrumented--testing--medium]] - Robolectric vs Instrumented tests
- [[q-integration-testing-strategies--testing--medium]] - Integration testing approaches

#### Unit Testing
- [[q-unit-testing-coroutines-flow--android--medium]] - Testing coroutines and Flow
- [[q-testing-coroutines-flow--testing--hard]] - Advanced coroutines/Flow testing
- [[q-testing-viewmodels-turbine--testing--medium]] - Testing ViewModels with Turbine
- [[q-fakes-vs-mocks-testing--testing--medium]] - Fakes vs Mocks
- [[q-test-doubles-dependency-injection--testing--medium]] - Test doubles and DI

#### UI Testing
- [[q-compose-testing--android--medium]] - Compose UI testing
- [[q-compose-ui-testing-advanced--testing--hard]] - Advanced Compose testing
- [[q-espresso-advanced-patterns--testing--medium]] - Advanced Espresso patterns
- [[q-screenshot-snapshot-testing--testing--medium]] - Screenshot/snapshot testing

#### Testing Tools
- [[q-mockk-advanced-features--testing--medium]] - MockK advanced features
- [[q-flaky-test-prevention--testing--medium]] - Preventing flaky tests
- [[q-test-coverage-quality-metrics--testing--medium]] - Test coverage metrics
- [[q-accessibility-testing--accessibility--medium]] - Accessibility testing

**All Testing Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "testing") OR contains(file.name, "test") OR contains(tags, "testing") OR topic = "testing"
SORT difficulty ASC, file.name ASC
```

### Architecture & Design Patterns

**Key Questions**:

#### Architecture Patterns
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles
- [[q-mvi-architecture--android--hard]] - MVI (Model-View-Intent) architecture
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture strategies

#### ViewModels & Lifecycle
- [[q-what-is-viewmodel--android--medium]] - Introduction to ViewModel
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose and internals
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation limits

**All Architecture Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "architecture") OR contains(tags, "mvvm") OR contains(tags, "mvi") OR contains(file.name, "architecture")
SORT difficulty ASC, file.name ASC
```

### Multiplatform (KMM)

**Key Questions**:

#### KMM Fundamentals
- [[q-kmm-architecture--multiplatform--hard]] - KMM architecture patterns
- [[q-kmm-production-readiness--multiplatform--hard]] - Production readiness considerations
- [[q-compose-multiplatform--multiplatform--hard]] - Compose Multiplatform

#### KMM Development
- [[q-kmm-ktor-networking--multiplatform--medium]] - Networking with Ktor
- [[q-kmm-sqldelight--multiplatform--medium]] - Database with SQLDelight
- [[q-kmm-dependency-injection--multiplatform--medium]] - Dependency injection in KMM
- [[q-kmm-testing--multiplatform--medium]] - Testing KMM code

#### Alternatives Comparison
- [[q-flutter-comparison--multiplatform--medium]] - KMM vs Flutter
- [[q-react-native-comparison--multiplatform--medium]] - KMM vs React Native

**All KMM Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "kmm") OR contains(file.name, "multiplatform") OR contains(tags, "multiplatform")
SORT difficulty ASC, file.name ASC
```

### Performance & Optimization

**Key Questions**:

#### Performance Measurement
- [[q-android-performance-measurement-tools--android--medium]] - Performance measurement tools
- [[q-what-is-layout-performance-measured-in--android--medium]] - Layout performance metrics
- [[q-jank-detection-frame-metrics--performance--medium]] - Jank detection and frame metrics
- [[q-memory-leak-detection--performance--medium]] - Memory leak detection

#### App Optimization
- [[q-app-startup-optimization--performance--medium]] - App startup optimization
- [[q-app-size-optimization--performance--medium]] - App size reduction
- [[q-baseline-profiles-optimization--performance--medium]] - Baseline profiles
- [[q-macrobenchmark-startup--performance--medium]] - Macrobenchmark for startup

#### Compose Performance
- [[q-compose-performance-optimization--android--hard]] - Compose performance optimization
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Modifier order impact
- [[q-performance-monitoring-jank-compose--android--medium]] - Monitoring jank in Compose

**All Performance Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

### Security

**Key Questions**:

#### Security Best Practices
- [[q-android-security-best-practices--android--medium]] - Android security overview
- [[q-android-security-practices-checklist--android--medium]] - Security practices checklist
- [[q-app-security-best-practices--security--medium]] - App security best practices

#### Data Protection
- [[q-android-keystore-system--security--medium]] - Android Keystore system
- [[q-data-encryption-at-rest--security--medium]] - Data encryption at rest
- [[q-database-encryption-android--android--medium]] - Database encryption
- [[q-encrypted-file-storage--security--medium]] - Encrypted file storage

#### Network Security
- [[q-certificate-pinning--security--medium]] - Certificate pinning

#### Code Protection
- [[q-proguard-r8-rules--security--medium]] - ProGuard/R8 obfuscation

**All Security Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "security") OR topic = "security" OR contains(file.name, "security")
SORT difficulty ASC, file.name ASC
```

### Fragments & Activities

**Key Questions**:

#### Activity Fundamentals
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]] - What is an Activity?
- [[q-how-does-activity-lifecycle-work--android--medium]] - Activity lifecycle overview
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle methods
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle methods details
- [[q-android-components-besides-activity--android--easy]] - Android components overview

#### Activity State Management
- [[q-how-to-save-activity-state--android--medium]] - Saving activity state
- [[q-how-to-save-scroll-state-when-activity-is-recreated--android--medium]] - Saving scroll state
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Memory management
- [[q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard]] - Activity stack behavior

#### Activity Navigation
- [[q-how-to-pass-data-from-one-activity-to-another--android--medium]] - Passing data between activities
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Deep link handling
- [[q-single-activity-approach--android--medium]] - Single-activity architecture
- [[q-single-activity-pros-cons--android--medium]] - Single-activity pros/cons

#### Fragment Basics
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Why use Fragments?
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Fragment purpose
- [[q-fragments-vs-activity--android--medium]] - Fragments vs Activities
- [[q-fragments-and-activity-relationship--android--hard]] - Fragment-Activity relationship
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Choosing Fragment layout

#### Fragment Lifecycle
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Fragment vs Activity lifecycle
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle differences
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle connection
- [[q-why-fragment-needs-separate-callback-for-ui-creation--android--hard]] - Fragment UI creation callbacks
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Callback differences

#### Fragment Communication
- [[q-how-to-pass-parameters-to-a-fragment--android--easy]] - Passing parameters to Fragments
- [[q-how-to-pass-parameters-to-fragment--android--easy]] - Fragment parameters
- [[q-how-to-pass-data-from-one-fragment-to-another--android--medium]] - Inter-fragment communication
- [[q-save-data-outside-fragment--android--medium]] - Saving data beyond Fragment scope
- [[q-how-can-data-be-saved-beyond-the-fragment-scope--android--medium]] - Data persistence

#### Fragment Transactions
- [[q-how-to-add-fragment-synchronously-asynchronously--android--medium]] - Adding Fragments (sync/async)
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment state loss

**All Fragment & Activity Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "fragment") OR contains(file.name, "activity") OR contains(tags, "fragments") OR contains(tags, "activities")
SORT difficulty ASC, file.name ASC
```

### Data & Networking

**Key Questions**:

#### Room Database
- [[q-room-database-migrations--room--medium]] - Database migrations
- [[q-room-relations-embedded--room--medium]] - Relations and embedded entities
- [[q-room-type-converters-advanced--room--medium]] - Type converters
- [[q-room-transactions-dao--room--medium]] - Transactions in DAO
- [[q-room-paging3-integration--room--medium]] - Paging 3 integration
- [[q-room-fts-full-text-search--room--hard]] - Full-text search

#### Networking Fundamentals
- [[q-graphql-vs-rest--networking--easy]] - GraphQL vs REST
- [[q-okhttp-interceptors-advanced--networking--medium]] - OkHttp interceptors
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Retrofit call adapters
- [[q-network-error-handling-strategies--networking--medium]] - Error handling strategies

#### Advanced Networking
- [[q-websocket-implementation--networking--medium]] - WebSocket implementation
- [[q-server-sent-events-sse--networking--medium]] - Server-Sent Events (SSE)
- [[q-graphql-apollo-android--networking--medium]] - GraphQL with Apollo Android
- [[q-network-request-deduplication--networking--hard]] - Request deduplication

#### Data Synchronization
- [[q-data-sync-unstable-network--android--hard]] - Sync with unstable network
- [[q-kmm-ktor-networking--multiplatform--medium]] - Ktor networking (KMM)

**All Data & Networking Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "networking") OR contains(tags, "retrofit") OR contains(tags, "data-sync") OR contains(file.name, "network") OR contains(file.name, "sync")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "40-Android"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "40-Android"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-kotlin]]
- [[moc-compSci]]
- [[moc-tools]]
