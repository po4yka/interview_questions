---
id: "20251013-600006"
title: "Design Patterns Fundamentals"
topic: architecture-patterns
difficulty: hard
status: draft
moc: moc-compSci
created: "2025-10-13"
tags: ["design-patterns", "gof", "creational", "structural", "behavioral", "singleton", "factory", "observer", "strategy", "decorator", "kotlin", "android"]
description: "Comprehensive coverage of essential design patterns (Creational, Structural, Behavioral) with real-world Android/Kotlin examples including Singleton, Factory, Observer, Strategy, Decorator, and more"
language: "en"
related: [q-singleton-pattern--design-patterns--easy, q-default-vs-io-dispatcher--programming-languages--medium, q-sharedflow-vs-stateflow--programming-languages--easy]
  - "20251012-600004"  # OOP Principles
  - "20251013-600005"  # Data Structures and Algorithms
subcategory: "design-patterns"
updated: "2025-10-13"
---
## Question

**English:**
Explain the fundamental design patterns from the Gang of Four (GoF) and modern patterns. Cover:

1. **Creational Patterns:** Singleton, Factory Method, Abstract Factory, Builder, Prototype
2. **Structural Patterns:** Adapter, Decorator, Facade, Proxy, Composite
3. **Behavioral Patterns:** Observer, Strategy, Command, State, Template Method, Chain of Responsibility
4. When to use each pattern and anti-patterns to avoid
5. Real-world Android/Kotlin implementations
6. Modern alternatives (Dependency Injection, Coroutines patterns)

Provide production Kotlin code with real Android examples.

**Russian:**
Объясните фундаментальные паттерны проектирования от Gang of Four (GoF) и современные паттерны. Охватите:

1. **Порождающие паттерны:** Singleton, Factory Method, Abstract Factory, Builder, Prototype
2. **Структурные паттерны:** Adapter, Decorator, Facade, Proxy, Composite
3. **Поведенческие паттерны:** Observer, Strategy, Command, State, Template Method, Chain of Responsibility
4. Когда использовать каждый паттерн и анти-паттерны которых следует избегать
5. Реальные Android/Kotlin реализации
6. Современные альтернативы (Dependency Injection, Coroutines паттерны)

Предоставьте production Kotlin код с реальными Android примерами.

---

## Answer

### 1. Creational Patterns / Порождающие Паттерны

#### 1.1 Singleton Pattern

**English:**
Ensures a class has only one instance and provides global access to it.

**Russian:**
Гарантирует, что класс имеет только один экземпляр и предоставляет глобальный доступ к нему.

```kotlin
// ❌ Bad: Not thread-safe
class SingletonBad {
    companion object {
        var instance: SingletonBad? = null
            get() {
                if (field == null) {
                    field = SingletonBad()  // Race condition!
                }
                return field
            }
    }
}

// ✅ Good: Thread-safe with object declaration
object DatabaseManager {
    private var database: Database? = null

    fun getDatabase(): Database {
        if (database == null) {
            synchronized(this) {
                if (database == null) {
                    database = Database.create()
                }
            }
        }
        return database!!
    }
}

// ✅ Better: Lazy initialization (Kotlin way)
class NetworkClient private constructor() {
    companion object {
        val instance: NetworkClient by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
            NetworkClient()
        }
    }

    fun makeRequest(url: String): Response {
        // Implementation
        return Response()
    }
}

// ✅ Best: Dependency Injection instead of Singleton
class Repository(private val apiService: ApiService) {
    fun getData(): List<Data> = apiService.fetch()
}

// In Hilt/Dagger:
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }
}

// Real Android example: Application class singleton
class MyApplication : Application() {
    companion object {
        lateinit var instance: MyApplication
            private set
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
    }
}

// Anti-pattern Warning:
// - Hard to test (global state)
// - Violates Single Responsibility
// - Hidden dependencies
//
// Modern Alternative: Use Dependency Injection!
```

#### 1.2 Factory Method Pattern

**English:**
Defines an interface for creating objects, but lets subclasses decide which class to instantiate.

**Russian:**
Определяет интерфейс для создания объектов, но позволяет подклассам решать, какой класс инстанцировать.

```kotlin
// ✅ Factory Method Pattern
sealed interface Notification {
    fun send(message: String)
}

class EmailNotification : Notification {
    override fun send(message: String) {
        println("Sending email: $message")
    }
}

class SMSNotification : Notification {
    override fun send(message: String) {
        println("Sending SMS: $message")
    }
}

class PushNotification : Notification {
    override fun send(message: String) {
        println("Sending push: $message")
    }
}

// Factory
abstract class NotificationFactory {
    abstract fun createNotification(): Notification

    fun notify(message: String) {
        val notification = createNotification()
        notification.send(message)
    }
}

class EmailNotificationFactory : NotificationFactory() {
    override fun createNotification(): Notification = EmailNotification()
}

class SMSNotificationFactory : NotificationFactory() {
    override fun createNotification(): Notification = SMSNotification()
}

// Usage
fun sendNotification(factory: NotificationFactory, message: String) {
    factory.notify(message)
}

// Kotlin idiomatic: Simple factory function
fun createNotification(type: String): Notification = when (type) {
    "email" -> EmailNotification()
    "sms" -> SMSNotification()
    "push" -> PushNotification()
    else -> throw IllegalArgumentException("Unknown type: $type")
}

// Real Android example: ViewModelProvider.Factory
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    // ViewModel logic
}

class UserViewModelFactory(
    private val repository: UserRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(UserViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return UserViewModel(repository) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}

// Usage in Fragment/Activity
val viewModel: UserViewModel by viewModels {
    UserViewModelFactory(repository)
}
```

#### 1.3 Abstract Factory Pattern

**English:**
Provides an interface for creating families of related objects without specifying their concrete classes.

**Russian:**
Предоставляет интерфейс для создания семейств связанных объектов без указания их конкретных классов.

