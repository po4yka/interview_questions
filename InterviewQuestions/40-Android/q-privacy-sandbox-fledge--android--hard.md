---
id: 20251012-12271170
title: "Privacy Sandbox Fledge"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-design-whatsapp-app--android--hard, q-retrofit-modify-all-requests--android--hard, q-http-protocols-comparison--android--medium]
created: 2025-10-15
tags: [privacy-sandbox, fledge, protected-audience, remarketing, privacy, advertising, difficulty/hard]
---

# Privacy Sandbox: FLEDGE (Protected Audience API) and On-Device Auctions

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
What is FLEDGE (Protected Audience API) in Privacy Sandbox? How does it enable remarketing without third-party cookies? How do you implement on-device ad auctions and what are the technical challenges?

## Answer (EN)
FLEDGE (First Locally-Executed Decision over Groups Experiment), now called Protected Audience API, enables remarketing and custom audience targeting without cross-site tracking. Ad auctions run on-device, keeping user data private while allowing personalized advertising.

#### 1. Protected Audience API Basics

**Understanding FLEDGE Architecture:**
```kotlin
/**
 * FLEDGE/Protected Audience API enables remarketing without tracking
 *
 * Key Concepts:
 * - Interest Groups: Collections of users with shared interests
 * - Custom Audiences: Advertiser-defined audience segments
 * - On-Device Auction: Ad selection happens locally
 * - Trusted Servers: Provide real-time bidding signals
 * - No cross-site tracking: User data stays on device
 *
 * Flow:
 * 1. Advertiser adds user to interest group (joinCustomAudience)
 * 2. Publisher requests ad (selectAds)
 * 3. On-device auction evaluates bids from interest groups
 * 4. Winning ad is returned and displayed
 */

import android.adservices.customaudience.CustomAudience
import android.adservices.customaudience.CustomAudienceManager
import android.adservices.customaudience.TrustedBiddingData
import android.adservices.adselection.AdSelectionConfig
import android.adservices.adselection.AdSelectionManager
import android.adservices.adselection.AdSelectionOutcome
import android.adservices.common.AdServicesPermissions
import android.adservices.common.AdTechIdentifier
import android.content.Context
import android.net.Uri
import android.os.Build
import androidx.annotation.RequiresApi
import androidx.annotation.RequiresPermission
import java.time.Instant
import java.time.temporal.ChronoUnit

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class ProtectedAudienceManager(private val context: Context) {

    private val customAudienceManager: CustomAudienceManager? =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.getSystemService(CustomAudienceManager::class.java)
        } else null

    private val adSelectionManager: AdSelectionManager? =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.getSystemService(AdSelectionManager::class.java)
        } else null

    /**
     * Join a custom audience (interest group)
     * Called by advertiser when user shows interest
     */
    @RequiresPermission(AdServicesPermissions.ACCESS_ADSERVICES_CUSTOM_AUDIENCE)
    suspend fun joinCustomAudience(
        audienceName: String,
        buyer: String,
        biddingLogicUri: String,
        dailyUpdateUri: String,
        userBiddingSignals: Map<String, Any>,
        ads: List<AdData>
    ): Result<Unit> {
        if (customAudienceManager == null) {
            return Result.failure(UnsupportedOperationException("Protected Audience API not available"))
        }

        return try {
            val customAudience = CustomAudience.Builder()
                .setName(audienceName)
                .setBuyer(AdTechIdentifier.fromString(buyer))
                .setDailyUpdateUri(Uri.parse(dailyUpdateUri))
                .setBiddingLogicUri(Uri.parse(biddingLogicUri))
                .setUserBiddingSignals(userBiddingSignals.toAdData())
                .setTrustedBiddingData(
                    TrustedBiddingData.Builder()
                        .setTrustedBiddingUri(Uri.parse("https://$buyer/bidding"))
                        .setTrustedBiddingKeys(listOf("key1", "key2"))
                        .build()
                )
                .setAds(ads.map { it.toAdData() })
                .setActivationTime(Instant.now())
                .setExpirationTime(Instant.now().plus(30, ChronoUnit.DAYS))
                .build()

            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                customAudienceManager.joinCustomAudience(
                    customAudience,
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Leave a custom audience
     */
    @RequiresPermission(AdServicesPermissions.ACCESS_ADSERVICES_CUSTOM_AUDIENCE)
    suspend fun leaveCustomAudience(
        audienceName: String,
        buyer: String
    ): Result<Unit> {
        if (customAudienceManager == null) {
            return Result.failure(UnsupportedOperationException("Protected Audience API not available"))
        }

        return try {
            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                customAudienceManager.leaveCustomAudience(
                    AdTechIdentifier.fromString(buyer),
                    audienceName,
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Select ads through on-device auction
     */
    @RequiresPermission(AdServicesPermissions.ACCESS_ADSERVICES_AD_SELECTION)
    suspend fun selectAd(
        seller: String,
        decisionLogicUri: String,
        customAudienceBuyers: List<String>,
        adSelectionSignals: Map<String, Any>,
        sellerSignals: Map<String, Any>,
        perBuyerSignals: Map<String, Map<String, Any>>
    ): Result<AdSelectionOutcome> {
        if (adSelectionManager == null) {
            return Result.failure(UnsupportedOperationException("Ad Selection API not available"))
        }

        return try {
            val config = AdSelectionConfig.Builder()
                .setSeller(AdTechIdentifier.fromString(seller))
                .setDecisionLogicUri(Uri.parse(decisionLogicUri))
                .setCustomAudienceBuyers(
                    customAudienceBuyers.map { AdTechIdentifier.fromString(it) }
                )
                .setAdSelectionSignals(adSelectionSignals.toAdData())
                .setSellerSignals(sellerSignals.toAdData())
                .setPerBuyerSignals(perBuyerSignals.mapKeys {
                    AdTechIdentifier.fromString(it.key)
                }.mapValues { it.value.toAdData() })
                .build()

            val outcome = suspendCancellableCoroutine<AdSelectionOutcome> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                adSelectionManager.selectAds(
                    config,
                    executor,
                    OutcomeReceiver.create(
                        { result -> continuation.resume(result) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(outcome)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Report impression for selected ad
     */
    @RequiresPermission(AdServicesPermissions.ACCESS_ADSERVICES_AD_SELECTION)
    suspend fun reportImpression(adSelectionId: Long): Result<Unit> {
        if (adSelectionManager == null) {
            return Result.failure(UnsupportedOperationException("Ad Selection API not available"))
        }

        return try {
            suspendCancellableCoroutine<Unit> { continuation ->
                val executor = Executors.newSingleThreadExecutor()

                adSelectionManager.reportImpression(
                    adSelectionId,
                    executor,
                    OutcomeReceiver.create(
                        { continuation.resume(Unit) },
                        { error -> continuation.resumeWithException(error) }
                    )
                )

                continuation.invokeOnCancellation {
                    executor.shutdown()
                }
            }

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun Map<String, Any>.toAdData(): AdData {
        // Convert map to AdData format
        return AdData("", emptyMap())
    }

    private fun AdData.toAdData(): android.adservices.common.AdData {
        // Convert to platform AdData
        return android.adservices.common.AdData.Builder()
            .setRenderUri(Uri.parse(this.renderUri))
            .setMetadata(this.metadata.toString())
            .build()
    }

    fun isApiAvailable(): Boolean {
        return Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
               customAudienceManager != null &&
               adSelectionManager != null
    }
}

data class AdData(
    val renderUri: String,
    val metadata: Map<String, Any>
)
```

