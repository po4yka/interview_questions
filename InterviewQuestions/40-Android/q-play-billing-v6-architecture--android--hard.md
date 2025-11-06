---
id: android-618
title: Play Billing v6 Architecture / Архитектура Play Billing v6
aliases:
  - Play Billing v6 Architecture
  - Архитектура Play Billing v6
topic: android
subtopics:
  - billing
  - monetization
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-play-billing
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/billing
  - monetization
  - difficulty/hard
sources:
  - url: https://developer.android.com/google/play/billing/integrate
    note: Google Play Billing integration guide
  - url: https://developer.android.com/google/play/billing/migrate-gpblv6
    note: Billing v6 migration
---

# Вопрос (RU)
> Как спроектировать архитектуру интеграции Play Billing v6: от каталога товаров и гибких подписок до бэкенд-проверки, RTDN и обработки отложенных покупок?

# Question (EN)
> How do you architect a Play Billing v6 integration covering product catalog, flexible subscriptions, backend verification, RTDN, and pending purchase handling?

---

## Ответ (RU)

### 1. Архитектура компонентов

- **Client**: `BillingClient` (v6), `PurchasesUpdatedListener`, `BillingClientStateListener`.
- **Server**: Play Developer API v3, RTDN Pub/Sub (Cloud Functions/Cloud Run).
- **Storage**: локальный кэш (Room/Proto DataStore) для product details и статуса подписок.
- **UI**: `BillingFlowParams.ProductDetailsParams`.

### 2. Каталог и подписки

```kotlin
val params = QueryProductDetailsParams.newBuilder()
    .setProductList(
        listOf(
            Product.newBuilder()
                .setProductId("premium_monthly")
                .setProductType(ProductType.SUBS)
                .build()
        )
    ).build()

billingClient.queryProductDetailsAsync(params) { billingResult, detailsList ->
    // cache detailsList
}
```

- Подписки: base plan + offers, pricing phases (free trial, intro price).
- Сохраняйте `ProductDetails.subscriptionOfferDetails`.

### 3. Запуск покупки

```kotlin
val offerToken = product.subscriptionOfferDetails!!.first().offerToken

val billingParams = BillingFlowParams.newBuilder()
    .setProductDetailsParamsList(
        listOf(
            BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(product)
                .setOfferToken(offerToken)
                .build()
        )
    ).build()

billingClient.launchBillingFlow(activity, billingParams)
```

- Pending purchases требуют UI уведомления и `enablePendingPurchases()`.
- Для multi-quantity (`BillingFlowParams.setIsOfferPersonalized`) используйте дополнительные флаги.

### 4. Обработка покупок

```kotlin
override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
    purchases?.forEach { purchase ->
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            verifyAndAcknowledge(purchase)
        } else if (purchase.purchaseState == Purchase.PurchaseState.PENDING) {
            // notify user
        }
    }
}
```

- Всегда вызывайте `acknowledgePurchase`; иначе через 3 дня транзакция отменится.
- Для consumables используйте `consumeAsync`.

### 5. Серверная валидация

- Play Developer API: `purchases.subscriptionsv2.get` / `purchases.products.get`.
- RTDN (Real-time developer notifications) подписывается на Pub/Sub и сообщает о отзыве/продлении.
- Храните `purchaseToken`, `accountIdentifiers`.

### 6. Edge-кейсы

- `BillingClient` state перезапускайте при `SERVICE_DISCONNECTED`.
- Отложенные покупки: ожидайте `PurchaseState.PURCHASED` после подтверждения опекуном.
- Промо-коды/предложения: `offerToken` обязателен.

### 7. Compliance

- Google Play требует информативного UI (цены, условия, управление подписками).
- Храните логи транзакций для возвратов (refund).
- GDPR/CPA: обработка персональных данных (accountId) через шифрование и consent.

---

## Answer (EN)

- Structure the integration with a v6 `BillingClient`, caching product details locally, and launching flows using offer tokens for flexible subscriptions.
- Always verify purchases server-side via Play Developer API v3 and subscribe to RTDN for lifecycle changes (renewals, revocations).
- Handle pending purchases by enabling pending support and surfacing UI hints until approval.
- Acknowledge or consume purchases promptly to avoid auto refunds.
- Ensure compliance: expose price breakdowns, manage subscription center deep links, and encrypt stored purchase tokens.

---

## Follow-ups
- Как синхронизировать Play Billing с бэкендом, если пользователи меняют подписку вне приложения?
- Какие best practices по кэшированию каталога и офферов?
- Как работать с многопользовательскими устройствами (Kids/Family accounts)?

## References
- [[c-play-billing]]
- https://developer.android.com/google/play/billing/integrate
- https://developer.android.com/google/play/billing/migrate-gpblv6

## Related Questions

- [[c-play-billing]]