```kotlin
// ✅ Abstract Factory Pattern
interface Button {
    fun render()
}

interface TextField {
    fun render()
}

// Material Design components
class MaterialButton : Button {
    override fun render() {
        println("Rendering Material Design button")
    }
}

class MaterialTextField : TextField {
    override fun render() {
        println("Rendering Material Design text field")
    }
}

// iOS-style components
class IOSButton : Button {
    override fun render() {
        println("Rendering iOS-style button")
    }
}

class IOSTextField : TextField {
    override fun render() {
        println("Rendering iOS-style text field")
    }
}

// Abstract Factory
interface UIFactory {
    fun createButton(): Button
    fun createTextField(): TextField
}

class MaterialUIFactory : UIFactory {
    override fun createButton(): Button = MaterialButton()
    override fun createTextField(): TextField = MaterialTextField()
}

class IOSUIFactory : UIFactory {
    override fun createButton(): Button = IOSButton()
    override fun createTextField(): TextField = IOSTextField()
}

// Client code
class Application(private val factory: UIFactory) {
    fun renderUI() {
        val button = factory.createButton()
        val textField = factory.createTextField()

        button.render()
        textField.render()
    }
}

// Usage
fun main() {
    val isMaterial = true
    val factory = if (isMaterial) MaterialUIFactory() else IOSUIFactory()
    val app = Application(factory)
    app.renderUI()
}

// Real Android example: Theme factory
interface ThemeFactory {
    fun getPrimaryColor(): Int
    fun getSecondaryColor(): Int
    fun getTypography(): Typeface
}

class LightThemeFactory : ThemeFactory {
    override fun getPrimaryColor() = Color.parseColor("#6200EE")
    override fun getSecondaryColor() = Color.parseColor("#03DAC5")
    override fun getTypography() = Typeface.DEFAULT
}

class DarkThemeFactory : ThemeFactory {
    override fun getPrimaryColor() = Color.parseColor("#BB86FC")
    override fun getSecondaryColor() = Color.parseColor("#03DAC5")
    override fun getTypography() = Typeface.DEFAULT_BOLD
}

class ThemedActivity : AppCompatActivity() {
    private lateinit var themeFactory: ThemeFactory

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val isDarkMode = resources.configuration.uiMode and
                Configuration.UI_MODE_NIGHT_MASK == Configuration.UI_MODE_NIGHT_YES

        themeFactory = if (isDarkMode) DarkThemeFactory() else LightThemeFactory()

        // Apply theme
        window.statusBarColor = themeFactory.getPrimaryColor()
    }
}
```

#### 1.4 Builder Pattern

**English:**
Separates object construction from its representation, allowing step-by-step creation.

**Russian:**
Отделяет конструирование объекта от его представления, позволяя пошаговое создание.

```kotlin
// ✅ Builder Pattern
data class User(
    val id: String,
    val name: String,
    val email: String?,
    val phone: String?,
    val address: String?,
    val age: Int?,
    val isVerified: Boolean
)

// Classic Builder
class UserBuilder {
    private var id: String = ""
    private var name: String = ""
    private var email: String? = null
    private var phone: String? = null
    private var address: String? = null
    private var age: Int? = null
    private var isVerified: Boolean = false

    fun id(id: String) = apply { this.id = id }
    fun name(name: String) = apply { this.name = name }
    fun email(email: String) = apply { this.email = email }
    fun phone(phone: String) = apply { this.phone = phone }
    fun address(address: String) = apply { this.address = address }
    fun age(age: Int) = apply { this.age = age }
    fun isVerified(isVerified: Boolean) = apply { this.isVerified = isVerified }

    fun build(): User {
        require(id.isNotEmpty()) { "ID is required" }
        require(name.isNotEmpty()) { "Name is required" }
        return User(id, name, email, phone, address, age, isVerified)
    }
}

// Usage
val user = UserBuilder()
    .id("123")
    .name("John Doe")
    .email("john@example.com")
    .age(30)
    .isVerified(true)
    .build()

// ✅ Kotlin DSL Builder
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?
) {
    class Builder {
        var url: String = ""
        var method: String = "GET"
        private val headers = mutableMapOf<String, String>()
        var body: String? = null

        fun header(key: String, value: String) {
            headers[key] = value
        }

        fun build(): HttpRequest {
            require(url.isNotEmpty()) { "URL is required" }
            return HttpRequest(url, method, headers, body)
        }
    }
}

fun httpRequest(init: HttpRequest.Builder.() -> Unit): HttpRequest {
    val builder = HttpRequest.Builder()
    builder.init()
    return builder.build()
}

// Usage with DSL
val request = httpRequest {
    url = "https://api.example.com/users"
    method = "POST"
    header("Content-Type", "application/json")
    header("Authorization", "Bearer token123")
    body = """{"name": "John"}"""
}

// Real Android example: AlertDialog builder
fun showDialog(context: Context) {
    AlertDialog.Builder(context)
        .setTitle("Confirm Action")
        .setMessage("Are you sure you want to proceed?")
        .setPositiveButton("Yes") { dialog, _ ->
            // Handle yes
            dialog.dismiss()
        }
        .setNegativeButton("No") { dialog, _ ->
            dialog.dismiss()
        }
        .setCancelable(false)
        .show()
}

// Real Android example: Retrofit builder
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com")
    .addConverterFactory(GsonConverterFactory.create())
    .addCallAdapterFactory(CoroutineCallAdapterFactory())
    .client(okHttpClient)
    .build()
```

#### 1.5 Prototype Pattern

**English:**
Creates new objects by cloning existing instances.

**Russian:**
Создает новые объекты путем клонирования существующих экземпляров.

```kotlin
// ✅ Prototype Pattern
interface Prototype<T> {
    fun clone(): T
}

data class Document(
    var title: String,
    var content: String,
    val metadata: MutableMap<String, String> = mutableMapOf()
) : Prototype<Document> {
    override fun clone(): Document {
        return Document(
            title = this.title,
            content = this.content,
            metadata = this.metadata.toMutableMap() // Deep copy
        )
    }
}

// Usage
val original = Document(
    title = "Report Q1",
    content = "Sales data...",
    metadata = mutableMapOf("author" to "John", "version" to "1.0")
)

val copy = original.clone()
copy.title = "Report Q2"  // Modify copy
copy.metadata["version"] = "2.0"

println(original.title)  // "Report Q1" - unchanged
println(copy.title)      // "Report Q2" - changed

// Kotlin idiomatic: data class copy()
data class UserProfile(
    val id: String,
    val name: String,
    val settings: UserSettings
)

data class UserSettings(
    val notifications: Boolean = true,
    val darkMode: Boolean = false
)

val user1 = UserProfile(
    id = "1",
    name = "Alice",
    settings = UserSettings(notifications = true)
)

// Shallow copy (references shared)
val user2 = user1.copy(name = "Bob")

// Deep copy (all new objects)
val user3 = user1.copy(
    name = "Charlie",
    settings = user1.settings.copy(darkMode = true)
)

// Real Android example: Intent cloning
fun cloneIntent(original: Intent): Intent {
    return Intent(original).apply {
        // All extras and data are copied
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
}

// Real Android example: Bundle cloning
fun cloneBundle(original: Bundle): Bundle {
    return Bundle(original)
}
```

