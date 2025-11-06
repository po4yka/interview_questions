---
id: android-445
title: Design Uber App / Проектирование приложения Uber
aliases: [Design Uber App, Проектирование приложения Uber]
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
status: reviewed
moc: moc-android
related:
  - q-data-sync-unstable-network--android--hard
  - q-design-instagram-stories--android--hard
created: 2025-10-20
updated: 2025-11-02
tags: [android/location, android/networking-http, android/service, architecture, difficulty/hard, location, maps, networking, performance, realtime, system-design, websocket]
---

# Вопрос (RU)

> Как спроектировать приложение Uber для Android?

## Краткая Версия

Спроектируйте Android‑приложение для заказа поездок в мегаполисе. Система должна поддерживать отслеживание местоположения в реальном времени, подбор ближайших водителей, расчет стоимости, маршрутизацию, оплату и работу в условиях прерывистой сети.

## Подробная Версия

Спроектируйте полноценное приложение Uber для Android со следующими требованиями:

**Производительность:**
- Взаимодействие с картой: <200мс от input до render
- Холодный старт: <2.5с (p95) на Pixel‑классе устройств
- Батарея: <3%/ч в foreground‑трекинге и <1%/ч в background ожидании

**Функциональность:**
- Отслеживание местоположения в реальном времени с адаптивной частотой
- Подбор ближайших водителей с геопространственным поиском
- Машина состояний поездки (запрос → матчинг → поездка → завершение)
- Realtime канал для обновлений ETA водителя и статуса поездки

**Надежность:**
- Поддержка прерывистой сети (offline-first подход)
- План фонового выполнения согласно правилам Android 14+
- Fallback механизмы без зависимости от Google Play Services

**Безопасность:**
- Анти‑абьюз и integrity проверки (обнаружение mock location, спуфинга)
- Валидация физики движения для предотвращения мошенничества

**Операции:**
- Наблюдаемость (метрики производительности, latency, батареи)
- Стратегия поэтапного релиза (staged rollout) с автоматическим откатом

# Question (EN)

> How to design Uber for Android?

## Short Version

Design an Android app for requesting rides in a tier‑1 city. The system should support real-time location tracking, nearby driver matching, fare calculation, routing, payment processing, and operation under intermittent connectivity.

## Detailed Version

Design a complete Uber Android app with the following requirements:

**Performance:**
- Map interaction: <200ms from input to render
- Cold start: <2.5s (p95) on Pixel‑class devices
- Battery: <3%/hr foreground tracking and <1%/hr background waiting

**Functionality:**
- Real-time location tracking with adaptive frequency
- Nearby driver matching with geospatial search
- Trip state machine (request → matching → trip → completion)
- Realtime channel for driver ETA updates and trip status

**Reliability:**
- Support intermittent connectivity (offline-first approach)
- Background execution plan per Android 14+ rules
- Fallback mechanisms without Google Play Services dependency

**Security:**
- Anti‑abuse and integrity checks (mock location detection, spoofing prevention)
- Movement physics validation to prevent fraud

**Operations:**
- Observability (performance metrics, latency, battery)
- Staged rollout strategy with automatic rollback

## Ответ (RU)

`Uber` — комплексная система для заказа поездок, включающая: отслеживание местоположения в реальном времени, подбор ближайших водителей через геопространственный поиск, расчёт стоимости с динамическим ценообразованием (surge pricing), маршрутизацию через картографические API, обработку платежей, масштабирование на миллионы пользователей, и офлайн-устойчивость для работы при прерывистой сети.

### Требования

**Функциональные:**

**Для пассажиров:**
-   Карта ближайших водителей в реальном времени с геопространственным поиском
-   Запрос поездки с указанием точки посадки и назначения
-   Отображение ETA (Estimated Time of Arrival) и расчетной стоимости с учетом surge pricing
-   Трекинг поездки в реальном времени (отслеживание местоположения водителя, маршрут, время прибытия)
-   Оплата через интегрированные платежные системы
-   История поездок с деталями и возможностью повторного использования адресов

**Для водителей:**
-   Переключение статуса онлайн/офлайн для управления доступностью
-   Получение заявок на поездки в реальном времени
-   Принятие или отклонение заявок с уведомлениями
-   Навигация к точке посадки и по маршруту до места назначения
-   Отслеживание заработка и статистики поездок

**Нефункциональные:**

