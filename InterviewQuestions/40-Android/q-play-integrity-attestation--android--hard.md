---\
id: android-619
title: Play Integrity Attestation / Аттестация Play Integrity
aliases: [Play Integrity Attestation, Аттестация Play Integrity]
topic: android
subtopics: [billing, keystore-crypto, play-console]
question_kind: theory
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-keystore, q-android-security-best-practices--android--medium, q-play-billing-v6-architecture--android--hard, q-play-feature-delivery--android--medium, q-play-store-publishing--android--medium]
created: 2024-11-02
updated: 2025-11-10
tags: [android/billing, android/keystore-crypto, android/play-console, difficulty/hard]
sources:
  - "https://cloud.google.com/play-integrity/reference/rest"
  - "https://developer.android.com/google/play/integrity"
anki_cards:
  - slug: android-619-0-en
    front: "How do you implement Play Integrity API for app attestation?"
    back: |
      **Client-side:**
      ```kotlin
      val token = IntegrityManagerFactory.create(context)
          .requestIntegrityToken(
              IntegrityTokenRequest.builder()
                  .setNonce(generateNonce())
                  .build()
          ).await().token()
      ```

      **Server-side verification:**
      - Decode via Play Integrity API (service account)
      - Verify: `requestPackageName`, `nonce`, `timestampMillis`
      - Check verdicts: `deviceRecognitionVerdict`, `appLicensingVerdict`

      **Key points:**
      - Nonce must be unique per request (replay protection)
      - Never store keys on client
      - Use capability tokens for offline scenarios
    tags:
      - android_general
      - difficulty::hard
  - slug: android-619-0-ru
    front: "Как реализовать Play Integrity API для аттестации приложения?"
    back: |
      **На клиенте:**
      ```kotlin
      val token = IntegrityManagerFactory.create(context)
          .requestIntegrityToken(
              IntegrityTokenRequest.builder()
                  .setNonce(generateNonce())
                  .build()
          ).await().token()
      ```

      **Проверка на сервере:**
      - Декодирование через Play Integrity API (service account)
      - Проверка: `requestPackageName`, `nonce`, `timestampMillis`
      - Анализ вердиктов: `deviceRecognitionVerdict`, `appLicensingVerdict`

      **Ключевые моменты:**
      - Nonce уникален для каждого запроса (защита от replay)
      - Никогда не храните ключи на клиенте
      - Используйте capability tokens для оффлайн-сценариев
    tags:
      - android_general
      - difficulty::hard

---\
# Вопрос (RU)
> Как реализовать Play Integrity: запрос токена на клиенте, проверка вердикта на сервере, использование capability tokens и связь с Play Billing?

# Question (EN)
> How do you implement Play Integrity, from client token requests to server verification, leveraging capability tokens and integrating with Play Billing workflows?

---

## Ответ (RU)

### Краткий Вариант

- Используйте Play Integrity API только через доверенный backend.
- На клиенте запрашивайте integrity-токен с `nonce`, связанным с конкретным запросом/покупкой.
- На сервере декодируйте токен через Play Integrity API, проверяйте пакет, nonce, время, вердикты.
- Используйте capability tokens для устойчивости в ограниченных условиях.
- Комбинируйте Play Integrity с server-side Play Billing проверкой и дополнительными сигналами.

### Подробный Вариант

### 1. Требования

- Функциональные:
  - Генерация и проверка токенов целостности для каждой чувствительной операции (логин, покупка, доступ к премиум-контенту).
  - Связка Play Integrity вердикта с конкретным запросом/покупкой (через `nonce`/контекст).
  - Возможность работы в условиях ограниченной доступности Google Play services (через capability tokens).
- Нефункциональные:
  - Безопасное хранение ключей (только на сервере).
  - Масштабируемость backend-проверок при высоком трафике.
  - Низкая задержка проверки и устойчивость к ошибкам API.

### 2. Архитектура

- Клиент (Android): запрашивает integrity-токен с уникальным `nonce`, отправляет токен на backend вместе с контекстом (user/session/purchase).
- Backend-сервис проверки:
  - Получает токен.
  - Через Play Integrity API декодирует `integrityToken`.
  - Проверяет пакет, `nonce`, время, вердикты.
  - Возвращает доверенное решение (allow/deny/flag) другим сервисам.
- Billing/бизнес-логика:
  - Валидирует покупки через Play Billing server-side.
  - Сопоставляет результаты с Play Integrity вердиктами.
- Хранилище/логирование:
  - Логирует результаты проверок, метрики, аномалии для мониторинга и tuning-а политик.

