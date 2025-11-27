---
id: android-488
title: Design Feature Flags & Experimentation SDK / Проектирование SDK флагов и экспериментов
aliases: [Experimentation SDK, Feature Flags SDK]
topic: android
subtopics:
  - architecture-clean
  - networking-http
  - service
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-clean-architecture
  - c-dependency-injection
  - c-workmanager
  - q-data-sync-unstable-network--android--hard
  - q-design-instagram-stories--android--hard
  - q-design-uber-app--android--hard
sources:
  - "https://developer.android.com/topic/architecture"
created: 2025-10-29
updated: 2025-11-10
tags: [android/architecture-clean, android/networking-http, android/service, difficulty/hard, experimentation, feature-flags, sdk-design]

date created: Saturday, November 1st 2025, 12:46:49 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)

> Как спроектировать SDK флагов функций и экспериментов для Android?

## Краткая Версия
Спроектируйте SDK флагов функций для Android. Основные требования: динамическое включение/выключение функций, A/B тестирование, <150мс bootstrap, sticky assignments, офлайн кеш с TTL, kill-switch семантика, privacy-safe exposure logging.

## Подробная Версия
Спроектируйте полноценный SDK флагов функций и экспериментов для Android со следующими требованиями:

**Производительность:**
- Bootstrap <150мс при холодном старте
- Sticky assignments для consistent user experience
- Офлайн кеш с TTL для работы без сети

**Функциональность:**
- Динамическое включение/выключение функций
- A/B тестирование с targeting rules
- Kill-switch для мгновенного отключения функций
- Privacy-safe exposure logging

**Надежность:**
- Градуальный rollout с автоматическим откатом
- Schema versioning для backward compatibility
- Security: signed configs, encrypted storage

**Наблюдаемость:**
- Метрики bootstrap latency, cache hit rate, evaluation errors
- Health-gated deployment
- Distributed tracing для debugging

# Question (EN)

> How to design a feature flags & experimentation SDK for Android?

## Short Version
Design a feature flags SDK for Android. Key requirements: dynamic feature toggles, A/B testing, <150ms bootstrap, sticky assignments, offline cache with TTL, kill-switch semantics, privacy-safe exposure logging.

## Detailed Version
Design a complete feature flags & experimentation SDK for Android with the following requirements:

**Performance:**
- Bootstrap <150ms on cold start
- Sticky assignments for consistent user experience
- Offline cache with TTL for network-independent operation

**Functionality:**
- Dynamic feature enable/disable
- A/B testing with targeting rules
- Kill-switch for instant feature disable
- Privacy-safe exposure logging

**Reliability:**
- Gradual rollout with automatic rollback
- Schema versioning for backward compatibility
- Security: signed configs, encrypted storage

**Observability:**
- Metrics for bootstrap latency, cache hit rate, evaluation errors
- Health-gated deployment
- Distributed tracing for debugging

## Ответ (RU)

SDK флагов функций обеспечивает динамическое включение/выключение функций и A/B тестирование без необходимости релиза приложения.

### Теоретические Основы

**Флаги функций** — это механизм декоплинга развертывания кода от выпуска функций. Позволяет выпускать код заранее, а включать функциональность динамически через конфигурацию.

**A/B тестирование** — метод сравнения двух версий функциональности для определения лучшей. Основывается на статистическом анализе конверсии, retention, engagement метрик.

**Sticky assignments** — гарантия consistent user experience. Пользователь всегда попадает в одну и ту же группу эксперимента независимо от устройства/сессии (детерминированное распределение по стабильному идентификатору).

**Kill-switch** — механизм мгновенного отключения проблемных функций без обновления приложения. Критично для поддержания availability при production incidents.

**Gradual rollout** — поэтапное включение функций для минимизации рисков. Начинается с 1% пользователей, постепенно увеличивается с мониторингом метрик.

**Targeting rules** — условия определения группы пользователей для эксперимента. Включает географию, версию приложения, тип устройства, cohort analysis.

**Schema versioning** — механизм поддержки backward compatibility при изменении структуры флагов. Использует semantic versioning и migration strategies.

