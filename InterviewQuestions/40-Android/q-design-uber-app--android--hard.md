---
id: 20251020-200000
title: Design Uber App / Проектирование приложения Uber
aliases:
  - Design Uber App
  - Проектирование приложения Uber
topic: android
subtopics:
  - location
  - networking-http
  - service
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
source: https://developers.google.com/location-context/fused-location-provider
source_note: Android Fused Location Provider overview
status: reviewed
moc: moc-android
related:
  - q-data-sync-unstable-network--android--hard
  - q-deep-link-vs-app-link--android--medium
  - q-android-performance-optimization--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
  - android/location
  - android/networking-http
  - android/service
  - maps
  - realtime
  - difficulty/hard
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
- Пассажир: карта ближайших водителей, запрос поездки, ETA/стоимость, трекинг, оплата, оценка, история.
- Водитель: онлайн/офлайн, заявки, принятие/отклонение, навигация, заработок, оценка.

**Нефункциональные:** real-time обновления 3–5s, матчинг <2s, высокая доступность, масштабируемость, точность GPS, бережная батарея, офлайн.

### Архитектура (высокоуровнево)
Клиент Android (локация, WebSocket, карты, офлайн очередь) → API Gateway → микросервисы (Location/Matching/Ride/Payment/Notification/Pricing) → DB (метаданные), кэш, геопространственная БД, платежи, Maps, очереди.

### Клиент Android: ключевые потоки
1) Локация: FusedLocationProvider, адаптивные интервалы/точность, backoff при батарее.
2) Синхронизация: дебаунс/батчинг, фон через WorkManager, восстановление при онлайне.
3) Поиск водителей: начальный REST + подписка WebSocket, фильтры по типу авто, кластеризация маркеров.
4) Запрос поездки: оценка тарифа → создание ride → матчинг → подтверждение → трекинг.
5) Трекинг поездки: состояния (REQUESTED→COMPLETED), маршрут и ETA, обновления по WebSocket.

```kotlin
// Location updates (essential)
val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 3000L)
  .setMinUpdateIntervalMillis(1000L)
  .build()
```

```kotlin
// Debounce + send in background
locationFlow.filterNotNull().debounce(3000).onEach { repo.update(it) }
```

```kotlin
// Initial REST + real-time updates
repo.getNearbyREST(loc).onStart { emit(fetch()) }.mergeWith(ws.stream())
```

```kotlin
// Request ride (essential fields)
rideRepo.create(Ride(pickup, dest, vehicleType, createdAt = now()))
```

```kotlin
// Observe ride + driver location
rideRepo.observe(rideId).combine(locRepo.observe(driverId)) { r, d -> r to d }
```

```kotlin
// Minimal map usage hints: markers + polylines; cluster when zoomed out
```

### Сервер: геопоиск и матчинг
- Геопоиск: Redis Geo / PostGIS; индекс по координатам; query по радиусу.
- Матчинг: score по рейтингу/дистанции/ETA, SLA <2s, идемпотентность.
- Очереди: Kafka для событий; outbox для согласованности.

### Архитектурный анализ

**Границы сервисов:**
- **Location Service**: принимает координаты от водителей (stream или batch), валидирует физику движения (скорость/ускорение), обновляет геоиндекс, публикует события в Kafka. Хранит только горячие данные (последние N минут).
- **Matching Service**: получает запрос поездки, выполняет геопоиск доступных водителей в радиусе, применяет scoring/ranking, резервирует водителя (optimistic lock), отправляет push-уведомление. Обрабатывает accept/reject от водителя с timeout.
- **Ride Service**: управляет FSM поездки (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), хранит полный аудит переходов, обеспечивает идемпотентность команд через уникальные ключи, координирует с Payment через событийную хореографию.
- **Pricing Service**: вычисляет базовый тариф по расстоянию/времени, применяет surge multiplier по зонам, генерирует котировку с TTL (2-5 минут), привязывает quoteId к ride для защиты от арбитража.
- **Payment Service**: выполняет pre-authorization при запросе, charge при завершении, refund при отмене, интегрируется с платёжными провайдерами (Stripe/PayPal), обеспечивает PCI DSS compliance.
- **Notification Service**: отправляет push (FCM/APNS), SMS (Twilio), email; поддерживает приоритизацию (critical: ride status → info: promo), retry с backoff, unsubscribe management.
- **Profile Service**: управляет KYC водителей/пассажиров, информацией об автомобилях, рейтингами, документами (права, страховка), верификацией.

