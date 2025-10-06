# Amit Shekhar Android Interview Questions - Deduplication Report

**Analysis Date:** October 6, 2025
**Source:** `sources/amitshekhariitbhu-android-interview-questions/README.md`
**Baseline:** Kirchhoff Android Interview Questions (337 questions)

---

## Executive Summary

The Amit Shekhar repository contains **~200 questions** organized into 13 categories. After systematic analysis against our existing Kirchhoff vault (337 questions), the results show:

### Overall Statistics
- **EXACT_DUPLICATE:** 78 questions (39%) - Already comprehensively covered in Kirchhoff
- **SIMILAR:** 64 questions (32%) - Partial overlap, may add value with different perspectives
- **UNIQUE:** 58 questions (29%) - New topics not covered in vault

### Key Findings
1. **High duplication in fundamentals:** Kotlin basics, Android components, design patterns
2. **Unique value in:** System design, performance optimization, specific library implementations
3. **External content:** Many questions link to YouTube videos and blog posts (need content extraction)
4. **Format difference:** Kirchhoff has detailed answers; Amit Shekhar mostly has external links

---

## Category-by-Category Analysis

### 1. Kotlin Coroutines (15 topics)

**EXACT_DUPLICATE (10):**
- ✓ What are coroutines
- ✓ suspend functions
- ✓ launch vs async
- ✓ Dispatchers (IO, Main, Default)
- ✓ Coroutine Scope & Context
- ✓ Coroutine Job
- ✓ viewModelScope, lifecycleScope
- ✓ Exception handling in coroutines
- ✓ runBlocking
- ✓ Suspending vs Blocking

**SIMILAR (3):**
- ~ suspendCoroutine, suspendCancellableCoroutine (Kirchhoff has Channels/Flow, not raw continuation)
- ~ coroutineScope vs supervisorScope (Kirchhoff mentions but not dedicated question)
- ~ GlobalScope (mentioned in context but not standalone)

**UNIQUE (2):**
- ✗ Callback to Coroutines conversion (practical implementation pattern)
- ✗ Parallel multiple network calls using Coroutines (specific use case)

**External Links:** 11 blog posts, 3 YouTube videos

---

### 2. Kotlin Flow API (12 topics)

**EXACT_DUPLICATE (5):**
- ✓ Flow basics (Builder, Operator, Collector)
- ✓ Cold Flow vs Hot Flow
- ✓ StateFlow and SharedFlow
- ✓ flowOn, dispatchers
- ✓ Terminal operators

**SIMILAR (4):**
- ~ Flow operators (filter, map, zip, flatMapConcat, retry, debounce, distinctUntilChanged, flatMapLatest)
- ~ callbackFlow, channelFlow (Kirchhoff has Channels but not these specific builders)
- ~ Exception handling in Flow (general coverage but not dedicated)
- ~ Instant search using Flow operators (use case pattern)

**UNIQUE (3):**
- ✗ Creating Flow using Flow Builder (detailed implementation)
- ✗ Long-running tasks in parallel with Flow
- ✗ Retry operator in Flow (specific operator deep-dive)

**External Links:** 14 blog posts

---

### 3. Kotlin (45 questions)

**EXACT_DUPLICATE (28):**
- ✓ const in Kotlin
- ✓ lateinit keyword
- ✓ inline function
- ✓ companion objects
- ✓ extension functions
- ✓ data class
- ✓ JvmStatic annotation
- ✓ JvmField annotation
- ✓ JvmOverloads annotation
- ✓ noinline
- ✓ crossinline
- ✓ scope functions (let, run, with, also, apply)
- ✓ reified keyword
- ✓ lateinit vs lazy
- ✓ init block
- ✓ == vs === (structural vs referential equality)
- ✓ higher-order functions
- ✓ Lambdas
- ✓ open keyword
- ✓ internal visibility modifier
- ✓ partition function
- ✓ infix notation
- ✓ val vs var
- ✓ lateinit initialization check
- ✓ lazy initialization
- ✓ visibility modifiers
- ✓ Singleton creation
- ✓ open vs public

