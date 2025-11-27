---
id: sd-001
title: "Softcode Vs Hardcode / Softcode против Hardcode"
aliases: [Softcode Vs Hardcode, Softcode против Hardcode]
topic: cs
subtopics: [architecture, clean-code, configuration]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns, q-abstract-factory-pattern--cs--medium]
created: 2025-10-13
updated: 2025-11-11
tags: [configuration, cs, difficulty/medium, flexibility, hardcoding, maintainability, softcoding]

date created: Tuesday, November 25th 2025, 12:56:01 pm
date modified: Tuesday, November 25th 2025, 8:53:53 pm
---
# Вопрос (RU)
> Что такое софткод и чем он отличается от хардкода?

# Question (EN)
> What is softcode and how is it different from hardcode?

## Ответ (RU)

Софткод (Softcode, Soft Coding) — это подход к проектированию, при котором поведение и настройки системы делают конфигурируемыми через внешние источники (конфигурационные файлы, переменные окружения, удалённый конфиг, базы данных, feature flags и т.п.), вместо жёсткого (hardcoded) вшивания всех значений в код. Базовая логика и инварианты остаются в коде, а внешними делают только те параметры и правила, которые ожидаемо могут меняться.

Ниже — детальное сравнение с хардкодом и примеры.

### Хардкод Против Софткода

#### Хардкод (Hard Coding)

Хардкод — это запись фиксированных значений или логики напрямую в исходный код.

Пример хардкода:

```kotlin
class PaymentProcessor {
    fun calculateFee(amount: Double): Double {
        // Тариф комиссии захардкожен
        return amount * 0.03  // 3% комиссия
    }

    fun getApiUrl(): String {
        // URL захардкожен
        return "https://api.payment.com/v1"
    }

    fun getMaxRetries(): Int {
        // Максимальное число ретраев захардкожено
        return 3
    }

    fun getSupportedCurrencies(): List<String> {
        // Поддерживаемые валюты захардкожены
        return listOf("USD", "EUR", "GBP")
    }
}
```

Проблемы хардкода:
- Любое изменение требует правки кода и релиза
- Сложно задавать разные значения для dev/staging/production
- Нельзя гибко менять поведение без пересборки
- Бизнес-правила смешаны с реализацией и медленно адаптируются

#### Софткод (Soft Coding)

Софткод — это вынос настраиваемых значений и правил во внешние источники, чтобы менять поведение без изменения и перезагрузки кода.

Пример софткода:

```kotlin
// NOTE: демонстрационный пример; предполагаются нужные импорты и настройка

// Конфигурация хранится во внешнем источнике
@kotlinx.serialization.Serializable
class AppConfig(
    val paymentFeeRate: Double,
    val apiUrl: String,
    val maxRetries: Int,
    val supportedCurrencies: List<String>
)

// Загрузка из JSON-файла
class ConfigLoader {
    fun loadConfig(): AppConfig {
        val json = java.io.File("config.json").readText()
        return kotlinx.serialization.json.Json.decodeFromString<AppConfig>(json)
    }
}

// config.json
/*
{
  "paymentFeeRate": 0.03,
  "apiUrl": "https://api.payment.com/v1",
  "maxRetries": 3,
  "supportedCurrencies": ["USD", "EUR", "GBP"]
}
*/

// Использование
class PaymentProcessor(private val config: AppConfig) {
    fun calculateFee(amount: Double): Double {
        // Тариф берётся из конфигурации
        return amount * config.paymentFeeRate
    }

    fun getApiUrl(): String {
        // URL берётся из конфигурации
        return config.apiUrl
    }

    fun getMaxRetries(): Int {
        // Максимальное число ретраев берётся из конфигурации
        return config.maxRetries
    }

    fun getSupportedCurrencies(): List<String> {
        // Валюты берутся из конфигурации
        return config.supportedCurrencies
    }
}
```

Преимущества софткода:
- Можно менять значения без пересборки
- Удобно задавать разные конфиги для окружений
- Конфигурацией могут управлять ops/бизнес через панели/сервисы
- Проще реализовать A/B-тесты и feature flags

---

### Типичные Источники Софткода

#### 1. Конфигурационные Файлы

JSON, YAML, TOML, properties-файлы.

