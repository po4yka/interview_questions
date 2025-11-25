---
id: ivm-20251018-140100
title: Performance & Optimization — MOC
kind: moc
created: 2025-10-18
updated: 2025-10-18
tags: [moc, topic/performance]
date created: Saturday, October 18th 2025, 2:45:12 pm
date modified: Tuesday, November 25th 2025, 8:53:47 pm
---

# Performance & Optimization — Map of Content

## Overview
This MOC aggregates performance-related questions across Android app optimization, Kotlin language performance, database query optimization, and general profiling techniques. Performance optimization spans multiple topics including startup time, memory management, rendering efficiency, compilation strategies, and benchmarking.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", topic AS "Topic", subtopics AS "Subtopics"
FROM "40-Android" OR "70-Kotlin" OR "50-Backend" OR "60-CompSci"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", topic AS "Topic", subtopics AS "Subtopics"
FROM "40-Android" OR "70-Kotlin" OR "50-Backend" OR "60-CompSci"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", topic AS "Topic", subtopics AS "Subtopics"
FROM "40-Android" OR "70-Kotlin" OR "50-Backend" OR "60-CompSci"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic with Key Questions

### Performance Measurement & Profiling

**Key Questions** (Curated Learning Path):

#### Measurement Tools
- [[q-android-performance-measurement-tools--android--medium]] - Overview of Android profiling tools
- [[q-jank-detection-frame-metrics--performance--medium]] - Detecting frame drops and jank
- [[q-performance-monitoring-jank-compose--android--medium]] - Monitoring jank in Jetpack Compose

#### Profiling Techniques
- [[q-strictmode-debugging--android--medium]] - StrictMode for detecting slow operations
- [[q-what-is-layout-performance-measured-in--android--medium]] - Layout performance metrics

**All Profiling Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "profiling") OR contains(tags, "android-profiler") OR contains(file.name, "profiling")
SORT difficulty ASC, file.name ASC
```

### App Startup Optimization

**Key Questions**:

#### Startup Performance
- [[q-app-startup-optimization--android--medium]] - App startup optimization strategies
- [[q-macrobenchmark-startup--performance--medium]] - Macrobenchmark for startup testing
- [[q-baseline-profiles-optimization--android--medium]] - Baseline profiles for AOT compilation
- [[q-baseline-profiles-android--android--medium]] - Baseline profiles implementation
- [[q-app-start-types-android--android--medium]] - Cold/warm/hot startup types
- [[q-fix-slow-app-startup-legacy--android--hard]] - Fixing slow startup in legacy apps

#### App Startup Library
- [[q-app-startup-library--android--medium]] - Jetpack App Startup library

**All Startup Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "startup") OR contains(tags, "app-startup") OR contains(file.name, "startup")
SORT difficulty ASC, file.name ASC
```

### Memory Management & Optimization

**Key Questions**:

#### Memory Leak Detection
- [[q-memory-leak-detection--performance--medium]] - Memory leak detection techniques
- [[q-memory-leaks-definition--android--easy]] - What are memory leaks?
- [[q-memory-leak-vs-oom-android--android--medium]] - Memory leaks vs OutOfMemoryError

#### Memory Optimization
- [[q-optimize-memory-usage-android--android--medium]] - Memory usage optimization strategies
- [[q-sparsearray-optimization--android--medium]] - SparseArray for memory efficiency
- [[q-primitive-maps-android--android--medium]] - Primitive collections for reduced allocation

**All Memory Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "memory") OR contains(tags, "performance-memory") OR contains(file.name, "memory")
SORT difficulty ASC, file.name ASC
```

### Jetpack Compose Performance

**Key Questions**:

#### Compose Optimization
- [[q-compose-performance-optimization--android--hard]] - Comprehensive Compose performance
- [[q-compose-modifier-order-performance--android--medium]] - Modifier order impact
- [[q-compose-stability-skippability--android--hard]] - Stability and skippability
- [[q-stable-classes-compose--android--hard]] - Stable annotation usage
- [[q-stable-annotation-compose--android--hard]] - @Stable in depth
- [[q-compose-lazy-layout-optimization--android--hard]] - Lazy layout optimization
- [[q-recomposition-compose--android--medium]] - Understanding recomposition
- [[q-recomposition-choreographer--android--hard]] - Recomposition and Choreographer
- [[q-how-to-reduce-the-number-of-recompositions-besides-side-effects--android--hard]] - Reducing recompositions

#### Compose Compiler
- [[q-compose-compiler-plugin--android--hard]] - Compose compiler plugin internals

**All Compose Performance Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "jetpack-compose") AND (contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance"))
SORT difficulty ASC, file.name ASC
```