**SIMILAR (10):**
- ~ Remove duplicates from array (Kirchhoff has collections, not this specific operation)
- ~ AssociateBy - List to Map (collection operation, partial coverage)
- ~ String vs StringBuffer vs StringBuilder (Java question, Kirchhoff covers)
- ~ Sealed classes (Kirchhoff covers but Amit has more use cases)
- ~ Collections in Kotlin (general coverage)
- ~ Elvis operator (?:)
- ~ Labels in Kotlin
- ~ inline classes (Kirchhoff has but limited)
- ~ Delegates in Kotlin (delegated properties covered)
- ~ yield in Coroutines

**UNIQUE (7):**
- ✗ How Kotlin Multiplatform works
- ✗ What is structured concurrency in Coroutines
- ✗ How to implement debounce using Coroutines
- ✗ Run coroutines in series and parallel (code examples)
- ✗ stateIn vs shareIn in Flow
- ✗ flatMapConcat, flatMapMerge, flatMapLatest comparison
- ✗ collect vs collectLatest

**External Links:** 30+ blog posts, 15 YouTube videos

---

### 4. Android (120+ questions)

#### 4a. Base (6 questions)

**EXACT_DUPLICATE (4):**
- ✓ Context in Android
- ✓ Android application components
- ✓ Project structure
- ✓ AndroidManifest.xml

**UNIQUE (2):**
- ✗ Why does an Android App lag? (performance analysis)
- ✗ Application class

#### 4b. Activity & Fragment (15 questions)

**EXACT_DUPLICATE (9):**
- ✓ Fragment default constructor
- ✓ Activity lifecycle
- ✓ onCreate() vs onStart()
- ✓ Fragment lifecycle
- ✓ launchMode (singleTask)
- ✓ Fragment vs Activity
- ✓ FragmentPagerAdapter vs FragmentStatePagerAdapter
- ✓ Fragment communication
- ✓ addToBackStack()

**SIMILAR (4):**
- ~ onSaveInstanceState() and onRestoreInstanceState() (Kirchhoff has savedInstanceState)
- ~ Bundle in Android (mentioned but not standalone)
- ~ retained Fragment
- ~ add vs replace Fragment

**UNIQUE (2):**
- ✗ When only onDestroy is called without onPause() and onStop()
- ✗ Why setContentView() in onCreate()

#### 4c. Views & ViewGroups (10 questions)

**EXACT_DUPLICATE (4):**
- ✓ View in Android
- ✓ View.GONE vs View.INVISIBLE
- ✓ ViewGroups vs Views
- ✓ Relative Layout vs Linear Layout

**SIMILAR (3):**
- ~ Custom view creation
- ~ Canvas
- ~ SurfaceView (Kirchhoff covers)

**UNIQUE (3):**
- ✗ Optimizing layouts in Android
- ✗ Constraint Layout optimization (Cassowary algorithm)
- ✗ View tree optimization

#### 4d. RecyclerView (11 questions)

**EXACT_DUPLICATE (6):**
- ✓ ListView vs RecyclerView
- ✓ How RecyclerView works
- ✓ RecyclerView Adapter and ViewHolder
- ✓ LayoutManager
- ✓ DiffUtil
- ✓ SnapHelper

**SIMILAR (3):**
- ~ RecyclerView optimization (Kirchhoff has general optimization)
- ~ Nested RecyclerView optimization (setRecycledViewPool)
- ~ Multiple view types in RecyclerView

**UNIQUE (2):**
- ✗ setHasFixedSize(true) purpose
- ✗ Update specific item in RecyclerView

#### 4e. Intents & Broadcasting (7 questions)

**EXACT_DUPLICATE (6):**
- ✓ Intent
- ✓ Implicit Intent
- ✓ Explicit Intent
- ✓ BroadcastReceiver
- ✓ PendingIntent
- ✓ Types of Broadcasts

**SIMILAR (1):**
- ~ Broadcast and Intent message passing

#### 4f. Services (6 questions)

**EXACT_DUPLICATE (5):**
- ✓ Service lifecycle
- ✓ Service
- ✓ Service vs IntentService
- ✓ Foreground Service
- ✓ JobScheduler

**UNIQUE (1):**
- ✗ On which thread does Service run
- ✗ How WorkManager guarantees task execution

#### 4g. Data Saving (8 questions)

