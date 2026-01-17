---
id: android-412
title: JIT vs AOT Compilation / JIT vs AOT компиляция
aliases: [Ahead-Of-Time, Android Runtime, ART, JIT vs AOT Compilation, JIT vs AOT компиляция, Just-In-Time]
topic: android
subtopics: [performance-startup, profiling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-app-startup-optimization--android--medium, q-kapt-vs-ksp--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/performance-startup, android/profiling, aot, art, baseline-profiles, compilation, difficulty/medium, jit]
anki_cards:
  - slug: android-412-0-en
    front: "What is the difference between JIT and AOT compilation in Android?"
    back: |
      **JIT (Just-In-Time):**
      - Compiles hot code at runtime
      - Fast install, smaller size
      - Requires warm-up time

      **AOT (Ahead-Of-Time):**
      - Compiles before execution (dex2oat)
      - Fast from first run
      - Larger storage, slower install

      **Hybrid (Android 7+):**
      Profile-guided optimization - JIT profiles hot paths, background AOT compiles them.

      **Baseline Profiles:** Pre-generated profiles shipped with APK for faster cold starts (~30%+).
    tags:
      - android_general
      - difficulty::medium
  - slug: android-412-0-ru
    front: "В чём разница между JIT и AOT компиляцией в Android?"
    back: |
      **JIT (Just-In-Time):**
      - Компилирует горячий код во время выполнения
      - Быстрая установка, меньший размер
      - Требует прогрева

      **AOT (Ahead-Of-Time):**
      - Компилирует заранее (dex2oat)
      - Быстро с первого запуска
      - Больше места, медленнее установка

      **Гибрид (Android 7+):**
      Profile-guided optimization - JIT профилирует горячие пути, фоновый AOT компилирует их.

      **Baseline Profiles:** Предгенерированные профили в APK для быстрого cold start (~30%+).
    tags:
      - android_general
      - difficulty::medium
sources: []
---
# Вопрос (RU)

> В чём разница между JIT и AOT компиляцией в Android? Как Android использует обе стратегии?

# Question (EN)

> What are the differences between JIT and AOT compilation in Android? How does Android use both strategies?

---

## Ответ (RU)

Android использует гибридный подход, сочетающий **JIT** (Just-In-Time) и **AOT** (Ahead-Of-Time) компиляцию (через ART) для баланса между производительностью, скоростью установки и размером.

Важно: ниже приведённые числа по времени и размеру — иллюстративные, не универсальные для всех устройств и версий Android.

### JIT (Just-In-Time)

**Принцип работы:**
- DEX-байткод может исполняться интерпретатором ART.
- Часто вызываемые ("горячие") участки кода профилируются и компилируются в машинный код во время выполнения.
- Компилированный код используется для ускорения дальнейших вызовов; профили и результаты JIT-компиляции могут сохраняться и использоваться для последующей AOT-компиляции, поэтому эффект не всегда полностью "теряется" при перезапуске приложения.

```kotlin
class JITExample {
    fun processData(numbers: List<Int>): Int {
        // Пример (условные числа для иллюстрации):
        // Первые вызовы: медленнее (интерпретация / неоптимизированный код)
        // После серии вызовов: JIT-компиляция горячего пути
        // Последующие вызовы: быстрее (скомпилированный код)
        return numbers.sum()
    }
}
```

**Преимущества:**
- ✅ Быстрая установка (без полной AOT-компиляции всего кода).
- ✅ Меньший начальный размер.
- ✅ Адаптивная оптимизация под реальные сценарии использования.

**Недостатки:**
- ❌ Нужен "прогрев" при первых запусках (JIT ещё не успел оптимизировать горячие пути).
- ❌ Runtime overhead (профилирование, компиляция во время работы приложения).
- ❌ Без использования профилей и последующей AOT часть преимуществ теряется между сессиями.

### AOT (Ahead-Of-Time)

