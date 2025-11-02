---
id: android-619
title: Play Integrity Attestation / Аттестация Play Integrity
aliases:
  - Play Integrity Attestation
  - Аттестация Play Integrity
topic: android
subtopics:
  - security
  - integrity
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
  - c-play-integrity
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/security
  - android/integrity
  - attestation
  - difficulty/hard
sources:
  - url: https://developer.android.com/google/play/integrity
    note: Play Integrity documentation
  - url: https://cloud.google.com/play-integrity/reference/rest
    note: REST API reference
---

# Вопрос (RU)
> Как реализовать Play Integrity: запрос токена на клиенте, проверка вердикта на сервере, использование capability tokens и связь с Play Billing?

# Question (EN)
> How do you implement Play Integrity, from client token requests to server verification, leveraging capability tokens and integrating with Play Billing workflows?

---

## Ответ (RU)

### 1. Настройка в Google Cloud

- Включите Play Integrity API в связанный GCP проект.
- Настройте сервисный аккаунт и сохраните JSON ключ.
- В Play Console привяжите приложение к проекту.

### 2. Клиентский запрос токена

```kotlin
val integrityManager = IntegrityManagerFactory.create(appContext)

val request = IntegrityTokenRequest.builder()
    .setNonce(generateNonce())
    .setCloudProjectNumber(CLOUD_PROJECT_NUMBER)
    .build()

val token = integrityManager.requestIntegrityToken(request)
    .await().token()
```

- `nonce` должен быть уникальным (включайте userId/sessionId).
- Используйте `setCloudProjectNumber` для capability tokens.
- Обновите зависимость `com.google.android.play:integrity`.

### 3. Серверная проверка

```python
def verify_token(token: str):
    client = googleapiclient.discovery.build('playintegrity', 'v1', credentials=service_account_creds)
    request = {
        "integrityToken": token
    }
    response = client.v1().decodeIntegrityToken(packageName=PACKAGE_NAME, body=request).execute()
    verdict = response["tokenPayloadExternal"]
    return verdict
```

- Проверяйте `accountDetails.appLicensingVerdict`, `deviceIntegrity.deviceRecognitionVerdict`.
- Сверяйте nonce и timestamp.
- Логируйте `requestDetails.requestPackageName`.

### 4. Capability Tokens

- Позволяют генерацию `IntegrityToken` без сети (до 24 часов).
- Запросите capability token на сервере и отправьте клиенту.
- Клиент использует capability token при запросе integrity токена оффлайн.

### 5. Интеграция с Play Billing

- Перед подтверждением покупки проверяйте integrity, блокируя устройства с `MEETS_BASIC` только (policy decision).
- Связывайте `purchaseToken` и `nonce` для предотвращения replay.
- Для высокой защиты используйте both Play Integrity и server-side Billing verification.

### 6. Политики и мониторинг

- Настройте метрики отказов (% устройств, не прошедших integrity).
- Не используйте Play Integrity как единственный метод блокировки (учитывайте false negatives).
- Обновляйте SDK: новые версии добавляют account verdict improvements.

---

## Answer (EN)

- Enable the API in GCP, bind the app, and request tokens on the client with unique nonces and cloud project number.
- Send the token to your backend, decode it with the Play Integrity REST API, and validate device/account verdicts plus nonce/timestamps.
- Issue capability tokens from your server to support offline scenarios within 24-hour windows.
- Combine integrity verdicts with Play Billing verification to prevent fraud (e.g., reject purchases from devices failing device integrity).
- Track failure rates and keep the SDK up to date; treat verdicts as one signal in a layered defense.

---

## Follow-ups
- Какой fallback использовать при недоступности Play Integrity?
- Как масштабировать серверную валидацию (Pub/Sub, Cloud Functions)?
- Какие стратегии для AB-тестов мер безопасности без роста false positive?

## References
- [[c-play-integrity]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/google/play/integrity
- https://cloud.google.com/play-integrity/reference/rest
