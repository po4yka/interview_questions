---
id: android-223
title: Measure Project Size / Измерение размера проекта
aliases:
- Measure Project Size
- Измерение размера проекта
topic: android
subtopics:
- architecture-modularization
- gradle
question_kind: theory
difficulty: easy
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-gradle
- q-how-navigation-is-implemented-in-android--android--medium
- q-how-to-write-recyclerview-cache-ahead--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/architecture-modularization
- android/gradle
- codebase-analysis
- difficulty/easy
- project-metrics

---

# Вопрос (RU)

> Как можно измерить размер проекта?

# Question (EN)

> How can you measure project size?

## Ответ (RU)

Размер Android-проекта можно оценивать несколькими практическими метриками (обычно в комбинации):

1. **Строки кода (LOC)** — объем исходного кода.
2. **Количество модулей** — уровень модуляризации и структурированности.
3. **Размер сборки (APK/AAB)** — размер финального артефакта и его содержимого.
4. **Дополнительные показатели** — количество методов, файлов, зависимостей, время сборки и т.п.

**Типичный крупный продуктовый проект (ориентир, не правило):** ~100,000+ строк кода, 5-10+ модулей, релизный артефакт (APK/AAB) обычно в диапазоне 20-40 MB на одну конфигурацию.

### 1. Строки Кода (LOC)

**Измерение через командную строку:**

```bash
# Подсчитать все Kotlin/Java файлы (грубая оценка)
find . \( -name "*.kt" -o -name "*.java" \) -print0 | xargs -0 wc -l

# Пример вывода: 102345 total
```

(Для более точной оценки можно исключать каталоги `build/`, скрипты и сгенерированный код.)

**Через Android Studio:**

1. Установить плагин "Statistic" (или аналогичный).
2. **Analyze → Statistic**.
3. Просмотреть разбивку по языкам: Kotlin, Java, XML и т.д.

**Интерпретация размера (примерные ориентиры):**

| Размер | LOC | Характеристика |
|--------|-----|----------------|
| Маленький | < 10,000 | Простое приложение с одной-двумя функциями |
| Средний | 10,000-50,000 | Стандартное приложение, несколько ключевых функций |
| Большой | 50,000-200,000 | Корпоративное приложение, несколько доменов, модули |
| Очень большой | > 200,000 | Сложная платформа/экосистема |

LOC сами по себе не отражают качества или сложности, но дают масштаб.

### 2. Количество Модулей

**Измерение:**

```bash
# Посчитать упоминания include в settings.gradle.kts (источник правды по модулям)
grep -E "include\(" settings.gradle.kts | wc -l
```

(Команда `find . -name "build.gradle.kts" | wc -l` даёт грубую оценку и может включать корневые/служебные файлы.)

**Типичная структура большого проекта:**

```kotlin
// ✅ Модульная архитектура
:app                    // Главный модуль
:core-network           // HTTP-клиент
:core-database          // Room, хранение
:core-ui                // UI-компоненты
:feature-login          // Экран входа
:feature-home           // Главный экран
:feature-profile        // Профиль
:feature-settings       // Настройки
```

**Интерпретация:**

| Модуляризация | Модулей | Особенности |
|---------------|---------|------------|
| Монолитная | 1 | Простая структура, но по мере роста — долгие сборки, сильные связи |
| Базовая | 2-4 | Начальное разделение доменов/слоёв |
| Модульная | 5-10 | Параллельные сборки, лучшее разделение ответственности |
| Высоко модульная | 10-20+ | Хорошая изоляция, но усложнение конфигурации и навигации |

Количество модулей важно рассматривать вместе с их границами и зависимостями, а не как самоцель.

### 3. Размер APK / AAB

**Измерение через командную строку (APK как пример):**

```bash
./gradlew assembleRelease
ls -lh app/build/outputs/apk/release/app-release.apk

# Пример вывода: 15M app-release.apk
```

Для современных проектов обычно собирают Android App `Bundle` (`.aab`), а фактический размер загружаемого APK для пользователя будет меньше за счёт сплитов по ABI/экрану/языкам.

**APK Analyzer в Android Studio:**

1. **Build → Analyze APK…** (или Analyze App `Bundle`).
2. Выбрать APK/AAB.
3. Просмотреть разбивку:
   - classes.dex
   - resources.arsc
   - res/
   - lib/
   - assets/

**Интерпретация размера (ориентиры для APK одного варианта):**