---

### 2. Structural Patterns / Структурные Паттерны

#### 2.1 Adapter Pattern

**English:**
Converts interface of a class into another interface clients expect.

**Russian:**
Преобразует интерфейс класса в другой интерфейс, ожидаемый клиентами.

```kotlin
// ✅ Adapter Pattern

// Legacy payment system
class OldPaymentProcessor {
    fun processOldPayment(amount: Double, accountNumber: String) {
        println("Processing legacy payment: $$amount to account $accountNumber")
    }
}

// New payment interface
interface PaymentGateway {
    fun pay(amount: Double, recipient: String)
}

// Adapter
class PaymentAdapter(
    private val oldProcessor: OldPaymentProcessor
) : PaymentGateway {
    override fun pay(amount: Double, recipient: String) {
        // Adapt new interface to old implementation
        oldProcessor.processOldPayment(amount, recipient)
    }
}

// Usage
val oldSystem = OldPaymentProcessor()
val adapter: PaymentGateway = PaymentAdapter(oldSystem)
adapter.pay(100.0, "ACC123")

// Real Android example: RecyclerView.Adapter
class UserAdapter(
    private val users: List<User>
) : RecyclerView.Adapter<UserAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val nameText: TextView = view.findViewById(R.id.nameText)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_user, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.nameText.text = users[position].name
    }

    override fun getItemCount() = users.size
}

// Real Android example: Retrofit call adapter
interface ApiService {
    @GET("users")
    fun getUsers(): Call<List<User>>  // Retrofit Call

    @GET("users")
    suspend fun getUsersCoroutine(): List<User>  // Coroutine adapter
}
```

#### 2.2 Decorator Pattern

**English:**
Adds new functionality to objects dynamically without altering their structure.

**Russian:**
Добавляет новую функциональность объектам динамически без изменения их структуры.

```kotlin
// ✅ Decorator Pattern

interface Coffee {
    fun cost(): Double
    fun description(): String
}

class SimpleCoffee : Coffee {
    override fun cost() = 5.0
    override fun description() = "Simple coffee"
}

// Decorator base class
abstract class CoffeeDecorator(
    private val coffee: Coffee
) : Coffee {
    override fun cost() = coffee.cost()
    override fun description() = coffee.description()
}

// Concrete decorators
class MilkDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 1.5
    override fun description() = super.description() + ", milk"
}

class SugarDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 0.5
    override fun description() = super.description() + ", sugar"
}

class WhipCreamDecorator(coffee: Coffee) : CoffeeDecorator(coffee) {
    override fun cost() = super.cost() + 2.0
    override fun description() = super.description() + ", whip cream"
}

// Usage
val coffee: Coffee = WhipCreamDecorator(
    SugarDecorator(
        MilkDecorator(
            SimpleCoffee()
        )
    )
)

println("${coffee.description()}: $${coffee.cost()}")
// Output: Simple coffee, milk, sugar, whip cream: $9.0

// Real Android example: Context wrapper
class ThemeContextWrapper(
    base: Context,
    private val theme: Resources.Theme
) : ContextWrapper(base) {
    override fun getTheme(): Resources.Theme = theme
}

fun createThemedContext(context: Context, @StyleRes themeResId: Int): Context {
    val theme = context.resources.newTheme()
    theme.applyStyle(themeResId, true)
    return ThemeContextWrapper(context, theme)
}

// Real Android example: OkHttp interceptor (decorator for networking)
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        println("Sending request: ${request.url}")

        val response = chain.proceed(request)

        println("Received response: ${response.code}")

        return response
    }
}

val client = OkHttpClient.Builder()
    .addInterceptor(LoggingInterceptor())
    .addInterceptor(AuthInterceptor())  // Multiple decorators!
    .build()
```

#### 2.3 Facade Pattern

**English:**
Provides a simplified interface to a complex subsystem.

**Russian:**
Предоставляет упрощенный интерфейс к сложной подсистеме.

```kotlin
// ✅ Facade Pattern

// Complex subsystems
class VideoFile(val filename: String)

class AudioMixer {
    fun fix(video: VideoFile): String {
        println("AudioMixer: fixing audio...")
        return "audio-fixed"
    }
}

class VideoDecoder {
    fun decode(file: VideoFile, codec: String): String {
        println("VideoDecoder: decoding with $codec...")
        return "decoded-data"
    }
}

class BitrateReader {
    fun read(file: VideoFile): String {
        println("BitrateReader: reading bitrate...")
        return "1080p"
    }

    fun convert(data: String, format: String): String {
        println("BitrateReader: converting to $format...")
        return "converted-data"
    }
}

// Facade - simple interface
class VideoConverter {
    fun convert(filename: String, format: String): String {
        val file = VideoFile(filename)
        val bitrateReader = BitrateReader()
        val decoder = VideoDecoder()
        val mixer = AudioMixer()

        val bitrate = bitrateReader.read(file)
        val decodedVideo = decoder.decode(file, "h264")
        val fixedAudio = mixer.fix(file)
        val result = bitrateReader.convert(decodedVideo, format)

        return "Converted: $filename to $format"
    }
}

// Usage
val converter = VideoConverter()
val result = converter.convert("video.mp4", "avi")
println(result)

// Real Android example: Authentication facade
class AuthFacade(
    private val biometricManager: BiometricManager,
    private val secureStorage: SecureStorage,
    private val authService: AuthService
) {
    suspend fun login(username: String, password: String): Result<User> {
        return try {
            // Complex authentication flow simplified
            val hashedPassword = secureStorage.hash(password)
            val user = authService.authenticate(username, hashedPassword)

            if (biometricManager.isAvailable()) {
                biometricManager.saveCredentials(username)
            }

            secureStorage.saveToken(user.token)

            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun biometricLogin(): Result<User> {
        return try {
            val username = biometricManager.getSavedUsername()
            val isAuthenticated = biometricManager.authenticate()

            if (isAuthenticated) {
                val user = authService.loginWithBiometric(username)
                secureStorage.saveToken(user.token)
                Result.success(user)
            } else {
                Result.failure(Exception("Biometric authentication failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Real Android example: Retrofit facade
class ApiClient(private val apiService: ApiService) {
    suspend fun getUserProfile(userId: String): User? {
        return try {
            apiService.getUser(userId)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun updateProfile(user: User): Boolean {
        return try {
            apiService.updateUser(user)
            true
        } catch (e: Exception) {
            false
        }
    }
}
```

