---
id: android-754
title: Network Connectivity on Android / Сетевое подключение на Android
aliases:
- Network Connectivity on Android
- Сетевое подключение на Android
topic: android
subtopics:
- networking
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-networking
- q-network-operations-android--android--medium
- q-data-sync-unstable-network--android--hard
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/training/monitoring-device-state/connectivity-status-type
- https://developer.android.com/reference/android/net/ConnectivityManager
- https://developer.android.com/training/basics/network-ops/reading-network-state
tags:
- android/networking
- difficulty/medium
- connectivity-manager
- network-callback
- network-state
- flow
anki_cards:
- slug: android-754-0-en
  language: en
- slug: android-754-0-ru
  language: ru
---
# Вопрос (RU)

> Как отслеживать состояние сети на Android? Объясните ConnectivityManager, NetworkCallback и реактивный подход с Flow.

# Question (EN)

> How do you monitor network connectivity on Android? Explain ConnectivityManager, NetworkCallback, and reactive approach with Flow.

---

## Ответ (RU)

**ConnectivityManager** - системный сервис Android для мониторинга сетевого состояния. Начиная с API 21 (Lollipop) рекомендуется использовать **NetworkCallback** вместо устаревших BroadcastReceiver подходов. Для реактивного UI лучше всего обернуть callback в **Flow**.

### Краткий Ответ

- **ConnectivityManager** предоставляет информацию о сетевом подключении
- **NetworkCallback** (API 21+) - современный способ подписки на изменения сети
- Используйте **Flow** для реактивной интеграции с ViewModel и Compose
- Проверяйте **NetworkCapabilities** для определения типа и качества соединения

### Подробный Ответ

### Проверка Текущего Состояния

```kotlin
class NetworkChecker @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    // Проверка наличия интернета (API 23+)
    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager?.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    // Проверка типа соединения
    fun getConnectionType(): ConnectionType {
        val network = connectivityManager?.activeNetwork ?: return ConnectionType.NONE
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return ConnectionType.NONE

        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> ConnectionType.WIFI
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> ConnectionType.CELLULAR
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> ConnectionType.ETHERNET
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> ConnectionType.VPN
            else -> ConnectionType.UNKNOWN
        }
    }

    // Проверка metered соединения (платный трафик)
    fun isMeteredConnection(): Boolean {
        return connectivityManager?.isActiveNetworkMetered ?: true
    }
}

enum class ConnectionType {
    WIFI, CELLULAR, ETHERNET, VPN, UNKNOWN, NONE
}
```

### NetworkCallback для Подписки на Изменения

```kotlin
class NetworkMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    private val _networkState = MutableStateFlow(NetworkState.Unknown)
    val networkState: StateFlow<NetworkState> = _networkState.asStateFlow()

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        // Вызывается когда сеть становится доступной
        override fun onAvailable(network: Network) {
            _networkState.value = NetworkState.Available
        }

        // Вызывается когда сеть теряется
        override fun onLost(network: Network) {
            _networkState.value = NetworkState.Lost
        }

        // Вызывается когда изменяются capabilities сети
        override fun onCapabilitiesChanged(
            network: Network,
            networkCapabilities: NetworkCapabilities
        ) {
            val hasInternet = networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_INTERNET
            )
            val isValidated = networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_VALIDATED
            )

            _networkState.value = if (hasInternet && isValidated) {
                NetworkState.Connected(
                    type = getConnectionType(networkCapabilities),
                    isMetered = !networkCapabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_NOT_METERED
                    )
                )
            } else {
                NetworkState.NoInternet
            }
        }

        // Вызывается когда сеть недоступна (таймаут)
        override fun onUnavailable() {
            _networkState.value = NetworkState.Unavailable
        }
    }

    fun startMonitoring() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, networkCallback)
    }

    fun stopMonitoring() {
        try {
            connectivityManager?.unregisterNetworkCallback(networkCallback)
        } catch (e: IllegalArgumentException) {
            // Callback was not registered
        }
    }

    private fun getConnectionType(capabilities: NetworkCapabilities): ConnectionType {
        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> ConnectionType.WIFI
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> ConnectionType.CELLULAR
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> ConnectionType.ETHERNET
            else -> ConnectionType.UNKNOWN
        }
    }
}

sealed class NetworkState {
    data object Unknown : NetworkState()
    data object Available : NetworkState()
    data object Lost : NetworkState()
    data object Unavailable : NetworkState()
    data object NoInternet : NetworkState()
    data class Connected(
        val type: ConnectionType,
        val isMetered: Boolean
    ) : NetworkState()
}
```

