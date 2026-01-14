---
id: android-489
title: Design BLE Wearable Sync / Проектирование синхронизации BLE носимых устройств
aliases:
- Design BLE Wearable Sync
- Проектирование синхронизации BLE носимых устройств
topic: android
subtopics:
- background-execution
- bluetooth
- service
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-lifecycle
- c-permissions
- c-service
- c-workmanager
sources: []
created: 2025-10-29
updated: 2025-10-30
tags:
- android/background-execution
- android/bluetooth
- android/service
- difficulty/hard
- topic/android
anki_cards:
- slug: android-489-0-en
  language: en
  anki_id: 1768364991649
  synced_at: '2026-01-14T09:17:53.656377'
- slug: android-489-0-ru
  language: ru
  anki_id: 1768364991673
  synced_at: '2026-01-14T09:17:53.658519'
---
# Вопрос (RU)

> Спроектируйте Android-компаньон для BLE носимого трекера здоровья. Требования: pairing & bonding, фоновая синхронизация каждые 10 мин, backfill пропущенных данных за 24ч, бюджет батареи <1%/ч во время активной синхронизации, защита приватности. Включите GATT profile, логику переподключения, модель данных, flow разрешений, наблюдаемость.

# Question (EN)

> Design an Android companion app for a BLE wearable health tracker. Requirements: pairing & bonding, background sync every 10 min, missed-data backfill for 24h, battery budget <1%/hr during active sync, and privacy safeguards. Include GATT profile, reconnect logic, data model, permissions flows, and observability.

---

## Ответ (RU)

BLE синхронизация носимых устройств требует архитектуры с разделением ответственности: управление подключением, GATT коммуникация, фоновая синхронизация, персистентное хранилище и обработка reconnects с учетом ограничений Doze/App Standby.

### 1. Архитектура Модулей

**Core modules**:

- **ble-core**: BluetoothGatt wrapper, connection state machine, MTU negotiation
- **device-manager**: pairing/bonding, device discovery, address caching
- **gatt-services**: custom GATT profile, characteristic reads/writes/notifications
- **sync-engine**: orchestration, backfill cursor, deduplication, retry logic
- **store (`Room`)**: local persistence, conflict resolution, cursor tracking
- **analytics**: connection metrics, sync success rates, battery impact
- **feature-flags**: gradual rollout of sync strategies

### 2. Pairing & Bonding

**Security model**: LE Secure Connections (Level 4) с passkey или Just Works в зависимости от capabilities устройства.

```kotlin
// ✅ Persist bond after successful pairing
fun createBond(context: Context, device: BluetoothDevice): Flow<BondState> = callbackFlow {
    val filter = IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val bondedDevice: BluetoothDevice? =
                intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
            if (bondedDevice?.address != device.address) return

            when (intent.getIntExtra(BluetoothDevice.EXTRA_BOND_STATE, BluetoothDevice.ERROR)) {
                BluetoothDevice.BOND_BONDED -> trySend(BondState.Bonded)
                BluetoothDevice.BOND_NONE -> trySend(BondState.None)
            }
        }
    }
    context.registerReceiver(receiver, filter)
    device.createBond() // ✅ Initiate pairing
    awaitClose { context.unregisterReceiver(receiver) }
}

// ❌ WRONG: Ignoring BOND_NONE / device change broadcasts leads to stale state
```

**Обработка revoke**: при `BOND_NONE` очистить cached device address/keys, запросить повторный pairing flow.

### 3. GATT Profile Design

**Пример сервиса** (иллюстративный, не стандартный профиль): использовать собственный vendor-specific UUID вида `0000XXXX-0000-1000-8000-00805F9B34FB`. Обратите внимание, что `0000180D-0000-1000-8000-00805F9B34FB` — это стандартный Heart Rate `Service` UUID Bluetooth SIG и не должен использоваться как «кастомный».

**Characteristics (пример)**:

