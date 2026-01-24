---
id: android-639
anki_cards:
- slug: android-639-0-en
  language: en
  anki_id: 1768413947269
  synced_at: '2026-01-23T16:45:06.191465'
- slug: android-639-0-ru
  language: ru
  anki_id: 1768413947293
  synced_at: '2026-01-23T16:45:06.192238'
title: Play Asset Delivery Strategy / Стратегия Play Asset Delivery
aliases:
- Play Asset Delivery Strategy
- Стратегия Play Asset Delivery
topic: android
subtopics:
- app-bundle
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-app-bundle
- q-android-app-bundles--android--easy
- q-play-billing-v6-architecture--android--hard
- q-play-feature-delivery--android--medium
- q-play-feature-delivery-dynamic-modules--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/app-bundle
- difficulty/hard
- play-asset-delivery
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

### Краткий Вариант

- Классифицировать ассеты и сопоставить им режимы доставки: install-time (критичные), fast-follow (крупные и скоро нужные), on-demand (опциональные/редкие).
- Настроить `App Bundle` и asset packs (plugin `com.android.asset-pack`, delivery modes, связка с динамическими фичами и `dist:`-атрибутами).
- Использовать `AssetPackManager` для запроса/мониторинга/чтения паков; корректно обрабатывать статусы и ошибки.
- Применять asset-only updates через Play Console (в рамках поддерживаемых PAD-сценариев), версионировать ассеты и иметь безопасный fallback.
- Мониторить доставку (Play Console, Reporting API), обеспечивать офлайн-устойчивость и деградацию качества.
- Прогонять сценарии через internal testing, контролировать размер, документировать процессы.

### Подробный Вариант

### 1. Анализ Ассетов

- Категоризируйте ресурсы: критичные (install-time), большие/нечасто используемые (fast-follow), опциональные (on-demand).
- Измерьте размер пакетов, таргетируйте устройства по ABI, texture compression (ETC2/ASTC).
- Определите зависимости между динамическими фичами и ассетами.

### 2. Настройка App `Bundle`

- Включите сплиты в `build.gradle` основного модуля:

