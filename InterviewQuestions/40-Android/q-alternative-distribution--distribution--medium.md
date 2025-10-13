---
tags:
  - Android
  - Kotlin
  - Distribution
  - APK
  - Samsung
difficulty: medium
status: draft
---

# Alternative App Distribution Channels

# Question (EN)
> 
Explain alternative app distribution channels beyond Google Play Store. How do you distribute apps through Samsung Galaxy Store, Amazon Appstore, Huawei AppGallery, and direct APK distribution? What are the requirements, limitations, and best practices for each platform?

## Answer (EN)
Alternative distribution channels provide access to millions of users outside the Google Play ecosystem, each with unique requirements, user bases, and technical considerations.

#### Samsung Galaxy Store

**1. Galaxy Store Setup**
```kotlin
// build.gradle.kts - Galaxy Store specific configuration
android {
    buildTypes {
        create("samsung") {
            initWith(getByName("release"))
            applicationIdSuffix = ""  // Keep same package name
            versionNameSuffix = "-samsung"

            // Galaxy Store allows larger APKs
            buildConfigField("String", "STORE_NAME", "\"Samsung Galaxy Store\"")
            buildConfigField("String", "STORE_URL", "\"samsungapps://ProductDetail/YOUR_PACKAGE_NAME\"")

            resValue("string", "store_name", "Samsung Galaxy Store")
        }
    }
}

dependencies {
    // Samsung IAP SDK
    "samsungImplementation"("com.samsung.android:in-app-purchase:7.0.0")

    // Samsung specific features
    "samsungImplementation"("com.samsung.android:lib.commonlib:1.1.2")
}
```

**2. Samsung IAP Integration**
```kotlin
class SamsungIapManager @Inject constructor(
    private val context: Context
) {
    private var iapHelper: IapHelper? = null

    fun initialize(onReady: () -> Unit, onError: (String) -> Unit) {
        iapHelper = IapHelper.getInstance(context)

        iapHelper?.startSetup { result ->
            when (result.errorCode) {
                IapHelper.IAP_ERROR_NONE -> {
                    Log.d(TAG, "Samsung IAP ready")
                    onReady()
                }
                IapHelper.IAP_ERROR_INITIALIZATION -> {
                    onError("Samsung IAP not available on this device")
                }
                else -> {
                    onError("Samsung IAP setup failed: ${result.errorString}")
                }
            }
        }
    }

    fun getOwnedProducts(onSuccess: (List<OwnedProduct>) -> Unit) {
        val ownedProductsRequest = OwnedProductsRequest()

        iapHelper?.getOwnedProducts(ownedProductsRequest) { result ->
            if (result.errorCode == IapHelper.IAP_ERROR_NONE) {
                onSuccess(result.ownedProducts ?: emptyList())
            }
        }
    }

    fun purchaseProduct(
        productId: String,
        activity: Activity,
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val purchaseRequest = PurchaseRequest().apply {
            itemId = productId
        }

        iapHelper?.startPayment(purchaseRequest, activity) { result ->
            when (result.errorCode) {
                IapHelper.IAP_ERROR_NONE -> {
                    // Verify purchase on server
                    verifyPurchase(result.purchaseData) {
                        onSuccess()
                    }
                }
                IapHelper.IAP_PAYMENT_IS_CANCELED -> {
                    onError("Payment cancelled by user")
                }
                else -> {
                    onError("Purchase failed: ${result.errorString}")
                }
            }
        }
    }

    private fun verifyPurchase(purchaseData: String, onVerified: () -> Unit) {
        // Send to your server for verification
        // Samsung provides purchase signature for validation
        onVerified()
    }

    companion object {
        private const val TAG = "SamsungIapManager"
    }
}
```

**3. Galaxy Store Specific Features**
```kotlin
// DeepLink to Galaxy Store product page
fun openGalaxyStoreListing(context: Context, packageName: String) {
    try {
        val intent = Intent(Intent.ACTION_VIEW).apply {
            data = Uri.parse("samsungapps://ProductDetail/$packageName")
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    } catch (e: ActivityNotFoundException) {
        // Galaxy Store not installed, open web version
        val webIntent = Intent(Intent.ACTION_VIEW).apply {
            data = Uri.parse("https://galaxystore.samsung.com/detail/$packageName")
        }
        context.startActivity(webIntent)
    }
}

// Check if running on Samsung device
fun isSamsungDevice(): Boolean {
    return Build.MANUFACTURER.equals("samsung", ignoreCase = true)
}

// OneUI version detection
fun getOneUiVersion(): String? {
    return try {
        val field = Build.VERSION::class.java.getDeclaredField("SEM_PLATFORM_INT")
        val semPlatformInt = field.getInt(null)
        when {
            semPlatformInt >= 130000 -> "6.0" // Android 14
            semPlatformInt >= 120000 -> "5.0" // Android 13
            semPlatformInt >= 110000 -> "4.0" // Android 12
            else -> "3.x or lower"
        }
    } catch (e: Exception) {
        null
    }
}
```

