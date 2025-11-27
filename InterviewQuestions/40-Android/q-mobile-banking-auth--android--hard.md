---
id: android-490
title: Design Mobile Banking Auth & Transaction Signing
aliases: [Design Mobile Banking Auth & Transaction Signing, Проектирование аутентификации и подписания транзакций]
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
tags: [android/keystore-crypto, android/networking-http, android/permissions, difficulty/hard, topic/android]

date created: Saturday, November 1st 2025, 12:46:58 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
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

Банковская аутентификация требует passkeys (на базе FIDO2), биометрии, device attestation и корректно спроектированного secure transaction signing.

### Архитектура

Модули: auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics. Поддержка жизненного цикла ключей и мульти-девайсных привязок (регистрация/отзыв девайсов и ключей).

### Credentials

Passkeys через FIDO2 API на Android (совместимые с WebAuthn на стороне сервера); fallback на username+OTP (строго rate‑limited, SMS не используется как единственный фактор для высокорисковых операций). Аутентификационные ключи и ключи подписания хранятся в Android Keystore (StrongBox где доступен), помечены как non-exportable и защищены user verification gating (биометрия / экранный PIN). Биометрия используется для разблокировки ключа и подтверждения пользователя, а не как самостоятельный секрет.

### Attestation

Сигналы Play Integrity и аналогичные механизмы интегритета устройства; привязка сессии и доверенных ключей к "device posture"; деградация возможностей на устройствах с низкой целостностью (например, блокировка высокорисковых операций, ограничения лимитов).

### Session

`Short`‑lived access token + refresh; ротация на risk events. Для 3DS flows использовать безопасную загрузку страниц эмитента/банка (через безопасный браузер/Custom Tab либо изолированный WebView с корректной привязкой origin и редиректов); для встроенных веб-флоу — secure cookies, строгое управление origin и CSRF tokens.

### Transaction Signing

- Для чувствительных операций формировать канонический payload (идентификатор получателя, сумма, валюта, время, nonce/челлендж, срок действия, идентификатор устройства/ключа).
- Подписывать payload приватным ключом, хранящимся в Android Keystore, привязанным к устройству и аккаунту, с включённой user authentication (например, биометрия) перед подписанием.
- Сервер хранит соответствующий публичный ключ (или его сертификат), проверяет подпись, валидирует nonce/челлендж и сроки, сопоставляет поля payload с фактической транзакцией для защиты от подмены и replay. При отзыве устройства/ключа сервер прекращает доверять соответствующим подписям.
- Пользователю показывать out‑of‑band push approval с детальным, человекочитаемым контекстом (получатель, сумма, валюта, комиссия), чтобы уменьшить риск подтверждения поддельных MFA‑запросов.

### Notifications

FCM data messages → открытие защищенного in‑app экрана; в push‑уведомлениях избегать чувствительных данных (сумма, полный номер счета и т.п.). Deep link с одноразовым nonce и истечением срока действия, сервер обязан валидировать nonce и контекст операции до выполнения.

### Storage

Зашифрованная БД для session metadata и ключевых атрибутов безопасности; избегать хранения полного PII и секретов (пароли, полные PAN). Защита от утечек через clipboard (не копировать коды или чувствительные данные автоматически).

### Наблюдаемость

Отслеживать: login p95, процент успешных approvals, false reject/accept, долю операций, отклонённых по сигналам целостности устройства, crash/ANR, аномальные паттерны аутентификации и подписания. Логирование должно исключать чувствительные данные.

### Тестирование

Покрыть сценарии: смена устройства и привязка/отзыв ключей и девайсов, clock skew, попытки MITM (TLS pinning + корректная обработка ошибок), biometric lockouts и fallback‑флоу, SIM‑swap сценарии (SMS OTP не использовать как единственный или основной фактор для критичных операций), защита от replay подписанных payload (одноразовые nonce/челленджи), корректная работа 3DS‑флоу (включая редиректы и origin), поведение ограниченного офлайн‑режима (ограниченные лимиты/операции без онлайновой валидации), ротация ключей/токенов.

