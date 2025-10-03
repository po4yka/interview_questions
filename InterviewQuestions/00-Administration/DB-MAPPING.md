# Database to Vault Mapping

**Source**: channels.db (easy_kotlin table)
**Total Q&A pairs**: 891
**Unique DB themes**: 197

This document maps database themes to Obsidian vault topics, subtopics, and folders.

---

## Mapping Strategy

### Topic Selection Rules
1. **Android-specific** → `topic: android` (use Android subtopics from TAXONOMY.md)
2. **Kotlin language** → `topic: programming-languages`
3. **Architecture/Design patterns** → `topic: architecture-patterns`
4. **Data structures** → `topic: data-structures`
5. **Coroutines (general)** → `topic: concurrency`
6. **Database/SQL** → `topic: databases`
7. **Networking** → `topic: networking`
8. **Performance** → `topic: performance`
9. **Testing** → `topic: testing`
10. **Security** → `topic: security`
11. **Git/DevOps** → `topic: devops-ci-cd`
12. **General CS** → `topic: cs`

### Folder Assignment
- `android` → `40-Android/`
- `programming-languages` → `60-CompSci/` (or create `65-Languages/` if needed)
- `architecture-patterns` → `60-CompSci/`
- `concurrency` → `60-CompSci/`
- `data-structures` → `60-CompSci/`
- `databases` → `60-CompSci/`
- All others → `60-CompSci/`

---

## Theme → Topic Mapping (197 themes)

### ANDROID (topic: android) - ~450 Q&As
**Folder**: `40-Android/`

#### Android UI (~137 Q&As)
**Subtopics**: `ui-views`, `ui-compose`, `ui-navigation`, `ui-widgets`, `ui-state`, `ui-performance`

DB Themes:
- Android UI (110)
- Jetpack Compose (5)
- Android UI Performance Optimization (6)
- Android UI Architecture (4)
- Android UI Optimization (2)
- Android UI Migration (2)
- Android UI Performance (1)
- Android UI Navigation (1)
- Android UI and State Management (1)
- Android UI Resources (1)
- Android Navigation (8)
- Android Navigation Architecture (1)

#### Android Lifecycle (~85 Q&As)
**Subtopics**: `lifecycle`, `activity`, `fragment`

DB Themes:
- Android Lifecycle (69)
- Android Lifecycle Management (3)
- Android Lifecycle and Events (2)
- Android Activity Lifecycle (2)
- Android Components (13)
- Android Services (5)
- Android Services Management (1)
- Android Services Lifecycle (1)

#### Android Architecture (~50 Q&As)
**Subtopics**: `architecture-mvvm`, `architecture-mvi`, `architecture-clean`, `architecture-modularization`

DB Themes:
- Android Architecture (20)
- Android Architecture Patterns (15)
- Android Architecture Components (3)
- Android Architecture Principles (2)
- Android UI Architecture (4)

#### Android Data & Storage (~25 Q&As)
**Subtopics**: `room`, `datastore`, `files-media`, `cache-offline`, `serialization`

DB Themes:
- Android Data Storage (9)
- Android Data Handling (2)
- Android Data Structures (2)
- Android Data Passing (5)
- Android Data Sharing (1)
- Data Persistence (2)
- Android Data Storage and Caching (1)

#### Android Dependency Injection (~11 Q&As)
**Subtopics**: `di-hilt` (or general DI)

DB Themes:
- Android Dependency Injection (4)
- Android DI (Dependency Injection) (1)
- Android DI and ViewModel Integration (1)
- Android DI and Architecture Components (1)

#### Android Networking (~12 Q&As)
**Subtopics**: `networking-http`, `connectivity-caching`

DB Themes:
- Android Network Communication (5)
- Android Network (4)
- Android Networking (2)
- Android Network Operations (2)
- Networking in Android (1)
- Android Networking & Data Handling (1)

#### Android Performance (~25 Q&As)
**Subtopics**: `performance-startup`, `performance-rendering`, `performance-memory`, `profiling`

DB Themes:
- Android Performance Optimization (10)
- Android Performance (3)
- Android Performance Testing (1)
- Android Runtime & Performance (2)
- Android Memory Management (11)
- Android UI Performance Optimization (6)
- Android UI Performance (1)

#### Android Concurrency & Threading (~15 Q&As)
**Subtopics**: `coroutines`, `threads-sync`, `background-execution`