### UI Rendering Performance

**Key Questions**:

#### Rendering Optimization
- [[q-overdraw-gpu-rendering--android--medium]] - GPU overdraw detection
- [[q-main-causes-ui-lag--android--medium]] - Common causes of UI lag
- [[q-why-list-scrolling-lags--android--medium]] - List scrolling performance issues
- [[q-android-app-lag-analysis--android--medium]] - Analyzing app lag
- [[q-how-to-fix-a-bad-element-layout--android--easy]] - Fixing slow layouts
- [[q-frame-time-120ms-meaning--android--easy]] - Understanding frame time

#### RecyclerView Performance
- [[q-recyclerview-sethasfixedsize--android--easy]] - setHasFixedSize optimization
- [[q-how-to-write-recyclerview-cache-ahead--android--medium]] - RecyclerView caching strategies
- [[q-diffutil-background-calculation-issues--android--medium]] - DiffUtil performance considerations
- [[q-why-use-diffutil--android--medium]] - DiffUtil for efficient updates
- [[q-recyclerview-diffutil-advanced--recyclerview--medium]] - Advanced DiffUtil patterns
- [[q-recyclerview-async-list-differ--recyclerview--medium]] - AsyncListDiffer for background diffing

#### Custom Views
- [[q-custom-view-lifecycle--android--medium]] - Custom view lifecycle
- [[q-canvas-optimization--graphics--medium]] - Canvas drawing optimization
- [[q-canvas-drawing-optimization--android--hard]] - Advanced canvas optimization

**All Rendering Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE (contains(tags, "rendering") OR contains(tags, "gpu-rendering") OR contains(file.name, "rendering") OR contains(file.name, "overdraw"))
SORT difficulty ASC, file.name ASC
```

### Build & Compilation Performance

**Key Questions**:

#### Build Optimization
- [[q-android-build-optimization--android--medium]] - Build time optimization
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization
- [[q-dagger-build-time-optimization--android--medium]] - Dagger build performance

#### Compilation Strategies
- [[q-jit-vs-aot-compilation--android--medium]] - JIT vs AOT compilation
- [[q-dalvik-vs-art-runtime--android--medium]] - Dalvik vs ART runtime
- [[q-android-runtime-art--android--medium]] - Android Runtime (ART) internals
- [[q-android-runtime-internals--android--hard]] - ART runtime deep dive

#### Annotation Processing
- [[q-kapt-vs-ksp--android--medium]] - KAPT vs KSP performance
- [[q-kapt-ksp-migration--gradle--medium]] - Migrating from KAPT to KSP

**All Build Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "gradle") OR contains(tags, "build") OR contains(file.name, "build") OR contains(file.name, "kapt") OR contains(file.name, "ksp")
SORT difficulty ASC, file.name ASC
```

### Kotlin Language Performance

**Key Questions**:

#### Coroutines Performance
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutine performance optimization
- [[q-dispatcher-performance--kotlin--hard]] - Dispatcher performance considerations
- [[q-flow-performance--kotlin--hard]] - Flow performance optimization
- [[q-flow-backpressure--kotlin--hard]] - Flow backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
- [[q-channel-buffering-strategies--kotlin--hard]] - Channel buffering for performance
- [[q-channel-buffer-strategies-comparison--kotlin--hard]] - Comparing buffer strategies

#### Inline Functions & Value Classes
- [[q-inline-functions--kotlin--medium]] - Inline function performance
- [[q-kotlin-inline-functions--kotlin--medium]] - Inline functions in detail
- [[q-inline-value-classes-performance--kotlin--medium]] - Value classes performance
- [[q-value-classes-inline-classes--kotlin--medium]] - Value classes overview
- [[q-inline-classes-value-classes--kotlin--medium]] - Inline vs value classes

