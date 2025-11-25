---
id: android-415
title: Privacy Sandbox FLEDGE / Privacy Sandbox FLEDGE (Protected Audience API)
aliases: [FLEDGE, On-Device Ad Auctions, Privacy Sandbox FLEDGE, Protected Audience API]
topic: android
subtopics:
  - privacy-sdks
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-permissions
  - q-http-protocols-comparison--android--medium
  - q-privacy-sandbox-attribution--android--medium
  - q-privacy-sandbox-sdk-runtime--android--hard
  - q-privacy-sandbox-topics-api--android--medium
  - q-retrofit-modify-all-requests--android--hard
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [advertising, android/privacy-sdks, difficulty/hard, fledge, privacy, privacy-sandbox, protected-audience, remarketing]
date created: Saturday, November 1st 2025, 12:47:01 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)

> Что такое FLEDGE (Protected Audience API) в Privacy Sandbox? Как он обеспечивает remarketing без third-party cookies? Как реализовать on-device аукционы рекламы и каковы технические вызовы?

# Question (EN)

> What is FLEDGE (Protected Audience API) in Privacy Sandbox? How does it enable remarketing without third-party cookies? How do you implement on-device ad auctions and what are the technical challenges?

---

## Ответ (RU)

FLEDGE (Protected Audience API) — механизм ремаркетинга без cross-site отслеживания и без third-party cookies. Рекламные аукционы выполняются локально на устройстве, членство пользователя в аудиториях и сигналы интересов хранятся на устройстве и комбинируются с контекстом запроса, а не с third-party cookies.

**Ключевая идея:** Рекламодатели через ad tech-платформы добавляют пользователя в custom audience (аудитории, связанные с конкретным buyer), затем конкурируют в on-device аукционах. Bidding/decision логика выполняется в изолированном JavaScript-окружении, без доступа к кросс-сайтовым идентификаторам и без возможности строить third-party cookie трекинг.

### Архитектура

**Основные компоненты:**
- **Custom Audiences** - Сегменты аудитории, определённые buyer'ом (ad tech/рекламодатель), хранящиеся на устройстве.
- **On-Device Auction** - Выбор рекламы происходит локально.
- **JavaScript Bidding/Scoring** - Логика ставок и оценивания выполняется изолированно в песочнице.
- **k-anonymity / policy thresholds** - Требования к минимальному размеру аудитории и другим условиям использования, определяемые платформенной политикой для гарантий приватности.

**Процесс (упрощённо):**
1. Рекламодатель/платформа добавляет пользователя в Custom Audience (`joinCustomAudience`).
2. Издатель запрашивает рекламу (`selectAds`) в контексте своего инвентаря.
3. On-device аукцион запускает buyer bidding и seller scoring скрипты для релевантных аудиторий.
4. Побеждает креатив с наивысшим score.
5. Отчёт об impression отправляется через соответствующий reporting API (в агрегированном/анонимизированном виде, согласно политикам Privacy Sandbox).

Все ниже приведённые примеры кода являются схематичными и демонстрируют концепции. Фактические сигнатуры, типы и классы AdServices/Privacy Sandbox API могут отличаться; необходимо проверять актуальную документацию.

### Реализация Custom Audiences

Ниже — схематичный пример использования Protected Audience API; сигнатуры и типы могут отличаться от конкретной версии AdServices SDK.

**Добавление пользователя в аудиторию (упрощённый пример):**

```kotlin
// ✅ Иллюстративный пример — конфигурация Custom Audience (срок жизни, сигналы, bidding-логика)
// Используйте реальные классы и сигнатуры AdServices SDK.
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

    // Реальный API использует асинхронные вызовы (Executor/Callback, ListenableFuture или suspend-обёртки).
    customAudienceManager.joinCustomAudience(customAudience, executor, callback)
}

// ⚠ Антипаттерн — пример проблемной конфигурации (иллюстративно)
suspend fun joinBadAudience() {
    CustomAudience.Builder()
        .setName("audience")
        .setBuyer(AdTechIdentifier.fromString("https://buyer.example"))
        // Отсутствует expirationTime — нарушает лучшие практики и может противоречить требованиям политики.
        // Нет полезных сигналов/объявлений — аудитория не несёт ценности для bidding.
        .build()
}
```

### On-Device Auction

**Запуск аукциона (схематично):**