### 3. Настройка В Google Cloud

- Включите Play Integrity API в связанном GCP-проекте.
- Настройте сервисный аккаунт и сохраните JSON-ключ (используется только на сервере).
- В Play Console привяжите приложение к этому GCP-проекту.

### 4. Клиентский Запрос Токена (основной поток)

```kotlin
val integrityManager = IntegrityManagerFactory.create(appContext)

val request = IntegrityTokenRequest.builder()
    .setNonce(generateNonce())
    .build()

val token = integrityManager.requestIntegrityToken(request)
    .await().token()
```

- `nonce` должен быть криптографически случайным, уникальным и связанным с контекстом (userId/sessionId/purchaseId) для защиты от replay.
- Обновите зависимость `com.google.android.play:integrity` до актуальной версии.
- Токен необходимо немедленно отправить на ваш защищённый backend для проверки.

### 5. Серверная Проверка

```python
def verify_token(token: str):
    client = googleapiclient.discovery.build(
        'playintegrity', 'v1', credentials=service_account_creds
    )
    request = {
        "integrityToken": token
    }
    response = client.v1().decodeIntegrityToken(
        packageName=PACKAGE_NAME,
        body=request
    ).execute()

    payload = response["tokenPayloadExternal"]
    # Обязательные проверки примера (детализируйте под свои требования)
    assert payload["requestDetails"]["requestPackageName"] == PACKAGE_NAME
    # Сверка nonce, timestamp и вердиктов выполняется вызывающим кодом
    return payload
```

- Проверяйте:
  - совпадение `requestDetails.requestPackageName` с ожидаемым `PACKAGE_NAME`.
  - совпадение `requestDetails.nonce` с тем, что был сгенерирован сервером/клиентом для этого запроса.
  - актуальность `timestampMillis` (отбросить слишком старые ответы).
  - `accountDetails.appLicensingVerdict`, `deviceIntegrity.deviceRecognitionVerdict` и другие вердикты согласно вашей политике.
- Вызывайте Play Integrity API только с сервера, используя сервисный аккаунт; не храните ключи на клиенте.

### 6. Capability Tokens

- Capability token запрашивается на сервере через Play Integrity API и передаётся клиенту.
- Клиент затем использует capability token при запросе integrity-токена, чтобы выполнять проверку, когда Google Play services/сеть недоступны или ограничены.
- Capability tokens имеют срок действия и ограничения по использованию; обрабатывайте истечение срока и ошибки (не полагайтесь на них как на постоянный оффлайн-режим).

### 7. Интеграция С Play Billing

- Перед подтверждением или разблокировкой контента на сервере сопоставляйте результаты Play Integrity с результатами server-side проверки покупок.
- Связывайте `purchaseToken` и `nonce` (или другой контекст запроса) для уменьшения риска replay-атак.
- Решения по блокировке (например, игнорировать покупки с определёнными `deviceRecognitionVerdict`) формулируйте как внутреннюю политику на основе риска; не опирайтесь на один конкретный флаг как на универсальную рекомендацию.
- Для повышенной защиты используйте комбинацию: Play Integrity + server-side Play Billing verification + дополнительные сигналы (rate limiting, поведение пользователя и др.).

### 8. Политики И Мониторинг

- Настройте метрики: доля запросов/устройств с "подозрительными" вердиктами, доля с ошибками Play Integrity и т.п.
- Не используйте Play Integrity как единственный критерий блокировки доступа: учитывайте возможные ложные срабатывания и проблемы совместимости.
- Регулярно обновляйте библиотеку Play Integrity: новые версии могут добавлять поля и улучшения вердиктов.

---

## Answer (EN)

### Short Version

- Use the Play Integrity API only via a trusted backend.
- On the client, request an integrity token with a `nonce` bound to the specific request/purchase.
- On the server, decode the token via the Play Integrity API and verify package name, nonce, timestamp, and verdicts.
- Use capability tokens for resilience in constrained environments.
- Combine Play Integrity with server-side Play Billing verification and additional signals.

### Detailed Version

### 1. Requirements

- Functional:
  - Generate and validate integrity tokens for each sensitive operation (login, purchase, premium access).
  - Bind the Play Integrity verdict to a specific request/purchase (via `nonce`/context).
  - Support constrained environments using capability tokens.
- Non-functional:
  - Secure key storage (backend only).
  - Scalable backend verification for high load.
  - Low latency and resilience to API errors.

### 2. Architecture