-   **Обновления**: 3-5 секунд для обновлений местоположения водителей и статуса поездки
-   **Матчинг**: <2 секунды для подбора водителя после запроса поездки
-   **Доступность**: высокая доступность (>99.9%) для критичных операций (запрос поездки, оплата)
-   **Точность GPS**: высокая точность определения местоположения (±5 метров) для корректной работы матчинга и навигации
-   **Экономия батареи**: оптимизированное потребление (<3%/ч в foreground, <1%/ч в background)
-   **Офлайн поддержка**: работа при прерывистой сети с синхронизацией при восстановлении соединения

### Архитектура

**Android клиент:**

Модульная архитектура с разделением по feature-модулям:
-   **Локация**: `FusedLocationProvider` для получения координат, адаптивная частота семплирования, обработка прерывистой сети
-   **WebSocket**: realtime канал для обновлений статуса поездки, ETA водителя, push-уведомлений
-   **Карты**: интеграция с картографическими SDK (`Google Maps`, `Mapbox`) для отображения маркеров, маршрутов, кластеризации
-   **Офлайн очередь**: локальное хранилище (`Room`) для неотправленных запросов, синхронизация через `WorkManager`

**Backend:**

Архитектура микросервисов с четким разделением ответственности:
-   **API Gateway**: единая точка входа для всех клиентских запросов, роутинг к соответствующим микросервисам, rate limiting, аутентификация
-   **Микросервисы**: `Location Service` (трекинг координат), `Matching Service` (подбор водителей), `Ride Service` (FSM поездки), `Payment Service` (обработка платежей), `Notification Service` (push-уведомления), `Pricing Service` (расчет стоимости, surge)
-   **Хранилище данных**: `PostgreSQL` для персистентных данных, `Redis` для кеширования и геопространственного поиска, очереди (`Kafka`/`RabbitMQ`) для асинхронной обработки событий

### Клиент Android: Ключевые Потоки

**1. Локация**

Стратегия отслеживания местоположения с адаптивной частотой для баланса между точностью и экономией батареи.

**Выбор провайдера:**

-   **`FusedLocationProvider` (рекомендуется)**: Интегрированный API от Google, комбинирует данные GPS, Wi‑Fi, сотовых сетей, и датчиков. Автоматически выбирает оптимальный источник для баланса точности и энергопотребления
-   **Fallback без Play Services**: `LocationManager` с `GPS_PROVIDER` и `NETWORK_PROVIDER`, сенсорный fusion для компенсации неточностей GPS

**Адаптивная частота:**

-   **Idle режим**: 0.2-0.5 Гц (раз в 2-5 секунд) с `Significant Motion` detection — снижение частоты когда пользователь неподвижен
-   **В пути**: 1 Гц (раз в секунду) с батчингом 5-10 секунд — сбор координат в буфер для batch отправки
-   **Foreground Service**: обязательный при активной поездке (Android 14+ требует явный `Foreground Service Type`)

```kotlin
// ✅ Location updates with adaptive priority
val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 3000L)
  .setMinUpdateIntervalMillis(1000L)  // Минимум 1 Гц
  .setMaxUpdateDelayMillis(5000L)     // Максимальная задержка для батчинга
  .build()

fusedLocationClient.requestLocationUpdates(req, callback, Looper.getMainLooper())
```

**Оптимизация батареи:**

-   **Backoff при низком заряде**: снижение частоты до 0.2 Гц когда батарея <20%
-   **Coalescing**: объединение нескольких обновлений в одно для batch отправки
-   **Kalman фильтрация**: сглаживание координат для уменьшения шума GPS без увеличения частоты запросов

**2. Синхронизация**

Эффективная синхронизация координат с сервером с минимизацией сетевых запросов и поддержкой офлайн режима.

**Дебаунс и батчинг:**

-   **Дебаунс**: задержка отправки на 3 секунды после последнего обновления — предотвращает spam запросов при частых изменениях координат
-   **Батчинг**: накопление координат в буфере (5-10 точек) и отправка batch запросом — снижение количества HTTP-запросов и overhead
-   **Coalescing**: объединение обновлений для отправки раз в 5-10 секунд вместо каждого обновления

```kotlin
// ✅ Debounce + background sync with batching
locationFlow
  .filterNotNull()
  .debounce(3000L)  // Дебаунс 3 секунды
  .batch(TimeWindow(5000L))  // Батчинг каждые 5 секунд
  .onEach { locations ->
    // Отправка batch координат
    repo.updateLocationBatch(locations)
  }
  .launchIn(viewModelScope)
```

**Фоновая синхронизация:**

