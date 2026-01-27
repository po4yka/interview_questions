---
id: android-755
title: Offline-First Architecture on Android / Offline-First архитектура на Android
aliases:
- Offline-First Architecture on Android
- Offline-First архитектура на Android
topic: android
subtopics:
- networking
- architecture-clean
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-networking
- q-data-sync-unstable-network--android--hard
- q-network-connectivity--networking--medium
- q-cache-implementation-strategies--android--medium
created: 2026-01-23
updated: 2026-01-23
sources:
- https://developer.android.com/topic/architecture/data-layer/offline-first
- https://developer.android.com/training/data-storage/room
- https://developer.android.com/topic/libraries/architecture/workmanager
tags:
- android/networking
- android/architecture-clean
- difficulty/hard
- offline-first
- room
- sync
- workmanager
- conflict-resolution
anki_cards:
- slug: android-755-0-en
  language: en
- slug: android-755-0-ru
  language: ru
---
# Вопрос (RU)

> Как построить offline-first архитектуру на Android? Объясните стратегии синхронизации, разрешение конфликтов и управление состоянием.

# Question (EN)

> How do you build an offline-first architecture on Android? Explain sync strategies, conflict resolution, and state management.

---

## Ответ (RU)

**Offline-first** архитектура предполагает, что локальная база данных является единственным источником истины (single source of truth), а синхронизация с сервером происходит асинхронно в фоновом режиме. Это обеспечивает мгновенный отклик UI и работоспособность приложения без сети.

### Краткий Ответ

- **Локальная БД** (Room) как единственный источник истины
- **Repository Pattern** для абстракции local/remote источников
- **WorkManager** для надежной фоновой синхронизации
- **Conflict Resolution**: Last-Write-Wins, Merge, или CRDT для сложных случаев

### Подробный Ответ

### Архитектура Offline-First

```
┌─────────────────────────────────────────────────────────────┐
│                           UI Layer                          │
│  (Compose / ViewModel - читает только из Local DB)         │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Repository                              │
│  - Записывает сначала в Local DB                            │
│  - Ставит операции в очередь синхронизации                  │
│  - Возвращает данные из Local DB                            │
└─────────────────────────┬───────────────────────────────────┘
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌──────────▼──────────┐
│   Local DB        │         │   Sync Engine       │
│   (Room/SQLite)   │         │   (WorkManager)     │
│                   │         │                     │
│ - Единственный    │         │ - Push локальных    │
│   источник истины │         │   изменений         │
│ - Offline доступ  │         │ - Pull удаленных    │
│ - Sync metadata   │         │   обновлений        │
└───────────────────┘         │ - Conflict resolve  │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │    Remote API       │
                              │    (REST/GraphQL)   │
                              └─────────────────────┘
```

### Data Layer: Room + Sync Metadata

```kotlin
// Сущность с метаданными синхронизации
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val createdAt: Long,
    val updatedAt: Long,

    // Sync metadata
    @ColumnInfo(name = "sync_status")
    val syncStatus: SyncStatus = SyncStatus.SYNCED,

    @ColumnInfo(name = "local_version")
    val localVersion: Int = 0,

    @ColumnInfo(name = "server_version")
    val serverVersion: Int = 0,

    @ColumnInfo(name = "deleted_locally")
    val deletedLocally: Boolean = false
)

enum class SyncStatus {
    SYNCED,           // Синхронизировано с сервером
    PENDING_CREATE,   // Создано локально, ожидает отправки
    PENDING_UPDATE,   // Обновлено локально, ожидает отправки
    PENDING_DELETE,   // Удалено локально, ожидает отправки
    CONFLICT          // Конфликт с серверной версией
}

@Dao
interface NoteDao {
    // UI читает только не удаленные заметки
    @Query("SELECT * FROM notes WHERE deleted_locally = 0 ORDER BY updatedAt DESC")
    fun observeNotes(): Flow<List<NoteEntity>>

    @Query("SELECT * FROM notes WHERE id = :id AND deleted_locally = 0")
    fun observeNote(id: String): Flow<NoteEntity?>

    // Sync operations
    @Query("SELECT * FROM notes WHERE sync_status != 'SYNCED'")
    suspend fun getPendingSyncNotes(): List<NoteEntity>

    @Query("SELECT * FROM notes WHERE sync_status = 'CONFLICT'")
    suspend fun getConflictedNotes(): List<NoteEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(note: NoteEntity)

    @Update
    suspend fun update(note: NoteEntity)

    @Query("DELETE FROM notes WHERE id = :id")
    suspend fun hardDelete(id: String)
}
```