#### 2. Bidding Logic and Decision Logic

**JavaScript Bidding Functions (run on-device):**
```javascript
// bidding_logic.js - Executed on-device by buyer

/**
 * Generate bid for custom audience
 * Runs in isolated JavaScript environment on device
 */
function generateBid(
    customAudience,
    auctionSignals,
    perBuyerSignals,
    trustedBiddingSignals,
    contextualSignals
) {
    // Custom audience information
    const audienceName = customAudience.name;
    const userBiddingSignals = customAudience.userBiddingSignals;
    const ads = customAudience.ads;

    // Calculate bid based on audience value
    const baseValue = userBiddingSignals.interestLevel || 1.0;
    const recencyBoost = calculateRecencyBoost(customAudience.activationTime);
    const contextualBoost = calculateContextualBoost(contextualSignals);

    // Select best ad from custom audience
    const selectedAd = selectBestAd(ads, auctionSignals);

    // Calculate final bid
    const bid = baseValue * recencyBoost * contextualBoost;

    return {
        ad: selectedAd,
        bid: bid,
        render: selectedAd.renderUri,
        metadata: {
            audienceName: audienceName,
            bidStrategy: "recency_weighted"
        }
    };
}

function calculateRecencyBoost(activationTime) {
    const now = Date.now();
    const daysSinceActivation = (now - activationTime) / (1000 * 60 * 60 * 24);

    // Decay factor: newer is better
    return Math.max(0.5, 1.0 - (daysSinceActivation / 30) * 0.5);
}

function calculateContextualBoost(contextualSignals) {
    // Boost based on current context
    if (contextualSignals.category === 'relevant') {
        return 1.2;
    }
    return 1.0;
}

function selectBestAd(ads, auctionSignals) {
    // Select ad based on auction signals and ad metadata
    return ads.reduce((best, current) => {
        const currentScore = current.metadata.performance || 0;
        const bestScore = best.metadata.performance || 0;
        return currentScore > bestScore ? current : best;
    }, ads[0]);
}

/**
 * Report win event
 */
function reportWin(
    auctionSignals,
    perBuyerSignals,
    sellerSignals,
    browserSignals
) {
    // Send win report to buyer's server
    sendReportTo(
        'https://buyer.example/report-win?' +
        'bid=' + browserSignals.bid +
        '&auction=' + browserSignals.auctionId
    );
}
```