### Flow-based Network Monitor

```kotlin
class FlowNetworkMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    // Flow который эмитит состояние сети при каждом изменении
    val networkStatus: Flow<NetworkStatus> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(NetworkStatus.Available)
            }

            override fun onLost(network: Network) {
                trySend(NetworkStatus.Lost)
            }

            override fun onCapabilitiesChanged(
                network: Network,
                capabilities: NetworkCapabilities
            ) {
                val status = NetworkStatus.Connected(
                    hasInternet = capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_INTERNET
                    ),
                    isValidated = capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_VALIDATED
                    ),
                    isWifi = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI),
                    isCellular = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR),
                    isMetered = !capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_NOT_METERED
                    ),
                    downloadBandwidthKbps = capabilities.linkDownstreamBandwidthKbps,
                    uploadBandwidthKbps = capabilities.linkUpstreamBandwidthKbps
                )
                trySend(status)
            }
        }

        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, callback)

        // Эмитим начальное состояние
        trySend(getCurrentNetworkStatus())

        awaitClose {
            connectivityManager?.unregisterNetworkCallback(callback)
        }
    }.distinctUntilChanged()

    // Простой Flow для проверки connectivity
    val isOnline: Flow<Boolean> = networkStatus.map { status ->
        when (status) {
            is NetworkStatus.Connected -> status.hasInternet && status.isValidated
            NetworkStatus.Available -> true
            else -> false
        }
    }.distinctUntilChanged()

    private fun getCurrentNetworkStatus(): NetworkStatus {
        val network = connectivityManager?.activeNetwork ?: return NetworkStatus.Lost
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return NetworkStatus.Lost

        return NetworkStatus.Connected(
            hasInternet = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET),
            isValidated = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED),
            isWifi = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI),
            isCellular = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR),
            isMetered = !capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED),
            downloadBandwidthKbps = capabilities.linkDownstreamBandwidthKbps,
            uploadBandwidthKbps = capabilities.linkUpstreamBandwidthKbps
        )
    }
}

sealed class NetworkStatus {
    data object Available : NetworkStatus()
    data object Lost : NetworkStatus()
    data class Connected(
        val hasInternet: Boolean,
        val isValidated: Boolean,
        val isWifi: Boolean,
        val isCellular: Boolean,
        val isMetered: Boolean,
        val downloadBandwidthKbps: Int,
        val uploadBandwidthKbps: Int
    ) : NetworkStatus()
}
```

### Интеграция с ViewModel

```kotlin
@HiltViewModel
class MainViewModel @Inject constructor(
    private val networkMonitor: FlowNetworkMonitor,
    private val userRepository: UserRepository
) : ViewModel() {

    val isOnline: StateFlow<Boolean> = networkMonitor.isOnline
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = true
        )

    val networkStatus: StateFlow<NetworkStatus> = networkMonitor.networkStatus
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = NetworkStatus.Available
        )

    // Автоматическая синхронизация при восстановлении сети
    init {
        viewModelScope.launch {
            networkMonitor.isOnline
                .filter { it } // Только когда online
                .distinctUntilChanged()
                .collect {
                    syncPendingData()
                }
        }
    }

    private suspend fun syncPendingData() {
        userRepository.syncPendingChanges()
    }
}
```