DB Themes:
- Android Concurrency (5)
- Android Threading (4)
- Android Asynchronous Programming (2)
- Android Background Processing (5)
- Android Concurrency and Threading (1)
- Background Tasks and Concurrency (1)

#### Android Build & Configuration (~25 Q&As)
**Subtopics**: `gradle`, `build-variants`, `versioning`, `ci-cd`

DB Themes:
- Android Project Structure (5)
- Android Project Configuration (2)
- Android Build System (2)
- Android Build Optimization (2)
- Android Build and Deployment (3)
- Android Build Process (1)
- Android Packaging (1)

#### Android Testing (~3 Q&As)
**Subtopics**: `testing-unit`, `testing-instrumented`, `testing-ui`

DB Themes:
- Android Testing (2)
- Testing (1)

#### Android Security & Permissions (~3 Q&As)
**Subtopics**: `permissions`, `keystore-crypto`, `network-security-config`

DB Themes:
- Android Security & Permissions (1)
- Android Security (1)
- Android File System Security (1)

#### Android Intents & Communication (~7 Q&As)
**Subtopics**: `intents-deeplinks`, `content-provider`, `broadcast-receiver`

DB Themes:
- Android Intents and Data Sharing (1)
- Android Intents and Data Passing (1)
- Android Intents and Components (1)
- Android Communication (1)

#### Android Fundamentals & Basics (~35 Q&As)
**Subtopics**: `activity`, `lifecycle`, `processes`, `app-startup`

DB Themes:
- Android Basics (2)
- Android Fundamentals (2)
- Android Development (1)
- Android Development Basics (1)
- Android Development Fundamentals (1)
- Android Development Practices (1)
- Android Development with Kotlin (2)
- Android Application Structure (3)
- Android System Features (2)
- Android System Behavior (2)
- Android System Architecture (1)
- Android Internals (1)
- Android Resources (2)
- Android File Handling (1)

#### Android Versions (~6 Q&As)
**Subtopics**: General Android

DB Themes:
- Android Versions Comparison (3)
- Android Versions Differences (1)
- Android Versions (1)
- Android OS Versions (1)

#### Android Design Patterns (~1 Q&A)
**Subtopics**: `architecture-patterns`

DB Themes:
- Android Design Patterns (1)
- Design Patterns in Mobile Development (1)

---

### KOTLIN / PROGRAMMING-LANGUAGES (topic: programming-languages) - ~280 Q&As
**Folder**: `60-CompSci/` (or consider creating separate folder)

#### Kotlin Basics & Syntax (~180 Q&As)
**Subtopics**: `kotlin`, `syntax`, `types`

DB Themes:
- Basic Kotlin (111)
- Kotlin Basics (39)
- Basic Kotlin Syntax (18)
- Kotlin Language Features (28)
- Kotlin Fundamentals (6)
- Kotlin Syntax (3)
- Kotlin Syntax and Features (2)
- Kotlin Syntax Features (1)
- Kotlin Syntax and Semantics (1)
- Basic Kotlin Syntax and Features (1)
- Basic Kotlin Types (1)
- Basic Kotlin Typesystem (2)
- Basic Kotlin Programming (1)
- Kotlin for Android Development (2)

#### Kotlin Functions (~6 Q&As)
**Subtopics**: `kotlin`, `functions`

DB Themes:
- Kotlin Functions (6)

#### Kotlin Classes & OOP (~20 Q&As)
**Subtopics**: `kotlin`, `oop`, `classes`

DB Themes:
- Kotlin Classes and Inheritance (4)
- Kotlin Classes (2)
- Kotlin Class Structure (1)
- Kotlin Object Oriented Programming (3)
- Object-Oriented Programming (5)
- Object-Oriented Programming Principles (5)
- Object-Oriented Programming Concepts (1)

#### Kotlin Data Classes (~3 Q&As)
**Subtopics**: `kotlin`, `data-classes`

DB Themes:
- Kotlin Data Classes (3)

#### Kotlin Generics & Type System (~8 Q&As)
**Subtopics**: `kotlin`, `generics`, `type-system`

DB Themes:
- Kotlin Type System (2)
- Kotlin Generics and Type System (2)
- Kotlin Generics and Null Safety (2)
- Kotlin Generics (2)

#### Kotlin Collections (~35 Q&As)
**Subtopics**: `kotlin`, `collections`