- **Summary** (read/notify): текущие метрики (шаги, пульс, калории) — компактный payload (≤ MTU - 3 байт)
- **History** (read/notify): bulk transfer для backfill — chunked, полезная нагрузка каждого пакета ограничена `(negotiatedMtu - 3)` байт
- **Control** (write): команды (start sync, set cursor, clear cache)
- **Device Info** (read): firmware version, battery level, capabilities

```kotlin
// ✅ Enable notifications for real-time updates
fun enableNotifications(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic): Boolean {
    if (!gatt.setCharacteristicNotification(characteristic, true)) return false
    val descriptor = characteristic.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG_UUID)
        ?: return false
    descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
    return gatt.writeDescriptor(descriptor) // ✅ Required for notifications to reach app
}

// ✅ MTU negotiation for bulk transfers
fun requestMtu(gatt: BluetoothGatt, size: Int = 512) {
    // Default MTU is 23; Android can negotiate up to 517 with compatible peripherals.
    gatt.requestMtu(size.coerceAtMost(517))
}
```

**Chunking**: для передач больше MTU разбивать на пакеты с sequence numbers и, при необходимости, checksum; собирать на клиенте с таймаутом и валидацией целостности.

### 4. Sync Engine

**Foreground vs Background**:

- **Active sync**: Foreground `Service` с notification (обязательно для Android 8+ при долгих операциях)
- **Periodic sync**: `WorkManager` с `ExistingPeriodicWorkPolicy.KEEP`, constraints на battery/network

```kotlin
// ✅ Foreground service for active sync (user-initiated)
class SyncForegroundService : Service() {
    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        val notification = createSyncNotification() // ✅ Required for FG service
        startForeground(NOTIFICATION_ID, notification)
        // ... sync logic
        return START_STICKY
    }
}

// ✅ WorkManager for background periodic sync
val constraints = Constraints.Builder()
    .setRequiresBatteryNotLow(true) // ✅ Respect battery constraints
    .build()

val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(10, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()
```

**Backfill strategy**: device cursor (последний синхронизированный timestamp), запрашивать данные с cursor до now, дедупликация по `(deviceId, timestamp, sequence)`.

### 5. Reconnect Logic

**Exponential backoff**: при GATT errors (133, 8, 22) повторять с 1s → 2s → 4s → 8s → max 60s.

```kotlin
// ✅ Auto-reconnect with exponential backoff (simplified)
suspend fun connectWithRetry(
    context: Context,
    device: BluetoothDevice,
    maxRetries: Int = 5
) {
    var attempt = 0
    while (attempt < maxRetries) {
        attempt++
        try {
            val gatt = device.connectGatt(context, false, gattCallback)
            if (waitForConnection(gatt, timeoutMillis = 10_000L)) return
        } catch (e: Exception) {
            // fall through to backoff
        }
        val backoffSeconds = min(2.0.pow((attempt - 1).toDouble()).toLong(), 60L)
        kotlinx.coroutines.delay(backoffSeconds * 1000L) // ✅ Exponential backoff
    }
    throw ConnectionFailedException()
}

// ❌ WRONG: Blindly relying on autoConnect=true can cause long hangs and unreliable reconnects
```

**Connection priority**: `CONNECTION_PRIORITY_HIGH` только во время передач, затем вернуть к `BALANCED` для экономии батареи.

### 6. Battery Optimization

**Strategies**:

- Batch reads: группировать characteristic reads в один connection window
- Notifications > polling: prefer GATT notifications для real-time data
- Payload compression: gzip или аналогичная схема для bulk history transfers (если поддерживает устройство)
- Throttle scans: не чаще 1 раз в 10 мин, использовать `ScanSettings.SCAN_MODE_LOW_POWER`
- Doze alignment: `setRequiresDeviceIdle(false)` + flex windows в `WorkManager` для согласования с системными окнами

**Target**: бюджет <1% battery/hr для активной синхронизации. Для батареи 2000mAh это ≈20mAh/час; при 10-минутном sync window ориентировочно ≤3–4mAh, что требует агрессивной оптимизации соединений.