#### 2.4 Proxy Pattern

**English:**
Provides a surrogate or placeholder to control access to an object.

**Russian:**
Предоставляет суррогат или заполнитель для контроля доступа к объекту.

```kotlin
// ✅ Proxy Pattern

interface Image {
    fun display()
}

// Real subject
class RealImage(private val filename: String) : Image {
    init {
        loadFromDisk()
    }

    private fun loadFromDisk() {
        println("Loading image: $filename")
        Thread.sleep(1000) // Simulate expensive operation
    }

    override fun display() {
        println("Displaying image: $filename")
    }
}

// Proxy - lazy loading
class ProxyImage(private val filename: String) : Image {
    private var realImage: RealImage? = null

    override fun display() {
        if (realImage == null) {
            realImage = RealImage(filename)
        }
        realImage?.display()
    }
}

// Usage
val image: Image = ProxyImage("photo.jpg")
// Image not loaded yet
image.display()  // Now loaded and displayed
image.display()  // Already loaded, just display

// Protection Proxy
interface Document {
    fun view()
    fun edit(content: String)
}

class SecureDocument(private val content: String) : Document {
    override fun view() {
        println("Viewing: $content")
    }

    override fun edit(content: String) {
        println("Editing: $content")
    }
}

class DocumentProxy(
    private val document: Document,
    private val userRole: String
) : Document {
    override fun view() {
        document.view()  // Anyone can view
    }

    override fun edit(content: String) {
        if (userRole == "ADMIN" || userRole == "EDITOR") {
            document.edit(content)
        } else {
            println("Access denied: Insufficient permissions")
        }
    }
}

// Usage
val doc = SecureDocument("Confidential Data")
val proxy = DocumentProxy(doc, "VIEWER")

proxy.view()          // ✅ Allowed
proxy.edit("New")     // ❌ Access denied

// Real Android example: Lazy bitmap loading
class LazyBitmapProxy(
    private val context: Context,
    private val resourceId: Int
) {
    private var bitmap: Bitmap? = null

    fun getBitmap(): Bitmap {
        if (bitmap == null) {
            bitmap = BitmapFactory.decodeResource(context.resources, resourceId)
        }
        return bitmap!!
    }

    fun recycle() {
        bitmap?.recycle()
        bitmap = null
    }
}

// Real Android example: Retrofit with caching proxy
class CachedApiService(
    private val apiService: ApiService,
    private val cache: Cache
) : ApiService {
    override suspend fun getUser(userId: String): User {
        // Check cache first
        cache.get(userId)?.let { return it }

        // Fetch from network
        val user = apiService.getUser(userId)

        // Save to cache
        cache.put(userId, user)

        return user
    }

    override suspend fun updateUser(user: User) {
        apiService.updateUser(user)
        cache.invalidate(user.id)
    }
}
```

#### 2.5 Composite Pattern

**English:**
Composes objects into tree structures to represent part-whole hierarchies.

**Russian:**
Компонует объекты в древовидные структуры для представления иерархий часть-целое.

```kotlin
// ✅ Composite Pattern

interface FileSystemComponent {
    fun getSize(): Long
    fun print(indent: String = "")
}

class File(
    private val name: String,
    private val size: Long
) : FileSystemComponent {
    override fun getSize() = size

    override fun print(indent: String) {
        println("$indent- $name ($size bytes)")
    }
}

class Directory(
    private val name: String
) : FileSystemComponent {
    private val children = mutableListOf<FileSystemComponent>()

    fun add(component: FileSystemComponent) {
        children.add(component)
    }

    fun remove(component: FileSystemComponent) {
        children.remove(component)
    }

    override fun getSize(): Long {
        return children.sumOf { it.getSize() }
    }

    override fun print(indent: String) {
        println("$indent+ $name (${getSize()} bytes)")
        children.forEach { it.print("$indent  ") }
    }
}

// Usage
val root = Directory("root")
val documents = Directory("documents")
val photos = Directory("photos")

documents.add(File("resume.pdf", 1024))
documents.add(File("cover-letter.pdf", 512))

photos.add(File("vacation.jpg", 2048))
photos.add(File("family.jpg", 3072))

root.add(documents)
root.add(photos)
root.add(File("readme.txt", 256))

root.print()
// Output:
// + root (6912 bytes)
//   + documents (1536 bytes)
//     - resume.pdf (1024 bytes)
//     - cover-letter.pdf (512 bytes)
//   + photos (5120 bytes)
//     - vacation.jpg (2048 bytes)
//     - family.jpg (3072 bytes)
//   - readme.txt (256 bytes)

println("Total size: ${root.getSize()} bytes")

// Real Android example: View hierarchy
interface ViewComponent {
    fun render()
    fun measure(): Pair<Int, Int>
}

class TextView(private val text: String) : ViewComponent {
    override fun render() {
        println("Rendering text: $text")
    }

    override fun measure(): Pair<Int, Int> {
        return text.length * 10 to 20
    }
}

class ViewGroup(private val name: String) : ViewComponent {
    private val children = mutableListOf<ViewComponent>()

    fun addChild(child: ViewComponent) {
        children.add(child)
    }

    override fun render() {
        println("Rendering ViewGroup: $name")
        children.forEach { it.render() }
    }

    override fun measure(): Pair<Int, Int> {
        val childMeasures = children.map { it.measure() }
        val width = childMeasures.maxOfOrNull { it.first } ?: 0
        val height = childMeasures.sumOf { it.second }
        return width to height
    }
}

// Usage
val layout = ViewGroup("LinearLayout")
layout.addChild(TextView("Title"))
layout.addChild(TextView("Subtitle"))

val container = ViewGroup("FrameLayout")
container.addChild(layout)
container.addChild(TextView("Footer"))

container.render()
println("Container size: ${container.measure()}")
```

