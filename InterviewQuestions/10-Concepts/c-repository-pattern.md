---
id: ivc-20251030-140000
title: Repository Pattern / Паттерн Repository
aliases: [Repository, Repository Pattern, Паттерн Repository]
kind: concept
summary: Abstraction layer that mediates between data sources and business logic
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [architecture-patterns, clean-architecture, concept, data-layer, repository]
date created: Thursday, October 30th 2025, 12:29:27 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

The **Repository Pattern** is a design pattern that creates an abstraction layer between the data layer and the business logic layer of an application. It acts as a single source of truth by mediating access to various data sources (network, local database, cache) and providing a clean API for data operations.

**Core Principles**:
- **Single Source of Truth**: Centralizes data access logic in one place
- **Data Source Abstraction**: Business logic doesn't know where data comes from
- **Separation of Concerns**: Decouples data access from business logic
- **Testability**: Easy to mock and test without real data sources

**Typical Architecture**:
```
ViewModel → Repository → [RemoteDataSource, LocalDataSource, CacheManager]
```

The repository decides which data source to use, handles caching strategies, and coordinates data synchronization between sources.

# Сводка (RU)

**Repository Pattern (Паттерн Репозиторий)** — это паттерн проектирования, который создаёт слой абстракции между слоем данных и слоем бизнес-логики приложения. Он выступает единым источником истины, управляя доступом к различным источникам данных (сеть, локальная база данных, кэш) и предоставляя чистый API для операций с данными.

**Основные принципы**:
- **Единый источник истины**: Централизует логику доступа к данным в одном месте
- **Абстракция источников данных**: Бизнес-логика не знает, откуда приходят данные
- **Разделение ответственности**: Отделяет доступ к данным от бизнес-логики
- **Тестируемость**: Легко мокировать и тестировать без реальных источников данных

**Типичная архитектура**:
```
ViewModel → Repository → [RemoteDataSource, LocalDataSource, CacheManager]
```

Репозиторий решает, какой источник данных использовать, управляет стратегиями кэширования и координирует синхронизацию данных между источниками.

---

## Responsibilities / Ответственность

**Repository is responsible for**:
1. **Data Fetching**: Retrieving data from network or local storage
2. **Caching Strategy**: Deciding when to use cached vs fresh data
3. **Data Synchronization**: Keeping remote and local data in sync
4. **Error Handling**: Converting data layer errors to domain layer errors
5. **Business Logic Isolation**: Shielding ViewModels from data source details

**Репозиторий отвечает за**:
1. **Получение данных**: Загрузка данных из сети или локального хранилища
2. **Стратегия кэширования**: Решение, когда использовать кэш, а когда свежие данные
3. **Синхронизация данных**: Поддержание синхронизации удалённых и локальных данных
4. **Обработка ошибок**: Преобразование ошибок слоя данных в ошибки слоя домена
5. **Изоляция бизнес-логики**: Защита ViewModels от деталей источников данных

---

## Architecture Position / Позиция В Архитектуре

**Clean Architecture Layers** (EN):
```
Presentation Layer (UI, ViewModel)
        ↓
Domain Layer (Use Cases, Business Logic)
        ↓
Data Layer (Repository) ← You are here
        ↓
Data Sources (Network API, Local DB, SharedPreferences)
```

**Repository Pattern Benefits**:
- ViewModels don't know about Retrofit, Room, or other implementation details
- Easy to switch data sources without changing business logic
- Centralized place for offline-first strategy
- Single place to add logging, analytics, or monitoring

**Слои Clean Architecture** (RU):
```
Слой представления (UI, ViewModel)
        ↓
Слой домена (Use Cases, бизнес-логика)
        ↓
Слой данных (Repository) ← Вы здесь
        ↓
Источники данных (Network API, Local DB, SharedPreferences)
```

**Преимущества паттерна Repository**:
- ViewModels не знают о Retrofit, Room или других деталях реализации
- Легко менять источники данных без изменения бизнес-логики
- Централизованное место для offline-first стратегии
- Единое место для добавления логирования, аналитики или мониторинга

---

## Code Example / Пример Кода