### Repository с Offline-First логикой

```kotlin
class NoteRepository @Inject constructor(
    private val noteDao: NoteDao,
    private val noteApi: NoteApi,
    private val syncScheduler: SyncScheduler
) {
    // UI наблюдает за локальной БД
    fun observeNotes(): Flow<List<Note>> =
        noteDao.observeNotes().map { entities ->
            entities.map { it.toDomain() }
        }

    fun observeNote(id: String): Flow<Note?> =
        noteDao.observeNote(id).map { it?.toDomain() }

    // Создание: сначала локально, потом синхронизация
    suspend fun createNote(title: String, content: String): Note {
        val note = NoteEntity(
            id = UUID.randomUUID().toString(),
            title = title,
            content = content,
            createdAt = System.currentTimeMillis(),
            updatedAt = System.currentTimeMillis(),
            syncStatus = SyncStatus.PENDING_CREATE,
            localVersion = 1
        )

        noteDao.upsert(note)
        syncScheduler.scheduleSync()

        return note.toDomain()
    }

    // Обновление: сначала локально, потом синхронизация
    suspend fun updateNote(id: String, title: String, content: String) {
        val existing = noteDao.observeNote(id).first() ?: return

        val updated = existing.copy(
            title = title,
            content = content,
            updatedAt = System.currentTimeMillis(),
            syncStatus = if (existing.syncStatus == SyncStatus.PENDING_CREATE) {
                SyncStatus.PENDING_CREATE
            } else {
                SyncStatus.PENDING_UPDATE
            },
            localVersion = existing.localVersion + 1
        )

        noteDao.update(updated)
        syncScheduler.scheduleSync()
    }

    // Soft delete: помечаем как удаленное, синхронизируем
    suspend fun deleteNote(id: String) {
        val existing = noteDao.observeNote(id).first() ?: return

        if (existing.syncStatus == SyncStatus.PENDING_CREATE) {
            // Если еще не было на сервере - просто удаляем локально
            noteDao.hardDelete(id)
        } else {
            val deleted = existing.copy(
                deletedLocally = true,
                syncStatus = SyncStatus.PENDING_DELETE,
                updatedAt = System.currentTimeMillis()
            )
            noteDao.update(deleted)
            syncScheduler.scheduleSync()
        }
    }
}
```

### Sync Engine с WorkManager