**Decision Logic (run by seller):**
```javascript
// decision_logic.js - Executed on-device by seller

/**
 * Score ads from different buyers
 */
function scoreAd(
    adMetadata,
    bid,
    auctionConfig,
    trustedScoringSignals,
    browserSignals
) {
    // Validate bid
    if (bid <= 0) {
        return 0;
    }

    // Apply seller's scoring logic
    let score = bid;

    // Quality adjustments
    const qualityMultiplier = getQualityMultiplier(
        adMetadata,
        trustedScoringSignals
    );
    score *= qualityMultiplier;

    // Brand safety checks
    if (!isBrandSafe(adMetadata)) {
        return 0; // Reject unsafe ads
    }

    // Floor price check
    const floorPrice = auctionConfig.floorPrice || 0;
    if (bid < floorPrice) {
        return 0;
    }

    return score;
}

function getQualityMultiplier(adMetadata, trustedScoringSignals) {
    // Adjust score based on ad quality signals
    const clickThroughRate = trustedScoringSignals.ctr || 0.01;
    const viewabilityRate = trustedScoringSignals.viewability || 0.5;

    return clickThroughRate * 10 + viewabilityRate;
}

function isBrandSafe(adMetadata) {
    // Check ad against brand safety criteria
    const blockedCategories = ['adult', 'gambling'];
    return !blockedCategories.includes(adMetadata.category);
}

/**
 * Report auction result
 */
function reportResult(auctionConfig, browserSignals) {
    // Send auction result to seller's server
    sendReportTo(
        'https://seller.example/report-result?' +
        'winner=' + browserSignals.interestGroupOwner +
        '&bid=' + browserSignals.bid +
        '&auction=' + browserSignals.auctionId
    );

    return {
        success: true,
        reportingUrl: 'https://seller.example/report'
    };
}
```

#### 3. Advanced Remarketing Implementation