### 7. Data Model & Persistence

**`Room` entities**:

```kotlin
@Entity(
    tableName = "health_samples",
    indices = [Index(value = ["device_id", "timestamp", "sequence"], unique = true)]
)
data class HealthSample(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "device_id") val deviceId: String,
    val timestamp: Long, // Unix millis
    val sequence: Int,   // For deduplication
    val steps: Int,
    val heartRate: Int?,
    val calories: Int
)

@Entity(tableName = "sync_cursors")
data class SyncCursor(
    @PrimaryKey @ColumnInfo(name = "device_id") val deviceId: String,
    val lastSyncTimestamp: Long,
    val lastSyncSequence: Int
)
```

**Conflict resolution**: при дубликатах (same `deviceId` + `timestamp` + `sequence`) использовать `INSERT OR IGNORE` / upsert и, при необходимости, хранить `uploadedAt` для выбора более свежей записи.

### 8. Permissions Flow

**Runtime permissions** (Android 12+):

- `BLUETOOTH_CONNECT` — для подключения к bonded devices
- `BLUETOOTH_SCAN` — для discovery новых устройств
- `BLUETOOTH_ADVERTISE` — если нужен reverse connection
- `ACCESS_FINE_LOCATION` — для BLE scan на устройствах до Android 11 (там, где требуется системой)

**`Request` flow**: показывать rationale UI перед запросом, обрабатывать denial с fallback на manual pairing через Settings и graceful degradation функциональности.

### 9. Privacy & Security

**Safeguards**:

- Encrypt at rest: `Room` database с SQLCipher или EncryptedSharedPreferences для токенов/ключей (не логировать сырые health данные в открытом виде)
- Minimize PII: минимизировать идентификаторы, использовать псевдонимизацию/хеширование device IDs
- User opt-out: позволять отключить cloud sync, поддерживать локальный режим
- Audit logs: логировать только метаданные доступа (кто/когда/операция) без избыточных health деталей, с учетом требований HIPAA/GDPR по минимуму и срокам хранения

### 10. Observability

**Key metrics** (Firebase Analytics / Datadog):

- **Connection success %**: `(successful_connects / total_attempts) * 100`
- **GATT error codes**: distribution of 133, 8, 22, 257 errors
- **Sync duration**: p50, p95, p99 latencies
- **Throughput**: bytes/sec during active sync
- **Battery impact**: оценка mAh или % батареи, потребленных за sync сессии
- **Crash/ANR**: BLE stack crashes, ANRs в GATT callbacks

**Logging**: structured logs с correlation IDs для трассировки одной sync session через все модули, без записи чувствительных payload-данных.

### 11. Edge Cases & Testing

**Scenarios**:

- **RF-noisy environments**: retry с exponential backoff, при необходимости fallback на меньший MTU / lower connection priority
- **Phone sleeps mid-transfer**: partial WakeLock во время active sync, корректное возобновление или повтор синхронизации после wake
- **Device firmware mismatch**: version check в Device Info characteristic, show upgrade prompt
- **Bond loss**: detect via `BOND_NONE` broadcast, trigger re-pairing flow
- **Multiple devices**: queue syncs, ограничивать 1 активное GATT-подключение на устройство одновременно (с учетом ограничений платформы)

**Instrumented tests**: mock BluetoothGatt для unit tests, real device tests для integration, сценарии нестабильного радио и фоновый режим.

### 12. Tradeoffs

| Decision                    | Pros                                | Cons                                     |
| --------------------------- | ----------------------------------- | ---------------------------------------- |
| High connection priority    | Faster sync (2-3x throughput)       | 20-30% higher battery drain              |
| Notifications vs polling    | Real-time updates, less power       | Requires device support, complex flow    |
| Foreground service          | Reliable sync, no background limits | User-visible notification always         |
| Compression                 | 30-50% less data transfer           | CPU overhead, added latency              |
| `WorkManager` flex windows    | Aligns with Doze, battery-friendly  | Delayed syncs (up to 10 min late)        |
| SQLCipher encryption        | Strong at-rest protection           | 10-15% performance penalty on `Room` reads |

