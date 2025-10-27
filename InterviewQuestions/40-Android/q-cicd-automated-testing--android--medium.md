---
id: 20251012-122796
title: CI/CD Automated Testing / Автоматизированное тестирование в CI/CD
aliases: [CI/CD Automated Testing, Автоматизированное тестирование в CI/CD]
topic: android
subtopics: [gradle, testing-instrumented, testing-unit, ci-cd]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-lint-tool--android--medium, q-android-testing-strategies--android--medium, q-build-optimization-gradle--android--medium, c-gradle-build-cache, c-test-sharding]
created: 2025-10-15
updated: 2025-10-27
sources: []
tags: [android/gradle, android/testing-instrumented, android/testing-unit, android/ci-cd, ci-cd, testing, difficulty/medium]
---

# Вопрос (RU)
> Как организовать автоматизированное тестирование Android-приложения в CI/CD пайплайне?

# Question (EN)
> How to organize automated testing for Android applications in a CI/CD pipeline?

---

## Ответ (RU)

### Цели
- Быстрая обратная связь (проверки PR < 10 мин)
- Детерминированные, изолированные сборки
- Понятные, действенные отчеты (тесты, lint, покрытие)

### Пайплайн (типичный)
- **Pre-merge**: статический анализ → юнит-тесты → инструментальные тесты (с шардингом) → артефакты + отчеты
- **Post-merge/nightly**: полный набор тестов, долгие проверки, device lab, производительность

### Тесты и область применения
- **Unit**: JVM, быстрые, мокируем Android-зависимости через [[c-unit-testing]] и [[c-mockito]]
- **Instrumented**: [[c-espresso]]/UI, реальные/эмулированные устройства, шардинг
- **Lint/Detekt**: стиль и корректность кода
- **Coverage**: объединение unit + instrumented; падение сборки при снижении порога

### Скорость и стабильность
- **Кэширование**: Gradle build cache + кэш зависимостей; включение configuration cache
- **Параллелизм**: `--parallel`, матрица (API уровни/ABI), шардинг тестов
- **Разделение модулей**: независимые сборки/тесты, избегание пересборки всего проекта
- **Нестабильные тесты**: карантин, повторный запуск с reruns, бэклог исправлений
- **Изолированность**: фиксация toolchains, pin SDKs, без сети в тестах (использовать MockWebServer)

### Минимальный CI-шаг (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2
      - name: Юнит-тесты (config + build cache)
        run: ./gradlew testDebugUnitTest --configuration-cache --build-cache --parallel
      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache
      - name: Загрузка отчетов
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Отчеты и артефакты
- Сохранение JUnit XML, lint HTML, покрытия (Jacoco) для каждой задачи
- Отображение ошибок через inline-аннотации; ссылка на список нестабильных тестов

### Тесты на устройствах
- Матрица эмуляторов для критичных PR; более широкая device farm для nightly
- Шардинг по пакетам/классам; повтор только упавших шардов

### Безопасность и compliance
- Подписание/AAB в защищенной задаче; секреты через OIDC; проверка supply-chain (контрольные суммы)

## Answer (EN)

### Goals
- Fast feedback (PR checks < 10 min)
- Deterministic, hermetic builds
- Clear, actionable reports (tests, lint, coverage)

### Pipeline (typical)
- Pre-merge: static checks → unit tests → instrumented tests (shards) → artifacts + reports
- Post-merge/nightly: full suite, long‑running, device lab, performance checks

### Tests and Scope
- **Unit**: JVM, fast, mock Android deps using [[c-unit-testing]] and [[c-mockito]]
- **Instrumented**: [[c-espresso]]/UI, real/emulated devices, sharding
- **Lint/Detekt**: style and correctness
- **Coverage**: merge unit + instrumented; fail on drop threshold

### Speed and Stability
- **Caching**: Gradle build cache + dependency cache; enable configuration cache
- **Parallelism**: `--parallel`, matrix (API levels/ABIs), test sharding
- **Split modules**: independent builds/tests, avoid rebuilding the world
- **Flaky tests**: quarantine, retry with reruns, deflake backlog
- **Hermeticity**: lock toolchains, pin SDKs, no network in tests (use [[c-mockwebserver]])

### Minimal CI Step (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2

      - name: Unit tests (config + build cache)
        run: ./gradlew testDebugUnitTest --configuration-cache --build-cache --parallel

      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache

      - name: Upload reports
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Reports and Artifacts
- Store JUnit XML, lint HTML, coverage (Jacoco) per job
- Surface failures with inline annotations; link to flaky quarantine list

### Device Tests
- Emulator matrix for critical PRs; broader device farm nightly
- Shard by package/class; retry failed shards only

### Security and Compliance
- Sign/AAB in protected job; secrets via OIDC; verify supply-chain (checksums)

## Follow-ups

- How to maintain a flaky test quarantine process and track deflake metrics?
- What criteria determine pre-merge vs nightly test scope for optimal cost/signal ratio?
- How to effectively shard instrumented tests across devices and retry failed shards?
- What caching strategies work best for Android CI (local, remote, configuration cache)?
- How to integrate code coverage requirements without slowing down feedback loops?

## References

- [[c-gradle-build-cache]] - Gradle build caching strategies
- [[c-test-sharding]] - Test sharding and parallelization
- [[c-espresso]] - Espresso UI testing framework
- [[c-mockito]] - Mocking framework for unit tests
- https://docs.gradle.org/current/userguide/build_cache.html - Gradle build cache
- https://developer.android.com/studio/test - Android testing fundamentals
- https://docs.github.com/actions - GitHub Actions documentation

## Related Questions

### Prerequisites
- [[q-android-testing-strategies--android--medium]] - Testing strategies overview
- [[q-gradle-basics--tools--easy]] - Gradle build system fundamentals

### Related
- [[q-android-lint-tool--android--medium]] - Static analysis with Android Lint
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization
- [[q-test-coverage-android--android--medium]] - Code coverage measurement

### Advanced
- [[q-distributed-testing-infrastructure--system-design--hard]] - Distributed test infrastructure
- [[q-performance-regression-testing--android--hard]] - Performance regression detection