```kotlin
// Data model
data class User(val id: String, val name: String, val email: String)

// Result wrapper for error handling
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Data sources
interface RemoteDataSource {
    suspend fun getUsers(): List<User>
}

interface LocalDataSource {
    suspend fun getUsers(): List<User>
    suspend fun saveUsers(users: List<User>)
}

// Repository implementation
class UserRepository(
    private val remoteDataSource: RemoteDataSource,
    private val localDataSource: LocalDataSource
) {
    // Offline-first strategy: return cached data, then fetch fresh
    fun getUsers(): Flow<Result<List<User>>> = flow {
        emit(Result.Loading)

        // Emit cached data first
        val cachedUsers = localDataSource.getUsers()
        if (cachedUsers.isNotEmpty()) {
            emit(Result.Success(cachedUsers))
        }

        // Fetch fresh data from network
        try {
            val freshUsers = remoteDataSource.getUsers()
            localDataSource.saveUsers(freshUsers) // Update cache
            emit(Result.Success(freshUsers))
        } catch (e: Exception) {
            // If network fails and we have cache, we already emitted it
            if (cachedUsers.isEmpty()) {
                emit(Result.Error(e))
            }
        }
    }

    // Single source fetch (network only)
    suspend fun refreshUsers(): Result<List<User>> {
        return try {
            val users = remoteDataSource.getUsers()
            localDataSource.saveUsers(users)
            Result.Success(users)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Usage in ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _users = MutableStateFlow<Result<List<User>>>(Result.Loading)
    val users: StateFlow<Result<List<User>>> = _users.asStateFlow()

    init {
        viewModelScope.launch {
            repository.getUsers().collect { result ->
                _users.value = result
            }
        }
    }
}
```

---

## Best Practices / Лучшие Практики

**EN**:
1. **Use sealed classes/Result wrapper**: Handle success, error, and loading states explicitly
2. **Offline-first strategy**: Return cached data immediately, then fetch fresh data
3. **Single Responsibility**: Repository only handles data access, not business logic
4. **Interface over implementation**: Expose repository as interface for easy testing
5. **Coroutines for async**: Use suspend functions and Flow for reactive data streams
6. **Error mapping**: Convert low-level exceptions to domain-specific errors

**RU**:
1. **Используйте sealed классы/Result wrapper**: Явно обрабатывайте состояния успеха, ошибки и загрузки
2. **Offline-first стратегия**: Возвращайте кэшированные данные сразу, затем загружайте свежие
3. **Единая ответственность**: Репозиторий только управляет доступом к данным, не бизнес-логикой
4. **Интерфейс вместо реализации**: Предоставляйте репозиторий как интерфейс для лёгкого тестирования
5. **Корутины для асинхронности**: Используйте suspend функции и Flow для реактивных потоков данных
6. **Преобразование ошибок**: Конвертируйте низкоуровневые исключения в ошибки уровня домена

---

## Use Cases / Trade-offs

**When to use**:
- Multi-source data access (network + database + cache)
- Need offline support and data synchronization
- Want to abstract data layer from presentation/domain layers
- Building scalable, testable applications with Clean Architecture

**Trade-offs**:
- **Pro**: Clean separation, easy to test, flexible data source switching
- **Pro**: Single place for caching and synchronization logic
- **Con**: Additional abstraction layer (more boilerplate for simple apps)
- **Con**: Can become complex with many data sources and sync strategies

**Когда использовать**:
- Многоисточниковый доступ к данным (сеть + база данных + кэш)
- Нужна поддержка оффлайн и синхронизация данных
- Хотите абстрагировать слой данных от слоёв представления/домена
- Построение масштабируемых, тестируемых приложений с Clean Architecture

**Компромиссы**:
- **Плюс**: Чёткое разделение, легко тестировать, гибкая смена источников данных
- **Плюс**: Единое место для логики кэширования и синхронизации
- **Минус**: Дополнительный слой абстракции (больше boilerplate для простых приложений)
- **Минус**: Может стать сложным при многих источниках данных и стратегиях синхронизации

---

## References

- [Android Architecture Components - Repository Pattern](https://developer.android.com/topic/architecture/data-layer)
- [Guide to app architecture - Data layer](https://developer.android.com/topic/architecture/data-layer)
- Martin Fowler - Patterns of Enterprise Application Architecture
