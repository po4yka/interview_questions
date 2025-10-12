---
id: 20251012-017
title: "Kotlin/Native / Kotlin/Native"
aliases: []

# Classification
topic: kotlin
subtopics: [kotlin-native, multiplatform, interop, cinterop, memory-model, native-compilation]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Kotlin/Native

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-expect-actual-kotlin--kotlin--medium, q-structured-concurrency--kotlin--hard, q-kotlin-collections--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, kotlin-native, multiplatform, interop, cinterop, ios, native, difficulty/hard]
---

# Question (EN)
> What is Kotlin/Native? Explain native compilation, interop with C libraries and Objective-C/Swift, memory model differences, and use cases for iOS development.

# Вопрос (RU)
> Что такое Kotlin/Native? Объясните нативную компиляцию, interop с C библиотеками и Objective-C/Swift, различия в модели памяти и случаи использования для iOS разработки.

---

## Answer (EN)

**Kotlin/Native** is a technology for compiling Kotlin code to native binaries that can run without a virtual machine. It enables Kotlin to target platforms like iOS, macOS, Linux, Windows, and embedded systems.

### Key Features

1. **Native Compilation**: Compiles to platform-specific machine code
2. **No JVM Required**: Standalone executables
3. **C Interop**: Direct integration with C libraries
4. **Objective-C/Swift Interop**: iOS/macOS development
5. **Multiplatform**: Share code across platforms
6. **Memory Management**: Automatic memory management without GC

### Kotlin/Native Architecture

```
┌──────────────────────────────────────┐
│       Kotlin Source Code              │
└───────────────┬──────────────────────┘
                │
        ┌───────▼────────┐
        │  Kotlin/Native  │
        │    Compiler     │
        └───────┬─────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼─────┐           ┌────▼────┐
│  LLVM   │           │  LLVM   │
│  iOS    │           │  macOS  │
└───┬─────┘           └────┬────┘
    │                      │
┌───▼──────┐         ┌─────▼────┐
│ .framework│         │  Binary  │
└──────────┘         └──────────┘
```

### Basic Kotlin/Native Project

```kotlin
// commonMain/Platform.kt
expect class Platform() {
    val name: String
}

fun getPlatformName(): String {
    return Platform().name
}

// iosMain/Platform.kt
import platform.UIKit.UIDevice

actual class Platform {
    actual val name: String = 
        UIDevice.currentDevice.systemName() + " " + 
        UIDevice.currentDevice.systemVersion
}

// Usage in iOS
fun main() {
    println("Running on: ${getPlatformName()}")
    // Output: Running on: iOS 16.0
}
```

### C Interop (cinterop)

**Calling C libraries from Kotlin:**

```kotlin
// 1. Create .def file
// curl.def:
headers = curl/curl.h
headerFilter = curl/*
compilerOpts.linux = -I/usr/include -I/usr/include/x86_64-linux-gnu
linkerOpts.osx = -L/opt/local/lib -L/usr/local/opt/curl/lib -lcurl
linkerOpts.linux = -L/usr/lib/x86_64-linux-gnu -lcurl
```

```kotlin
// 2. Use in Kotlin
import kotlinx.cinterop.*
import curl.*

fun httpGet(url: String): String? {
    val curl = curl_easy_init()
    
    if (curl != null) {
        curl_easy_setopt(curl, CURLOPT_URL, url)
        curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L)
        
        val result = curl_easy_perform(curl)
        curl_easy_cleanup(curl)
        
        if (result == CURLE_OK) {
            return "Success"
        }
    }
    
    return null
}

// Usage
fun main() {
    val result = httpGet("https://example.com")
    println(result)
}
```

**Working with C structs:**

```c
// mylib.h
typedef struct {
    int id;
    char name[100];
    double value;
} MyStruct;

void process_struct(MyStruct* s);
```

