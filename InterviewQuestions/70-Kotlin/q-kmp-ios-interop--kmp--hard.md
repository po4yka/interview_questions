---
id: kotlin-kmp-008
title: KMP iOS Interop / Взаимодействие KMP с iOS
aliases:
- Kotlin Native iOS
- Swift Kotlin Interop
- KMP iOS Challenges
topic: kotlin
subtopics:
- kmp
- multiplatform
- ios
- kotlin-native
- interop
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kmp
- multiplatform
- ios
- kotlin-native
- swift
- interop
- difficulty/hard
anki_cards:
- slug: kotlin-kmp-008-0-en
  language: en
  anki_id: 1769344150215
  synced_at: '2026-01-25T16:29:10.266552'
- slug: kotlin-kmp-008-0-ru
  language: ru
  anki_id: 1769344150265
  synced_at: '2026-01-25T16:29:10.268789'
---
# Question (EN)
> What are the challenges of Kotlin/Native and Swift interop in KMP, and how do you address them?

# Vopros (RU)
> Какие сложности возникают при взаимодействии Kotlin/Native и Swift в KMP, и как их решать?

## Answer (EN)

Kotlin Multiplatform compiles shared code to a native iOS framework using Kotlin/Native. While interop has improved significantly (2026), understanding the challenges helps build better cross-platform apps.

### Framework Generation

```kotlin
// build.gradle.kts
kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "SharedKit"
            isStatic = true  // Static framework (recommended)
            // isStatic = false  // Dynamic framework

            export(project(":core"))  // Re-export dependencies
            transitiveExport = true
        }
    }
}
```

### Challenge 1: Generics Limitations

Kotlin generics are erased in Objective-C headers, limiting Swift usage.

```kotlin
// Kotlin (commonMain)
class Repository<T> {
    fun getAll(): List<T> = emptyList()
    fun getById(id: String): T? = null
}

// Generated Objective-C - generics lost
@interface SharedKitRepository : KotlinBase
- (NSArray *)getAll;
- (id _Nullable)getByIdId:(NSString *)id;
@end

// Swift usage - type safety lost
let repo = Repository()
let items = repo.getAll()  // Returns [Any]
```

**Solutions:**

```kotlin
// Option 1: Use concrete types in public API
interface UserRepository {
    fun getAll(): List<User>
    fun getById(id: String): User?
}

// Option 2: Use @ObjCName for better Swift names
@ObjCName("UserRepo", exact = true)
class UserRepository {
    @ObjCName("fetchAllUsers")
    fun getAll(): List<User> = emptyList()
}

// Option 3: SKIE for enhanced generics support
// With SKIE plugin, generics work better in Swift
```

### Challenge 2: Suspend Functions

Suspend functions generate complex callback-based APIs in Objective-C.

```kotlin
// Kotlin
class UserService {
    suspend fun fetchUser(id: String): User { /* ... */ }
}

// Without SKIE - callback-based
// Swift usage (old approach)
userService.fetchUser(id: "123") { user, error in
    if let user = user {
        // Handle user
    }
}
```

**Modern Solution with SKIE:**

```kotlin
// build.gradle.kts
plugins {
    id("co.touchlab.skie") version "0.8.0"
}

skie {
    features {
        enableSwiftUIObservingPreview = true
        coroutinesInterop.set(true)
    }
}
```

```swift
// Swift with SKIE - native async/await
let user = try await userService.fetchUser(id: "123")

// Flow becomes AsyncSequence
for await user in userService.observeUser(id: "123") {
    updateUI(with: user)
}
```

### Challenge 3: Sealed Classes and Enums

Sealed classes don't map perfectly to Swift enums.

```kotlin
// Kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

```swift
// Swift without SKIE - verbose pattern matching
switch result {
case let success as ResultSuccess<User>:
    handleUser(success.data)
case let error as ResultError:
    showError(error.message)
case is ResultLoading:
    showLoading()
default:
    fatalError("Unknown result type")
}

// Swift with SKIE - exhaustive switch
switch onEnum(of: result) {
case .success(let success):
    handleUser(success.data)
case .error(let error):
    showError(error.message)
case .loading:
    showLoading()
}
```

### Challenge 4: Flow Observation

Kotlin Flow needs adaptation for iOS reactive patterns.

```kotlin
// Kotlin
class UserViewModel {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()
}
```

**Without SKIE:**

```swift
// Manual Flow collection in Swift
class UserViewModelWrapper: ObservableObject {
    @Published var state: UserState = UserState()
    private var job: Kotlinx_coroutines_coreJob?

    init(viewModel: UserViewModel) {
        job = FlowCollector.collect(viewModel.state) { [weak self] state in
            DispatchQueue.main.async {
                self?.state = state
            }
        }
    }