#### Amazon Appstore

**1. Amazon SDK Integration**
```kotlin
// build.gradle.kts
android {
    buildTypes {
        create("amazon") {
            initWith(getByName("release"))
            versionNameSuffix = "-amazon"

            buildConfigField("String", "STORE_NAME", "\"Amazon Appstore\"")
            buildConfigField("Boolean", "IS_AMAZON_BUILD", "true")

            resValue("string", "store_name", "Amazon Appstore")
        }
    }
}

dependencies {
    // Amazon IAP SDK
    "amazonImplementation"(files("libs/amazon-appstore-sdk.jar"))
}
```

**2. Amazon IAP Implementation**
```kotlin
class AmazonIapManager @Inject constructor(
    private val context: Context
) {
    private var purchasingService: PurchasingService? = null
    private var userId: String? = null

    fun initialize() {
        // Enable sandbox mode for testing
        PurchasingService.enablePendingPurchases()

        PurchasingService.registerListener(
            context,
            object : PurchasingListener {
                override fun onUserDataResponse(response: UserDataResponse) {
                    when (response.requestStatus) {
                        UserDataResponse.RequestStatus.SUCCESSFUL -> {
                            userId = response.userData.userId
                            Log.d(TAG, "Amazon user ID: $userId")
                        }
                        UserDataResponse.RequestStatus.FAILED,
                        UserDataResponse.RequestStatus.NOT_SUPPORTED -> {
                            Log.e(TAG, "Failed to get user data")
                        }
                    }
                }

                override fun onProductDataResponse(response: ProductDataResponse) {
                    when (response.requestStatus) {
                        ProductDataResponse.RequestStatus.SUCCESSFUL -> {
                            handleProductData(response.productData)
                        }
                        else -> {
                            Log.e(TAG, "Failed to get product data")
                        }
                    }
                }

                override fun onPurchaseResponse(response: PurchaseResponse) {
                    when (response.requestStatus) {
                        PurchaseResponse.RequestStatus.SUCCESSFUL -> {
                            handlePurchase(response.receipt)
                        }
                        PurchaseResponse.RequestStatus.FAILED -> {
                            Log.e(TAG, "Purchase failed")
                        }
                        PurchaseResponse.RequestStatus.INVALID_SKU -> {
                            Log.e(TAG, "Invalid SKU")
                        }
                        PurchaseResponse.RequestStatus.ALREADY_PURCHASED -> {
                            Log.w(TAG, "Already purchased")
                        }
                        else -> {}
                    }
                }

                override fun onPurchaseUpdatesResponse(response: PurchaseUpdatesResponse) {
                    // Handle receipt updates
                    response.receipts.forEach { receipt ->
                        handlePurchase(receipt)
                    }
                }
            }
        )

        // Get user data
        PurchasingService.getUserData()
    }

    fun queryProducts(skus: Set<String>) {
        PurchasingService.getProductData(skus)
    }

    fun purchase(sku: String) {
        val requestId = PurchasingService.purchase(sku)
        Log.d(TAG, "Purchase request ID: $requestId")
    }

    private fun handleProductData(productData: Map<String, Product>) {
        productData.forEach { (sku, product) ->
            Log.d(TAG, "Product: ${product.title}, Price: ${product.price}")
        }
    }

    private fun handlePurchase(receipt: Receipt) {
        // Verify receipt with Amazon RVS (Receipt Verification Service)
        // or your own server
        Log.d(TAG, "Purchase successful: ${receipt.sku}")
    }

    companion object {
        private const val TAG = "AmazonIapManager"
    }
}
```