### Интеграция с Compose

```kotlin
@Composable
fun NetworkAwareContent(
    viewModel: MainViewModel = hiltViewModel()
) {
    val isOnline by viewModel.isOnline.collectAsStateWithLifecycle()
    val networkStatus by viewModel.networkStatus.collectAsStateWithLifecycle()

    Column {
        // Offline banner
        AnimatedVisibility(visible = !isOnline) {
            Surface(
                color = MaterialTheme.colorScheme.errorContainer,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "No internet connection",
                    modifier = Modifier.padding(16.dp),
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }

        // Connection type indicator
        when (val status = networkStatus) {
            is NetworkStatus.Connected -> {
                if (status.isMetered && status.isCellular) {
                    MeteredConnectionWarning()
                }
            }
            else -> {}
        }

        // Main content
        MainContent()
    }
}

@Composable
fun MeteredConnectionWarning() {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        ),
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Text(
            text = "Using mobile data",
            modifier = Modifier.padding(8.dp),
            style = MaterialTheme.typography.bodySmall
        )
    }
}
```

### Проверка Permissions

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Лучшие Практики

1. **registerDefaultNetworkCallback** (API 24+) - для отслеживания активной сети
2. **Проверяйте VALIDATED** - NET_CAPABILITY_INTERNET не гарантирует реальный доступ
3. **Используйте Flow** - для реактивной интеграции с UI
4. **Unregister callback** - всегда отписывайтесь при уничтожении
5. **Fallback для старых API** - проверяйте minSdkVersion
6. **Exponential backoff** - при retry после восстановления сети

---

## Answer (EN)

**ConnectivityManager** is an Android system service for monitoring network state. Starting from API 21 (Lollipop), **NetworkCallback** is the recommended approach instead of deprecated BroadcastReceiver methods. For reactive UI, it's best to wrap callbacks in **Flow**.

### Short Version

- **ConnectivityManager** provides network connection information
- **NetworkCallback** (API 21+) - modern way to subscribe to network changes
- Use **Flow** for reactive integration with ViewModel and Compose
- Check **NetworkCapabilities** to determine connection type and quality

### Detailed Version

### Checking Current State

```kotlin
class NetworkChecker @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    // Check internet availability (API 23+)
    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager?.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    // Check connection type
    fun getConnectionType(): ConnectionType {
        val network = connectivityManager?.activeNetwork ?: return ConnectionType.NONE
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return ConnectionType.NONE

        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> ConnectionType.WIFI
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> ConnectionType.CELLULAR
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> ConnectionType.ETHERNET
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_VPN) -> ConnectionType.VPN
            else -> ConnectionType.UNKNOWN
        }
    }

    // Check metered connection (paid traffic)
    fun isMeteredConnection(): Boolean {
        return connectivityManager?.isActiveNetworkMetered ?: true
    }
}

enum class ConnectionType {
    WIFI, CELLULAR, ETHERNET, VPN, UNKNOWN, NONE
}
```

### NetworkCallback for Subscribing to Changes

