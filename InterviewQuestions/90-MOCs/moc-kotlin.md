---
id: ivm-20251012-140200
title: Kotlin — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/kotlin]
date created: Sunday, October 12th 2025, 1:07:06 pm
date modified: Sunday, October 26th 2025, 8:53:02 pm
---

# Kotlin — Map of Content

## Overview
This MOC covers Kotlin language features, syntax, coroutines, Flow, collection operations, advanced language features, standard library functions, interoperability with Java, and best practices for Kotlin development.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Coroutines

**Key Questions** (Curated Learning Path):

#### Fundamentals
- [[q-what-is-coroutine--kotlin--easy]] - What is a coroutine and how does it work?
- [[q-suspend-functions-basics--kotlin--easy]] - Understanding suspend functions
- [[q-coroutines-vs-threads--programming-languages--medium]] - Coroutines vs Threads comparison
- [[q-kotlin-coroutines-overview--programming-languages--medium]] - Comprehensive coroutine overview

#### Coroutine Builders & Scope
- [[q-coroutine-builders-basics--kotlin--easy]] - launch, async, runBlocking basics
- [[q-coroutine-scope-basics--kotlin--easy]] - Understanding CoroutineScope
- [[q-lifecyclescope-viewmodelscope--kotlin--medium]] - Android-specific scopes
- [[q-coroutinescope-vs-coroutinecontext--kotlin--medium]] - Scope vs Context differences

#### Context & Dispatchers
- [[q-coroutine-context-detailed--kotlin--hard]] - Deep dive into CoroutineContext
- [[q-dispatchers-types--kotlin--medium]] - Main, IO, Default, Unconfined dispatchers
- [[q-dispatchers-io-vs-default--kotlin--medium]] - When to use IO vs Default
- [[q-coroutine-dispatchers--kotlin--medium]] - Dispatcher selection strategies

#### Structured Concurrency
- [[q-structured-concurrency-kotlin--kotlin--medium]] - Principles of structured concurrency
- [[q-coroutine-exception-handling--kotlin--medium]] - Exception handling in coroutines
- [[q-coroutinescope-supervisorscope--kotlin--medium]] - CoroutineScope vs SupervisorScope
- [[q-coroutine-cancellation--kotlin--medium]] - Cancellation and cleanup

#### Advanced Patterns
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Parallel API calls
- [[q-deferred-async-patterns--kotlin--medium]] - Async/await patterns
- [[q-actor-pattern--kotlin--hard]] - Actor model for concurrency
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced concurrency patterns

#### Testing & Debugging
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing coroutines in ViewModels
- [[q-test-dispatcher-types--kotlin--medium]] - Test dispatchers (TestDispatcher, StandardTestDispatcher)
- [[q-coroutine-virtual-time--kotlin--medium]] - Virtual time in tests
- [[q-debugging-coroutines-techniques--kotlin--medium]] - Debugging strategies
- [[q-coroutine-profiling--kotlin--hard]] - Performance profiling

**All Coroutine Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "coroutines") OR contains(subtopics, "coroutines") OR contains(file.name, "coroutine")
SORT difficulty ASC, file.name ASC
```

### Flow & Reactive Programming

**Key Questions** (Curated Learning Path):

#### Flow Fundamentals
- [[q-kotlin-flow-basics--kotlin--medium]] - Introduction to Kotlin Flow
- [[q-flow-basics--kotlin--easy]] - Flow basics and creation
- [[q-flow-operators-map-filter--kotlin--medium]] - Basic operators: map, filter, transform
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData

#### Hot Vs Cold Flows
- [[q-hot-cold-flows--kotlin--medium]] - Cold Flow, SharedFlow, StateFlow differences
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow vs SharedFlow detailed
- [[q-statein-sharein-flow--kotlin--medium]] - stateIn and shareIn operators

#### Flow Operators
- [[q-flow-operators--kotlin--medium]] - Comprehensive operator guide
- [[q-flow-time-operators--kotlin--medium]] - debounce, throttle, delay, timeout
- [[q-catch-operator-flow--kotlin--medium]] - catch operator for error handling
- [[q-flow-completion-oncompletion--kotlin--medium]] - onCompletion and finalization
- [[q-instant-search-flow-operators--kotlin--medium]] - Building instant search with Flow

#### Advanced Flow
- [[q-channelflow-callbackflow-flow--kotlin--medium]] - channelFlow vs callbackFlow
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling strategies
- [[q-fan-in-fan-out--kotlin--hard]] - Fan-in and fan-out patterns
- [[q-channel-flow-comparison--kotlin--medium]] - Channels vs Flow comparison

#### Error Handling
- [[q-flow-exception-handling--kotlin--medium]] - Exception handling in Flow
- [[q-retry-operators-flow--kotlin--medium]] - retry, retryWhen operators

#### Testing
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing hot Flows
- [[q-turbine-flow-testing--kotlin--medium]] - Using Turbine for Flow testing

**All Flow Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "flow") OR contains(subtopics, "flow") OR contains(file.name, "flow") OR contains(tags, "reactive")
SORT difficulty ASC, file.name ASC
```

