---
id: 20251012-1227111180
title: "Softcode Vs Hardcode / Softcode против Hardcode"
topic: architecture-patterns
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - best-practices
  - configuration
  - flexibility
  - hardcoding
  - maintainability
  - softcoding
  - software-design
moc: moc-architecture-patterns
related: [q-extensions-concept--programming-languages--easy, q-proxy-pattern--design-patterns--medium, q-flyweight-pattern--design-patterns--hard]
subtopics: ["design-principles", "best-practices", "architecture"]
---
# Что такое софткод?

# Question (EN)
> What is softcode?

# Вопрос (RU)
> Что такое софткод?

---

## Answer (EN)

**Softcode (Soft Coding)** is a programming approach where **program logic is stored in configuration files, databases, or other external sources** rather than being **hardcoded** (hard-coded) directly in the code.

## Hardcode vs Softcode

### Hardcode (Hard Coding)

**Hardcoding** means writing **fixed values or logic directly in the source code**.

#### - Hardcoded Example

```kotlin
class PaymentProcessor {
    fun calculateFee(amount: Double): Double {
        // - Fee rate is hardcoded
        return amount * 0.03  // 3% fee
    }

    fun getApiUrl(): String {
        // - URL is hardcoded
        return "https://api.payment.com/v1"
    }

    fun getMaxRetries(): Int {
        // - Max retries hardcoded
        return 3
    }

    fun getSupportedCurrencies(): List<String> {
        // - Currencies hardcoded
        return listOf("USD", "EUR", "GBP")
    }
}
```

**Problems with hardcoding:**
- Changing fee rate requires **code modification and redeployment**
- Can't configure different values for dev/staging/production
- No way to change values without rebuilding the app
- Business logic is mixed with implementation

---

### Softcode (Soft Coding)

**Softcoding** means storing **configurable values in external sources**.

#### - Softcoded Example

```kotlin
// Configuration stored externally
class AppConfig(
    val paymentFeeRate: Double,
    val apiUrl: String,
    val maxRetries: Int,
    val supportedCurrencies: List<String>
)

// Load from JSON file
class ConfigLoader {
    fun loadConfig(): AppConfig {
        val json = File("config.json").readText()
        return Json.decodeFromString<AppConfig>(json)
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
        // - Fee rate from config
        return amount * config.paymentFeeRate
    }

    fun getApiUrl(): String {
        // - URL from config
        return config.apiUrl
    }

    fun getMaxRetries(): Int {
        // - Max retries from config
        return config.maxRetries
    }

    fun getSupportedCurrencies(): List<String> {
        // - Currencies from config
        return config.supportedCurrencies
    }
}
```

**Benefits of softcoding:**
- Change values **without rebuilding** the app
- Different configs for **dev/staging/production**
- **Business users** can modify configurations
- Easier A/B testing and feature flags

---

## Common Softcode Sources

### 1. Configuration Files

**JSON, YAML, TOML, Properties files**

```kotlin
// application.properties
/*
payment.fee.rate=0.03
api.url=https://api.payment.com/v1
max.retries=3
supported.currencies=USD,EUR,GBP
*/

// Load from Properties
class PropertiesConfigLoader {
    fun loadConfig(): AppConfig {
        val props = Properties()
        props.load(FileInputStream("application.properties"))

        return AppConfig(
            paymentFeeRate = props.getProperty("payment.fee.rate").toDouble(),
            apiUrl = props.getProperty("api.url"),
            maxRetries = props.getProperty("max.retries").toInt(),
            supportedCurrencies = props.getProperty("supported.currencies").split(",")
        )
    }
}
```

---

### 2. Environment Variables

```kotlin
// Read from environment
class EnvConfigLoader {
    fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = System.getenv("PAYMENT_FEE_RATE")?.toDouble() ?: 0.03,
            apiUrl = System.getenv("API_URL") ?: "https://api.payment.com/v1",
            maxRetries = System.getenv("MAX_RETRIES")?.toInt() ?: 3,
            supportedCurrencies = System.getenv("SUPPORTED_CURRENCIES")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}

// Set environment variables
// export PAYMENT_FEE_RATE=0.025
// export API_URL=https://api.staging.payment.com/v1
// export MAX_RETRIES=5
```

