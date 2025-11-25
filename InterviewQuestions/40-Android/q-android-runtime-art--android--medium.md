---
id: android-297
title: Android Runtime (ART) / Android Runtime
aliases: [Android Runtime, Android Runtime (ART)]
topic: android
subtopics:
  - performance-memory
  - processes
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android-basics
  - q-android-app-lag-analysis--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-android-runtime-internals--android--hard
  - q-dalvik-vs-art-runtime--android--medium
  - q-optimize-memory-usage-android--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-memory, android/processes, compilation, difficulty/medium, gc, runtime]
sources: []
date created: Saturday, November 1st 2025, 1:02:46 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Что такое Android Runtime (ART) и чем он отличается от Dalvik?

# Question (EN)
> What is Android Runtime (ART) and how does it differ from Dalvik?

## Ответ (RU)

**Android Runtime (ART)** — среда выполнения приложений Android, отвечающая за компиляцию, запуск кода и управление памятью. ART заменил Dalvik VM и в современных версиях Android использует гибридный подход (интерпретация + JIT + profile-guided AOT) для баланса между производительностью, временем установки и размером кода.

Исторически:
- Ранний ART (Android 5–6) делал в основном AOT-компиляцию при установке (dex2oat).
- Начиная с Android 7+, используется комбинация интерпретатора, JIT и последующей AOT-оптимизации на основе профилей.

### Гибридная Компиляция

```kotlin
// ✅ Установка: baseline profile → быстрая установка ключевых путей
class HotPath {
    fun frequentOperation() {
        // JIT профилирует "горячие" методы и может их компилировать
        processData()
    }
}

// 🔍 Редко используемый код может выполняться интерпретатором или JIT-компилироваться при необходимости
class ColdPath {
    fun rareOperation() { cleanup() }
}
```

Типичный жизненный цикл компиляции в современных версиях Android:
1. **Установка** — минимальная AOT-компиляция критических путей по baseline-профилям для быстрого первого запуска.
2. **Выполнение** — интерпретация + JIT-профилирование и JIT-компиляция активно используемого кода.
3. **Фоновая оптимизация** — profile-guided AOT-компиляция во время зарядки и простоя, с учетом реальных профилей использования.

### Улучшенная Сборка Мусора

```kotlin
// ✅ Concurrent / concurrent-copying / generational GC минимизирует паузы
class MemoryExample {
    private val largeList = mutableListOf<Bitmap>()

    fun allocateMemory() {
        // Значительная часть работы GC выполняется конкурентно с приложением
        repeat(1000) { largeList.add(createBitmap()) }
    }
}

// 🔍 В Dalvik были stop-the-world паузы и менее эффективные алгоритмы;
// ART использует более современные конкурентные сборщики и лучше оптимизирует паузы.
```

### DEX Формат

```kotlin
// ✅ DEX: все классы в одном контейнере
val dexFormat = """
    Header
    StringIds → все строки
    TypeIds → все типы
    MethodIds → все методы
    ClassDefs → определения классов
"""

// 🔍 DEX формат используется и Dalvik, и ART.
// ART дополнительно компилирует DEX в нативный код (oat/odex/art) для выполнения.

// ❌ В обычной JVM: отдельный .class для каждого класса (Java bytecode)
```

### ART Vs Dalvik

| Характеристика | Dalvik | ART |
|----------------|--------|-----|
| Компиляция | В основном JIT во время выполнения (DEX-интерпретатор + JIT) | Интерпретатор + JIT + profile-guided AOT (в ранних версиях преимущественно AOT) |
| Запуск приложения | Обычно медленнее | Обычно быстрее (AOT/JIT оптимизации и baseline profiles) |
| Использование памяти | Меньше (меньше нативного кода) | Больше (из-за скомпилированного кода и структур для профилей) |
| GC | Менее продвинутые алгоритмы, заметные STW-паузы | Более эффективные и конкурентные сборщики, короче паузы |
| Батарея | Выше накладные расходы на JIT/GC в ряде сценариев | Как правило, эффективнее за счет AOT/JIT на профилях и улучшенного GC |

### Проверка Runtime

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Современные Android: обычно "ART"
    // ❌ Старые устройства (Android 4.4 и ниже): "Dalvik"
}

