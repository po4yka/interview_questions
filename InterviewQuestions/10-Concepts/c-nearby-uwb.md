---
id: ivc-20251102-007
title: Nearby, NFC & UWB / Nearby, NFC & UWB
aliases: [Nearby API, NFC on Android, Ultra Wideband Android]
kind: concept
summary: Short-range communication APIs on Android including NFC, Nearby Connections, and Ultra Wideband
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [android, concept, connectivity, nfc, uwb]
---

# Summary (EN)

Android supports several close-range communication stacks: **NFC** (tag reading, HCE, payments), **Nearby Connections** (BLE/Wi-Fi/LTE direct handshakes), and **Ultra Wideband (UWB)** for centimeter-level ranging. Each API targets different latency, bandwidth, and security constraints.

# Сводка (RU)

Android предоставляет несколько стеков ближней связи: **NFC** (чтение меток, HCE, платежи), **Nearby Connections** (BLE/Wi-Fi/LTE Direct), и **Ultra Wideband (UWB)** с точным определением расстояния. Каждый API рассчитан на разные задержки, пропускную способность и требования к безопасности.

## Highlights

- **NFC**: `NfcAdapter`, `ReaderMode`, `HostApduService`, secure element.
- **Nearby**: `ConnectionsClient`, `AdvertisingOptions`, `Payload`.
- **UWB**: `UwbManager`, `RangingSession`, `PersistableBundle` parameters, requires hardware + permissions.

## Considerations

- UWB разрешён только партнёрам (`uwb_RANGING` privileged permission).
- NFC Background tag reading ограничено (foreground dispatch).
- Nearby API требует runtime разрешений (Bluetooth, Location) и управляет peer discovery.

