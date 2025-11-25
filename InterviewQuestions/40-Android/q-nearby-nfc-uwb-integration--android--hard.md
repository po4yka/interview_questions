---
id: android-620
title: Nearby, NFC & UWB Integration / Интеграция Nearby, NFC и UWB
aliases: [Nearby NFC UWB Integration, NFC и UWB, Интеграция Nearby]
topic: android
subtopics:
  - networking-http
  - nfc
  - sensors
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - c-android-ipc
  - q-android-auto-guidelines--android--hard
  - q-integration-testing-strategies--android--medium
  - q-room-paging3-integration--android--medium
  - q-wearos-health-connect-integration--android--hard
created: 2025-11-02
updated: 2025-11-11
tags: [android/networking-http, android/nfc, android/sensors, difficulty/hard]
sources:
- url: "https://developer.android.com/guide/topics/connectivity/nfc"
  note: NFC developer guide
- url: "https://developer.android.com/guide/topics/connectivity/uwb"
  note: UWB API overview
- url: "https://developers.google.com/nearby/connections/overview"
  note: Nearby Connections docs

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)
> Как спроектировать гибридную систему ближней связи на Android, комбинируя NFC для первичной инициализации, Nearby Connections для обмена данными и UWB для точного позиционирования? Какие ограничения безопасность и аппаратная совместимость накладывают?

# Question (EN)
> How do you design a hybrid proximity experience on Android that uses NFC for bootstrapping, Nearby Connections for data transfer, and UWB for high-precision ranging, while respecting security and hardware constraints?

---

## Ответ (RU)

## Краткая Версия
- NFC: одноразовый tap для безопасного обмена параметрами сессии.
- Nearby Connections: основной зашифрованный канал данных.
- UWB: высокоточное измерение расстояния/угла при наличии поддержки, с fallback на BLE/Nearby.
- Строгая проверка аппаратных возможностей, разрешений и ограниченного доступа к UWB.
- Связка всех каналов через криптографически защищённую сессию.

## Подробная Версия

### Требования

- Функциональные:
  - Инициализация связи через NFC одним касанием.
  - Автоматическое установление надёжного канала передачи данных (Nearby).
  - Высокоточное позиционирование через UWB при наличии поддержки.
  - Поддержка fallback-сценариев: отсутствие NFC или UWB.
- Нефункциональные:
  - Безопасность (подпись, шифрование, защита от replay/mitm).
  - Энергоэффективность (ограничение времени discover/advertise, разумные payload).
  - Надёжность в условиях помех и различного железа.
  - Соответствие требованиям разрешений и приватности.

### Архитектура

#### 1. Архитектура Потока

1. NFC tap — обмен первичным payload (например, session key, peer ID, nonce, идентификатор сервиса).
2. Nearby Connections — создание зашифрованного канала для данных (TLS/Noise/доп. шифрование поверх встроенной защиты Nearby).
3. UWB ranging — запуск точного позиционирования/дистанции при наличии поддержки.

#### 2. NFC Bootstrapping

```kotlin
nfcAdapter.enableReaderMode(
    activity,
    { tag ->
        val ndef = Ndef.get(tag)
        val message = ndef?.cachedNdefMessage
        val record = message?.records?.firstOrNull()
        val payload = record?.payload ?: return@enableReaderMode
        startNearbyHandshake(payload)
    },
    NfcAdapter.FLAG_READER_NFC_A or NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK,
    null
)
```

- Для платежей/HCE используются `HostApduService`, `IsoDep` и протоколы уровня ISO-7816.
- Чтение тегов требует активности приложения на переднем плане (foreground dispatch/reader mode); полное прозрачное чтение в фоне для обычных приложений недоступно.

#### 3. Nearby Connections

```kotlin
val options = AdvertisingOptions.Builder()
    .setStrategy(Strategy.P2P_POINT_TO_POINT)
    .build()

connectionsClient.startAdvertising(
    endpointName,
    SERVICE_ID,
    connectionLifecycleCallback,
    options
)
```

- Требуются разрешения на Bluetooth и геолокацию (ACCESS_FINE_LOCATION/NEARBY_DEVICES в зависимости от версии).
- Соединения Nearby Connections уже шифруются; при повышенных требованиях добавляйте своё приложение-уровневое шифрование поверх `Payload.Type.BYTES`.
- Устанавливайте timeout на discover/advertise и ограничивайте размер/частоту payload.

#### 4. UWB Ranging

```kotlin
val uwbManager = context.getSystemService(UwbManager::class.java)
val session = uwbManager.openRangingSession(parameters, rangingCallback, executor)

session.start(params)
```

- На поддерживаемых устройствах требуется разрешение `android.permission.UWB_RANGING`, обычно доступное только системным/OEM/партнёрским приложениям.
- `RangingSessionCallback.onRangingResult` предоставляет distance/angle/quality; используйте фильтрацию и сглаживание.
- Если прямой UWB API недоступен, стройте UX с graceful fallback (BLE RSSI/Angle-of-Arrival, только Nearby и NFC).