```kotlin
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted appContext: Context,
    @Assisted params: WorkerParameters,
    private val noteDao: NoteDao,
    private val noteApi: NoteApi,
    private val conflictResolver: ConflictResolver
) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        return try {
            // 1. Push локальных изменений
            pushLocalChanges()

            // 2. Pull удаленных обновлений
            pullRemoteChanges()

            Result.success()
        } catch (e: IOException) {
            // Сеть недоступна - повторим позже
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        } catch (e: Exception) {
            Result.failure()
        }
    }

    private suspend fun pushLocalChanges() {
        val pendingNotes = noteDao.getPendingSyncNotes()

        for (note in pendingNotes) {
            try {
                when (note.syncStatus) {
                    SyncStatus.PENDING_CREATE -> {
                        val serverNote = noteApi.createNote(note.toApiRequest())
                        noteDao.upsert(note.copy(
                            syncStatus = SyncStatus.SYNCED,
                            serverVersion = serverNote.version
                        ))
                    }

                    SyncStatus.PENDING_UPDATE -> {
                        val serverNote = noteApi.updateNote(note.id, note.toApiRequest())

                        if (serverNote.version > note.serverVersion + 1) {
                            // Сервер имеет более новую версию - конфликт
                            handleConflict(note, serverNote)
                        } else {
                            noteDao.upsert(note.copy(
                                syncStatus = SyncStatus.SYNCED,
                                serverVersion = serverNote.version
                            ))
                        }
                    }

                    SyncStatus.PENDING_DELETE -> {
                        noteApi.deleteNote(note.id)
                        noteDao.hardDelete(note.id)
                    }

                    else -> {}
                }
            } catch (e: HttpException) {
                if (e.code() == 409) {
                    // Conflict from server
                    val serverNote = noteApi.getNote(note.id)
                    handleConflict(note, serverNote)
                } else {
                    throw e
                }
            }
        }
    }

    private suspend fun pullRemoteChanges() {
        // Получаем timestamp последней синхронизации
        val lastSyncTimestamp = getLastSyncTimestamp()

        val remoteNotes = noteApi.getNotesSince(lastSyncTimestamp)

        for (remoteNote in remoteNotes) {
            val localNote = noteDao.observeNote(remoteNote.id).first()

            when {
                localNote == null -> {
                    // Новая заметка с сервера
                    noteDao.upsert(remoteNote.toEntity(SyncStatus.SYNCED))
                }

                localNote.syncStatus == SyncStatus.SYNCED -> {
                    // Локальная версия синхронизирована - обновляем
                    noteDao.upsert(remoteNote.toEntity(SyncStatus.SYNCED))
                }

                else -> {
                    // Локальные изменения - проверяем конфликт
                    if (remoteNote.version > localNote.serverVersion) {
                        handleConflict(localNote, remoteNote)
                    }
                }
            }
        }

        saveLastSyncTimestamp(System.currentTimeMillis())
    }

    private suspend fun handleConflict(local: NoteEntity, remote: NoteApiResponse) {
        val resolved = conflictResolver.resolve(local, remote)

        noteDao.upsert(resolved.copy(
            syncStatus = if (resolved != local.copy(
                serverVersion = remote.version,
                syncStatus = SyncStatus.SYNCED
            )) {
                SyncStatus.PENDING_UPDATE
            } else {
                SyncStatus.SYNCED
            }
        ))
    }
}
```

### Стратегии Разрешения Конфликтов

```kotlin
interface ConflictResolver {
    suspend fun resolve(local: NoteEntity, remote: NoteApiResponse): NoteEntity
}

// Last-Write-Wins: побеждает более новая версия
class LastWriteWinsResolver : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        return if (local.updatedAt > remote.updatedAt) {
            local.copy(serverVersion = remote.version)
        } else {
            remote.toEntity(SyncStatus.SYNCED)
        }
    }
}

// Field-level Merge: объединяем изменения по полям
class FieldMergeResolver : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        return NoteEntity(
            id = local.id,
            // Берем более длинный title (простая эвристика)
            title = if (local.title.length > remote.title.length) local.title else remote.title,
            // Объединяем content если оба изменились
            content = mergeContent(local.content, remote.content),
            createdAt = minOf(local.createdAt, remote.createdAt),
            updatedAt = maxOf(local.updatedAt, remote.updatedAt),
            syncStatus = SyncStatus.SYNCED,
            localVersion = local.localVersion + 1,
            serverVersion = remote.version
        )
    }

    private fun mergeContent(local: String, remote: String): String {
        // Простое объединение - в реальности используйте diff/patch алгоритмы
        return if (local == remote) local
        else "$local\n\n---\nServer version:\n$remote"
    }
}

// Manual Resolution: показываем пользователю выбор
class ManualConflictResolver(
    private val conflictStore: ConflictStore
) : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        // Сохраняем конфликт для показа пользователю
        conflictStore.saveConflict(
            ConflictData(
                localNote = local,
                remoteNote = remote
            )
        )
        return local.copy(syncStatus = SyncStatus.CONFLICT)
    }
}
```