**Доменные модели:**
- **Ride**: FSM с переходами (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), поля: id, riderId, driverId, pickupLat/Lng, destLat/Lng, quoteId, fareAmount, currency, vehicleType, timestamps (created/accepted/started/ended), cancellationReason, rating.
- **Driver**: id, profileId, status (ONLINE/OFFLINE/BUSY), availability, currentLat/Lng, lastSeen, vehicleId, rating, completedRides, acceptanceRate, cancellationRate.
- **Quote**: id, riderId, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil (TTL), distanceMeters, durationSeconds, vehicleType.
- **SurgeZone**: zoneId, polygon (GeoJSON), currentMultiplier (1.0-3.0), demand, supply, computedAt, TTL (5-15 минут).

**Хранение данных:**
- **Транзакционная БД (PostgreSQL)**: таблицы rides, payments, refunds с ACID гарантиями. Партиционирование по created_at для горячих/холодных данных. Индексы на rider_id, driver_id, status. Репликация master-slave для чтения.
- **Геопространственная БД (Redis Geo/PostGIS)**: Redis Geo для активных водителей (TTL 5 минут, автоочистка), команды GEOADD/GEORADIUS для мгновенного поиска. PostGIS как холодный fallback и для аналитики маршрутов.
- **Кэш (Redis)**: котировки (key: quoteId, TTL 5 мин), онлайн-кольца водителей (set: online_drivers, TTL 10 сек), session tokens, rate limit counters.
- **Холодное хранилище (S3 + Parquet)**: архив завершённых поездок, траектории (для ML/аналитики), логи, для Spark/Athena queries.

**Согласованность и транзакции:**
- **Outbox pattern**: сервисы записывают событие в локальную таблицу outbox в той же транзакции, что и бизнес-операцию. Отдельный процесс читает outbox и публикует в Kafka (at-least-once delivery).
- **Идемпотентность**: клиент генерирует requestId, сервис проверяет дубликаты перед выполнением. Для create-ride: unique constraint на (riderId, requestId). Для charge: idempotency key в Payment Service.
- **Saga (хореография)**: Ride → PAYMENT_REQUESTED event → Payment → PAYMENT_COMPLETED/FAILED → Ride. При PAYMENT_FAILED: автоматическая компенсация (отмена поездки, возврат водителя в пул).
- **Source of Truth**: Ride Service владеет состоянием поездки. Другие сервисы запрашивают через API или подписываются на события.

**Алгоритм матчинга:**
- **Эвристический scoring (низкая латентность)**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3. Сортировка по убыванию score, выбор топ-1. Время: O(n log n) для n водителей, обычно <100ms для радиуса 5км.
- **Оптимальное назначение (batch, высокое качество)**: во время пиков собираем batch запросов (50-100 поездок), строим граф (riders → drivers), применяем Hungarian Algorithm или Min-Cost-Flow для глобальной оптимизации. Время: O(n³) или O(n² log n), выполняется раз в 10-30 секунд. Trade-off: задержка матчинга vs общее ETA.
- **Fairness**: ротация водителей, штрафы за отклонения, бонусы за дальние поездки, ограничение consecutive rides для предотвращения выгорания.

