---
id: 20251006-000003
title: "How to design Uber App? / Как спроектировать приложение Uber?"
aliases: []

# Classification
topic: system-design
subtopics: [location, real-time, maps, architecture, scalability, mobile-app-design]
question_kind: design
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [location-tracking, real-time-updates, websocket, maps-integration]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [system-design, uber, location, real-time, maps, architecture, android, difficulty/hard]
---
## Question (EN)
> How would you design an Uber-like ride-hailing application for Android?
## Вопрос (RU)
> Как бы вы спроектировали приложение для вызова такси, подобное Uber, для Android?

---

## Answer (EN)

Designing an Uber-like application involves complex real-time location tracking, matching algorithms, payment processing, and scalable architecture. Here's a comprehensive system design:

### 1. Core Requirements

**Functional Requirements:**

*Rider App:*
- View nearby drivers on map
- Request ride with pickup/destination
- See estimated fare and arrival time
- Track driver in real-time
- In-app payment
- Rate driver
- Ride history

*Driver App:*
- Go online/offline
- Receive ride requests
- Accept/reject rides
- Navigate to pickup/destination
- Track earnings
- Rate rider

**Non-Functional Requirements:**
- Real-time location updates (every 3-5 seconds)
- Low latency matching (< 2 seconds)
- High availability (99.99%)
- Scalability (millions of concurrent users)
- Accurate GPS tracking
- Battery optimization
- Offline capability

### 2. High-Level Architecture

```
┌──────────────┐        ┌──────────────┐
│  Rider App   │        │  Driver App  │
└──────┬───────┘        └──────┬───────┘
       │                       │
       ├───────────┬───────────┤
       │           │           │
       ├── REST API (Ride management)
       ├── WebSocket (Real-time location)
       ├── Google Maps API
       └── Payment Gateway
       │
┌──────▼──────────────────────┐
│    Load Balancer/API Gateway│
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│  Microservices Architecture │
│  ┌────────────────────────┐ │
│  │ Location Service       │ │
│  │ Matching Service       │ │
│  │ Ride Service           │ │
│  │ Payment Service        │ │
│  │ Notification Service   │ │
│  │ Pricing Service        │ │
│  └────────────────────────┘ │
└─────────────────────────────┘
       │
       ├─── Geospatial DB (Redis GeoHash)
       ├─── Relational DB (PostgreSQL)
       ├─── Message Queue (Kafka)
       ├─── Cache (Redis)
       └─── Maps Service (Google Maps)
```

### 3. Android App Architecture

#### Data Models

```kotlin
data class Location(
    val latitude: Double,
    val longitude: Double,
    val bearing: Float = 0f,
    val accuracy: Float = 0f,
    val timestamp: Long = System.currentTimeMillis()
)

data class Ride(
    val id: String,
    val riderId: String,
    val driverId: String?,
    val pickupLocation: Location,
    val destinationLocation: Location,
    val status: RideStatus,
    val fare: Double,
    val distance: Double, // in meters
    val duration: Int, // in seconds
    val vehicleType: VehicleType,
    val createdAt: Long,
    val acceptedAt: Long? = null,
    val startedAt: Long? = null,
    val completedAt: Long? = null
)

enum class RideStatus {
    REQUESTED,
    ACCEPTED,
    ARRIVED,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
}

enum class VehicleType {
    UBER_X,
    UBER_XL,
    UBER_BLACK,
    UBER_POOL
}

data class Driver(
    val id: String,
    val name: String,
    val rating: Float,
    val currentLocation: Location,
    val vehicleType: VehicleType,
    val vehicleNumber: String,
    val isOnline: Boolean,
    val isAvailable: Boolean
)
```

#### Location Tracking