**E-commerce Remarketing Example:**
```kotlin
class EcommerceRemarketingManager(
    private val context: Context,
    private val audienceManager: ProtectedAudienceManager
) {

    /**
     * Add user to product viewers audience
     */
    suspend fun trackProductView(
        productId: String,
        productCategory: String,
        price: Double
    ) {
        val audienceName = "product_viewers_${productCategory}"
        val userSignals = mapOf(
            "productId" to productId,
            "category" to productCategory,
            "price" to price,
            "viewTime" to System.currentTimeMillis(),
            "interestLevel" to calculateInterestLevel(productId)
        )

        val ads = generateRemarketingAds(productId, productCategory, price)

        audienceManager.joinCustomAudience(
            audienceName = audienceName,
            buyer = "https://advertiser.example",
            biddingLogicUri = "https://advertiser.example/bidding.js",
            dailyUpdateUri = "https://advertiser.example/update-audience",
            userBiddingSignals = userSignals,
            ads = ads
        )
    }

    /**
     * Add user to cart abandoners audience
     */
    suspend fun trackCartAbandonment(
        cartItems: List<CartItem>,
        totalValue: Double
    ) {
        val audienceName = "cart_abandoners"
        val userSignals = mapOf(
            "cartValue" to totalValue,
            "itemCount" to cartItems.size,
            "abandonTime" to System.currentTimeMillis(),
            "items" to cartItems.map { it.toMap() }
        )

        val ads = generateCartRecoveryAds(cartItems, totalValue)

        audienceManager.joinCustomAudience(
            audienceName = audienceName,
            buyer = "https://advertiser.example",
            biddingLogicUri = "https://advertiser.example/bidding-cart.js",
            dailyUpdateUri = "https://advertiser.example/update-cart",
            userBiddingSignals = userSignals,
            ads = ads
        )
    }

    /**
     * Add user to purchasers audience (for cross-sell)
     */
    suspend fun trackPurchase(
        orderId: String,
        purchasedItems: List<CartItem>,
        totalValue: Double
    ) {
        // Remove from cart abandoners
        audienceManager.leaveCustomAudience("cart_abandoners", "https://advertiser.example")

        // Add to purchasers for cross-sell
        val audienceName = "recent_purchasers"
        val userSignals = mapOf(
            "orderValue" to totalValue,
            "purchaseTime" to System.currentTimeMillis(),
            "categories" to purchasedItems.map { it.category }.distinct(),
            "customerValue" to calculateCustomerValue(orderId)
        )

        val ads = generateCrossSellAds(purchasedItems)

        audienceManager.joinCustomAudience(
            audienceName = audienceName,
            buyer = "https://advertiser.example",
            biddingLogicUri = "https://advertiser.example/bidding-cross-sell.js",
            dailyUpdateUri = "https://advertiser.example/update-purchasers",
            userBiddingSignals = userSignals,
            ads = ads
        )
    }

    private fun calculateInterestLevel(productId: String): Double {
        // Calculate interest based on viewing history
        val prefs = context.getSharedPreferences("product_views", Context.MODE_PRIVATE)
        val viewCount = prefs.getInt(productId, 0)
        return minOf(1.0, 0.3 + viewCount * 0.1)
    }

    private fun calculateCustomerValue(orderId: String): Double {
        // Calculate lifetime value
        return 1.0 // Placeholder
    }

    private fun generateRemarketingAds(
        productId: String,
        category: String,
        price: Double
    ): List<AdData> {
        return listOf(
            AdData(
                renderUri = "https://advertiser.example/ads/product-$productId",
                metadata = mapOf(
                    "type" to "product_remarketing",
                    "productId" to productId,
                    "category" to category,
                    "price" to price,
                    "discount" to 0.1 // 10% discount for remarketing
                )
            )
        )
    }

    private fun generateCartRecoveryAds(
        items: List<CartItem>,
        totalValue: Double
    ): List<AdData> {
        return listOf(
            AdData(
                renderUri = "https://advertiser.example/ads/cart-recovery",
                metadata = mapOf(
                    "type" to "cart_recovery",
                    "cartValue" to totalValue,
                    "discount" to 0.15, // 15% discount for cart recovery
                    "itemCount" to items.size
                )
            )
        )
    }

    private fun generateCrossSellAds(items: List<CartItem>): List<AdData> {
        // Generate ads for complementary products
        return items.flatMap { item ->
            getComplementaryProducts(item).map { complementary ->
                AdData(
                    renderUri = "https://advertiser.example/ads/cross-sell-${complementary.id}",
                    metadata = mapOf(
                        "type" to "cross_sell",
                        "originalProduct" to item.id,
                        "recommendedProduct" to complementary.id
                    )
                )
            }
        }
    }

    private fun getComplementaryProducts(item: CartItem): List<Product> {
        // Get complementary products for cross-sell
        return emptyList() // Placeholder
    }
}

data class CartItem(
    val id: String,
    val name: String,
    val category: String,
    val price: Double
) {
    fun toMap(): Map<String, Any> {
        return mapOf(
            "id" to id,
            "name" to name,
            "category" to category,
            "price" to price
        )
    }
}

data class Product(
    val id: String,
    val name: String,
    val category: String,
    val price: Double
)
```