| Категория | Размер | Примеры |
|-----------|--------|---------|
| Легковесное | < 10 MB | Утилиты, простые приложения |
| Стандартное | 10-30 MB | Большинство приложений |
| С медиа | 30-100 MB | Соцсети, фото, контент с большим количеством ресурсов |
| Большое | 100-500 MB | Игры, офлайн-контент, стриминг (обычно с доп. кэшем) |

Важно анализировать не только общий размер, но и какие ресурсы/библиотеки его формируют.

### 4. Дополнительные Метрики

**Количество методов (DEX count):**

```bash
# ✅ Использование dexcount плагина (пример задачи)
./gradlew :app:countDebugDexMethods

# Пример вывода: Total methods in classes.dex: 45,234
# Лимит: 65,536 ссылок на методы на один classes.dex.
# При превышении используют MultiDex или уменьшают количество методов (shrinking, удаление зависимостей).
```

App Bundles сами по себе не отменяют лимит 65,536 ссылок на DEX внутри конкретного APK: важно контролировать итоговые DEX-файлы.

**Пример метрик реального проекта (e-commerce, средний размер, условный):**

```
Строки кода:      ~78,000 LOC (79% Kotlin, 11% Java, 10% XML)
Модули:           8 модулей
Размер APK:       ~24 MB release (одна конфигурация)
Методы:           ~42,000 методов
Файлы:            ~500+ исходных файлов
Зависимости:      ~30-40 библиотек
Время сборки:     ~2м (инкрементальная)
```

### Инструменты Измерения

1. **Android Studio** — APK Analyzer, анализ AAB, статистика по файлам.
2. **SonarQube** — `./gradlew sonarqube` для метрик качества и покрытия.
3. **Detekt** — статический анализ Kotlin.
4. **Dexcount** — подсчет методов в DEX.

### Лучшие Практики

1. **Мониторинг роста** — отслеживать ключевые метрики (LOC, методы, размеры, время сборки) по коммитам/релизам.
2. **Установка лимитов** — использовать проверки в CI/Gradle (fail build) при превышении порогов (например, размер APK, количество методов).
3. **Регулярная очистка** — удалять неиспользуемые зависимости, ресурсы, мертвый код.
4. **Оптимизация** — R8/ProGuard shrinking, resource shrinking, split APK/ABI, оптимизация изображений и нативных библиотек.

## Answer (EN)

You can measure Android project size using several practical metrics (usually combined):

1. **Lines of Code (LOC)** — overall source code volume.
2. **Number of Modules** — modularization level and structure.
3. **Artifact Size (APK/AAB)** — final build size and its contents.
4. **Additional indicators** — method count, file count, dependencies, build time, etc.

**Typical product-grade large project (rough guideline, not a rule):** ~100,000+ LOC, 5-10+ modules, release artifact (APK/AAB) often in the 20-40 MB range per variant.

### 1. Lines of Code (LOC)

**Command-line measurement:**

```bash
# Count all Kotlin/Java files (rough estimate)
find . \( -name "*.kt" -o -name "*.java" \) -print0 | xargs -0 wc -l

# Example output: 102345 total
```

(For more accurate numbers, exclude `build/`, generated code, scripts, etc.)

**Android Studio:**

1. Install the "Statistic" (or similar) plugin.
2. Use **Analyze → Statistic**.
3. View breakdown by language: Kotlin, Java, XML, etc.

**Size interpretation (approximate):**

| Size | LOC | Characteristics |
|------|-----|-----------------|
| Small | < 10,000 | Simple app with one or two features |
| Medium | 10,000-50,000 | Standard app with several features |
| Large | 50,000-200,000 | Enterprise/complex app with multiple domains and modules |
| Very Large | > 200,000 | Complex platform/ecosystem |

LOC alone do not indicate quality or complexity, but help to understand scale.

### 2. Number of Modules

**Measurement:**

```bash
# Count include statements in settings.gradle.kts (source of truth for modules)
grep -E "include\(" settings.gradle.kts | wc -l
```

(Using `find . -name "build.gradle.kts" | wc -l` is a rough proxy and may count root/auxiliary build files.)

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

| Modularization | Modules | Notes |
|----------------|---------|-------|
| Monolithic | 1 | Simple layout; as it grows, builds slow down and coupling increases |
| Basic | 2-4 | Initial separation of layers/domains |
| Modular | 5-10 | Better separation, parallel builds, clearer ownership |
| Highly Modular | 10-20+ | Strong isolation; more complex configuration and navigation |

