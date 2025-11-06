---
id: android-412
title: JIT vs AOT Compilation / JIT vs AOT компиляция
aliases: [Ahead-Of-Time, Android Runtime, ART, JIT vs AOT Compilation, JIT vs AOT компиляция, Just-In-Time]
topic: android
subtopics: [gradle, performance-startup, profiling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, c-performance-optimization, q-android-build-optimization--android--medium, q-app-startup-optimization--android--medium, q-kapt-vs-ksp--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/gradle, android/performance-startup, android/profiling, aot, art, baseline-profiles, compilation, difficulty/medium, jit]
sources: []
---

# Вопрос (RU)

> В чём разница между JIT и AOT компиляцией в Android? Как Android использует обе стратегии?

# Question (EN)

> What are the differences between JIT and AOT compilation in Android? How does Android use both strategies?

---

## Ответ (RU)

Android использует гибридный подход, сочетающий **JIT** (Just-In-Time) и **AOT** (Ahead-Of-Time) компиляцию для баланса между производительностью и скоростью установки.

### JIT (Just-In-Time)

**Принцип работы:**
- Байткод интерпретируется при выполнении
- Горячий код компилируется в runtime
- Результат хранится в памяти (теряется при перезапуске)

```kotlin
class JITExample {
    fun processData(numbers: List<Int>): Int {
        // Первые вызовы: ~1000ns (интерпретация)
        // После 10-100 вызовов: JIT компиляция
        // Последующие вызовы: ~100ns (нативный код)
        return numbers.sum()
    }
}
```

**Преимущества:**
- ✅ Быстрая установка (5 сек)
- ✅ Малый размер (~20 MB)
- ✅ Адаптивная оптимизация под реальное использование

**Недостатки:**
- ❌ Прогрев при первых запусках (~1500 ms)
- ❌ Runtime overhead (профилирование, компиляция)
- ❌ Теряется при рестарте приложения

### AOT (Ahead-Of-Time)

**Принцип работы:**
- Компиляция DEX → машинный код при установке (dex2oat)
- OAT файл хранится на диске
- Приложение запускается сразу с нативным кодом

```kotlin
class AOTExample {
    fun processData(numbers: List<Int>): Int {
        // Все вызовы: ~100ns с первого запуска
        // Скомпилировано при установке
        return numbers.sum()
    }
}
```

**Преимущества:**
- ✅ Мгновенная производительность с первого запуска
- ✅ Предсказуемое время выполнения
- ✅ Ниже расход батареи (нет runtime компиляции)

**Недостатки:**
- ❌ Медленная установка (45 сек, 9x медленнее)
- ❌ Большой размер (~60 MB, 2x больше)
- ❌ Компилирует весь код, даже неиспользуемый

### Гибридный Подход (Android 7+)

**Profile-Guided Optimization:**

```
Установка → Быстро (только DEX)
    ↓
Первый запуск → JIT + профилирование горячих путей
    ↓
Фон (устройство на зарядке) → AOT компиляция только горячего кода
    ↓
Последующие запуски → Быстро (оптимизированный нативный код)
```

```kotlin
// Профиль сохраняется в:
// /data/misc/profiles/cur/0/com.example.app/primary.prof

class ProfileGuidedExample {
    // Горячий метод → AOT компиляция в фоне
    fun frequentOperation() { /* ... */ }

    // Холодный метод → остаётся интерпретированным
    fun rareDebugOperation() { /* ... */ }
}
```

**Режимы компиляции (adb):**

```bash
# Profile-guided (по умолчанию)
adb shell cmd package compile -m speed-profile com.example.app

# Полная AOT компиляция
adb shell cmd package compile -m speed com.example.app

# Сброс компиляции
adb shell cmd package compile --reset com.example.app
```

### Baseline Profiles (Android 9+)

Предгенерированные профили, поставляемые с APK для оптимизации критических путей при установке.

```kotlin
// app/src/main/baseline-prof.txt
class BaselineProfileExample {
    // Метод из baseline-prof.txt → компилируется при установке
    fun criticalStartupMethod() {
        // Быстро с первого запуска
    }
}

// Проверка статуса:
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    Log.d("Compilation", """
        Has profile: ${status.hasReferenceProfile()}
        Compiled with profile: ${status.isCompiledWithProfile}
    """.trimIndent())
}
```

**Улучшение производительности:**
- Cold start: ~33% быстрее
- Warm start: ~38% быстрее

### Сравнение Подходов

| Аспект | JIT | AOT | Hybrid (Profile-Guided) |
|--------|-----|-----|------------------------|
| Установка | 5s | 45s | 5s |
| Первый запуск | 1500ms | 700ms | 850ms |
| Оптим. запуск | 800ms | 700ms | 750ms |
| Размер | 20MB | 60MB | 35MB |
| Батарея | Выше | Ниже | Низкий |
| Обновления | Быстро | Медленно | Быстро |

### Стратегия Выбора

```kotlin
fun chooseStrategy(appType: AppType): Strategy {
    return when (appType) {
        Gaming -> Strategy.FullAOT // Стабильные фреймтаймы
        SocialMedia -> Strategy.ProfileGuided // Частые обновления
        Utility -> Strategy.BaselineProfile // Быстрый первый запуск
        Enterprise -> Strategy.FullAOT // Стабильность > скорость обновлений
    }
}
```