    deinit {
        job?.cancel(cause: nil)
    }
}
```

**With SKIE:**

```swift
// StateFlow becomes @Published automatically
@MainActor
class UserScreen: View {
    @ObservedObject var viewModel: UserViewModel

    var body: some View {
        // state automatically observable
        Text(viewModel.state.userName)
    }
}
```

### Challenge 5: Memory Management

Kotlin/Native uses different memory model than Swift ARC.

```kotlin
// Potential memory leak - capturing self in lambda
class DataManager {
    private val listeners = mutableListOf<() -> Unit>()

    fun addListener(listener: () -> Unit) {
        listeners.add(listener)
    }
}
```

```swift
// Swift - creates retain cycle
dataManager.addListener { [self] in
    self.handleUpdate()  // Strong reference to self
}

// Fix - use weak reference
dataManager.addListener { [weak self] in
    self?.handleUpdate()
}
```

**Kotlin-side fixes:**

```kotlin
// Use WeakReference for callbacks
class DataManager {
    private val listeners = mutableListOf<WeakReference<DataListener>>()

    fun addListener(listener: DataListener) {
        listeners.add(WeakReference(listener))
    }

    fun notifyListeners() {
        listeners.removeAll { it.get() == null }
        listeners.forEach { it.get()?.onDataChanged() }
    }
}

interface DataListener {
    fun onDataChanged()
}
```

### Challenge 6: Exception Handling

Kotlin exceptions become NSError in Objective-C.

```kotlin
// Kotlin
class UserService {
    @Throws(UserNotFoundException::class, NetworkException::class)
    suspend fun getUser(id: String): User {
        // ...
    }
}
```

```swift
// Swift - must handle as throwing function
do {
    let user = try await userService.getUser(id: "123")
} catch let error as UserNotFoundException {
    showUserNotFound()
} catch let error as NetworkException {
    showNetworkError()
} catch {
    showGenericError(error)
}
```

### Challenge 7: Module Visibility

Controlling what's exported to iOS framework.

```kotlin
// build.gradle.kts
kotlin {
    targets.withType<KotlinNativeTarget> {
        binaries.framework {
            // Only export specific modules
            export(project(":shared:api"))
            // Don't export implementation details
        }
    }
}

// Use internal modifier for implementation details
internal class InternalHelper {
    // Not visible in iOS framework
}

// Public API
class PublicService {
    fun doSomething() { /* ... */ }
}
```

### SKIE Configuration (Recommended)

```kotlin
// build.gradle.kts
skie {
    analytics {
        enabled.set(false)
    }

    features {
        // Sealed class enums
        enableSealedClassEnums = true

        // Coroutines as async/await
        coroutinesInterop.set(true)

        // Flow as AsyncSequence
        enableFlowInterop = true

        // Default arguments in Swift
        enableDefaultArgumentsInSwift = true

        // SwiftUI integration
        enableSwiftUIObservingPreview = true
    }

    // Custom Swift names
    swiftFunctionNameMapping {
        argumentLabels.set(true)
    }
}
```

### Best Practices for iOS Interop

1. **Use SKIE** - Dramatically improves Swift experience
2. **Prefer interfaces over abstract classes** - Better Objective-C mapping
3. **Avoid deep generic hierarchies** - Generics don't translate well
4. **Use @ObjCName** - Control Swift-facing names
5. **Mark internal classes as internal** - Don't pollute the framework API
6. **Test on iOS early** - Catch interop issues during development
7. **Document Swift usage** - Help iOS developers use your API

### Debugging Tips

```kotlin
// Enable better crash reports
kotlin {
    targets.withType<KotlinNativeTarget> {
        binaries.all {
            freeCompilerArgs += listOf(
                "-Xruntime-logs=gc=info",
                "-Xallocator=mimalloc"
            )
        }
    }
}
```

```swift
// Debug Kotlin exceptions in Xcode
// Add symbolic breakpoint for:
// kotlin.Throwable.init
```

---

## Otvet (RU)

Kotlin Multiplatform компилирует общий код в нативный iOS фреймворк с использованием Kotlin/Native. Хотя interop значительно улучшился (2026), понимание сложностей помогает строить лучшие кросс-платформенные приложения.

### Генерация фреймворка

```kotlin
// build.gradle.kts
kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "SharedKit"
            isStatic = true  // Статический фреймворк (рекомендуется)
        }
    }
}
```

### Сложность 1: Ограничения дженериков

Kotlin дженерики стираются в Objective-C заголовках, ограничивая использование в Swift.

```kotlin
// Kotlin (commonMain)
class Repository<T> {
    fun getAll(): List<T> = emptyList()
    fun getById(id: String): T? = null
}

