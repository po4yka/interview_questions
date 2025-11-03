---
id: android-639
title: Play Asset Delivery Strategy / Стратегия Play Asset Delivery
aliases:
  - Play Asset Delivery Strategy
  - Стратегия Play Asset Delivery
topic: android
subtopics:
  - release-engineering
  - app-bundle
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-release-engineering
  - c-app-bundle
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/release
  - play-asset-delivery
  - app-bundle
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/playcore/asset-delivery
    note: Play Asset Delivery documentation
  - url: https://developer.android.com/guide/app-bundle/asset-delivery-options
    note: Delivery modes overview
---

# Вопрос (RU)
> Как разработать стратегию Play Asset Delivery: выбрать режимы (install-time, fast-follow, on-demand), управлять динамическими фичами, обновлять ассеты без релиза и мониторить доставку?

# Question (EN)
> How do you architect a Play Asset Delivery strategy, choosing delivery modes (install-time, fast-follow, on-demand), managing dynamic features, updating assets without full releases, and monitoring delivery health?

---

## Ответ (RU)

### 1. Анализ ассетов

- Категоризируйте ресурсы: критичные (install-time), большие/нечасто используемые (fast-follow), опциональные (on-demand).
- Измерьте размер пакетов, таргетируйте устройства по ABI, texture compression (ETC2/ASTC).
- Определите зависимости между динамическими фичами и ассетами.

### 2. Настройка App Bundle

- `build.gradle`:

```groovy
android {
    bundle {
        language { enableSplit = false }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}

play {
    assetPacks = [":assetpack_install", ":assetpack_fast_follow", ":assetpack_on_demand"]
}
```

- Asset pack module gradle plugin (`com.android.asset-pack`) + delivery mode в `asset-pack` `build.gradle`.
- Для динамических фич используйте `dist:onDemand="true"` и `dist:fusing`.

### 3. Доставка и управление

- SDK Play Core:

```kotlin
val assetManager = AssetPackManagerFactory.getInstance(context)
assetManager.fetch(listOf("assetpack_on_demand"))
assetManager.registerListener { state ->
    when (state.status()) {
        AssetPackStatus.DOWNLOADING -> showProgress(state.bytesDownloaded(), state.totalBytesToDownload())
        AssetPackStatus.COMPLETED -> loadAssets(state)
    }
}
```

- Fast-follow → доступен после установки/обновления без ожидания в приложении.
- On-demand → инициируйте `fetch` при необходимости; учитывайте cancellation и storage.

### 4. Обновления без релиза

- \"Asset only\" updates: загрузка новых ассетов через Play Console без обновления бинаря.
- Планируйте версионирование ассетов (semantic versioning) + fallback на bundled ресурс.
- Для AB testing храните mapping версия → feature flag (remote config).

### 5. Мониторинг и отзывчивость

- Play Console (Delivery insights) + Play Developer Reporting API для успеха скачиваний.
- Отслеживайте ошибки установок (insufficient storage) и выдавайте подсказки пользователю.
- Логируйте время загрузки/готовности ассетов, сравнивайте с целями UX.

### 6. Offline и fallback

- Для критичных сценариев держите минимальный набор ассетов install-time.
- Если on-demand загрузка провалилась → уведомление и retry / degrade gracefully (меньше текстур).
- Подумайте о prefetch (Wi-Fi only) через WorkManager.

### 7. Compliance & QA

- Тестируйте asset packs в Play Internal Testing (поддерживает asset delivery).
- Проводите size regression tests (bundletool `dump manifest --modules`).
- Документируйте процессы обновления и лицензирования (например, сторонние медиа).

---

## Answer (EN)

- Classify assets by criticality and size to map them to install-time, fast-follow, or on-demand packs; configure splits (ABI, density, language) appropriately.
- Define asset pack modules in the App Bundle, set delivery modes, and manage dynamic feature dependencies.
- Use Play Core to request, monitor, and consume asset packs at runtime, handling progress, cancellation, and storage errors.
- Take advantage of asset-only updates for content refreshes without full app releases and version assets for A/B support.
- Monitor delivery health via Play Console/Reporting API, log setup times, and provide user feedback or fallbacks when downloads fail.
- Keep minimal critical assets install-time, implement retries/prefetch, and verify asset packs through internal testing and regression checks.

---

## Follow-ups
- Как совместить PAD с собственной CDN fallback (для сторонових сторах)?
- Как распределять ассеты между device tier (low-end vs high-end)?
- Какие стратегии для локализации ассетов (языки, региональные правовые ограничения)?

## References
- [[c-release-engineering]]
- [[c-app-bundle]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/playcore/asset-delivery