```kotlin
// Kotlin
import kotlinx.cinterop.*
import mylib.*

fun useStruct() {
    val struct = nativeHeap.alloc<MyStruct>()
    
    struct.id = 42
    struct.name[0] = 'T'.code.toByte()
    struct.name[1] = 'e'.code.toByte()
    struct.name[2] = 's'.code.toByte()
    struct.name[3] = 't'.code.toByte()
    struct.value = 3.14
    
    process_struct(struct.ptr)
    
    nativeHeap.free(struct)
}
```

### Objective-C/Swift Interop

**Calling Objective-C from Kotlin:**

```objective-c
// MyClass.h
@interface MyClass : NSObject
- (NSString *)greet:(NSString *)name;
- (NSInteger)add:(NSInteger)a and:(NSInteger)b;
@property (nonatomic, strong) NSString *title;
@end

// MyClass.m
@implementation MyClass
- (NSString *)greet:(NSString *)name {
    return [NSString stringWithFormat:@"Hello, %@!", name];
}

- (NSInteger)add:(NSInteger)a and:(NSInteger)b {
    return a + b;
}
@end
```

```kotlin
// Kotlin
import platform.Foundation.*
import cocoapods.MyFramework.*

fun useObjCClass() {
    val obj = MyClass()
    
    // Call methods
    val greeting = obj.greet("World")
    println(greeting) // Hello, World!
    
    val sum = obj.addAnd(5, 3)
    println(sum) // 8
    
    // Properties
    obj.title = "My Title"
    println(obj.title)
}
```

**iOS Framework Creation:**

```kotlin
// Shared Kotlin code for iOS
class UserRepository {
    suspend fun getUsers(): List<User> {
        delay(1000)
        return listOf(
            User(1, "Alice"),
            User(2, "Bob")
        )
    }
}

data class User(val id: Int, val name: String)

// Expose to iOS
@OptIn(ExperimentalForeignApi::class)
fun iosGetUsers(completion: (List<User>) -> Unit) {
    val repository = UserRepository()
    
    MainScope().launch {
        val users = repository.getUsers()
        completion(users)
    }
}
```

**Swift usage:**

```swift
import Shared

class ViewModel: ObservableObject {
    @Published var users: [User] = []
    
    func loadUsers() {
        SharedKt.iosGetUsers { users in
            DispatchQueue.main.async {
                self.users = users
            }
        }
    }
}

// SwiftUI View
struct UsersView: View {
    @StateObject var viewModel = ViewModel()
    
    var body: some View {
        List(viewModel.users, id: \.id) { user in
            Text(user.name)
        }
        .onAppear {
            viewModel.loadUsers()
        }
    }
}
```

### Memory Model

**Old Memory Model (before 1.7.20):**

```kotlin
// Strict thread isolation
class DataHolder {
    var data = "Hello" // Frozen after first access from another thread
}

val holder = DataHolder()

// Main thread
holder.data = "World" // OK

// Background thread
GlobalScope.launch {
    holder.data = "Modified" // Error! Object is frozen
}
```

**New Memory Model (1.7.20+):**

```kotlin
// Concurrent mutability like JVM/JS
class DataHolder {
    var data = "Hello" // Can be modified from any thread
}

val holder = DataHolder()

// Any thread
holder.data = "Modified" // OK

// Thread-safe collections
val safeList = mutableListOf<String>().also {
    it.add("Item 1")
}
```

**Memory management:**

```kotlin
import kotlinx.cinterop.*

// Manual memory management for C interop
fun manualMemory() {
    // Allocate
    val buffer = nativeHeap.allocArray<ByteVar>(1024)
    
    try {
        // Use buffer
        buffer[0] = 'H'.code.toByte()
        buffer[1] = 'i'.code.toByte()
    } finally {
        // Must free manually
        nativeHeap.free(buffer)
    }
}

// Arena for grouped allocations
fun arenaMemory() {
    memScoped {
        val buffer = allocArray<ByteVar>(1024)
        // Automatically freed when memScoped exits
    }
}
```