```kotlin
class NetworkMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    private val _networkState = MutableStateFlow(NetworkState.Unknown)
    val networkState: StateFlow<NetworkState> = _networkState.asStateFlow()

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        // Called when network becomes available
        override fun onAvailable(network: Network) {
            _networkState.value = NetworkState.Available
        }

        // Called when network is lost
        override fun onLost(network: Network) {
            _networkState.value = NetworkState.Lost
        }

        // Called when network capabilities change
        override fun onCapabilitiesChanged(
            network: Network,
            networkCapabilities: NetworkCapabilities
        ) {
            val hasInternet = networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_INTERNET
            )
            val isValidated = networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_VALIDATED
            )

            _networkState.value = if (hasInternet && isValidated) {
                NetworkState.Connected(
                    type = getConnectionType(networkCapabilities),
                    isMetered = !networkCapabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_NOT_METERED
                    )
                )
            } else {
                NetworkState.NoInternet
            }
        }

        // Called when network is unavailable (timeout)
        override fun onUnavailable() {
            _networkState.value = NetworkState.Unavailable
        }
    }

    fun startMonitoring() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, networkCallback)
    }

    fun stopMonitoring() {
        try {
            connectivityManager?.unregisterNetworkCallback(networkCallback)
        } catch (e: IllegalArgumentException) {
            // Callback was not registered
        }
    }

    private fun getConnectionType(capabilities: NetworkCapabilities): ConnectionType {
        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> ConnectionType.WIFI
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> ConnectionType.CELLULAR
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> ConnectionType.ETHERNET
            else -> ConnectionType.UNKNOWN
        }
    }
}

sealed class NetworkState {
    data object Unknown : NetworkState()
    data object Available : NetworkState()
    data object Lost : NetworkState()
    data object Unavailable : NetworkState()
    data object NoInternet : NetworkState()
    data class Connected(
        val type: ConnectionType,
        val isMetered: Boolean
    ) : NetworkState()
}
```

### Flow-based Network Monitor

```kotlin
class FlowNetworkMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    // Flow that emits network state on each change
    val networkStatus: Flow<NetworkStatus> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(NetworkStatus.Available)
            }

            override fun onLost(network: Network) {
                trySend(NetworkStatus.Lost)
            }

            override fun onCapabilitiesChanged(
                network: Network,
                capabilities: NetworkCapabilities
            ) {
                val status = NetworkStatus.Connected(
                    hasInternet = capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_INTERNET
                    ),
                    isValidated = capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_VALIDATED
                    ),
                    isWifi = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI),
                    isCellular = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR),
                    isMetered = !capabilities.hasCapability(
                        NetworkCapabilities.NET_CAPABILITY_NOT_METERED
                    ),
                    downloadBandwidthKbps = capabilities.linkDownstreamBandwidthKbps,
                    uploadBandwidthKbps = capabilities.linkUpstreamBandwidthKbps
                )
                trySend(status)
            }
        }

        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager?.registerNetworkCallback(request, callback)

        // Emit initial state
        trySend(getCurrentNetworkStatus())

        awaitClose {
            connectivityManager?.unregisterNetworkCallback(callback)
        }
    }.distinctUntilChanged()

    // Simple Flow for connectivity check
    val isOnline: Flow<Boolean> = networkStatus.map { status ->
        when (status) {
            is NetworkStatus.Connected -> status.hasInternet && status.isValidated
            NetworkStatus.Available -> true
            else -> false
        }
    }.distinctUntilChanged()

    private fun getCurrentNetworkStatus(): NetworkStatus {
        val network = connectivityManager?.activeNetwork ?: return NetworkStatus.Lost
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return NetworkStatus.Lost

        return NetworkStatus.Connected(
            hasInternet = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET),
            isValidated = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED),
            isWifi = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI),
            isCellular = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR),
            isMetered = !capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED),
            downloadBandwidthKbps = capabilities.linkDownstreamBandwidthKbps,
            uploadBandwidthKbps = capabilities.linkUpstreamBandwidthKbps
        )
    }
}

sealed class NetworkStatus {
    data object Available : NetworkStatus()
    data object Lost : NetworkStatus()
    data class Connected(
        val hasInternet: Boolean,
        val isValidated: Boolean,
        val isWifi: Boolean,
        val isCellular: Boolean,
        val isMetered: Boolean,
        val downloadBandwidthKbps: Int,
        val uploadBandwidthKbps: Int
    ) : NetworkStatus()
}
```

### Integration with ViewModel