-   **`WorkManager`**: автоматическая синхронизация в фоне с constraints (сеть, зарядка) — продолжает работу даже при закрытом приложении
-   **Восстановление при онлайне**: автоматический retry при восстановлении сети с exponential backoff
-   **Очередь**: локальное хранилище (`Room`) для неотправленных координат с персистентной очередью синхронизации

**3. Поиск водителей**

Гибридный подход для отображения ближайших водителей: начальная загрузка через REST и realtime обновления через WebSocket.

**Стратегия загрузки:**

-   **Начальный REST запрос**: загрузка списка ближайших водителей при открытии карты — обеспечивает быстрый старт отображения
-   **WebSocket подписка**: realtime обновления для изменений местоположения водителей, добавления/удаления водителей — снижает latency обновлений
-   **Фильтры**: фильтрация по типу авто (Economy, Premium, XL), статусу водителя (онлайн/занят)

```kotlin
// ✅ REST seed + WebSocket stream with filtering
repo.getNearbyDrivers(
  location = currentLocation,
  vehicleType = selectedVehicleType
)
  .onStart { emit(fetchInitial()) }  // Начальная загрузка через REST
  .combine(websocket.driverUpdates()) { initial, updates ->
    initial.merge(updates)  // Слияние с realtime обновлениями
      .filter { it.vehicleType == selectedVehicleType }
  }
```

**Оптимизация отображения:**

-   **Кластеризация маркеров**: группировка маркеров водителей при zoom out для снижения количества отображаемых элементов — улучшает производительность рендеринга карты
-   **Ленивая загрузка**: загрузка только водителей в видимой области карты — снижение сетевого трафика и нагрузки на рендеринг

**4. Запрос поездки**

Многоэтапный процесс создания запроса поездки с оптимистичным UI и надежной обработкой ошибок.

**Поток запроса:**

1.   **Оценка тарифа**: предварительный расчет стоимости через `Pricing Service` с учетом surge multiplier — пользователь видит цену до подтверждения
2.   **Создание ride**: создание записи поездки в `Ride Service` с уникальным `requestId` для идемпотентности
3.   **Матчинг**: подбор ближайшего водителя через `Matching Service` с scoring алгоритмом
4.   **Подтверждение**: получение подтверждения от водителя через `WebSocket` или push-уведомление
5.   **Трекинг**: начало отслеживания поездки в реальном времени

```kotlin
// ✅ Request ride with essential fields and idempotency
rideRepo.create(
  Ride(
    requestId = generateUniqueId(),  // Для идемпотентности
    pickup = currentLocation,
    destination = destLocation,
    vehicleType = vehicleType,
    quoteId = estimatedQuote.id,    // Привязка к котировке
    createdAt = now()
  )
)
```

**Обработка ошибок:**

-   **Оптимистичный UI**: немедленное отображение состояния "Поиск водителя" до получения ответа от сервера — улучшение UX
-   **Retry логика**: автоматический retry при сетевых ошибках с exponential backoff
-   **Офлайн режим**: сохранение запроса в локальную очередь (`Room`) для отправки при восстановлении сети

**5. Трекинг поездки**

Отслеживание поездки в реальном времени с комбинацией состояния поездки и местоположения водителя.

**Машина состояний:**

Переходы между состояниями: `IDLE` → `REQUESTING` → `MATCHING` → `DRIVER_EN_ROUTE` → `PICKUP` → `ON_TRIP` → `DROPOFF` → `RECEIPT`

**Объединение данных:**

-   **Состояние поездки**: получение через `WebSocket` для обновлений статуса (принято водителем, прибыл, началась поездка, завершена)
-   **Местоположение водителя**: realtime обновления координат водителя через `WebSocket` для отображения на карте
-   **Маршрут и ETA**: расчет через картографические API (`Google Maps Directions`, `Mapbox`) для отображения маршрута и времени прибытия

```kotlin
// ✅ Combine ride state + driver location with route
rideRepo.observeRide(rideId)
  .combine(
    locationRepo.observeDriver(driverId),
    mapsRepo.getRoute(pickup, destination)
  ) { ride, driverLoc, route ->
    RideTracking(
      ride = ride,
      driverLocation = driverLoc,
      route = route,
      eta = calculateETA(route, driverLoc)
    )
  }
```

**Персистентность состояния:**

-   **`Room` database**: сохранение текущего состояния поездки с `vectorClock` и `lastServerVersion` для разрешения конфликтов при восстановлении после смерти процесса
-   **Восстановление**: автоматическое восстановление состояния из `Room` при запуске приложения после краша

### Сервер: Архитектурный Анализ