```kotlin
class LocationTracker @Inject constructor(
    private val context: Context,
    private val fusedLocationClient: FusedLocationProviderClient
) {
    private val _locationUpdates = MutableStateFlow<Location?>(null)
    val locationUpdates: StateFlow<Location?> = _locationUpdates.asStateFlow()

    @SuppressLint("MissingPermission")
    fun startLocationUpdates() {
        val locationRequest = LocationRequest.Builder(
            Priority.PRIORITY_HIGH_ACCURACY,
            3000L // Update every 3 seconds
        ).apply {
            setMinUpdateIntervalMillis(1000L) // Fastest 1 second
            setMaxUpdateDelayMillis(5000L)
            setWaitForAccurateLocation(true)
        }.build()

        val locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { location ->
                    _locationUpdates.value = Location(
                        latitude = location.latitude,
                        longitude = location.longitude,
                        bearing = location.bearing,
                        accuracy = location.accuracy,
                        timestamp = location.time
                    )
                }
            }
        }

        fusedLocationClient.requestLocationUpdates(
            locationRequest,
            locationCallback,
            Looper.getMainLooper()
        )
    }

    fun stopLocationUpdates() {
        fusedLocationClient.removeLocationUpdates(locationCallback)
    }
}
```

#### Driver Location Sync

```kotlin
class DriverLocationSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val locationTracker: LocationTracker,
    private val locationRepository: LocationRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        locationTracker.locationUpdates
            .filterNotNull()
            .debounce(3000) // Send every 3 seconds
            .collect { location ->
                try {
                    // Send location to server
                    locationRepository.updateDriverLocation(
                        driverId = getDriverId(),
                        location = location
                    )
                } catch (e: Exception) {
                    Log.e("LocationSync", "Failed to update location", e)
                }
            }

        return Result.success()
    }

    companion object {
        fun enqueue(workManager: WorkManager) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val work = OneTimeWorkRequestBuilder<DriverLocationSyncWorker>()
                .setConstraints(constraints)
                .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                .build()

            workManager.enqueue(work)
        }
    }
}
```

#### Nearby Drivers Discovery

```kotlin
class NearbyDriversUseCase @Inject constructor(
    private val driverRepository: DriverRepository,
    private val locationTracker: LocationTracker
) {
    operator fun invoke(
        radius: Int = 5000, // 5 km
        vehicleType: VehicleType = VehicleType.UBER_X
    ): Flow<List<Driver>> {
        return locationTracker.locationUpdates
            .filterNotNull()
            .flatMapLatest { currentLocation ->
                driverRepository.getNearbyDrivers(
                    location = currentLocation,
                    radius = radius,
                    vehicleType = vehicleType
                )
            }
    }
}

// Repository implementation
class DriverRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val websocketManager: WebSocketManager
) : DriverRepository {

    override fun getNearbyDrivers(
        location: Location,
        radius: Int,
        vehicleType: VehicleType
    ): Flow<List<Driver>> = flow {
        // Initial fetch via REST API
        val drivers = apiService.getNearbyDrivers(
            lat = location.latitude,
            lng = location.longitude,
            radius = radius,
            vehicleType = vehicleType.name
        )
        emit(drivers)

        // Subscribe to real-time updates via WebSocket
        websocketManager.subscribeToDriverUpdates(location, radius)
            .collect { updatedDrivers ->
                emit(updatedDrivers)
            }
    }
}
```

#### Ride Request Flow

```kotlin
class RequestRideUseCase @Inject constructor(
    private val rideRepository: RideRepository,
    private val pricingService: PricingService,
    private val matchingService: MatchingService
) {
    suspend operator fun invoke(
        pickup: Location,
        destination: Location,
        vehicleType: VehicleType
    ): Result<Ride> {
        return try {
            // 1. Calculate estimated fare
            val estimatedFare = pricingService.calculateFare(
                pickup = pickup,
                destination = destination,
                vehicleType = vehicleType
            )

            // 2. Create ride request
            val ride = Ride(
                id = UUID.randomUUID().toString(),
                riderId = getCurrentUserId(),
                driverId = null,
                pickupLocation = pickup,
                destinationLocation = destination,
                status = RideStatus.REQUESTED,
                fare = estimatedFare.amount,
                distance = estimatedFare.distance,
                duration = estimatedFare.duration,
                vehicleType = vehicleType,
                createdAt = System.currentTimeMillis()
            )

            // 3. Save ride
            rideRepository.createRide(ride)

            // 4. Find matching driver
            matchingService.findDriver(ride)

            Result.Success(ride)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}
```