### Coroutines in Kotlin/Native

```kotlin
// iOS-compatible coroutines wrapper
class FlowWrapper<T>(private val flow: Flow<T>) {
    fun subscribe(
        onEach: (T) -> Unit,
        onComplete: () -> Unit,
        onThrow: (Throwable) -> Unit
    ): Cancellable {
        val scope = MainScope()
        
        scope.launch {
            try {
                flow.collect { value ->
                    onEach(value)
                }
                onComplete()
            } catch (e: Exception) {
                onThrow(e)
            }
        }
        
        return object : Cancellable {
            override fun cancel() {
                scope.cancel()
            }
        }
    }
}

interface Cancellable {
    fun cancel()
}

// Swift usage
func observeFlow() {
    let wrapper = FlowWrapper(flow: myFlow)
    
    let cancellable = wrapper.subscribe(
        onEach: { value in
            print("Got value: \(value)")
        },
        onComplete: {
            print("Completed")
        },
        onThrow: { error in
            print("Error: \(error)")
        }
    )
    
    // Later
    cancellable.cancel()
}
```

### Platform-Specific APIs

```kotlin
// iOS specific
expect class PlatformFile(path: String) {
    fun readText(): String
    fun writeText(text: String)
}

// iOS implementation
import platform.Foundation.*

actual class PlatformFile actual constructor(private val path: String) {
    actual fun readText(): String {
        val url = NSURL.fileURLWithPath(path)
        return NSString.stringWithContentsOfURL(
            url,
            encoding = NSUTF8StringEncoding,
            error = null
        ) as String
    }
    
    actual fun writeText(text: String) {
        val url = NSURL.fileURLWithPath(path)
        (text as NSString).writeToURL(
            url,
            atomically = true,
            encoding = NSUTF8StringEncoding,
            error = null
        )
    }
}
```

### Build Configuration

```kotlin
// build.gradle.kts
kotlin {
    ios()
    
    // Or specific targets
    iosArm64()
    iosX64() // iOS Simulator
    iosSimulatorArm64() // M1 Simulator
    
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
            }
        }
        
        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                // iOS-specific dependencies
            }
        }
        
        val iosArm64Main by getting {
            dependsOn(iosMain)
        }
        
        val iosX64Main by getting {
            dependsOn(iosMain)
        }
    }
}
```

### Real-World Example: Shared Networking

```kotlin
// commonMain
interface ApiService {
    suspend fun fetchUsers(): List<User>
    suspend fun createUser(user: User): User
}

expect class NetworkClient() {
    suspend fun get(url: String): String
    suspend fun post(url: String, body: String): String
}

class ApiServiceImpl(private val client: NetworkClient) : ApiService {
    override suspend fun fetchUsers(): List<User> {
        val json = client.get("https://api.example.com/users")
        return Json.decodeFromString(json)
    }
    
    override suspend fun createUser(user: User): User {
        val body = Json.encodeToString(user)
        val json = client.post("https://api.example.com/users", body)
        return Json.decodeFromString(json)
    }
}

// iosMain
import platform.Foundation.*

actual class NetworkClient {
    actual suspend fun get(url: String): String = suspendCoroutine { continuation ->
        val nsUrl = NSURL(string = url)
        val request = NSURLRequest(uRL = nsUrl)
        
        NSURLSession.sharedSession.dataTaskWithRequest(request) { data, response, error ->
            when {
                error != null -> continuation.resumeWithException(
                    Exception(error.localizedDescription)
                )
                data != null -> {
                    val string = NSString.create(data = data, encoding = NSUTF8StringEncoding)
                    continuation.resume(string.toString())
                }
                else -> continuation.resumeWithException(Exception("Unknown error"))
            }
        }.resume()
    }
    
    actual suspend fun post(url: String, body: String): String {
        // Similar implementation
        return ""
    }
}
```

### Use Cases