```kotlin
// application.properties
/*
payment.fee.rate=0.03
api.url=https://api.payment.com/v1
max.retries=3
supported.currencies=USD,EUR,GBP
*/

// Загрузка из properties (упрощено)
class PropertiesConfigLoader {
    fun loadConfig(): AppConfig {
        val props = java.util.Properties()
        props.load(java.io.FileInputStream("application.properties"))

        return AppConfig(
            paymentFeeRate = props.getProperty("payment.fee.rate").toDouble(),
            apiUrl = props.getProperty("api.url"),
            maxRetries = props.getProperty("max.retries").toInt(),
            supportedCurrencies = props.getProperty("supported.currencies").split(",")
        )
    }
}
```

#### 2. Переменные Окружения

```kotlin
// Чтение из переменных окружения (упрощено; в реальном коде нужна валидация)
class EnvConfigLoader {
    fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = System.getenv("PAYMENT_FEE_RATE")?.toDoubleOrNull() ?: 0.03,
            apiUrl = System.getenv("API_URL") ?: "https://api.payment.com/v1",
            maxRetries = System.getenv("MAX_RETRIES")?.toIntOrNull() ?: 3,
            supportedCurrencies = System.getenv("SUPPORTED_CURRENCIES")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}

// Примеры:
// export PAYMENT_FEE_RATE=0.025
// export API_URL=https://api.staging.payment.com/v1
// export MAX_RETRIES=5
```

Используется для:
- Настроек контейнеров, Kubernetes/Docker
- CI/CD-конфигураций
- Секретов (через менеджер секретов + env)

#### 3. Удалённая Конфигурация

```kotlin
// Firebase Remote Config (упрощено)
class RemoteConfigLoader(private val remoteConfig: FirebaseRemoteConfig) {

    suspend fun loadConfig(): AppConfig {
        remoteConfig.fetchAndActivate().await()

        val supportedCurrenciesRaw = remoteConfig.getString("supported_currencies")

        return AppConfig(
            paymentFeeRate = remoteConfig.getDouble("payment_fee_rate"),
            apiUrl = remoteConfig.getString("api_url"),
            maxRetries = remoteConfig.getLong("max_retries").toInt(),
            supportedCurrencies = if (supportedCurrenciesRaw.isNotEmpty())
                supportedCurrenciesRaw.split(",")
            else
                listOf("USD", "EUR", "GBP")
        )
    }
}

// Преимущества:
// - Обновление конфигурации без обновления приложения
// - A/B-тесты
// - Feature flags
// - Персонализация по сегментам
```

#### 4. База Данных

```kotlin
// Хранение конфигурации в БД (пример на Room, упрощённый)
@Entity(tableName = "app_config")
data class ConfigEntity(
    @PrimaryKey val key: String,
    val value: String
)

@Dao
interface ConfigDao {
    @Query("SELECT value FROM app_config WHERE key = :key")
    suspend fun getValue(key: String): String?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun setValue(config: ConfigEntity)
}

// Загрузка из БД
class DatabaseConfigLoader(private val configDao: ConfigDao) {

    suspend fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = configDao.getValue("payment_fee_rate")?.toDoubleOrNull() ?: 0.03,
            apiUrl = configDao.getValue("api_url") ?: "https://api.payment.com/v1",
            maxRetries = configDao.getValue("max_retries")?.toIntOrNull() ?: 3,
            supportedCurrencies = configDao.getValue("supported_currencies")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}
```

---

### Когда Использовать Софткод И Когда Хардкод

Используем софткод для:

1. Конфигурационных значений, которые могут меняться:
   ```kotlin
   val apiUrl = config.getApiUrl()
   val timeoutMs = config.getTimeout()
   val maxRetries = config.getMaxRetries()
   ```

2. Значений, зависящих от окружения:
   ```kotlin
   val apiUrl = when (BuildConfig.BUILD_TYPE) {
       "debug" -> config.devApiUrl
       "staging" -> config.stagingApiUrl
       "release" -> config.prodApiUrl
       else -> config.devApiUrl
   }
   ```

3. Бизнес-правил, часто меняющихся продуктовой командой:
   ```kotlin
   val feeRate = remoteConfig.getDouble("payment_fee_rate")
   val minOrderAmount = remoteConfig.getDouble("min_order_amount")
   ```

4. Feature flags:
   ```kotlin
   if (remoteConfig.getBoolean("new_checkout_enabled")) {
       showNewCheckout()
   } else {
       showOldCheckout()
   }
   ```

