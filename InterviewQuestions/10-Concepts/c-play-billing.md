---
id: ivc-20251102-005
title: Google Play Billing / Платежи Google Play
aliases: [Google Play Billing v6, Play Billing]
kind: concept
summary: Google Play Billing client and server flow for in-app purchases and subscriptions
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [android, billing, concept, monetization]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

**Google Play Billing** handles in-app products, subscriptions, and offers via the Play Store. Version 5/6 introduces billing as a service, multi-line items, new subscription flexibility, and server verification requirements.

**Flow**
1. Query products (`BillingClient.queryProductDetailsAsync`)
2. Launch billing UI (`BillingFlowParams`)
3. Receive `Purchase` via `PurchasesUpdatedListener`
4. Acknowledge or consume purchase
5. Verify using Play Developer API / Real-time developer notifications (RTDN)

# Сводка (RU)

**Google Play Billing** отвечает за внутриигровые покупки, подписки и промо-предложения через Play Store. В версиях 5/6 появились гибкие подписки, улучшенная архитектура и усиленная серверная валидация.

**Процесс**
1. Запрос каталога (`BillingClient.queryProductDetailsAsync`)
2. Запуск Play UI (`BillingFlowParams`)
3. Получение `Purchase` в `PurchasesUpdatedListener`
4. Подтверждение (`acknowledgePurchase`) или расходование (`consumeAsync`)
5. Верификация через Play Developer API / RTDN

## Advanced Topics

- Многоуровневые подписки (base plan, offer, pricing phase)
- Управление отсроченными покупками (pending transactions)
- Server-side API v3 и Billing Library v6 (feature parity, regional compliance)
- Integration с Play Integrity, backend reconciliation