```kotlin
// ✅ Иллюстративный пример — конфигурация аукциона с seller, buyers и сигналами.
// В реальном коде используйте фактический AdSelectionManager API и асинхронные вызовы.
suspend fun selectAd(seller: String, buyers: List<String>) {
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
        .setPerBuyerSignals(buyers.associateWith {
            AdData.Builder().setData("""{"timeout":50}""").build()
        }.mapKeys { AdTechIdentifier.fromString(it.key) })
        .build()

    // В реальном API аукцион запускается асинхронно, например:
    // adSelectionManager.selectAds(config, executor, callback)
}
```

### JavaScript Bidding Logic

Ниже приведены упрощённые примеры логики bidding/scoring в песочнице. Структуры `customAudience`, `adMetadata` и поля в примере схематичны и не отражают дословно реальные типы API.

**Генерация ставки (выполняется на устройстве в изолированной среде, схематично):**

```javascript
// ✅ Упрощённый пример быстрой bidding-логики (псевдокод)
function generateBid(customAudience, auctionSignals, perBuyerSignals) {
    const baseValue = (customAudience.userBiddingSignals && customAudience.userBiddingSignals.interestLevel) || 1.0;
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
    return Math.max(0.5, 1.0 - (days / 30) * 0.5); // Плавное затухание в течение 30 дней
}

// ❌ Антипаттерн — может привести к таймауту/нарушению ограничений среды
function generateBadBid(customAudience) {
    // Тяжёлые вычисления — риск превышения жёстких ограничений по времени выполнения
    for (let i = 0; i < 1000000; i++) { /* expensive loop */ }
    // Внешние запросы из bidding JS запрещены в изолированной среде
    fetch('https://external.com/data');
}
```

**Decision Logic (seller scoring, изолированная логика продавца, псевдокод):**

```javascript
// ✅ Упрощённый пример быстрой scoring-логики (псевдокод)
function scoreAd(adMetadata, bid, auctionConfig) {
    if (bid <= 0) return 0;

    const floorPrice = (auctionConfig.sellerSignals && auctionConfig.sellerSignals.floorPrice) || 0;
    if (bid < floorPrice) return 0;

    // Пример учёта качества (поля условные)
    const qualityMultiplier = (adMetadata.ctr || 0) * 10 + (adMetadata.viewability || 0);
    return bid * qualityMultiplier;
}
```

### E-commerce Remarketing

Ниже показан паттерн: как события e-commerce могут мапиться в custom audiences. Код иллюстративный: используются упрощённые типы и вспомогательные методы, а не реальные классы AdServices SDK.

**Отслеживание событий и управление аудиториями (псевдокод):**

```kotlin
// ✅ Иллюстративный пример ремаркетинг-пайплайна поверх Protected Audience API.
// Фактическая реализация должна использовать реальные API AdServices и типы данных.
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
        // После покупки пользователь должен быть удалён из "cart_abandoners"
        leaveCustomAudience("cart_abandoners", buyer = /* соответствующий AdTechIdentifier */)

        // И добавлен в аудиторию покупателей для cross-sell
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

    // Реализации joinCustomAudience/leaveCustomAudience/calculateValue/... подразумеваются
    // и должны быть основаны на конкретном AdServices API.
}
```

### Технические Вызовы

**1. Производительность**
- Жёсткие ограничения на время исполнения JS в песочнице (нужно укладываться в очень небольшой бюджет времени; точные лимиты зависят от реализации и могут меняться).
- Ограниченные ресурсы на устройстве.
- Параллельные аукционы и несколько buyers.

**Решение:** Держать bidding/decision JS максимально простым и детерминированным, избегать тяжёлых вычислений и сложных структур.

**2. Privacy-ограничения**
- Требования к минимальному размеру аудитории и другим условиям использования (k-anonymity и связанные пороги определяются политиками Privacy Sandbox/платформы).
- Запрет на cross-site идентификаторы и прямой user-level трекинг.
- Данные интересов и membership аудиторий хранятся и обрабатываются на устройстве.

**Решение:** Формировать достаточно крупные сегменты, избегать 1:1 user IDs и fingerprinting-сигналов, соблюдать официальные политики.

**3. Изоляция JavaScript**
- Нет доступа к DOM.
- Нет прямых network-запросов из bidding/scoring JS.
- Нет доступа к persistent storage API.

