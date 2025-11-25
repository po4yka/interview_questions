---
id: android-618
title: Play Billing v6 Architecture / Архитектура Play Billing v6
aliases: [Play Billing v6 Architecture, Архитектура Play Billing v6]
topic: android
subtopics:
  - billing
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-play-billing
  - q-android-release-pipeline-cicd--android--hard
  - q-multi-module-best-practices--android--hard
  - q-play-feature-delivery--android--medium
  - q-quick-settings-tiles-architecture--android--medium
created: 2024-11-02
updated: 2025-11-10
tags: [android/billing, difficulty/hard]
sources:
- url: "https://developer.android.com/google/play/billing/integrate"
  note: Google Play Billing integration guide
- url: "https://developer.android.com/google/play/billing/migrate-gpblv6"
  note: Billing v6 migration

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)
> Как спроектировать архитектуру интеграции Play Billing v6: от каталога товаров и гибких подписок до бэкенд-проверки, RTDN и обработки отложенных покупок?

# Question (EN)
> How do you architect a Play Billing v6 integration covering product catalog, flexible subscriptions, backend verification, RTDN, and pending purchase handling?

---

## Ответ (RU)

### Краткий Вариант

- `BillingClient` v6 с `enablePendingPurchases`, кэш `ProductDetails`, явное управление base plans и offers.
- Сервер с Play Developer API, RTDN (Pub/Sub), хранением `purchaseToken` + связки с пользователем.
- Централизованная обработка покупок: серверная валидация, `acknowledge`/`consume`, история транзакций.
- Отказоустойчивая обработка ошибок (`SERVICE_DISCONNECTED`), отложенных покупок и смен/отзывов подписок.
- Соблюдение UI/правовых требований Google Play.

### Подробная Версия

#### Требования

- Функциональные:
  - Поддержка in-app товаров и гибких подписок (base plans + offers).
  - Обработка отложенных покупок, multi-quantity для INAPP и апгрейдов/даунгрейдов подписок.
  - Консистентные права доступа между приложением и бэкендом.
  - Реакция на события жизненного цикла из Play (renewal, expiration, revoke, pause и т.п.).
- Нефункциональные:
  - Устойчивость к сетевым и сервисным сбоям.
  - Безопасная обработка токенов и идентификаторов пользователей.
  - Аудируемая история транзакций и соответствие политикам.

#### Архитектура

##### 1. Архитектура Компонентов

- **Client**: `BillingClient` (v6), `PurchasesUpdatedListener`, `BillingClientStateListener`.
- **Server**: Play Developer API v3, RTDN через Pub/Sub (Cloud Functions/Cloud Run или аналогичная обработка уведомлений).
- **Storage**: локальный кэш (Room/Proto DataStore) для `ProductDetails` и статуса подписок; бэкенд-БД как источник истины по правам доступа.
- **UI**: использование `BillingFlowParams.ProductDetailsParams` для выбора base plan и offer по `offerToken`.

##### 2. Каталог И Подписки

```kotlin
val params = QueryProductDetailsParams.newBuilder()
    .setProductList(
        listOf(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId("premium_monthly")
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
        )
    ).build()

billingClient.queryProductDetailsAsync(params) { billingResult, detailsList ->
    // cache detailsList (ProductDetails with base plans and offers)
}
```

- Подписки: используйте base plans и subscription offers, pricing phases (free trial, intro price, recurring).
- Сохраняйте и учитывайте `ProductDetails.subscriptionOfferDetails` при выборе подходящего `offerToken` согласно бизнес-логике (регион, промо, eligibility).

##### 3. Запуск Покупки

