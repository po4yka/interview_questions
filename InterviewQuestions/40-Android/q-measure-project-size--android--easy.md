---
id: 20251016-162851
title: "Measure Project Size / Измерение размера проекта"
aliases: ["Measure Project Size", "Измерение размера проекта"]
topic: android
subtopics: [project-structure]
question_kind: theory
difficulty: easy
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-how-navigation-is-implemented-in-android--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/project-structure, project-metrics, codebase-analysis, difficulty/easy]
---

# Вопрос (RU)

Как можно измерить размер проекта?

# Question (EN)

How can you measure project size?

---

## Ответ (RU)

Размер проекта измеряется тремя основными метриками:

1. **Строки кода (LOC)** — количество строк исходного кода
2. **Количество модулей** — уровень модуляризации
3. **Размер APK** — размер финального приложения

**Типичный крупный проект:** ~100,000 строк кода, 5-10 модулей, APK 20-40 MB.

### 1. Строки кода (LOC)

**Измерение через командную строку:**

```bash
# Подсчитать все Kotlin/Java файлы
find . \( -name "*.kt" -o -name "*.java" \) | xargs wc -l

# Вывод: 102345 total
```

**Через Android Studio:**

1. Установить плагин "Statistic"
2. **Analyze → Statistic**
3. Просмотреть разбивку: Kotlin (83%), Java (12%), XML (5%)

**Интерпретация размера:**

| Размер | LOC | Сложность |
|--------|-----|-----------|
| Маленький | < 10,000 | Приложение с одной функцией |
| Средний | 10,000-50,000 | Стандартное приложение, 2-5 функций |
| Большой | 50,000-200,000 | Корпоративное приложение, 5-10 модулей |
| Очень большой | > 200,000 | Сложная платформа, 10+ модулей |

### 2. Количество модулей

**Измерение:**

```bash
# Подсчитать build.gradle.kts файлы
find . -name "build.gradle.kts" | wc -l

# Или в settings.gradle.kts
cat settings.gradle.kts | grep "include" | wc -l
```

**Типичная структура большого проекта:**

```kotlin
// ✅ Модульная архитектура
:app                    // Главный модуль
:core-network           // HTTP клиент
:core-database          // Room, хранение
:core-ui                // UI компоненты
:feature-login          // Экран входа
:feature-home           // Главный экран
:feature-profile        // Профиль
:feature-settings       // Настройки
```

**Интерпретация:**

| Модуляризация | Модулей | Преимущества |
|---------------|---------|--------------|
| Монолитная | 1 | Просто, быстрые сборки |
| Базовая | 2-4 | Некоторое разделение |
| Модульная | 5-10 | Параллельные сборки, хорошее разделение |
| Высоко модульная | 10-20 | Отличное разделение, сложная настройка |

### 3. Размер APK

**Измерение через командную строку:**

```bash
./gradlew assembleRelease
ls -lh app/build/outputs/apk/release/app-release.apk

# Вывод: 15M app-release.apk
```

**APK Analyzer в Android Studio:**

1. **Build → Analyze APK**
2. Выбрать APK файл
3. Просмотреть разбивку:
   - classes.dex: 5.2 MB (34%)
   - resources.arsc: 2.1 MB (14%)
   - res/: 4.8 MB (32%)
   - lib/: 2.3 MB (15%)
   - assets/: 0.5 MB (3%)

**Интерпретация размера:**

| Категория | Размер | Примеры |
|-----------|--------|---------|
| Легковесное | < 10 MB | Утилиты, простые игры |
| Стандартное | 10-30 MB | Большинство приложений |
| С медиа | 30-100 MB | Социальные сети, фото |
| Большое | 100-500 MB | Игры, видео-стриминг |

### 4. Дополнительные метрики

**Количество методов:**

```bash
# ✅ Использование dexcount плагина
./gradlew countDebugDexMethods

# Вывод: Total methods: 45,234
# ❌ Лимит Android: 65,536 методов на DEX (требуется MultiDex)
```

**Пример метрик реального проекта (e-commerce, средний размер):**

```
Строки кода:      78,234 LOC (79% Kotlin, 11% Java, 10% XML)
Модули:           8 модулей
Размер APK:       24.3 MB release
Методы:           42,156 методов
Файлы:            523 исходных файла
Зависимости:      38 библиотек
Время сборки:     2м 15с (инкрементальная)
```

### Инструменты измерения

1. **Android Studio** — APK Analyzer, плагин Statistics
2. **SonarQube** — `./gradlew sonarqube` для качества кода
3. **Detekt** — статический анализ Kotlin
4. **Dexcount** — подсчет методов

### Лучшие практики

