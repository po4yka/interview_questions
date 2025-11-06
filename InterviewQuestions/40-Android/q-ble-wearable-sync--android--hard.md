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
status: reviewed
moc: moc-android
related: [c-service, c-workmanager, c-lifecycle, c-permissions]
sources: []
created: 2025-10-29
updated: 2025-10-30
tags:
- difficulty/hard
- android/background-execution
- android/bluetooth
- android/service
- topic/android
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

-   **ble-core**: BluetoothGatt wrapper, connection state machine, MTU negotiation
-   **device-manager**: pairing/bonding, device discovery, address caching
-   **gatt-services**: custom GATT profile, characteristic reads/writes/notifications
-   **sync-engine**: orchestration, backfill cursor, deduplication, retry logic
-   **store (Room)**: local persistence, conflict resolution, cursor tracking
-   **analytics**: connection metrics, sync success rates, battery impact
-   **feature-flags**: gradual rollout of sync strategies

### 2. Pairing & Bonding

**Security model**: LE Secure Connections (Level 4) с passkey или Just Works в зависимости от capabilities устройства.

```kotlin
// ✅ Persist bond after successful pairing
fun createBond(device: BluetoothDevice): Flow<BondState> = callbackFlow {
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.getIntExtra(BluetoothDevice.EXTRA_BOND_STATE, -1)) {
                BluetoothDevice.BOND_BONDED -> trySend(BondState.Bonded)
                BluetoothDevice.BOND_NONE -> trySend(BondState.None)
            }
        }
    }
    context.registerReceiver(receiver, IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED))
    device.createBond() // ✅ Initiate pairing
    awaitClose { context.unregisterReceiver(receiver) }
}

// ❌ WRONG: Not handling bond revocation or device address changes
```

**Обработка revoke**: при `BOND_NONE` очистить cached device address, запросить повторный pairing flow.

### 3. GATT Profile Design

**Custom service UUID**: `0000180D-0000-1000-8000-00805F9B34FB` (Health Tracker Service)

**Characteristics**:

-   **Summary** (read/notify): текущие метрики (шаги, пульс, калории) - 20 bytes
-   **History** (read): bulk transfer для backfill - chunked, до 512 bytes per MTU
-   **Control** (write): команды (start sync, set cursor, clear cache)
-   **Device Info** (read): firmware version, battery level, capabilities

```kotlin
// ✅ Enable notifications for real-time updates
fun enableNotifications(characteristic: BluetoothGattCharacteristic): Boolean {
    gatt.setCharacteristicNotification(characteristic, true)
    val descriptor = characteristic.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG_UUID)
    descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
    return gatt.writeDescriptor(descriptor) // ✅ Critical for notifications
}

// ✅ MTU negotiation for bulk transfers
fun requestMtu(size: Int = 512) {
    gatt.requestMtu(size) // Default 23, negotiate up to 517
}
```

**Chunking**: для передач >MTU разбивать на packets с sequence numbers, собирать на клиенте с таймаутом.

### 4. Sync Engine

**Foreground vs Background**:

-   **Active sync**: Foreground Service с notification (обязательно для Android 8+)
-   **Periodic sync**: WorkManager с `ExistingPeriodicWorkPolicy.KEEP`, constraints на battery/network

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
// ✅ Auto-reconnect with exponential backoff
suspend fun connectWithRetry(device: BluetoothDevice, maxRetries: Int = 5) {
    repeat(maxRetries) { attempt ->
        try {
            gatt = device.connectGatt(context, false, gattCallback) // ✅ autoConnect=false for faster initial
            if (waitForConnection(timeout = 10.seconds)) return
        } catch (e: Exception) {
            val delay = min(2.0.pow(attempt).toLong(), 60)
            delay(delay * 1000L) // ✅ Exponential backoff
        }
    }
    throw ConnectionFailedException()
}

