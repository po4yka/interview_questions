---
id: android-488
title: Design Feature Flags & Experimentation SDK / Проектирование SDK флагов и экспериментов
aliases:
  - Feature Flags SDK
  - Experimentation SDK
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
status: reviewed
moc: moc-android
related:
  - c-clean-architecture
  - c-dependency-injection
  - c-workmanager
sources:
  - https://developer.android.com/topic/architecture
created: 2025-10-29
updated: 2025-11-03
tags:
  - android/architecture-clean
  - android/networking-http
  - android/service
  - difficulty/hard
  - feature-flags
  - experimentation
  - sdk-design
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

### Теоретические основы

**Флаги функций** — это механизм декоплинга развертывания кода от выпуска функций. Позволяет выпускать код заранее, а включать функциональность динамически через конфигурацию.

**A/B тестирование** — метод сравнения двух версий функциональности для определения лучшей. Основывается на статистическом анализе конверсии, retention, engagement метрик.

**Sticky assignments** — гарантия consistent user experience. Пользователь всегда попадает в одну и ту же группу эксперимента независимо от устройства/сессии.

**Kill-switch** — механизм мгновенного отключения проблемных функций без обновления приложения. Критично для поддержания availability при production incidents.

**Gradual rollout** — поэтапное включение функций для минимизации рисков. Начинается с 1% пользователей, постепенно увеличивается с мониторингом метрик.

**Targeting rules** — условия определения группы пользователей для эксперимента. Включает географию, версию приложения, тип устройства, cohort analysis.

**Schema versioning** — механизм поддержки backward compatibility при изменении структуры флагов. Использует semantic versioning и migration strategies.