#### 4. Ad Rendering and Display

**Protected Audience Ad View:**
```kotlin
class ProtectedAudienceAdView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : FrameLayout(context, attrs) {

    private val audienceManager = ProtectedAudienceManager(context)
    private var currentAdSelectionId: Long? = null

    private val webView: WebView = WebView(context).apply {
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = false // Prevent tracking
        settings.cacheMode = WebSettings.LOAD_NO_CACHE
    }

    init {
        addView(webView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT))
    }

    /**
     * Load ad through Protected Audience auction
     */
    suspend fun loadAd(
        seller: String,
        buyers: List<String>,
        contextualSignals: Map<String, Any>
    ) {
        try {
            // Run on-device auction
            val outcome = audienceManager.selectAd(
                seller = seller,
                decisionLogicUri = "https://$seller/decision.js",
                customAudienceBuyers = buyers,
                adSelectionSignals = contextualSignals,
                sellerSignals = mapOf(
                    "floorPrice" to 0.5,
                    "auctionType" to "first_price"
                ),
                perBuyerSignals = buyers.associateWith { buyer ->
                    mapOf("timeout" to 50) // 50ms bidding timeout
                }
            ).getOrThrow()

            currentAdSelectionId = outcome.adSelectionId

            // Render winning ad
            renderAd(outcome.renderUri)

            // Report impression
            audienceManager.reportImpression(outcome.adSelectionId)

        } catch (e: Exception) {
            Log.e("ProtectedAudienceAd", "Failed to load ad", e)
            showFallbackAd()
        }
    }

    private fun renderAd(renderUri: Uri) {
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                // Handle ad clicks
                request?.url?.let { url ->
                    handleAdClick(url)
                }
                return true
            }
        }

        webView.loadUrl(renderUri.toString())
    }

    private fun handleAdClick(url: Uri) {
        // Open ad destination
        val intent = Intent(Intent.ACTION_VIEW, url)
        context.startActivity(intent)

        // Track click
        trackClick()
    }

    private fun trackClick() {
        currentAdSelectionId?.let { adId ->
            // Report click event
            // Note: Actual reporting would use reportEvent API
            Log.d("ProtectedAudienceAd", "Ad clicked: $adId")
        }
    }

    private fun showFallbackAd() {
        // Show contextual ad as fallback
        webView.loadData(
            "<html><body><h3>Contextual Ad</h3></body></html>",
            "text/html",
            "UTF-8"
        )
    }

    fun cleanup() {
        webView.destroy()
    }
}
```

**Compose Integration:**
```kotlin
@Composable
fun ProtectedAudienceAd(
    seller: String,
    buyers: List<String>,
    contextualSignals: Map<String, Any>,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val audienceManager = remember { ProtectedAudienceManager(context) }

    var renderUri by remember { mutableStateOf<Uri?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(seller, buyers) {
        try {
            val outcome = audienceManager.selectAd(
                seller = seller,
                decisionLogicUri = "https://$seller/decision.js",
                customAudienceBuyers = buyers,
                adSelectionSignals = contextualSignals,
                sellerSignals = emptyMap(),
                perBuyerSignals = emptyMap()
            ).getOrThrow()

            renderUri = outcome.renderUri
            isLoading = false

            // Report impression
            audienceManager.reportImpression(outcome.adSelectionId)
        } catch (e: Exception) {
            error = e.message
            isLoading = false
        }
    }

    Box(modifier = modifier) {
        when {
            isLoading -> {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            }
            error != null -> {
                Text(
                    "Ad failed to load",
                    modifier = Modifier.align(Alignment.Center)
                )
            }
            renderUri != null -> {
                AndroidView(
                    factory = { ctx ->
                        WebView(ctx).apply {
                            settings.javaScriptEnabled = true
                            loadUrl(renderUri.toString())
                        }
                    },
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
    }
}
```

### Best Practices

1. **Custom Audience Management:**
   - Set appropriate expiration times (7-30 days)
   - Remove users from audiences after conversion
   - Limit number of custom audiences per user
   - Update audience data regularly