**Решение:**
- Передавать необходимые данные через signals (adSelectionSignals, sellerSignals, perBuyerSignals, userBiddingSignals).
- Для обновления сигналов и trusted данных использовать разрешённые механизмы (daily update, Trusted Bidding Data endpoints) вне on-device JS выполнения.

**4. Доступность API**
- Protected Audience API доступен на устройствах, участвующих в программе Privacy Sandbox on Android (изначально Android 13+ с AdServices; возможно распространение через системные/Play сервисы в зависимости от релиза и региона).
- Требуется согласие пользователя и соблюдение политики Google.
- Может быть недоступен в отдельных регионах или на конкретных девайсах.

**Решение:** Проверять доступность AdServices/Privacy Sandbox API на устройстве и статус consent во время выполнения; при недоступности — fallback на контекстную рекламу и другие privacy-preserving механизмы.

---

## Answer (EN)

FLEDGE (Protected Audience API) enables remarketing without cross-site tracking and without third-party cookies. Ad auctions run locally on the device; audience membership and interest signals are stored on-device and combined with the publisher's contextual request signals instead of third-party cookies.

**Core Concept:** Advertisers (via ad tech platforms) add users into custom audiences (audiences bound to specific buyers). When a publisher issues an ad request, eligible buyers participate in an on-device auction. Bidding and decision logic executes in an isolated JavaScript environment without access to cross-site identifiers and without enabling traditional third-party cookie-based tracking.

### Architecture

**Components:**
- **Custom Audiences** - Buyer-defined audience segments stored on-device.
- **On-Device Auction** - Ad selection happens locally on the device.
- **JavaScript Bidding/Scoring** - Bidding and scoring logic runs in a sandboxed JS environment.
- **k-anonymity / policy thresholds** - Minimum audience size and other eligibility conditions enforced via platform policies to protect privacy.

**Flow (simplified):**
1. Advertiser/ad tech adds the user to a Custom Audience via `joinCustomAudience`.
2. Publisher initiates an ad request via `selectAds` within its own context.
3. The on-device auction runs buyer bidding scripts and seller scoring scripts for relevant audiences.
4. The highest scoring ad/creative wins.
5. Impression reporting is performed through the corresponding reporting APIs in a privacy-preserving (aggregated/limited) manner in line with Privacy Sandbox policies.

All code examples below are schematic and for conceptual illustration only. Actual AdServices/Privacy Sandbox APIs (class names, methods, async patterns) MUST be validated against the latest official documentation.

### Custom Audience Implementation

Below is a schematic example of using the Protected Audience API; exact signatures and types may vary by AdServices SDK version.

**Adding user to audience (simplified example):**

```kotlin
// ✅ Illustrative example — Custom Audience configuration (lifetime, signals, bidding logic).
// Use concrete AdServices SDK classes and signatures in real code.
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

    // Real APIs use async calls (Executor/Callback, futures, or suspend wrappers).
    customAudienceManager.joinCustomAudience(customAudience, executor, callback)
}

// ⚠ Anti-pattern — example of a problematic configuration (illustrative)
suspend fun joinBadAudience() {
    CustomAudience.Builder()
        .setName("audience")
        .setBuyer(AdTechIdentifier.fromString("https://buyer.example"))
        // Missing expirationTime — violates lifecycle best practices and may conflict with policy.
        // Missing useful signals/ads — audience provides no value for bidding.
        .build()
}
```

### On-Device Auction

**Running auction (schematic):**

```kotlin
// ✅ Illustrative example — auction config with seller, buyers, and signals.
// In production, wire this to the real AdSelectionManager API and its async model.
suspend fun selectAd(seller: String, buyers: List<String>) {
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
        .setPerBuyerSignals(buyers.associateWith {
            AdData.Builder().setData("""{"timeout":50}""").build()
        }.mapKeys { AdTechIdentifier.fromString(it.key) })
        .build()

    // In actual implementations, trigger the auction asynchronously, e.g.:
    // adSelectionManager.selectAds(config, executor, callback)
}
```

### JavaScript Bidding Logic

The following examples illustrate the shape of bidding/scoring logic. Object shapes and field names are schematic, not exact API definitions.

**Generating bid (runs on-device in an isolated environment, pseudo-code):**