**Surge pricing:**
- **Зонирование**: город разбит на гексагоны (H3 resolution 7-9, ~0.5-1км²). Каждая зона: demand (pending requests), supply (available drivers).
- **Вычисление**: multiplier = min(max_cap, base + α·(demand/supply - threshold)). Демпфер (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge для плавности.
- **Котировка**: привязка quoteId к surge на момент запроса. При создании ride проверяем TTL котировки и validируем surge не изменился >10%, иначе перерасчёт.
- **Анти-арбитраж**: блокировка множественных запросов от одного riderId в короткий промежуток, require quoteId для create-ride.

**Отказоустойчивость:**
- **WebSocket → Polling fallback**: при disconnect клиент переключается на long-polling с интервалом 5-10 сек. Сервер детектирует WS failures через heartbeat и переводит клиентов в fallback mode.
- **Redis Geo → PostGIS fallback**: если Redis недоступен, геопоиск выполняется через PostGIS (slower, ~100-500ms vs <10ms). Health check мониторит Redis latency.
- **Retry с jitter**: экспоненциальный backoff с jitter для избежания thundering herd: delay = base·2^attempt + random(0, jitter).
- **Circuit breaker**: к внешним API (Maps, Payment). States: CLOSED → OPEN (после N failures) → HALF_OPEN (test request) → CLOSED/OPEN. Timeout в OPEN: 30-60 сек.
- **Rate limiting**: token bucket per riderId/driverId (10 requests/min для ride creation, 100/min для location updates). Distributed counter в Redis.

**Безопасность и приватность:**
- **Scoped tokens**: JWT с минимальными claims (riderId/driverId, role, exp). Короткий TTL (15 мин), refresh token для продления.
- **Шифрование**: TLS 1.3 для transit, координаты шифруются AES-256 в БД (envelope encryption через KMS).
- **Retention**: координаты хранятся 30 дней, после агрегируются для аналитики (уровень зоны, не точные координаты). GDPR compliance: right to erasure.
- **Spoofing mitigation**: физическая валидация (speed <150 km/h, acceleration <10 m/s²), fingerprinting устройств, trust score на базе истории, детект jump >5км без движения, блокировка mock location apps.

**Наблюдаемость и SLO:**
- **Метрики**: P50/P95/P99 matching latency (цель <2s at P99), match success rate (>95%), ETA accuracy (±20% для 80% поездок), location error rate (<1%), battery drain (≤5%/hour), WebSocket uptime (>99.9%).
- **Distributed tracing**: Jaeger/Zipkin для сквозной трассировки request → gateway → Location/Matching/Ride → DB/Cache/Kafka. Span tags: riderId, driverId, region.
- **SLO alerting**: Prometheus + Alertmanager. Alert if matching_latency_p99 > 2s for 5 consecutive minutes OR match_success_rate < 95% for 10 minutes.
- **Logging**: structured JSON logs (ELK stack), level: ERROR для failures, WARN для degraded mode, INFO для ключевых событий (ride created/completed).

**Масштабирование:**
- **Горизонтальное шардирование**: Location/Matching сервисы шардируются по географическим регионам (US-West, US-East, EU, APAC). Ride/Payment партиционируются по riderId hash.
- **Sticky routing**: запросы одного riderId направляются на тот же Matching instance для consistency (L7 load balancer с cookie-based affinity).
- **Data residency**: GDPR/локальные законы требуют хранения данных в юрисдикции. Multi-region deployment с репликацией между регионами для DR.
- **CDN для Maps**: тайлы карт кэшируются в CloudFront/Cloudflare, уменьшение нагрузки на Google Maps API на 80-90%.
- **Auto-scaling**: Kubernetes HPA на базе CPU (70% threshold) и custom metrics (pending rides queue depth >100).

### Оптимизация
- Батарея: адаптивная точность и частота; пауза в фоне; Doze-aware.
- Сеть: батчинг координат, компрессия, WebSocket вместо polling.
- Память/карты: кластеризация, рендер только видимых объектов.

### Офлайн
- Кэширование незавершенных действий; очередь синхронизации; авто-ресенд.

## Ответ (EN)

Uber involves realtime location, driver matching, pricing, routing, payments, scale, and offline resilience.

### Requirements
- Rider: nearby drivers, request, ETA/fare, tracking, pay, rate, history.
- Driver: online/offline, requests, accept/reject, navigate, earnings, rate.
- Non-functional: 3–5s updates, <2s matching, availability, scalability, GPS accuracy, battery, offline.

### Architecture (high-level)
- Android client → API → microservices (Location/Matching/Ride/Payment/Pricing/Notification) → DB/cache/geo/queues/CDN/Maps.

### Android client key flows
1) Location: Fused provider, adaptive intervals/accuracy.
2) Sync: debounce/batching, background, resume on reconnect.
3) Nearby: REST seed + WebSocket stream.
4) Request: fare estimate → create → match → confirm → track.
5) Tracking: ride FSM, route + ETA via Maps, WebSocket updates.

