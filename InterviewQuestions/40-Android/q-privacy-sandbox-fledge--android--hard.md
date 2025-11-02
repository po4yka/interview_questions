---
id: android-415
title: "Privacy Sandbox FLEDGE / Privacy Sandbox FLEDGE (Protected Audience API)"
aliases: [FLEDGE, Protected Audience API, Privacy Sandbox FLEDGE, On-Device Ad Auctions]
topic: android
subtopics: [privacy-sdks]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-retrofit-modify-all-requests--android--hard, q-http-protocols-comparison--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [android/privacy-sdks, privacy-sandbox, fledge, protected-audience, remarketing, privacy, advertising, difficulty/hard]
---

# Вопрос (RU)

> Что такое FLEDGE (Protected Audience API) в Privacy Sandbox? Как он обеспечивает remarketing без third-party cookies? Как реализовать on-device аукционы рекламы и каковы технические вызовы?

# Question (EN)

> What is FLEDGE (Protected Audience API) in Privacy Sandbox? How does it enable remarketing without third-party cookies? How do you implement on-device ad auctions and what are the technical challenges?

---

## Ответ (RU)

FLEDGE (Protected Audience API) — система remarketing без cross-site отслеживания. Рекламные аукционы выполняются локально на устройстве, данные пользователя остаются приватными.

**Ключевая идея:** Рекламодатели добавляют пользователей в Custom Audiences, затем конкурируют в real-time аукционах на устройстве. Bidding/decision логика выполняется в изолированном JavaScript окружении.

### Архитектура

**Основные компоненты:**
- **Custom Audiences** - Сегменты аудитории, определённые рекламодателем
- **On-Device Auction** - Выбор рекламы происходит локально
- **JavaScript Bidding** - Логика ставок выполняется изолированно
- **k-anonymity** - Минимальный размер аудитории для privacy

**Процесс:**
1. Рекламодатель добавляет пользователя в Custom Audience (`joinCustomAudience`)
2. Издатель запрашивает рекламу (`selectAds`)
3. On-device аукцион оценивает ставки от всех audiences
4. Побеждает реклама с наивысшим score
5. Impression отчёт отправляется (`reportImpression`)

### Реализация Custom Audiences

**Добавление пользователя в аудиторию:**

```kotlin
// ✅ Корректно - полная конфигурация Custom Audience
suspend fun joinCustomAudience(productId: String, category: String) {
    val customAudience = CustomAudience.Builder()
        .setName("product_viewers_$category")
        .setBuyer(AdTechIdentifier.fromString("https://advertiser.example"))
        .setBiddingLogicUri(Uri.parse("https://advertiser.example/bidding.js"))
        .setDailyUpdateUri(Uri.parse("https://advertiser.example/update"))
        .setUserBiddingSignals(AdData.Builder()
            .setData("""{"productId":"$productId","interestLevel":0.8}""")
            .build())
        .setTrustedBiddingData(TrustedBiddingData.Builder()
            .setTrustedBiddingUri(Uri.parse("https://advertiser.example/signals"))
            .setTrustedBiddingKeys(listOf("key1", "key2"))
            .build())
        .setActivationTime(Instant.now())
        .setExpirationTime(Instant.now().plus(30, ChronoUnit.DAYS))
        .build()

    customAudienceManager.joinCustomAudience(customAudience, executor, callback)
}

// ❌ Неправильно - нет expiration, некорректные signals
suspend fun joinBadAudience() {
    CustomAudience.Builder()
        .setName("audience")
        .setBuyer(AdTechIdentifier.fromString("buyer"))
        // Нет expirationTime - аудитория никогда не удалится
        // Нет userBiddingSignals - нечего использовать для bidding
        .build()
}
```

### On-Device Auction

**Запуск аукциона:**

```kotlin
// ✅ Корректно - полная конфигурация аукциона
suspend fun selectAd(seller: String, buyers: List<String>): AdSelectionOutcome {
    val config = AdSelectionConfig.Builder()
        .setSeller(AdTechIdentifier.fromString(seller))
        .setDecisionLogicUri(Uri.parse("https://$seller/decision.js"))
        .setCustomAudienceBuyers(buyers.map { AdTechIdentifier.fromString(it) })
        .setAdSelectionSignals(AdData.Builder()
            .setData("""{"context":"shopping","category":"electronics"}""")
            .build())
        .setSellerSignals(AdData.Builder()
            .setData("""{"floorPrice":0.5}""")
            .build())
        .setPerBuyerSignals(buyers.associateWith { buyer ->
            AdData.Builder().setData("""{"timeout":50}""").build()
        }.mapKeys { AdTechIdentifier.fromString(it.key) })
        .build()

    return adSelectionManager.selectAds(config, executor, callback)
}
```

