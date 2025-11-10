---
id: android-490
title: Design Mobile Banking Auth & Transaction Signing
aliases:
- Design Mobile Banking Auth & Transaction Signing
- Проектирование аутентификации и подписания транзакций
topic: android
subtopics:
- keystore-crypto
- networking-http
- permissions
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related: [c-android-keystore]
sources: []
created: 2025-10-29
updated: 2025-11-10
tags:
- difficulty/hard
- android/keystore-crypto
- android/networking-http
- android/permissions
- topic/android

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

Банковская аутентификация требует passkeys, биометрии, device attestation и корректно спроектированного secure transaction signing.

### Архитектура

Модули: auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics.

### Credentials

Passkeys через FIDO2/WebAuthn API; fallback на username+OTP (rate‑limited). Аутентификационные ключи и ключи подписания хранятся в Android Keystore (StrongBox где возможно), помечены как non-exportable и защищены biometric / user verification gating. Биометрия используется для разблокировки ключа и подтверждения пользователя, а не как самостоятельный секрет.

### Attestation

Сигналы Play Integrity и аналогичные механизмы интегритета устройства; привязка сессии и доверенных ключей к "device posture"; деградация возможностей на устройствах с низкой целостностью (например, блокировка высокорисковых операций).

### Session

`Short`‑lived access token + refresh; ротация на risk events; для 3DS flows в WebView — secure cookies и изоляция origin; CSRF tokens для веб‑контента при наличии встроенных веб‑флоу.

### Transaction Signing

- Для чувствительных операций формировать канонический payload (идентификатор получателя, сумма, валюта, время, nonce/челлендж, срок действия, идентификатор устройства/ключа).
- Подписывать payload приватным ключом, хранящимся в Android Keystore, привязанным к устройству и аккаунту, с включенной user authentication (например, биометрия) перед подписанием.
- Сервер хранит соответствующий публичный ключ (или его сертификат), проверяет подпись, валидирует nonce/челлендж и сроки, сопоставляет поля payload c фактической транзакцией для защиты от подмены и replay.
- Пользователю показывать out‑of‑band push approval с детальным, человекочитаемым контекстом (получатель, сумма, валюта, комиссия), чтобы уменьшить риск подтверждения поддельных MFA‑запросов.

### Notifications

FCM data messages → открытие защищенного in‑app экрана; в push‑уведомлениях избегать чувствительных данных (сумма, полный номер счета и т.п.). Deep link с одноразовым nonce и истечением срока действия, сервер обязан валидировать nonce и контекст операции до выполнения.

### Storage

Зашифрованная БД для session metadata и ключевых атрибутов безопасности; избегать хранения полного PII и секретов (пароли, полные PAN). Защита от утечек через clipboard (не копировать коды или чувствительные данные автоматически).

### Наблюдаемость

Отслеживать: login p95, процент успешных approvals, false reject/accept, долю операций, отклоненных по сигналам целостности устройства, crash/ANR. Логирование должно исключать чувствительные данные.

### Тестирование

Покрыть сценарии: смена устройства и привязка ключей, clock skew, попытки MITM (TLS pinning + корректная обработка ошибок), biometric lockouts и fallback‑флоу, SIM‑swap сценарии (противодействие чрезмерной доверенности к SMS), защита от replay подписанных payload (одноразовые nonce), корректная работа 3DS‑флоу, поведение ограниченного офлайн‑режима и ротация ключей/токенов.

### Tradeoffs

Агрессивные pinning/attestation и строгие политики могут блокировать часть легитимных пользователей; важно предоставить верифицированный appeals flow, безопасную деградацию (например, переход к более ограниченным лимитам или дополнительной оффлайн‑верификации), сохраняя высокий уровень защиты.

## Answer (EN)

Banking authentication requires passkeys, biometrics, device attestation, and a correctly designed secure transaction signing scheme.

### Architecture

auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics.

### Credentials

Passkeys via FIDO2/WebAuthn APIs; fallback to username+OTP (rate‑limited). Authentication keys and signing keys are stored in Android Keystore (StrongBox where possible), marked non-exportable and protected via biometric / user verification gating. Biometrics are used to unlock the key / verify the user, not as a standalone secret.

### Attestation

Use Play Integrity and similar device integrity signals; bind sessions and trusted keys to device posture; degrade capabilities on low‑integrity devices (e.g., block high‑risk operations).

### Session

`Short`‑lived access token + refresh; rotate on risk events; for 3DS flows in WebView use secure cookies and proper origin isolation; CSRF tokens for embedded web content where applicable.

### Transaction Signing

- For sensitive operations, build a canonical payload (beneficiary identifier, amount, currency, timestamp, nonce/challenge, expiration, device/key identifier).
- Sign the payload with a private key stored in Android Keystore, device- and account-bound, with user authentication (e.g., biometric) required before signing.
- The server maintains the corresponding public key (or certificate), verifies the signature, validates nonce/challenge and expiry, and checks that payload fields match the intended transaction to prevent tampering and replay.
- Show an out‑of‑band push approval screen with clear, human-readable context (recipient, amount, currency, fees) to reduce the risk of users approving fraudulent MFA prompts.

### Notifications

Use FCM data messages to open a secure in‑app screen; avoid sensitive data (amounts, full account numbers, etc.) in the notification body. Deep links must carry a one‑time nonce with expiration; the server must validate the nonce and operation context before executing.

### Storage

Use an encrypted DB for session metadata and security-critical attributes; avoid storing full PII and secrets (passwords, full PAN). Protect against clipboard leaks (do not auto-copy codes or sensitive data).

### Observability

Track: login p95, approval success%, false reject/accept rates, share of operations rejected by device integrity policies, crash/ANR. Ensure logs exclude sensitive data.

### Testing

Cover: device changes and key binding, clock skew, MITM attempts (TLS pinning + robust failure handling), biometric lockouts and fallback flows, SIM‑swap scenarios (avoid over-reliance on SMS), replay protection for signed payloads (one-time nonce), correct 3DS integration, offline-limited mode behavior, and key/token rotation flows.

### Tradeoffs

Aggressive pinning/attestation and strict policies can block some legitimate users; provide a verified appeals flow and safe degradation paths (e.g., reduced limits or additional offline verification) while maintaining strong protection.

---

## Дополнительные вопросы (RU)

- Как обрабатывать отказы биометрии и fallback-флоу?
- Какая стратегия помогает против SIM-swap атак?
- Как сбалансировать безопасность и UX в аутентификации?
- Как реализовать безопасное управление мульти-девайсными сессиями?

## Follow-ups

- How to handle biometric failures and fallback flows?
- What strategy prevents SIM-swap attacks?
- How to balance security with user experience in authentication?
- How to implement secure multi-device session management?

## Ссылки (RU)

- [[q-database-encryption-android--android--medium]]
- [[c-android-keystore]]
- [Android Keystore](https://developer.android.com/training/articles/keystore)

## References

- [[q-database-encryption-android--android--medium]]
- [[c-android-keystore]]
- [Android Keystore](https://developer.android.com/training/articles/keystore)

## Связанные вопросы (RU)

### Предпосылки (проще)

- [[q-database-encryption-android--android--medium]]

### Связанные (тот же уровень)

- [[q-feature-flags-sdk--android--hard]]

### Продвинутые (сложнее)

- Спроектировать систему детектирования мошенничества в финансовом масштабе

## Related Questions

### Prerequisites (Easier)

- [[q-database-encryption-android--android--medium]]

### Related (Same Level)

- [[q-feature-flags-sdk--android--hard]]

### Advanced (Harder)

- Design a fraud detection system at financial scale