### Server geo & matching
- Geo index (Redis Geo/PostGIS); radius queries; score by rating/distance/ETA.

### Architecture analysis

**Service boundaries:**
- **Location Service**: accepts driver coordinates (stream/batch), validates movement physics (speed/acceleration), updates geo-index, publishes events to Kafka. Stores only hot data (last N minutes).
- **Matching Service**: receives ride request, performs geo-search for available drivers in radius, applies scoring/ranking, reserves driver (optimistic lock), sends push notification. Handles driver accept/reject with timeout.
- **Ride Service**: manages ride FSM (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), stores full audit trail, ensures command idempotency via unique keys, coordinates with Payment through event choreography.
- **Pricing Service**: calculates base fare by distance/time, applies surge multiplier by zones, generates quote with TTL (2-5 minutes), binds quoteId to ride for anti-arbitrage protection.
- **Payment Service**: executes pre-authorization on request, charge on completion, refund on cancellation, integrates with payment providers (Stripe/PayPal), ensures PCI DSS compliance.
- **Notification Service**: sends push (FCM/APNS), SMS (Twilio), email; supports prioritization (critical: ride status → info: promo), retry with backoff, unsubscribe management.
- **Profile Service**: manages driver/rider KYC, vehicle information, ratings, documents (license, insurance), verification.

**Domain models:**
- **Ride**: FSM with transitions (REQUESTED→ACCEPTED→ARRIVED→IN_PROGRESS→COMPLETED/CANCELLED), fields: id, riderId, driverId, pickupLat/Lng, destLat/Lng, quoteId, fareAmount, currency, vehicleType, timestamps (created/accepted/started/ended), cancellationReason, rating.
- **Driver**: id, profileId, status (ONLINE/OFFLINE/BUSY), availability, currentLat/Lng, lastSeen, vehicleId, rating, completedRides, acceptanceRate, cancellationRate.
- **Quote**: id, riderId, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil (TTL), distanceMeters, durationSeconds, vehicleType.
- **SurgeZone**: zoneId, polygon (GeoJSON), currentMultiplier (1.0-3.0), demand, supply, computedAt, TTL (5-15 minutes).

**Data storage:**
- **Transactional DB (PostgreSQL)**: tables rides, payments, refunds with ACID guarantees. Partitioning by created_at for hot/cold data. Indexes on rider_id, driver_id, status. Master-slave replication for reads.
- **Geospatial DB (Redis Geo/PostGIS)**: Redis Geo for active drivers (TTL 5 min, auto-cleanup), GEOADD/GEORADIUS commands for instant search. PostGIS as cold fallback and for route analytics.
- **Cache (Redis)**: quotes (key: quoteId, TTL 5 min), online driver rings (set: online_drivers, TTL 10 sec), session tokens, rate limit counters.
- **Cold storage (S3 + Parquet)**: archive of completed rides, trajectories (for ML/analytics), logs, for Spark/Athena queries.

**Consistency and transactions:**
- **Outbox pattern**: services write event to local outbox table in same transaction as business operation. Separate process reads outbox and publishes to Kafka (at-least-once delivery).
- **Idempotency**: client generates requestId, service checks duplicates before execution. For create-ride: unique constraint on (riderId, requestId). For charge: idempotency key in Payment Service.
- **Saga (choreography)**: Ride → PAYMENT_REQUESTED event → Payment → PAYMENT_COMPLETED/FAILED → Ride. On PAYMENT_FAILED: automatic compensation (cancel ride, return driver to pool).
- **Source of Truth**: Ride Service owns ride state. Other services query via API or subscribe to events.

**Matching algorithm:**
- **Heuristic scoring (low latency)**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3. Sort by descending score, pick top-1. Time: O(n log n) for n drivers, typically <100ms for 5km radius.
- **Optimal assignment (batch, high quality)**: during peaks collect batch of requests (50-100 rides), build graph (riders → drivers), apply Hungarian Algorithm or Min-Cost-Flow for global optimization. Time: O(n³) or O(n² log n), executed every 10-30 seconds. Trade-off: matching delay vs overall ETA.
- **Fairness**: driver rotation, penalties for rejections, bonuses for long trips, limit on consecutive rides to prevent burnout.