**Exposure logging** — запись факта показа пользователю определенной версии функциональности. Необходим для статистического анализа экспериментов.

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
    fun isExpired(): Boolean
}
```

Модули: `flags-core`, `evaluator`, `store`, `network`, `telemetry`, `flags-ui`. Contract tests для rule evaluation.

### Bootstrap (<150мс)

Критично для UX — пользователи не должны ждать загрузки флагов.

```kotlin
class FlagBootstrapper(
    private val store: FlagStore,
    private val network: FlagNetworkClient,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun bootstrap(): Config {
        // 1. Load last good config from disk (<150ms target)
        val cached = store.getConfig()
        cached?.let { if (!store.isExpired()) return it }

        // 2. Async fetch update (lazy loading)
        val fresh = network.fetchConfig(ETag = cached?.etag)
        fresh?.let { store.saveConfig(it) }

        return fresh ?: cached ?: getFailsafeDefaults()
    }
}
```

### Evaluation Engine

Детерминированное bucketing для consistent user experience:

```kotlin
class HashEvaluator : FlagEvaluator {
    override fun evaluate(rule: Rule, context: EvaluationContext): Variant {
        val hash = MurmurHash3.hash128("${rule.flagId}:${context.userId}")
        val bucket = (hash % 100).toInt()

        return when {
            rule.enabled == false -> Variant.DISABLED
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
)

class RoomFlagStore(private val dao: FlagDao) : FlagStore {
    override suspend fun getConfig(): Config? {
        val cached = dao.getLatest()
        return if (cached?.isExpired() == false) {
            Json.decodeFromString(cached.configJson)
        } else null
    }

    override suspend fun saveConfig(config: Config) {
        dao.insert(CachedConfig(
            configJson = Json.encodeToString(config),
            etag = config.etag,
            fetchedAt = System.currentTimeMillis()
        ))
    }
}
```

### Kill-Switch

Мгновенное отключение критичных функций через dedicated remote flag:

```kotlin
class KillSwitchManager(
    private val flags: FeatureFlags,
    private val fcm: FirebaseMessaging = FirebaseMessaging.getInstance()
) {
    init {
        // FCM nudge for instant updates
        fcm.subscribeToTopic("kill_switch")
    }

    fun shouldDisableFeature(feature: String): Boolean {
        // Check kill switch first
        if (flags.isEnabled("kill_switch_$feature")) {
            return true
        }
        return false
    }
}
```

### Telemetry & Privacy

PII-safe exposure logging с buffered flushing.

### Security & Encryption

Защита конфигураций через `EncryptedSharedPreferences`:

```kotlin
class SecureFlagStore(private val context: Context) : FlagStore {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    override suspend fun saveConfig(config: Config) {
        val encryptedPrefs = EncryptedSharedPreferences.create(
            context, "flags_secure", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
        encryptedPrefs.edit()
            .putString("config", Json.encodeToString(config))
            .apply()
    }
}
```

### Observability

Key metrics for production reliability: bootstrap latency (<150ms), cache hit rate (>95%), evaluation errors (<0.1%), exposure volume, config fetch success.

### Лучшие практики

- **Versioned evaluators** — каждый rule имеет версию для backward compatibility
- **Contract tests** — shared test suite между client/server для rule evaluation
- **Gradual rollout** — health-gated deployment с automatic rollback
- **Schema migration** — protobuf для efficient serialization и versioning
- **Fail-safe defaults** — graceful degradation при network issues

### Типичные ошибки

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

**Sticky assignments** — guarantee of consistent user experience. User always lands in the same experiment group regardless of device/session.

**Kill-switch** — mechanism for instantly disabling problematic features without app updates. Critical for maintaining availability during production incidents.

**Gradual rollout** — phased feature enablement to minimize risks. Starts with 1% of users, gradually increases while monitoring metrics.

**Targeting rules** — conditions for determining user groups for experiments. Includes geography, app version, device type, cohort analysis.

**Schema versioning** — mechanism for maintaining backward compatibility when flag structure changes. Uses semantic versioning and migration strategies.

**Exposure logging** — recording when a user is shown a specific version of functionality. Required for statistical analysis of experiments.

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
    fun isExpired(): Boolean
}
```

Modules: `flags-core`, `evaluator`, `store`, `network`, `telemetry`, `flags-ui`. Contract tests for rule evaluation.

### Bootstrap (<150ms)

Critical for UX — users shouldn't wait for flag loading.

```kotlin
class FlagBootstrapper(
    private val store: FlagStore,
    private val network: FlagNetworkClient,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun bootstrap(): Config {
        // 1. Load last good config from disk (<150ms target)
        val cached = store.getConfig()
        cached?.let { if (!store.isExpired()) return it }

        // 2. Async fetch update (lazy loading)
        val fresh = network.fetchConfig(ETag = cached?.etag)
        fresh?.let { store.saveConfig(it) }

        return fresh ?: cached ?: getFailsafeDefaults()
    }
}
```

### Evaluation Engine

Deterministic bucketing for consistent user experience:

```kotlin
class HashEvaluator : FlagEvaluator {
    override fun evaluate(rule: Rule, context: EvaluationContext): Variant {
        val hash = MurmurHash3.hash128("${rule.flagId}:${context.userId}")
        val bucket = (hash % 100).toInt()

        return when {
            rule.enabled == false -> Variant.DISABLED
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
)

class RoomFlagStore(private val dao: FlagDao) : FlagStore {
    override suspend fun getConfig(): Config? {
        val cached = dao.getLatest()
        return if (cached?.isExpired() == false) {
            Json.decodeFromString(cached.configJson)
        } else null
    }

    override suspend fun saveConfig(config: Config) {
        dao.insert(CachedConfig(
            configJson = Json.encodeToString(config),
            etag = config.etag,
            fetchedAt = System.currentTimeMillis()
        ))
    }
}
```

### Kill-Switch

Instant disabling of critical features via dedicated remote flag:

```kotlin
class KillSwitchManager(
    private val flags: FeatureFlags,
    private val fcm: FirebaseMessaging = FirebaseMessaging.getInstance()
) {
    init {
        // FCM nudge for instant updates
        fcm.subscribeToTopic("kill_switch")
    }

    fun shouldDisableFeature(feature: String): Boolean {
        // Check kill switch first
        if (flags.isEnabled("kill_switch_$feature")) {
            return true
        }
        return false
    }
}
```

### Telemetry & Privacy

PII-safe exposure logging with buffered flushing.

### Security & Encryption

Protecting configs via `EncryptedSharedPreferences`:

```kotlin
class SecureFlagStore(private val context: Context) : FlagStore {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    override suspend fun saveConfig(config: Config) {
        val encryptedPrefs = EncryptedSharedPreferences.create(
            context, "flags_secure", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
        encryptedPrefs.edit()
            .putString("config", Json.encodeToString(config))
            .apply()
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

## References

-   [[c-clean-architecture]]
-   [[c-dependency-injection]]
-   [[c-workmanager]]
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]