---

### 3. Behavioral Patterns / Поведенческие Паттерны

#### 3.1 Observer Pattern

**English:**
Defines a one-to-many dependency where when one object changes state, all dependents are notified.

**Russian:**
Определяет зависимость один-ко-многим, где при изменении состояния одного объекта все зависимые уведомляются.

```kotlin
// ✅ Observer Pattern

interface Observer {
    fun update(temperature: Float, humidity: Float, pressure: Float)
}

interface Subject {
    fun registerObserver(observer: Observer)
    fun removeObserver(observer: Observer)
    fun notifyObservers()
}

class WeatherStation : Subject {
    private val observers = mutableListOf<Observer>()
    private var temperature: Float = 0f
    private var humidity: Float = 0f
    private var pressure: Float = 0f

    override fun registerObserver(observer: Observer) {
        observers.add(observer)
    }

    override fun removeObserver(observer: Observer) {
        observers.remove(observer)
    }

    override fun notifyObservers() {
        observers.forEach { it.update(temperature, humidity, pressure) }
    }

    fun setMeasurements(temperature: Float, humidity: Float, pressure: Float) {
        this.temperature = temperature
        this.humidity = humidity
        this.pressure = pressure
        notifyObservers()
    }
}

class CurrentConditionsDisplay : Observer {
    override fun update(temperature: Float, humidity: Float, pressure: Float) {
        println("Current: ${temperature}°C, ${humidity}% humidity")
    }
}

class StatisticsDisplay : Observer {
    private val temperatures = mutableListOf<Float>()

    override fun update(temperature: Float, humidity: Float, pressure: Float) {
        temperatures.add(temperature)
        val avg = temperatures.average()
        println("Avg temperature: ${"%.1f".format(avg)}°C")
    }
}

// Usage
val weatherStation = WeatherStation()

val currentDisplay = CurrentConditionsDisplay()
val statsDisplay = StatisticsDisplay()

weatherStation.registerObserver(currentDisplay)
weatherStation.registerObserver(statsDisplay)

weatherStation.setMeasurements(25.5f, 65f, 1013f)
weatherStation.setMeasurements(27.0f, 70f, 1012f)

// Modern alternative: Flow/StateFlow
class WeatherRepository {
    private val _temperature = MutableStateFlow(0f)
    val temperature: StateFlow<Float> = _temperature.asStateFlow()

    fun updateTemperature(temp: Float) {
        _temperature.value = temp
    }
}

@Composable
fun WeatherScreen(repository: WeatherRepository) {
    val temperature by repository.temperature.collectAsState()

    Text(text = "Temperature: $temperature°C")
}

// Real Android example: LiveData observer
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _user.value = repository.getUser(userId)
        }
    }
}

// In Activity/Fragment
viewModel.user.observe(viewLifecycleOwner) { user ->
    // Update UI when user changes
    binding.nameText.text = user.name
}
```

#### 3.2 Strategy Pattern

**English:**
Defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Russian:**
Определяет семейство алгоритмов, инкапсулирует каждый и делает их взаимозаменяемыми.

```kotlin
// ✅ Strategy Pattern

interface SortStrategy {
    fun sort(list: MutableList<Int>)
}

class BubbleSortStrategy : SortStrategy {
    override fun sort(list: MutableList<Int>) {
        println("Sorting using bubble sort")
        for (i in list.indices) {
            for (j in 0 until list.size - i - 1) {
                if (list[j] > list[j + 1]) {
                    val temp = list[j]
                    list[j] = list[j + 1]
                    list[j + 1] = temp
                }
            }
        }
    }
}

class QuickSortStrategy : SortStrategy {
    override fun sort(list: MutableList<Int>) {
        println("Sorting using quick sort")
        quickSort(list, 0, list.size - 1)
    }

    private fun quickSort(list: MutableList<Int>, low: Int, high: Int) {
        if (low < high) {
            val pi = partition(list, low, high)
            quickSort(list, low, pi - 1)
            quickSort(list, pi + 1, high)
        }
    }

    private fun partition(list: MutableList<Int>, low: Int, high: Int): Int {
        val pivot = list[high]
        var i = low - 1
        for (j in low until high) {
            if (list[j] < pivot) {
                i++
                val temp = list[i]
                list[i] = list[j]
                list[j] = temp
            }
        }
        val temp = list[i + 1]
        list[i + 1] = list[high]
        list[high] = temp
        return i + 1
    }
}

class Sorter(private var strategy: SortStrategy) {
    fun setStrategy(strategy: SortStrategy) {
        this.strategy = strategy
    }

    fun sort(list: MutableList<Int>) {
        strategy.sort(list)
    }
}

// Usage
val list = mutableListOf(5, 2, 9, 1, 7)
val sorter = Sorter(BubbleSortStrategy())

sorter.sort(list)
println(list)

sorter.setStrategy(QuickSortStrategy())
sorter.sort(mutableListOf(5, 2, 9, 1, 7))

// Real Android example: Payment strategy
interface PaymentStrategy {
    suspend fun pay(amount: Double): Result<String>
}

class CreditCardPayment(
    private val cardNumber: String,
    private val cvv: String
) : PaymentStrategy {
    override suspend fun pay(amount: Double): Result<String> {
        // Process credit card payment
        return Result.success("Paid $$amount with credit card")
    }
}

class PayPalPayment(private val email: String) : PaymentStrategy {
    override suspend fun pay(amount: Double): Result<String> {
        // Process PayPal payment
        return Result.success("Paid $$amount with PayPal")
    }
}

class GooglePayPayment : PaymentStrategy {
    override suspend fun pay(amount: Double): Result<String> {
        // Process Google Pay payment
        return Result.success("Paid $$amount with Google Pay")
    }
}

class CheckoutViewModel : ViewModel() {
    private var paymentStrategy: PaymentStrategy? = null

    fun setPaymentMethod(strategy: PaymentStrategy) {
        paymentStrategy = strategy
    }

    fun checkout(amount: Double) {
        viewModelScope.launch {
            paymentStrategy?.pay(amount)?.onSuccess { message ->
                // Show success
            }?.onFailure { error ->
                // Show error
            }
        }
    }
}

// Usage
val viewModel = CheckoutViewModel()

// User selects payment method
when (selectedPaymentMethod) {
    PaymentMethod.CREDIT_CARD -> {
        viewModel.setPaymentMethod(CreditCardPayment("1234-5678", "123"))
    }
    PaymentMethod.PAYPAL -> {
        viewModel.setPaymentMethod(PayPalPayment("user@example.com"))
    }
    PaymentMethod.GOOGLE_PAY -> {
        viewModel.setPaymentMethod(GooglePayPayment())
    }
}

viewModel.checkout(99.99)
```