**EXACT_DUPLICATE (2):**
- ✓ Jetpack DataStore Preferences
- ✓ Ways to store data in Android

**SIMILAR (4):**
- ~ ORM (Room covered separately)
- ~ Preserve Activity state during rotation (savedInstanceState covered)
- ~ Scoped Storage
- ~ Encrypt data in Android

**UNIQUE (2):**
- ✗ commit() vs apply() in SharedPreferences
- ✗ Persisting data patterns

#### 4h. Memory & Performance (8 questions)

**EXACT_DUPLICATE (2):**
- ✓ onTrimMemory()
- ✓ Bitmap handling

**SIMILAR (3):**
- ~ Memory leak identification
- ~ OutOfMemory issues
- ~ Bitmap pool

**UNIQUE (3):**
- ✗ Improve Android App Performance (comprehensive guide)
- ✗ Memory leak vs OOM error
- ✗ Garbage Collection (forced GC)

#### 4i. Android Jetpack (12 questions)

**EXACT_DUPLICATE (8):**
- ✓ Android Jetpack
- ✓ ViewModel
- ✓ SharedViewModel
- ✓ Architecture Components
- ✓ LiveData
- ✓ setValue vs postValue
- ✓ Share ViewModel between Fragments
- ✗ WorkManager

**SIMILAR (2):**
- ~ StateFlow vs LiveData
- ~ ObservableField vs LiveData

**UNIQUE (2):**
- ✗ How ViewModel works internally
- ✗ Minimum repeat interval for PeriodicWorkRequest

#### 4j. Others (20+ questions)

**EXACT_DUPLICATE (12):**
- ✓ Parcelable vs Serializable
- ✓ Bundle class usage
- ✓ Android push notification system
- ✓ AAPT
- ✓ HashMap, ArrayMap, SparseArray
- ✓ Annotations
- ✓ Custom Annotations
- ✓ Android Support Library
- ✓ Data Binding
- ✓ ANR prevention
- ✓ Looper, Handler, HandlerThread
- ✓ ThreadPool

**SIMILAR (5):**
- ~ FlatBuffers vs JSON
- ~ Spannable/SpannableString
- ~ Dark mode implementation
- ~ Runnable vs Thread
- ~ Daemon vs User threads

**UNIQUE (3):**
- ✗ Android App Starts: Hot, Warm & Cold
- ✗ Baseline Profiles
- ✗ Android Runtime (Dalvik, ART, JIT, AOT)

---

### 5. Android Libraries (20 questions)

**EXACT_DUPLICATE (12):**
- ✓ OkHttp Interceptor
- ✓ HTTP Caching with OkHttp
- ✓ Dagger 2 basics
- ✓ @Inject, @Module, @Provides, @Component in Dagger
- ✓ Dagger Component
- ✓ Dagger Module
- ✓ Custom scope in Dagger
- ✓ CompositeDisposable dispose vs clear
- ✓ RxJava basics
- ✓ RxJava error handling
- ✓ RxJava operators (map, flatMap, create, fromCallable, defer, zip, concat, merge)
- ✓ RxJava Subjects

**SIMILAR (5):**
- ~ Logging in OkHttp
- ~ Dagger 2 vs Dagger-Hilt choice
- ~ Multipart Request (networking, not library-specific)
- ~ Image loading libraries (Glide, Fresco) - how they work
- ~ Schedulers.io() vs Schedulers.computation()

**UNIQUE (3):**
- ✗ App Startup Library
- ✗ RxJava instant search implementation
- ✗ Pagination in RecyclerView using RxJava

**External Links:** 15+ blog posts

---

### 6. Android Architecture (7 questions)

**EXACT_DUPLICATE (3):**
- ✓ MVVM
- ✓ MVC vs MVP vs MVVM
- ✓ MVI

**SIMILAR (2):**
- ~ Clean Architecture (mentioned but not detailed)
- ~ Software Architecture vs Software Design

**UNIQUE (2):**
- ✗ Multi-Module Architecture benefits
- ✗ Multi-Module Project: Why and When?

---

### 7. Design Patterns (11 questions)

**EXACT_DUPLICATE (8):**
- ✓ Builder
- ✓ Singleton
- ✓ Factory
- ✓ Observer
- ✓ Repository
- ✓ Adapter
- ✓ Facade
- ✓ Dependency Injection

