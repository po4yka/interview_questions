---
id: 20251012-122799
title: CI/CD Pipeline for Android / CI/CD пайплайн для Android
aliases:
- CI/CD Pipeline for Android
- CI/CD пайплайн для Android
topic: android
subtopics:
- gradle
- pipeline
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related:
- q-cicd-automated-testing--devops--medium
- q-cicd-deployment-automation--devops--medium
- q-build-optimization-gradle--gradle--medium
created: 2025-10-11
updated: 2025-10-20
original_language: en
language_tags:
- en
- ru
tags:
- android/gradle
- ci-cd
- pipeline
- testing
- release
- difficulty/medium
- android/pipeline
---# Вопрос (RU)

> Как выглядит надёжный CI/CD пайплайн для Android (этапы, кеширование, параллелизм, quality‑gates, артефакты, релиз)?

---

# Question (EN)

> What does a robust Android CI/CD pipeline look like (stages, caching, parallelism, quality gates, artifacts, release)?

## Ответ (RU):

### Цели

* Быстрые и надёжные проверки PR (цель ≤10 мин на средний репозиторий); герметичные и воспроизводимые сборки (Gradle wrapper, зафиксированные SDK/build‑tools); трассировка (ссылки на ран/сканы сборки); безопасные секреты (OIDC к Play, без долгоживущих JSON‑ключей); низкая флаки и детерминированные релизы.

### Этапы (типовые)

* Setup: checkout; JDK 17/21 (Temurin); Android SDK cmdline‑tools + platform‑tools + нужные platforms/build‑tools; включён configuration cache; удалённый build cache (напр., Develocity) read‑only на PR; прогрев зависимостей.
* Статпроверки: ktlint, detekt, Android Lint (XML + SARIF для аннотаций в PR); опционально проверка API‑контракта (metalava); аудит зависимостей/безопасности (dependency‑review/OWASP); контроль дрейфа версий (Gradle versions plugin).
* Unit‑тесты: JVM‑тесты по модулям (JUnit 5) с `--parallel`; отчёты Kover/Jacoco (XML + HTML); плагин retry (макс. 1 перезапуск) для локализации флаки; падения новых флаки в изменённых модулях — блокер.
* Сборка: assemble/bundle (AAB) с configuration/build cache; воспроизводимое версионирование (code/name с CI); R8 в полном режиме; артефакты: mapping.txt, сплиты по ABI/ресурсам при необходимости.
* Инструментальные тесты: Gradle Managed Devices (GMD) или ферма девайсов; эмулятор headless (GPU swiftshader, отключён cold boot); шардинг через `numShards`/`shardIndex` или Marathon/Flank; логкат, скриншоты, видео; один retry на упавшие шарды.
* Артефакты/отчёты: JUnit XML; Lint SARIF; Kover/Jacoco XML + HTML; отчёты detekt/ktlint; APK/AAB; mapping.txt; граф зависимостей/SBOM (CycloneDX) для прозрачности цепочки поставок.
* Релиз (ручной gate): загрузка во внутренний трек Google Play через Gradle Play Publisher по OIDC; промоут по трекам с постепенным раскатом; выгрузка ProGuard mapping и нативных символов (Crashlytics/Play); тег коммита и changelog; план отката (авто‑стоп по деградации vitals).

### Кеш/параллель

* Включить configuration cache + локальный/удалённый build cache; кешировать wrapper, загруженные зависимости, KMP‑артефакты; ключи кешей — по хешу wrapper + `gradle.properties` + settings/version catalogs; для PR удалённый кеш только на чтение.
* Запускать с `--parallel` и настроить `org.gradle.workers.max` под доступные ядра; разнести workflow на независимые job‑ы (checks/tests/build) ради максимального параллелизма на уровне CI.
* Матрица запусков (API‑уровни/ABI, где нужно debug/release); шардинг UI‑тестов по пакетам/классам; кеш AVD (`~/.android/avd`) для ускорения старта эмулятора.

### Quality‑gates

* Lint: падение на новых проблемах относительно baseline; `Fatal` — блокер; baseline обновляется только отдельным maintenance‑PR.
* Покрытие: `kover` с правилом `verify` (например, по модулю строки ≥70%, ветви ≥50%); регресс покрытия в затронутых модулях — fail.
* Стиль/статанализ: detekt/ktlint — ноль новых нарушений; пороги detekt настроены так, чтобы `Error` блокировал.
* Безопасность: dependency‑review/OWASP блокируют High/Critical; обязательное secret‑сканирование; SAST на `buildSrc`/скрипты по мере необходимости.
* Тесты: SLO на pass‑rate (например, ≥99% за N последних прогонов); допускается quarantine‑лист, но он пуст для изменённых модулей; любые падения — блокер.
* Релиз‑предохранители: ступенчатый раскат (например, 5%→20%→50%→100%); авто‑стоп при падении crash‑free/росте ANR; бюджет на размер APK/AAB и бюджет на деградацию старта приложения.