### Tradeoffs

Агрессивные pinning/attestation и строгие политики могут блокировать часть легитимных пользователей; важно предоставить верифицированный appeals flow, безопасную деградацию (например, переход к более ограниченным лимитам или дополнительной оффлайн‑верификации), сохраняя высокий уровень защиты.

## Answer (EN)

Banking authentication requires passkeys (FIDO2-based), biometrics, device attestation, and a correctly designed secure transaction signing scheme.

### Architecture

auth-core, crypto (Keystore), session, approvals, notifications, flags, analytics. Include key lifecycle and multi-device support (device/key registration and revocation).

### Credentials

Passkeys via Android FIDO2 APIs (compatible with WebAuthn on the server side); fallback to username+OTP (strictly rate‑limited, SMS OTP not used as the sole factor for high-risk operations). Authentication keys and signing keys are stored in Android Keystore (StrongBox where available), marked non-exportable and protected via user verification gating (biometrics / screen lock). Biometrics are used to unlock the key / verify the user, not as a standalone secret.

### Attestation

Use Play Integrity and similar device integrity signals; bind sessions and trusted keys to device posture; degrade capabilities on low‑integrity devices (e.g., block high‑risk operations, enforce lower limits).

### Session

Short‑lived access token + refresh; rotate on risk events. For 3DS flows, load issuer/acquirer pages securely (prefer Custom Tabs or a well-isolated WebView with proper origin binding and redirect handling); for embedded web content use secure cookies, strict origin management, and CSRF tokens.

### Transaction Signing

- For sensitive operations, build a canonical payload (beneficiary identifier, amount, currency, timestamp, nonce/challenge, expiration, device/key identifier).
- Sign the payload with a private key stored in Android Keystore, device- and account-bound, with user authentication (e.g., biometric) required before signing.
- The server maintains the corresponding public key (or certificate), verifies the signature, validates nonce/challenge and expiry, and checks that payload fields match the intended transaction to prevent tampering and replay. On device/key revocation, the server must stop trusting signatures from that key.
- Show an out‑of‑band push approval screen with clear, human-readable context (recipient, amount, currency, fees) to reduce the risk of users approving fraudulent MFA prompts.

### Notifications

Use FCM data messages to open a secure in‑app screen; avoid sensitive data (amounts, full account numbers, etc.) in the notification body. Deep links must carry a one‑time nonce with expiration; the server must validate the nonce and operation context before executing.

### Storage

Use an encrypted DB for session metadata and security-critical attributes; avoid storing full PII and secrets (passwords, full PAN). Protect against clipboard leaks (do not auto-copy codes or sensitive data).

### Observability

Track: login p95, approval success%, false reject/accept rates, share of operations rejected by device integrity policies, crash/ANR, and anomalous auth/signing patterns. Ensure logs exclude sensitive data.

### Testing

Cover: device changes and device/key binding & revocation, clock skew, MITM attempts (TLS pinning + robust failure handling), biometric lockouts and fallback flows, SIM‑swap scenarios (do not treat SMS OTP as the only or primary factor for critical actions), replay protection for signed payloads (one-time nonces/challenges), correct 3DS integration (including redirects and origin handling), offline-limited mode behavior (restricted limits/operations without online validation), and key/token rotation flows.

### Tradeoffs

Aggressive pinning/attestation and strict policies can block some legitimate users; provide a verified appeals flow and safe degradation paths (e.g., reduced limits or additional offline verification) while maintaining strong protection.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать отказы биометрии и fallback-флоу?
- Какая стратегия помогает против SIM-swap атак (почему SMS не должно быть единственным сильным фактором)?
- Как сбалансировать безопасность и UX в аутентификации?
- Как реализовать безопасное управление мульти-девайсными сессиями?

## Follow-ups

- How to handle biometric failures and fallback flows?
- What strategy prevents SIM-swap attacks (why SMS must not be the only strong factor)?
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

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[q-database-encryption-android--android--medium]]

### Связанные (тот Же уровень)

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
