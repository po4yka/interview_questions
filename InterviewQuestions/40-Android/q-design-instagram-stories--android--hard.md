---
id: 20251006-000002
title: "How to design Instagram Stories feature? / Как спроектировать функцию Instagram Stories?"
aliases: []

# Classification
topic: system-design
subtopics: [media, real-time, video-streaming, architecture, mobile-app-design]
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
related: [video-streaming, image-processing, caching, offline-first]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [system-design, instagram, stories, media, video, architecture, android, difficulty/hard]
---
## Question (EN)
> How would you design the Instagram Stories feature for Android?
## Вопрос (RU)
> Как бы вы спроектировали функцию Instagram Stories для Android?

---

## Answer (EN)

Instagram Stories is a complex feature involving media capture, processing, storage, real-time viewing, and expiration. Here's a comprehensive system design:

### 1. Core Requirements

**Functional Requirements:**
- Create stories (photo/video up to 15 seconds)
- Add filters, stickers, text, drawings
- View stories from followed users
- Story ring indicator (seen/unseen)
- Story expiration after 24 hours
- View count and viewer list
- Reply to stories via DM
- Share stories to close friends
- Story highlights (permanent stories)
- Swipe navigation between stories

**Non-Functional Requirements:**
- Fast story upload (< 5 seconds)
- Smooth playback (no buffering)
- Minimal storage usage
- Low battery consumption
- Efficient media compression
- Handle poor network conditions

### 2. High-Level Architecture

```
┌─────────────────────┐
│   Android Client    │
│  ┌──────────────┐   │
│  │ Camera       │   │
│  │ Media Editor │   │
│  │ Story Viewer │   │
│  └──────────────┘   │
└──────────┬──────────┘
           │
           ├─── REST API (Upload/Download)
           ├─── CDN (Media Delivery)
           └─── WebSocket (Real-time updates)
           │
┌──────────▼──────────┐
│   Backend Services  │
│  ┌──────────────┐   │
│  │ Media        │   │
│  │ Processing   │   │
│  │ Service      │   │
│  └──────────────┘   │
│  ┌──────────────┐   │
│  │ Story        │   │
│  │ Expiration   │   │
│  │ Worker       │   │
│  └──────────────┘   │
└─────────────────────┘
           │
           ├─── Object Storage (S3)
           ├─── Database (Stories metadata)
           └─── Cache (Redis)
```

### 3. Android App Architecture

#### Data Models

```kotlin
@Entity(tableName = "stories")
data class Story(
    @PrimaryKey val id: String,
    val userId: String,
    val mediaUrl: String,
    val thumbnailUrl: String,
    val mediaType: MediaType, // IMAGE, VIDEO
    val createdAt: Long,
    val expiresAt: Long,
    val viewCount: Int = 0,
    val isSeen: Boolean = false,
    val duration: Int = 5000 // milliseconds for images, actual for videos
)

data class StoryBucket(
    val userId: String,
    val userName: String,
    val userAvatar: String,
    val stories: List<Story>,
    val hasUnseenStories: Boolean,
    val lastUpdated: Long
)

enum class MediaType {
    IMAGE, VIDEO
}
```

#### Story Creation Flow

```kotlin
class CreateStoryUseCase @Inject constructor(
    private val mediaProcessor: MediaProcessor,
    private val storyRepository: StoryRepository,
    private val uploadManager: UploadManager
) {
    suspend operator fun invoke(
        mediaUri: Uri,
        filters: List<Filter>,
        stickers: List<Sticker>
    ): Result<Story> {
        return withContext(Dispatchers.IO) {
            try {
                // 1. Process media (compress, apply filters)
                val processedMedia = mediaProcessor.process(
                    uri = mediaUri,
                    filters = filters,
                    stickers = stickers,
                    maxDuration = 15_000 // 15 seconds
                )

                // 2. Generate thumbnail
                val thumbnail = mediaProcessor.generateThumbnail(processedMedia)

                // 3. Upload to server
                val uploadResult = uploadManager.uploadStory(
                    media = processedMedia,
                    thumbnail = thumbnail
                )

                // 4. Save metadata
                val story = Story(
                    id = uploadResult.storyId,
                    userId = getCurrentUserId(),
                    mediaUrl = uploadResult.mediaUrl,
                    thumbnailUrl = uploadResult.thumbnailUrl,
                    mediaType = getMediaType(mediaUri),
                    createdAt = System.currentTimeMillis(),
                    expiresAt = System.currentTimeMillis() + 24.hours.inWholeMilliseconds
                )

                storyRepository.saveStory(story)

                Result.Success(story)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
}
```