**Exposure logging** — запись факта показа пользователю определенной версии функциональности. Необходим для статистического анализа экспериментов.

### Требования

**Функциональные требования:**
- Управление флагами функций и конфигурацией экспериментов на стороне сервера
- Динамическая загрузка и обновление конфигов без релиза приложения
- Sticky assignments и детерминированный bucketing
- Поддержка A/B и много вариантных экспериментов
- Targeting rules по атрибутам пользователя и устройства
- Kill-switch для мгновенного отключения критичных функций
- Локальный офлайн-кеш с TTL и безопасными дефолтами
- Логирование экспозиций и результатов для аналитики

**Нефункциональные требования:**
- Bootstrap <150мс на холодном старте за счет локального кеша
- Высокая надежность: предсказуемое поведение при сетевых сбоях
- Безопасность: подпись конфигов, защищенное хранение
- Конфиденциальность: отсутствие PII в телеметрии
- Масштабируемость: поддержка большого числа флагов и запросов
- Наблюдаемость: метрики, логи, трассировка для диагностики
- Обратная совместимость через версионирование схемы

### Архитектура

Модульная архитектура с чётким разделением ответственности:

```kotlin
// Core interfaces для dependency injection
interface FeatureFlags {
    fun isEnabled(flag: String): Boolean
    fun getVariant(flag: String, userId: String?): String
    suspend fun refresh(): Result<Unit>
}

interface FlagEvaluator {
    fun evaluate(rule: Rule, context: EvaluationContext): Variant
}

interface FlagStore {
    suspend fun getConfig(): Config?
    suspend fun saveConfig(config: Config)
    fun isExpired(config: Config): Boolean
}
```

Модули: `flags-core`, `evaluator`, `store`, `network`, `telemetry`, `flags-ui`. Contract tests для rule evaluation.

### Bootstrap (<150мс)

Критично для UX — пользователи не должны ждать загрузки флагов.

```kotlin
class FlagBootstrapper(
    private val store: FlagStore,
    private val network: FlagNetworkClient,
    private val scope: CoroutineScope,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun bootstrap(): Config {
        return withContext(dispatcher) {
            // 1. Load last good config from disk (<150ms target)
            val cached = store.getConfig()
            if (cached != null && !store.isExpired(cached)) {
                // Fire-and-forget async refresh in background using provided scope
                scope.launch { refreshInBackground(cached) }
                return@withContext cached
            }

            // 2. Fetch update synchronously as fallback
            val fresh = network.fetchConfig(etag = cached?.etag)
            if (fresh != null) {
                store.saveConfig(fresh)
                return@withContext fresh
            }

            // 3. Failsafe defaults (must be local and fast)
            return@withContext getFailsafeDefaults()
        }
    }

    private suspend fun refreshInBackground(cached: Config?) {
        val fresh = network.fetchConfig(etag = cached?.etag)
        if (fresh != null) {
            store.saveConfig(fresh)
        }
    }
}
```

`FlagNetworkClient`, `Config` (включая поле `etag`) и `getFailsafeDefaults()` подразумеваются как часть SDK контракта и должны быть определены отдельно. Важно: для фонового обновления используется явный `CoroutineScope`.

### Evaluation Engine

Детерминированное bucketing для consistent user experience:

```kotlin
class HashEvaluator : FlagEvaluator {
    override fun evaluate(rule: Rule, context: EvaluationContext): Variant {
        val key = "${rule.flagId}:${context.userId ?: "anon"}"
        val hash = murmurHash32(key)
        val bucket = (hash.toLong() and 0xffffffffL) % 100 // 0..99

        return when {
            !rule.enabled -> Variant.DISABLED
            bucket < rule.rolloutPercent -> rule.variantA
            else -> rule.variantB
        }
    }
}

// Usage
val variant = evaluator.evaluate(
    rule = Rule("checkout_flow", enabled = true, rolloutPercent = 50),
    context = EvaluationContext(userId = "user123")
)
```

`murmurHash32` — любая детерминированная реализация (клиент/сервер должны совпадать).

### Cache & Offline Support

Robust offline handling с TTL и fallback стратегиями:

```kotlin
@Entity
data class CachedConfig(
    @PrimaryKey val id: String = "flags",
    val configJson: String,
    val etag: String?,
    val fetchedAt: Long,
    val ttlMs: Long = 3600000 // 1 hour
) {
    fun isExpired(now: Long = System.currentTimeMillis()): Boolean =
        now - fetchedAt > ttlMs
}

class RoomFlagStore(private val dao: FlagDao) : FlagStore {
    override suspend fun getConfig(): Config? {
        val cached = dao.getLatest() ?: return null
        return if (!cached.isExpired()) {
            Json.decodeFromString<Config>(cached.configJson)
        } else {
            null
        }
    }

    override suspend fun saveConfig(config: Config) {
        val cached = CachedConfig(
            configJson = Json.encodeToString(config),
            etag = config.etag,
            fetchedAt = System.currentTimeMillis()
        )
        dao.insert(cached)
    }

    override fun isExpired(config: Config): Boolean {
        // В примере TTL/expiration реализованы через CachedConfig.
        // В production-реализации следует последовательно применять
        // единую стратегию истечения срока действия (например, через metadata).
        return false
    }
}
```

В реальной реализации TTL/expiration должна быть согласованной: либо через метаданные `CachedConfig`, либо через поля `Config`, без дублирования логики.

### Kill-Switch

Мгновенное отключение критичных функций через dedicated remote flag. Push (например, FCM) используется только как ускоритель обновления, а не единственный источник истины:

```kotlin
class KillSwitchManager(
    private val flags: FeatureFlags,
    private val fcm: FirebaseMessaging = FirebaseMessaging.getInstance()
) {
    init {
        // FCM nudge for instant updates (best effort)
        fcm.subscribeToTopic("kill_switch")
    }

    fun isFeatureDisabled(feature: String): Boolean {
        // Если включен kill_switch_<feature>, считаем фичу отключенной
        return flags.isEnabled("kill_switch_$feature")
    }
}
```

### Telemetry & Privacy

PII-safe exposure logging с буферизацией и периодическим сбросом. Не логировать прямые идентификаторы пользователя; использовать стабильные псевдонимизированные идентификаторы или агрегированные события.

### Security & Encryption

Защита конфигураций через `EncryptedSharedPreferences` (пример концептуальный; реализация интерфейса должна быть полной):

```kotlin
class SecureFlagStore(private val context: Context) : FlagStore {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "flags_secure",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    override suspend fun getConfig(): Config? {
        val json = encryptedPrefs.getString("config", null) ?: return null
        return Json.decodeFromString<Config>(json)
    }

    override suspend fun saveConfig(config: Config) {
        encryptedPrefs.edit()
            .putString("config", Json.encodeToString(config))
            .apply()
    }

    override fun isExpired(config: Config): Boolean {
        // TTL/expiration может храниться внутри Config или в отдельных метаданных.
        // Важно, чтобы стратегия была согласованной с bootstrap и cache.
        return false
    }
}
```

### Observability

Key metrics for production reliability: bootstrap latency (<150ms), cache hit rate (>95%), evaluation errors (<0.1%), exposure volume, config fetch success.

### Лучшие Практики

- **Versioned evaluators** — каждый rule имеет версию для backward compatibility
- **Contract tests** — shared test suite между client/server для rule evaluation
- **Gradual rollout** — health-gated deployment с automatic rollback
- **Schema migration** — protobuf для efficient serialization и versioning
- **Fail-safe defaults** — graceful degradation при network issues

### Типичные Ошибки

- **Non-deterministic evaluation** — приводит к inconsistent user experience
- **PII in telemetry** — нарушает privacy regulations
- **No offline fallback** — app broken when network unavailable
- **Large config payloads** — slow bootstrap и battery drain
- **Missing kill switches** — невозможно быстро отключить buggy features

## Answer (EN)

Feature flags SDK enables dynamic feature toggles and A/B testing without requiring app releases.

### Theoretical Foundations

**Feature flags** — a mechanism for decoupling code deployment from feature release. Allows shipping code early and enabling functionality dynamically via configuration.

**A/B testing** — method for comparing two versions of functionality to determine the better one. Based on statistical analysis of conversion, retention, engagement metrics.