**Рекомендация**: включать HIGH priority временно (с explicit timeout ~30s), использовать compression только для bulk history (не для real-time metrics).

---

## Answer (EN)

BLE wearable sync requires an architecture with separated concerns: connection management, GATT communication, background sync, persistent storage, and reconnect handling under Doze/App Standby constraints.

### 1. Module Architecture

**Core modules**:

- **ble-core**: BluetoothGatt wrapper, connection state machine, MTU negotiation
- **device-manager**: pairing/bonding, device discovery, address caching
- **gatt-services**: custom GATT profile, characteristic reads/writes/notifications
- **sync-engine**: orchestration, backfill cursor, deduplication, retry logic
- **store (`Room`)**: local persistence, conflict resolution, cursor tracking
- **analytics**: connection metrics, sync success rates, battery impact
- **feature-flags**: gradual rollout of sync strategies

### 2. Pairing & Bonding

**Security model**: LE Secure Connections (Level 4) with passkey or Just Works depending on device capabilities.

```kotlin
// ✅ Persist bond after successful pairing
fun createBond(context: Context, device: BluetoothDevice): Flow<BondState> = callbackFlow {
    val filter = IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val bondedDevice: BluetoothDevice? =
                intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
            if (bondedDevice?.address != device.address) return

            when (intent.getIntExtra(BluetoothDevice.EXTRA_BOND_STATE, BluetoothDevice.ERROR)) {
                BluetoothDevice.BOND_BONDED -> trySend(BondState.Bonded)
                BluetoothDevice.BOND_NONE -> trySend(BondState.None)
            }
        }
    }
    context.registerReceiver(receiver, filter)
    device.createBond() // ✅ Initiate pairing
    awaitClose { context.unregisterReceiver(receiver) }
}

// ❌ WRONG: Ignoring BOND_NONE / device change broadcasts leads to stale state
```

**Handle revoke**: on `BOND_NONE`, clear cached device address/keys and trigger a fresh pairing flow.

### 3. GATT Profile Design

**Example service** (illustrative, not a standard profile): use a vendor-specific UUID such as `0000XXXX-0000-1000-8000-00805F9B34FB`. Note that `0000180D-0000-1000-8000-00805F9B34FB` is the standard Heart Rate `Service` UUID assigned by the Bluetooth SIG and must not be treated as a "custom" service.

**Characteristics (example)**:

- **Summary** (read/notify): current metrics (steps, heart rate, calories) — compact payload (≤ MTU - 3 bytes)
- **History** (read/notify): bulk transfer for backfill — chunked, each packet payload limited by `(negotiatedMtu - 3)` bytes
- **Control** (write): commands (start sync, set cursor, clear cache)
- **Device Info** (read): firmware version, battery level, capabilities

```kotlin
// ✅ Enable notifications for real-time updates
fun enableNotifications(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic): Boolean {
    if (!gatt.setCharacteristicNotification(characteristic, true)) return false
    val descriptor = characteristic.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG_UUID)
        ?: return false
    descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
    return gatt.writeDescriptor(descriptor) // ✅ Required for notifications to be delivered
}

// ✅ MTU negotiation for bulk transfers
fun requestMtu(gatt: BluetoothGatt, size: Int = 512) {
    // Default MTU is 23; Android can negotiate up to 517 with compatible peripherals.
    gatt.requestMtu(size.coerceAtMost(517))
}
```

**Chunking**: for transfers larger than MTU, split into packets with sequence numbers and optional checksum; reassemble on the client with timeout and integrity validation.

### 4. Sync Engine

**Foreground vs Background**:

- **Active sync**: Foreground `Service` with a notification (required on Android 8+ for long-running work)
- **Periodic sync**: `WorkManager` with `ExistingPeriodicWorkPolicy.KEEP`, constraints on battery/network