#### Media Processing

```kotlin
class MediaProcessor @Inject constructor(
    private val context: Context
) {
    suspend fun process(
        uri: Uri,
        filters: List<Filter>,
        stickers: List<Sticker>,
        maxDuration: Long
    ): File {
        return when (getMediaType(uri)) {
            MediaType.IMAGE -> processImage(uri, filters, stickers)
            MediaType.VIDEO -> processVideo(uri, filters, stickers, maxDuration)
        }
    }

    private suspend fun processImage(
        uri: Uri,
        filters: List<Filter>,
        stickers: List<Sticker>
    ): File = withContext(Dispatchers.Default) {
        // Load bitmap
        val bitmap = BitmapFactory.decodeStream(
            context.contentResolver.openInputStream(uri)
        )

        // Apply filters
        var processedBitmap = bitmap
        filters.forEach { filter ->
            processedBitmap = filter.apply(processedBitmap)
        }

        // Add stickers
        val canvas = Canvas(processedBitmap)
        stickers.forEach { sticker ->
            canvas.drawBitmap(sticker.bitmap, sticker.x, sticker.y, null)
        }

        // Compress (max 1080x1920, JPEG quality 85%)
        val compressed = compressImage(
            processedBitmap,
            maxWidth = 1080,
            maxHeight = 1920,
            quality = 85
        )

        // Save to temp file
        val outputFile = File(context.cacheDir, "story_${UUID.randomUUID()}.jpg")
        FileOutputStream(outputFile).use { out ->
            compressed.compress(Bitmap.CompressFormat.JPEG, 85, out)
        }

        outputFile
    }

    private suspend fun processVideo(
        uri: Uri,
        filters: List<Filter>,
        stickers: List<Sticker>,
        maxDuration: Long
    ): File = withContext(Dispatchers.IO) {
        // Use MediaCodec or FFmpeg for video processing
        val outputFile = File(context.cacheDir, "story_${UUID.randomUUID()}.mp4")

        // Trim video to max 15 seconds
        val trimCommand = "-i $uri -t ${maxDuration / 1000} -c:v libx264 " +
                "-preset ultrafast -crf 28 -c:a aac -b:a 128k $outputFile"

        // Execute FFmpeg command
        FFmpegKit.execute(trimCommand)

        // Compress video (max 1080x1920, 2Mbps bitrate)
        compressVideo(
            inputFile = outputFile,
            maxWidth = 1080,
            maxHeight = 1920,
            bitrate = 2_000_000 // 2 Mbps
        )

        outputFile
    }

    fun generateThumbnail(mediaFile: File): File {
        val thumbnail = if (isVideo(mediaFile)) {
            extractVideoThumbnail(mediaFile)
        } else {
            // For images, create smaller version
            val bitmap = BitmapFactory.decodeFile(mediaFile.absolutePath)
            Bitmap.createScaledBitmap(bitmap, 200, 355, true)
        }

        val thumbnailFile = File(context.cacheDir, "thumb_${UUID.randomUUID()}.jpg")
        FileOutputStream(thumbnailFile).use { out ->
            thumbnail.compress(Bitmap.CompressFormat.JPEG, 80, out)
        }

        return thumbnailFile
    }
}
```

#### Story Upload

```kotlin
class UploadManager @Inject constructor(
    private val apiService: ApiService,
    private val workManager: WorkManager
) {
    suspend fun uploadStory(
        media: File,
        thumbnail: File
    ): UploadResult {
        // Create multipart request
        val mediaBody = media.asRequestBody("video/mp4".toMediaTypeOrNull())
        val mediaPart = MultipartBody.Part.createFormData(
            "media",
            media.name,
            mediaBody
        )

        val thumbnailBody = thumbnail.asRequestBody("image/jpeg".toMediaTypeOrNull())
        val thumbnailPart = MultipartBody.Part.createFormData(
            "thumbnail",
            thumbnail.name,
            thumbnailBody
        )

        // Upload with progress tracking
        return apiService.uploadStory(mediaPart, thumbnailPart)
    }

    // Background upload using WorkManager
    fun enqueueUpload(media: File, thumbnail: File) {
        val data = Data.Builder()
            .putString("media_path", media.absolutePath)
            .putString("thumbnail_path", thumbnail.absolutePath)
            .build()

        val uploadWork = OneTimeWorkRequestBuilder<StoryUploadWorker>()
            .setInputData(data)
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        workManager.enqueue(uploadWork)
    }
}
```