```javascript
// ✅ Simplified example of fast bidding logic (pseudo-code)
function generateBid(customAudience, auctionSignals, perBuyerSignals) {
    const baseValue = (customAudience.userBiddingSignals && customAudience.userBiddingSignals.interestLevel) || 1.0;
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
    return Math.max(0.5, 1.0 - (days / 30) * 0.5); // Decay over ~30 days
}

// ❌ Anti-pattern — likely to hit execution limits / violate environment constraints
function generateBadBid(customAudience) {
    // Heavy computation — may exceed strict execution time limits
    for (let i = 0; i < 1000000; i++) { /* expensive loop */ }
    // Network calls from bidding JS are forbidden in the sandbox
    fetch('https://external.com/data');
}
```

**Decision logic (seller scoring, isolated, pseudo-code):**

```javascript
// ✅ Simplified example of fast scoring logic (pseudo-code)
function scoreAd(adMetadata, bid, auctionConfig) {
    if (bid <= 0) return 0;

    const floorPrice = (auctionConfig.sellerSignals && auctionConfig.sellerSignals.floorPrice) || 0;
    if (bid < floorPrice) return 0;

    // Example quality adjustment using hypothetical fields
    const qualityMultiplier = (adMetadata.ctr || 0) * 10 + (adMetadata.viewability || 0);
    return bid * qualityMultiplier;
}
```

### E-commerce Remarketing

Pattern-level example: mapping typical e-commerce events into Protected Audience custom audiences. This is illustrative and omits real API wiring and concrete types.

**Event tracking and audience management (pseudo-code):**

```kotlin
// ✅ Illustrative example of a remarketing pipeline built on top of Protected Audience API.
// Real implementation must be based on the concrete AdServices/Privacy Sandbox APIs.
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
        leaveCustomAudience("cart_abandoners", buyer = /* appropriate AdTechIdentifier */)

        // Add to purchasers audience for cross-sell
        joinCustomAudience(
            audienceName = "recent_purchasers",
            userSignals = mapOf("orderValue" to calculateValue(orderId)),
            ads = generateCrossSellAds()
        )
    }

    private fun createProductAd(productId: String, price: Double): AdData {
        return AdData(
            renderUri = "https://advertiser.example/ads/product-$productId",
            metadata = mapOf("discount" to 0.1)
        )
    }

    // Implementations of joinCustomAudience / leaveCustomAudience / calculateValue / etc.
    // must use the concrete AdServices API.
}
```

### Technical Challenges

**1. Performance**
- Strict execution limits for JS sandbox; bidding and scoring must complete within a small time budget (implementation-specific).
- Limited device resources.
- Multiple concurrent auctions and buyers.

**Solution:** Keep JS logic deterministic and lightweight; avoid heavy loops and complex computations.

**2. Privacy constraints**
- Minimum audience size and other eligibility thresholds (k-anonymity style guarantees) defined and enforced by Privacy Sandbox policies/platform behavior.
- No cross-site identifiers or direct user-level tracking.
- Audience membership and interest data stored and evaluated on-device.

**Solution:** Use sufficiently large segments; avoid combining with user IDs or fingerprinting techniques; comply with official policies.

**3. JavaScript isolation**
- No DOM access.
- No direct network access from bidding/scoring JS.
- No persistent storage APIs.

**Solution:**
- Provide required data via signals (adSelectionSignals, sellerSignals, perBuyerSignals, userBiddingSignals).
- Use allowed mechanisms such as daily updates and Trusted Bidding Data endpoints to refresh signals outside the sandboxed JS execution.

**4. API availability**
- Protected Audience API is available on devices participating in the Privacy Sandbox on Android program (initially Android 13+ with AdServices; may be delivered via system/Play services depending on rollout and region).
- Requires user consent and compliance with Google policies.
- May be unavailable in certain regions or on specific devices.

**Solution:** Check for AdServices/Privacy Sandbox availability and user consent at runtime; when unavailable, fall back to contextual ads and other privacy-preserving approaches.

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

### Prerequisites / Concepts

- [[c-permissions]]


### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Network protocols for ad delivery

### Related (Same Level)
- [[q-retrofit-modify-all-requests--android--hard]] - Network request modification
- [[q-design-whatsapp-app--android--hard]] - System design with privacy considerations

### Advanced (Harder)
- Design a complete privacy-preserving ad platform using all Privacy Sandbox APIs