5. Параметров A/B-тестов:
   ```kotlin
   val buttonColor = remoteConfig.getString("button_color_variant")
   ```

6. Локализуемого контента:
   ```kotlin
   val welcomeMessage = localizationService.getString("welcome_message")
   ```

Используем хардкод для:

1. Фундаментальных констант:
   ```kotlin
   const val PI = 3.14159265359
   const val SPEED_OF_LIGHT = 299792458  // m/s
   ```

2. Стабильной доменной логики:
   ```kotlin
   fun calculateDiscount(price: Double, quantity: Int): Double {
       return if (quantity >= 10) {
           price * 0.9  // 10% скидка
       } else {
           price
       }
   }
   ```

3. Внутренних идентификаторов и констант:
   ```kotlin
   const val REQUEST_CODE_CAMERA = 1001
   const val PERMISSION_REQUEST_CODE = 2001
   ```

4. Идентификаторов `View` и ресурсов:
   ```kotlin
   findViewById<TextView>(R.id.title)
   getString(R.string.app_name)
   ```

---

### Овер-софткодинг (антипаттерн)

Чрезмерный софткодинг вреден.

Плохой пример:

```kotlin
// Всё конфигурируется, даже базовые операции — избыточная гибкость
class Calculator(private val config: CalculatorConfig) {

    fun add(a: Int, b: Int): Int {
        // Даже оператор сложения "настраивается"
        return when (config.additionOperator) {
            "plus" -> a + b
            "concat" -> (a.toString() + b.toString()).toInt()
            else -> 0
        }
    }

    fun multiply(a: Int, b: Int): Int {
        // Ненужная сложность
        return when (config.multiplicationStrategy) {
            "repeated_addition" -> {
                var result = 0
                repeat(b) { result += a }
                result
            }
            "normal" -> a * b
            else -> 0
        }
    }
}
```

Проблемы:
- Лишняя сложность и косвенные уровни
- Потери в производительности
- Код труднее понимать и отлаживать
- Ошибки из-за некорректных конфигураций

Правило: фундаментальные алгоритмы, инварианты и safety-critical логика должны оставаться в коде; во внешние конфиги выносить только то, что ожидаемо меняется.

---

### Android-пример: Система Конфигурации

```kotlin
// Демонстрационный пример; опущены импорты и обработка ошибок

// 1. Data class конфигурации
data class AppConfig(
    val apiBaseUrl: String,
    val apiTimeout: Long,
    val maxRetries: Int,
    val enableAnalytics: Boolean,
    val featureFlags: FeatureFlags
)

data class FeatureFlags(
    val newCheckoutEnabled: Boolean,
    val darkModeEnabled: Boolean,
    val experimentalFeaturesEnabled: Boolean
)

// 2. Репозиторий конфигурации
interface ConfigRepository {
    suspend fun getConfig(): AppConfig
    suspend fun updateConfig(config: AppConfig)
}

class ConfigRepositoryImpl(
    private val remoteConfig: FirebaseRemoteConfig,
    private val localPrefs: SharedPreferences
) : ConfigRepository {

    override suspend fun getConfig(): AppConfig {
        remoteConfig.fetchAndActivate().await()

        return AppConfig(
            apiBaseUrl = remoteConfig.getString("api_base_url")
                .takeIf { it.isNotEmpty() }
                ?: localPrefs.getString("api_base_url", DEFAULT_API_URL)!!,

            apiTimeout = remoteConfig.getLong("api_timeout")
                .takeIf { it > 0 }
                ?: localPrefs.getLong("api_timeout", DEFAULT_TIMEOUT),

            maxRetries = remoteConfig.getLong("max_retries").toInt()
                .takeIf { it > 0 }
                ?: localPrefs.getInt("max_retries", DEFAULT_MAX_RETRIES),

            enableAnalytics = remoteConfig.getBoolean("enable_analytics"),

            featureFlags = FeatureFlags(
                newCheckoutEnabled = remoteConfig.getBoolean("new_checkout_enabled"),
                darkModeEnabled = remoteConfig.getBoolean("dark_mode_enabled"),
                experimentalFeaturesEnabled = remoteConfig.getBoolean("experimental_features_enabled")
            )
        )
    }

    override suspend fun updateConfig(config: AppConfig) {
        localPrefs.edit {
            putString("api_base_url", config.apiBaseUrl)
            putLong("api_timeout", config.apiTimeout)
            putInt("max_retries", config.maxRetries)
        }
    }

    companion object {
        private const val DEFAULT_API_URL = "https://api.myapp.com/v1"
        private const val DEFAULT_TIMEOUT = 30000L
        private const val DEFAULT_MAX_RETRIES = 3
    }
}

// 3. Использование в ViewModel
class MainViewModel(
    private val configRepository: ConfigRepository,
    private val apiService: ApiService
) : ViewModel() {

    private val _config = MutableStateFlow<AppConfig?>(null)
    val config: StateFlow<AppConfig?> = _config.asStateFlow()

    init {
        loadConfig()
    }

    private fun loadConfig() {
        viewModelScope.launch {
            val config = configRepository.getConfig()
            _config.value = config

            apiService.updateBaseUrl(config.apiBaseUrl)
            apiService.updateTimeout(config.apiTimeout)
        }
    }
}

// 4. Использование feature flags в UI
class CheckoutFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.config.collect { config ->
                if (config?.featureFlags?.newCheckoutEnabled == true) {
                    showNewCheckout()
                } else {
                    showOldCheckout()
                }
            }
        }
    }
}
```