#### Story Viewer

```kotlin
class StoryViewerViewModel @Inject constructor(
    private val storyRepository: StoryRepository,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() {

    private val _currentStoryBucket = MutableStateFlow<StoryBucket?>(null)
    val currentStoryBucket = _currentStoryBucket.asStateFlow()

    private val _currentStoryIndex = MutableStateFlow(0)
    val currentStoryIndex = _currentStoryIndex.asStateFlow()

    fun loadStories(userId: String) {
        viewModelScope.launch {
            storyRepository.getStoriesByUser(userId)
                .collect { bucket ->
                    _currentStoryBucket.value = bucket
                    _currentStoryIndex.value = bucket.stories.indexOfFirst { !it.isSeen }
                        .takeIf { it >= 0 } ?: 0
                }
        }
    }

    fun onStoryViewed(storyId: String) {
        viewModelScope.launch {
            // Mark as seen
            storyRepository.markAsSeen(storyId)

            // Track analytics
            analyticsTracker.trackStoryView(storyId)

            // Move to next story
            moveToNextStory()
        }
    }

    private fun moveToNextStory() {
        val bucket = _currentStoryBucket.value ?: return
        val currentIndex = _currentStoryIndex.value

        if (currentIndex < bucket.stories.size - 1) {
            _currentStoryIndex.value = currentIndex + 1
        } else {
            // Move to next user's stories
            loadNextUserStories()
        }
    }
}
```

#### Story Viewer UI (Jetpack Compose)

```kotlin
@Composable
fun StoryViewer(
    bucket: StoryBucket,
    currentIndex: Int,
    onStoryComplete: () -> Unit,
    onClose: () -> Unit,
    modifier: Modifier = Modifier
) {
    val story = bucket.stories[currentIndex]
    var isPaused by remember { mutableStateOf(false) }

    Box(modifier = modifier.fillMaxSize()) {
        // Story content
        when (story.mediaType) {
            MediaType.IMAGE -> {
                AsyncImage(
                    model = story.mediaUrl,
                    contentDescription = null,
                    modifier = Modifier.fillMaxSize(),
                    contentScale = ContentScale.Crop
                )
            }
            MediaType.VIDEO -> {
                VideoPlayer(
                    url = story.mediaUrl,
                    isPaused = isPaused,
                    onVideoEnd = onStoryComplete,
                    modifier = Modifier.fillMaxSize()
                )
            }
        }

        // Progress indicators
        StoryProgressIndicators(
            storyCount = bucket.stories.size,
            currentIndex = currentIndex,
            duration = story.duration,
            isPaused = isPaused,
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp)
                .align(Alignment.TopCenter)
        )

        // User info
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.TopStart),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = bucket.userAvatar,
                contentDescription = null,
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = bucket.userName,
                color = Color.White,
                fontWeight = FontWeight.Bold
            )
        }

        // Tap zones for navigation
        Row(modifier = Modifier.fillMaxSize()) {
            // Previous story
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight()
                    .clickable { /* Go to previous story */ }
            )
            // Next story
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight()
                    .clickable { onStoryComplete() }
            )
        }

        // Long press to pause
        Box(
            modifier = Modifier
                .fillMaxSize()
                .pointerInput(Unit) {
                    detectTapGestures(
                        onPress = {
                            isPaused = true
                            tryAwaitRelease()
                            isPaused = false
                        }
                    )
                }
        )
    }
}

@Composable
fun StoryProgressIndicators(
    storyCount: Int,
    currentIndex: Int,
    duration: Int,
    isPaused: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        repeat(storyCount) { index ->
            val progress = when {
                index < currentIndex -> 1f
                index == currentIndex -> {
                    var currentProgress by remember { mutableStateOf(0f) }

                    LaunchedEffect(isPaused) {
                        if (!isPaused) {
                            animate(
                                initialValue = currentProgress,
                                targetValue = 1f,
                                animationSpec = tween(
                                    durationMillis = ((1f - currentProgress) * duration).toInt(),
                                    easing = LinearEasing
                                )
                            ) { value, _ ->
                                currentProgress = value
                            }
                        }
                    }

                    currentProgress
                }
                else -> 0f
            }

            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier
                    .weight(1f)
                    .height(2.dp),
                color = Color.White,
                backgroundColor = Color.White.copy(alpha = 0.3f)
            )
        }
    }
}
```