```kotlin
val offerToken = product.subscriptionOfferDetails!!
    .first()
    .offerToken

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

- Отложенные покупки требуют `enablePendingPurchases()` при создании `BillingClient` и понятного UI-уведомления, что покупка в ожидании.
- Для multi-quantity покупок (только для INAPP в v6) используйте `BillingFlowParams.ProductDetailsParams.setQuantity(quantity)`.
- `setIsOfferPersonalized` относится к маркировке персонализированных предложений, а не к количеству.

##### 4. Обработка Покупок

```kotlin
override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
    if (result.responseCode != BillingClient.BillingResponseCode.OK || purchases == null) {
        // handle error / user cancellation
        return
    }

    purchases.forEach { purchase ->
        when (purchase.purchaseState) {
            Purchase.PurchaseState.PURCHASED -> {
                // Отправить на сервер для проверки и acknowledgment/consume
                verifyAndAcknowledge(purchase)
            }
            Purchase.PurchaseState.PENDING -> {
                // Уведомить пользователя, что покупка в ожидании подтверждения
            }
            Purchase.PurchaseState.UNSPECIFIED_STATE -> {
                // Игнорировать или залогировать
            }
        }
    }
}
```

- После успешной проверки на сервере всегда вызывайте `acknowledgePurchase`; иначе транзакция будет автоматически возвращена через короткий период.
- Для consumable-товаров используйте `consumeAsync` (также после серверной проверки).

##### 5. Серверная Валидация

- Используйте Play Developer API: `purchases.subscriptionsv2.get` для подписок и `purchases.products.get` для разовых покупок.
- RTDN (Real-time developer notifications): подпишитесь через Pub/Sub; обрабатывайте события (renewal, expiration, revoke, pause, restart и т.п.) и синхронизируйте состояние подписок с вашей БД и выдачей прав.
- Храните `purchaseToken` и (опционально) обфусцированные идентификаторы (`obfuscatedAccountId` / `obfuscatedProfileId`) для сопоставления с аккаунтом.

##### 6. Edge-кейсы

- При ошибках `BillingClient` типа `SERVICE_DISCONNECTED` восстанавливайте соединение через `startConnection` и повторяйте запросы каталога/покупок с бэкоффом.
- Отложенные покупки: периодически (или по событию) запрашивайте актуальные покупки (`queryPurchasesAsync`) и ожидайте `PurchaseState.PURCHASED` после подтверждения опекуном, затем применяйте entitlement и подтверждайте покупку.
- Промо-коды/подписочные предложения: корректно используйте соответствующий `offerToken`, если он требуется для выбранного base plan/offer.

##### 7. Compliance

- Google Play требует информативного UI: прозрачные цены, условия подписки, период, пробный период/intro price, как отменить и как управлять подпиской (включая ссылку в центр управления подписками Play).
- Ведите историю транзакций на сервере, чтобы корректно обрабатывать возвраты (refund), истечения и смены планов.
- Персональные данные и идентификаторы (например, обфусцированные account/profile ID) храните с учетом требований GDPR/CCPA: минимизация данных, шифрование at rest и in transit, явный consent там, где применимо.

---

## Answer (EN)

### Short Version

- Use `BillingClient` v6 with `enablePendingPurchases`, cache `ProductDetails`, and explicitly manage base plans and subscription offers.
- Introduce a backend that validates purchases via Play Developer API, processes RTDN messages, and owns entitlements and transaction history.
- Centralize purchase handling: server-side validation, `acknowledge`/`consume`, robust error handling, and compliance with Play policies.

### Detailed Version

#### Requirements

- Functional:
  - Support in-app products and flexible subscriptions (base plans + offers).
  - Handle pending purchases, multi-quantity in-app items, and subscription upgrades/downgrades.
  - Keep entitlements consistent between app and backend.
  - React to lifecycle events from Play (renewal, expiration, revoke, pause, etc.).
- Non-functional:
  - Resilient to network/service issues.
  - Secure handling of tokens and user identifiers.
  - Auditable transaction history and policy compliance.

#### Architecture

##### 1. Architecture Components

- Client: `BillingClient` v6, `PurchasesUpdatedListener`, `BillingClientStateListener`.
- Server: services using Play Developer API v3 and Pub/Sub RTDN handlers.
- Storage: local cache (Room/Proto DataStore) for `ProductDetails` and local subscription/payment state; persistent backend DB as source of truth for entitlements.
- UI: flows built around `BillingFlowParams.ProductDetailsParams` to pick appropriate base plan and offer via `offerToken`.

##### 2. Catalog and Subscriptions

Use `queryProductDetailsAsync` to fetch products and cache them:

```kotlin
val params = QueryProductDetailsParams.newBuilder()
    .setProductList(
        listOf(
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId("premium_monthly")
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
        )
    ).build()