DB Themes:
- Kotlin Collections (29)
- Kotlin Collections Performance (3)
- Kotlin Collections and Strings (2)
- Kotlin Collections and Functions (1)

#### Kotlin Null Safety (~1 Q&A)
**Subtopics**: `kotlin`, `null-safety`

DB Themes:
- Kotlin Null Safety (1)

#### Kotlin Delegation (~4 Q&As)
**Subtopics**: `kotlin`, `delegation`

DB Themes:
- Kotlin Delegation Pattern (2)
- Kotlin Delegation and Properties (1)

#### Kotlin Special Features (~2 Q&As)
**Subtopics**: `kotlin`, `advanced`

DB Themes:
- Kotlin Special Classes and Features (1)
- Kotlin Scoping Functions (1)

#### Kotlin Memory Management (~13 Q&As)
**Subtopics**: `kotlin`, `memory`

DB Themes:
- Kotlin Memory Management (13)

#### Kotlin Performance (~1 Q&A)
**Subtopics**: `kotlin`, `performance`

DB Themes:
- Kotlin Performance Optimization (1)

#### Kotlin Data Structures (~1 Q&A)
**Subtopics**: `kotlin`, `data-structures`

DB Themes:
- Kotlin Data Structures (1)

#### Kotlin Dependency Injection (~1 Q&A)
**Subtopics**: `kotlin`, `di`

DB Themes:
- Kotlin Dependency Injection (1)

#### Kotlin Architecture (~1 Q&A)
**Subtopics**: `kotlin`, `architecture`

DB Themes:
- Kotlin Architecture Patterns (1)

#### Kotlin Data Processing (~2 Q&As)
**Subtopics**: `kotlin`, `data-processing`

DB Themes:
- Data Processing in Kotlin (1)
- Data Processing and Transformation (1)

#### Java Basics (~20 Q&As)
**Subtopics**: `java`, `jvm`

DB Themes:
- Java Basics (9)
- Basic Java (2)
- Basic Java Syntax (2)
- Java Fundamentals (1)
- Java Object Methods (1)
- Java Object Initialization (1)
- Java Standart Library (1)

#### Java-Kotlin Interoperability (~3 Q&As)
**Subtopics**: `kotlin`, `java`, `interop`

DB Themes:
- Kotlin and Java Interoperability (2)
- Java-Kotlin Interoperability (1)

#### Functional Programming (~3 Q&As)
**Subtopics**: `functional-programming`

DB Themes:
- Functional Programming Kotlin/Java (3)
- Functional Programming Concepts (1)

---

### CONCURRENCY (topic: concurrency) - ~80 Q&As
**Folder**: `60-CompSci/`

#### Kotlin Coroutines (~55 Q&As)
**Subtopics**: `coroutines`, `kotlin`

DB Themes:
- Kotlin Coroutines (53)
- Kotlin Concurrency (2)
- Kotlin Coroutines vs RxJava (1)
- Kotlin Concurrency and Memory Management (1)

#### General Concurrency (~15 Q&As)
**Subtopics**: `threads`, `synchronization`

DB Themes:
- Concurrency in Kotlin/JVM (2)
- Concurrency in Kotlin/Java (1)
- Concurrency in Kotlin/Android (1)
- Concurrency Issues (2)
- Concurrency and Thread Safety (1)
- Concurrency Models (1)
- Concurrency (1)

#### Java Concurrency (~1 Q&A)
**Subtopics**: `java`, `threads`

DB Themes:
- Java Concurrency (1)

#### Reactive Programming (~5 Q&As)
**Subtopics**: `rxjava`, `reactive`

DB Themes:
- Reactive Programming (3)
- RxJava Operators (1)
- RxJava Observables (1)

---

### DATA-STRUCTURES (topic: data-structures) - ~10 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Data Structures (6)
- Data Structures Performance (2)
- Data Structures Basics (1)
- Data Structures and Algorithms (1)

---

### DATABASES (topic: databases) - ~15 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- SQL and Database Operations (2)
- Database Querying (1)
- Database Query Optimization (1)
- Database Management (1)
- Database Design (1)
- Database Concepts (1)
- Оптимизация запросов к БД (1)

---

### ARCHITECTURE-PATTERNS (topic: architecture-patterns) - ~12 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Software Design Principles (5)
- Software Architecture Principles (1)
- Software Architecture Design (1)
- Dependency Injection Patterns (1)
- State Management Patterns (1)
- State Management Kotlin (1)

---