**Принцип работы:**
- Компиляция DEX → машинный код выполняется заранее (например, при установке или в отложенных задачах `dex2oat`), на основе политики системы.
- Полученные артефакты (OAT/ART/VDex) хранятся на диске и используются при запуске.
- Приложение может выполнять уже скомпилированный код без JIT для этих частей.

```kotlin
class AOTExample {
    fun processData(numbers: List<Int>): Int {
        // При наличии AOT-компиляции этот метод может работать быстро с первого запуска.
        return numbers.sum()
    }
}
```

**Преимущества:**
- ✅ Высокая производительность с первых запусков для заранее скомпилированных участков.
- ✅ Более предсказуемое время выполнения таких участков.
- ✅ Меньше runtime-накладных расходов на компиляцию (и потенциально ниже расход батареи для этих путей).

**Недостатки:**
- ❌ Увеличение времени установки или фоновой оптимизации при агрессивной AOT-компиляции.
- ❌ Увеличение занимаемого места за счёт нативных артефактов.
- ❌ Риск компиляции кода, который фактически редко или никогда не используется (если не применять профили).

### Гибридный Подход (Android 7+)

Современный ART использует гибрид: интерпретация + JIT + профили + выборочная AOT-компиляция на основе профилей (Profile-Guided Optimization).

**Profile-Guided Optimization (в упрощённом виде):**

```text
Установка → Быстро (DEX + минимальная начальная компиляция)
    ↓
Первый запуск → Интерпретация + JIT + профилирование горячих путей
    ↓
Фон (устройство на зарядке / простаивает) → dex2oat компилирует по профилю только горячий код
    ↓
Последующие запуски → Быстрее (часть кода уже в оптимизированном нативном виде)
```

```kotlin
// Пример пути профиля (может отличаться между версиями):
// /data/misc/profiles/cur/0/com.example.app/primary.prof

class ProfileGuidedExample {
    // Часто вызываемый метод → с высокой вероятностью попадёт в профиль и будет AOT-компилироваться в фоне.
    fun frequentOperation() { /* ... */ }

    // Редко используемый метод → может остаться интерпретируемым или JIT-компилироваться по мере надобности.
    fun rareDebugOperation() { /* ... */ }
}
```

**Режимы компиляции (adb) для отладки и тестирования:**

```bash
# Профильно-ориентированная компиляция (использует комбинацию JIT + AOT по профилю)
adb shell cmd package compile -m speed-profile com.example.app

# Более агрессивная AOT-компиляция (speed)
adb shell cmd package compile -m speed com.example.app

# Сбросить состояние компиляции
adb shell cmd package compile --reset com.example.app
```

### Baseline Profiles (Android 7+ / RU комментарий)

Baseline Profiles поддерживаются ART, начиная с Android 7.0+ (API 24+), и используются экосистемой (в т.ч. Play Store и Jetpack библиотеками) для того, чтобы заранее передать профили оптимизации.

**Идея:** предгенерированные профили, поставляемые с APK/AAB, позволяют системе компилировать критические пути уже при установке или ранних фоновых оптимизациях, уменьшая время "прогрева".

```kotlin
// Как правило, файл профиля в модуле указывается относительно корня модуля, например:
// src/main/baseline-prof.txt
class BaselineProfileExample {
    // Метод, попавший в baseline-prof.txt → может быть AOT-соптимизирован ранее.
    fun criticalStartupMethod() {
        // Более быстрый запуск с первых сессий.
    }
}

// Проверка статуса; пример использования ProfileVerifier:
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    Log.d("Compilation", """
        Has profile: ${status.hasReferenceProfile()}
        Compiled with profile: ${status.isCompiledWithProfile}
    """.trimIndent())
}
```

**Типичные эффекты (по данным документации и измерений, зависят от приложения):**
- Cold start: может стать заметно быстрее (например, до ~30%+).
- Warm start: аналогично может ускоряться.

### Сравнение Подходов