**Surge pricing:**
- **Zoning**: city divided into hexagons (H3 resolution 7-9, ~0.5-1km²). Each zone: demand (pending requests), supply (available drivers).
- **Computation**: multiplier = min(max_cap, base + α·(demand/supply - threshold)). Dampener (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge for smoothness.
- **Quote**: bind quoteId to surge at request time. On ride creation verify quote TTL and validate surge hasn't changed >10%, else recalculate.
- **Anti-arbitrage**: block multiple requests from same riderId in short interval, require quoteId for create-ride.

**Resilience:**
- **WebSocket → Polling fallback**: on disconnect client switches to long-polling with 5-10 sec interval. Server detects WS failures via heartbeat and moves clients to fallback mode.
- **Redis Geo → PostGIS fallback**: if Redis unavailable, geo-search executes through PostGIS (slower, ~100-500ms vs <10ms). Health check monitors Redis latency.
- **Retry with jitter**: exponential backoff with jitter to avoid thundering herd: delay = base·2^attempt + random(0, jitter).
- **Circuit breaker**: to external APIs (Maps, Payment). States: CLOSED → OPEN (after N failures) → HALF_OPEN (test request) → CLOSED/OPEN. Timeout in OPEN: 30-60 sec.
- **Rate limiting**: token bucket per riderId/driverId (10 requests/min for ride creation, 100/min for location updates). Distributed counter in Redis.

**Security and privacy:**
- **Scoped tokens**: JWT with minimal claims (riderId/driverId, role, exp). Short TTL (15 min), refresh token for extension.
- **Encryption**: TLS 1.3 for transit, coordinates encrypted AES-256 in DB (envelope encryption via KMS).
- **Retention**: coordinates stored 30 days, then aggregated for analytics (zone level, not exact coords). GDPR compliance: right to erasure.
- **Spoofing mitigation**: physics validation (speed <150 km/h, acceleration <10 m/s²), device fingerprinting, trust score based on history, detect jump >5km without movement, block mock location apps.

**Observability and SLOs:**
- **Metrics**: P50/P95/P99 matching latency (target <2s at P99), match success rate (>95%), ETA accuracy (±20% for 80% rides), location error rate (<1%), battery drain (≤5%/hour), WebSocket uptime (>99.9%).
- **Distributed tracing**: Jaeger/Zipkin for end-to-end tracing request → gateway → Location/Matching/Ride → DB/Cache/Kafka. Span tags: riderId, driverId, region.
- **SLO alerting**: Prometheus + Alertmanager. Alert if matching_latency_p99 > 2s for 5 consecutive minutes OR match_success_rate < 95% for 10 minutes.
- **Logging**: structured JSON logs (ELK stack), level: ERROR for failures, WARN for degraded mode, INFO for key events (ride created/completed).

**Scalability:**
- **Horizontal sharding**: Location/Matching services sharded by geographic regions (US-West, US-East, EU, APAC). Ride/Payment partitioned by riderId hash.
- **Sticky routing**: requests from same riderId routed to same Matching instance for consistency (L7 load balancer with cookie-based affinity).
- **Data residency**: GDPR/local laws require data storage in jurisdiction. Multi-region deployment with cross-region replication for DR.
- **CDN for Maps**: map tiles cached in CloudFront/Cloudflare, reducing Google Maps API load by 80-90%.
- **Auto-scaling**: Kubernetes HPA based on CPU (70% threshold) and custom metrics (pending rides queue depth >100).

### Optimization
- Battery/network/maps best practices as RU.

### Offline
- Queue + local cache + auto-resend.

## Follow-ups
- How to implement surge pricing fairly and at scale?
- How to detect and mitigate driver/rider fraud?
- How to design fallback when WebSocket is unavailable?

## References
- https://developers.google.com/location-context/fused-location-provider
- https://developers.google.com/maps/documentation/android-sdk
- https://redis.io/commands/geoadd/
- https://developer.android.com/topic/libraries/architecture/workmanager
- https://developer.android.com/topic/performance/power

## Related Questions
- [[q-design-instagram-stories--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]
- [[q-deep-link-vs-app-link--android--medium]]