### Collections & Sequences

**Key Questions**:

#### Basics
- [[q-kotlin-collections--kotlin--medium]] - Kotlin collection types overview
- [[q-list-set-map-differences--programming-languages--easy]] - List, Set, Map differences
- [[q-collection-implementations--programming-languages--easy]] - Implementation details
- [[q-array-vs-list-kotlin--kotlin--easy]] - Array vs List in Kotlin

#### Operations
- [[q-associatewith-vs-associateby--kotlin--easy]] - associateWith vs associateBy
- [[q-kotlin-fold-reduce--kotlin--medium]] - fold, reduce, and accumulation
- [[q-kotlin-collections-operations--kotlin--medium]] - map, filter, flatMap, groupBy

#### Sequences
- [[q-sequences-vs-collections--kotlin--medium]] - When to use sequences
- [[q-sequences-lazy-evaluation--kotlin--medium]] - Lazy evaluation in sequences

**All Collection Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "collections") OR contains(tags, "sequences") OR contains(subtopics, "collections") OR contains(file.name, "collection") OR contains(file.name, "sequence")
SORT difficulty ASC, file.name ASC
```

### Channels & Concurrency Primitives

**Key Questions**:

#### Channel Basics
- [[q-channels-basics-types--kotlin--medium]] - Channel types and basics
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow comparison
- [[q-channel-buffering-strategies--kotlin--hard]] - Buffering strategies

#### Advanced Patterns
- [[q-channel-pipelines--kotlin--hard]] - Building channel pipelines
- [[q-produce-actor-builders--kotlin--medium]] - produce and actor builders
- [[q-select-expression-channels--kotlin--hard]] - select expressions for channels

#### Synchronization
- [[q-atomic-vs-synchronized--kotlin--medium]] - Atomic operations vs synchronized
- [[q-mutex-vs-semaphore--kotlin--medium]] - Mutex and Semaphore usage

### Language Features & Syntax

**Key Questions**:

#### Inline & Reified
- [[q-kotlin-inline-functions--kotlin--medium]] - Inline functions comprehensive guide
- [[q-inline-function-limitations--kotlin--medium]] - Limitations and caveats
- [[q-reified-type-parameters--kotlin--medium]] - Reified type parameters
- [[q-inline-value-classes-performance--kotlin--medium]] - Inline value classes

#### Extensions
- [[q-kotlin-extensions--kotlin--easy]] - Extension functions and properties
- [[q-extensions-in-java--programming-languages--medium]] - How extensions work in Java
- [[q-property-delegates--kotlin--medium]] - Property delegation

#### Operators & Functions
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operator overloading
- [[q-kotlin-higher-order-functions--kotlin--medium]] - Higher-order functions
- [[q-by-keyword-function-call--programming-languages--easy]] - by keyword usage

#### Properties & Initialization
- [[q-kotlin-properties--kotlin--easy]] - Kotlin properties overview
- [[q-kotlin-val-vs-var--kotlin--easy]] - val vs var differences
- [[q-kotlin-init-block--kotlin--easy]] - Init blocks and initialization
- [[q-kotlin-constructors--kotlin--easy]] - Primary and secondary constructors
- [[q-lazy-vs-lateinit--kotlin--medium]] - lazy vs lateinit properties

**All Language Feature Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "language-features") OR contains(tags, "syntax") OR contains(tags, "inline") OR contains(tags, "lambdas") OR contains(tags, "extensions")
SORT difficulty ASC, file.name ASC
```

### Object-Oriented Features

**Key Questions**:

#### Classes & Objects
- [[q-object-companion-object--kotlin--medium]] - Object declarations and companion objects
- [[q-sealed-classes--kotlin--medium]] - Sealed classes and hierarchies
- [[q-kotlin-sealed-when-exhaustive--kotlin--medium]] - Exhaustive when with sealed classes
- [[q-value-classes-inline-classes--kotlin--medium]] - Value classes (inline classes)
- [[q-data-class-requirements--programming-languages--medium]] - Data class requirements

#### Abstract Classes & Interfaces
- [[q-abstract-class-vs-interface--kotlin--medium]] - Abstract class vs Interface
- [[q-kotlin-java-abstract-differences--programming-languages--medium]] - Kotlin vs Java abstractions

#### Delegation
- [[q-kotlin-delegation-detailed--kotlin--medium]] - Class delegation with 'by'
- [[q-property-delegates--kotlin--medium]] - Property delegation patterns

