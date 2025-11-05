---
id: android-620
title: Nearby, NFC & UWB Integration / Интеграция Nearby, NFC и UWB
aliases:
  - Nearby NFC UWB Integration
  - Интеграция Nearby, NFC и UWB
topic: android
subtopics:
  - connectivity
  - nfc
  - uwb
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-nearby-uwb
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/nfc
  - android/nearby
  - android/uwb
  - connectivity
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/connectivity/nfc
    note: NFC developer guide
  - url: https://developer.android.com/guide/topics/connectivity/uwb
    note: UWB API overview
  - url: https://developers.google.com/nearby/connections/overview
    note: Nearby Connections docs
---

# Вопрос (RU)
> Как спроектировать гибридную систему ближней связи на Android, комбинируя NFC для первичной инициализации, Nearby Connections для обмена данными и UWB для точного позиционирования? Какие ограничения безопасность и аппаратная совместимость накладывают?

# Question (EN)
> How do you design a hybrid proximity experience on Android that uses NFC for bootstrapping, Nearby Connections for data transfer, and UWB for high-precision ranging, while respecting security and hardware constraints?

---

## Ответ (RU)

### 1. Архитектура потока

1. **NFC tap** — обмен первичным payload (например, session key, peer ID).
2. **Nearby Connections** — создание зашифрованного канала для данных.
3. **UWB ranging** — запуск точного позиционирования/дистанции.

### 2. NFC bootstrapping

```kotlin
nfcAdapter.enableReaderMode(
    activity,
    { tag ->
        val ndef = Ndef.get(tag)
        val payload = ndef.cachedNdefMessage.records.first().payload
        startNearbyHandshake(payload)
    },
    FLAG_READER_NFC_A or FLAG_READER_SKIP_NDEF_CHECK,
    null
)
```

- Для платежей/HCE — `HostApduService`, `IsoDep`.
- Нельзя читать теги в фоне (Android 12+ ограничения).

### 3. Nearby Connections

```kotlin
val options = AdvertisingOptions.Builder().setStrategy(Strategy.P2P_POINT_TO_POINT).build()

connectionsClient.startAdvertising(
    endpointName,
    SERVICE_ID,
    connectionLifecycleCallback,
    options
)
```

- Требуются разрешения Bluetooth + Location.
- Используйте `Payload.Type.BYTES` + `PayloadEncryption`.
- Устанавливайте timeout на discover/advertise (энергобюджет).

### 4. UWB Ranging

```kotlin
val uwbManager = context.getSystemService(UwbManager::class.java)
val session = uwbManager.openRangingSession(parameters, rangingCallback, executor)

session.start(params)
```

- Требуются разрешения `FINE_LOCATION`, `uwb_RANGING` (приложения OEM/партнёры).
- `RangingSessionCallback.onRangingResult` содержит distance/angle.
- Для публичных приложений можно использовать Nearby Finder API (ограниченная доступность).

### 5. Безопасность

- NFC payload должен содержать подпись/nonce; проверяйте на сервере.
- Nearby callbacks дают `ConnectionInfo.isIncomingConnection` — проводите mutual authentication.
- UWB — ограничения по доступу; используйте fallback (BLE RSSI) при отсутствии аппаратной поддержки.

### 6. Аппаратная совместимость

- Проверяйте `PackageManager.hasSystemFeature(PackageManager.FEATURE_UWB)`.
- Для устройств без UWB используйте BLE Angle-of-Arrival (Android 14+).
- Предусмотрите graceful fallback (только NFC + Nearby).

### 7. Тестирование

- NFC: `TagWriter` + эмулятор? используйте реальные устройства/PN532 readers.
- Nearby: інструментальные тесты с Mock `ConnectionsClient`.
- UWB: Pixel 6 Pro/Pixel Fold; записывайте логи (`adb shell dumpsys uwb`).

---

## Answer (EN)

- Bootstrap secure sessions with NFC (tap-to-pair), passing signed payloads to launch Nearby.
- Use Nearby Connections for encrypted bidirectional data; enforce timeouts and retry policies.
- Initiate UWB ranging for precision distance when the hardware and permissions permit; otherwise fall back to BLE RSSI.
- Validate hardware capabilities at runtime and design fallbacks for devices lacking UWB or NFC.
- Log and monitor energy usage; ensure all handshakes meet Play policy for background location/Bluetooth access.

---

## Follow-ups
- Какие UX-паттерны для повторной привязки устройств без повторного NFC-tap?
- Как хранить и ротацировать сессионные ключи между Nearby и UWB?
- Какие стратегии деградации использовать в странах, где UWB отключён регуляторами?

## References
- [[c-nearby-uwb]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/connectivity/nfc
- https://developer.android.com/guide/topics/connectivity/uwb
- https://developers.google.com/nearby/connections/overview

## Related Questions

- [[c-nearby-uwb]]
- [[q-android-coverage-gaps--android--hard]]
