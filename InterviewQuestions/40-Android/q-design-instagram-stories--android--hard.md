---
id: android-441
title: Design Instagram Stories / Проектирование Instagram Stories
aliases: [Design Instagram Stories, Проектирование Instagram Stories]
topic: android
subtopics: [architecture-clean, media, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
sources:
  - "https://developer.android.com/guide/topics/media"
status: draft
moc: moc-android
related: [c-android, q-data-sync-unstable-network--android--hard, q-database-optimization-android--android--medium, q-design-uber-app--android--hard, q-feature-flags-sdk--android--hard]
created: 2025-10-20
updated: 2025-11-10
tags: [android/architecture-clean, android/media, android/service, architecture, difficulty/hard, exoplayer, mediacodec, performance, system-design, workmanager]

---
# Вопрос (RU)

> Как спроектировать Instagram Stories для Android?

## Краткая Версия
Спроектируйте систему для создания, загрузки и воспроизведения Stories на Android. Система должна поддерживать быстрый захват видео, надежную загрузку в фоне, и плавное воспроизведение с автоматическим удалением через 24 часа.

## Подробная Версия
Спроектируйте полноценную систему Instagram Stories для Android со следующими требованиями:

**Захват видео:**
- Длительность: 15 секунд
- Разрешение: таргетированное 720p @ 30fps (можно писать в более высоком качестве на устройстве и транскодировать на backend при необходимости)
- AR-эффекты: опциональные (фильтры в реальном времени)
- Экспорт: <3 секунды (p95) на устройстве среднего уровня (Snapdragon 7‑серии)

**Воспроизведение:**
- Старт: <150мс (p95, при условии агрессивного prefetch/кеша)
- Плавность: 60fps на современных устройствах
- Адаптация: graceful degradation на бюджетных устройствах (30fps, низкое разрешение)

**Надежность:**
- Поддержка прерывистой сети (offline-first подход)
- Фоновая возобновляемая загрузка (chunked upload с retry)

**Детали реализации (для обсуждения):**
- Выбор камеры: `CameraX` vs `Camera2` (обоснование выбора)
- Рендер-пайплайн: zero-copy путь от камеры к энкодеру
- Конфигурация кодера: codec, profile, bitrate, `GOP` (Group of Pictures)
- Загрузка: чанковая структура, возобновление по смещению
- Кеширование: CDN prefetch, on-device cache policy (`LRU`, eviction)
- Воспроизведение: стратегия `ExoPlayer` (`HLS`/`DASH`, `ABR`)
- Ресурсы: аудиофокус, меры по теплу/батарее (thermal throttling)
- Операции: наблюдаемость (метрики), релиз/откат (staged rollout)
- Доступность: `TalkBack`, субтитры, крупные тач-таргеты

# Question (EN)

> How to design Instagram Stories for Android?

## Short Version
Design a system for creating, uploading, and playing Stories on Android. The system should support fast video capture, reliable background upload, and smooth playback with automatic deletion after 24 hours.

## Detailed Version
Design a complete Instagram Stories system for Android with the following requirements:

**Video capture:**
- Duration: 15 seconds
- Resolution: target 720p @ 30fps (you may capture higher and transcode server-side if needed)
- AR effects: optional (real-time filters)
- Export: <3 seconds (p95) on mid-tier device (Snapdragon 7‑series)

**Playback:**
- Startup: <150ms (p95, assuming aggressive prefetch/caching)
- Smoothness: 60fps on modern devices
- Adaptation: graceful degradation on low-end devices (30fps, lower resolution)

**Reliability:**
- Support intermittent connectivity (offline-first approach)
- Background resumable upload (chunked upload with retry)

**Implementation details (for discussion):**
- Camera choice: `CameraX` vs `Camera2` (justify selection)
- Render pipeline: zero-copy path from camera to encoder
- Encoder configuration: codec, profile, bitrate, `GOP` (Group of Pictures)
- Upload: chunked structure, resumption by offset
- Caching: CDN prefetch, on-device cache policy (`LRU`, eviction)
- Playback: `ExoPlayer` strategy (`HLS`/`DASH`, `ABR`)
- Resources: audio focus, thermal/battery mitigation (thermal throttling)
- Operations: observability (metrics), release/rollback (staged rollout)
- Accessibility: `TalkBack`, captions, larger tap targets

## Ответ (RU)

`Instagram Stories` — система для создания, загрузки, воспроизведения и автоматического удаления медиа через 24 часа. Ключевые требования: быстрый захват видео (15 секунд @ 720p/30fps), оптимизированный экспорт (<3 секунды p95), плавное воспроизведение (целевой p95 старта <150мс при наличии prefetch/кеша), поддержка прерывистой сети, и эффективное использование ресурсов устройства (батарея, тепло, память).

### Требования

**Функциональные:**
- Захват, редактирование (фильтры/текст/стикеры) и публикация stories.
- Фоновая и возобновляемая загрузка медиа.
- Автоматическое истечение и скрытие stories через 24 часа.
- Просмотр ленты stories с быстрым переключением и prefetch.
- Учёт просмотров и базовая аналитика.

**Нефункциональные:**
- Время старта воспроизведения p95 <150 мс при наличии кеша/prefetch.
- Время экспорта p95 <3 секунд на mid-tier устройствах.
- Работа в условиях нестабильной сети (offline-first, chunked upload, retry).
- Масштабируемость backend и эффективное использование CDN.
- Минимальное влияние на батарею, память и тепловой режим.

### Архитектура

**Android-клиент:**

Архитектура следует принципам `Clean Architecture` с четким разделением слоев:

- **Domain Layer**: Содержит бизнес-логику — сущность `Story` с полями (id, userId, mediaUrl, createdAt, expiresAt), логика TTL (24 часа), правила валидации (максимальная длительность 15 секунд, целевое разрешение 720p, возможно сохранение исходника до 1080p для последующей транскодировки)
- **Data Layer**: `Repository Pattern` для абстракции источников данных — `StoryRepository` координирует локальное хранилище (`Room`), сетевые запросы (`Retrofit`), и кеш (`OkHttp` cache, `LruCache`). Обрабатывает синхронизацию при восстановлении сети
- **Presentation Layer**: `MVVM` для камеры и просмотра — `CameraViewModel` управляет захватом и экспортом, `StoryPlayerViewModel` управляет воспроизведением и prefetch. Использует `Coroutines` и `Flow` для реактивности

**Технологический стек:**

- **`WorkManager`** для надежной фоновой загрузки с автоматическими повторами, constraints (сеть, зарядка), и интеграцией с `Doze Mode`
- **`ExoPlayer`** для видео — поддерживает `HLS`/`DASH`, `ABR` (Adaptive Bitrate), prefetching, и graceful degradation на слабых устройствах
- **`Coil`** для изображений — эффективная загрузка и кеширование с поддержкой трансформаций
- **Многоуровневый кеш**: `Memory Cache` (`LruCache`) → `Disk Cache` (`OkHttp` disk cache, `Room`) → `Network` (CDN с prefetch, управляемый backend)

**Backend:**

- **API**: RESTful API для загрузки (`POST /stories/upload`), получения списка (`GET /stories/{userId}`), транскодирования (асинхронные джобы через `Kafka`/`RabbitMQ`), TTL-джобы (периодическая очистка через `Cron`), и ACL (проверка прав доступа к stories других пользователей)
- **Хранилище**: `S3`/`GCS` для медиафайлов с lifecycle policies для автоматического удаления через 24 часа, CDN (`CloudFront`/`Cloudflare`) для глобального распространения с edge caching, метаданные в `PostgreSQL`/`MongoDB` с индексами по `userId` и `expiresAt` для быстрой очистки
- **Realtime**: `WebSocket`/`Pub-Sub` (`Redis Pub/Sub`, `Kafka`) для счетчиков просмотров в реальном времени, обновления статуса загрузки, и push-уведомлений о новых stories от подписок

### Ключевые Потоки

**Создание и загрузка:**

Процесс создания включает захват видео через `CameraX`/`Camera2`, применение AR-эффектов через `OpenGL ES`, и кодирование через `MediaCodec`. После захвата медиафайл сжимается и загружается в фоне через `WorkManager`.

```kotlin
//  Надежная загрузка с повторами и прогрессом (псевдокод)
class UploadStoryWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    return try {
      val uri = inputData.getString("uri")!!
      // Сжатие: JPEG/WEBP для превью, H.264 для видео, ~4-6Mbps битрейт для 720p/30fps
      val compressed = compressMedia(uri)

      // Загрузка с прогрессом через callback
      storyRepo.upload(
        compressed,
        // Используйте реальное время в мс; запись ниже носит иллюстративный характер
        expiresAt = System.currentTimeMillis() + 24 * 60 * 60 * 1000L,
        onProgress = { progress -> setProgress(workDataOf("progress" to progress)) }
      )
      Result.success()
    } catch (e: Exception) {
      // Экспоненциальный backoff настраивается при создании WorkRequest
      if (runAttemptCount < 3) Result.retry() else Result.failure()
    }
  }
}
```

**Детали реализации:**

- **Сжатие**: Используйте `MediaCodec` с `H.264` кодеком (Baseline profile для совместимости, High profile для лучшего качества), битрейт 4-6 Mbps для 720p/30fps, `GOP` (Group of Pictures) ≈ 1 секунда для быстрого старта воспроизведения
- **Чанковая загрузка**: Разбивайте файлы на чанки 4-8MB для возобновления при обрыве сети, используйте `SHA-256` хеш каждого чанка для проверки целостности
- **Возобновление**: При восстановлении сети `WorkManager` обеспечивает персистентность и повторный запуск задач, а клиент и сервер по протоколу offset negotiation продолжают загрузку с последнего успешно принятого чанка

**Просмотр:**

Воспроизведение должно начинаться максимально быстро и быть плавным (60fps на современных устройствах). Используется стратегия prefetching для предварительной загрузки следующих stories.

- **Prefetching**: Предзагрузка текущей story + 2 следующих stories параллельно — первые сегменты загружаются в фоне пока пользователь смотрит текущую
- **Кеширование**: `OkHttp` disk cache для хранения сегментов на диске (~250MB limit), `LruCache` в памяти для превью и первых сегментов текущей story (быстрый доступ без I/O)
- **Батарея**: Пауза `ExoPlayer` при переходе приложения в фон для экономии батареи, возобновление при возврате в foreground
- **Адаптивное качество**: `ABR` (Adaptive Bitrate) — `ExoPlayer` автоматически выбирает оптимальный битрейт на основе пропускной способности сети и производительности устройства
- **Graceful degradation**: На слабых устройствах — ограничение до 30fps, выбор меньших разрешений из ladder, отключение тяжелых переходов между stories

**TTL (24 часа):**

Stories автоматически истекают через 24 часа с момента создания. Периодическая очистка удаляет истекшие stories с устройства и из кеша.

```kotlin
//  Периодическая очистка истекших stories (псевдокод)
class CleanupExpiredWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    val now = System.currentTimeMillis()

    // Удаление из локальной БД
    storyRepo.deleteExpired(before = now)

    // Очистка кеша (диск и память)
    cacheManager.evict { story -> story.expiresAt < now }

    // Инвалидация CDN кеша (если поддерживается backend API)
    cdnCacheManager.invalidateExpired()

    return Result.success()
  }
}
```

**Стратегия очистки:**

- **Периодичность**: Запуск `CleanupExpiredWorker` каждые 6 часов через `PeriodicWorkRequest` — баланс между частотой очистки и нагрузкой на систему
- **Локальное хранилище**: Удаление из `Room` database с каскадным удалением связанных метаданных (превью, thumbnail)
- **Кеш**: Эвикция из `OkHttp` disk cache и `LruCache` по критерию `expiresAt < now` — освобождение места для новых stories
- **Оптимизация**: Индексы в БД по `expiresAt` для быстрого поиска истекших stories, batch deletion для эффективности

### Оптимизация Производительности

**Offline-first подход:**

- **Очередь загрузки**: `WorkManager` ставит загрузки в очередь при отсутствии сети — пользователь может создавать stories офлайн, они загрузятся при восстановлении соединения
- **Локальная БД**: `Room` хранит метаданные stories (id, userId, expiresAt, uploadStatus) даже при отсутствии сети — позволяет отображать локально созданные stories до загрузки
- **Синхронизация**: При восстановлении сети синхронизация через `WorkManager` с заданными constraints — например, загрузка только при наличии Wi-Fi или зарядки (опционально)

**CDN оптимизация:**

- **Подписанные URL**: CDN или origin выдает временные подписанные URL с коротким TTL (1-2 часа) для безопасности — предотвращает неавторизованный доступ к истекшим stories
- **Edge caching**: Кеширование на edge-серверах CDN ближе к пользователям — снижение latency для глобальной аудитории
- **Prefetch на CDN**: По данным backend популярные stories могут агрессивно кешироваться на edge — снижение задержки при переходе между stories

**Скейлинг Backend:**

- **Партиционирование**: Партиционирование данных по `userId` (sharding) — распределение нагрузки по нескольким БД-инстансам
- **Денормализация**: Хранение `seen/unseen` ring в денормализованном виде для быстрого отображения — избегание сложных JOIN-запросов
- **Read replicas**: Использование read replicas для снижения нагрузки на master БД — масштабирование чтений независимо от записей

### Детальная Реализация Capture Pipeline

**Архитектура модулей:**

Модульная структура разделяет функциональность по feature-модулям для независимой разработки и тестирования:

- **feature-stories-capture**: Модуль захвата — `CameraViewModel`, UI для камеры, обработка AR-эффектов
- **feature-stories-playback**: Модуль воспроизведения — `StoryPlayerViewModel`, `ExoPlayer` integration, UI для viewer
- **media-core**: Общий медиа-модуль — `CameraX`/`Camera2` wrappers, `OpenGL ES` рендеринг, `MediaCodec` encoding
- **upload**: Модуль загрузки — `WorkManager` workers, chunked upload logic, retry strategies
- **cache**: Модуль кеширования — многоуровневый кеш (`Memory`, `Disk`, `Network`), eviction policies
- **analytics**: Модуль аналитики — метрики производительности, ошибки, user engagement
- **flags**: Feature flags — динамическое управление кодеком (`H.264`/`HEVC`), длиной сегментов, prefetch размером

**Паттерны архитектуры:**

- **MVVM + однонаправленный поток данных**: `ViewModel` содержит бизнес-логику и state, `View` (Compose/Views) только отображает состояние и отправляет события обратно в `ViewModel`. `Flow` обеспечивает реактивность
- **DI (Hilt)**: Dependency injection для управления зависимостями между модулями — легкость тестирования и поддержки

**Захват видео:**

Выбор камеры:

- **CameraX (рекомендуется)**: Широкая совместимость с устройствами (API 21+), упрощенный API, автоматическая обработка lifecycle. Подходит для большинства случаев
- **Camera2 (fallback)**: Используйте для ручного контроля (manual exposure, focus, RAW capture) или когда нужна максимальная производительность на современных устройствах

Рендер-пайплайн:

- **Zero-copy путь**: `Camera` → `SurfaceTexture` → `OpenGL ES` → `Surface(Encoder)` — данные камеры напрямую попадают в `OpenGL` контекст без копирования в память, затем рендерятся на `Surface` энкодера. Это минимизирует задержку и использование памяти
- **AR-эффекты**: Применение фильтров через `OpenGL ES` shaders — обработка происходит на GPU параллельно с захватом, минимальный overhead

Конфигурация кодера:

- **Codec**: `MediaCodec` с `H.264` кодеком (Baseline profile для максимальной совместимости, High profile для лучшего сжатия). `HEVC` (H.265) под feature flag для устройств с поддержкой — на 30-50% лучше сжатие, но требует больше CPU/GPU
- **Bitrate**: 4-6 Mbps @ 720p/30fps — баланс между качеством и размером файла. Используйте `CBR`-biased `VBR` (Variable Bitrate с упором на стабильность) для предсказуемого размера файла
- **GOP (Group of Pictures)**: GOP ≈ 1 секунда (30 кадров при 30fps) — короткий `GOP` позволяет быстрее начинать воспроизведение, так как `I-frame` появляется чаще
- **Audio**: `AAC` кодек, битрейт 128-192 kbps — достаточное качество для голоса и музыки
- **Multiplexing**: `MediaMuxer` объединяет видео и аудио дорожки в `MP4` контейнер — стандартный формат с широкой поддержкой

Тепловой и батарейный менеджмент:

- **Thermal throttling**: Мониторинг температуры через `ThermalManager` (API 29+). При перегреве — даунскейл до 540p, понижение битрейта до 2-3 Mbps, отключение тяжелых AR-фильтров
- **Battery optimization**: Использование `JobScheduler` constraints для загрузки только при зарядке (опционально), снижение частоты кадров до 24fps при низком заряде батареи

**Загрузка (Upload Pipeline):**

Pre-upload оптимизации:

- **Thumbnail/Preview**: Генерация low-resolution превью (`JPEG` 320x240) для быстрого отображения в UI до завершения загрузки основного файла
- **Perceptual hash**: Вычисление perceptual hash (например, `pHash`) для дедупликации — предотвращение повторной загрузки идентичного контента

Чанковая загрузка:

- **Размер чанков**: 4-8MB — баланс между количеством запросов и возможностью возобновления. Меньшие чанки увеличивают количество HTTP-запросов, большие — снижают гибкость при обрыве
- **Интегритет**: `SHA-256` хеширование каждого чанка для проверки целостности на сервере — обнаружение повреждений при передаче
- **Возобновление**: Offset negotiation — сервер сообщает последний успешно загруженный байт, клиент продолжает с этого смещения. `WorkManager` обеспечивает хранение состояния и повторный запуск задач, но сам протокол возобновления реализуется в приложении и на backend
- **Безопасность**: `TLS` для транспорта, опционально клиентское шифрование `AES-GCM` для критичных данных перед загрузкой

WorkManager интеграция:

- **Constraints**: Загрузка только при наличии сети (`NetworkType.CONNECTED`), опционально только на Wi-Fi или при зарядке — экономия мобильного трафика и батареи
- **Exponential backoff**: Автоматическая задержка между retry с экспоненциальным увеличением для предотвращения перегрузки сервера
- **Doze Mode**: `WorkManager` уважает `Doze Mode` и `App Standby` — задачи откладываются до maintenance window в соответствии с платформой

**Воспроизведение (Playback System):**

ExoPlayer конфигурация:

- **Формат**: `HLS`/`DASH` с сегментами ~1 секунды — короткие сегменты помогают снизить время до первого кадра при наличии кеша/prefetch, но фактический p95 старта зависит от сети и реализаций
- **ABR (Adaptive Bitrate)**: Несколько битрейтов в manifest — `ExoPlayer` автоматически выбирает оптимальный битрейт на основе текущей пропускной способности сети и производительности устройства
- **Bitrate ladder**: Множество вариантов качества (например, 1080p @ 8Mbps, 720p @ 4Mbps, 480p @ 2Mbps, 360p @ 1Mbps) — плавная адаптация к условиям

Prefetch стратегия:

- **Объем**: Prefetch первых 2-3 сегментов следующей story параллельно с воспроизведением текущей — пользователь не ждет загрузки при свайпе
- **Отмена**: При свайпе прочь от prefetched story — немедленная отмена загрузки для экономии трафика и батареи

On-device кеш:

- **Размер**: `LRU` кеш ~250MB на диске — баланс между объемом и использованием места на устройстве
- **Eviction policy**: Удаление по времени (истекшие stories), по последнему просмотру (`LRU`), и по размеру — освобождение места для новых stories
- **Оптимизация**: Хранение только первых N сегментов для редких stories — экономия места, полная загрузка по требованию

Graceful degradation:

- **Слабые устройства**: Ограничение до 30fps (вместо 60fps), выбор меньших разрешений из ladder (480p вместо 720p), отключение тяжелых переходов (fade, slide) — сохранение плавности воспроизведения

Audio focus и PiP:

- **Audio focus**: Обработка `AUDIOFOCUS_LOSS` для паузы воспроизведения при звонке или другом аудио-приложении
- **PiP (Picture-in-Picture)**: Поддержка `Picture-in-Picture` режима (API 24+) для просмотра stories в маленьком окне поверх других приложений

**Наблюдаемость и Операции:**

Метрики производительности:

- **p95 старта**: 95-й перцентиль времени старта воспроизведения — целевой <150мс при оптимальном prefetch/кешировании
- **p95 экспорта**: 95-й перцентиль времени экспорта видео — целевой <3 секунды на mid-tier устройствах
- **Rebuffer ratio**: Отношение времени rebuffering к общему времени воспроизведения — индикатор проблем с сетью или кешем
- **Ошибки кодека**: Частота ошибок `MediaCodec` — индикатор проблем с совместимостью устройств
- **ANR/Crashes**: Мониторинг `ANR` и крэшей — критично для стабильности
- **Cache hit rate**: Процент запросов, обслуженных из кеша — индикатор эффективности кеширования
- **Upload retries**: Количество повторных попыток загрузки — индикатор проблем с сетью

Guardrails и безопасность:

- **Kill-switches**: Feature flags для экстренного отключения кодеков (`HEVC`), размеров сегментов, prefetch — отключение проблемных фич без нового релиза
- **Staged rollout**: Постепенный запуск новых фич (1% → 5% → 25% → 100%) с мониторингом метрик на каждом этапе
- **Авто-откат**: Автоматический откат при деградации ключевых метрик (рост ANR, падение cache hit rate) — защита от проблемных релизов

**Тестирование и Релиз:**

Стратегия тестирования:

- **Unit тесты**: Тесты фильтров (`OpenGL` shaders), конфигов кодера (`MediaCodec` parameters), state machines (`ViewModel` логика)
- **Integration тесты**: Тесты `ExoPlayer` с throttled network — проверка ABR и graceful degradation
- **Performance тесты**: Перф-тесты на матрице устройств (low-end, mid-tier, high-end) — проверка соответствия SLA (экспорт <3s, старт <150ms)
- **Golden tests**: Тесты запись→воспроизведение — проверка, что записанное видео корректно воспроизводится
- **Beta тестирование**: Постепенный запуск на 5-10% пользователей с мониторингом метрик перед полным релизом

**Последовательность разработки:**

MVP → Hardening → Scale:

1.   **MVP**: Базовый захват → `H.264` кодирование → одношаговая загрузка → простое воспроизведение без prefetch
2.   **Hardening**: Добавление prefetch, многоуровневого кеша, возобновляемых загрузок, обработка ошибок сети
3.   **Scale**: Оптимизация с `ABR`, `HEVC` под флагом, термальная адаптация, A/B тестирование для оптимизации метрик

**Компромиссы (Trade-offs):**

- Сегменты по ~1 секунде уменьшают ощутимую задержку старта, но увеличивают нагрузку на CDN (больше запросов). Более длинные сегменты (2-3 секунды) снижают overhead, но могут увеличить время до первого кадра.
- `HEVC` уменьшает требуемый битрейт на 30-50%, но ухудшает совместимость (поддерживается не на всех устройствах). Решение: включать через feature flag и всегда иметь fallback на `H.264`.

**Доступность и устойчивость UX:**

- **TalkBack labels**: Корректные `contentDescription` для всех интерактивных элементов (кнопки записи, свайпы, переходы) — поддержка для пользователей с нарушениями зрения
- **Captions/Subtitles**: Автоматические или пользовательские субтитры для видео stories — поддержка для пользователей с нарушениями слуха
- **Larger tap targets**: Минимальный размер тач-таргетов 48dp для удобства нажатия — поддержка для пользователей с ограниченной моторикой
- **Retry flows**: Четкие UI-сообщения и кнопки повтора при обрыве сети или ошибках загрузки — улучшение UX при сбоях

## Answer (EN)

`Instagram Stories` is a system for creating, uploading, playing, and auto-deleting media after 24 hours. Key requirements: fast video capture (15 seconds @ 720p/30fps), optimized export (<3 seconds p95), smooth playback (target p95 startup <150ms with effective prefetch/cache), support for intermittent connectivity, and efficient device resource usage (battery, thermal, memory).

### Requirements

**Functional:**
- Capture, edit (filters/text/stickers), and publish stories.
- Background and resumable media upload.
- Automatic expiration and hiding of stories after 24 hours.
- Stories tray and viewer with fast switching and prefetch.
- `View` tracking and basic analytics.

**Non-functional:**
- p95 playback startup <150ms with caching/prefetch where possible.
- p95 export time <3 seconds on mid-tier devices.
- Robust behavior under flaky networks (offline-first, chunked upload, retries).
- Scalable backend and efficient CDN usage.
- Minimal impact on battery, memory, and thermal constraints.

### Architecture

**Android client:**

Architecture follows `Clean Architecture` principles with clear layer separation:

- **Domain Layer**: Contains business logic — `Story` entity with fields (id, userId, mediaUrl, createdAt, expiresAt), TTL logic (24 hours), validation rules (max duration 15 seconds, target 720p resolution, optionally keep higher-res source up to 1080p for server-side transcoding)
- **Data Layer**: `Repository Pattern` for data source abstraction — `StoryRepository` coordinates local storage (`Room`), network requests (`Retrofit`), and cache (`OkHttp` cache, `LruCache`). Handles synchronization on network recovery
- **Presentation Layer**: `MVVM` for camera and viewer — `CameraViewModel` manages capture and export, `StoryPlayerViewModel` manages playback and prefetch. Uses `Coroutines` and `Flow` for reactivity

**Technology stack:**

- **`WorkManager`** for reliable background upload with automatic retries, constraints (network, charging), and `Doze Mode` integration
- **`ExoPlayer`** for video — supports `HLS`/`DASH`, `ABR` (Adaptive Bitrate), prefetching, and graceful degradation on low-end devices
- **`Coil`** for images — efficient loading and caching with transformation support
- **Multi-level cache**: `Memory Cache` (`LruCache`) → `Disk Cache` (`OkHttp` disk cache, `Room`) → `Network` (CDN with prefetch controlled by backend policies)

**Backend:**

- **API**: RESTful API for upload (`POST /stories/upload`), list retrieval (`GET /stories/{userId}`), transcoding (async jobs via `Kafka`/`RabbitMQ`), TTL jobs (periodic cleanup via `Cron`), and ACL (access control validation for other users' stories)
- **Storage**: `S3`/`GCS` for media files with lifecycle policies for automatic deletion after 24 hours, CDN (`CloudFront`/`Cloudflare`) for global distribution with edge caching, metadata in `PostgreSQL`/`MongoDB` with indexes on `userId` and `expiresAt` for fast cleanup
- **Realtime**: `WebSocket`/`Pub-Sub` (`Redis Pub/Sub`, `Kafka`) for real-time view counters, upload status updates, and push notifications for new stories from subscriptions

### Key Flows

**Create and Upload:**

Creation process includes video capture via `CameraX`/`Camera2`, AR effects via `OpenGL ES`, and encoding via `MediaCodec`. After capture, media is compressed and uploaded in background via `WorkManager`.

```kotlin
//  Reliable upload with retries and progress (pseudocode)
class UploadStoryWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    return try {
      val uri = inputData.getString("uri")!!
      // Compression: JPEG/WEBP for preview, H.264 for video, ~4-6Mbps bitrate for 720p/30fps
      val compressed = compressMedia(uri)

      // Upload with progress via callback
      storyRepo.upload(
        compressed,
        // Use real epoch millis; this line is illustrative
        expiresAt = System.currentTimeMillis() + 24 * 60 * 60 * 1000L,
        onProgress = { progress -> setProgress(workDataOf("progress" to progress)) }
      )
      Result.success()
    } catch (e: Exception) {
      // Exponential backoff is configured on the WorkRequest
      if (runAttemptCount < 3) Result.retry() else Result.failure()
    }
  }
}
```

**Implementation details:**

- **Compression**: Use `MediaCodec` with `H.264` codec (Baseline profile for compatibility, High profile for better quality), bitrate 4-6 Mbps for 720p/30fps, `GOP` (Group of Pictures) ≈ 1 second for fast playback startup
- **Chunked upload**: Split files into 4-8MB chunks for resumability on network interruption, use `SHA-256` hashing per chunk for integrity verification
- **Resumability**: On network recovery, `WorkManager` ensures persisted work and retries; the client and server implement offset negotiation to continue from the last confirmed chunk

**Playback:**

Playback must start as fast as possible and be smooth (60fps on modern devices). Prefetching strategy preloads next stories.

- **Prefetching**: Preload current story + next 2 stories in parallel — first segments load in background while user watches current
- **Caching**: `OkHttp` disk cache for segment storage on disk (~250MB limit), `LruCache` in memory for previews and first segments of current story (fast access without I/O)
- **Battery**: Pause `ExoPlayer` when app goes to background to save battery, resume on foreground return
- **Adaptive quality**: `ABR` (Adaptive Bitrate) — `ExoPlayer` automatically selects optimal bitrate based on network bandwidth and device performance
- **Graceful degradation**: On low-end devices — cap at 30fps, select smaller resolutions from ladder, disable heavy transitions between stories

**TTL (24 hours):**

Stories automatically expire 24 hours after creation. Periodic cleanup removes expired stories from device and cache.

```kotlin
//  Periodic cleanup of expired stories (pseudocode)
class CleanupExpiredWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    val now = System.currentTimeMillis()

    // Delete from local DB
    storyRepo.deleteExpired(before = now)

    // Clear cache (disk and memory)
    cacheManager.evict { story -> story.expiresAt < now }

    // Invalidate CDN cache (if supported via backend API)
    cdnCacheManager.invalidateExpired()

    return Result.success()
  }
}
```

**Cleanup strategy:**

- **Frequency**: Run `CleanupExpiredWorker` every 6 hours via `PeriodicWorkRequest` — balance between cleanup frequency and system load
- **Local storage**: Delete from `Room` database with cascade deletion of related metadata (previews, thumbnails)
- **Cache**: Eviction from `OkHttp` disk cache and `LruCache` by `expiresAt < now` — free space for new stories
- **Optimization**: Indexes in DB on `expiresAt` for fast expired-story lookup, batch deletion for efficiency

### Performance Optimization

**Offline-first approach:**

- **Upload queue**: `WorkManager` queues uploads on network absence — users can create stories offline, they upload on connection recovery
- **Local DB**: `Room` stores story metadata (id, userId, expiresAt, uploadStatus) even without network — enables displaying locally created stories before upload
- **Synchronization**: On network recovery, use `WorkManager` constraints to control when uploads run (e.g., Wi-Fi / charging only)

**CDN optimization:**

- **Signed URLs**: CDN/origin issues temporary signed URLs with short TTL (1-2 hours) for security — prevents unauthorized access to expired stories
- **Edge caching**: Caching on CDN edge servers closer to users — reduces latency for global audience
- **CDN prefetch**: Backend-driven aggressive caching/prefetching for popular users' stories — reduces delay when switching stories

**Backend scaling:**

- **Partitioning**: Data partitioning by `userId` (sharding) — distributes load across multiple DB instances
- **Denormalization**: Store `seen/unseen` ring in denormalized form for fast display — avoids complex JOIN queries
- **Read replicas**: Use read replicas to reduce master DB load — scale reads independently from writes

### Detailed Implementation Capture Pipeline

**Module architecture:**

Modular structure separates functionality by feature modules for independent development and testing:

- **feature-stories-capture**: Capture module — `CameraViewModel`, camera UI, AR effects processing
- **feature-stories-playback**: Playback module — `StoryPlayerViewModel`, `ExoPlayer` integration, viewer UI
- **media-core**: Common media module — `CameraX`/`Camera2` wrappers, `OpenGL ES` rendering, `MediaCodec` encoding
- **upload**: Upload module — `WorkManager` workers, chunked upload logic, retry strategies
- **cache**: Caching module — multi-level cache (`Memory`, `Disk`, `Network`), eviction policies
- **analytics**: Analytics module — performance metrics, errors, user engagement
- **flags**: Feature flags — dynamic control of codec (`H.264`/`HEVC`), segment length, prefetch size

**Architecture patterns:**

- **MVVM + unidirectional data flow**: `ViewModel` contains business logic and state, `View` (Compose/Views) only displays state and sends events back to `ViewModel`. `Flow` provides reactivity
- **DI (Hilt)**: Dependency injection for managing dependencies between modules — ease of testing and maintenance

**Video capture:**

Camera choice:

- **CameraX (recommended)**: Wide device compatibility (API 21+), simplified API, automatic lifecycle handling. Suitable for most cases
- **Camera2 (fallback)**: Use for manual control (manual exposure, focus, RAW capture) or when maximum performance is needed on modern devices

Render pipeline:

- **Zero-copy path**: `Camera` → `SurfaceTexture` → `OpenGL ES` → `Surface(Encoder)` — camera data enters `OpenGL` context without extra memory copy, then rendered to encoder `Surface`. Minimizes latency and memory usage
- **AR effects**: Apply filters via `OpenGL ES` shaders — processing on GPU in parallel with capture, minimal overhead

Encoder configuration:

- **Codec**: `MediaCodec` with `H.264` codec (Baseline profile for maximum compatibility, High profile for better compression). `HEVC` (H.265) behind feature flag for supported devices — 30-50% better compression, but higher CPU/GPU requirements
- **Bitrate**: 4-6 Mbps @ 720p/30fps — balance between quality and file size. Use `CBR`-biased `VBR` (Variable Bitrate with stability emphasis) for predictable file size
- **GOP (Group of Pictures)**: GOP ≈ 1 second (30 frames at 30fps) — short `GOP` enables faster playback startup as `I-frame` appears more frequently
- **Audio**: `AAC` codec, bitrate 128-192 kbps — sufficient quality for voice and music
- **Multiplexing**: `MediaMuxer` combines video and audio tracks into `MP4` container — standard format with wide support

Thermal and battery management:

- **Thermal throttling**: Monitor temperature via `ThermalManager` (API 29+). On overheating — downscale to 540p, reduce bitrate to 2-3 Mbps, disable heavy AR filters
- **Battery optimization**: Use `JobScheduler` constraints for upload only when charging (optional), reduce frame rate to 24fps at low battery

**Upload pipeline:**

Pre-upload optimizations:

- **Thumbnail/Preview**: Generate low-resolution preview (`JPEG` 320x240) for fast UI display before main file upload completes
- **Perceptual hash**: Compute perceptual hash (e.g., `pHash`) for deduplication — prevents re-uploading identical content

Chunked upload:

- **Chunk size**: 4-8MB — balance between request count and resumability. Smaller chunks increase HTTP requests, larger reduce flexibility on interruption
- **Integrity**: `SHA-256` hashing per chunk for server-side integrity verification — detects corruption during transfer
- **Resumability**: Offset negotiation — server reports last successfully uploaded byte, client continues from that offset. `WorkManager` persists task state and reschedules if needed; the resumable protocol is implemented in app/backend
- **Security**: `TLS` for transport, optionally client-side `AES-GCM` encryption for critical data before upload

WorkManager integration:

- **Constraints**: Upload only on network (`NetworkType.CONNECTED`), optionally only on Wi-Fi or charging — saves mobile data and battery
- **Exponential backoff**: Automatic delay between retries with exponential increase to prevent server overload
- **Doze Mode**: `WorkManager` respects `Doze Mode` and `App Standby` — work deferred to maintenance windows per platform rules

**Playback system:**

ExoPlayer configuration:

- **Format**: `HLS`/`DASH` with ~1 second segments — short segments help reduce time-to-first-frame when cached/prefetched; actual p95 startup depends on network and implementation
- **ABR (Adaptive Bitrate)**: Multiple bitrates in manifest — `ExoPlayer` automatically selects optimal bitrate based on current network bandwidth and device performance
- **Bitrate ladder**: Multiple quality options (e.g., 1080p @ 8Mbps, 720p @ 4Mbps, 480p @ 2Mbps, 360p @ 1Mbps) — smooth adaptation to conditions

Prefetch strategy:

- **Volume**: Prefetch first 2-3 segments of next story in parallel with current playback — user doesn't wait on swipe
- **Cancellation**: On swipe away from prefetched story — immediate cancellation of in-flight loads to save data and battery

On-device cache:

- **Size**: `LRU` cache ~250MB on disk — balance between volume and device storage usage
- **Eviction policy**: Removal by time (expired stories), by last viewed (`LRU`), and by size — free space for new stories
- **Optimization**: Store only first N segments for less frequently viewed stories — save space, full load on demand

Graceful degradation:

- **Low-end devices**: Cap at 30fps (instead of 60fps), select smaller resolutions from ladder (480p instead of 720p), disable heavy transitions (fade, slide) — preserve playback smoothness

Audio focus and PiP:

- **Audio focus**: Handle `AUDIOFOCUS_LOSS` to pause playback on call or other audio app
- **PiP (Picture-in-Picture)**: Support `Picture-in-Picture` mode (API 24+) for viewing stories in small window over other apps

**Observability and Operations:**

Performance metrics:

- **Startup p95**: 95th percentile playback startup time — target <150ms with strong prefetch/caching
- **Export p95**: 95th percentile video export time — target <3 seconds on mid-tier devices
- **Rebuffer ratio**: Ratio of rebuffering time to total playback time — indicator of network or cache issues
- **Codec errors**: Frequency of `MediaCodec` errors (failure to configure, encoding errors) — indicator of device compatibility issues
- **ANR/Crashes**: Monitor `ANR` and crashes — critical for stability
- **Cache hit rate**: Percentage of requests served from cache — indicator of caching effectiveness
- **Upload retries**: Number of upload retry attempts — indicator of network issues

Guardrails and safety:

- **Kill-switches**: Feature flags for emergency disabling of codecs (`HEVC`), segment sizes, prefetch — quick disable of problematic features without release
- **Staged rollout**: Gradual new feature launch (1% → 5% → 25% → 100%) with metrics monitoring at each stage
- **Auto-rollback**: Automatic rollback on key metric degradation (ANR increase, cache hit rate decrease) — protection from problematic releases

**Testing and Release:**

Testing strategy:

- **Unit tests**: Tests for filters (`OpenGL` shaders), encoder configs (`MediaCodec` parameters), state machines (`ViewModel` logic)
- **Integration tests**: `ExoPlayer` tests with throttled network — verify ABR and graceful degradation
- **Performance tests**: Perf tests on device matrix (low-end, mid-tier, high-end) — verify SLA compliance (export <3s, startup <150ms)
- **Golden tests**: Record→playback tests — verify recorded video plays correctly (integrity check)
- **Beta testing**: Gradual launch to 5-10% users with metrics monitoring before full release

**Development sequence:**

MVP → Hardening → Scale:

1.   **MVP**: Basic capture → `H.264` encoding → single-step upload → simple playback without prefetch
2.   **Hardening**: Add prefetch, multi-level cache, resumable uploads, network error handling
3.   **Scale**: Optimization with `ABR`, `HEVC` behind flag, thermal adaptation, A/B testing for metric optimization

**Trade-offs:**

- `Short` 1s segments reduce perceived start latency but increase CDN overhead (more requests). Longer segments (2-3s) reduce overhead but can increase startup time
- `HEVC` reduces bitrate by 30-50% but risks compatibility (not all devices support). Use feature flags and fallback (e.g., also provide `H.264`) where needed

**Accessibility & UX resilience:**

- **TalkBack labels**: Correct `contentDescription` for all interactive elements (record button, swipes, transitions) — support for visually impaired users
- **Captions/Subtitles**: Automatic or user-generated subtitles for video stories — support for hearing impaired users
- **Larger tap targets**: Minimum 48dp tap target size for easier tapping — support for users with limited motor skills
- **Retry flows**: Clear UI messages and retry buttons on network interruption or upload errors — improved UX on failures

## Дополнительные Вопросы (RU)

- Как обрабатывать неудачи транскодирования видео и стратегию повторных попыток?
- Какую стратегию кеширования выбрать, чтобы минимизировать трафик и обеспечить плавное воспроизведение?
- Как реализовать эффективный preloading без чрезмерного расхода батареи?
- Какие меры безопасности предотвратят несанкционированный доступ к истекшим stories?
- Как оптимизировать конфигурацию `MediaCodec` под разные классы устройств?
- Какие стратегии улучшают время старта `ExoPlayer` на слабых устройствах?

## Follow-ups

- How to handle video transcoding failures and retry strategies?
- What caching strategy minimizes bandwidth while ensuring smooth playback?
- How to implement efficient preloading without draining battery?
- What security measures prevent unauthorized access to expired stories?
- How to optimize `MediaCodec` configuration for different device capabilities?
- What strategies improve `ExoPlayer` startup time on low-end devices?

## Ссылки (RU)

- [Android Media APIs](https://developer.android.com/guide/topics/media)
- [Android Background Tasks](https://developer.android.com/guide/background)
- [CameraX Documentation](https://developer.android.com/training/camerax)
- [ExoPlayer Documentation](https://developer.android.com/guide/topics/media/exoplayer)
- [MediaCodec API](https://developer.android.com/reference/android/media/MediaCodec)
- [[c-android]]

## References

- [Android Media APIs](https://developer.android.com/guide/topics/media)
- [Android Background Tasks](https://developer.android.com/guide/background)
- [CameraX Documentation](https://developer.android.com/training/camerax)
- [ExoPlayer Documentation](https://developer.android.com/guide/topics/media/exoplayer)
- [MediaCodec API](https://developer.android.com/reference/android/media/MediaCodec)
- [[c-android]]

## Связанные Вопросы (RU)

### Предварительные Знания

- Понимание политик повторных попыток и ограничений `WorkManager`
- Базовые знания `ExoPlayer` для видео-воспроизведения

### Связанные

- [[q-data-sync-unstable-network--android--hard]]
- [[q-database-optimization-android--android--medium]]

### Продвинутые

- Проектирование стратегии CDN-кеширования для эфемерного контента
- Реализация счетчиков просмотров в реальном времени на масштабе Instagram

## Related Questions

### Prerequisites

- Understanding of WorkManager retry policies and constraints
- ExoPlayer basics for video playback

### Related

- [[q-data-sync-unstable-network--android--hard]]
- [[q-database-optimization-android--android--medium]]

### Advanced

- Design a CDN caching strategy for ephemeral content
- Implement real-time view counters at Instagram scale