### 4. Caching Strategy

```kotlin
class StoryCacheManager @Inject constructor(
    private val context: Context,
    private val diskCache: DiskCache
) {
    private val memoryCache = LruCache<String, Bitmap>(
        (Runtime.getRuntime().maxMemory() / 8).toInt()
    )

    // Preload next stories for smooth experience
    fun preloadStories(stories: List<Story>) {
        stories.take(3).forEach { story ->
            viewModelScope.launch(Dispatchers.IO) {
                when (story.mediaType) {
                    MediaType.IMAGE -> preloadImage(story.mediaUrl)
                    MediaType.VIDEO -> preloadVideo(story.mediaUrl)
                }
            }
        }
    }

    private suspend fun preloadImage(url: String) {
        val bitmap = Glide.with(context)
            .asBitmap()
            .load(url)
            .submit()
            .get()

        memoryCache.put(url, bitmap)
    }

    private suspend fun preloadVideo(url: String) {
        // Download first few segments for immediate playback
        diskCache.download(url, prefetchSize = 1_000_000) // 1MB
    }
}
```

### 5. Story Expiration

```kotlin
class StoryExpirationWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val storyDao = getDatabase().storyDao()

        // Delete expired stories
        val expiredStories = storyDao.getExpiredStories(System.currentTimeMillis())
        expiredStories.forEach { story ->
            // Delete from local storage
            deleteMediaFile(story.mediaUrl)
            deleteMediaFile(story.thumbnailUrl)

            // Delete from database
            storyDao.deleteStory(story.id)
        }

        return Result.success()
    }

    companion object {
        fun schedule(workManager: WorkManager) {
            val work = PeriodicWorkRequestBuilder<StoryExpirationWorker>(
                repeatInterval = 1,
                repeatIntervalTimeUnit = TimeUnit.HOURS
            ).build()

            workManager.enqueueUniquePeriodicWork(
                "story_expiration",
                ExistingPeriodicWorkPolicy.KEEP,
                work
            )
        }
    }
}
```

### Best Practices

1. **Media Compression**: Compress images to max 1080x1920, videos to 2Mbps bitrate
2. **Preloading**: Preload next 2-3 stories for smooth navigation
3. **Caching**: Use multi-level cache (Memory → Disk → Network)
4. **Background Upload**: Use WorkManager for reliable uploads
5. **Battery Optimization**: Stop video playback when app goes to background
6. **Network Optimization**: Use adaptive streaming for videos
7. **Storage Management**: Auto-delete expired stories, limit cache size

### Common Pitfalls

1. Not compressing media leading to large files and slow uploads
2. Loading all stories at once causing memory issues
3. Poor video playback performance
4. Not handling story expiration
5. Inefficient caching strategy
6. Not optimizing for poor network conditions
7. Battery drain from continuous video processing

## Ответ (RU)

Instagram Stories - это сложная функция, включающая захват, обработку, хранение медиа, просмотр в реальном времени и автоматическое удаление. Вот комплексный системный дизайн:

### 1. Основные требования

**Функциональные требования:**
- Создание stories (фото/видео до 15 секунд)
- Добавление фильтров, стикеров, текста, рисунков
- Просмотр stories от отслеживаемых пользователей
- Индикатор кольца (просмотрено/не просмотрено)
- Автоматическое удаление через 24 часа
- Счетчик просмотров и список зрителей
- Ответ на stories через личные сообщения
- Публикация для близких друзей
- Highlights (постоянные stories)
- Навигация свайпом между stories

**Нефункциональные требования:**
- Быстрая загрузка stories (< 5 секунд)
- Плавное воспроизведение (без буферизации)
- Минимальное использование хранилища
- Низкое потребление батареи
- Эффективное сжатие медиа
- Работа в условиях плохой сети