(Числа условные, для понимания trade-off'ов.)

| Аспект | JIT | AOT | Hybrid (Profile-Guided) |
|--------|-----|-----|------------------------|
| Установка | Быстрая | Медленнее при полном AOT | Быстрая / адаптивная |
| Первый запуск | Медленнее (прогрев) | Быстрее для AOT-кода | Ближе к AOT для горячих путей |
| Оптим. запуск | После прогрева | Стабильный | Стабильный для профилированных путей |
| Размер | Меньше артефактов | Больше из-за нативного кода | Компромисс |
| Батарея | Выше из-за JIT | Ниже для AOT-кода | Компромисс, ниже при хороших профилях |
| Обновления | Быстрые | Может требовать дополнительной компиляции | Быстрые + дооптимизация в фоне |

### Стратегия Выбора

Ниже — концептуальный пример рассуждения о том, какой подход был бы выгоден для разных типов приложений (это не реальные Android API):

```kotlin
fun chooseStrategy(appType: AppType): Strategy {
    return when (appType) {
        Gaming -> Strategy.FullAOT          // Максимально стабильные фреймтаймы (концептуально)
        SocialMedia -> Strategy.ProfileGuided // Частые обновления, важен баланс
        Utility -> Strategy.BaselineProfile // Быстрый первый запуск и лёгкость
        Enterprise -> Strategy.FullAOT      // Ставка на предсказуемость
    }
}
```

Реально на Android выбор стратегии определяется политикой ART, настройками сборки, baseline-профилями и поведением магазина, а не ручным переключением таких enum'ов из приложения.

---

## Answer (EN)

Android uses a hybrid approach with **JIT** (Just-In-Time) and **AOT** (Ahead-Of-Time) compilation (via ART) to balance performance, install time, and storage.

Note: Numbers mentioned below for time/size are illustrative, not universal across devices or Android versions.

### JIT (Just-In-Time)

**How it works:**
- ART can initially execute DEX bytecode via an interpreter.
- Frequently executed ("hot") code paths are profiled and JIT-compiled into native code at runtime.
- The compiled code is reused for subsequent calls; profiles and JIT results can be persisted and later used to drive AOT compilation, so benefits are not always fully lost on app restart.

```kotlin
class JITExample {
    fun processData(numbers: List<Int>): Int {
        // Example (illustrative only):
        // Initial calls: slower (interpreted / unoptimized)
        // After repeated calls: JIT kicks in for hot path
        // Subsequent calls: faster (compiled code)
        return numbers.sum()
    }
}
```

**Advantages:**
- ✅ Fast installation (no full-AOT of all code at install).
- ✅ Smaller initial storage footprint.
- ✅ Adaptive optimizations based on real-world usage.

**Disadvantages:**
- ❌ Warm-up time while JIT collects profiles and compiles hot code.
- ❌ Runtime overhead for profiling and compilation.
- ❌ Without profile-based AOT, some benefits diminish between process restarts.

### AOT (Ahead-Of-Time)

**How it works:**
- DEX → native compilation is performed ahead of time (e.g., during install or deferred background optimizations via `dex2oat`), according to system policy.
- Resulting artifacts (OAT/ART/VDex) are stored on disk and used on launch.
- The app can execute pre-compiled native code for those parts without JIT overhead.

```kotlin
class AOTExample {
    fun processData(numbers: List<Int>): Int {
        // When AOT-compiled, this method can be fast from the first run.
        return numbers.sum()
    }
}
```

**Advantages:**
- ✅ High performance from the first runs for precompiled regions.
- ✅ More predictable execution time for those regions.
- ✅ Reduced runtime compilation overhead (and potentially better battery usage for those paths).

**Disadvantages:**
- ❌ Longer install or background optimization time under aggressive full AOT.
- ❌ Larger storage footprint due to native artifacts.
- ❌ May compile rarely used code if not guided by profiles.

### Hybrid Approach (Android 7+)

Modern ART uses a hybrid: interpretation + JIT + profiles + selective AOT based on profiles (Profile-Guided Optimization).

**Profile-Guided Optimization (simplified):**

```text
Install → Fast (DEX + minimal initial compilation)
    ↓
First Run → Interpretation + JIT + profiling of hot paths
    ↓
Background (device charging / idle) → dex2oat compiles hot code based on profiles
    ↓
Subsequent Runs → Faster (hot paths already optimized)
```

```kotlin
// Example profile path (may vary by version):
// /data/misc/profiles/cur/0/com.example.app/primary.prof

class ProfileGuidedExample {
    // Hot method → likely ends up in profile and gets AOT-compiled in background.
    fun frequentOperation() { /* ... */ }

    // Cold method → may remain interpreted or JIT-compiled on demand.
    fun rareDebugOperation() { /* ... */ }
}
```

**Compilation modes (adb) for debugging and testing:**

```bash
# Profile-guided style (combination of JIT + profile-based AOT)
adb shell cmd package compile -m speed-profile com.example.app

# More aggressive AOT (speed)
adb shell cmd package compile -m speed com.example.app

# Reset compilation state
adb shell cmd package compile --reset com.example.app
```

### Baseline Profiles (Android 7+ / EN note)

Baseline Profiles are supported by ART starting from Android 7.0+ (API 24+) and used by the ecosystem (including Play Store and Jetpack libraries) to supply optimization profiles ahead of time.

**Idea:** pre-generated profiles shipped with the APK/AAB allow the system to compile critical paths during install or early background optimizations, reducing warm-up time.

```kotlin
// Typically defined relative to the module root, e.g.:
// src/main/baseline-prof.txt
class BaselineProfileExample {
    // Method listed in baseline-prof.txt → can be AOT-optimized earlier.
    fun criticalStartupMethod() {
        // Faster from early sessions.
    }
}

// Check compilation status; ProfileVerifier usage example:
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
    val status = ProfileVerifier.getCompilationStatusAsync().get()
    Log.d("Compilation", """
        Has profile: ${status.hasReferenceProfile()}
        Compiled with profile: ${status.isCompiledWithProfile}
    """.trimIndent())
}
```

**Typical effects (per docs and measurements; app-dependent):**
- Cold start: can be significantly faster (e.g. around ~30%+).
- Warm start: similar potential improvements.

### Comparison

(Values are conceptual, illustrating trade-offs.)

| Aspect | JIT | AOT | Hybrid (Profile-Guided) |
|--------|-----|-----|------------------------|
| Install Time | Fast | Slower with full AOT | Fast / adaptive |
| First Run | Slower (warm-up) | Faster for AOT code | Closer to AOT on hot paths |
| Optimized Run | After warm-up | Stable | Stable for profiled paths |
| Storage | Smaller artifacts | Larger due to native code | In-between |
| Battery | Higher due to JIT work | Lower for AOT code | Balanced; improved with good profiles |
| Updates | Fast | May trigger extra compilation | Fast + background re-optimization |

### Strategy Selection

Below is a conceptual example for reasoning about trade-offs for different app types (this is NOT an actual Android API):

```kotlin
fun chooseStrategy(appType: AppType): Strategy {
    return when (appType) {
        Gaming -> Strategy.FullAOT          // Conceptually favor stable frame times
        SocialMedia -> Strategy.ProfileGuided // Frequent updates, need balance
        Utility -> Strategy.BaselineProfile // Strong first impression, lightweight
        Enterprise -> Strategy.FullAOT      // Predictability emphasized
    }
}
```

In reality, Android chooses strategies via ART policies, build configuration, baseline profiles, and store behavior; apps do not directly flip such enums at runtime.

---

## Follow-ups

1. How do baseline profiles differ from runtime-generated profiles?
2. What triggers background AOT compilation (dex2oat) in profile-guided mode?
3. How can you force full AOT compilation for performance testing?
4. What are the trade-offs between `speed` and `speed-profile` compilation modes?
5. How does code shrinking/obfuscation (R8/ProGuard) interact with JIT/AOT compilation on ART?

## References

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