---

### Лучшие Практики (RU)

#### Делайте (DO)

1. Используйте софткод для конфигурируемых значений:
   ```kotlin
   val apiUrl = BuildConfig.API_URL
   val timeout = remoteConfig.getLong("timeout")
   ```

2. Задавайте разумные значения по умолчанию:
   ```kotlin
   val maxRetries = config.getInt("max_retries", defaultValue = 3)
   ```

3. Валидируйте конфигурацию:
   ```kotlin
   fun validateConfig(config: AppConfig): Result<Unit> {
       if (config.apiTimeout <= 0) {
           return Result.failure(IllegalArgumentException("Timeout must be positive"))
       }
       return Result.success(Unit)
   }
   ```

4. Используйте типобезопасные конфиги:
   ```kotlin
   data class AppConfig(/* поля */)
   // вместо
   val rawConfig: Map<String, Any>
   ```

#### Не Делайте (DON'T)

1. Не переусердствуйте с софткодом:
   ```kotlin
   // Не стоит конфигурировать базовые операторы и контроль потока
   if (config.getString("comparison_operator") == "equals") { /* ... */ }
   ```

2. Не храните чувствительные данные в небезопасных конфигурациях:
   ```kotlin
   // Избегайте хранения секретов в открытом виде на клиенте
   val apiKey = remoteConfig.getString("api_key")
   ```

3. Не выносите в конфиг то, что стабильно и критично для корректности:
   ```kotlin
   const val MAX_USERNAME_LENGTH = 50
   ```

---

## Answer (EN)

Softcode (soft coding) is a design approach where system behavior and configuration are made configurable through external sources (configuration files, environment variables, remote config, databases, feature flags, etc.) instead of hardcoding all values into the source code. Core logic and invariants remain in code; only parameters and rules expected to change are externalized.

Below is a detailed comparison with hardcoding and aligned examples.

### Hardcode Vs Softcode

#### Hardcode

Hardcoding is putting fixed values or logic directly into source code.

Example of hardcoding:

```kotlin
class PaymentProcessor {
    fun calculateFee(amount: Double): Double {
        // Fee rate is hardcoded
        return amount * 0.03  // 3% fee
    }

    fun getApiUrl(): String {
        // URL is hardcoded
        return "https://api.payment.com/v1"
    }

    fun getMaxRetries(): Int {
        // Max retries are hardcoded
        return 3
    }

    fun getSupportedCurrencies(): List<String> {
        // Supported currencies are hardcoded
        return listOf("USD", "EUR", "GBP")
    }
}
```

Problems with hardcoding:
- Any change requires code modification and release
- Hard to have different values for dev/staging/production
- Cannot flexibly change behavior without rebuild
- Business rules get mixed with implementation and adapt slowly

#### Softcode

Softcoding is moving configurable values and rules into external sources so behavior can change without modifying/redeploying code.

Example of softcoding:

```kotlin
// NOTE: demo example; assumes required imports and setup

// Configuration stored externally
@kotlinx.serialization.Serializable
class AppConfig(
    val paymentFeeRate: Double,
    val apiUrl: String,
    val maxRetries: Int,
    val supportedCurrencies: List<String>
)

// Load from JSON file
class ConfigLoader {
    fun loadConfig(): AppConfig {
        val json = java.io.File("config.json").readText()
        return kotlinx.serialization.json.Json.decodeFromString<AppConfig>(json)
    }
}

// config.json
/*
{
  "paymentFeeRate": 0.03,
  "apiUrl": "https://api.payment.com/v1",
  "maxRetries": 3,
  "supportedCurrencies": ["USD", "EUR", "GBP"]
}
*/

// Usage
class PaymentProcessor(private val config: AppConfig) {
    fun calculateFee(amount: Double): Double {
        // Fee is taken from config
        return amount * config.paymentFeeRate
    }

    fun getApiUrl(): String {
        // URL from config
        return config.apiUrl
    }

    fun getMaxRetries(): Int {
        // Max retries from config
        return config.maxRetries
    }

    fun getSupportedCurrencies(): List<String> {
        // Currencies from config
        return config.supportedCurrencies
    }
}
```

Benefits of softcoding:
- Change values without rebuild
- Easy environment-specific configs
- Ops/product can manage configs via tools/services
- Easier A/B tests and feature flags

---

### Typical Sources of Softcode

#### 1. Configuration Files

JSON, YAML, TOML, properties files.

```kotlin
// application.properties
/*
payment.fee.rate=0.03
api.url=https://api.payment.com/v1
max.retries=3
supported.currencies=USD,EUR,GBP
*/

// Simplified loading from properties
class PropertiesConfigLoader {
    fun loadConfig(): AppConfig {
        val props = java.util.Properties()
        props.load(java.io.FileInputStream("application.properties"))

        return AppConfig(
            paymentFeeRate = props.getProperty("payment.fee.rate").toDouble(),
            apiUrl = props.getProperty("api.url"),
            maxRetries = props.getProperty("max.retries").toInt(),
            supportedCurrencies = props.getProperty("supported.currencies").split(",")
        )
    }
}
```

#### 2. Environment Variables

```kotlin
// Reading from environment variables (simplified; real code needs validation)
class EnvConfigLoader {
    fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = System.getenv("PAYMENT_FEE_RATE")?.toDoubleOrNull() ?: 0.03,
            apiUrl = System.getenv("API_URL") ?: "https://api.payment.com/v1",
            maxRetries = System.getenv("MAX_RETRIES")?.toIntOrNull() ?: 3,
            supportedCurrencies = System.getenv("SUPPORTED_CURRENCIES")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}

// Examples:
// export PAYMENT_FEE_RATE=0.025
// export API_URL=https://api.staging.payment.com/v1
// export MAX_RETRIES=5
```

Used for:
- Container/Kubernetes/Docker configuration
- CI/CD configuration
- Secrets (combined with secrets manager + env)

#### 3. Remote Configuration

```kotlin
// Firebase Remote Config (simplified)
class RemoteConfigLoader(private val remoteConfig: FirebaseRemoteConfig) {

    suspend fun loadConfig(): AppConfig {
        remoteConfig.fetchAndActivate().await()

        val supportedCurrenciesRaw = remoteConfig.getString("supported_currencies")

        return AppConfig(
            paymentFeeRate = remoteConfig.getDouble("payment_fee_rate"),
            apiUrl = remoteConfig.getString("api_url"),
            maxRetries = remoteConfig.getLong("max_retries").toInt(),
            supportedCurrencies = if (supportedCurrenciesRaw.isNotEmpty())
                supportedCurrenciesRaw.split(",")
            else
                listOf("USD", "EUR", "GBP")
        )
    }
}

// Advantages:
// - Update config without app update
// - A/B tests
// - Feature flags
// - Segmentation/personalization
```

#### 4. Database

```kotlin
// Storing config in DB (Room example, simplified)
@Entity(tableName = "app_config")
data class ConfigEntity(
    @PrimaryKey val key: String,
    val value: String
)

@Dao
interface ConfigDao {
    @Query("SELECT value FROM app_config WHERE key = :key")
    suspend fun getValue(key: String): String?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun setValue(config: ConfigEntity)
}

// Load from DB
class DatabaseConfigLoader(private val configDao: ConfigDao) {

    suspend fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = configDao.getValue("payment_fee_rate")?.toDoubleOrNull() ?: 0.03,
            apiUrl = configDao.getValue("api_url") ?: "https://api.payment.com/v1",
            maxRetries = configDao.getValue("max_retries")?.toIntOrNull() ?: 3,
            supportedCurrencies = configDao.getValue("supported_currencies")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}
```