```groovy
android {
    bundle {
        language { enableSplit = false }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

- Для asset pack-модулей используйте плагин `com.android.asset-pack` и задайте режим доставки в их `build.gradle` через `assetPack` / `deliveryType` (install-time, fast-follow, on-demand) согласно документации Play Asset Delivery.
- Для динамических фич используйте правильные атрибуты в манифесте/`dist`-модуле (например, `dist:onDemand="true"`, `dist:fusing`) в пространстве имён `dist`.

### 3. Требования

- Функциональные:
  - Доставка ассетов в зависимости от важности и сценариев использования.
  - Возможность обновлять ассеты без полного релиза приложения.
  - Поддержка динамических фич и корректных зависимостей ассетов.
- Нефункциональные:
  - Минимизация размера первоначальной установки.
  - Надёжность доставки и предсказуемость времени загрузки.
  - Устойчивость к сетевым ошибкам и ограниченному хранилищу.

### 4. Архитектура

- Использование `App Bundle` и Play Asset Delivery как основного механизма доставки ассетов.
- Asset packs, привязанные к конкретным фичам/сценариям, с выбранными режимами доставки.
- Сервис/слой в приложении для:
  - работы с `AssetPackManager` (запросы, мониторинг статусов, повторные попытки);
  - выбора правильной версии ассетов и fallback;
  - логирования метрик доставки.
- Интеграция с remote config/feature flags для включения/отключения контента и A/B-тестов.

### 5. Доставка И Управление

- Используйте библиотеку Play Core для работы с ассет-паками на устройстве:

```kotlin
val assetManager = AssetPackManagerFactory.getInstance(context)
assetManager.fetch(listOf("assetpack_on_demand"))
assetManager.registerListener { state ->
    when (state.status()) {
        AssetPackStatus.DOWNLOADING ->
            showProgress(state.bytesDownloaded(), state.totalBytesToDownload())
        AssetPackStatus.COMPLETED ->
            loadAssets(state)
        // Обрабатывайте также FAILED, CANCELED, WAITING_FOR_WIFI и другие статусы
    }
}
```

- Fast-follow → контент загружается автоматически после установки/обновления и становится доступен без явного запроса из приложения.
- On-demand → инициируйте `fetch` при необходимости; учитывайте отмену, нехватку памяти, Wi‑Fi only, повторные запросы.

### 6. Обновления Без Релиза

- Используйте "asset-only" updates: загрузка новых ассетов через Play Console без обновления бинаря приложения (в пределах поддерживаемых сценариев PAD).
- Планируйте версионирование ассетов (например, semantic versioning) и fallback на ассеты, включенные в основной APK/AAB.
- Для A/B-тестирования храните mapping версия → feature flag (remote config), чтобы управлять выбором ассет-паков.

### 7. Мониторинг И Отзывчивость

- Используйте Play Console (Delivery insights) и Play Developer Reporting API для отслеживания успешности скачиваний и отказов.
- Отслеживайте ошибки установок (например, insufficient storage) и показывайте пользователю понятные подсказки и варианты действий.
- Логируйте время загрузки/готовности ассетов и проверяйте соответствие целям UX/SLI.

### 8. Offline И Fallback

- Для критичных сценариев держите минимальный набор ассетов в install-time-паке.
- Если on-demand загрузка провалилась → уведомление, retry с бэком-оффом и graceful degradation (например, более низкое качество ресурсов).
- Рассмотрите prefetch (Wi‑Fi only) через `WorkManager` для ожидаемых сценариев.

### 9. Compliance & QA

- Тестируйте asset packs через Play Internal Testing (поддерживает asset delivery-сценарии).
- Проводите size regression tests (например, с помощью `bundletool`).
- Документируйте процессы обновления ассетов и лицензирования (например, сторонние медиа, шрифты, текстуры).

---

## Answer (EN)

### Short Version

- Classify assets and map them to delivery modes: install-time (critical core), fast-follow (large and likely needed soon), on-demand (optional/rare).
- Configure the `App Bundle` and asset packs (`com.android.asset-pack` plugin, delivery modes, dynamic feature dependencies, `dist:` attributes).
- Use `AssetPackManager` to request/monitor/consume packs; handle all key statuses and failures.
- Use asset-only updates via Play Console (within PAD-supported scenarios), version assets, and keep safe fallbacks.
- Monitor delivery health (Play Console, Reporting API), ensure offline resilience and graceful degradation.
- Validate via internal testing, guard bundle size, and document asset workflows.

### Detailed Version

### 1. Asset Analysis

- Analyze and classify assets by criticality, size, and usage frequency to map them to install-time (critical core), fast-follow (large but commonly needed soon), or on-demand (optional/rare) asset packs.
- Measure bundle size and use ABI/texture compression targeting (ETC2/ASTC) to avoid shipping unnecessary variants.
- Identify dependencies between dynamic feature modules and their required asset packs.

### 2. App `Bundle` Configuration

- Configure splits in the base module `build.gradle`:

```groovy
android {
    bundle {
        language { enableSplit = false }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
}
```

- Configure asset pack modules with the `com.android.asset-pack` plugin and set delivery modes (install-time, fast-follow, on-demand) in their Gradle configuration.
- For dynamic features, define correct attributes in the manifest/`dist` module (e.g., `dist:onDemand="true"`, `dist:fusing`) using the `dist` namespace.

### 3. Requirements

- Functional:
  - Deliver assets according to criticality and usage scenarios.
  - Allow updating assets without a full app binary release.
  - Support dynamic features and correct asset dependencies.
- Non-functional:
  - Minimize initial download size.
  - Provide reliable, predictable delivery and load times.
  - Be resilient to network/storage issues.

### 4. Architecture

- Use `App Bundle` + Play Asset Delivery as the primary delivery mechanism.
- Model asset packs per feature/use case with appropriate delivery modes.
- Introduce an in-app asset delivery layer/service to:
  - interact with `AssetPackManager` (requests, status tracking, retries);
  - select proper asset versions and fallbacks;
  - log delivery metrics.
- Integrate with remote config/feature flags for content toggling and A/B tests.

### 5. Delivery and Runtime Management

- Use the Play Core library's `AssetPackManager` to request, monitor, and consume asset packs at runtime:

```kotlin
val assetManager = AssetPackManagerFactory.getInstance(context)
assetManager.fetch(listOf("assetpack_on_demand"))
assetManager.registerListener { state ->
    when (state.status()) {
        AssetPackStatus.DOWNLOADING ->
            showProgress(state.bytesDownloaded(), state.totalBytesToDownload())
        AssetPackStatus.COMPLETED ->
            loadAssets(state)
        // Also handle FAILED, CANCELED, WAITING_FOR_WIFI and other statuses
    }
}
```

- Fast-follow: content is downloaded automatically after install/update and becomes available without explicit app-initiated requests.
- On-demand: trigger `fetch` when needed; handle cancellation, low storage, Wi‑Fi-only policies, and retries.

### 6. Updates without Full Releases

- Leverage asset-only updates via Play Console to push new/updated assets without a full app release (within PAD constraints).
- Version assets (e.g., semantic versioning) and keep safe fallbacks in base install-time assets.
- For A/B tests, map asset versions to remote-config/feature-flag values controlling which packs to use.

### 7. Monitoring and Responsiveness

- Monitor delivery health via Play Console (Delivery insights) and Play Developer Reporting API.
- Track download success/failure reasons (e.g., insufficient storage) and show actionable messages to users.
- Log time-to-ready metrics and validate against UX/SLO targets.

### 8. Offline Behavior and Fallbacks

- Keep a minimal critical asset set as install-time.
- On on-demand failure, notify the user, retry with backoff, and gracefully degrade (e.g., lower-quality resources or reduced features).
- Optionally prefetch expected asset packs over Wi‑Fi using background work (e.g., `WorkManager`).

### 9. Compliance and QA

- Validate PAD flows using Play Internal Testing tracks.
- Run size regression checks (e.g., with `bundletool`).
- Document asset update flows and licensing constraints (third-party media, fonts, textures).

---

## Дополнительные Вопросы (RU)
- Как совместить PAD с собственной CDN fallback (для сторонних сторов)?
- Как распределять ассеты между device tier (low-end vs high-end)?
- Какие стратегии для локализации ассетов (языки, региональные правовые ограничения)?

## Follow-ups
- How to combine PAD with your own CDN fallback (for alternative stores)?
- How to distribute assets across device tiers (low-end vs high-end)?
- What strategies to use for asset localization (languages, regional legal constraints)?

## Ссылки (RU)
- [[c-app-bundle]]
- https://developer.android.com/guide/playcore/asset-delivery

## References
- [[c-app-bundle]]
- https://developer.android.com/guide/playcore/asset-delivery

## Related Questions

- [[q-android-app-bundles--android--easy]]