### JavaScript Bidding Logic

**Генерация ставки (выполняется на устройстве):**

```javascript
// ✅ Корректно - быстрая bidding логика
function generateBid(customAudience, auctionSignals, perBuyerSignals) {
    const baseValue = customAudience.userBiddingSignals.interestLevel || 1.0;
    const recency = calculateRecency(customAudience.activationTime);
    const bid = baseValue * recency;

    return {
        ad: customAudience.ads[0],
        bid: bid,
        render: customAudience.ads[0].renderUri
    };
}

function calculateRecency(activationTime) {
    const days = (Date.now() - activationTime) / 86400000;
    return Math.max(0.5, 1.0 - days / 30 * 0.5); // Decay over 30 days
}

// ❌ Неправильно - слишком сложно, таймаут
function generateBadBid(customAudience) {
    // Медленные вычисления - вызовет таймаут (>50ms)
    for (let i = 0; i < 1000000; i++) { /* expensive loop */ }
    // Внешние запросы - запрещены в isolated environment
    fetch('https://external.com/data');
}
```

**Decision Logic (seller scoring):**

```javascript
// ✅ Корректно - быстрая scoring логика
function scoreAd(adMetadata, bid, auctionConfig) {
    if (bid <= 0) return 0;

    const floorPrice = auctionConfig.sellerSignals.floorPrice || 0;
    if (bid < floorPrice) return 0;

    // Quality adjustment
    const qualityMultiplier = adMetadata.ctr * 10 + adMetadata.viewability;
    return bid * qualityMultiplier;
}
```

### E-commerce Remarketing

**Отслеживание событий и управление аудиториями:**

```kotlin
// ✅ Корректно - полный remarketing pipeline
class EcommerceRemarketingManager(
    private val audienceManager: CustomAudienceManager
) {
    suspend fun trackProductView(productId: String, category: String, price: Double) {
        joinCustomAudience(
            audienceName = "product_viewers_$category",
            userSignals = mapOf(
                "productId" to productId,
                "price" to price,
                "viewTime" to System.currentTimeMillis()
            ),
            ads = listOf(createProductAd(productId, price))
        )
    }

    suspend fun trackCartAbandonment(cartItems: List<CartItem>, total: Double) {
        joinCustomAudience(
            audienceName = "cart_abandoners",
            userSignals = mapOf(
                "cartValue" to total,
                "itemCount" to cartItems.size
            ),
            ads = listOf(createCartRecoveryAd(cartItems, discount = 0.15))
        )
    }

    suspend fun trackPurchase(orderId: String) {
        // Remove from cart abandoners after purchase
        leaveCustomAudience("cart_abandoners", buyer)

        // Add to purchasers for cross-sell
        joinCustomAudience(
            audienceName = "recent_purchasers",
            userSignals = mapOf("orderValue" to calculateValue(orderId)),
            ads = generateCrossSellAds()
        )
    }

    private fun createProductAd(productId: String, price: Double): AdData {
        return AdData(
            renderUri = "https://advertiser.example/ads/product-$productId",
            metadata = mapOf("discount" to 0.1) // 10% remarketing discount
        )
    }
}
```

### Технические вызовы

**1. Производительность**
- JavaScript execution < 50ms (иначе таймаут)
- Ограниченные ресурсы на устройстве
- Множественные buyers конкурируют одновременно

**Решение:** Минимизировать JavaScript сложность, использовать простые вычисления, избегать циклов.

**2. Privacy ограничения**
- k-anonymity требования (минимум пользователей в audience)
- Нет cross-site identifiers
- Данные остаются на устройстве

**Решение:** Использовать достаточно большие audiences, не комбинировать с user IDs.

**3. JavaScript изоляция**
- Нет доступа к DOM
- Нет network requests
- Нет storage API

