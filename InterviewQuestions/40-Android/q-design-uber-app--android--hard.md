---
id: 20251020-200000
title: Design Uber App / Проектирование приложения Uber
aliases: [Design Uber App, Проектирование приложения Uber, Uber Android architecture, Архитектура Uber Android]
topic: android
subtopics: [location, networking-http, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-performance-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-deep-link-vs-app-link--android--medium, c-microservices, c-real-time-systems]
sources: [https://developers.google.com/location-context/fused-location-provider]
created: 2025-10-20
updated: 2025-10-28
tags: [android/location, android/networking-http, android/service, difficulty/hard, maps, realtime]
---

# Вопрос (RU)
> Как спроектировать приложение Uber для Android?

# Question (EN)
> How to design Uber for Android?

---

## Ответ (RU)

Uber включает: отслеживание местоположения в реальном времени, подбор водителей, расчёт стоимости, маршрутизацию, оплату, масштабирование и офлайн-устойчивость.

### Требования

**Функциональные:**
- Пассажир: карта ближайших водителей, запрос поездки, ETA/стоимость, трекинг, оплата, история.
- Водитель: онлайн/офлайн, заявки, принятие/отклонение, навигация, заработок.

**Нефункциональные:** обновления 3–5s, матчинг <2s, высокая доступность, точность GPS, экономия батареи, офлайн.

### Архитектура

Android клиент (локация, WebSocket, карты, офлайн очередь) → API Gateway → микросервисы (Location/Matching/Ride/Payment/Notification/Pricing) → DB, кэш, геопространственная БД, очереди.

### Клиент Android: Ключевые Потоки

**1. Локация**
FusedLocationProvider, адаптивные интервалы/точность, backoff при низком заряде.

```kotlin
// ✅ Location updates with adaptive priority
val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 3000L)
  .setMinUpdateIntervalMillis(1000L)
  .build()

fusedLocationClient.requestLocationUpdates(req, callback, Looper.getMainLooper())
```

**2. Синхронизация**
Дебаунс/батчинг, фон через WorkManager, восстановление при онлайне.

```kotlin
// ✅ Debounce + background sync
locationFlow
  .filterNotNull()
  .debounce(3000)
  .onEach { repo.updateLocation(it) }
  .launchIn(viewModelScope)
```

**3. Поиск водителей**
Начальный REST + подписка WebSocket, фильтры по типу авто, кластеризация маркеров.

```kotlin
// ✅ REST seed + WebSocket stream
repo.getNearbyDrivers(location)
  .onStart { emit(fetchInitial()) }
  .combine(websocket.driverUpdates()) { initial, updates ->
    initial.merge(updates)
  }
```

**4. Запрос поездки**
Оценка тарифа → создание ride → матчинг → подтверждение → трекинг.

```kotlin
// ✅ Request ride with essential fields
rideRepo.create(
  Ride(
    pickup = currentLocation,
    destination = destLocation,
    vehicleType = vehicleType,
    createdAt = now()
  )
)
```

**5. Трекинг поездки**
Состояния (REQUESTED→COMPLETED), маршрут и ETA, обновления по WebSocket.

```kotlin
// ✅ Combine ride state + driver location
rideRepo.observeRide(rideId)
  .combine(locationRepo.observeDriver(driverId)) { ride, driverLoc ->
    RideTracking(ride, driverLoc)
  }
```

### Сервер: Архитектурный Анализ

**Границы сервисов:**
- **Location Service**: принимает координаты, валидирует физику движения (скорость <150 km/h), обновляет геоиндекс, публикует события в Kafka. Хранит только горячие данные (последние 30 минут).
- **Matching Service**: выполняет геопоиск доступных водителей в радиусе, применяет scoring (рейтинг·0.4 + 1/distance·0.3 + 1/ETA·0.3), резервирует водителя с optimistic lock, отправляет push. Обрабатывает accept/reject с timeout.
- **Ride Service**: управляет FSM поездки (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), хранит аудит переходов, обеспечивает идемпотентность через requestId, координирует с Payment через события.
- **Pricing Service**: вычисляет базовый тариф по расстоянию/времени, применяет surge multiplier, генерирует котировку с TTL (2-5 минут), привязывает quoteId к ride.
- **Payment Service**: pre-authorization при запросе, charge при завершении, refund при отмене, PCI DSS compliance.

**Доменные модели:**
- **Ride**: id, riderId, driverId, pickup/dest (lat/lng), quoteId, fareAmount, vehicleType, timestamps, status (FSM).
- **Driver**: id, status (ONLINE/OFFLINE/BUSY), currentLocation, rating, completedRides, acceptanceRate.
- **Quote**: id, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil, vehicleType.

**Хранение данных:**
- **PostgreSQL**: rides, payments с ACID, партиционирование по created_at, индексы на rider_id/driver_id/status, репликация master-slave.
- **Redis Geo**: активные водители (TTL 5 мин), GEOADD/GEORADIUS для мгновенного поиска.
- **Redis Cache**: котировки (TTL 5 мин), session tokens, rate limit counters.
- **S3 + Parquet**: архив завершённых поездок, траектории для ML/аналитики.

**Согласованность:**
- **Outbox pattern**: событие в локальную таблицу outbox в той же транзакции, отдельный процесс публикует в Kafka (at-least-once).
- **Идемпотентность**: requestId от клиента, unique constraint на (riderId, requestId) для create-ride.
- **Saga**: Ride → PAYMENT_REQUESTED → Payment → PAYMENT_COMPLETED/FAILED → Ride. При FAILED: компенсация (отмена поездки, возврат водителя).

**Алгоритм матчинга:**
- **Эвристический**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3, сортировка, топ-1. O(n log n), <100ms.
- **Оптимальный (batch)**: Hungarian Algorithm для 50-100 поездок раз в 10-30 сек. Trade-off: задержка vs общее ETA.

**Surge pricing:**
- Зонирование: гексагоны H3, multiplier = min(max_cap, base + α·(demand/supply - threshold)).
- Демпфер (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge.
- Привязка quoteId к surge на момент запроса, валидация при создании ride.

**Отказоустойчивость:**
- WebSocket → long-polling fallback при disconnect.
- Redis Geo → PostGIS fallback (100-500ms vs <10ms).
- Retry с jitter, circuit breaker к внешним API (Maps, Payment).
- Rate limiting: token bucket per riderId/driverId (10 req/min для ride, 100/min для location).

**Безопасность:**
- JWT с короткими TTL (15 мин), refresh token.
- TLS, координаты шифруются AES-256 в БД (KMS).
- Retention: 30 дней, затем агрегация для аналитики. GDPR compliance.
- Валидация физики движения, fingerprinting устройств, блокировка mock location.

**Наблюдаемость:**
- Метрики: P99 matching latency <2s, match success >95%, ETA accuracy ±20%, battery ≤5%/hour, WebSocket uptime >99.9%.
- Distributed tracing (Jaeger/Zipkin), Prometheus + Alertmanager, structured logging (ELK).

**Масштабирование:**
- Шардирование по географическим регионам (US-West, EU, APAC).
- Sticky routing для consistency (L7 load balancer).
- Multi-region для GDPR/data residency.
- CDN для map tiles, Kubernetes HPA.

### Оптимизация

- **Батарея**: адаптивная точность и частота, пауза в фоне, Doze-aware.
- **Сеть**: батчинг координат, компрессия, WebSocket вместо polling.
- **Карты**: кластеризация, рендер только видимых объектов.

### Офлайн

Кэширование незавершенных действий, очередь синхронизации, авто-ресенд при восстановлении сети.

---

## Answer (EN)

Uber involves realtime location tracking, driver matching, pricing, routing, payments, scale, and offline resilience.

### Requirements

**Functional:**
- Rider: nearby drivers map, request ride, ETA/fare, tracking, payment, history.
- Driver: online/offline toggle, ride requests, accept/reject, navigation, earnings.

**Non-functional:** 3–5s updates, <2s matching, high availability, GPS accuracy, battery efficiency, offline support.

### Architecture

Android client (location, WebSocket, maps, offline queue) → API Gateway → microservices (Location/Matching/Ride/Payment/Notification/Pricing) → DB, cache, geospatial DB, queues.

### Android Client: Key Flows

**1. Location**
FusedLocationProvider, adaptive intervals/accuracy, backoff on low battery.

**2. Sync**
Debounce/batching, background via WorkManager, resume on reconnect.

**3. Nearby Drivers**
REST seed + WebSocket stream, filters by vehicle type, marker clustering.

**4. Request Ride**
Fare estimate → create ride → matching → confirmation → tracking.

**5. Track Ride**
Ride FSM (REQUESTED→COMPLETED), route + ETA via Maps, WebSocket updates.

### Server: Architecture Analysis

**Service boundaries:**
- **Location Service**: accepts coordinates, validates movement physics (speed <150 km/h), updates geo-index, publishes events to Kafka. Stores only hot data (last 30 minutes).
- **Matching Service**: performs geo-search for available drivers in radius, applies scoring (rating·0.4 + 1/distance·0.3 + 1/ETA·0.3), reserves driver with optimistic lock, sends push. Handles accept/reject with timeout.
- **Ride Service**: manages ride FSM (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), stores audit trail, ensures idempotency via requestId, coordinates with Payment through events.
- **Pricing Service**: calculates base fare by distance/time, applies surge multiplier, generates quote with TTL (2-5 minutes), binds quoteId to ride.
- **Payment Service**: pre-authorization on request, charge on completion, refund on cancellation, PCI DSS compliance.

**Domain models:**
- **Ride**: id, riderId, driverId, pickup/dest (lat/lng), quoteId, fareAmount, vehicleType, timestamps, status (FSM).
- **Driver**: id, status (ONLINE/OFFLINE/BUSY), currentLocation, rating, completedRides, acceptanceRate.
- **Quote**: id, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil, vehicleType.

**Data storage:**
- **PostgreSQL**: rides, payments with ACID, partitioning by created_at, indexes on rider_id/driver_id/status, master-slave replication.
- **Redis Geo**: active drivers (TTL 5 min), GEOADD/GEORADIUS for instant search.
- **Redis Cache**: quotes (TTL 5 min), session tokens, rate limit counters.
- **S3 + Parquet**: archive completed rides, trajectories for ML/analytics.

**Consistency:**
- **Outbox pattern**: write event to local outbox table in same transaction, separate process publishes to Kafka (at-least-once).
- **Idempotency**: requestId from client, unique constraint on (riderId, requestId) for create-ride.
- **Saga**: Ride → PAYMENT_REQUESTED → Payment → PAYMENT_COMPLETED/FAILED → Ride. On FAILED: compensation (cancel ride, return driver).

**Matching algorithm:**
- **Heuristic**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3, sort, pick top-1. O(n log n), <100ms.
- **Optimal (batch)**: Hungarian Algorithm for 50-100 rides every 10-30 sec. Trade-off: delay vs overall ETA.

**Surge pricing:**
- Zoning: H3 hexagons, multiplier = min(max_cap, base + α·(demand/supply - threshold)).
- Dampener (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge.
- Bind quoteId to surge at request time, validate on ride creation.

**Resilience:**
- WebSocket → long-polling fallback on disconnect.
- Redis Geo → PostGIS fallback (100-500ms vs <10ms).
- Retry with jitter, circuit breaker to external APIs (Maps, Payment).
- Rate limiting: token bucket per riderId/driverId (10 req/min for ride, 100/min for location).

**Security:**
- JWT with short TTL (15 min), refresh token.
- TLS, coordinates encrypted AES-256 in DB (KMS).
- Retention: 30 days, then aggregated for analytics. GDPR compliance.
- Movement physics validation, device fingerprinting, block mock location.

**Observability:**
- Metrics: P99 matching latency <2s, match success >95%, ETA accuracy ±20%, battery ≤5%/hour, WebSocket uptime >99.9%.
- Distributed tracing (Jaeger/Zipkin), Prometheus + Alertmanager, structured logging (ELK).

**Scalability:**
- Sharding by geographic regions (US-West, EU, APAC).
- Sticky routing for consistency (L7 load balancer).
- Multi-region for GDPR/data residency.
- CDN for map tiles, Kubernetes HPA.

### Optimization

- **Battery**: adaptive precision/frequency, pause in background, Doze-aware.
- **Network**: batch coordinates, compression, WebSocket over polling.
- **Maps**: clustering, render only visible objects.

### Offline

Cache incomplete actions, sync queue, auto-resend on network restore.

---

## Follow-ups

- How to implement surge pricing fairly and at scale?
- How to detect and mitigate driver/rider fraud (GPS spoofing, fake rides)?
- How to design fallback when WebSocket is unavailable?
- How to optimize battery for continuous location tracking?
- How to handle cross-region rides (data residency, latency)?

## References

- [Fused Location Provider](https://developers.google.com/location-context/fused-location-provider)
- [Google Maps Android SDK](https://developers.google.com/maps/documentation/android-sdk)
- [Redis Geo Commands](https://redis.io/commands/geoadd/)
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Battery Performance](https://developer.android.com/topic/performance/power)

## Related Questions

### Prerequisites (Easier)
- [[q-data-sync-unstable-network--android--hard]]
- [[q-deep-link-vs-app-link--android--medium]]

### Related (Same Level)
- [[q-design-instagram-stories--android--hard]]
- [[q-android-performance-optimization--android--medium]]

### Advanced Concepts
- [[c-microservices]]
- [[c-real-time-systems]]