### 2. Архитектура приложения

Приложение использует многослойную архитектуру с компонентами:
- Camera и Media Editor для создания контента
- Story Viewer для просмотра
- REST API для загрузки/скачивания
- CDN для доставки медиа
- WebSocket для обновлений в реальном времени

### 3. Процесс создания Story

**Обработка медиа:**
1. Захват фото/видео с камеры
2. Применение фильтров и эффектов
3. Сжатие (изображения до 1080x1920, видео до 2Mbps)
4. Генерация превью
5. Загрузка на сервер
6. Сохранение метаданных

**Сжатие изображений:**
- Максимальное разрешение: 1080x1920
- Формат: JPEG с качеством 85%
- Применение фильтров через Canvas API
- Наложение стикеров

**Обработка видео:**
- Обрезка до 15 секунд максимум
- Сжатие с использованием H.264 кодека
- Bitrate: 2 Mbps
- Использование FFmpeg или MediaCodec
- Генерация превью из первого кадра

### 4. Просмотр Stories

**Архитектура просмотра:**
- ViewPager2 для навигации между пользователями
- ExoPlayer для воспроизведения видео
- Coil/Glide для загрузки изображений
- Индикаторы прогресса для каждой story
- Зоны нажатий для навигации

**Механизм прогресса:**
- Автоматический переход каждые 5 секунд для изображений
- Продолжительность видео определяет время показа
- Пауза при долгом нажатии
- Анимация прогресс-баров

**Навигация:**
- Нажатие слева - предыдущая story
- Нажатие справа - следующая story
- Свайп вниз - закрыть просмотр
- Свайп влево/вправо - переход между пользователями

### 5. Стратегия кэширования

**Многоуровневое кэширование:**
- Memory Cache (LruCache) для недавно просмотренных
- Disk Cache для офлайн доступа
- Предзагрузка следующих 2-3 stories
- Удаление кэша просроченных stories

**Оптимизация загрузки:**
- Приоритет загрузки текущей и следующей story
- Adaptive streaming для видео
- Прогрессивная загрузка медиа
- Использование CDN для быстрой доставки

### 6. Автоматическое удаление

**Механизм истечения:**
- WorkManager для периодической проверки (каждый час)
- Удаление stories старше 24 часов
- Очистка локальных файлов
- Удаление из базы данных
- Уведомление сервера об удалении

### 7. Оптимизация производительности

**Батарея:**
- Остановка воспроизведения при сворачивании
- Ленивая загрузка stories
- Эффективное использование ExoPlayer
- Отмена предзагрузки при низком заряде

**Память:**
- Пагинация списка stories
- Освобождение ресурсов после просмотра
- Ограничение размера кэша
- Bitmap pooling

**Сеть:**
- Адаптивное качество в зависимости от скорости
- Пакетная загрузка метаданных
- Сжатие медиа перед отправкой
- Возобновление прерванных загрузок

### Лучшие практики

1. **Сжатие медиа**: Всегда сжимать перед загрузкой
2. **Предзагрузка**: Загружать следующие stories заранее
3. **Кэширование**: Использовать многоуровневый кэш
4. **Фоновая загрузка**: WorkManager для надежной загрузки
5. **Оптимизация батареи**: Останавливать воспроизведение в фоне
6. **Управление хранилищем**: Автоудаление просроченных stories

### Частые ошибки

1. Отсутствие сжатия медиа → большие файлы и медленная загрузка
2. Загрузка всех stories сразу → проблемы с памятью
3. Плохая производительность видео
4. Необработка истечения stories
5. Неэффективная стратегия кэширования
6. Отсутствие оптимизации для плохой сети
7. Разряд батареи от постоянной обработки видео

---

## References
- [ExoPlayer Documentation](https://exoplayer.dev/)
- [FFmpeg Android](https://github.com/tanersener/ffmpeg-kit)
- [Android Camera2 API](https://developer.android.com/training/camera2)
- [Glide Caching](https://bumptech.github.io/glide/doc/caching.html)
- [Video Compression Techniques](https://developer.android.com/guide/topics/media/mediacodec)

## Related Questions
- How to implement video player in Android?
- What is the best way to compress videos?
- How to implement image filters in Android?
- How to optimize media caching?
- What is ExoPlayer and when to use it?