**Решение:** Все данные передавать через signals, использовать trusted servers для real-time данных.

**4. API доступность**
- Только Android 13+ (API 33)
- Требует user consent
- Может быть недоступен в регионах

**Решение:** Проверять `Build.VERSION.SDK_INT`, fallback на contextual ads.

---

## Answer (EN)

FLEDGE (Protected Audience API) enables remarketing without cross-site tracking. Ad auctions run locally on-device, keeping user data private while allowing personalized advertising.

**Core Concept:** Advertisers add users to Custom Audiences, then compete in real-time on-device auctions. Bidding/decision logic executes in isolated JavaScript environments.

### Architecture

**Components:**
- **Custom Audiences** - Advertiser-defined audience segments
- **On-Device Auction** - Ad selection happens locally
- **JavaScript Bidding** - Isolated bidding logic execution
- **k-anonymity** - Minimum audience size for privacy

**Flow:**
1. Advertiser adds user to Custom Audience (`joinCustomAudience`)
2. Publisher requests ad (`selectAds`)
3. On-device auction evaluates bids from all audiences
4. Highest scoring ad wins
5. Impression report sent (`reportImpression`)

### Custom Audience Implementation

**Adding user to audience:**

```kotlin
// ✅ Correct - full Custom Audience configuration
suspend fun joinCustomAudience(productId: String, category: String) {
    val customAudience = CustomAudience.Builder()
        .setName("product_viewers_$category")
        .setBuyer(AdTechIdentifier.fromString("https://advertiser.example"))
        .setBiddingLogicUri(Uri.parse("https://advertiser.example/bidding.js"))
        .setDailyUpdateUri(Uri.parse("https://advertiser.example/update"))
        .setUserBiddingSignals(AdData.Builder()
            .setData("""{"productId":"$productId","interestLevel":0.8}""")
            .build())
        .setTrustedBiddingData(TrustedBiddingData.Builder()
            .setTrustedBiddingUri(Uri.parse("https://advertiser.example/signals"))
            .setTrustedBiddingKeys(listOf("key1", "key2"))
            .build())
        .setActivationTime(Instant.now())
        .setExpirationTime(Instant.now().plus(30, ChronoUnit.DAYS))
        .build()

    customAudienceManager.joinCustomAudience(customAudience, executor, callback)
}

// ❌ Wrong - no expiration, incorrect signals
suspend fun joinBadAudience() {
    CustomAudience.Builder()
        .setName("audience")
        .setBuyer(AdTechIdentifier.fromString("buyer"))
        // No expirationTime - audience never expires
        // No userBiddingSignals - nothing to use for bidding
        .build()
}
```

### On-Device Auction

**Running auction:**

```kotlin
// ✅ Correct - full auction configuration
suspend fun selectAd(seller: String, buyers: List<String>): AdSelectionOutcome {
    val config = AdSelectionConfig.Builder()
        .setSeller(AdTechIdentifier.fromString(seller))
        .setDecisionLogicUri(Uri.parse("https://$seller/decision.js"))
        .setCustomAudienceBuyers(buyers.map { AdTechIdentifier.fromString(it) })
        .setAdSelectionSignals(AdData.Builder()
            .setData("""{"context":"shopping","category":"electronics"}""")
            .build())
        .setSellerSignals(AdData.Builder()
            .setData("""{"floorPrice":0.5}""")
            .build())
        .setPerBuyerSignals(buyers.associateWith { buyer ->
            AdData.Builder().setData("""{"timeout":50}""").build()
        }.mapKeys { AdTechIdentifier.fromString(it.key) })
        .build()

    return adSelectionManager.selectAds(config, executor, callback)
}
```

### JavaScript Bidding Logic

**Generating bid (runs on-device):**

```javascript
// ✅ Correct - fast bidding logic
function generateBid(customAudience, auctionSignals, perBuyerSignals) {
    const baseValue = customAudience.userBiddingSignals.interestLevel || 1.0;
    const recency = calculateRecency(customAudience.activationTime);
    const bid = baseValue * recency;

    return {
        ad: customAudience.ads[0],
        bid: bid,
        render: customAudience.ads[0].renderUri
    };
}

function calculateRecency(activationTime) {
    const days = (Date.now() - activationTime) / 86400000;
    return Math.max(0.5, 1.0 - days / 30 * 0.5); // Decay over 30 days
}

// ❌ Wrong - too complex, will timeout
function generateBadBid(customAudience) {
    // Slow computation - will timeout (>50ms)
    for (let i = 0; i < 1000000; i++) { /* expensive loop */ }
    // External requests - forbidden in isolated environment
    fetch('https://external.com/data');
}
```