**3. Amazon Device Features**
```kotlin
// Detect Amazon Fire devices
fun isAmazonDevice(): Boolean {
    return Build.MANUFACTURER.equals("Amazon", ignoreCase = true)
}

// Handle Fire TV specific features
fun isFireTV(): Boolean {
    val uiMode = (context.getSystemService(Context.UI_MODE_SERVICE) as UiModeManager)
        .currentModeType
    return uiMode == Configuration.UI_MODE_TYPE_TELEVISION
}

// Amazon Silk Browser detection
fun openInSilkBrowser(url: String) {
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
        setPackage("com.amazon.cloud9")
    }

    try {
        context.startActivity(intent)
    } catch (e: ActivityNotFoundException) {
        // Silk not available, use default browser
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    }
}
```

#### Huawei AppGallery

**1. HMS Integration**
```kotlin
// build.gradle.kts (project level)
buildscript {
    repositories {
        maven { url = uri("https://developer.huawei.com/repo/") }
    }
    dependencies {
        classpath("com.huawei.agconnect:agcp:1.9.1.300")
    }
}

// build.gradle.kts (app level)
plugins {
    id("com.huawei.agconnect")
}

android {
    buildTypes {
        create("huawei") {
            initWith(getByName("release"))
            versionNameSuffix = "-huawei"

            buildConfigField("String", "STORE_NAME", "\"Huawei AppGallery\"")
            buildConfigField("Boolean", "IS_HUAWEI_BUILD", "true")
        }
    }
}

dependencies {
    // HMS Core
    "huaweiImplementation"("com.huawei.hms:base:6.11.0.300")

    // HMS IAP
    "huaweiImplementation"("com.huawei.hms:iap:6.12.0.300")

    // HMS Push (alternative to FCM)
    "huaweiImplementation"("com.huawei.hms:push:6.11.0.300")

    // HMS Location (alternative to Google Play Services Location)
    "huaweiImplementation"("com.huawei.hms:location:6.11.0.300")

    // HMS Maps (alternative to Google Maps)
    "huaweiImplementation"("com.huawei.hms:maps:6.11.0.300")
}
```

**2. HMS Availability Check**
```kotlin
class HmsAvailabilityChecker @Inject constructor(
    private val context: Context
) {
    fun isHmsAvailable(): Boolean {
        val result = HuaweiApiAvailability
            .getInstance()
            .isHuaweiMobileServicesAvailable(context)

        return result == com.huawei.hms.api.ConnectionResult.SUCCESS
    }

    fun getHmsVersion(): Int {
        return try {
            val packageInfo = context.packageManager
                .getPackageInfo("com.huawei.hwid", 0)
            packageInfo.versionCode
        } catch (e: PackageManager.NameNotFoundException) {
            0
        }
    }

    fun isHuaweiDevice(): Boolean {
        return Build.MANUFACTURER.equals("HUAWEI", ignoreCase = true) ||
                Build.MANUFACTURER.equals("HONOR", ignoreCase = true)
    }

    fun promptHmsUpdate(activity: Activity) {
        val result = HuaweiApiAvailability
            .getInstance()
            .isHuaweiMobileServicesAvailable(activity)

        if (result != com.huawei.hms.api.ConnectionResult.SUCCESS) {
            if (HuaweiApiAvailability.getInstance().isUserResolvableError(result)) {
                HuaweiApiAvailability.getInstance()
                    .showErrorDialogFragment(activity, result, 1001)
            }
        }
    }
}
```