// Сгенерированный Objective-C - дженерики потеряны
// Swift использование - типобезопасность потеряна
let repo = Repository()
let items = repo.getAll()  // Возвращает [Any]
```

**Решения:**

```kotlin
// Вариант 1: Используйте конкретные типы в публичном API
interface UserRepository {
    fun getAll(): List<User>
    fun getById(id: String): User?
}

// Вариант 2: Используйте @ObjCName для лучших Swift имён
@ObjCName("UserRepo", exact = true)
class UserRepository {
    @ObjCName("fetchAllUsers")
    fun getAll(): List<User> = emptyList()
}
```

### Сложность 2: Suspend функции

Suspend функции генерируют сложные callback-based API в Objective-C.

**Современное решение с SKIE:**

```kotlin
// build.gradle.kts
plugins {
    id("co.touchlab.skie") version "0.8.0"
}
```

```swift
// Swift с SKIE - нативный async/await
let user = try await userService.fetchUser(id: "123")

// Flow становится AsyncSequence
for await user in userService.observeUser(id: "123") {
    updateUI(with: user)
}
```

### Сложность 3: Sealed классы и Enum

Sealed классы не идеально мапятся на Swift enum.

```kotlin
// Kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}
```

```swift
// Swift с SKIE - исчерпывающий switch
switch onEnum(of: result) {
case .success(let success):
    handleUser(success.data)
case .error(let error):
    showError(error.message)
case .loading:
    showLoading()
}
```

### Сложность 4: Наблюдение за Flow

Kotlin Flow требует адаптации для iOS реактивных паттернов.

**С SKIE:**

```swift
// StateFlow становится @Published автоматически
@MainActor
class UserScreen: View {
    @ObservedObject var viewModel: UserViewModel

    var body: some View {
        // state автоматически observable
        Text(viewModel.state.userName)
    }
}
```

### Сложность 5: Управление памятью

Kotlin/Native использует другую модель памяти чем Swift ARC.

```swift
// Swift - создаёт retain cycle
dataManager.addListener { [self] in
    self.handleUpdate()  // Сильная ссылка на self
}

// Исправление - используйте weak ссылку
dataManager.addListener { [weak self] in
    self?.handleUpdate()
}
```

### Сложность 6: Обработка исключений

Kotlin исключения становятся NSError в Objective-C.

```kotlin
// Kotlin
class UserService {
    @Throws(UserNotFoundException::class, NetworkException::class)
    suspend fun getUser(id: String): User {
        // ...
    }
}
```

```swift
// Swift - должен обрабатывать как throwing функцию
do {
    let user = try await userService.getUser(id: "123")
} catch let error as UserNotFoundException {
    showUserNotFound()
} catch let error as NetworkException {
    showNetworkError()
} catch {
    showGenericError(error)
}
```

### Конфигурация SKIE (рекомендуется)

```kotlin
// build.gradle.kts
skie {
    features {
        // Sealed class enums
        enableSealedClassEnums = true

        // Корутины как async/await
        coroutinesInterop.set(true)

        // Flow как AsyncSequence
        enableFlowInterop = true

        // SwiftUI интеграция
        enableSwiftUIObservingPreview = true
    }
}
```

### Лучшие практики для iOS Interop

1. **Используйте SKIE** - Кардинально улучшает Swift experience
2. **Предпочитайте интерфейсы абстрактным классам** - Лучше маппинг в Objective-C
3. **Избегайте глубоких иерархий дженериков** - Дженерики плохо транслируются
4. **Используйте @ObjCName** - Контролируйте Swift-facing имена
5. **Помечайте internal классы как internal** - Не засоряйте API фреймворка
6. **Тестируйте на iOS рано** - Ловите interop проблемы во время разработки
7. **Документируйте Swift использование** - Помогите iOS разработчикам использовать ваш API

---

## Follow-ups

- How does SKIE improve KMP iOS interop?
- What is the performance overhead of Kotlin/Native on iOS?
- How do you debug memory issues in KMP iOS apps?
- How do you integrate KMP with existing Swift codebase?

## Dopolnitelnye Voprosy (RU)

- Как SKIE улучшает KMP iOS interop?
- Какова производительность Kotlin/Native на iOS?
- Как отлаживать проблемы с памятью в KMP iOS приложениях?
- Как интегрировать KMP с существующей Swift кодовой базой?

## References

- [Kotlin/Native Documentation](https://kotlinlang.org/docs/native-overview.html)
- [SKIE by Touchlab](https://skie.touchlab.co/)
- [Kotlin/Native Memory Management](https://kotlinlang.org/docs/native-memory-manager.html)

## Ssylki (RU)

- [[c-kotlin]]
- [Документация Kotlin/Native](https://kotlinlang.org/docs/native-overview.html)
- [SKIE от Touchlab](https://skie.touchlab.co/)

## Related Questions

- [[q-kmp-architecture--kmp--hard]]
- [[q-compose-multiplatform--kmp--medium]]