---

### When to Use Softcoding Vs Hardcoding

Use softcoding for:

1. Config values that may change:
   ```kotlin
   val apiUrl = config.getApiUrl()
   val timeoutMs = config.getTimeout()
   val maxRetries = config.getMaxRetries()
   ```

2. Environment-dependent values:
   ```kotlin
   val apiUrl = when (BuildConfig.BUILD_TYPE) {
       "debug" -> config.devApiUrl
       "staging" -> config.stagingApiUrl
       "release" -> config.prodApiUrl
       else -> config.devApiUrl
   }
   ```

3. Business rules frequently tuned by product/ops:
   ```kotlin
   val feeRate = remoteConfig.getDouble("payment_fee_rate")
   val minOrderAmount = remoteConfig.getDouble("min_order_amount")
   ```

4. Feature flags:
   ```kotlin
   if (remoteConfig.getBoolean("new_checkout_enabled")) {
       showNewCheckout()
   } else {
       showOldCheckout()
   }
   ```

5. A/B test parameters:
   ```kotlin
   val buttonColor = remoteConfig.getString("button_color_variant")
   ```

6. Localizable content:
   ```kotlin
   val welcomeMessage = localizationService.getString("welcome_message")
   ```

Use hardcoding for:

1. Fundamental constants:
   ```kotlin
   const val PI = 3.14159265359
   const val SPEED_OF_LIGHT = 299792458  // m/s
   ```

2. Stable domain logic:
   ```kotlin
   fun calculateDiscount(price: Double, quantity: Int): Double {
       return if (quantity >= 10) {
           price * 0.9  // 10% discount
       } else {
           price
       }
   }
   ```

3. Internal IDs and constants:
   ```kotlin
   const val REQUEST_CODE_CAMERA = 1001
   const val PERMISSION_REQUEST_CODE = 2001
   ```

4. `View` and resource IDs:
   ```kotlin
   findViewById<TextView>(R.id.title)
   getString(R.string.app_name)
   ```

---

### Over-softcoding (antipattern)

Excessive softcoding is harmful.

Bad example:

```kotlin
// Everything is configurable, even basic operations — unnecessary flexibility
class Calculator(private val config: CalculatorConfig) {

    fun add(a: Int, b: Int): Int {
        // Even the addition operator is "configurable"
        return when (config.additionOperator) {
            "plus" -> a + b
            "concat" -> (a.toString() + b.toString()).toInt()
            else -> 0
        }
    }

    fun multiply(a: Int, b: Int): Int {
        // Unnecessary complexity
        return when (config.multiplicationStrategy) {
            "repeated_addition" -> {
                var result = 0
                repeat(b) { result += a }
                result
            }
            "normal" -> a * b
            else -> 0
        }
    }
}
```

Issues:
- Extra layers of indirection and complexity
- Performance overhead
- Harder to read and debug
- Higher risk of misconfiguration

Rule: fundamental algorithms, invariants, and safety-critical logic should stay in code; only externalize what is expected to change.

---

### Android Example: Configuration System