// ART-ориентированные меры предосторожности
@Keep // Предотвращает удаление/обфускацию при ProGuard/R8; важно, если используется reflection и др.
class CriticalPath {
    fun criticalOperation() { /* критичный код, не должен быть удален */ }
}
```

## Дополнительные Вопросы (RU)

- Как baseline profiles влияют на время установки и первый запуск приложения?
- В каких случаях AOT-компиляция может критично увеличить размер APK?
- Почему concurrent / concurrent-copying GC эффективнее классического mark-and-sweep для мобильных приложений?
- Как профилировать JIT и поведение runtime для выявления кандидатов на AOT-оптимизацию?
- Какие методы и классы следует маркировать `@Keep` для предотвращения проблем с reflection после R8?

## Ссылки (RU)

- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/baselineprofiles
- [[c-android-basics]]

## Связанные Вопросы (RU)

### Предпосылки
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Связанные
- [[q-android-app-lag-analysis--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-build-optimization--android--medium]]

## Answer (EN)

**Android Runtime (ART)** is the application runtime for Android, responsible for compilation, code execution, and memory management. ART replaced the Dalvik VM and, in modern Android versions, uses a hybrid approach (interpreter + JIT + profile-guided AOT) to balance performance, install time, and code size.

Historically:
- Early ART (Android 5–6) primarily performed AOT compilation at install time (dex2oat).
- From Android 7+ onward, ART combines an interpreter, JIT, and subsequent profile-guided AOT optimization.

### Hybrid Compilation

```kotlin
// ✅ Install: baseline profile → fast install of key hot paths
class HotPath {
    fun frequentOperation() {
        // JIT profiles "hot" methods and may compile them
        processData()
    }
}

// 🔍 Rarely used code may run in the interpreter or be JIT-compiled if it becomes hot
class ColdPath {
    fun rareOperation() { cleanup() }
}
```

Typical compilation lifecycle on modern Android:
1. **Install** — minimal AOT compilation of critical paths using baseline profiles to keep install fast.
2. **Runtime** — interpretation + JIT profiling and JIT compilation of actively used code.
3. **Background optimization** — profile-guided AOT compilation while charging and idle, based on real-world usage profiles.

### Improved Garbage Collection

```kotlin
// ✅ Concurrent / concurrent-copying / generational GC minimizes pauses
class MemoryExample {
    private val largeList = mutableListOf<Bitmap>()

    fun allocateMemory() {
        // A significant portion of GC work runs concurrently with the app
        repeat(1000) { largeList.add(createBitmap()) }
    }
}

// 🔍 Dalvik had noticeable stop-the-world pauses and less advanced algorithms;
// ART introduces more modern concurrent collectors with shorter pauses.
```

### DEX Format

```kotlin
// ✅ DEX: all classes in a single container
val dexFormat = """
    Header
    StringIds → all strings
    TypeIds → all types
    MethodIds → all methods
    ClassDefs → class definitions
"""

// 🔍 The DEX format is used by both Dalvik and ART.
// ART additionally compiles DEX into native code (oat/odex/art) for execution.

// ❌ On a standard JVM: separate .class file per class (Java bytecode)
```

### ART Vs Dalvik

| Feature | Dalvik | ART |
|---------|--------|-----|
| Compilation | Mostly JIT at runtime (DEX interpreter + JIT) | Interpreter + JIT + profile-guided AOT (early ART was mostly AOT) |
| App startup | Typically slower | Typically faster (AOT/JIT optimizations and baseline profiles) |
| Memory usage | Lower (less native compiled code) | Higher (compiled code + profiling/optimization metadata) |
| GC | Less advanced, more noticeable STW pauses | More efficient, concurrent collectors with shorter pauses |
| Battery | Higher overhead from JIT/GC in some scenarios | Generally more efficient due to profile-guided AOT/JIT and better GC |

### Runtime Detection

```kotlin
fun detectRuntime(): String {
    return System.getProperty("java.vm.name") ?: "Unknown"
    // ✅ Modern Android devices typically report "ART"
    // ❌ Older devices (Android 4.4 and below) report "Dalvik"
}

// ART-oriented safeguards
@Keep // Prevents removal/obfuscation by ProGuard/R8; important when using reflection etc.
class CriticalPath {
    fun criticalOperation() { /* critical code that must not be stripped */ }
}
```

## Follow-ups

- How do baseline profiles affect install time and first app launch?
- In which cases can AOT compilation significantly increase APK size?
- Why are concurrent / concurrent-copying GCs more effective than classic mark-and-sweep for mobile apps?
- How to profile JIT and runtime behavior to identify candidates for AOT optimization?
- Which methods and classes should be marked with `@Keep` to avoid reflection issues after R8?

## References

- https://source.android.com/docs/core/runtime
- https://developer.android.com/topic/performance/baselineprofiles
- [[c-android-basics]]

## Related Questions

### Prerequisites
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related
- [[q-android-app-lag-analysis--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
- [[q-android-build-optimization--android--medium]]