---

## Answer (EN)

Android uses a hybrid approach combining **JIT** (Just-In-Time) and **AOT** (Ahead-Of-Time) compilation for optimal balance between performance and install speed.

### JIT (Just-In-Time)

**How it works:**
- Bytecode interpreted at runtime
- Hot code compiled on-the-fly
- Results cached in memory (lost on restart)

```kotlin
class JITExample {
    fun processData(numbers: List<Int>): Int {
        // First calls: ~1000ns (interpreted)
        // After 10-100 calls: JIT compilation triggered
        // Subsequent calls: ~100ns (native code)
        return numbers.sum()
    }
}
```

**Advantages:**
- ✅ Fast installation (5 sec)
- ✅ Small footprint (~20 MB)
- ✅ Adaptive optimization based on actual usage

**Disadvantages:**
- ❌ Warm-up time on first runs (~1500 ms)
- ❌ Runtime overhead (profiling, compilation)
- ❌ Lost on app restart

### AOT (Ahead-Of-Time)

**How it works:**
- DEX → native code compilation at install time (dex2oat)
- OAT file stored on disk
- App launches with pre-compiled native code

```kotlin
class AOTExample {
    fun processData(numbers: List<Int>): Int {
        // All calls: ~100ns from first launch
        // Compiled during installation
        return numbers.sum()
    }
}
```

**Advantages:**
- ✅ Instant performance from first launch
- ✅ Predictable execution times
- ✅ Lower battery usage (no runtime compilation)

**Disadvantages:**
- ❌ Slow installation (45 sec, 9x slower)
- ❌ Large footprint (~60 MB, 2x larger)
- ❌ Compiles all code, even unused

### Hybrid Approach (Android 7+)

**Profile-Guided Optimization:**

```
Installation → Fast (DEX only)
    ↓
First Run → JIT + profiling hot paths
    ↓
Background (device charging) → AOT compile hot code only
    ↓
Subsequent Runs → Fast (optimized native code)
```

```kotlin
// Profile stored at:
// /data/misc/profiles/cur/0/com.example.app/primary.prof

class ProfileGuidedExample {
    // Hot method → AOT compiled in background
    fun frequentOperation() { /* ... */ }

    // Cold method → remains interpreted
    fun rareDebugOperation() { /* ... */ }
}
```

**Compilation modes (adb):**

```bash
# Profile-guided (default)
adb shell cmd package compile -m speed-profile com.example.app

# Full AOT compilation
adb shell cmd package compile -m speed com.example.app

# Reset compilation
adb shell cmd package compile --reset com.example.app
```

### Baseline Profiles (Android 9+)

Pre-generated profiles shipped with APK to optimize critical paths at install time.

```kotlin
// app/src/main/baseline-prof.txt
class BaselineProfileExample {
    // Method listed in baseline-prof.txt → compiled at install
    fun criticalStartupMethod() {
        // Fast from first launch
    }
}

// Check compilation status:
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    Log.d("Compilation", """
        Has profile: ${status.hasReferenceProfile()}
        Compiled with profile: ${status.isCompiledWithProfile}
    """.trimIndent())
}
```

**Performance improvements:**
- Cold start: ~33% faster
- Warm start: ~38% faster

### Comparison

| Aspect | JIT | AOT | Hybrid (Profile-Guided) |
|--------|-----|-----|------------------------|
| Install Time | 5s | 45s | 5s |
| First Run | 1500ms | 700ms | 850ms |
| Optimized Run | 800ms | 700ms | 750ms |
| Storage | 20MB | 60MB | 35MB |
| Battery | Higher | Lower | Low |
| Updates | Fast | Slow | Fast |

### Strategy Selection

```kotlin
fun chooseStrategy(appType: AppType): Strategy {
    return when (appType) {
        Gaming -> Strategy.FullAOT // Consistent frame times
        SocialMedia -> Strategy.ProfileGuided // Frequent updates
        Utility -> Strategy.BaselineProfile // Fast first impression
        Enterprise -> Strategy.FullAOT // Stability > update speed
    }
}
```

---

## Follow-ups

1. How do baseline profiles differ from runtime-generated profiles?
2. What triggers background AOT compilation (dex2oat) in profile-guided mode?
3. How can you force full AOT compilation for performance testing?
4. What are the trade-offs between `speed` and `speed-profile` compilation modes?
5. How does R8/ProGuard optimization interact with JIT/AOT compilation?

## References

- [[c-performance-optimization]]
- [[c-gradle]]
- [Android Runtime (ART) and Dalvik](https://source.android.com/docs/core/runtime)
- [Baseline Profiles Guide](https://developer.android.com/topic/performance/baselineprofiles)
- [ProfileInstaller Library](https://developer.android.com/jetpack/androidx/releases/profileinstaller)

## Related Questions

### Prerequisites

- [[q-gradle-basics--android--easy]]
- [[q-performance-optimization-android--android--medium]]

### Related

- [[q-kapt-vs-ksp--android--medium]]
- [[q-app-startup-optimization--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-macrobenchmark-startup--android--medium]]

### Advanced

- [[q-compose-performance-optimization--android--hard]]
- [[q-fix-slow-app-startup-legacy--android--hard]]