#### 3.3 Command Pattern

**English:**
Encapsulates a request as an object, allowing parameterization and queuing of requests.

**Russian:**
Инкапсулирует запрос как объект, позволяя параметризацию и постановку запросов в очередь.

```kotlin
// ✅ Command Pattern

interface Command {
    fun execute()
    fun undo()
}

class Light {
    fun turnOn() {
        println("Light is ON")
    }

    fun turnOff() {
        println("Light is OFF")
    }
}

class LightOnCommand(private val light: Light) : Command {
    override fun execute() {
        light.turnOn()
    }

    override fun undo() {
        light.turnOff()
    }
}

class LightOffCommand(private val light: Light) : Command {
    override fun execute() {
        light.turnOff()
    }

    override fun undo() {
        light.turnOn()
    }
}

// Invoker
class RemoteControl {
    private val history = mutableListOf<Command>()

    fun executeCommand(command: Command) {
        command.execute()
        history.add(command)
    }

    fun undo() {
        if (history.isNotEmpty()) {
            val command = history.removeAt(history.size - 1)
            command.undo()
        }
    }
}

// Usage
val light = Light()
val remote = RemoteControl()

remote.executeCommand(LightOnCommand(light))   // Light is ON
remote.executeCommand(LightOffCommand(light))  // Light is OFF
remote.undo()                                  // Light is ON (undo off)

// Real Android example: Text editor commands
interface TextCommand {
    fun execute()
    fun undo()
}

class InsertTextCommand(
    private val editText: EditText,
    private val text: String,
    private val position: Int
) : TextCommand {
    private var previousText: String = ""

    override fun execute() {
        previousText = editText.text.toString()
        val current = editText.text.toString()
        val newText = current.substring(0, position) + text + current.substring(position)
        editText.setText(newText)
    }

    override fun undo() {
        editText.setText(previousText)
    }
}

class DeleteTextCommand(
    private val editText: EditText,
    private val start: Int,
    private val end: Int
) : TextCommand {
    private var deletedText: String = ""

    override fun execute() {
        val current = editText.text.toString()
        deletedText = current.substring(start, end)
        val newText = current.substring(0, start) + current.substring(end)
        editText.setText(newText)
    }

    override fun undo() {
        val current = editText.text.toString()
        val newText = current.substring(0, start) + deletedText + current.substring(start)
        editText.setText(newText)
    }
}

class TextEditor {
    private val commandHistory = mutableListOf<TextCommand>()
    private val redoStack = mutableListOf<TextCommand>()

    fun execute(command: TextCommand) {
        command.execute()
        commandHistory.add(command)
        redoStack.clear()
    }

    fun undo() {
        if (commandHistory.isNotEmpty()) {
            val command = commandHistory.removeAt(commandHistory.size - 1)
            command.undo()
            redoStack.add(command)
        }
    }

    fun redo() {
        if (redoStack.isNotEmpty()) {
            val command = redoStack.removeAt(redoStack.size - 1)
            command.execute()
            commandHistory.add(command)
        }
    }
}
```

#### 3.4 State Pattern

**English:**
Allows an object to alter its behavior when its internal state changes.

**Russian:**
Позволяет объекту изменять поведение при изменении внутреннего состояния.