```kotlin
// ✅ Foreground service for active sync (user-initiated)
class SyncForegroundService : Service() {
    override fun onStartCommand(intent: Intent, flags: Int, startId: Int): Int {
        val notification = createSyncNotification() // ✅ Required for FG service
        startForeground(NOTIFICATION_ID, notification)
        // ... sync logic
        return START_STICKY
    }
}

// ✅ WorkManager for background periodic sync
val constraints = Constraints.Builder()
    .setRequiresBatteryNotLow(true) // ✅ Respect battery constraints
    .build()

val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(10, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()
```

**Backfill strategy**: device cursor (last synced timestamp), request data from cursor to now, deduplicate by `(deviceId, timestamp, sequence)`.

### 5. Reconnect Logic

**Exponential backoff**: on GATT errors (133, 8, 22) retry with 1s → 2s → 4s → 8s → up to 60s.

```kotlin
// ✅ Auto-reconnect with exponential backoff (simplified)
suspend fun connectWithRetry(
    context: Context,
    device: BluetoothDevice,
    maxRetries: Int = 5
) {
    var attempt = 0
    while (attempt < maxRetries) {
        attempt++
        try {
            val gatt = device.connectGatt(context, false, gattCallback)
            if (waitForConnection(gatt, timeoutMillis = 10_000L)) return
        } catch (e: Exception) {
            // fall through to backoff
        }
        val backoffSeconds = min(2.0.pow((attempt - 1).toDouble()).toLong(), 60L)
        kotlinx.coroutines.delay(backoffSeconds * 1000L)
    }
    throw ConnectionFailedException()
}

// ❌ WRONG: Blindly using autoConnect=true often causes long hangs and unreliable reconnects
```

**Connection priority**: use `CONNECTION_PRIORITY_HIGH` only during transfers, then revert to `BALANCED` for battery savings.

### 6. Battery Optimization

**Strategies**:

- Batch reads: group characteristic reads into one connection window
- Notifications > polling: prefer GATT notifications for real-time data
- Payload compression: gzip or similar for bulk history transfers (only if both sides support it)
- Throttle scans: no more than once per 10 min, use `ScanSettings.SCAN_MODE_LOW_POWER`
- Doze alignment: `setRequiresDeviceIdle(false)` + flex windows in `WorkManager` to align with system maintenance windows

**Target**: keep active sync under <1% battery/hr. For a 2000mAh battery, this is about 20mAh per hour; for a 10-minute sync window, the budget is roughly 3–4mAh, so connection efficiency is critical.

### 7. Data Model & Persistence

**`Room` entities**:

```kotlin
@Entity(
    tableName = "health_samples",
    indices = [Index(value = ["device_id", "timestamp", "sequence"], unique = true)]
)
data class HealthSample(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "device_id") val deviceId: String,
    val timestamp: Long, // Unix millis
    val sequence: Int,   // For deduplication
    val steps: Int,
    val heartRate: Int?,
    val calories: Int
)

@Entity(tableName = "sync_cursors")
data class SyncCursor(
    @PrimaryKey @ColumnInfo(name = "device_id") val deviceId: String,
    val lastSyncTimestamp: Long,
    val lastSyncSequence: Int
)
```

**Conflict resolution**: on duplicates (same `deviceId` + `timestamp` + `sequence`), rely on unique index with `INSERT OR IGNORE` / upsert and, if you track `uploadedAt`, prefer the more recent record.

### 8. Permissions Flow

**Runtime permissions** (Android 12+):

- `BLUETOOTH_CONNECT` — for connecting to bonded devices
- `BLUETOOTH_SCAN` — for discovering new devices
- `BLUETOOTH_ADVERTISE` — if reverse connection is needed
- `ACCESS_FINE_LOCATION` — for BLE scan on legacy Android (<12) where required by the platform

**`Request` flow**: show rationale UI before requesting, handle denial with fallback to manual pairing via Settings and graceful feature degradation.

### 9. Privacy & Security

