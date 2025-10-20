---
id: 20251012-122796
title: CI/CD Automated Testing / Автоматизированное тестирование в CI/CD
aliases: [CI/CD Automated Testing, Автоматизированное тестирование в CI/CD]
topic: android
subtopics: [gradle, testing-unit, testing-instrumented]
question_kind: android
difficulty: medium
status: draft
moc: moc-android
related: [q-android-testing-strategies--android--medium, q-android-lint-tool--android--medium, q-build-optimization-gradle--gradle--medium]
created: 2025-10-15
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/gradle, android/testing-unit, android/testing-instrumented, ci-cd, testing, difficulty/medium]
---

# Question (EN)
> How do you design fast and reliable CI/CD automated testing for Android (stages, caching, parallelism, flakiness, and reports)?

# Вопрос (RU)
> Как спроектировать быстрые и надёжные автоматизированные тесты в CI/CD для Android (этапы, кеширование, параллелизм, флаки‑тесты и отчёты)?

---

## Answer (EN)

### Goals
- Fast feedback (PR checks < 10 min)
- Deterministic, hermetic builds
- Clear, actionable reports (tests, lint, coverage)

### Pipeline (typical)
- Pre-merge: static checks → unit tests → instrumented tests (shards) → artifacts + reports
- Post-merge/nightly: full suite, long‑running, device lab, performance checks

### Tests and scope
- Unit: JVM, fast, mock Android deps
- Instrumented: Espresso/UI, real/emulated devices, sharding
- Lint/Detekt: style and correctness
- Coverage: merge unit + instrumented; fail on drop threshold

### Speed and stability
- Caching: Gradle build cache + dependency cache; enable configuration cache
- Parallelism: `--parallel`, matrix (API levels/ABIs), test sharding
- Split modules: independent builds/tests, avoid rebuilding the world
- Flaky tests: quarantine, retry with reruns, deflake backlog
- Hermeticity: lock toolchains, pin SDKs, no network in tests (use MockWebServer)

### Minimal CI step (GitHub Actions)
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

### Reports and artifacts
- Store JUnit XML, lint HTML, coverage (Jacoco) per job
- Surface failures with inline annotations; link to flaky quarantine list

### Device tests
- Emulator matrix for critical PRs; broader device farm nightly
- Shard by package/class; retry failed shards only

### Security and compliance
- Sign/AAB in protected job; secrets via OIDC; verify supply‑chain (checksums)

## Ответ (RU)

### Цели
- Быстрая обратная связь (PR < 10 мин)
- Детерминизм и герметичность сборок
- Понятные отчёты (тесты, линт, покрытие)

### Конвейер (типовой)
- Перед мерджем: статпроверки → unit → инструментальные (шардинг) → артефакты + отчёты
- После мержа/ночью: полный набор, длительные, девайс‑лаб, перф‑проверки

### Тесты и охват
- Unit: JVM, быстро, заглушки Android
- Инструментальные: Espresso/UI, реальные/эмуляторы, шардинг
- Lint/Detekt: стиль и корректность
- Покрытие: объединять unit + instrumented; падать при падении порога

### Скорость и стабильность
- Кеши: Gradle build + зависимости; включить configuration cache
- Параллелизм: `--parallel`, матрица (API/ABI), шардинг тестов
- Разделение модулей: независимые сборки/тесты
- Флаки: карантин, ретраи, бэклог дефлейка
- Герметичность: фиксированные SDK/toolchain, сеть в тестах запрещена (MockWebServer)

### Минимальный шаг CI (GitHub Actions)
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

### Отчёты и артефакты
- Сохранять JUnit XML, lint HTML, покрытие (Jacoco) по джобам
- Показывать ошибки аннотациями; ссылка на список флаки

### Девайс‑тесты
- Матрица эмуляторов для критичных PR; шире — ночью
- Шардить по пакетам/классам; ретраить только упавшие шары

### Безопасность
- Подписывать/AAB в защищённой джобе; секреты через OIDC; проверять цепочку поставки

---

## Follow-ups
- How to maintain a flaky test quarantine process and metrics?
- What should be pre‑merge vs nightly for optimal signal vs cost?
- How to shard instrumented tests effectively across devices?

## References
- https://docs.gradle.org/current/userguide/build_cache.html
- https://developer.android.com/studio/test
- https://docs.github.com/actions

## Related Questions

### Prerequisites (Easier)
- [[q-android-testing-strategies--android--medium]]

### Related (Same Level)
- [[q-android-lint-tool--android--medium]]
- [[q-build-optimization-gradle--gradle--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
