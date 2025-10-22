---
id: 20251020-200000
title: "Design Uber App / Проектирование приложения Uber"
aliases: [Design Uber App, Проектирование приложения Uber]

topic: android
subtopics: [location, networking-http, service]
question_kind: android
difficulty: hard

original_language: en
language_tags: [en, ru]
source: https://developers.google.com/location-context/fused-location-provider
source_note: Android Fused Location Provider overview

status: draft
moc: moc-android
related: [q-data-sync-unstable-network--android--hard, q-deep-link-vs-app-link--android--medium, q-android-performance-optimization--android--medium]

created: 2025-10-20
updated: 2025-10-20

tags: [android/location, android/networking-http, android/service, maps, realtime, difficulty/hard]
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