```kotlin
// ✅ State Pattern

interface PlayerState {
    fun play(player: MusicPlayer)
    fun pause(player: MusicPlayer)
    fun stop(player: MusicPlayer)
}

class PlayingState : PlayerState {
    override fun play(player: MusicPlayer) {
        println("Already playing")
    }

    override fun pause(player: MusicPlayer) {
        println("Pausing playback")
        player.state = PausedState()
    }

    override fun stop(player: MusicPlayer) {
        println("Stopping playback")
        player.state = StoppedState()
    }
}

class PausedState : PlayerState {
    override fun play(player: MusicPlayer) {
        println("Resuming playback")
        player.state = PlayingState()
    }

    override fun pause(player: MusicPlayer) {
        println("Already paused")
    }

    override fun stop(player: MusicPlayer) {
        println("Stopping from pause")
        player.state = StoppedState()
    }
}

class StoppedState : PlayerState {
    override fun play(player: MusicPlayer) {
        println("Starting playback")
        player.state = PlayingState()
    }

    override fun pause(player: MusicPlayer) {
        println("Cannot pause - not playing")
    }

    override fun stop(player: MusicPlayer) {
        println("Already stopped")
    }
}

class MusicPlayer {
    var state: PlayerState = StoppedState()

    fun play() = state.play(this)
    fun pause() = state.pause(this)
    fun stop() = state.stop(this)
}

// Usage
val player = MusicPlayer()
player.play()   // Starting playback
player.pause()  // Pausing playback
player.play()   // Resuming playback
player.stop()   // Stopping playback

// Modern alternative: Sealed class with when
sealed class OrderState {
    data object Pending : OrderState()
    data object Processing : OrderState()
    data object Shipped : OrderState()
    data object Delivered : OrderState()
    data class Cancelled(val reason: String) : OrderState()
}

class Order {
    var state: OrderState = OrderState.Pending
        private set

    fun process() {
        state = when (state) {
            is OrderState.Pending -> {
                println("Processing order")
                OrderState.Processing
            }
            else -> {
                println("Cannot process in current state")
                state
            }
        }
    }

    fun ship() {
        state = when (state) {
            is OrderState.Processing -> {
                println("Shipping order")
                OrderState.Shipped
            }
            else -> {
                println("Cannot ship in current state")
                state
            }
        }
    }

    fun deliver() {
        state = when (state) {
            is OrderState.Shipped -> {
                println("Order delivered")
                OrderState.Delivered
            }
            else -> {
                println("Cannot deliver in current state")
                state
            }
        }
    }

    fun cancel(reason: String) {
        state = when (state) {
            is OrderState.Pending, is OrderState.Processing -> {
                println("Cancelling order: $reason")
                OrderState.Cancelled(reason)
            }
            else -> {
                println("Cannot cancel in current state")
                state
            }
        }
    }
}

// Real Android example: Download state
sealed class DownloadState {
    data object Idle : DownloadState()
    data class Downloading(val progress: Int) : DownloadState()
    data class Completed(val filePath: String) : DownloadState()
    data class Failed(val error: String) : DownloadState()
}

class DownloadManager {
    private val _state = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val state: StateFlow<DownloadState> = _state.asStateFlow()

    suspend fun download(url: String) {
        _state.value = DownloadState.Downloading(0)

        try {
            // Simulate download with progress
            for (progress in 0..100 step 10) {
                delay(100)
                _state.value = DownloadState.Downloading(progress)
            }

            _state.value = DownloadState.Completed("/storage/file.zip")
        } catch (e: Exception) {
            _state.value = DownloadState.Failed(e.message ?: "Unknown error")
        }
    }
}

@Composable
fun DownloadScreen(manager: DownloadManager) {
    val state by manager.state.collectAsState()

    when (val currentState = state) {
        is DownloadState.Idle -> {
            Button(onClick = { /* start download */ }) {
                Text("Download")
            }
        }
        is DownloadState.Downloading -> {
            LinearProgressIndicator(progress = currentState.progress / 100f)
            Text("Downloading: ${currentState.progress}%")
        }
        is DownloadState.Completed -> {
            Text("Downloaded to: ${currentState.filePath}")
        }
        is DownloadState.Failed -> {
            Text("Error: ${currentState.error}", color = Color.Red)
        }
    }
}
```

#### 3.5 Template Method Pattern

**English:**
Defines skeleton of an algorithm in a method, deferring some steps to subclasses.

**Russian:**
Определяет скелет алгоритма в методе, откладывая некоторые шаги подклассам.

```kotlin
// ✅ Template Method Pattern

abstract class DataProcessor {
    // Template method
    fun process() {
        loadData()
        validateData()
        processData()
        saveData()
    }

    protected abstract fun loadData()
    protected abstract fun processData()

    protected open fun validateData() {
        println("Default validation")
    }

    protected open fun saveData() {
        println("Default save")
    }
}

class CSVDataProcessor : DataProcessor() {
    override fun loadData() {
        println("Loading CSV data")
    }

    override fun processData() {
        println("Processing CSV data")
    }

    override fun saveData() {
        println("Saving to database")
    }
}

class JSONDataProcessor : DataProcessor() {
    override fun loadData() {
        println("Loading JSON data")
    }

    override fun processData() {
        println("Processing JSON data")
    }

    override fun validateData() {
        println("JSON schema validation")
    }
}

// Usage
val csvProcessor = CSVDataProcessor()
csvProcessor.process()

val jsonProcessor = JSONDataProcessor()
jsonProcessor.process()

// Real Android example: Fragment lifecycle template
abstract class BaseFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Template method
        setupUI()
        setupObservers()
        loadData()
    }

    protected abstract fun setupUI()
    protected abstract fun setupObservers()
    protected abstract fun loadData()
}

class UserProfileFragment : BaseFragment() {
    override fun setupUI() {
        // Setup profile UI
    }

    override fun setupObservers() {
        // Observe user LiveData
        viewModel.user.observe(viewLifecycleOwner) { user ->
            // Update UI
        }
    }

    override fun loadData() {
        viewModel.loadUserProfile()
    }
}

// Modern alternative: Higher-order functions
fun <T> processData(
    load: () -> T,
    validate: (T) -> Boolean = { true },
    process: (T) -> T,
    save: (T) -> Unit
) {
    val data = load()
    if (validate(data)) {
        val processed = process(data)
        save(processed)
    }
}

// Usage
processData(
    load = { File("data.csv").readText() },
    validate = { it.isNotEmpty() },
    process = { it.uppercase() },
    save = { File("output.txt").writeText(it) }
)
```

#### 3.6 Chain of Responsibility Pattern

**English:**
Passes request along chain of handlers until one handles it.

**Russian:**
Передает запрос по цепочке обработчиков, пока один из них не обработает его.