**Decision logic (seller scoring):**

```javascript
// ✅ Correct - fast scoring logic
function scoreAd(adMetadata, bid, auctionConfig) {
    if (bid <= 0) return 0;

    const floorPrice = auctionConfig.sellerSignals.floorPrice || 0;
    if (bid < floorPrice) return 0;

    // Quality adjustment
    const qualityMultiplier = adMetadata.ctr * 10 + adMetadata.viewability;
    return bid * qualityMultiplier;
}
```

### E-commerce Remarketing

**Event tracking and audience management:**

```kotlin
// ✅ Correct - complete remarketing pipeline
class EcommerceRemarketingManager(
    private val audienceManager: CustomAudienceManager
) {
    suspend fun trackProductView(productId: String, category: String, price: Double) {
        joinCustomAudience(
            audienceName = "product_viewers_$category",
            userSignals = mapOf(
                "productId" to productId,
                "price" to price,
                "viewTime" to System.currentTimeMillis()
            ),
            ads = listOf(createProductAd(productId, price))
        )
    }

    suspend fun trackCartAbandonment(cartItems: List<CartItem>, total: Double) {
        joinCustomAudience(
            audienceName = "cart_abandoners",
            userSignals = mapOf(
                "cartValue" to total,
                "itemCount" to cartItems.size
            ),
            ads = listOf(createCartRecoveryAd(cartItems, discount = 0.15))
        )
    }

    suspend fun trackPurchase(orderId: String) {
        // Remove from cart abandoners after purchase
        leaveCustomAudience("cart_abandoners", buyer)

        // Add to purchasers for cross-sell
        joinCustomAudience(
            audienceName = "recent_purchasers",
            userSignals = mapOf("orderValue" to calculateValue(orderId)),
            ads = generateCrossSellAds()
        )
    }

    private fun createProductAd(productId: String, price: Double): AdData {
        return AdData(
            renderUri = "https://advertiser.example/ads/product-$productId",
            metadata = mapOf("discount" to 0.1) // 10% remarketing discount
        )
    }
}
```

### Technical Challenges

**1. Performance**
- JavaScript execution < 50ms (else timeout)
- Limited on-device resources
- Multiple buyers competing simultaneously

**Solution:** Minimize JavaScript complexity, use simple calculations, avoid loops.

**2. Privacy constraints**
- k-anonymity requirements (minimum users in audience)
- No cross-site identifiers
- Data stays on-device

**Solution:** Use sufficiently large audiences, don't combine with user IDs.

**3. JavaScript isolation**
- No DOM access
- No network requests
- No storage API

**Solution:** Pass all data through signals, use trusted servers for real-time data.

**4. API availability**
- Only Android 13+ (API 33)
- Requires user consent
- May be unavailable in regions

**Solution:** Check `Build.VERSION.SDK_INT`, fallback to contextual ads.

---

## Follow-ups

- How does k-anonymity work and what are minimum audience sizes?
- How to test FLEDGE implementation without production traffic?
- What are the performance implications of running multiple auctions?
- How to migrate from third-party cookie remarketing to FLEDGE?
- How to handle fallback when Protected Audience API is unavailable?
- What are the reporting limitations compared to traditional ad tracking?

## References

- [Privacy Sandbox Developer Guide](https://developer.android.com/design-for-safety/privacy-sandbox)
- [FLEDGE API Explainer](https://github.com/WICG/turtledove/blob/main/FLEDGE.md)
- [Android Ad Services API](https://developer.android.com/design-for-safety/privacy-sandbox/reference/adservices/packages)

## Related Questions

### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Network protocols for ad delivery

### Related (Same Level)
- [[q-retrofit-modify-all-requests--android--hard]] - Network request modification
- [[q-design-whatsapp-app--android--hard]] - System design with privacy considerations

### Advanced (Harder)
- Design a complete privacy-preserving ad platform using all Privacy Sandbox APIs