// ❌ WRONG: autoConnect=true causes indefinite hangs on 133 errors
```

**Connection priority**: `CONNECTION_PRIORITY_HIGH` только во время передач, затем вернуть к `BALANCED` для экономии батареи.

### 6. Battery Optimization

**Strategies**:

-   Batch reads: группировать characteristic reads в один connection window
-   Notifications > polling: prefer GATT notifications для real-time data
-   Payload compression: gzip для bulk history transfers (30-50% reduction)
-   Throttle scans: не чаще 1 раз в 10 мин, использовать `ScanSettings.SCAN_MODE_LOW_POWER`
-   Doze alignment: `setRequiresDeviceIdle(false)` + flex windows в WorkManager

**Target**: <1% battery/hr = ~20mAh за 10 мин sync window на 2000mAh батарее.

### 7. Data Model & Persistence

**Room entities**:

```kotlin
@Entity(tableName = "health_samples", indices = [Index(value = ["device_id", "timestamp", "sequence"], unique = true)])
data class HealthSample(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val deviceId: String,
    val timestamp: Long, // Unix millis
    val sequence: Int,   // For deduplication
    val steps: Int,
    val heartRate: Int?,
    val calories: Int
)

@Entity(tableName = "sync_cursors")
data class SyncCursor(
    @PrimaryKey val deviceId: String,
    val lastSyncTimestamp: Long,
    val lastSyncSequence: Int
)
```

**Conflict resolution**: при дубликатах (same deviceId+timestamp+sequence) предпочитать запись с более поздним `uploadedAt`.

### 8. Permissions Flow

**Runtime permissions** (Android 12+):

-   `BLUETOOTH_CONNECT` - для подключения к bonded devices
-   `BLUETOOTH_SCAN` - для discovery новых устройств
-   `BLUETOOTH_ADVERTISE` - если нужен reverse connection
-   `ACCESS_FINE_LOCATION` - для BLE scan (legacy Android <12)

**Request flow**: показывать rationale UI перед запросом, обрабатывать denial с fallback на manual pairing через Settings.

### 9. Privacy & Security

**Safeguards**:

-   Encrypt at rest: Room database с SQLCipher или EncryptedSharedPreferences для device tokens
-   Minimize PII: anonymize user data перед cloud upload, use hashed device IDs
-   User opt-out: allow disabling cloud sync, keep local-only mode
-   Audit logs: track access to health data для compliance (HIPAA/GDPR)

### 10. Observability

**Key metrics** (Firebase Analytics / Datadog):

-   **Connection success %**: `(successful_connects / total_attempts) * 100`
-   **GATT error codes**: distribution of 133, 8, 22, 257 errors
-   **Sync duration**: p50, p95, p99 latencies
-   **Throughput**: bytes/sec during active sync
-   **Battery impact**: mAh consumed per sync session
-   **Crash/ANR**: BLE stack crashes, ANRs в GATT callbacks

**Logging**: structured logs с correlation IDs для tracing single sync session через все модули.

### 11. Edge Cases & Testing

**Scenarios**:

-   **RF-noisy environments**: retry с exponential backoff, fallback на lower MTU
-   **Phone sleeps mid-transfer**: WakeLock во время active sync, resume на wake
-   **Device firmware mismatch**: version check в Device Info characteristic, show upgrade prompt
-   **Bond loss**: detect via `BOND_NONE` broadcast, trigger re-pairing flow
-   **Multiple devices**: queue syncs, limit to 1 active connection at a time

**Instrumented tests**: mock BluetoothGatt для unit tests, real device tests для integration.

### 12. Tradeoffs

| Decision                    | Pros                                | Cons                                     |
| --------------------------- | ----------------------------------- | ---------------------------------------- |
| High connection priority    | Faster sync (2-3x throughput)       | 20-30% higher battery drain              |
| Notifications vs polling    | Real-time updates, less power       | Requires device support, complex flow    |
| Foreground service          | Reliable sync, no background limits | User-visible notification always         |
| Compression                 | 30-50% less data transfer           | CPU overhead, added latency              |
| WorkManager flex windows    | Aligns with Doze, battery-friendly  | Delayed syncs (up to 10 min late)        |
| SQLCipher encryption        | Strong at-rest protection           | 10-15% performance penalty on Room reads |

**Рекомендация**: включать HIGH priority временно (с explicit timeout 30s), использовать compression только для bulk history (не для real-time metrics).

---

## Answer (EN)

BLE wearable sync requires an architecture with separated concerns: connection management, GATT communication, background sync, persistent storage, and reconnect handling under Doze/App Standby constraints.

### 1. Module Architecture

**Core modules**:

-   **ble-core**: BluetoothGatt wrapper, connection state machine, MTU negotiation
-   **device-manager**: pairing/bonding, device discovery, address caching
-   **gatt-services**: custom GATT profile, characteristic reads/writes/notifications
-   **sync-engine**: orchestration, backfill cursor, deduplication, retry logic
-   **store (Room)**: local persistence, conflict resolution, cursor tracking
-   **analytics**: connection metrics, sync success rates, battery impact
-   **feature-flags**: gradual rollout of sync strategies

### 2. Pairing & Bonding

**Security model**: LE Secure Connections (Level 4) with passkey or Just Works depending on device capabilities.

```kotlin
// ✅ Persist bond after successful pairing
fun createBond(device: BluetoothDevice): Flow<BondState> = callbackFlow {
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            when (intent.getIntExtra(BluetoothDevice.EXTRA_BOND_STATE, -1)) {
                BluetoothDevice.BOND_BONDED -> trySend(BondState.Bonded)
                BluetoothDevice.BOND_NONE -> trySend(BondState.None)
            }
        }
    }
    context.registerReceiver(receiver, IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED))
    device.createBond() // ✅ Initiate pairing
    awaitClose { context.unregisterReceiver(receiver) }
}

