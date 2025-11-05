---
id: android-490
title: Design Mobile Banking Auth & Transaction Signing / Проектирование аутентификации и подписания транзакций
aliases: []
topic: android
subtopics: [keystore-crypto, networking-http, permissions]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
sources: []
created: 2025-10-29
updated: 2025-10-29
tags: []
date created: Wednesday, October 29th 2025, 5:03:40 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)

> Как спроектировать безопасный вход и подписание транзакций для банковского приложения?

# Question (EN)

> How to design secure sign‑in and transaction signing for a banking app?

---

### Upgraded Interview Prompt (RU)

Спроектируйте безопасный sign‑in и подписание транзакций для банковского приложения. Используйте passkeys/biometric, поддержку 3DS challenges, device attestation, управление сессиями, офлайн‑ограниченный режим. Цели: логин <800мс (p95) post‑bootstrap, fraud‑resistant flows, приватность. Включите управление ключами, secure storage, push‑based approvals, уведомления, наблюдаемость, rollback/kill‑switch.

### Upgraded Interview Prompt (EN)

Design secure sign‑in and transaction signing for a banking app. Use passkeys/biometric, support 3DS challenges, device attestation, session management, and offline‑limited mode. Targets: login <800ms (p95) post‑bootstrap, fraud‑resistant flows, and privacy. Include key management, secure storage, push‑based approvals, notifications, observability, and rollback/kill‑switch.

## Ответ (RU)

Банковская аутентификация требует passkeys, биометрии, device attestation и secure transaction signing.

### Архитектура

Модули: auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics.

### Credentials

Passkeys через FIDO2/CTAP; fallback на username+OTP (rate‑limited). Ключи в Android Keystore (StrongBox где возможно) с biometric gating.

### Attestation

Play Integrity/DeviceCheck signals; bind session к device posture; деградация capabilities на low‑integrity.

### Session

Short‑lived access token + refresh; rotate на risk events; secure cookies в WebView для 3DS flows; CSRF tokens.

### Transaction Signing

Построить canonical payload → sign с app private key (Keystore) → server верифицирует против public key; display out‑of‑band push approval с детальным контекстом для защиты от replay MFA prompts.

### Notifications

FCM data → secure in‑app screen (нет чувствительного текста в notification). Deep link с one‑time nonce.

### Storage

Encrypted DB для session metadata; избегать хранения полного PII. Clipboard protections.

### Наблюдаемость

Login p95, approval success%, false reject/accept, rooted/jailbroken detection rate, crash/ANR.

### Тестирование

Device change, clock skew, network MITM (ожидать TLS pinning), biometric lockouts, SIM‑swap scenarios.

### Tradeoffs

Агрессивные pinning/attestation блокируют некоторых легитимных пользователей; предоставить appeals flow и safe degradation.

## Answer (EN)

Banking authentication requires passkeys, biometrics, device attestation, and secure transaction signing.

### Architecture

auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics.

### Credentials

Passkeys via FIDO2/CTAP; fallback to username+OTP (rate‑limited). Keys in Android Keystore (StrongBox where possible) with biometric gating.

### Attestation

Play Integrity/DeviceCheck signals; bind session to device posture; degrade capabilities on low‑integrity.

### Session

Short‑lived access token + refresh; rotate on risk events; secure cookies in WebView for 3DS flows; CSRF tokens.

### Transaction Signing

Build canonical payload → sign with app private key (Keystore) → server verifies against public key; display out‑of‑band push approval with detailed context to fight MFA prompts replay.

### Notifications

FCM data → secure in‑app screen (no sensitive text in notification). Deep link with one‑time nonce.

### Storage

Encrypted DB for session metadata; avoid storing full PII. Clipboard protections.

### Observability

Login p95, approval success%, false reject/accept, rooted/jailbroken detection rate, crash/ANR.

### Testing

Device change, clock skew, network MITM (expect TLS pinning), biometric lockouts, SIM‑swap scenarios.

### Tradeoffs

Aggressive pinning/attestation blocks some legit users; provide appeals flow and safe degradation.

---

## Follow-ups

-   How to handle biometric failures and fallback flows?
-   What strategy prevents SIM-swap attacks?
-   How to balance security with user experience in authentication?
-   How to implement secure multi-device session management?

## References

-   [[q-database-encryption-android--android--medium]]
-   [[c-encryption]]
-   [[c-permissions]]
- [Android Keystore](https://developer.android.com/training/articles/keystore)
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]


## Related Questions

### Prerequisites (Easier)

-   [[q-database-encryption-android--android--medium]]

### Related (Same Level)

-   [[q-feature-flags-sdk--android--hard]]

### Advanced (Harder)

-   Design a fraud detection system at financial scale