**Use cases:**
- **Kubernetes/Docker** configurations
- **CI/CD** pipeline settings
- **Secrets** (API keys, passwords)

---

### 3. Remote Configuration (Firebase Remote Config, Server)

```kotlin
// Firebase Remote Config
class RemoteConfigLoader(private val remoteConfig: FirebaseRemoteConfig) {

    suspend fun loadConfig(): AppConfig {
        remoteConfig.fetchAndActivate().await()

        return AppConfig(
            paymentFeeRate = remoteConfig.getDouble("payment_fee_rate"),
            apiUrl = remoteConfig.getString("api_url"),
            maxRetries = remoteConfig.getLong("max_retries").toInt(),
            supportedCurrencies = remoteConfig.getString("supported_currencies")
                .split(",")
        )
    }
}

// Benefits:
// - Update config without app update
// - A/B testing
// - Feature flags
// - Per-user configurations
```

---

### 4. Database

```kotlin
// Store config in database
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

// Load from database
class DatabaseConfigLoader(private val configDao: ConfigDao) {

    suspend fun loadConfig(): AppConfig {
        return AppConfig(
            paymentFeeRate = configDao.getValue("payment_fee_rate")?.toDouble() ?: 0.03,
            apiUrl = configDao.getValue("api_url") ?: "https://api.payment.com/v1",
            maxRetries = configDao.getValue("max_retries")?.toInt() ?: 3,
            supportedCurrencies = configDao.getValue("supported_currencies")
                ?.split(",") ?: listOf("USD", "EUR", "GBP")
        )
    }
}
```

---

## When to Use Softcode vs Hardcode

### - Use Softcode For:

1. **Configuration values** that may change:
   ```kotlin
   // - Softcode
   val apiUrl = config.getApiUrl()
   val timeoutMs = config.getTimeout()
   val maxRetries = config.getMaxRetries()
   ```

2. **Environment-specific values**:
   ```kotlin
   // - Different per environment
   val apiUrl = when (BuildConfig.BUILD_TYPE) {
       "debug" -> config.devApiUrl
       "staging" -> config.stagingApiUrl
       "release" -> config.prodApiUrl
   }
   ```

3. **Business rules** that change frequently:
   ```kotlin
   // - Business team can update
   val feeRate = remoteConfig.getDouble("payment_fee_rate")
   val minOrderAmount = remoteConfig.getDouble("min_order_amount")
   ```

4. **Feature flags**:
   ```kotlin
   // - Enable/disable features remotely
   if (remoteConfig.getBoolean("new_checkout_enabled")) {
       showNewCheckout()
   } else {
       showOldCheckout()
   }
   ```

5. **A/B testing parameters**:
   ```kotlin
   // - Different values for different users
   val buttonColor = remoteConfig.getString("button_color_variant")
   ```

6. **Localized content**:
   ```kotlin
   // - Translations from external source
   val welcomeMessage = localizationService.getString("welcome_message")
   ```

---

### - Use Hardcode For:

1. **Constants that never change**:
   ```kotlin
   // - Hardcode - mathematical constants
   const val PI = 3.14159265359
   const val SPEED_OF_LIGHT = 299792458  // m/s
   ```

2. **Application structure/logic**:
   ```kotlin
   // - Hardcode - business logic
   fun calculateDiscount(price: Double, quantity: Int): Double {
       return if (quantity >= 10) {
           price * 0.9  // 10% discount for bulk
       } else {
           price
       }
   }
   ```

3. **Internal IDs and constants**:
   ```kotlin
   // - Hardcode - internal constants
   const val REQUEST_CODE_CAMERA = 1001
   const val PERMISSION_REQUEST_CODE = 2001
   ```

4. **View IDs, resource references**:
   ```kotlin
   // - Hardcode - Android resources
   findViewById<TextView>(R.id.title)
   getString(R.string.app_name)
   ```

---

## Over-Softcoding (Anti-pattern)

**Warning:** Too much softcoding can be harmful!

### - BAD: Over-Softcoded