### Sync Scheduler

```kotlin
class SyncScheduler @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val workManager = WorkManager.getInstance(context)

    // Немедленная синхронизация (при наличии сети)
    fun scheduleSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                Duration.ofSeconds(30)
            )
            .build()

        workManager.enqueueUniqueWork(
            "sync_work",
            ExistingWorkPolicy.REPLACE,
            request
        )
    }

    // Периодическая синхронизация
    fun schedulePeriodicSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val request = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatInterval = 15,
            repeatIntervalTimeUnit = TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .build()

        workManager.enqueueUniquePeriodicWork(
            "periodic_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            request
        )
    }

    // Отмена синхронизации
    fun cancelSync() {
        workManager.cancelUniqueWork("sync_work")
    }
}
```

### UI State Management

```kotlin
@HiltViewModel
class NotesViewModel @Inject constructor(
    private val noteRepository: NoteRepository,
    private val syncScheduler: SyncScheduler,
    private val networkMonitor: NetworkMonitor
) : ViewModel() {

    // UI state
    val notes = noteRepository.observeNotes()
        .stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())

    val syncState = combine(
        noteRepository.getPendingSyncCount(),
        networkMonitor.isOnline
    ) { pendingCount, isOnline ->
        SyncUiState(
            pendingChanges = pendingCount,
            isOnline = isOnline,
            isSyncing = pendingCount > 0 && isOnline
        )
    }.stateIn(viewModelScope, SharingStarted.Eagerly, SyncUiState())

    fun createNote(title: String, content: String) {
        viewModelScope.launch {
            noteRepository.createNote(title, content)
        }
    }

    fun refreshFromServer() {
        syncScheduler.scheduleSync()
    }
}

data class SyncUiState(
    val pendingChanges: Int = 0,
    val isOnline: Boolean = true,
    val isSyncing: Boolean = false
)
```

### Лучшие Практики

1. **Single Source of Truth** - UI всегда читает из локальной БД
2. **Optimistic Updates** - изменения сразу отражаются в UI
3. **Idempotent Operations** - операции синхронизации должны быть идемпотентными
4. **Version Vectors** - отслеживайте версии для корректного merge
5. **Soft Delete** - не удаляйте данные физически до синхронизации
6. **Conflict UI** - дайте пользователю возможность разрешать конфликты

---

## Answer (EN)

**Offline-first** architecture assumes that the local database is the single source of truth, and synchronization with the server happens asynchronously in the background. This ensures instant UI response and app functionality without network.

### Short Version

- **Local DB** (Room) as single source of truth
- **Repository Pattern** for abstracting local/remote sources
- **WorkManager** for reliable background sync
- **Conflict Resolution**: Last-Write-Wins, Merge, or CRDT for complex cases

### Detailed Version

### Offline-First Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                           UI Layer                          │
│  (Compose / ViewModel - reads only from Local DB)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Repository                              │
│  - Writes to Local DB first                                 │
│  - Queues operations for sync                               │
│  - Returns data from Local DB                               │
└─────────────────────────┬───────────────────────────────────┘
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼─────────┐         ┌──────────▼──────────┐
│   Local DB        │         │   Sync Engine       │
│   (Room/SQLite)   │         │   (WorkManager)     │
│                   │         │                     │
│ - Single source   │         │ - Push local        │
│   of truth        │         │   changes           │
│ - Offline access  │         │ - Pull remote       │
│ - Sync metadata   │         │   updates           │
└───────────────────┘         │ - Conflict resolve  │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │    Remote API       │
                              │    (REST/GraphQL)   │
                              └─────────────────────┘