#### Real-time Ride Tracking

```kotlin
class RideTrackingViewModel @Inject constructor(
    private val rideRepository: RideRepository,
    private val locationRepository: LocationRepository
) : ViewModel() {

    private val _rideState = MutableStateFlow<RideState>(RideState.Idle)
    val rideState = _rideState.asStateFlow()

    private val _driverLocation = MutableStateFlow<Location?>(null)
    val driverLocation = _driverLocation.asStateFlow()

    fun trackRide(rideId: String) {
        viewModelScope.launch {
            // Observe ride status changes
            rideRepository.observeRide(rideId)
                .collect { ride ->
                    _rideState.value = when (ride.status) {
                        RideStatus.REQUESTED -> RideState.Searching
                        RideStatus.ACCEPTED -> RideState.DriverAssigned(ride)
                        RideStatus.ARRIVED -> RideState.DriverArrived(ride)
                        RideStatus.IN_PROGRESS -> RideState.InProgress(ride)
                        RideStatus.COMPLETED -> RideState.Completed(ride)
                        RideStatus.CANCELLED -> RideState.Cancelled
                    }

                    // Track driver location if ride is active
                    if (ride.driverId != null &&
                        ride.status in listOf(
                            RideStatus.ACCEPTED,
                            RideStatus.ARRIVED,
                            RideStatus.IN_PROGRESS
                        )
                    ) {
                        trackDriverLocation(ride.driverId)
                    }
                }
        }
    }

    private fun trackDriverLocation(driverId: String) {
        viewModelScope.launch {
            locationRepository.observeDriverLocation(driverId)
                .collect { location ->
                    _driverLocation.value = location
                }
        }
    }
}

sealed class RideState {
    object Idle : RideState()
    object Searching : RideState()
    data class DriverAssigned(val ride: Ride) : RideState()
    data class DriverArrived(val ride: Ride) : RideState()
    data class InProgress(val ride: Ride) : RideState()
    data class Completed(val ride: Ride) : RideState()
    object Cancelled : RideState()
}
```

#### Map Integration (Google Maps)

```kotlin
@Composable
fun RideMapScreen(
    rideState: RideState,
    driverLocation: Location?,
    onRequestRide: (Location, Location) -> Unit,
    modifier: Modifier = Modifier
) {
    val cameraPositionState = rememberCameraPositionState()
    var pickupMarker by remember { mutableStateOf<LatLng?>(null) }
    var destinationMarker by remember { mutableStateOf<LatLng?>(null) }

    GoogleMap(
        modifier = modifier.fillMaxSize(),
        cameraPositionState = cameraPositionState,
        properties = MapProperties(
            isMyLocationEnabled = true
        ),
        uiSettings = MapUiSettings(
            myLocationButtonEnabled = true,
            zoomControlsEnabled = false
        )
    ) {
        // Pickup marker
        pickupMarker?.let { position ->
            Marker(
                state = MarkerState(position = position),
                title = "Pickup Location",
                icon = BitmapDescriptorFactory.defaultMarker(
                    BitmapDescriptorFactory.HUE_GREEN
                )
            )
        }

        // Destination marker
        destinationMarker?.let { position ->
            Marker(
                state = MarkerState(position = position),
                title = "Destination",
                icon = BitmapDescriptorFactory.defaultMarker(
                    BitmapDescriptorFactory.HUE_RED
                )
            )
        }

        // Driver marker (if assigned)
        if (rideState is RideState.DriverAssigned && driverLocation != null) {
            Marker(
                state = MarkerState(
                    position = LatLng(driverLocation.latitude, driverLocation.longitude)
                ),
                title = "Your Driver",
                icon = BitmapDescriptorFactory.fromResource(R.drawable.ic_car),
                rotation = driverLocation.bearing
            )

            // Draw route from driver to pickup
            val route = calculateRoute(driverLocation, pickupMarker)
            Polyline(
                points = route,
                color = Color.Blue,
                width = 10f
            )
        }

        // Route from pickup to destination
        if (pickupMarker != null && destinationMarker != null) {
            val route = calculateRoute(pickupMarker, destinationMarker)
            Polyline(
                points = route,
                color = Color.Gray,
                width = 10f
            )
        }
    }

    // Bottom sheet with ride details
    when (rideState) {
        is RideState.Searching -> SearchingDriverSheet()
        is RideState.DriverAssigned -> DriverDetailsSheet(rideState.ride)
        is RideState.InProgress -> RideInProgressSheet(rideState.ride)
        else -> PickupDestinationSelector(
            onConfirm = { pickup, destination ->
                onRequestRide(pickup, destination)
            }
        )
    }
}
```