**Границы сервисов:**

-   **`Location Service`**: принимает координаты от клиентов, валидирует физику движения (проверка скорости <150 km/h для обнаружения спуфинга), обновляет геоиндекс в `Redis Geo` для быстрого поиска, публикует события в `Kafka` для downstream сервисов. Хранит только горячие данные (последние 30 минут) для оптимизации памяти.
-   **`Matching Service`**: выполняет геопоиск доступных водителей в радиусе через `Redis Geo` (`GEORADIUS`), применяет scoring алгоритм (рейтинг·0.4 + 1/distance·0.3 + 1/ETA·0.3), резервирует водителя с optimistic lock для предотвращения двойного матчинга, отправляет push-уведомление водителю. Обрабатывает accept/reject с timeout (30 секунд) для автоматической отмены при отсутствии ответа.
-   **`Ride Service`**: управляет FSM (Finite State Machine) поездки с переходами `REQUESTED`→`ACCEPTED`→`ARRIVED`→`IN_PROGRESS`→`COMPLETED`/`CANCELLED`, хранит аудит всех переходов состояний для аналитики и отладки, обеспечивает идемпотентность через `requestId` от клиента, координирует с `Payment Service` через события для синхронизации оплаты.
-   **`Pricing Service`**: вычисляет базовый тариф по расстоянию и времени поездки, применяет surge multiplier на основе спроса/предложения в зоне, генерирует котировку с TTL (2-5 минут) для предотвращения устаревших цен, привязывает `quoteId` к ride для валидации при создании поездки.
-   **`Payment Service`**: выполняет pre-authorization при запросе поездки (блокировка средств), charge (списание) при завершении поездки, refund (возврат) при отмене поездки. Соответствует требованиям `PCI DSS` для безопасной обработки платежных данных.

**Доменные модели:**

-   **Ride**: id, riderId, driverId, pickup/dest (lat/lng), quoteId, fareAmount, vehicleType, timestamps, status (FSM).
-   **Driver**: id, status (ONLINE/OFFLINE/BUSY), currentLocation, rating, completedRides, acceptanceRate.
-   **Quote**: id, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil, vehicleType.

**Хранение данных:**

-   **PostgreSQL**: rides, payments с ACID, партиционирование по created_at, индексы на rider_id/driver_id/status, репликация master-slave.
-   **Redis Geo**: активные водители (TTL 5 мин), GEOADD/GEORADIUS для мгновенного поиска.
-   **Redis Cache**: котировки (TTL 5 мин), session tokens, rate limit counters.
-   **S3 + Parquet**: архив завершённых поездок, траектории для ML/аналитики.

**Согласованность:**

-   **Outbox pattern**: событие в локальную таблицу outbox в той же транзакции, отдельный процесс публикует в Kafka (at-least-once).
-   **Идемпотентность**: requestId от клиента, unique constraint на (riderId, requestId) для create-ride.
-   **Saga**: Ride → PAYMENT_REQUESTED → Payment → PAYMENT_COMPLETED/FAILED → Ride. При FAILED: компенсация (отмена поездки, возврат водителя).

**Алгоритм матчинга:**

-   **Эвристический**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3, сортировка, топ-1. O(n log n), <100ms.
-   **Оптимальный (batch)**: Hungarian Algorithm для 50-100 поездок раз в 10-30 сек. Trade-off: задержка vs общее ETA.

**Surge pricing:**