**3. HMS IAP Implementation**
```kotlin
class HuaweiIapManager @Inject constructor(
    private val context: Context
) {
    private val iapClient = Iap.getIapClient(context)

    suspend fun initialize(): Result<Unit> = suspendCancellableCoroutine { continuation ->
        // Check IAP availability
        val task = iapClient.isEnvironmentReady

        task.addOnSuccessListener {
            continuation.resume(Result.success(Unit))
        }.addOnFailureListener { exception ->
            if (exception is IapApiException) {
                val status = exception.status
                if (status.statusCode == OrderStatusCode.ORDER_HWID_NOT_LOGIN) {
                    // User not logged in to Huawei ID
                    continuation.resume(Result.failure(Exception("Please sign in to Huawei ID")))
                } else {
                    continuation.resume(Result.failure(exception))
                }
            } else {
                continuation.resume(Result.failure(exception))
            }
        }
    }

    suspend fun queryProducts(productIds: List<String>, type: Int): List<ProductInfo> =
        suspendCancellableCoroutine { continuation ->
            val request = ProductInfoReq().apply {
                priceType = type // IapClient.PriceType.IN_APP_CONSUMABLE or IN_APP_NONCONSUMABLE
                productIds = productIds
            }

            val task = iapClient.obtainProductInfo(request)

            task.addOnSuccessListener { result ->
                continuation.resume(result.productInfoList ?: emptyList())
            }.addOnFailureListener { exception ->
                continuation.resumeWithException(exception)
            }
        }

    fun purchaseProduct(
        activity: Activity,
        productInfo: ProductInfo,
        requestCode: Int = IAP_REQUEST_CODE
    ) {
        val request = PurchaseIntentReq().apply {
            productId = productInfo.productId
            priceType = productInfo.priceType
            developerPayload = "developer_payload_${System.currentTimeMillis()}"
        }

        val task = iapClient.createPurchaseIntent(request)

        task.addOnSuccessListener { result ->
            val status = result.status
            if (status.hasResolution()) {
                try {
                    status.startResolutionForResult(activity, requestCode)
                } catch (e: IntentSender.SendIntentException) {
                    Log.e(TAG, "Failed to start purchase intent", e)
                }
            }
        }.addOnFailureListener { exception ->
            Log.e(TAG, "Purchase failed", exception)
        }
    }

    suspend fun verifyPurchase(purchaseResultInfo: PurchaseResultInfo): Boolean {
        // Verify purchase signature
        val publicKey = "YOUR_HMS_PUBLIC_KEY"

        return try {
            val signature = purchaseResultInfo.inAppPurchaseData
            val data = purchaseResultInfo.inAppDataSignature

            // Verify signature with public key
            CipherUtil.doCheck(signature, data, publicKey)
        } catch (e: Exception) {
            Log.e(TAG, "Signature verification failed", e)
            false
        }
    }

    companion object {
        private const val TAG = "HuaweiIapManager"
        private const val IAP_REQUEST_CODE = 6001
    }
}
```

#### Direct APK Distribution

**1. APK Signing for Direct Distribution**
```kotlin
// build.gradle.kts
android {
    signingConfigs {
        create("direct") {
            storeFile = file("../keystore/direct-distribution.jks")
            storePassword = System.getenv("DIRECT_KEYSTORE_PASSWORD")
            keyAlias = System.getenv("DIRECT_KEY_ALIAS")
            keyPassword = System.getenv("DIRECT_KEY_PASSWORD")

            enableV1Signing = true // Required for older Android versions
            enableV2Signing = true // APK Signature Scheme v2
            enableV3Signing = true // APK Signature Scheme v3
            enableV4Signing = false // Not needed for direct distribution
        }
    }

    buildTypes {
        create("direct") {
            initWith(getByName("release"))
            versionNameSuffix = "-direct"
            signingConfig = signingConfigs.getByName("direct")

            // Disable ProGuard for easier debugging
            isMinifyEnabled = false

            buildConfigField("String", "UPDATE_URL", "\"https://yourapp.com/api/update\"")
            buildConfigField("Boolean", "AUTO_UPDATE_ENABLED", "true")
        }
    }
}
```

**2. Self-Update Mechanism**
```kotlin
@Singleton
class AppUpdateManager @Inject constructor(
    private val context: Context,
    private val apiService: ApiService
) {
    suspend fun checkForUpdates(): UpdateInfo? {
        val currentVersion = BuildConfig.VERSION_CODE

        return try {
            val updateInfo = apiService.checkUpdate(
                packageName = context.packageName,
                currentVersion = currentVersion
            )

            if (updateInfo.versionCode > currentVersion) {
                updateInfo
            } else {
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to check for updates", e)
            null
        }
    }

    suspend fun downloadAndInstallUpdate(
        updateInfo: UpdateInfo,
        onProgress: (Int) -> Unit
    ): Result<Unit> {
        val apkFile = File(context.getExternalFilesDir(null), "update.apk")

        return try {
            // Download APK
            downloadApk(updateInfo.downloadUrl, apkFile, onProgress)

            // Install APK
            installApk(apkFile)

            Result.success(Unit)
        } catch (e: Exception) {
            Log.e(TAG, "Update failed", e)
            Result.failure(e)
        }
    }

    private suspend fun downloadApk(
        url: String,
        destination: File,
        onProgress: (Int) -> Unit
    ) = withContext(Dispatchers.IO) {
        val client = OkHttpClient()
        val request = Request.Builder().url(url).build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Download failed: ${response.code}")

            val body = response.body ?: throw IOException("Empty response body")
            val contentLength = body.contentLength()

            destination.outputStream().use { output ->
                body.byteStream().use { input ->
                    val buffer = ByteArray(8192)
                    var downloaded = 0L
                    var read: Int

                    while (input.read(buffer).also { read = it } != -1) {
                        output.write(buffer, 0, read)
                        downloaded += read

                        val progress = (downloaded * 100 / contentLength).toInt()
                        withContext(Dispatchers.Main) {
                            onProgress(progress)
                        }
                    }
                }
            }
        }
    }

    private fun installApk(apkFile: File) {
        val intent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            // Use FileProvider for Android 7+
            val apkUri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                apkFile
            )

            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(apkUri, "application/vnd.android.package-archive")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION
            }
        } else {
            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(Uri.fromFile(apkFile), "application/vnd.android.package-archive")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
        }

        context.startActivity(intent)
    }

    companion object {
        private const val TAG = "AppUpdateManager"
    }
}

data class UpdateInfo(
    val versionCode: Int,
    val versionName: String,
    val downloadUrl: String,
    val changelog: String,
    val fileSize: Long,
    val isMandatory: Boolean
)
```