### 4. Backend Architecture Considerations

#### Geospatial Indexing

The backend uses **Redis with Geospatial indexes** for efficient nearby driver queries:

```
GEOADD drivers:online longitude latitude driverId
GEORADIUS drivers:online longitude latitude 5 km WITHDIST
```

This allows sub-millisecond queries for finding drivers within a radius.

#### Matching Algorithm

```kotlin
// Simplified matching logic (actual implementation on backend)
class DriverMatchingService {
    fun findBestDriver(
        ride: Ride,
        availableDrivers: List<Driver>
    ): Driver? {
        return availableDrivers
            .filter { it.isAvailable }
            .filter { it.vehicleType == ride.vehicleType }
            .map { driver ->
                val distance = calculateDistance(
                    driver.currentLocation,
                    ride.pickupLocation
                )
                val eta = calculateETA(distance)
                val score = calculateScore(driver.rating, distance, eta)

                driver to score
            }
            .maxByOrNull { it.second }
            ?.first
    }

    private fun calculateScore(
        rating: Float,
        distance: Double,
        eta: Int
    ): Double {
        // Prioritize: high rating, close distance, low ETA
        return (rating * 0.4) +
               ((1.0 / (distance + 1)) * 0.3) +
               ((1.0 / (eta + 1)) * 0.3)
    }
}
```

### 5. Performance Optimizations

#### Battery Optimization

```kotlin
class AdaptiveLocationTracker @Inject constructor(
    private val fusedLocationClient: FusedLocationProviderClient,
    private val batteryManager: BatteryManager
) {
    fun getOptimalUpdateInterval(): Long {
        val batteryLevel = batteryManager.getIntProperty(
            BatteryManager.BATTERY_PROPERTY_CAPACITY
        )

        return when {
            batteryLevel > 50 -> 3000L // 3 seconds
            batteryLevel > 20 -> 5000L // 5 seconds
            else -> 10000L // 10 seconds
        }
    }

    fun adjustLocationAccuracy(): Int {
        return if (batteryLevel > 20) {
            Priority.PRIORITY_HIGH_ACCURACY
        } else {
            Priority.PRIORITY_BALANCED_POWER_ACCURACY
        }
    }
}
```

#### Network Optimization

```kotlin
class LocationBatcher @Inject constructor(
    private val apiService: ApiService
) {
    private val locationBuffer = mutableListOf<Location>()
    private val batchSize = 10

    suspend fun bufferLocation(location: Location) {
        locationBuffer.add(location)

        if (locationBuffer.size >= batchSize) {
            flushBuffer()
        }
    }

    private suspend fun flushBuffer() {
        if (locationBuffer.isNotEmpty()) {
            try {
                apiService.batchUpdateLocations(locationBuffer)
                locationBuffer.clear()
            } catch (e: Exception) {
                Log.e("Batcher", "Failed to send batch", e)
            }
        }
    }
}
```