#### 5. Безопасность

- NFC payload должен содержать подпись, nonce и идентификатор контекста.
- На уровне Nearby выполняйте взаимную аутентификацию, не полагайтесь только на имя endpoint.
- UWB доступ ограничен; минимизируйте данные и привязывайте измерения к сессии.

#### 6. Аппаратная Совместимость

- Проверяйте `PackageManager.hasSystemFeature(PackageManager.FEATURE_NFC)` и `PackageManager.hasSystemFeature(PackageManager.FEATURE_UWB)`.
- Для устройств без UWB используйте BLE как более грубую оценку расстояния.
- Реализуйте graceful degradation: только NFC, NFC + Nearby без UWB или только Nearby.

#### 7. Тестирование

- NFC: тестирование на реальных устройствах и реальных тегах.
- Nearby: инструментальные тесты с mock/stub `ConnectionsClient`.
- UWB: реальные устройства с поддержкой, анализ логов и проверка fallback-путей.

---

## Answer (EN)

## Short Version
- Use NFC for a single tap to bootstrap a secure session.
- Use Nearby Connections as the main encrypted data channel.
- Use UWB for precise ranging when available, with BLE/Nearby fallbacks.
- Enforce strict capability checks, permissions, and limited UWB access.
- Cryptographically bind all channels into one authenticated session.

## Detailed Version

### Requirements

- Functional:
  - Initialize communication via single NFC tap.
  - Automatically establish a reliable data channel via Nearby.
  - Use UWB for high-precision ranging when supported.
  - Support fallbacks when NFC or UWB are unavailable.
- Non-functional:
  - Strong security (signatures, encryption, replay/MITM protection).
  - Battery efficiency (bounded discovery/advertising, sensible payload sizes).
  - Robustness across devices and radio environments.
  - Compliance with permission/privacy requirements.

### Architecture

#### 1. Flow Architecture

1. Use an NFC tap to exchange an initial payload (e.g., session key material, peer ID, nonce, service identifier).
2. Use Nearby Connections to establish a secure data channel.
3. Start UWB ranging for precise distance/angle when supported; otherwise rely on BLE-based proximity or stay with NFC + Nearby.

#### 2. NFC Bootstrapping

- Use `NfcAdapter.enableReaderMode` (or foreground dispatch) in a foreground `Activity` to read an NDEF record and extract the signed bootstrap payload.
- For payments/HCE flows, use `HostApduService` and `IsoDep` following ISO-7816 instead of generic NDEF.
- Background/transparent NFC tag reads for general apps are not supported; user presence/foreground is expected.

#### 3. Nearby Connections

- Require proper Bluetooth and Location/Nearby Devices permissions depending on Android version.
- Nearby Connections already encrypts traffic; add application-level encryption if you need stronger guarantees.
- Configure strategies, timeouts, and payload sizing to balance reliability, latency, and battery.

#### 4. UWB Ranging

- Use `UwbManager` and ranging sessions on devices that support UWB.
- The `android.permission.UWB_RANGING` permission is typically limited to system/OEM/partner apps.
- Use UWB ranging results only when available and validated; otherwise fall back to BLE RSSI/AoA or Nearby-only flows.

#### 5. Security

- Make NFC bootstrapping payloads signed and bound to a nonce/session ID; verify on server or against a trusted keystore.
- Perform mutual authentication over Nearby; do not rely solely on endpoint names.
- Bind UWB ranging sessions to the authenticated session established via NFC + Nearby.

#### 6. Hardware Compatibility & Fallbacks

- Check `FEATURE_NFC` and `FEATURE_UWB` (and required Bluetooth features) at runtime.
- Provide fallbacks: NFC + Nearby without UWB; Nearby-only when NFC/UWB are missing; BLE-based proximity where UWB is unavailable.

#### 7. Testing

- NFC: test on real devices and tags.
- Nearby: use instrumented tests with mocked/stubbed `ConnectionsClient`.
- UWB: test on UWB-capable devices, inspect logs, and verify fallback paths.

---

## Follow-ups (RU)
- Какие UX-паттерны для повторной привязки устройств без повторного NFC-tap?
- Как хранить и ротировать сессионные ключи между Nearby и UWB?
- Какие стратегии деградации использовать в странах, где UWB отключён регуляторами?

## Follow-ups (EN)
- What UX patterns can you use for re-pairing devices without requiring another NFC tap?
- How should you store and rotate session keys shared between Nearby and UWB?
- What degradation strategies work in regions where UWB is disabled by regulators?

## References (RU)
- [[c-android]]
- https://developer.android.com/guide/topics/connectivity/nfc
- https://developer.android.com/guide/topics/connectivity/uwb
- https://developers.google.com/nearby/connections/overview

## References (EN)
- [[c-android]]
- https://developer.android.com/guide/topics/connectivity/nfc
- https://developer.android.com/guide/topics/connectivity/uwb
- https://developers.google.com/nearby/connections/overview

## Related Questions

- [[q-android-auto-guidelines--android--hard]]