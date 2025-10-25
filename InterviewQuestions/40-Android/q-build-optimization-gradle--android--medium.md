---
id: 20251011-220005
title: Gradle Build Optimization / Оптимизация сборки Gradle
aliases: [Gradle Build Optimization, Оптимизация сборки Gradle]
topic: android
subtopics:
  - dependency-management
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-modularization--android--medium
  - q-baseline-profiles-optimization--android--medium
created: 2025-10-11
updated: 2025-10-20
tags: [android/dependency-management, android/gradle, difficulty/medium]
source: Original
source_note: Gradle build performance best practices
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:52 pm
---

# Вопрос (RU)
> Как оптимизировать сборку Gradle в Android?

# Question (EN)
> How to optimize Gradle build in Android?

---

## Ответ (RU)

### Принципы
- **Профилировать сначала**: Использовать build scans для поиска узких мест (конфигурация vs выполнение, промахи кэша).
- **Агрессивное кэширование**: Configuration cache + build cache для переиспользования между сборками/CI.
- **Уменьшать работу**: Модуляризация, KSP вместо KAPT, избегать динамических версий, избегать некэшируемых задач.
- **Параллелизация**: Включить parallel workers, держать модули независимыми.
- **Стабилизировать входы**: Закрепить версии (no dynamic), provider APIs, детерминированные пути.

(См. подробные примеры кода и best practices в английской секции)

## Answer (EN)

### Principles
- **Profile first**: Use build scans to locate bottlenecks (configuration vs execution, cache misses).
- **Cache aggressively**: Configuration cache + build cache for reuse across builds/CI.
- **Reduce work**: Modularization, KSP instead of KAPT, avoid dynamic versions, avoid non-cacheable tasks.
- **Parallelize**: Enable parallel workers, keep modules independent.
- **Stabilize inputs**: Pin versions (no dynamic), provider APIs, deterministic paths.

### Configuration Cache (largest Single win)
- Caches the configuration phase; subsequent builds skip re-config.
- Requirements: no side effects at configuration time; use Provider API instead of reading env/files directly.
```kotlin
// GOOD: defer reading env to execution via Provider API
val apiKey = providers.environmentVariable("API_KEY")
android { defaultConfig { buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" }) } }
```

### Build Cache (local + remote)
- Reuses task outputs between builds/machines; great for CI/teams.
- Ensure tasks are cacheable (declared inputs/outputs; no absolute paths; no time-dependent logic).
```kotlin
// settings.gradle.kts (conceptual)
buildCache {
  local { isEnabled = true }
  // remote<HttpBuildCache> { url = uri("<your-cache-url>"); isPush = (System.getenv("CI") == "true") }
}
```

### Parallelism and Workers
- Enable parallel task execution and adequate workers.
- Keep module graph shallow; reduce cross-module coupling to maximize concurrency.

### Modularization
- Split features and core layers into modules for smaller incremental rebuilds.
- Depend on API-only where possible to minimize recompilation surface.

### KSP over KAPT
- KSP avoids Java stub generation; typically ~2x faster annotation processing.
- Migrate processors when supported ([[c-room]], [[c-hilt]], Moshi, etc.).
```kotlin
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler); ksp(libs.hilt.compiler) }
```

### Version Catalogs (no Hardcoded Versions in Build files)
- Centralize versions; speed up sync; avoid dynamic `+`.
```toml
# libs.versions.toml (structure only, no specific numbers)
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Build Scans (measurement)
- Run with `--scan`; analyze task timeline, cache hit rates, configuration time, dependency resolution.
- Fix hotspots iteratively; confirm wins by comparing scans before/after.

### CI/CD
- Reuse caches (Gradle action + caches for wrapper and `.gradle` dirs).
- Run with `--configuration-cache --build-cache --parallel`.
- Keep Java toolchain stable; enable remote cache write from CI only.

### Common Pitfalls
- Dynamic versions (`1.+`), absolute paths, configuration-time I/O, too many tiny modules, non-cacheable custom tasks, disabled daemon, not profiling.

## Follow-ups
- How to make a custom Gradle task cacheable (inputs/outputs)?
- When does configuration cache break, and how to detect it quickly?
- KSP migration steps and verification for each processor?

## References
- https://docs.gradle.org/current/userguide/configuration_cache.html
- https://docs.gradle.org/current/userguide/build_cache.html
- https://docs.gradle.org/current/userguide/performance.html

## Related Questions

### Prerequisites (Easier)
- [[q-android-build-optimization--android--medium]]

### Related (Same Level)
- [[q-android-modularization--android--medium]]
- [[q-baseline-profiles-optimization--android--medium]]

### Advanced (Harder)
- [[q-cicd-pipeline-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