#### Visibility & Access
- [[q-access-modifiers--programming-languages--medium]] - Kotlin access modifiers
- [[q-prohibit-object-creation--programming-languages--easy]] - Private constructors

**All OOP Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "oop") OR contains(tags, "inheritance") OR contains(tags, "abstract-class") OR contains(tags, "interface") OR contains(file.name, "object") OR contains(file.name, "class")
SORT difficulty ASC, file.name ASC
```

### Functional Programming

**Key Questions**:

#### Higher-Order Functions & Lambdas
- [[q-kotlin-higher-order-functions--kotlin--medium]] - Higher-order functions overview
- [[q-kotlin-lambda-expressions--kotlin--medium]] - Lambda expressions and syntax
- [[q-kotlin-fold-reduce--kotlin--medium]] - fold, reduce, and functional accumulation
- [[q-kotlin-sam-interfaces--kotlin--medium]] - SAM (Single Abstract Method) interfaces

#### Immutability & Collections
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Immutable collections in Kotlin

**All Functional Programming Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "functional-programming") OR contains(tags, "higher-order-functions") OR contains(tags, "pure-functions") OR contains(tags, "immutability")
SORT difficulty ASC, file.name ASC
```

### Standard Library & Operators

**Key Questions**:

#### Scope Functions
- [[q-kotlin-scope-functions--kotlin--medium]] - Scope functions (let, run, with, apply, also)
- [[q-kotlin-scope-functions-advanced--kotlin--medium]] - Advanced scope function patterns
- [[q-kotlin-let-function--programming-languages--easy]] - let function usage

#### Operators
- [[q-kotlin-operator-overloading--kotlin--medium]] - Operator overloading
- [[q-equality-operators-kotlin--kotlin--easy]] - Equality operators (== vs ===)
- [[q-infix-functions--kotlin--medium]] - Infix function notation

**All Standard Library Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "stdlib") OR contains(tags, "operators") OR contains(tags, "scope-functions") OR contains(file.name, "operator")
SORT difficulty ASC, file.name ASC
```

### Concurrency & Async Programming

**Key Questions** (Beyond Coroutines section):

#### Synchronization Primitives
- [[q-atomic-vs-synchronized--kotlin--medium]] - Atomic operations vs synchronized blocks
- [[q-mutex-vs-semaphore--kotlin--medium]] - Mutex and Semaphore for thread safety

#### Patterns & Advanced Topics
- [[q-actor-pattern--kotlin--hard]] - Actor pattern for concurrency
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Parallel API calls with coroutines
- [[q-deferred-async-patterns--kotlin--medium]] - Deferred and async patterns

**All Concurrency Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "async") OR contains(tags, "concurrency") OR contains(tags, "channels") OR contains(tags, "dispatchers") OR contains(tags, "cancellation")
SORT difficulty ASC, file.name ASC
```

### Serialization & Data Processing

**Key Questions**:

#### Serialization Basics
- [[q-serialization-basics--programming-languages--medium]] - Serialization fundamentals

**All Serialization Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "serialization") OR contains(tags, "json") OR contains(tags, "parsing") OR contains(file.name, "serialization")
SORT difficulty ASC, file.name ASC
```

### Error Handling & Exceptions

**Key Questions**:

#### Exception Handling in Coroutines
- [[q-coroutine-exception-handling--kotlin--medium]] - Exception handling in coroutines
- [[q-coroutine-exception-handler--kotlin--medium]] - CoroutineExceptionHandler usage

#### Flow Exception Handling
- [[q-flow-exception-handling--kotlin--medium]] - Exception handling in Flow
- [[q-catch-operator-flow--kotlin--medium]] - catch operator for Flow errors
- [[q-retry-operators-flow--kotlin--medium]] - retry and retryWhen operators

**All Error Handling Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "error-handling") OR contains(tags, "exceptions") OR contains(tags, "result") OR contains(file.name, "exception")
SORT difficulty ASC, file.name ASC
```

### Interoperability

**Key Questions**:

#### Kotlin-Java Interoperability
- [[q-extensions-in-java--programming-languages--medium]] - How extension functions work in Java
- [[q-kotlin-java-abstract-differences--programming-languages--medium]] - Kotlin vs Java abstract class differences
- [[q-desugaring-android-java--kotlin--medium]] - Desugaring and Android Java compatibility

#### JVM & Compilation
- [[q-jit-compilation-definition--programming-languages--medium]] - JIT compilation in JVM
- [[q-kotlin-null-safety--kotlin--medium]] - Null safety and Java interop

**All Interoperability Questions:**
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "java-interop") OR contains(tags, "jvm") OR contains(file.name, "java")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "70-Kotlin"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "70-Kotlin"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-cs]]
- [[moc-backend]]