```

### Data Layer: Room + Sync Metadata

```kotlin
// Entity with sync metadata
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val createdAt: Long,
    val updatedAt: Long,

    // Sync metadata
    @ColumnInfo(name = "sync_status")
    val syncStatus: SyncStatus = SyncStatus.SYNCED,

    @ColumnInfo(name = "local_version")
    val localVersion: Int = 0,

    @ColumnInfo(name = "server_version")
    val serverVersion: Int = 0,

    @ColumnInfo(name = "deleted_locally")
    val deletedLocally: Boolean = false
)

enum class SyncStatus {
    SYNCED,           // Synchronized with server
    PENDING_CREATE,   // Created locally, pending push
    PENDING_UPDATE,   // Updated locally, pending push
    PENDING_DELETE,   // Deleted locally, pending push
    CONFLICT          // Conflict with server version
}

@Dao
interface NoteDao {
    // UI reads only non-deleted notes
    @Query("SELECT * FROM notes WHERE deleted_locally = 0 ORDER BY updatedAt DESC")
    fun observeNotes(): Flow<List<NoteEntity>>

    @Query("SELECT * FROM notes WHERE id = :id AND deleted_locally = 0")
    fun observeNote(id: String): Flow<NoteEntity?>

    // Sync operations
    @Query("SELECT * FROM notes WHERE sync_status != 'SYNCED'")
    suspend fun getPendingSyncNotes(): List<NoteEntity>

    @Query("SELECT * FROM notes WHERE sync_status = 'CONFLICT'")
    suspend fun getConflictedNotes(): List<NoteEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(note: NoteEntity)

    @Update
    suspend fun update(note: NoteEntity)

    @Query("DELETE FROM notes WHERE id = :id")
    suspend fun hardDelete(id: String)
}
```

### Repository with Offline-First Logic

```kotlin
class NoteRepository @Inject constructor(
    private val noteDao: NoteDao,
    private val noteApi: NoteApi,
    private val syncScheduler: SyncScheduler
) {
    // UI observes local DB
    fun observeNotes(): Flow<List<Note>> =
        noteDao.observeNotes().map { entities ->
            entities.map { it.toDomain() }
        }

    fun observeNote(id: String): Flow<Note?> =
        noteDao.observeNote(id).map { it?.toDomain() }

    // Create: local first, then sync
    suspend fun createNote(title: String, content: String): Note {
        val note = NoteEntity(
            id = UUID.randomUUID().toString(),
            title = title,
            content = content,
            createdAt = System.currentTimeMillis(),
            updatedAt = System.currentTimeMillis(),
            syncStatus = SyncStatus.PENDING_CREATE,
            localVersion = 1
        )

        noteDao.upsert(note)
        syncScheduler.scheduleSync()

        return note.toDomain()
    }

    // Update: local first, then sync
    suspend fun updateNote(id: String, title: String, content: String) {
        val existing = noteDao.observeNote(id).first() ?: return

        val updated = existing.copy(
            title = title,
            content = content,
            updatedAt = System.currentTimeMillis(),
            syncStatus = if (existing.syncStatus == SyncStatus.PENDING_CREATE) {
                SyncStatus.PENDING_CREATE
            } else {
                SyncStatus.PENDING_UPDATE
            },
            localVersion = existing.localVersion + 1
        )

        noteDao.update(updated)
        syncScheduler.scheduleSync()
    }

    // Soft delete: mark as deleted, sync
    suspend fun deleteNote(id: String) {
        val existing = noteDao.observeNote(id).first() ?: return

        if (existing.syncStatus == SyncStatus.PENDING_CREATE) {
            // Not yet on server - just delete locally
            noteDao.hardDelete(id)
        } else {
            val deleted = existing.copy(
                deletedLocally = true,
                syncStatus = SyncStatus.PENDING_DELETE,
                updatedAt = System.currentTimeMillis()
            )
            noteDao.update(deleted)
            syncScheduler.scheduleSync()
        }
    }
}
```

### Conflict Resolution Strategies

```kotlin
interface ConflictResolver {
    suspend fun resolve(local: NoteEntity, remote: NoteApiResponse): NoteEntity
}