### PERFORMANCE (topic: performance) - ~5 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Performance Optimization (2)
- Memory Management (3)
- Data Loading Optimization (1)

---

### TESTING (topic: testing) - ~1 Q&A
**Folder**: `60-CompSci/`

DB Themes:
- Testing (1) (already counted in Android Testing)

---

### SECURITY (topic: security) - ~1 Q&A
**Folder**: `60-CompSci/`

DB Themes:
- Security Principles (1)

---

### DEVOPS-CI-CD (topic: devops-ci-cd) - ~10 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Version Control Strategies (4)
- Git Workflow (2)
- Git Basics (1)

---

### NETWORKING (topic: networking) - ~1 Q&A
**Folder**: `60-CompSci/`

DB Themes:
- Networking (1)

---

### OPERATING-SYSTEMS (topic: operating-systems) - ~2 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Operating System Scheduling (1)
- Computer Architecture Basics (1)

---

### UI-UX-ACCESSIBILITY (topic: ui-ux-accessibility) - ~1 Q&A
**Folder**: `60-CompSci/`

DB Themes:
- User Interface Design (1)

---

### SOFTWARE DEVELOPMENT / CS (topic: cs) - ~10 Q&As
**Folder**: `60-CompSci/`

DB Themes:
- Software Development Principles (1)
- Software Development Practices (1)
- Software Development Management (1)
- General Programming Principles (1)
- Code Quality (1)
- Library Selection Criteria (1)
- Library Development (1)
- Team Management (1)
- Cross-Platform Development (1)
- Error Handling in Kotlin (1)
- Data Handling in Android/Kotlin (1)
- Data Storage Techniques (1)

---

## Summary Statistics

| Vault Topic | Estimated Q&As | Folder | Notes |
|-------------|----------------|--------|-------|
| android | ~450 | 40-Android/ | Largest category, use Android subtopics |
| programming-languages | ~280 | 60-CompSci/ | Mostly Kotlin, some Java |
| concurrency | ~80 | 60-CompSci/ | Coroutines, threading, RxJava |
| data-structures | ~10 | 60-CompSci/ | |
| databases | ~15 | 60-CompSci/ | SQL, query optimization |
| architecture-patterns | ~12 | 60-CompSci/ | Design principles, DI |
| performance | ~5 | 60-CompSci/ | |
| devops-ci-cd | ~10 | 60-CompSci/ | Git, version control |
| security | ~1 | 60-CompSci/ | |
| testing | ~1 | 60-CompSci/ | |
| networking | ~1 | 60-CompSci/ | |
| operating-systems | ~2 | 60-CompSci/ | |
| ui-ux-accessibility | ~1 | 60-CompSci/ | |
| cs | ~10 | 60-CompSci/ | General software development |

**Total**: ~878 Q&As (some themes may have overlap or miscounts)

---

## Android Subtopic Detection Rules

Use DB tags and theme to determine Android subtopics:

| Keyword in theme/tags | Android Subtopic |
|-----------------------|------------------|
| UI, compose, view, widget, navigation | ui-compose, ui-views, ui-navigation |
| lifecycle, activity, fragment | lifecycle, activity, fragment |
| service, background | service, background-execution |
| coroutines (in Android context) | coroutines |
| room, database, storage | room, datastore, files-media |
| network, retrofit, http | networking-http |
| performance, memory, startup | performance-startup, performance-memory |
| testing | testing-unit, testing-instrumented |
| gradle, build | gradle, build-variants |
| dependency injection, dagger, hilt | di-hilt |
| architecture, mvvm, mvi | architecture-mvvm, architecture-mvi |
| intent, broadcast | intents-deeplinks, broadcast-receiver |
| security, permissions | permissions, keystore-crypto |

---

## Question Kind Detection

Based on DB tags and content:

- **coding**: If question asks to implement/write code
- **theory**: If question asks "what is", "explain", "difference between"
- **android**: If Android-specific question (use this for most Android Q&As)

---

## Difficulty Mapping

DB doesn't have difficulty field. Use heuristics:

- **easy**: Basic concepts, definitions, simple differences
- **medium**: Complex explanations, multi-part answers, comparisons
- **hard**: Advanced topics, performance optimization, architecture decisions

Default to **medium** for most Q&As, adjust during import based on answer complexity.

---

## Next Steps

1. ✅ Create this mapping document
2. ⏭️ Design import strategy
3. ⏭️ Build import script using this mapping