// ❌ WRONG: Not handling bond revocation or device address changes
```

**Handle revoke**: on `BOND_NONE`, clear cached device address, trigger re-pairing flow.

### 3. GATT Profile Design

**Custom service UUID**: `0000180D-0000-1000-8000-00805F9B34FB` (Health Tracker Service)

**Characteristics**:

-   **Summary** (read/notify): current metrics (steps, heart rate, calories) - 20 bytes
-   **History** (read): bulk transfer for backfill - chunked, up to 512 bytes per MTU
-   **Control** (write): commands (start sync, set cursor, clear cache)
-   **Device Info** (read): firmware version, battery level, capabilities

```kotlin
// ✅ Enable notifications for real-time updates
fun enableNotifications(characteristic: BluetoothGattCharacteristic): Boolean {
    gatt.setCharacteristicNotification(characteristic, true)
    val descriptor = characteristic.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG_UUID)
    descriptor.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
    return gatt.writeDescriptor(descriptor) // ✅ Critical for notifications
}

// ✅ MTU negotiation for bulk transfers
fun requestMtu(size: Int = 512) {
    gatt.requestMtu(size) // Default 23, negotiate up to 517
}
```

**Chunking**: for transfers >MTU, split into packets with sequence numbers, reassemble on client with timeout.

### 4. Sync Engine

**Foreground vs Background**:

-   **Active sync**: Foreground Service with notification (required Android 8+)
-   **Periodic sync**: WorkManager with `ExistingPeriodicWorkPolicy.KEEP`, constraints on battery/network

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

**Exponential backoff**: on GATT errors (133, 8, 22) retry with 1s → 2s → 4s → 8s → max 60s.

```kotlin
// ✅ Auto-reconnect with exponential backoff
suspend fun connectWithRetry(device: BluetoothDevice, maxRetries: Int = 5) {
    repeat(maxRetries) { attempt ->
        try {
            gatt = device.connectGatt(context, false, gattCallback) // ✅ autoConnect=false for faster initial
            if (waitForConnection(timeout = 10.seconds)) return
        } catch (e: Exception) {
            val delay = min(2.0.pow(attempt).toLong(), 60)
            delay(delay * 1000L) // ✅ Exponential backoff
        }
    }
    throw ConnectionFailedException()
}

// ❌ WRONG: autoConnect=true causes indefinite hangs on 133 errors
```

**Connection priority**: `CONNECTION_PRIORITY_HIGH` only during transfers, then revert to `BALANCED` for battery savings.

### 6. Battery Optimization

**Strategies**:

-   Batch reads: group characteristic reads into one connection window
-   Notifications > polling: prefer GATT notifications for real-time data
-   Payload compression: gzip for bulk history transfers (30-50% reduction)
-   Throttle scans: no more than 1 per 10 min, use `ScanSettings.SCAN_MODE_LOW_POWER`
-   Doze alignment: `setRequiresDeviceIdle(false)` + flex windows in WorkManager

**Target**: <1% battery/hr = ~20mAh per 10 min sync window on 2000mAh battery.

### 7. Data Model & Persistence

**Room entities**:

```kotlin
@Entity(tableName = "health_samples", indices = [Index(value = ["device_id", "timestamp", "sequence"], unique = true)])
data class HealthSample(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val deviceId: String,
    val timestamp: Long, // Unix millis
    val sequence: Int,   // For deduplication
    val steps: Int,
    val heartRate: Int?,
    val calories: Int
)