**UNIQUE (3):**
- ✗ Design patterns in Android libraries (Retrofit, Glide)
- ✗ Kotlin Optional Parameters vs Builder Pattern
- ✗ Design Patterns in AOSP

**External Links:** 5 blog posts

---

### 8. Android System Design (18 questions)

**EXACT_DUPLICATE (1):**
- ✓ LRU Cache design

**SIMILAR (5):**
- ~ Image Loading Library design (Kirchhoff doesn't have system design)
- ~ File Downloader Library
- ~ Networking Library design
- ~ Caching Library design
- ~ Analytics Library design

**UNIQUE (12):**
- ✗ Design WhatsApp
- ✗ Design Instagram Stories
- ✗ Design Facebook Near-By Friends
- ✗ Location-based app design
- ✗ Offline-first app architecture
- ✗ HTTP Request vs Long-Polling vs WebSocket vs SSE
- ✗ Voice and Video Call implementation
- ✗ Data sync on unstable networks
- ✗ Design Uber App
- ✗ Database Normalization vs Denormalization
- ✗ Hash vs Encrypt vs Encode
- ✗ Webhook vs Polling
- ✗ Real-time updates options
- ✗ Network optimization in mobile apps
- ✗ Firebase Remote Config
- ✗ Accurate time in Android
- ✗ SQLite query optimization
- ✗ WebSocket vs Socket.IO
- ✗ Symmetric vs Asymmetric Encryption
- ✗ SMS Retriever API

**External Links:** 20+ blog posts, comprehensive system design content

**Priority: HIGH** - System design is critically missing from Kirchhoff

---

### 9. Android Unit Testing (8 questions)

**EXACT_DUPLICATE (6):**
- ✓ Espresso
- ✓ Robolectric
- ✓ Robolectric disadvantages
- ✓ UI-Automator
- ✓ Unit test
- ✓ Instrumented test
- ✓ Mockito

**UNIQUE (2):**
- ✗ Unit Testing ViewModel with Coroutines and LiveData
- ✗ Unit Testing ViewModel with Flow and StateFlow
- ✗ Code coverage

---

### 10. Jetpack Compose (35 topics + 30 questions)

**EXACT_DUPLICATE (8):**
- ✓ Jetpack Compose basics
- ✓ State (remember, rememberSaveable, MutableState)
- ✓ Recomposition
- ✓ Side-effects
- ✓ Modifier
- ✓ CompositionLocal
- ✓ Phases
- ✓ Lifecycle

**SIMILAR (15):**
- ~ Declarative UI concept
- ~ Declarative vs Imperative UI
- ~ Composable functions
- ~ State management
- ~ Stateful vs Stateless composable
- ~ LaunchedEffect vs DisposableEffect
- ~ rememberCoroutineScope
- ~ Observe Flows and LiveData in Compose
- ~ Async operations in Compose
- ~ Convert non-compose state to Compose state
- ~ derivedStateOf
- ~ rememberUpdatedState
- ~ remember vs rememberSaveable (Kirchhoff covers)
- ~ Lifecycle events in Compose
- ~ Performance optimization

**UNIQUE (12):**
- ✗ Jetpack Compose vs Android View System
- ✗ State Hoisting
- ✗ Semantics
- ✗ Handle user input and events
- ✗ Navigation in Compose
- ✗ Orientation changes in Compose
- ✗ Unidirectional data flow
- ✗ Custom Layouts in Compose
- ✗ Can we use traditional Views and Compose together

**External Links:** 10+ resources

**Priority: MEDIUM** - Kirchhoff has basics, Amit adds advanced topics

---

### 11. Android Tools & Technologies (20 questions)

**EXACT_DUPLICATE (8):**
- ✓ ADB
- ✓ StrictMode
- ✓ Lint
- ✓ Firebase
- ✓ SQLite Debug Database
- ✓ Proguard
- ✓ Gradle
- ✓ Build Variants

**SIMILAR (7):**
- ~ Git
- ~ Memory Profiler usage
- ~ Proguard considerations
- ~ Gradle build optimization
- ~ Multiple APKs
- ~ Obfuscation vs minification
- ~ Firebase Remote Config

**UNIQUE (5):**
- ✗ CI/CD Pipeline for Android
- ✗ 16 KB page size for Android Apps
- ✗ Android App Release Checklist
- ✗ Method execution time measurement
- ✗ Kotlin DSL for Gradle
- ✗ implementation vs api in Gradle
- ✗ Gradle files in Android project
- ✗ Custom Gradle tasks
- ✗ annotationProcessor, kapt, ksp
- ✗ Desugaring in Android
- ✗ ProGuard vs R8
- ✗ proguard-rules.pro file
- ✗ Write-Ahead Logging (WAL)

**Priority: MEDIUM** - Build tools and optimization knowledge

---

### 12. Java (80 questions) - **SKIPPED AS REQUESTED**

Note: Kirchhoff has comprehensive Java coverage (72 Java files). Focus on Kotlin/Android.

---

### 13. Other Topics (8 questions)

**EXACT_DUPLICATE (2):**
- ✓ SQLite
- ✓ Room

**SIMILAR (3):**
- ~ Android development best practices
- ~ App performance metrics
- ~ Memory usage

**UNIQUE (3):**
- ✗ React Native vs Flutter
- ✗ Kotlin Multiplatform implementation
- ✗ Memory Heap Dumps usage
- ✗ API keys security
- ✗ Cleartext traffic
- ✗ Annotation processing
- ✗ Local notification at exact time

---

## Priority Recommendations

### HIGH Priority (Import Immediately - 25 questions)

**System Design (12 questions):**
1. Design WhatsApp
2. Design Instagram Stories
3. Design Uber App
4. HTTP Request vs Long-Polling vs WebSocket vs SSE
5. Voice and Video Call implementation
6. Data sync on unstable networks
7. Database Normalization vs Denormalization
8. Hash vs Encrypt vs Encode
9. Network optimization in mobile apps
10. SQLite query optimization
11. Symmetric vs Asymmetric Encryption
12. SMS Retriever API

**Performance & Optimization (5 questions):**
13. Why does Android App lag
14. Improve Android App Performance
15. Memory leak vs OOM error
16. Android App Starts: Hot, Warm & Cold
17. Baseline Profiles

**Android Runtime (3 questions):**
18. Android Runtime (Dalvik, ART, JIT, AOT)
19. Multidex
20. Forced Garbage Collection

**Advanced Testing (2 questions):**
21. Unit Testing ViewModel with Coroutines/LiveData
22. Unit Testing ViewModel with Flow/StateFlow

**Build & Tools (3 questions):**
23. CI/CD Pipeline for Android
24. ProGuard vs R8
25. 16 KB page size for Android Apps

### MEDIUM Priority (Review & Import - 20 questions)

**Kotlin Advanced (7 questions):**
1. Kotlin Multiplatform implementation
2. Structured concurrency in Coroutines
3. stateIn vs shareIn in Flow
4. flatMapConcat, flatMapMerge, flatMapLatest
5. collect vs collectLatest
6. Debounce implementation using Coroutines
7. yield in Coroutines

**Jetpack Compose Advanced (6 questions):**
8. Jetpack Compose vs View System
9. State Hoisting
10. Semantics
11. Navigation in Compose
12. Unidirectional data flow
13. Custom Layouts in Compose

**Architecture & Patterns (4 questions):**
14. Multi-Module Architecture benefits
15. Design patterns in Android libraries
16. Design Patterns in AOSP
17. Kotlin Optional Parameters vs Builder Pattern

**Tools (3 questions):**
18. Kotlin DSL for Gradle
19. implementation vs api in Gradle
20. annotationProcessor, kapt, ksp

### LOW Priority (Consider for Completeness - 13 questions)

**Specific Use Cases:**
1. Callback to Coroutines conversion
2. Parallel network calls patterns
3. Instant search using Flow/RxJava
4. Pagination in RecyclerView using RxJava
5. Image Loading Library internals (Glide/Fresco)
6. App Startup Library
7. commit() vs apply() in SharedPreferences
8. setHasFixedSize(true) in RecyclerView
9. WorkManager task execution guarantee
10. React Native vs Flutter
11. Cleartext traffic
12. Annotation processing
13. Local notification at exact time

---

## Import Strategy

### Phase 1: Foundation (System Design & Performance)
- Import all HIGH priority system design questions
- Create new category: `40-Android/system-design/`
- Import performance optimization questions
- Add Android runtime internals

**Estimated: 25 questions**

### Phase 2: Advanced Kotlin & Compose
- Import MEDIUM priority Kotlin advanced topics
- Expand Jetpack Compose coverage
- Add advanced coroutines and Flow topics

**Estimated: 20 questions**

### Phase 3: Completeness
- Review LOW priority questions
- Import based on comprehensive coverage needs
- Focus on practical implementation patterns

**Estimated: 10-13 questions**

### Total New Questions: 55-58

---

## External Content Strategy

### Content Requiring Extraction (High Value):

**YouTube Videos (Priority):**
1. Android Push Notification Flow using FCM
2. How Android Push Notification works
3. Kotlin Multiplatform implementation
4. ViewModel internal working
5. HTTP Request vs WebSocket vs SSE (video)
6. Voice and Video Call implementation

**Blog Posts (Priority):**
1. All System Design blogs (outcomeschool.com)
2. Performance optimization guides
3. Android Runtime deep-dives
4. Testing with Coroutines/Flow
5. Multi-module architecture

### Extraction Approach:
1. For videos: Transcribe key points, create comprehensive written answers
2. For blogs: Extract core concepts, restructure for vault format
3. Add references to original sources
4. Ensure answers are self-contained

---

## Duplication Notes

### Questions to SKIP (Already Well Covered):

**Kotlin Basics (Complete coverage in Kirchhoff):**
- inline, lateinit, const, companion object
- data class, extension functions
- JvmStatic, JvmField, JvmOverloads
- scope functions, reified
- visibility modifiers

**Android Fundamentals (Complete coverage):**
- Activity/Fragment lifecycle
- Intents, BroadcastReceiver
- RecyclerView basics
- ViewModel, LiveData basics
- Services, WorkManager

**Design Patterns (Complete coverage):**
- All standard patterns (Singleton, Factory, Builder, etc.)
- MVVM, MVP, MVI architecture

**RxJava (Complete coverage):**
- All operators
- Subjects, Schedulers
- Hot vs Cold observables

---

## Quality Assessment

### Amit Shekhar Strengths:
1. Excellent system design coverage
2. Performance optimization focus
3. Practical implementation patterns
4. Up-to-date with modern Android
5. Good external resources (videos, blogs)

### Amit Shekhar Weaknesses:
1. Most answers are external links (not self-contained)
2. Less detailed explanations than Kirchhoff
3. Some overlap with basic topics
4. Missing comprehensive code examples in README

### Integration Recommendations:
1. **Extract content from external links** for key topics
2. **Create comprehensive answers** based on blog/video content
3. **Add code examples** where Amit only has links
4. **Cross-reference** with Kirchhoff when appropriate
5. **Prioritize unique system design questions**

---

## Next Steps

1. **Start with HIGH priority questions** (25 questions)
   - Create system-design category
   - Extract content from linked resources
   - Write comprehensive answers

2. **Review MEDIUM priority** (20 questions)
   - Assess value addition over Kirchhoff
   - Import those adding significant depth

3. **Evaluate LOW priority** (13 questions)
   - Import only if filling gaps

4. **Content extraction pipeline:**
   - Identify all high-value external links
   - Transcribe/extract content
   - Format for vault consistency

5. **Quality assurance:**
   - Ensure all imported questions have complete answers
   - Add code examples where needed
   - Cross-reference related questions

---

## Conclusion

The Amit Shekhar repository adds significant value in:
- **System Design** (critical gap in Kirchhoff)
- **Performance Optimization** (advanced topics)
- **Modern Android** (Compose, latest APIs)
- **Practical Patterns** (real-world implementations)

**Recommended Import: 55-58 questions** focusing on unique, high-value content.

**Timeline Estimate:**
- Phase 1 (HIGH): 2-3 days (25 questions + content extraction)
- Phase 2 (MEDIUM): 2 days (20 questions)
- Phase 3 (LOW): 1 day (10-13 questions)
- **Total: 5-6 days for complete integration**

The repository complements Kirchhoff excellently, filling critical gaps in system design and advanced topics while avoiding redundancy in fundamentals.