```kotlin
// ✅ Chain of Responsibility Pattern

abstract class SupportHandler {
    protected var nextHandler: SupportHandler? = null

    fun setNext(handler: SupportHandler): SupportHandler {
        nextHandler = handler
        return handler
    }

    abstract fun handleRequest(request: SupportRequest)
}

data class SupportRequest(
    val level: Int,
    val message: String
)

class Level1Support : SupportHandler() {
    override fun handleRequest(request: SupportRequest) {
        if (request.level <= 1) {
            println("Level 1 Support: Handling ${request.message}")
        } else {
            println("Level 1 Support: Escalating...")
            nextHandler?.handleRequest(request)
        }
    }
}

class Level2Support : SupportHandler() {
    override fun handleRequest(request: SupportRequest) {
        if (request.level <= 2) {
            println("Level 2 Support: Handling ${request.message}")
        } else {
            println("Level 2 Support: Escalating...")
            nextHandler?.handleRequest(request)
        }
    }
}

class Level3Support : SupportHandler() {
    override fun handleRequest(request: SupportRequest) {
        println("Level 3 Support: Handling ${request.message}")
    }
}

// Usage
val level1 = Level1Support()
val level2 = Level2Support()
val level3 = Level3Support()

level1.setNext(level2).setNext(level3)

level1.handleRequest(SupportRequest(1, "Password reset"))
level1.handleRequest(SupportRequest(2, "Bug in app"))
level1.handleRequest(SupportRequest(3, "System crash"))

// Real Android example: Event handling chain
interface EventHandler {
    fun handle(event: TouchEvent): Boolean
    fun setNext(handler: EventHandler): EventHandler
}

class TouchEvent(val x: Float, val y: Float, val action: Int)

abstract class BaseEventHandler : EventHandler {
    protected var nextHandler: EventHandler? = null

    override fun setNext(handler: EventHandler): EventHandler {
        nextHandler = handler
        return handler
    }
}

class ClickHandler : BaseEventHandler() {
    override fun handle(event: TouchEvent): Boolean {
        return if (event.action == MotionEvent.ACTION_UP) {
            println("Handling click at (${event.x}, ${event.y})")
            true
        } else {
            nextHandler?.handle(event) ?: false
        }
    }
}

class LongPressHandler : BaseEventHandler() {
    override fun handle(event: TouchEvent): Boolean {
        return if (event.action == MotionEvent.ACTION_LONG_PRESS) {
            println("Handling long press")
            true
        } else {
            nextHandler?.handle(event) ?: false
        }
    }
}

class SwipeHandler : BaseEventHandler() {
    override fun handle(event: TouchEvent): Boolean {
        // Detect swipe
        println("Handling swipe")
        return true
    }
}

// Modern alternative: List of handlers
class EventProcessor {
    private val handlers = mutableListOf<(TouchEvent) -> Boolean>()

    fun addHandler(handler: (TouchEvent) -> Boolean) {
        handlers.add(handler)
    }

    fun process(event: TouchEvent): Boolean {
        for (handler in handlers) {
            if (handler(event)) {
                return true
            }
        }
        return false
    }
}

// Usage
val processor = EventProcessor()
processor.addHandler { event ->
    if (event.action == MotionEvent.ACTION_UP) {
        println("Click handled")
        true
    } else false
}
processor.addHandler { event ->
    if (event.action == MotionEvent.ACTION_LONG_PRESS) {
        println("Long press handled")
        true
    } else false
}
```

---

### Summary / Резюме

**English:**

**Creational Patterns:**
- **Singleton:** Single instance (use DI instead)
- **Factory Method:** Create objects without specifying exact class
- **Abstract Factory:** Create families of related objects
- **Builder:** Construct complex objects step-by-step
- **Prototype:** Clone existing objects

**Structural Patterns:**
- **Adapter:** Convert interface to another
- **Decorator:** Add functionality dynamically
- **Facade:** Simplify complex subsystem
- **Proxy:** Control access to object
- **Composite:** Tree structures of objects

**Behavioral Patterns:**
- **Observer:** Notify dependents of state changes (LiveData, Flow)
- **Strategy:** Interchangeable algorithms
- **Command:** Encapsulate requests as objects
- **State:** Change behavior based on state (sealed classes)
- **Template Method:** Algorithm skeleton with customizable steps
- **Chain of Responsibility:** Pass request along chain

**Modern Android Alternatives:**
- Dependency Injection instead of Singleton
- StateFlow/SharedFlow instead of classic Observer
- Sealed classes for State pattern
- Coroutines for async patterns

**Russian:**

**Порождающие паттерны:**
- **Singleton:** Единственный экземпляр (лучше использовать DI)
- **Factory Method:** Создание объектов без указания точного класса
- **Abstract Factory:** Создание семейств связанных объектов
- **Builder:** Пошаговое построение сложных объектов
- **Prototype:** Клонирование существующих объектов

**Структурные паттерны:**
- **Adapter:** Преобразование интерфейса в другой
- **Decorator:** Динамическое добавление функциональности
- **Facade:** Упрощение сложной подсистемы
- **Proxy:** Контроль доступа к объекту
- **Composite:** Древовидные структуры объектов

**Поведенческие паттерны:**
- **Observer:** Уведомление зависимостей об изменениях (LiveData, Flow)
- **Strategy:** Взаимозаменяемые алгоритмы
- **Command:** Инкапсуляция запросов как объектов
- **State:** Изменение поведения на основе состояния (sealed классы)
- **Template Method:** Скелет алгоритма с настраиваемыми шагами
- **Chain of Responsibility:** Передача запроса по цепочке

**Современные Android альтернативы:**
- Dependency Injection вместо Singleton
- StateFlow/SharedFlow вместо классического Observer
- Sealed классы для State паттерна
- Coroutines для асинхронных паттернов

---

## Follow-up Questions / Вопросы для Закрепления

1. **What is the main problem with Singleton pattern? What's the modern alternative?**
   **В чем основная проблема паттерна Singleton? Какая современная альтернатива?**

2. **When would you use Factory Method vs Abstract Factory?**
   **Когда использовать Factory Method против Abstract Factory?**

3. **Explain the difference between Decorator and Proxy patterns.**
   **Объясните разницу между паттернами Decorator и Proxy.**

4. **How does StateFlow/SharedFlow replace the classic Observer pattern?**
   **Как StateFlow/SharedFlow заменяет классический паттерн Observer?**

5. **What are the benefits of using Builder pattern in Android?**
   **Каковы преимущества использования паттерна Builder в Android?**

6. **When would you use Strategy pattern? Give an Android example.**
   **Когда бы вы использовали паттерн Strategy? Приведите Android пример.**

7. **Explain how RecyclerView.Adapter is an example of Adapter pattern.**
   **Объясните, как RecyclerView.Adapter является примером паттерна Adapter.**

8. **What is the difference between State pattern and sealed classes?**
   **В чем разница между паттерном State и sealed классами?**

9. **How does Command pattern enable undo/redo functionality?**
   **Как паттерн Command обеспечивает функциональность отмены/повтора?**

10. **Why is Composition preferred over Inheritance? Relate to Decorator pattern.**
    **Почему композиция предпочтительнее наследования? Свяжите с паттерном Decorator.**

## Related Questions

- [[q-singleton-pattern--design-patterns--easy]]
- [[q-default-vs-io-dispatcher--programming-languages--medium]]
- [[q-sharedflow-vs-stateflow--programming-languages--easy]]