Module count should be evaluated together with boundaries and dependencies, not optimized blindly.

### 3. APK / AAB Size

**Command-line measurement (APK example):**

```bash
./gradlew assembleRelease
ls -lh app/build/outputs/apk/release/app-release.apk

# Example output: 15M app-release.apk
```

Modern distribution typically uses Android App Bundles (`.aab`); actual per-device APKs downloaded from Play Store are smaller due to splits by ABI/screen/language.

**APK Analyzer in Android Studio:**

1. **Build → Analyze APK…** (or analyze App `Bundle`).
2. Select APK/AAB.
3. Inspect breakdown, for example:
   - classes.dex
   - resources.arsc
   - res/
   - lib/
   - assets/

**Size interpretation (guidelines for a single APK variant):**

| Category | Size | Examples |
|----------|------|----------|
| Lightweight | < 10 MB | Utilities, simple apps |
| Standard | 10-30 MB | Most typical apps |
| Media-heavy | 30-100 MB | Social/media/photo apps with many resources |
| Large | 100-500 MB | Games, offline/streaming content (often with extra asset downloads) |

Focus not just on the total size, but which resources and libraries contribute most.

### 4. Additional Metrics

**Method count (DEX count):**

```bash
# ✅ Using dexcount plugin (example task)
./gradlew :app:countDebugDexMethods

# Example output: Total methods in classes.dex: 45,234
# Limit: 65,536 method references per classes.dex.
# When exceeding it, use MultiDex and/or reduce method count via shrinking and dependency cleanup.
```

Android App Bundles do not remove the 65,536 reference limit for the DEX files inside a given APK; you still need to control the final APK's DEX layout.

**Example metrics of a real-world (e-commerce, medium-sized, hypothetical) project:**

```
Lines of Code:    ~78,000 LOC (79% Kotlin, 11% Java, 10% XML)
Modules:          8 modules
APK Size:         ~24 MB release (single variant)
Methods:          ~42,000 methods
Files:            ~500+ source files
Dependencies:     ~30-40 libraries
Build Time:       ~2 min (incremental)
```

### Measurement Tools

1. **Android Studio** — APK Analyzer, AAB analysis, file statistics.
2. **SonarQube** — `./gradlew sonarqube` for quality and coverage metrics.
3. **Detekt** — Kotlin static analysis.
4. **Dexcount** — DEX method count.

### Best Practices

1. **Monitor growth** — track key metrics (LOC, methods, sizes, build time) over commits/releases.
2. **Set limits** — enforce thresholds in CI/Gradle (e.g., fail build if APK size or method count exceeds agreed limits).
3. **Regular cleanup** — remove unused dependencies, resources, and dead code.
4. **Optimize** — use R8/ProGuard shrinking, resource shrinking, ABI/language splits, and optimize images/native libs.

## Дополнительные вопросы (RU)

- Как уменьшить размер APK, если он превышает допустимые значения?
- В чем разница между MultiDex и App `Bundle` при работе с лимитом методов?
- Как измерять технический долг и сложность кода помимо LOC?
- Какие метрики должны служить триггером для рефакторинга или модуляризации проекта?

## Follow-ups

- How to reduce APK size if it exceeds acceptable limits?
- What's the difference between MultiDex and App Bundles for handling method count limits?
- How to measure technical debt and code complexity beyond LOC?
- What metrics should trigger project refactoring or modularization?

## Ссылки (RU)

- Android Developer Guide: APK Analyzer
- Gradle User Manual: Build Scans
- SonarQube documentation for Android projects

## References

- Android Developer Guide: APK Analyzer
- Gradle User Manual: Build Scans
- SonarQube documentation for Android projects

## Связанные вопросы (RU)

### Предварительные знания / Концепции

- [[c-gradle]]

### Предварительные (проще)

- Базовая структура проекта
- Основы системы сборки Gradle
- Состав и структура APK

### Связанные (того же уровня)

- [[q-how-to-write-recyclerview-cache-ahead--android--medium]]
- [[q-how-navigation-is-implemented-in-android--android--medium]]

### Продвинутые (сложнее)

- Стратегии оптимизации сборки
- Архитектурные паттерны модуляризации
- Динамические feature-модули и поставка по запросу

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

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