@Entity(tableName = "sync_cursors")
data class SyncCursor(
    @PrimaryKey val deviceId: String,
    val lastSyncTimestamp: Long,
    val lastSyncSequence: Int
)
```

**Conflict resolution**: on duplicates (same deviceId+timestamp+sequence), prefer record with later `uploadedAt`.

### 8. Permissions Flow

**Runtime permissions** (Android 12+):

-   `BLUETOOTH_CONNECT` - for connecting to bonded devices
-   `BLUETOOTH_SCAN` - for discovering new devices
-   `BLUETOOTH_ADVERTISE` - if reverse connection needed
-   `ACCESS_FINE_LOCATION` - for BLE scan (legacy Android <12)

**Request flow**: show rationale UI before request, handle denial with fallback to manual pairing via Settings.

### 9. Privacy & Security

**Safeguards**:

-   Encrypt at rest: Room database with SQLCipher or EncryptedSharedPreferences for device tokens
-   Minimize PII: anonymize user data before cloud upload, use hashed device IDs
-   User opt-out: allow disabling cloud sync, keep local-only mode
-   Audit logs: track access to health data for compliance (HIPAA/GDPR)

### 10. Observability

**Key metrics** (Firebase Analytics / Datadog):

-   **Connection success %**: `(successful_connects / total_attempts) * 100`
-   **GATT error codes**: distribution of 133, 8, 22, 257 errors
-   **Sync duration**: p50, p95, p99 latencies
-   **Throughput**: bytes/sec during active sync
-   **Battery impact**: mAh consumed per sync session
-   **Crash/ANR**: BLE stack crashes, ANRs in GATT callbacks

**Logging**: structured logs with correlation IDs for tracing single sync session across all modules.

### 11. Edge Cases & Testing

**Scenarios**:

-   **RF-noisy environments**: retry with exponential backoff, fallback to lower MTU
-   **Phone sleeps mid-transfer**: WakeLock during active sync, resume on wake
-   **Device firmware mismatch**: version check in Device Info characteristic, show upgrade prompt
-   **Bond loss**: detect via `BOND_NONE` broadcast, trigger re-pairing flow
-   **Multiple devices**: queue syncs, limit to 1 active connection at a time

**Instrumented tests**: mock BluetoothGatt for unit tests, real device tests for integration.

### 12. Tradeoffs

| Decision                 | Pros                            | Cons                                     |
| ------------------------ | ------------------------------- | ---------------------------------------- |
| High connection priority | Faster sync (2-3x throughput)   | 20-30% higher battery drain              |
| Notifications vs polling | Real-time updates, less power   | Requires device support, complex flow    |
| Foreground service       | Reliable sync, no BG limits     | User-visible notification always         |
| Compression              | 30-50% less data transfer       | CPU overhead, added latency              |
| WorkManager flex windows | Aligns with Doze, battery-friendly | Delayed syncs (up to 10 min late)     |
| SQLCipher encryption     | Strong at-rest protection       | 10-15% performance penalty on Room reads |

**Recommendation**: enable HIGH priority temporarily (with explicit 30s timeout), use compression only for bulk history (not for real-time metrics).

---

## Follow-ups

-   How would you handle device firmware updates over BLE (DFU protocol)?
-   What strategies ensure data completeness when the device buffer overflows between syncs?
-   How to scale the architecture to support simultaneous syncing with multiple paired wearables?
-   How to recover from corrupted GATT data (invalid checksums, incomplete packets)?
-   How would you implement privacy-preserving analytics while maintaining regulatory compliance (HIPAA/GDPR)?

## References

-   [[c-lifecycle]]
-   [[c-workmanager]]
-   [[c-room]]
-   [[c-service]]
-   [[c-permissions]]
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]
-   https://developer.android.com/guide/topics/connectivity/bluetooth/ble-overview
-   https://developer.android.com/develop/connectivity/bluetooth/bt-background-optimizations

## Related Questions

### Prerequisites (Easier)

-   [[q-service-component--android--medium]] - Understanding Service lifecycle and foreground services
-   [[q-service-restrictions-why--android--medium]] - Background execution limits on Android 8+

### Related (Same Level)

-   [[q-service-lifecycle-binding--android--hard]] - Bound services and lifecycle management
-   [[q-polling-implementation--android--medium]] - Alternative sync strategies with WorkManager

### Advanced (Harder)

-   [[q-modularization-patterns--android--hard]] - Multi-module architecture for complex apps
-   Design a multi-device health data aggregation platform with conflict resolution