**Safeguards**:

- Encrypt at rest: use SQLCipher for `Room` or EncryptedSharedPreferences for tokens/keys; avoid logging raw health data
- Minimize PII: anonymize/pseudonymize user and device identifiers before cloud upload
- User opt-out: allow disabling cloud sync and support local-only mode
- Audit logs: record only necessary metadata (who/when/what action) for access events, with retention and minimization aligned to HIPAA/GDPR; avoid storing full payloads in logs

### 10. Observability

**Key metrics** (Firebase Analytics / Datadog):

- **Connection success %**: `(successful_connects / total_attempts) * 100`
- **GATT error codes**: distribution of 133, 8, 22, 257 errors
- **Sync duration**: p50, p95, p99 latencies
- **Throughput**: bytes/sec during active sync
- **Battery impact**: estimated mAh or % consumed per sync session
- **Crash/ANR**: BLE stack crashes, ANRs in GATT callbacks

**Logging**: structured logs with correlation IDs for tracing a single sync session across modules, without persisting sensitive payload data.

### 11. Edge Cases & Testing

**Scenarios**:

- **RF-noisy environments**: retry with exponential backoff, consider lower MTU / lower priority
- **Phone sleeps mid-transfer**: acquire a partial WakeLock during active sync and resume or restart sync on wake
- **Device firmware mismatch**: version check via Device Info characteristic, show upgrade prompt
- **Bond loss**: detect via `BOND_NONE` broadcast, trigger re-pairing flow
- **Multiple devices**: queue syncs and limit to one active GATT connection per device at a time within platform limits

**Instrumented tests**: mock BluetoothGatt for unit tests, use real devices for integration tests, cover unstable RF and background execution scenarios.

### 12. Tradeoffs

| Decision                 | Pros                                 | Cons                                     |
| ------------------------ | ------------------------------------ | ---------------------------------------- |
| High connection priority | Faster sync (2-3x throughput)        | 20-30% higher battery drain              |
| Notifications vs polling | Real-time updates, less power        | Requires device support, complex flow    |
| Foreground service       | Reliable sync, no BG limits          | User-visible notification always         |
| Compression              | 30-50% less data transfer            | CPU overhead, added latency              |
| `WorkManager` flex windows | Aligns with Doze, battery-friendly   | Delayed syncs (up to 10 min late)        |
| SQLCipher encryption     | Strong at-rest protection            | 10-15% performance penalty on `Room` reads |

**Recommendation**: enable HIGH priority only temporarily (with ~30s timeout), and use compression only for bulk history transfers (not for real-time metrics).

---

## Follow-ups

- How would you handle device firmware updates over BLE (DFU protocol)?
- What strategies ensure data completeness when the device buffer overflows between syncs?
- How to scale the architecture to support simultaneous syncing with multiple paired wearables?
- How to recover from corrupted GATT data (invalid checksums, incomplete packets)?
- How would you implement privacy-preserving analytics while maintaining regulatory compliance (HIPAA/GDPR)?

## References

- [[c-lifecycle]]
- [[c-workmanager]]
- [[c-room]]
- [[c-service]]
- [[c-permissions]]
- [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
- [[ANDROID-INTERVIEWER-GUIDE]]
- https://developer.android.com/guide/topics/connectivity/bluetooth/ble-overview
- https://developer.android.com/develop/connectivity/bluetooth/bt-background-optimizations

## Related Questions

### Prerequisites (Easier)

- [[q-service-component--android--medium]] - Understanding `Service` lifecycle and foreground services
- [[q-service-restrictions-why--android--medium]] - Background execution limits on Android 8+

### Related (Same Level)

- [[q-service-lifecycle-binding--android--hard]] - Bound services and lifecycle management
- [[q-polling-implementation--android--medium]] - Alternative sync strategies with `WorkManager`

### Advanced (Harder)

- [[q-modularization-patterns--android--hard]] - Multi-module architecture for complex apps
- Design a multi-device health data aggregation platform with conflict resolution