// Last-Write-Wins: newer version wins
class LastWriteWinsResolver : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        return if (local.updatedAt > remote.updatedAt) {
            local.copy(serverVersion = remote.version)
        } else {
            remote.toEntity(SyncStatus.SYNCED)
        }
    }
}

// Field-level Merge: merge changes by field
class FieldMergeResolver : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        return NoteEntity(
            id = local.id,
            // Take longer title (simple heuristic)
            title = if (local.title.length > remote.title.length) local.title else remote.title,
            // Merge content if both changed
            content = mergeContent(local.content, remote.content),
            createdAt = minOf(local.createdAt, remote.createdAt),
            updatedAt = maxOf(local.updatedAt, remote.updatedAt),
            syncStatus = SyncStatus.SYNCED,
            localVersion = local.localVersion + 1,
            serverVersion = remote.version
        )
    }

    private fun mergeContent(local: String, remote: String): String {
        // Simple merge - in reality use diff/patch algorithms
        return if (local == remote) local
        else "$local\n\n---\nServer version:\n$remote"
    }
}

// Manual Resolution: show user the choice
class ManualConflictResolver(
    private val conflictStore: ConflictStore
) : ConflictResolver {
    override suspend fun resolve(
        local: NoteEntity,
        remote: NoteApiResponse
    ): NoteEntity {
        // Save conflict to show user
        conflictStore.saveConflict(
            ConflictData(
                localNote = local,
                remoteNote = remote
            )
        )
        return local.copy(syncStatus = SyncStatus.CONFLICT)
    }
}
```

### Best Practices

1. **Single Source of Truth** - UI always reads from local DB
2. **Optimistic Updates** - changes immediately reflected in UI
3. **Idempotent Operations** - sync operations must be idempotent
4. **Version Vectors** - track versions for correct merge
5. **Soft Delete** - don't physically delete data until synced
6. **Conflict UI** - let users resolve conflicts manually

---

## Дополнительные Вопросы (RU)

1. Как реализовать CRDT для автоматического разрешения конфликтов?
2. Как обрабатывать partial sync failures?
3. Как реализовать очередь операций с приоритетами?
4. Когда использовать pessimistic vs optimistic locking?
5. Как тестировать offline-first логику?

## Follow-ups

1. How do you implement CRDT for automatic conflict resolution?
2. How do you handle partial sync failures?
3. How do you implement operation queue with priorities?
4. When should you use pessimistic vs optimistic locking?
5. How do you test offline-first logic?

## Ссылки (RU)

- [Offline-first Android](https://developer.android.com/topic/architecture/data-layer/offline-first)
- [Room Database](https://developer.android.com/training/data-storage/room)
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)

## References

- [Offline-first Android](https://developer.android.com/topic/architecture/data-layer/offline-first)
- [Room Database](https://developer.android.com/training/data-storage/room)
- [WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager)

## Связанные Вопросы (RU)

### Предпосылки

- [[q-room-database--android--medium]]
- [[q-workmanager-execution-guarantee--android--medium]]

### Похожие

- [[q-data-sync-unstable-network--android--hard]]
- [[q-cache-implementation-strategies--android--medium]]

### Продвинутое

- [[q-distributed-systems-consistency--architecture--hard]]
- [[q-crdt-implementation--architecture--hard]]

## Related Questions

### Prerequisites

- [[q-room-database--android--medium]]
- [[q-workmanager-execution-guarantee--android--medium]]

### Related

- [[q-data-sync-unstable-network--android--hard]]
- [[q-cache-implementation-strategies--android--medium]]

### Advanced

- [[q-distributed-systems-consistency--architecture--hard]]
- [[q-crdt-implementation--architecture--hard]]