**3. Installation Permissions**
```xml
<!-- AndroidManifest.xml -->
<manifest>
    <!-- Required for downloading updates -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!-- Required for installing APKs (Android 8+) -->
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />

    <!-- FileProvider for APK installation -->
    <application>
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
```

```xml
<!-- res/xml/file_paths.xml -->
<paths>
    <external-files-path
        name="updates"
        path="." />
</paths>
```

#### Multi-Store Management

**1. Build Variant Strategy**
```kotlin
// buildSrc/src/main/kotlin/StoreVariants.kt
object StoreVariants {
    val configurations = listOf(
        StoreConfig(
            name = "googleplay",
            displayName = "Google Play",
            inAppPurchaseSdk = "com.android.billingclient:billing:6.1.0",
            pushSdk = "com.google.firebase:firebase-messaging:23.4.0"
        ),
        StoreConfig(
            name = "samsung",
            displayName = "Samsung Galaxy Store",
            inAppPurchaseSdk = "com.samsung.android:in-app-purchase:7.0.0",
            pushSdk = "com.google.firebase:firebase-messaging:23.4.0"
        ),
        StoreConfig(
            name = "amazon",
            displayName = "Amazon Appstore",
            inAppPurchaseSdk = files("libs/amazon-appstore-sdk.jar"),
            pushSdk = "com.amazon.device.messaging:amazon-device-messaging:1.2.0"
        ),
        StoreConfig(
            name = "huawei",
            displayName = "Huawei AppGallery",
            inAppPurchaseSdk = "com.huawei.hms:iap:6.12.0.300",
            pushSdk = "com.huawei.hms:push:6.11.0.300"
        )
    )
}

data class StoreConfig(
    val name: String,
    val displayName: String,
    val inAppPurchaseSdk: Any,
    val pushSdk: String
)
```

**2. Unified IAP Interface**
```kotlin
interface IapProvider {
    suspend fun initialize(): Result<Unit>
    suspend fun queryProducts(productIds: List<String>): List<Product>
    suspend fun purchase(productId: String, activity: Activity): Result<Purchase>
    suspend fun queryPurchases(): List<Purchase>
    suspend fun consumePurchase(purchase: Purchase): Result<Unit>
}

data class Product(
    val id: String,
    val title: String,
    val description: String,
    val price: String,
    val priceAmountMicros: Long,
    val priceCurrencyCode: String
)

data class Purchase(
    val orderId: String,
    val productId: String,
    val purchaseTime: Long,
    val purchaseToken: String
)

// Factory to get appropriate IAP provider
class IapProviderFactory @Inject constructor(
    private val context: Context
) {
    fun getProvider(): IapProvider {
        return when (BuildConfig.FLAVOR) {
            "googleplay" -> GooglePlayIapProvider(context)
            "samsung" -> SamsungIapProvider(context)
            "amazon" -> AmazonIapProvider(context)
            "huawei" -> HuaweiIapProvider(context)
            else -> GooglePlayIapProvider(context)
        }
    }
}
```

#### Best Practices

1. **Multi-Store Strategy**:
   - Use build flavors for store-specific builds
   - Abstract platform-specific APIs
   - Test on each platform before release
   - Monitor metrics per store

2. **Direct Distribution**:
   - Implement self-update mechanism
   - Use HTTPS for APK downloads
   - Verify APK signatures
   - Provide clear installation instructions