2. **Bidding Strategy:**
   - Implement recency decay (recent interactions valued higher)
   - Consider contextual relevance
   - Set reasonable bid floors
   - Optimize for ROI, not just volume

3. **Privacy Protection:**
   - Never combine with cross-site identifiers
   - Respect audience size minimums (k-anonymity)
   - Implement proper consent management
   - Provide clear opt-out mechanisms

4. **Performance Optimization:**
   - Keep bidding logic lightweight (< 50ms)
   - Minimize JavaScript complexity
   - Cache frequently used data
   - Implement timeouts

5. **Testing:**
   - Test auction logic offline
   - Validate JavaScript execution
   - Monitor auction completion rates
   - A/B test bidding strategies

### Common Pitfalls

1. **Complex bidding logic** → Auction timeouts
   - Keep JavaScript simple and fast

2. **Not handling API unavailability** → App crashes
   - Always check API availability

3. **Forgetting to report impressions** → Inaccurate metrics
   - Always call reportImpression()

4. **Too many custom audiences** → Performance issues
   - Limit to 1000 audiences per device

5. **Not setting expiration** → Stale audiences
   - Set appropriate expiration times

6. **Combining with user IDs** → Privacy violation
   - Keep data on-device only

### Summary

FLEDGE/Protected Audience API enables remarketing without third-party cookies through on-device ad auctions. Advertisers add users to custom audiences, then compete in real-time auctions that run locally on the device. Bidding and decision logic execute in isolated JavaScript environments, ensuring user data never leaves the device. This approach balances personalized advertising with strong privacy protections.

---



## Ответ (RU)

FLEDGE (First Locally-Executed Decision over Groups Experiment), теперь называемый Protected Audience API, обеспечивает remarketing и таргетинг на пользовательские аудитории без cross-site отслеживания. Рекламные аукционы выполняются на устройстве, сохраняя данные пользователя приватными, но позволяя персонализированную рекламу.

#### Архитектура FLEDGE

**Ключевые компоненты:**
- Interest Groups: Группы пользователей с общими интересами
- Custom Audiences: Сегменты аудитории определённые рекламодателем
- On-Device Auction: Выбор рекламы происходит локально
- Trusted Servers: Предоставляют real-time bidding signals
- JavaScript Execution: Bidding/decision логика выполняется на устройстве

**Процесс:**
1. Рекламодатель добавляет пользователя в interest group
2. Издатель запрашивает рекламу
3. On-device аукцион оценивает ставки
4. Победившая реклама возвращается и отображается
5. Impression отчёт отправляется

#### Технические вызовы

**1. Производительность:**
- JavaScript выполнение должно быть < 50мс
- Ограниченные вычислительные ресурсы
- Множественные bidders конкурируют

**2. Приватность:**
- k-anonymity требования
- Нет cross-site identifiers
- Данные остаются на устройстве

**3. Сложность:**
- Bidding логика в JavaScript
- On-device auction механика
- Интеграция с существующими системами

### Лучшие практики

1. **Управление аудиториями:** Expiration times, удаление после конверсии
2. **Bidding стратегия:** Recency decay, контекстуальная релевантность
3. **Защита приватности:** Никаких cross-site ID, k-anonymity
4. **Оптимизация:** Лёгкая bidding логика, timeouts
5. **Тестирование:** Offline тесты, мониторинг completion rates

### Распространённые ошибки

1. Сложная bidding логика → таймауты
2. Не проверять доступность API → краши
3. Забывать reportImpression() → неточные метрики
4. Слишком много аудиторий → проблемы производительности
5. Не устанавливать expiration → устаревшие аудитории
6. Комбинировать с user ID → нарушение приватности

### Резюме

FLEDGE/Protected Audience API обеспечивает remarketing без third-party cookies через on-device аукционы. Рекламодатели добавляют пользователей в custom audiences, затем конкурируют в real-time аукционах, выполняющихся локально на устройстве. Bidding и decision логика выполняются в изолированных JavaScript окружениях, гарантируя что пользовательские данные никогда не покидают устройство.

## Related Questions

- [[q-design-whatsapp-app--android--hard]]
- [[q-retrofit-modify-all-requests--android--hard]]
- [[q-http-protocols-comparison--android--medium]]