### 6. Offline Handling

```kotlin
class OfflineRideManager @Inject constructor(
    private val rideDao: RideDao,
    private val networkMonitor: NetworkMonitor
) {
    init {
        observeNetworkChanges()
    }

    private fun observeNetworkChanges() {
        viewModelScope.launch {
            networkMonitor.isOnline
                .filter { it } // Only when online
                .collect {
                    syncPendingRides()
                }
        }
    }

    private suspend fun syncPendingRides() {
        val pendingRides = rideDao.getPendingRides()
        pendingRides.forEach { ride ->
            try {
                rideRepository.syncRide(ride)
                rideDao.markAsSynced(ride.id)
            } catch (e: Exception) {
                Log.e("Sync", "Failed to sync ride ${ride.id}", e)
            }
        }
    }
}
```

### Best Practices

1. **Location Updates**: Use FusedLocationProvider with adaptive intervals
2. **Battery Optimization**: Adjust accuracy and frequency based on battery level
3. **Offline Support**: Cache recent rides and sync when online
4. **Real-time Updates**: Use WebSocket for driver location, fallback to polling
5. **Map Optimization**: Only render visible markers, cluster when zoomed out
6. **Network Efficiency**: Batch location updates, compress data
7. **Security**: Use SSL/TLS, encrypt sensitive data, validate on backend

### Common Pitfalls

1. Not optimizing location tracking leading to battery drain
2. Polling for driver updates instead of using WebSocket
3. Loading all nearby drivers without clustering
4. Not handling offline scenarios
5. Poor map performance with too many markers
6. Inaccurate fare calculation
7. Not handling edge cases (GPS inaccuracy, network failures)

## Ответ (RU)

Проектирование приложения для вызова такси, подобного Uber, включает сложное отслеживание местоположения в реальном времени, алгоритмы подбора водителей, обработку платежей и масштабируемую архитектуру.

### 1. Основные требования

**Функциональные требования:**

*Приложение пассажира:*
- Просмотр ближайших водителей на карте
- Запрос поездки с указанием места посадки/назначения
- Просмотр предполагаемой стоимости и времени прибытия
- Отслеживание водителя в реальном времени
- Оплата в приложении
- Оценка водителя
- История поездок

*Приложение водителя:*
- Включение/выключение режима онлайн
- Получение запросов на поездки
- Принятие/отклонение поездок
- Навигация к месту посадки/назначения
- Отслеживание заработка
- Оценка пассажира

**Нефункциональные требования:**
- Обновление местоположения в реальном времени (каждые 3-5 секунд)
- Низкая задержка подбора (< 2 секунд)
- Высокая доступность (99.99%)
- Масштабируемость (миллионы одновременных пользователей)
- Точное GPS отслеживание
- Оптимизация батареи
- Офлайн функциональность

### 2. Архитектура приложения

Система построена на микросервисной архитектуре с следующими компонентами:
- Location Service - отслеживание местоположения
- Matching Service - подбор водителей
- Ride Service - управление поездками
- Payment Service - обработка платежей
- Notification Service - уведомления
- Pricing Service - расчет стоимости

### 3. Отслеживание местоположения

**LocationTracker** использует Fused Location Provider:
- Высокая точность (PRIORITY_HIGH_ACCURACY)
- Обновления каждые 3 секунды
- Минимальный интервал 1 секунда
- Фильтрация неточных координат

**Синхронизация местоположения водителя:**
- WorkManager для фоновой работы
- Debounce 3 секунды для оптимизации сети
- Пакетная отправка координат
- Обработка ошибок сети

### 4. Поиск ближайших водителей

