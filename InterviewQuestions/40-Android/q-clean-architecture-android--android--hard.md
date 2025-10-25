---
id: 20251012-122801
title: Clean Architecture on Android / Clean Architecture в Android
aliases:
- Clean Architecture on Android
- Clean Architecture в Android
topic: android
subtopics:
- architecture-clean
- architecture-modularization
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-android-architectural-patterns--android--medium
- q-android-modularization--android--medium
- q-architecture-components-libraries--android--easy
created: 2025-10-11
updated: 2025-10-20
tags:
- android/architecture-clean
- android/architecture-modularization
- difficulty/hard
---

# Вопрос (RU)
> Clean Architecture в Android?

# Question (EN)
> Clean Architecture on Android?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Principles
- Dependency Rule: source code dependencies point inward (UI → domain; data implements domain interfaces)
- Separation of concerns: domain pure Kotlin; frameworks at the edges
- Testable: business rules independent of Android SDK

### Layers (typical)
- Domain: entities + use cases (pure Kotlin, no Android)
- Data: repositories (implement domain ports), mappers, data sources (network/db)
- Presentation: ViewModel/UI (Android), maps to domain models

### Boundaries and contracts
- Define domain interfaces (ports); implement in data (adapters)
- Map DTO/DB models at boundaries; keep domain models stable
- See [[c-database-design]] for data layer modeling best practices

### Minimal module layout
```text
app/                 # presentation wiring only
feature-*/           # feature presentation
core-domain/         # entities, use cases, ports (pure Kotlin)
core-data/           # repo impls, mappers, sources
```

### Minimal code (ports and use case)
```kotlin
// core-domain
interface UserRepository { suspend fun getUser(id: String): User }
class GetUser(private val repo: UserRepository) {
  suspend operator fun invoke(id: String): User = repo.getUser(id)
}
```

```kotlin
// core-data (depends on core-domain)
class UserRepositoryImpl(private val api: Api, private val dao: UserDao) : UserRepository {
  override suspend fun getUser(id: String): User =
    dao.get(id)?.toDomain() ?: api.fetch(id).also { dao.insert(it.toEntity()) }.toDomain()
}
```

```kotlin
// app/feature presentation (depends on core-domain)
class UserViewModel(private val getUser: GetUser) : ViewModel() {
  val state = MutableStateFlow<UiState>(UiState.Loading)
  fun load(id: String) = viewModelScope.launch { state.value = UiState.Data(getUser(id)) }
}
```

### DI and wiring
- Provide use cases in presentation module via constructor injection (Hilt/Koin/plain DI)
- Bind domain ports to data adapters in DI graph; UI never sees data details

### Testing
- Domain: fast unit tests with fake repositories
- Data: contract tests against domain ports; instrumented for DB if needed
- Presentation: ViewModel tests with TestDispatcher; fake use cases

### Concurrency and errors
- Keep domain synchronous/pure when possible; wrap suspending at boundaries
- Convert infra exceptions to domain failures; handle mapping in presentation

## Follow-ups
- How to split features into modules without over‑fragmentation?
- Where to place navigation and analytics within Clean Architecture?
- How to manage domain events across features?

## References
- https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html
- https://developer.android.com/topic/architecture

## Related Questions

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-modularization--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
