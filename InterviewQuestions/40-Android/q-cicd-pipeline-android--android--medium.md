---
id: 20251012-122799
title: CI/CD Pipeline for Android / CI/CD пайплайн для Android
aliases:
- CI/CD Pipeline for Android
- CI/CD пайплайн для Android
topic: android
subtopics:
- gradle
- ci-cd
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-cicd-automated-testing--android--medium
- q-cicd-deployment-automation--android--medium
- q-build-optimization-gradle--android--medium
created: 2025-10-11
updated: 2025-10-20
tags:
- android/gradle
- android/ci-cd
- difficulty/medium
---

# Вопрос (RU)
> CI/CD пайплайн для Android?

# Question (EN)
> CI/CD Pipeline for Android?

---

## Ответ (RU)

(Требуется перевод из английской секции)

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