#### Collections Performance
- [[q-sequences-vs-collections-performance--kotlin--medium]] - Sequences vs collections
- [[q-sequences-detailed--kotlin--medium]] - Sequence performance characteristics
- [[q-list-vs-sequence--kotlin--medium]] - List vs Sequence tradeoffs
- [[q-array-vs-list-kotlin--kotlin--easy]] - Array vs List performance

#### Async Performance
- [[q-deferred-async-patterns--kotlin--medium]] - Deferred and async patterns
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Parallel call optimization

**All Kotlin Performance Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

### Database Performance

**Key Questions**:

#### Database Optimization
- [[q-database-optimization-android--android--medium]] - Android database optimization
- [[q-sql-join-algorithms-complexity--backend--hard]] - SQL join performance
- [[q-virtual-tables-disadvantages--backend--medium]] - Virtual table performance

#### Room Optimization
- [[q-room-fts-full-text-search--room--hard]] - Full-text search in Room
- [[q-room-type-converters-advanced--room--medium]] - Type converter efficiency

**All Database Performance Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android" OR "50-Backend"
WHERE (contains(tags, "database") OR contains(tags, "room") OR contains(tags, "sql")) AND (contains(tags, "performance") OR contains(tags, "optimization"))
SORT difficulty ASC, file.name ASC
```

### General Optimization Strategies

**Key Questions**:

#### App Size Optimization
- [[q-app-size-optimization--android--medium]] - Reducing APK/AAB size
- [[q-reduce-apk-size-techniques--android--medium]] - APK size reduction techniques

#### Resource Optimization
- [[q-webp-image-format-android--android--easy]] - WebP for smaller images
- [[q-when-is-it-better-to-use-png-and-webp-and-when-svg--android--easy]] - Image format selection

#### Parsing & Serialization
- [[q-parsing-optimization-android--android--medium]] - Parsing optimization strategies

#### Caching
- [[q-cache-implementation-strategies--android--medium]] - Cache implementation patterns

#### Network Performance
- [[q-network-request-deduplication--networking--hard]] - Request deduplication
- [[q-http-protocols-comparison--android--medium]] - HTTP protocol performance

#### Data Rendering
- [[q-fast-chat-rendering--android--hard]] - Optimizing chat rendering

**All General Optimization Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE (contains(tags, "optimization") OR contains(file.name, "optimization") OR contains(file.name, "optimize"))
  AND NOT contains(tags, "performance")
SORT difficulty ASC, file.name ASC
```

### ANR & Responsiveness

**Key Questions**:

- [[q-anr-application-not-responding--android--medium]] - Understanding ANRs
- [[q-why-multithreading-tools--android--easy]] - Why use multithreading?
- [[q-how-does-the-main-thread-work--android--medium]] - Main thread mechanics

**All ANR Questions:**
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "anr") OR contains(tags, "strictmode") OR contains(file.name, "anr")
SORT difficulty ASC, file.name ASC
```

## By Platform

### Android-Specific Performance
```dataview
TABLE difficulty, subtopics, status
FROM "40-Android"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

### Kotlin Performance
```dataview
TABLE difficulty, subtopics, status
FROM "70-Kotlin"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

### Backend/Database Performance
```dataview
TABLE difficulty, subtopics, status
FROM "50-Backend"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

## All Performance Questions
```dataview
TABLE difficulty, topic, subtopics, status, tags
FROM "40-Android" OR "70-Kotlin" OR "50-Backend" OR "60-CompSci"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, topic ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "40-Android" OR "70-Kotlin" OR "50-Backend" OR "60-CompSci"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
GROUP BY difficulty
SORT difficulty ASC
```

## Related Concepts

- [[c-database-performance]] - Database performance optimization patterns

## Related MOCs

- [[moc-android]] - Android development (contains many performance questions)
- [[moc-kotlin]] - Kotlin language (coroutines, inline functions, collections)
- [[moc-cs]] - Computer science fundamentals
- [[moc-backend]] - Backend and database optimization