```kotlin
@HiltViewModel
class MainViewModel @Inject constructor(
    private val networkMonitor: FlowNetworkMonitor,
    private val userRepository: UserRepository
) : ViewModel() {

    val isOnline: StateFlow<Boolean> = networkMonitor.isOnline
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = true
        )

    val networkStatus: StateFlow<NetworkStatus> = networkMonitor.networkStatus
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = NetworkStatus.Available
        )

    // Auto-sync when network is restored
    init {
        viewModelScope.launch {
            networkMonitor.isOnline
                .filter { it } // Only when online
                .distinctUntilChanged()
                .collect {
                    syncPendingData()
                }
        }
    }

    private suspend fun syncPendingData() {
        userRepository.syncPendingChanges()
    }
}
```

### Integration with Compose

```kotlin
@Composable
fun NetworkAwareContent(
    viewModel: MainViewModel = hiltViewModel()
) {
    val isOnline by viewModel.isOnline.collectAsStateWithLifecycle()
    val networkStatus by viewModel.networkStatus.collectAsStateWithLifecycle()

    Column {
        // Offline banner
        AnimatedVisibility(visible = !isOnline) {
            Surface(
                color = MaterialTheme.colorScheme.errorContainer,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "No internet connection",
                    modifier = Modifier.padding(16.dp),
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }

        // Connection type indicator
        when (val status = networkStatus) {
            is NetworkStatus.Connected -> {
                if (status.isMetered && status.isCellular) {
                    MeteredConnectionWarning()
                }
            }
            else -> {}
        }

        // Main content
        MainContent()
    }
}

@Composable
fun MeteredConnectionWarning() {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer
        ),
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Text(
            text = "Using mobile data",
            modifier = Modifier.padding(8.dp),
            style = MaterialTheme.typography.bodySmall
        )
    }
}
```

### Permission Check

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Best Practices

1. **registerDefaultNetworkCallback** (API 24+) - for tracking active network
2. **Check VALIDATED** - NET_CAPABILITY_INTERNET doesn't guarantee actual access
3. **Use Flow** - for reactive UI integration
4. **Unregister callback** - always unsubscribe on destruction
5. **Fallback for older APIs** - check minSdkVersion
6. **Exponential backoff** - when retrying after network restoration

---

## Дополнительные Вопросы (RU)

1. Чем отличается registerNetworkCallback от registerDefaultNetworkCallback?
2. Как определить качество сетевого соединения (bandwidth)?
3. Как обрабатывать переключение между WiFi и Cellular?
4. Как тестировать код с NetworkCallback?
5. Какие ограничения на network state в background?

## Follow-ups

1. What is the difference between registerNetworkCallback and registerDefaultNetworkCallback?
2. How do you determine network connection quality (bandwidth)?
3. How do you handle switching between WiFi and Cellular?
4. How do you test code with NetworkCallback?
5. What are the limitations on network state in background?

## Ссылки (RU)

- [Monitor connectivity status](https://developer.android.com/training/monitoring-device-state/connectivity-status-type)
- [ConnectivityManager](https://developer.android.com/reference/android/net/ConnectivityManager)
- [Reading network state](https://developer.android.com/training/basics/network-ops/reading-network-state)

## References

- [Monitor connectivity status](https://developer.android.com/training/monitoring-device-state/connectivity-status-type)
- [ConnectivityManager](https://developer.android.com/reference/android/net/ConnectivityManager)
- [Reading network state](https://developer.android.com/training/basics/network-ops/reading-network-state)

## Связанные Вопросы (RU)

### Предпосылки

- [[q-network-operations-android--android--medium]]
- [[q-broadcast-receiver-basics--android--easy]]

### Похожие

- [[q-workmanager-execution-guarantee--android--medium]]
- [[q-polling-implementation--android--medium]]

### Продвинутое

- [[q-data-sync-unstable-network--android--hard]]
- [[q-offline-first--networking--hard]]

## Related Questions

### Prerequisites

- [[q-network-operations-android--android--medium]]
- [[q-broadcast-receiver-basics--android--easy]]

### Related

- [[q-workmanager-execution-guarantee--android--medium]]
- [[q-polling-implementation--android--medium]]

### Advanced

- [[q-data-sync-unstable-network--android--hard]]
- [[q-offline-first--networking--hard]]