**Sticky assignments** — guarantee of consistent user experience via deterministic bucketing. A user always lands in the same experiment group across sessions/devices when using a stable identifier.

**Kill-switch** — mechanism for instantly disabling problematic features without app updates. Critical for maintaining availability during production incidents.

**Gradual rollout** — phased feature enablement to minimize risks. Starts with 1% of users, gradually increases while monitoring metrics.

**Targeting rules** — conditions for determining user groups for experiments. Includes geography, app version, device type, cohort analysis.

**Schema versioning** — mechanism for maintaining backward compatibility when flag structure changes. Uses semantic versioning and migration strategies.

**Exposure logging** — recording when a user is shown a specific version of functionality. Required for statistical analysis of experiments.

### Requirements

**Functional requirements:**
- Server-side management of feature flags and experiment configs
- Dynamic loading and updating of configs without app releases
- Sticky assignments and deterministic bucketing
- Support for A/B and multivariate experiments
- Targeting rules based on user/device attributes
- Kill-switch for instant shutdown of critical features
- Local offline cache with TTL and safe defaults
- Exposure and result logging for analytics

**Non-functional requirements:**
- Bootstrap <150ms on cold start via local cache
- High reliability: predictable behavior under network failures
- Security: signed configs, protected storage
- Privacy: no PII in telemetry
- Scalability: support many flags and high request volume
- Observability: metrics, logs, tracing for diagnostics
- Backward compatibility via schema versioning

### Architecture

Modular architecture with clear separation of concerns:

```kotlin
// Core interfaces for dependency injection
interface FeatureFlags {
    fun isEnabled(flag: String): Boolean
    fun getVariant(flag: String, userId: String?): String
    suspend fun refresh(): Result<Unit>
}

interface FlagEvaluator {
    fun evaluate(rule: Rule, context: EvaluationContext): Variant
}

interface FlagStore {
    suspend fun getConfig(): Config?
    suspend fun saveConfig(config: Config)
    fun isExpired(config: Config): Boolean
}
```

Modules: `flags-core`, `evaluator`, `store`, `network`, `telemetry`, `flags-ui`. Contract tests for rule evaluation.

### Bootstrap (<150ms)

Critical for UX — users should not wait for flag loading.

```kotlin
class FlagBootstrapper(
    private val store: FlagStore,
    private val network: FlagNetworkClient,
    private val scope: CoroutineScope,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun bootstrap(): Config {
        return withContext(dispatcher) {
            // 1. Load last good config from disk (<150ms target)
            val cached = store.getConfig()
            if (cached != null && !store.isExpired(cached)) {
                // Fire-and-forget async refresh in background using provided scope
                scope.launch { refreshInBackground(cached) }
                return@withContext cached
            }

            // 2. Fetch update synchronously as fallback
            val fresh = network.fetchConfig(etag = cached?.etag)
            if (fresh != null) {
                store.saveConfig(fresh)
                return@withContext fresh
            }

            // 3. Failsafe defaults (local, fast)
            return@withContext getFailsafeDefaults()
        }
    }

    private suspend fun refreshInBackground(cached: Config?) {
        val fresh = network.fetchConfig(etag = cached?.etag)
        if (fresh != null) {
            store.saveConfig(fresh)
        }
    }
}
```

`FlagNetworkClient`, `Config` (including `etag`) and `getFailsafeDefaults()` are part of the SDK contract and must be defined elsewhere. Note: background refresh uses an explicit `CoroutineScope`.

### Evaluation Engine

Deterministic bucketing for consistent user experience:

```kotlin
class HashEvaluator : FlagEvaluator {
    override fun evaluate(rule: Rule, context: EvaluationContext): Variant {
        val key = "${rule.flagId}:${context.userId ?: "anon"}"
        val hash = murmurHash32(key)
        val bucket = (hash.toLong() and 0xffffffffL) % 100 // 0..99

        return when {
            !rule.enabled -> Variant.DISABLED
            bucket < rule.rolloutPercent -> rule.variantA
            else -> rule.variantB
        }
    }
}

// Usage
val variant = evaluator.evaluate(
    rule = Rule("checkout_flow", enabled = true, rolloutPercent = 50),
    context = EvaluationContext(userId = "user123")
)
```