```kotlin
// - Everything is softcoded, even basic logic!
class Calculator(private val config: CalculatorConfig) {

    fun add(a: Int, b: Int): Int {
        // - Even basic operators are "configured"
        return when (config.additionOperator) {
            "plus" -> a + b
            "concat" -> (a.toString() + b.toString()).toInt()
            else -> 0
        }
    }

    fun multiply(a: Int, b: Int): Int {
        // - Absurd configuration
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

**Problems:**
- Makes code **unnecessarily complex**
- **Harms performance** (loading configs repeatedly)
- **Harder to understand** and debug
- **Error-prone** (wrong config values cause bugs)

---

## Android Example: Complete Configuration System

```kotlin
// 1. Define config data class
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

// 2. Create config repository
interface ConfigRepository {
    suspend fun getConfig(): AppConfig
    suspend fun updateConfig(config: AppConfig)
}

class ConfigRepositoryImpl(
    private val remoteConfig: FirebaseRemoteConfig,
    private val localPrefs: SharedPreferences
) : ConfigRepository {

    override suspend fun getConfig(): AppConfig {
        // Try remote config first
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

// 3. Use config in ViewModel
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

            // Apply config
            apiService.updateBaseUrl(config.apiBaseUrl)
            apiService.updateTimeout(config.apiTimeout)
        }
    }
}

// 4. Use feature flags in UI
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

## Best Practices

### - DO

1. **Use softcode for configurable values**:
   ```kotlin
   val apiUrl = BuildConfig.API_URL  // From gradle
   val timeout = remoteConfig.getLong("timeout")
   ```

2. **Provide sensible defaults**:
   ```kotlin
   val maxRetries = config.getInt("max_retries", defaultValue = 3)
   ```

3. **Validate configuration**:
   ```kotlin
   fun validateConfig(config: AppConfig): Result<Unit> {
       if (config.apiTimeout <= 0) {
           return Result.failure(IllegalArgumentException("Timeout must be positive"))
       }
       return Result.success(Unit)
   }
   ```

4. **Use type-safe configs**:
   ```kotlin
   data class AppConfig(...)  // - Type-safe
   // vs
   Map<String, Any>  // - Not type-safe
   ```

---

### - DON'T

1. **Don't over-softcode**:
   ```kotlin
   // - Don't softcode basic logic
   if (config.getString("comparison_operator") == "equals") { ... }
   ```

2. **Don't expose sensitive data**:
   ```kotlin
   // - Don't store secrets in remote config
   val apiKey = remoteConfig.getString("api_key")  // - Insecure!
   ```

3. **Don't softcode everything**:
   ```kotlin
   // - Constants don't need softcoding
   const val MAX_USERNAME_LENGTH = 50  // - Hardcode is fine
   ```

---

## Summary

**Softcode:**
- Configuration stored in **external sources** (files, database, remote config)
- Can be changed **without code modification**
- Good for **configurable business rules** and **feature flags**

**Hardcode:**
- Values written directly in **source code**
- Requires **code change and redeployment** to modify
- Good for **constants** and **core logic**

**Best approach:** Use **softcode for things that change**, **hardcode for things that don't**.

---

## Ответ (RU)

Софткод (Softcode, Soft Coding) — это подход к программированию, при котором логика программы хранится в конфигурационных файлах, базе данных или других внешних источниках, а не жёстко (hardcoded) прописана в коде.

**Преимущества софткода:**
- Изменение конфигурации без перекомпиляции
- Разные настройки для разных окружений (dev/staging/production)
- Бизнес-пользователи могут изменять параметры
- Легче проводить A/B тестирование

**Когда использовать:**
- Для конфигурационных значений (URL API, таймауты)
- Для бизнес-правил, которые могут меняться
- Для feature flags (включение/выключение функций)
- Для локализации

**Когда НЕ использовать (хардкод лучше):**
- Математические константы
- Основная бизнес-логика
- Внутренние идентификаторы


---

## Related Questions

### Related (Medium)
- [[q-solid-principles--software-design--medium]] - Design Principles
- [[q-android-security-practices-checklist--android--medium]] - Security
- [[q-usecase-pattern-android--android--medium]] - Architecture

### Advanced (Harder)
- [[q-modularization-patterns--android--hard]] - Architecture
- [[q-design-instagram-stories--android--hard]] - Media
- [[q-design-uber-app--android--hard]] - Location