```kotlin
// Demo example; imports and error handling omitted

// 1. Configuration data class
data class AppConfig(
    val apiBaseUrl: String,
    val apiTimeout: Long,
    val maxRetries: Int,
    val enableAnalytics: Boolean,
    val featureFlags: FeatureFlags
)

data class FeatureFlags(
    val newCheckoutEnabled: Boolean,
    val darkModeEnabled: Boolean,
    val experimentalFeaturesEnabled: Boolean
)

// 2. Config repository
interface ConfigRepository {
    suspend fun getConfig(): AppConfig
    suspend fun updateConfig(config: AppConfig)
}

class ConfigRepositoryImpl(
    private val remoteConfig: FirebaseRemoteConfig,
    private val localPrefs: SharedPreferences
) : ConfigRepository {

    override suspend fun getConfig(): AppConfig {
        remoteConfig.fetchAndActivate().await()

        return AppConfig(
            apiBaseUrl = remoteConfig.getString("api_base_url")
                .takeIf { it.isNotEmpty() }
                ?: localPrefs.getString("api_base_url", DEFAULT_API_URL)!!,

            apiTimeout = remoteConfig.getLong("api_timeout")
                .takeIf { it > 0 }
                ?: localPrefs.getLong("api_timeout", DEFAULT_TIMEOUT),

            maxRetries = remoteConfig.getLong("max_retries").toInt()
                .takeIf { it > 0 }
                ?: localPrefs.getInt("max_retries", DEFAULT_MAX_RETRIES),

            enableAnalytics = remoteConfig.getBoolean("enable_analytics"),

            featureFlags = FeatureFlags(
                newCheckoutEnabled = remoteConfig.getBoolean("new_checkout_enabled"),
                darkModeEnabled = remoteConfig.getBoolean("dark_mode_enabled"),
                experimentalFeaturesEnabled = remoteConfig.getBoolean("experimental_features_enabled")
            )
        )
    }

    override suspend fun updateConfig(config: AppConfig) {
        localPrefs.edit {
            putString("api_base_url", config.apiBaseUrl)
            putLong("api_timeout", config.apiTimeout)
            putInt("max_retries", config.maxRetries)
        }
    }

    companion object {
        private const val DEFAULT_API_URL = "https://api.myapp.com/v1"
        private const val DEFAULT_TIMEOUT = 30000L
        private const val DEFAULT_MAX_RETRIES = 3
    }
}

// 3. Usage in ViewModel
class MainViewModel(
    private val configRepository: ConfigRepository,
    private val apiService: ApiService
) : ViewModel() {

    private val _config = MutableStateFlow<AppConfig?>(null)
    val config: StateFlow<AppConfig?> = _config.asStateFlow()

    init {
        loadConfig()
    }

    private fun loadConfig() {
        viewModelScope.launch {
            val config = configRepository.getConfig()
            _config.value = config

            apiService.updateBaseUrl(config.apiBaseUrl)
            apiService.updateTimeout(config.apiTimeout)
        }
    }
}

// 4. Using feature flags in UI
class CheckoutFragment : Fragment() {

    private val viewModel: MainViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.config.collect { config ->
                if (config?.featureFlags?.newCheckoutEnabled == true) {
                    showNewCheckout()
                } else {
                    showOldCheckout()
                }
            }
        }
    }
}
```

---

### Best Practices (EN)

#### DO

1. Use softcoding for configurable values:
   ```kotlin
   val apiUrl = BuildConfig.API_URL
   val timeout = remoteConfig.getLong("timeout")
   ```

2. Provide reasonable defaults:
   ```kotlin
   val maxRetries = config.getInt("max_retries", defaultValue = 3)
   ```

3. Validate configuration:
   ```kotlin
   fun validateConfig(config: AppConfig): Result<Unit> {
       if (config.apiTimeout <= 0) {
           return Result.failure(IllegalArgumentException("Timeout must be positive"))
       }
       return Result.success(Unit)
   }
   ```

4. Use type-safe configs:
   ```kotlin
   data class AppConfig(/* fields */)
   // instead of
   val rawConfig: Map<String, Any>
   ```

#### DON'T

1. Don't overuse softcoding:
   ```kotlin
   // Avoid configuring basic operators and control flow
   if (config.getString("comparison_operator") == "equals") { /* ... */ }
   ```

2. Don't store sensitive data in insecure configs:
   ```kotlin
   // Avoid storing secrets in plain text on the client
   val apiKey = remoteConfig.getString("api_key")
   ```

3. Don't externalize values that are stable and critical for correctness:
   ```kotlin
   const val MAX_USERNAME_LENGTH = 50
   ```

---

## Дополнительные Вопросы (RU)

- Сравните использование софткода с dependency injection для достижения гибкости.
- В каких случаях избыточный софткодинг повышает риски системы вместо их снижения?
- Как спроектировать миграцию с хардкоженных конфигов на софткод в легаси-системе?

## Additional Questions (EN)

- Compare softcoding with using dependency injection for flexibility.
- When can over-softcoding increase system risk instead of reducing it?
- How would you design a migration from hardcoded configs to softcoded configs in a legacy system?

## Ссылки (RU)

- [[c-architecture-patterns]]

## References (EN)

- [[c-architecture-patterns]]

## Related Questions

- [[q-abstract-factory-pattern--cs--medium]]