`murmurHash32` is any deterministic implementation shared between client and server.

### Cache & Offline Support

Robust offline handling with TTL and fallback strategies:

```kotlin
@Entity
data class CachedConfig(
    @PrimaryKey val id: String = "flags",
    val configJson: String,
    val etag: String?,
    val fetchedAt: Long,
    val ttlMs: Long = 3600000 // 1 hour
) {
    fun isExpired(now: Long = System.currentTimeMillis()): Boolean =
        now - fetchedAt > ttlMs
}

class RoomFlagStore(private val dao: FlagDao) : FlagStore {
    override suspend fun getConfig(): Config? {
        val cached = dao.getLatest() ?: return null
        return if (!cached.isExpired()) {
            Json.decodeFromString<Config>(cached.configJson)
        } else {
            null
        }
    }

    override suspend fun saveConfig(config: Config) {
        val cached = CachedConfig(
            configJson = Json.encodeToString(config),
            etag = config.etag,
            fetchedAt = System.currentTimeMillis()
        )
        dao.insert(cached)
    }

    override fun isExpired(config: Config): Boolean {
        // In this example, expiration is implemented via CachedConfig metadata.
        // In production, choose a single consistent expiration strategy.
        return false
    }
}
```

In a real implementation, TTL/expiration logic should be consistently defined either via cache metadata or fields on Config, without duplicating or ignoring it.

### Kill-Switch

Instant disabling of critical features via dedicated remote flag. Push (e.g., FCM) is only a nudge, not the source of truth:

```kotlin
class KillSwitchManager(
    private val flags: FeatureFlags,
    private val fcm: FirebaseMessaging = FirebaseMessaging.getInstance()
) {
    init {
        // FCM nudge for instant updates (best effort)
        fcm.subscribeToTopic("kill_switch")
    }

    fun isFeatureDisabled(feature: String): Boolean {
        // If kill_switch_<feature> is enabled, treat the feature as disabled
        return flags.isEnabled("kill_switch_$feature")
    }
}
```

### Telemetry & Privacy

PII-safe exposure logging with buffered flushing. Do not log raw user identifiers; use stable pseudonymous IDs or aggregated metrics.

### Security & Encryption

Protecting configs via `EncryptedSharedPreferences` (example is conceptual; implementation must fully satisfy FlagStore contract):

```kotlin
class SecureFlagStore(private val context: Context) : FlagStore {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "flags_secure",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    override suspend fun getConfig(): Config? {
        val json = encryptedPrefs.getString("config", null) ?: return null
        return Json.decodeFromString<Config>(json)
    }

    override suspend fun saveConfig(config: Config) {
        encryptedPrefs.edit()
            .putString("config", Json.encodeToString(config))
            .apply()
    }

    override fun isExpired(config: Config): Boolean {
        // TTL/expiration can be implemented using Config or separate metadata.
        // Ensure alignment with bootstrap and cache behavior.
        return false
    }
}
```

### Observability

Key metrics for production reliability: bootstrap latency (<150ms), cache hit rate (>95%), evaluation errors (<0.1%), exposure volume, config fetch success.

### Best Practices

- **Versioned evaluators** — each rule has version for backward compatibility
- **Contract tests** — shared test suite between client/server for rule evaluation
- **Gradual rollout** — health-gated deployment with automatic rollback
- **Schema migration** — protobuf for efficient serialization and versioning
- **Fail-safe defaults** — graceful degradation during network issues

### Common Pitfalls

- **Non-deterministic evaluation** — leads to inconsistent user experience
- **PII in telemetry** — violates privacy regulations
- **No offline fallback** — app broken when network unavailable
- **Large config payloads** — slow bootstrap and battery drain
- **Missing kill switches** — impossible to quickly disable buggy features

---

## Follow-ups

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [[c-workmanager]]

## References

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [[c-workmanager]]

## Related Questions

- [[c-clean-architecture]]
- [[c-dependency-injection]]
- [[c-workmanager]]

## Ссылки (RU)
## Дополнительные Вопросы (RU)