**Geospatial запросы:**
- Радиус поиска 5 км по умолчанию
- Фильтрация по типу автомобиля
- Real-time обновления через WebSocket
- Кэширование результатов

**Backend оптимизация:**
- Redis GeoHash для быстрых геопространственных запросов
- Sub-millisecond время ответа
- Индексация по местоположению

### 5. Процесс запроса поездки

**Шаги:**
1. Расчет предполагаемой стоимости
2. Создание запроса поездки
3. Сохранение в базу данных
4. Поиск подходящего водителя
5. Уведомление водителя
6. Ожидание подтверждения

**Алгоритм подбора водителя:**
- Учет рейтинга водителя (40%)
- Расстояние до пассажира (30%)
- Предполагаемое время прибытия (30%)
- Фильтрация по типу автомобиля
- Приоритизация лучших водителей

### 6. Отслеживание поездки в реальном времени

**Состояния поездки:**
- REQUESTED - запрошена
- ACCEPTED - принята водителем
- ARRIVED - водитель прибыл
- IN_PROGRESS - в процессе
- COMPLETED - завершена
- CANCELLED - отменена

**Отслеживание:**
- WebSocket подключение для обновлений
- Анимация перемещения маркера водителя
- Отображение маршрута на карте
- ETA обновления

### 7. Интеграция с картами

**Google Maps API:**
- Отображение текущего местоположения
- Маркеры места посадки и назначения
- Маркер водителя с правильной ориентацией
- Polyline для отображения маршрута
- Автоматическое масштабирование карты

**Оптимизация:**
- Кластеризация маркеров при отдалении
- Ленивая загрузка маркеров
- Переработка неиспользуемых объектов

### 8. Оптимизация производительности

**Батарея:**
- Адаптивная частота обновлений в зависимости от уровня заряда
- Низкая точность при низком заряде
- Остановка обновлений в фоне
- Использование Doze mode

**Сеть:**
- Пакетная отправка координат (каждые 10 обновлений)
- Сжатие данных
- WebSocket вместо polling
- Кэширование данных карты

**Память:**
- Ограничение количества видимых маркеров
- Освобождение ресурсов неактивных экранов
- Оптимизация растровых изображений

### 9. Обработка офлайн режима

**Стратегия:**
- Кэширование последних поездок
- Сохранение незавершенных действий
- Автоматическая синхронизация при восстановлении сети
- Уведомление пользователя об офлайн режиме

### Лучшие практики

1. **Отслеживание местоположения**: FusedLocationProvider с адаптивными интервалами
2. **Оптимизация батареи**: Настройка точности и частоты на основе уровня заряда
3. **Офлайн поддержка**: Кэширование поездок и синхронизация при подключении
4. **Real-time обновления**: WebSocket для местоположения водителя
5. **Оптимизация карты**: Рендеринг только видимых маркеров, кластеризация
6. **Эффективность сети**: Пакетная отправка обновлений, сжатие данных

### Частые ошибки

1. Неоптимизированное отслеживание местоположения → разряд батареи
2. Polling для обновлений вместо WebSocket
3. Загрузка всех ближайших водителей без кластеризации
4. Необработка офлайн сценариев
5. Плохая производительность карты с большим количеством маркеров
6. Неточный расчет стоимости
7. Необработка граничных случаев (неточность GPS, сетевые сбои)

---

## References
- [Fused Location Provider](https://developers.google.com/location-context/fused-location-provider)
- [Google Maps Android API](https://developers.google.com/maps/documentation/android-sdk)
- [Redis Geospatial](https://redis.io/commands/geoadd/)
- [WorkManager Guide](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Battery Optimization](https://developer.android.com/topic/performance/power)

## Related Questions
- How to optimize location tracking in Android?
- What is geospatial indexing?
- How to implement real-time tracking with WebSocket?
- How to integrate Google Maps in Android?
- What is the best way to handle background location updates?