- Client (Android): requests integrity tokens with unique `nonce`, sends the token to backend with context (user/session/purchase).
- Verification backend service:
  - Receives the token.
  - Calls Play Integrity API to decode `integrityToken`.
  - Validates package, `nonce`, timestamp, and verdicts.
  - Returns a trusted decision (allow/deny/flag) to other services.
- Billing/business logic:
  - Performs server-side Play Billing verification.
  - Correlates results with Play Integrity verdicts.
- Storage/logging:
  - Logs checks, metrics, anomalies for monitoring and policy tuning.

### 3. Google Cloud Setup

- Enable the Play Integrity API in the linked GCP project.
- Create and configure a service account; keep the JSON key only on the backend.
- In Play Console, bind your app to this GCP project.

### 4. Client Integrity Token Request (main flow)

```kotlin
val integrityManager = IntegrityManagerFactory.create(appContext)

val request = IntegrityTokenRequest.builder()
    .setNonce(generateNonce())
    .build()

val token = integrityManager.requestIntegrityToken(request)
    .await().token()
```

- Use a cryptographically strong, unique `nonce` bound to request context (userId/sessionId/purchaseId) to prevent replay.
- Keep `com.google.android.play:integrity` up to date.
- Immediately send the received token to your secure backend for verification.

### 5. Server-side Verification

```python
def verify_token(token: str):
    client = googleapiclient.discovery.build(
        'playintegrity', 'v1', credentials=service_account_creds
    )
    request = {
        "integrityToken": token
    }
    response = client.v1().decodeIntegrityToken(
        packageName=PACKAGE_NAME,
        body=request
    ).execute()

    payload = response["tokenPayloadExternal"]
    # Required checks example (extend with your own policies)
    assert payload["requestDetails"]["requestPackageName"] == PACKAGE_NAME
    # Matching nonce, timestamp, and verdicts is done by the caller
    return payload
```

- `Call` the Play Integrity API only from your backend using the service account; never store keys on the client.
- Validate at minimum:
  - `requestDetails.requestPackageName` matches your `PACKAGE_NAME`.
  - `requestDetails.nonce` matches the value generated for this request.
  - `timestampMillis` is fresh (reject stale responses).
  - `accountDetails.appLicensingVerdict`, `deviceIntegrity.deviceRecognitionVerdict`, and other verdicts according to your risk policy.

### 6. Capability Tokens

- `Request` capability tokens on the backend via the Play Integrity API and deliver them to the client.
- The client uses the capability token when requesting integrity tokens in constrained environments (e.g., limited Google Play services / network).
- Respect their validity period and usage limits; handle expiry and errors, and do not treat them as a permanent offline mode.

### 7. Play Billing Integration

- Before confirming or unlocking content, combine Play Integrity verdicts with server-side Play Billing verification.
- Explicitly link `purchaseToken` and `nonce` (or other request context) to reduce replay risk and ensure that the integrity verdict belongs to the same logical purchase/session.
- Define blocking policies internally (e.g., ignore or flag purchases from devices with certain `deviceRecognitionVerdict` values) instead of relying on a single flag.
- For stronger protection, use: Play Integrity + server-side Billing checks + additional signals (rate limiting, behavioral heuristics, etc.).

### 8. Policies and Monitoring

- Track metrics such as the share of requests/devices with suspicious verdicts and the share of Play Integrity errors.
- Do not treat Play Integrity as the sole gatekeeper; account for false positives and compatibility issues.
- Regularly update the Play Integrity library to benefit from new fields and verdict improvements.

---

## Дополнительные Вопросы (RU)
- Какой fallback использовать при недоступности Play Integrity?
- Как масштабировать серверную валидацию (Pub/Sub, Cloud Functions)?
- Какие стратегии для AB-тестов мер безопасности без роста false positive?

## Follow-ups
- What fallback strategies can you use when Play Integrity is unavailable?
- How would you scale server-side verification (e.g., Pub/Sub, Cloud Functions)?
- How to A/B test security measures without significantly increasing false positives?

## Ссылки (RU)
- https://developer.android.com/google/play/integrity
- https://cloud.google.com/play-integrity/reference/rest

## References
- https://developer.android.com/google/play/integrity
- https://cloud.google.com/play-integrity/reference/rest

## Связанные Вопросы (RU)

- [[q-android-security-best-practices--android--medium]]

## Related Questions

- [[q-android-security-best-practices--android--medium]]

## Концепции (RU)
- [[c-android-keystore]]

## Concepts (EN)
- [[c-android-keystore]]