-   Зонирование: гексагоны H3, multiplier = min(max_cap, base + α·(demand/supply - threshold)).
-   Демпфер (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge.
-   Привязка quoteId к surge на момент запроса, валидация при создании ride.

**Отказоустойчивость:**

-   WebSocket → long-polling fallback при disconnect.
-   Redis Geo → PostGIS fallback (100-500ms vs <10ms).
-   Retry с jitter, circuit breaker к внешним API (Maps, Payment).
-   Rate limiting: token bucket per riderId/driverId (10 req/min для ride, 100/min для location).

**Безопасность:**

-   JWT с короткими TTL (15 мин), refresh token.
-   TLS, координаты шифруются AES-256 в БД (KMS).
-   Retention: 30 дней, затем агрегация для аналитики. GDPR compliance.
-   Валидация физики движения, fingerprinting устройств, блокировка mock location.

**Наблюдаемость:**

-   Метрики: P99 matching latency <2s, match success >95%, ETA accuracy ±20%, battery ≤5%/hour, WebSocket uptime >99.9%.
-   Distributed tracing (Jaeger/Zipkin), Prometheus + Alertmanager, structured logging (ELK).

**Масштабирование:**

-   Шардирование по географическим регионам (US-West, EU, APAC).
-   Sticky routing для consistency (L7 load balancer).
-   Multi-region для GDPR/data residency.
-   CDN для map tiles, Kubernetes HPA.

### Оптимизация

-   **Батарея**: адаптивная точность и частота, пауза в фоне, Doze-aware.
-   **Сеть**: батчинг координат, компрессия, WebSocket вместо polling.
-   **Карты**: кластеризация, рендер только видимых объектов.

### Офлайн

Кэширование незавершенных действий, очередь синхронизации, авто-ресенд при восстановлении сети.

### Staff-level Model Answer (RU)

Архитектура: модули feature-ride-request, feature-trip, maps-ui, location-core, realtime, payments, flags, analytics. UDF/MVI по экранам; TripRepository объединяет Room + сеть; флаги для протоколов и частоты семплинга.

Карта/перф: бюджет кадра 16ms, интерполяции и кластеризацию выполнять вне UI‑потока.

Локация: FusedLocationProvider; без Play Services — GNSS+сенсоры. Семплинг: idle 0.2–0.5 Гц (significant‑motion), в пути 1 Гц с батчингом 5–10с; сглаживание (Kalman), физпроверки против спуфинга. FG‑сервис при активной поездке.

Машина состояний: IDLE→REQUESTING→MATCHING→DRIVER_EN_ROUTE→PICKUP→ON_TRIP→DROPOFF→RECEIPT. Персист в Room (vectorClock/lastServerVersion) на случай смерти процесса.

Realtime: FCM‑nudges + WebSocket; heartbeat, backoff, обновление токена; в фоне — редкие дельты по push. Идемпотентность и порядковые номера.

Офлайн/сбои: очередь запросов с оптимистичным UI; reconnect с ключами идемпотентности; fallback long‑poll при блокировке WS.

Анти‑абьюз/интегрити: isFromMockProvider, сенсорный фьюжн и Play Integrity сигналы; деградация UX при подозрении.

Батарея/термал: 1 Гц при движении, coalesce записи; significant‑motion при стазисе; избегать wakeful loops; push‑driven дельты.

Наблюдаемость/релиз: метрики (cold start p95, map frame p95, accuracy, battery/100км, WS reconnect, ANR/crash). Health gates + staged rollout; kill‑switch для WS.

Тестирование: симулированные GPS‑трассы, сетевой хаос, смерть процесса/отзыв разрешений, jank‑профилирование.

Последовательность: MVP (поиск адреса→запрос→ETA через polling→треккинг) → упрочнение (WS, офлайн‑очередь, FG‑сервис, батарея) → масштаб (анти‑абьюз, интегрити, I18N, богатые карты).

---

## Answer (EN)

`Uber` is a comprehensive ride-hailing system involving: real-time location tracking, nearby driver matching via geospatial search, fare calculation with dynamic pricing (surge pricing), routing via mapping APIs, payment processing, scaling to millions of users, and offline resilience for operation under intermittent connectivity.

### Requirements

**Functional:**

**For riders:**
-   Real-time nearby drivers map with geospatial search
-   Ride request with pickup and destination points
-   ETA (Estimated Time of Arrival) display and fare calculation with surge pricing
-   Real-time trip tracking (driver location, route, arrival time)
-   Payment via integrated payment systems
-   Trip history with details and reusable address functionality

**For drivers:**
-   Online/offline toggle for availability management
-   Real-time ride request notifications
-   Accept or reject requests with notifications
-   Navigation to pickup point and route to destination
-   Earnings tracking and trip statistics

**Non-functional:**

-   **Updates**: 3-5 seconds for driver location and trip status updates
-   **Matching**: <2 seconds to match driver after ride request
-   **Availability**: high availability (>99.9%) for critical operations (ride request, payment)
-   **GPS accuracy**: high location accuracy (±5 meters) for correct matching and navigation
-   **Battery efficiency**: optimized consumption (<3%/hr foreground, <1%/hr background)
-   **Offline support**: operation under intermittent connectivity with sync on connection recovery

### Architecture

**Android client:**

Modular architecture with separation by feature modules:
-   **Location**: `FusedLocationProvider` for coordinate retrieval, adaptive sampling frequency, intermittent connectivity handling
-   **WebSocket**: realtime channel for trip status updates, driver ETA, push notifications
-   **Maps**: integration with mapping SDKs (`Google Maps`, `Mapbox`) for markers, routes, clustering
-   **Offline queue**: local storage (`Room`) for unsent requests, synchronization via `WorkManager`

**Backend:**

Microservices architecture with clear separation of responsibility:
-   **API Gateway**: single entry point for all client requests, routing to corresponding microservices, rate limiting, authentication
-   **Microservices**: `Location Service` (coordinate tracking), `Matching Service` (driver matching), `Ride Service` (trip FSM), `Payment Service` (payment processing), `Notification Service` (push notifications), `Pricing Service` (fare calculation, surge)
-   **Data storage**: `PostgreSQL` for persistent data, `Redis` for caching and geospatial search, queues (`Kafka`/`RabbitMQ`) for asynchronous event processing

### Android Client: Key Flows

**1. Location**

Location tracking strategy with adaptive frequency for balance between accuracy and battery efficiency.

**Provider choice:**

-   **`FusedLocationProvider` (recommended)**: Integrated API from Google, combines GPS, Wi‑Fi, cellular, and sensor data. Automatically selects optimal source for accuracy/battery balance
-   **Fallback without Play Services**: `LocationManager` with `GPS_PROVIDER` and `NETWORK_PROVIDER`, sensor fusion to compensate GPS inaccuracies

**Adaptive frequency:**

-   **Idle mode**: 0.2-0.5 Hz (every 2-5 seconds) with `Significant Motion` detection — reduce frequency when user stationary
-   **En route**: 1 Hz (per second) with 5-10 second batching — collect coordinates in buffer for batch sending
-   **Foreground Service**: required during active trip (Android 14+ requires explicit `Foreground Service Type`)

```kotlin
// ✅ Location updates with adaptive priority
val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 3000L)
  .setMinUpdateIntervalMillis(1000L)  // Minimum 1 Hz
  .setMaxUpdateDelayMillis(5000L)     // Maximum delay for batching
  .build()

fusedLocationClient.requestLocationUpdates(req, callback, Looper.getMainLooper())
```

**Battery optimization:**

-   **Backoff on low battery**: reduce frequency to 0.2 Hz when battery <20%
-   **Coalescing**: combine multiple updates into one for batch sending
-   **Kalman filtering**: smooth coordinates to reduce GPS noise without increasing request frequency

**2. Sync**

Debounce and batching for efficient network usage, background processing via `WorkManager`, automatic resume on reconnect.

**3. Nearby Drivers**

Hybrid approach for displaying nearby drivers: initial load via REST and realtime updates via WebSocket.

**Loading strategy:**

-   **Initial REST request**: load nearby drivers list on map open — ensures fast initial display
-   **WebSocket subscription**: realtime updates for driver location changes, add/remove drivers — reduces update latency
-   **Filters**: filter by vehicle type (Economy, Premium, XL), driver status (online/busy)

```kotlin
// ✅ REST seed + WebSocket stream with filtering
repo.getNearbyDrivers(
  location = currentLocation,
  vehicleType = selectedVehicleType
)
  .onStart { emit(fetchInitial()) }  // Initial load via REST
  .combine(websocket.driverUpdates()) { initial, updates ->
    initial.merge(updates)  // Merge with realtime updates
      .filter { it.vehicleType == selectedVehicleType }
  }
```

**Display optimization:**

-   **Marker clustering**: group driver markers on zoom out to reduce displayed elements — improves map rendering performance
-   **Lazy loading**: load only drivers in visible map area — reduces network traffic and rendering load

**4. Request Ride**

Multi-step process for creating ride request with optimistic UI and reliable error handling.

**Request flow:**

1.   **Fare estimate**: preliminary cost calculation via `Pricing Service` with surge multiplier — user sees price before confirmation
2.   **Create ride**: create ride record in `Ride Service` with unique `requestId` for idempotency
3.   **Matching**: find nearest driver via `Matching Service` with scoring algorithm
4.   **Confirmation**: receive driver confirmation via `WebSocket` or push notification
5.   **Tracking**: start real-time trip tracking

```kotlin
// ✅ Request ride with essential fields and idempotency
rideRepo.create(
  Ride(
    requestId = generateUniqueId(),  // For idempotency
    pickup = currentLocation,
    destination = destLocation,
    vehicleType = vehicleType,
    quoteId = estimatedQuote.id,    // Bind to quote
    createdAt = now()
  )
)
```

**Error handling:**

-   **Optimistic UI**: immediate "Searching for driver" display before server response — improves UX
-   **Retry logic**: automatic retry on network errors with exponential backoff
-   **Offline mode**: save request to local queue (`Room`) for sending on network recovery

**5. Track Ride**

Real-time trip tracking with combination of trip state and driver location.

**State machine:**

State transitions: `IDLE` → `REQUESTING` → `MATCHING` → `DRIVER_EN_ROUTE` → `PICKUP` → `ON_TRIP` → `DROPOFF` → `RECEIPT`

**Data combination:**

-   **Trip state**: received via `WebSocket` for status updates (driver accepted, arrived, trip started, completed)
-   **Driver location**: realtime driver coordinate updates via `WebSocket` for map display
-   **Route and ETA**: calculated via mapping APIs (`Google Maps Directions`, `Mapbox`) for route and arrival time display

```kotlin
// ✅ Combine ride state + driver location with route
rideRepo.observeRide(rideId)
  .combine(
    locationRepo.observeDriver(driverId),
    mapsRepo.getRoute(pickup, destination)
  ) { ride, driverLoc, route ->
    RideTracking(
      ride = ride,
      driverLocation = driverLoc,
      route = route,
      eta = calculateETA(route, driverLoc)
    )
  }
```

**State persistence:**

-   **`Room` database**: save current trip state with `vectorClock` and `lastServerVersion` for conflict resolution on process death recovery
-   **Recovery**: automatic state recovery from `Room` on app startup after crash

### Server: Architecture Analysis

**Service boundaries:**

-   **`Location Service`**: accepts coordinates from clients, validates movement physics (speed check <150 km/h for spoofing detection), updates geo-index in `Redis Geo` for fast search, publishes events to `Kafka` for downstream services. Stores only hot data (last 30 minutes) for memory optimization.
-   **`Matching Service`**: performs geo-search for available drivers in radius via `Redis Geo` (`GEORADIUS`), applies scoring algorithm (rating·0.4 + 1/distance·0.3 + 1/ETA·0.3), reserves driver with optimistic lock to prevent double matching, sends push notification to driver. Handles accept/reject with timeout (30 seconds) for automatic cancellation on no response.
-   **`Ride Service`**: manages FSM (Finite State Machine) with transitions `REQUESTED`→`ACCEPTED`→`ARRIVED`→`IN_PROGRESS`→`COMPLETED`/`CANCELLED`, stores audit trail of all state transitions for analytics and debugging, ensures idempotency via `requestId` from client, coordinates with `Payment Service` via events for payment synchronization.
-   **`Pricing Service`**: calculates base fare by trip distance and time, applies surge multiplier based on demand/supply in zone, generates quote with TTL (2-5 minutes) to prevent stale pricing, binds `quoteId` to ride for validation on ride creation.
-   **`Payment Service`**: performs pre-authorization on ride request (funds hold), charge on trip completion, refund on cancellation. Complies with `PCI DSS` requirements for secure payment data processing.

**Domain models:**

-   **Ride**: id, riderId, driverId, pickup/dest (lat/lng), quoteId, fareAmount, vehicleType, timestamps, status (FSM).
-   **Driver**: id, status (ONLINE/OFFLINE/BUSY), currentLocation, rating, completedRides, acceptanceRate.
-   **Quote**: id, pickupZone, destZone, baseFare, surgeMultiplier, totalFare, validUntil, vehicleType.

**Data storage:**

-   **PostgreSQL**: rides, payments with ACID, partitioning by created_at, indexes on rider_id/driver_id/status, master-slave replication.
-   **Redis Geo**: active drivers (TTL 5 min), GEOADD/GEORADIUS for instant search.
-   **Redis Cache**: quotes (TTL 5 min), session tokens, rate limit counters.
-   **S3 + Parquet**: archive completed rides, trajectories for ML/analytics.

**Consistency:**

-   **Outbox pattern**: write event to local outbox table in same transaction, separate process publishes to Kafka (at-least-once).
-   **Idempotency**: requestId from client, unique constraint on (riderId, requestId) for create-ride.
-   **Saga**: Ride → PAYMENT_REQUESTED → Payment → PAYMENT_COMPLETED/FAILED → Ride. On FAILED: compensation (cancel ride, return driver).

**Matching algorithm:**

-   **Heuristic**: score = rating·0.4 + (1/distance)·0.3 + (1/ETA)·0.3, sort, pick top-1. O(n log n), <100ms.
-   **Optimal (batch)**: Hungarian Algorithm for 50-100 rides every 10-30 sec. Trade-off: delay vs overall ETA.

**Surge pricing:**

-   Zoning: H3 hexagons, multiplier = min(max_cap, base + α·(demand/supply - threshold)).
-   Dampener (EMA): new_surge = 0.7·old_surge + 0.3·computed_surge.
-   Bind quoteId to surge at request time, validate on ride creation.

**Resilience:**

-   WebSocket → long-polling fallback on disconnect.
-   Redis Geo → PostGIS fallback (100-500ms vs <10ms).
-   Retry with jitter, circuit breaker to external APIs (Maps, Payment).
-   Rate limiting: token bucket per riderId/driverId (10 req/min for ride, 100/min for location).

**Security:**

-   JWT with short TTL (15 min), refresh token.
-   TLS, coordinates encrypted AES-256 in DB (KMS).
-   Retention: 30 days, then aggregated for analytics. GDPR compliance.
-   Movement physics validation, device fingerprinting, block mock location.

**Observability:**

-   Metrics: P99 matching latency <2s, match success >95%, ETA accuracy ±20%, battery ≤5%/hour, WebSocket uptime >99.9%.
-   Distributed tracing (Jaeger/Zipkin), Prometheus + Alertmanager, structured logging (ELK).

**Scalability:**

-   Sharding by geographic regions (US-West, EU, APAC).
-   Sticky routing for consistency (L7 load balancer).
-   Multi-region for GDPR/data residency.
-   CDN for map tiles, Kubernetes HPA.

### Optimization

-   **Battery**: adaptive precision/frequency, pause in background, Doze-aware.
-   **Network**: batch coordinates, compression, WebSocket over polling.
-   **Maps**: clustering, render only visible objects.

### Offline

Cache incomplete actions, sync queue, auto-resend on network restore.

### Staff-level Model Answer (EN)

Architecture overview: feature-ride-request, feature-trip, maps-ui, location-core, realtime, payments, flags, analytics. UDF/MVI; TripRepository orchestrates Room + network; feature flags for protocols and sampling.

Map performance: frame budget <16ms; offload interpolation/clustering; keep main-thread work minimal.

Location strategy: FusedLocationProvider; fallback to GNSS+sensor fusion. Sampling idle 0.2–0.5 Hz with significant‑motion; en‑route 1 Hz with 5–10s batching; Kalman smoothing; spoofing checks. Foreground service during active trip.

Trip state machine: IDLE→REQUESTING→MATCHING→DRIVER_EN_ROUTE→PICKUP→ON_TRIP→DROPOFF→RECEIPT. Persist in Room with vectorClock/lastServerVersion.

Realtime updates: FCM nudge → WebSocket; heartbeat, backoff, token refresh; background relies on push with sparse deltas. Apply updates by sequence number; drop dups/out-of-order.

Offline/failure modes: idempotency-keyed queue with optimistic UI; reconnect and resend; long‑poll fallback.

Anti‑abuse & integrity: mock detection, sensor inconsistencies, Play Integrity; degrade to manual verification on suspicion.

Battery/thermal: 1 Hz sampling with coalesced writes; switch to significant‑motion when stationary; push‑driven deltas; avoid wakeful loops.

Observability & rollout: cold start p95, map frame p95, accuracy, battery/100km, WS reconnect, crash/ANR; health gates, staged rollout, kill‑switch for WS.

Testing: GPS trace sims; network chaos; process-death and permission-revocation tests; jank profiling.

Sequencing: MVP → Hardening → Scale; WS latency vs background limits tradeoffs.

---

## Follow-ups

-   How to implement surge pricing fairly and at scale?
-   How to detect and mitigate driver/rider fraud (GPS spoofing, fake rides)?
-   How to design fallback when WebSocket is unavailable?
-   How to optimize battery for continuous location tracking?
-   How to handle cross-region rides (data residency, latency)?

## References

-   [Fused Location Provider](https://developers.google.com/location-context/fused-location-provider)
-   [Google Maps Android SDK](https://developers.google.com/maps/documentation/android-sdk)
-   [Redis Geo Commands](https://redis.io/commands/geoadd/)
-   [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)
-   [Battery Performance](https://developer.android.com/topic/performance/power)
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]
-   [[c-service]]
-   [[c-workmanager]]

## Related Questions

### Prerequisites (Easier)

-   [[q-data-sync-unstable-network--android--hard]]
-   [[q-deep-link-vs-app-link--android--medium]]

### Related (Same Level)

-   [[q-design-instagram-stories--android--hard]]
-   [[q-load-balancing-strategies--system-design--medium]]

### Advanced Concepts

-   [[q-microservices-vs-monolith--system-design--hard]]
-   [[q-message-queues-event-driven--system-design--medium]]