billingClient.queryProductDetailsAsync(params) { billingResult, detailsList ->
    // cache detailsList (ProductDetails with base plans and offers)
}
```

- Use base plans and subscription offers with pricing phases (free trial, intro, recurring).
- Read `subscriptionOfferDetails` and choose `offerToken` according to business rules (region, promos, eligibility).

##### 3. Purchase Flow

```kotlin
val offerToken = product.subscriptionOfferDetails!!
    .first()
    .offerToken

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

- Enable pending purchases with `enablePendingPurchases()` and clearly inform the user when a purchase is pending.
- For multi-quantity purchases (INAPP only in v6), use `setQuantity(quantity)` on `ProductDetailsParams`.
- `setIsOfferPersonalized` is only for marking personalized offers, not quantity.

##### 4. Purchase Handling

```kotlin
override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
    if (result.responseCode != BillingClient.BillingResponseCode.OK || purchases == null) {
        // Handle error / user cancellation, log for troubleshooting
        return
    }

    purchases.forEach { purchase ->
        when (purchase.purchaseState) {
            Purchase.PurchaseState.PURCHASED -> {
                // Send to backend for validation and acknowledgment/consumption
                verifyAndAcknowledge(purchase)
            }
            Purchase.PurchaseState.PENDING -> {
                // Inform the user that the purchase is pending approval
            }
            Purchase.PurchaseState.UNSPECIFIED_STATE -> {
                // Log or safely ignore
            }
        }
    }
}
```

- After successful server-side validation, always call `acknowledgePurchase`; otherwise Play will auto-refund after a short period.
- For consumables, call `consumeAsync` after server validation.

##### 5. Server-side Validation

- Use Play Developer API: `purchases.subscriptionsv2.get` for subscriptions and `purchases.products.get` for one-time products.
- Subscribe to RTDN via Pub/Sub and handle event types: renewals, expirations, revocations, pauses, resumes, etc.; update entitlements and transaction history accordingly.
- Store `purchaseToken` and optionally `obfuscatedAccountId` / `obfuscatedProfileId` to map Play purchases to your internal user accounts.

##### 6. Edge Cases

- On `SERVICE_DISCONNECTED` and similar errors, re-establish the `BillingClient` connection (`startConnection`) and retry catalog/purchase queries with appropriate backoff.
- For pending purchases, periodically or on app start call `queryPurchasesAsync` and grant entitlements only after state becomes `PURCHASED` and the backend confirms.
- For promo codes and special subscription offers, ensure you pass the correct `offerToken` that matches the configured base plan/offer.

##### 7. Compliance

- Show clear pricing and subscription terms: billing period, free trial/intro price, renewal details, and cancellation/management instructions (including link to Play subscription center).
- Maintain server-side transaction history to correctly handle refunds, expirations, and plan changes.
- Protect personal data and IDs (including obfuscated IDs) with encryption in transit and at rest, collect only what is needed, and align with GDPR/CCPA requirements.

---

## Follow-ups (RU)
- Как синхронизировать Play Billing с бэкендом, если пользователи меняют подписку вне приложения?
- Какие best practices по кэшированию каталога и офферов?
- Как работать с многопользовательскими устройствами (Kids/Family accounts)?

## Follow-ups (EN)
- How do you sync Play Billing with the backend when users change subscriptions outside the app?
- What are best practices for caching the catalog and subscription offers?
- How do you handle multi-user devices (Kids/Family accounts) with separate entitlements?

## References
- [[c-play-billing]]
- https://developer.android.com/google/play/billing/integrate
- https://developer.android.com/google/play/billing/migrate-gpblv6

## Related Questions

- [[c-play-billing]]