### Релизы (отдельный workflow)

* Сборка подписанного AAB с release‑конфигом; Play App Signing + Gradle Play Publisher (OIDC) для загрузки во внутренний трек; прикрепить релиз‑ноты и changelog; выгрузить mapping и нативные символы; ступенчатый раскат с правилами защиты окружения; авто‑промоут при здоровых vitals; документированный и протестированный план отката.

---

## Answer (EN)

### Goals

* Fast and reliable PR checks (target ≤10 min on mid‑size repo); hermetic & reproducible builds (Gradle wrapper, locked SDK/build‑tools); traceability (links to run/build scans); secure secrets (OIDC to Play, no long‑lived JSON keys); low flakiness & deterministic releases.

### Stages (typical)

* Setup: checkout; JDK 17/21 (Temurin); Android SDK cmdline‑tools + platform‑tools + required platforms/build‑tools; Gradle configuration cache on; remote build cache (e.g., Develocity) read‑only on PRs; pre‑warm dependencies.
* Static checks: ktlint, detekt, Android Lint (XML + SARIF for PR annotations); optional API surface check (metalava); dependency & security review (dependency‑review/OWASP); version drift check (Gradle versions plugin).
* Unit tests: JVM tests by module (JUnit 5) with `--parallel`; Kover/Jacoco XML + HTML; test retry plugin (1 rerun max) to contain flakes; fail on new flaky in changed modules.
* Build: assemble/bundle (AAB) using configuration/build cache; reproducible versioning (CI‑provided code/name); R8 full mode; produce mapping.txt and ABI/resource splits as needed.
* Instrumented tests: Gradle Managed Devices (GMD) or device farm; headless emulator (GPU swiftshader, cold boot disabled); shard via `numShards`/`shardIndex` or Marathon/Flank; capture logcat, screenshots, and videos; retry failed shards once.
* Artifact/report upload: JUnit XML; Lint SARIF; Kover/Jacoco XML + HTML; detekt/ktlint reports; APK(s)/AAB; mapping.txt; dependency graph/SBOM (CycloneDX) for supply‑chain visibility.
* Release (manual gate): upload to Play internal via Gradle Play Publisher using OIDC; promote by track with staged rollout; upload ProGuard mapping & native symbols (Crashlytics/Play); tag commit & attach changelog; rollback plan (halt rollout on bad vitals).

### Caching/parallel

* Enable configuration cache + local/remote build cache; cache Gradle wrapper, downloaded deps, KMP artifacts; key caches by hash of Gradle wrapper + `gradle.properties` + settings/version catalogs to avoid stale reuse; PRs use read‑only remote cache to prevent pollution.
* Run with `--parallel` and tune `org.gradle.workers.max` to available cores; split workflow into independent jobs (checks/tests/build) to unlock CI‑level concurrency.
* Matrix runs (API levels/ABIs, debug/release where needed); shard UI tests by package/class count; cache AVD images (`~/.android/avd`) to cut emulator startup time.

### Quality gates

* Lint: fail on new issues vs baseline; treat `Fatal` as blocking; update baseline only via separate maintenance PR.
* Coverage: enforce with Kover `verify` (e.g., per‑module line ≥70%, branch ≥50%); fail on coverage regressions for touched modules.
* Style & static analysis: detekt/ktlint must have zero new violations; detekt severity thresholds tuned to block `Error`.
* Security: dependency‑review/OWASP block High/Critical; secret scanning required; SAST on `buildSrc`/scripts where applicable.
* Tests: pass rate SLO (e.g., ≥99% last N runs); quarantine list allowed but must be empty for changed modules; any failed test blocks merge.
* Release guardrails: staged rollout (e.g., 5%→20%→50%→100%); auto‑halt on crash‑free user drop/ANR rise; size budget (max delta MB/percentage) and startup perf budget for release candidates.

### Releases (separate workflow)

* Build signed AAB with release config; use Play App Signing + Gradle Play Publisher (OIDC) to upload to internal track; attach release notes & changelog; upload mapping & native symbols; staged rollout with environment protection rules; auto‑promote on healthy vitals; rollback strategy documented & tested.

## Follow-ups
- How to shard/emulate instrumented tests efficiently?
- How to enforce coverage gates and trend reports?
- How to secure signing keys and service accounts in CI?

## References
- https://docs.github.com/actions
- https://developer.android.com/studio/test
- https://docs.gradle.org/current/userguide/build_cache.html

## Related Questions

### Prerequisites (Easier)
- [[q-cicd-automated-testing--android--medium]]

### Related (Same Level)
- [[q-cicd-deployment-automation--android--medium]]
- [[q-build-optimization-gradle--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]