3. **HMS vs GMS**:
   - Detect service availability at runtime
   - Gracefully fallback to alternatives
   - Use same package name
   - Test on devices without GMS

4. **Security**:
   - Sign APKs with proper certificates
   - Verify in-app purchase receipts
   - Use HTTPS for all network calls
   - Implement certificate pinning

5. **User Experience**:
   - Deep link to correct store
   - Show appropriate update prompts
   - Handle installation errors gracefully
   - Provide support contact

#### Common Pitfalls

1. **Wrong Package Name**: Different stores require consistent package names
2. **Missing Permissions**: Installation permissions not requested
3. **Signature Mismatch**: Using different signing keys
4. **No Fallback**: Not handling service unavailability
5. **Hardcoded Store**: Not abstracting store-specific logic
6. **Poor Testing**: Not testing on actual devices

### Summary

Alternative distribution channels expand your user base beyond Google Play:
- **Samsung Galaxy Store**: 300M+ users, Samsung device optimization
- **Amazon Appstore**: Fire devices, alternative IAP
- **Huawei AppGallery**: 580M+ users, HMS ecosystem
- **Direct Distribution**: Full control, self-updates, enterprise deployment

Key considerations: build variants, unified interfaces, runtime detection, security, and comprehensive testing across all platforms.

---

# Вопрос (RU)
> 
Объясните альтернативные каналы распространения приложений помимо Google Play Store. Как распространять приложения через Samsung Galaxy Store, Amazon Appstore, Huawei AppGallery и прямую раздачу APK? Каковы требования, ограничения и best practices для каждой платформы?

## Ответ (RU)
Альтернативные каналы распространения обеспечивают доступ к миллионам пользователей вне экосистемы Google Play, каждый со своими уникальными требованиями, аудиторией и техническими особенностями.

#### Samsung Galaxy Store

**Аудитория**: 300M+ пользователей
**Преимущества**:
- Предустановлен на Samsung устройствах
- Доступ к OneUI функциям
- Samsung IAP

**Особенности**:
- Собственный IAP SDK
- Поддержка больших APK
- Интеграция с Samsung Pass
- DeepLink в Galaxy Store

#### Amazon Appstore

**Аудитория**: Fire devices, некоторые Android устройства
**Преимущества**:
- Fire TV, Fire tablets
- Amazon IAP
- Amazon Coins

**Особенности**:
- Собственный IAP SDK
- DRM (optional)
- Amazon Device Messaging (ADM)
- Тестирование через App Tester

#### Huawei AppGallery

**Аудитория**: 580M+ пользователей (особенно Китай, Европа)
**Преимущества**:
- Устройства без GMS
- HMS ecosystem
- Огромный рынок

**Особенности**:
- HMS Core (альтернатива GMS)
- HMS IAP
- HMS Push (альтернатива FCM)
- HMS Location, Maps

**Важно**: Проверять доступность HMS в runtime

#### Прямое распространение APK

**Use Cases**:
- Enterprise приложения
- Beta testing
- Региональные ограничения
- Полный контроль

**Функции**:
- Self-update механизм
- FileProvider для Android 7+
- REQUEST_INSTALL_PACKAGES permission
- Signature verification

**Безопасность**:
- HTTPS для загрузки
- Проверка подписи
- Certificate pinning
- Secure keystore

#### Multi-Store стратегия

**Build Variants**:
```
productFlavors {
    googleplay { }
    samsung { }
    amazon { }
    huawei { }
}
```

**Unified Interface**:
- Абстракция IAP
- Runtime service detection
- Fallback mechanisms
- Единый package name

### Резюме

Альтернативные каналы расширяют аудиторию:
- **Samsung Galaxy Store**: Samsung устройства, OneUI
- **Amazon Appstore**: Fire devices, Amazon ecosystem
- **Huawei AppGallery**: Устройства без GMS, HMS
- **Direct APK**: Enterprise, полный контроль

Ключевые моменты: build variants, unified interfaces, runtime detection, безопасность, тестирование на реальных устройствах каждой платформы.

---

## Related Questions

### Related (Medium)
- [[q-internal-app-distribution--distribution--medium]] - Distribution
- [[q-app-store-optimization--distribution--medium]] - Distribution
- [[q-play-store-publishing--distribution--medium]] - Distribution
- [[q-android-app-bundles--android--easy]] - Distribution