1. **Мониторинг роста** — отслеживать метрики в commits
2. **Установка лимитов** — Gradle fail на превышении 50 MB APK
3. **Регулярная очистка** — удалять неиспользуемые зависимости, мертвый код
4. **Оптимизация ресурсов** — использовать R8/ProGuard shrinking

---

## Answer (EN)

Project size is measured using three main metrics:

1. **Lines of Code (LOC)** — source code line count
2. **Number of Modules** — modularization level
3. **APK Size** — final application size

**Typical large project:** ~100,000 LOC, 5-10 modules, 20-40 MB APK.

### 1. Lines of Code (LOC)

**Command-line measurement:**

```bash
# Count all Kotlin/Java files
find . \( -name "*.kt" -o -name "*.java" \) | xargs wc -l

# Output: 102345 total
```

**Android Studio:**

1. Install "Statistic" plugin
2. **Analyze → Statistic**
3. View breakdown: Kotlin (83%), Java (12%), XML (5%)

**Size interpretation:**

| Size | LOC | Complexity |
|------|-----|------------|
| Small | < 10,000 | Single feature app |
| Medium | 10,000-50,000 | Standard app, 2-5 features |
| Large | 50,000-200,000 | Enterprise app, 5-10 modules |
| Very Large | > 200,000 | Complex platform, 10+ modules |

### 2. Number of Modules

**Measurement:**

```bash
# Count build.gradle.kts files
find . -name "build.gradle.kts" | wc -l

# Or check settings.gradle.kts
cat settings.gradle.kts | grep "include" | wc -l
```

**Typical large project structure:**

```kotlin
// ✅ Modular architecture
:app                    // Main module
:core-network           // HTTP client
:core-database          // Room, storage
:core-ui                // UI components
:feature-login          // Login screen
:feature-home           // Home screen
:feature-profile        // Profile
:feature-settings       // Settings
```

**Interpretation:**

| Modularization | Modules | Benefits |
|----------------|---------|----------|
| Monolithic | 1 | Simple, fast builds |
| Basic | 2-4 | Some separation |
| Modular | 5-10 | Parallel builds, good separation |
| Highly Modular | 10-20 | Excellent separation, complex setup |

### 3. APK Size

**Command-line measurement:**

```bash
./gradlew assembleRelease
ls -lh app/build/outputs/apk/release/app-release.apk

# Output: 15M app-release.apk
```

**APK Analyzer in Android Studio:**

1. **Build → Analyze APK**
2. Select APK file
3. View breakdown:
   - classes.dex: 5.2 MB (34%)
   - resources.arsc: 2.1 MB (14%)
   - res/: 4.8 MB (32%)
   - lib/: 2.3 MB (15%)
   - assets/: 0.5 MB (3%)

**Size interpretation:**

| Category | Size | Examples |
|----------|------|----------|
| Lightweight | < 10 MB | Utilities, simple games |
| Standard | 10-30 MB | Most apps |
| Media-rich | 30-100 MB | Social media, photo apps |
| Large | 100-500 MB | Games, video streaming |

### 4. Additional Metrics

**Method count:**

```bash
# ✅ Using dexcount plugin
./gradlew countDebugDexMethods

# Output: Total methods: 45,234
# ❌ Android limit: 65,536 methods per DEX (MultiDex required)
```

**Real project example (e-commerce, medium size):**

```
Lines of Code:    78,234 LOC (79% Kotlin, 11% Java, 10% XML)
Modules:          8 modules
APK Size:         24.3 MB release
Methods:          42,156 methods
Files:            523 source files
Dependencies:     38 libraries
Build Time:       2m 15s (incremental)
```

### Measurement Tools

1. **Android Studio** — APK Analyzer, Statistics plugin
2. **SonarQube** — `./gradlew sonarqube` for code quality
3. **Detekt** — Kotlin static analysis
4. **Dexcount** — method counting

### Best Practices

1. **Monitor growth** — track metrics in commits
2. **Set limits** — Gradle fail on APK exceeding 50 MB
3. **Regular cleanup** — remove unused dependencies, dead code
4. **Optimize resources** — use R8/ProGuard shrinking

---

## Follow-ups

- How to reduce APK size if it exceeds acceptable limits?
- What's the difference between MultiDex and App Bundles for handling method count limits?
- How to measure technical debt and code complexity beyond LOC?
- What metrics should trigger project refactoring or modularization?

## References

- Android Developer Guide: APK Analyzer
- Gradle User Manual: Build Scans
- SonarQube documentation for Android projects

## Related Questions

### Prerequisites (Easier)
- Project structure basics
- Gradle build system fundamentals
- APK composition and structure

### Related (Same Level)
- [[q-how-to-write-recyclerview-cache-ahead--android--medium]]
- [[q-how-navigation-is-implemented-in-android--android--medium]]

### Advanced (Harder)
- Build optimization strategies
- Modularization architecture patterns
- Dynamic feature modules and on-demand delivery