1. **iOS App Development**
   - Share business logic between Android and iOS
   - Keep UI platform-specific (Swift/Compose)

2. **Cross-Platform Libraries**
   - Networking, database, crypto
   - One codebase, multiple platforms

3. **Embedded Systems**
   - IoT devices
   - Microcontrollers

4. **Native CLI Tools**
   - Command-line utilities
   - System tools

5. **Game Development**
   - Shared game logic
   - Platform-specific rendering

### Best Practices

#### DO:

```kotlin
// Share business logic
// commonMain
class UserRepository {
    suspend fun getUsers(): List<User> { /* */ }
}

// Keep UI platform-specific
// iOS uses SwiftUI
// Android uses Jetpack Compose

// Use expect/actual for platform APIs
expect fun getCurrentTimestamp(): Long

// Memory management in cinterop
memScoped {
    val buffer = allocArray<ByteVar>(1024)
    // Auto-freed
}

// Wrap coroutines for iOS
class FlowWrapper<T>(private val flow: Flow<T>)
```

#### DON'T:

```kotlin
// Don't forget memory management
val buffer = nativeHeap.allocArray<ByteVar>(1024)
// Forgot to free - memory leak!

// Don't expose suspend functions directly to Swift
// Won't work well
suspend fun getData(): List<User>

// Don't share UI code
// Keep UI platform-specific

// Don't use old memory model patterns
// Use new memory model (1.7.20+)
```

---

## Ответ (RU)

**Kotlin/Native** - это технология для компиляции Kotlin кода в нативные бинарные файлы, которые могут работать без виртуальной машины. Позволяет Kotlin таргетировать платформы как iOS, macOS, Linux, Windows и встроенные системы.

### Ключевые возможности

1. **Нативная компиляция**: Компилируется в платформо-специфичный машинный код
2. **Не требует JVM**: Автономные исполняемые файлы
3. **C Interop**: Прямая интеграция с C библиотеками
4. **Objective-C/Swift Interop**: iOS/macOS разработка
5. **Мультиплатформа**: Разделение кода между платформами
6. **Управление памятью**: Автоматическое управление без GC

### C Interop

```kotlin
import kotlinx.cinterop.*
import curl.*

fun httpGet(url: String): String? {
    val curl = curl_easy_init()
    
    if (curl != null) {
        curl_easy_setopt(curl, CURLOPT_URL, url)
        val result = curl_easy_perform(curl)
        curl_easy_cleanup(curl)
        
        if (result == CURLE_OK) {
            return "Success"
        }
    }
    
    return null
}
```

### Objective-C/Swift Interop

```kotlin
// Kotlin
fun useObjCClass() {
    val obj = MyClass()
    val greeting = obj.greet("World")
    println(greeting) // Hello, World!
}
```

```swift
// Swift
import Shared

class ViewModel {
    func loadUsers() {
        SharedKt.iosGetUsers { users in
            print(users)
        }
    }
}
```

### Модель памяти

**Новая модель памяти (1.7.20+):**

```kotlin
// Конкурентная изменяемость как JVM/JS
class DataHolder {
    var data = "Hello" // Может быть изменено из любого потока
}
```

### Случаи использования

1. **iOS разработка** - Разделение бизнес-логики
2. **Кросс-платформенные библиотеки** - Один код, множество платформ
3. **Встроенные системы** - IoT устройства
4. **Нативные CLI инструменты** - Утилиты командной строки
5. **Разработка игр** - Разделённая игровая логика

---

## References

- [Kotlin/Native Documentation](https://kotlinlang.org/docs/native-overview.html)
- [C Interop](https://kotlinlang.org/docs/native-c-interop.html)
- [Objective-C Interop](https://kotlinlang.org/docs/native-objc-interop.html)
- [Memory Management](https://kotlinlang.org/docs/native-memory-manager.html)

## Related Questions

- [[q-expect-actual-kotlin--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-kotlin-collections--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC Links

- [[moc-kotlin]]
