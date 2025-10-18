---
id: 20251012-400009
title: "Kotlin Context Receivers"
topic: android
difficulty: hard
status: draft
created: 2025-10-12
tags: [context-receivers, experimental, dsl, api-design, android/context-receivers, android/advanced-features, android/dsl, android/api-design, difficulty/hard]
moc: moc-android
related:   - q-kotlin-dsl-builders--kotlin--hard
  - q-sealed-classes-state-management--kotlin--medium
  - q-kotlin-coroutines-advanced--kotlin--hard
subtopics:   - kotlin
  - context-receivers
  - advanced-features
  - dsl
  - api-design
---

# Question (EN)

> What are Kotlin context receivers? How do they differ from extension functions, and when should you use them in Android?

# Вопрос (RU)

> Что такое context receivers в Kotlin? Чем они отличаются от extension-функций и когда их стоит применять в Android?

---

## Answer (EN)

### Problem Statement

Context receivers are an experimental Kotlin feature that allows declaring context dependencies for functions and properties. They provide a cleaner alternative to extension functions with receivers, enabling more expressive DSLs and dependency injection patterns.

**The Question:** What are context receivers? How do they differ from extension functions? When should you use them? What are real-world use cases in Android?

### Detailed Answer

---

### CONTEXT RECEIVERS BASICS

**Enable in build.gradle:**

```kotlin
compilerOptions {
    freeCompilerArgs.add("-Xcontext-receivers")
}
```

**Basic syntax:**

```kotlin
// Traditional extension function
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// With context receiver
context(Context)
fun showToast(message: String) {
    Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
}

// Usage (same for both)
fun Activity.someMethod() {
    showToast("Hello")
}
```

**Key differences:**

```
Extension function:
 Single receiver
 Stable language feature
 Can't combine multiple contexts easily

Context receiver:
 Multiple contexts possible
 More flexible
 Better for DSLs
 Experimental feature
```

---

### MULTIPLE CONTEXT RECEIVERS

```kotlin
// Multiple contexts
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// Usage
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Both Context and CoroutineScope available
        lifecycleScope.launch {
            launchAndShowToast("Hello from context receivers!")
        }
    }
}

// With 3 contexts
context(Context, LifecycleOwner, CoroutineScope)
fun observeAndShowData() {
    launch {
        // Can use Context
        val resources = this@Context.resources

        // Can use LifecycleOwner
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                // Handle resume
            }
        })

        // Can use CoroutineScope
        delay(1000)
    }
}
```

---

### LOGGING WITH CONTEXT RECEIVERS

```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

class AndroidLogger : Logger {
    override fun log(message: String) {
        Log.d("App", message)
    }

    override fun error(message: String, throwable: Throwable?) {
        Log.e("App", message, throwable)
    }
}

// Functions that require logging
context(Logger)
fun processData(data: String) {
    log("Processing data: $data")

    try {
        // Process
        log("Data processed successfully")
    } catch (e: Exception) {
        error("Failed to process data", e)
    }
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId")

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}

// Usage
class UserRepository(private val logger: Logger) {
    suspend fun loadUser(userId: String): User {
        with(logger) {
            return fetchUser(userId)
        }
    }
}
```

---

### DEPENDENCY INJECTION PATTERN

```kotlin
interface DatabaseProvider {
    val database: AppDatabase
}

interface NetworkProvider {
    val apiService: ApiService
}

interface LoggerProvider {
    val logger: Logger
}

// Repository with context receivers
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        // Try local database first
        database.userDao().getUser(userId)?.let {
            logger.log("User found in database")
            return it
        }

        // Fetch from network
        logger.log("Fetching from network")
        val user = apiService.getUser(userId)

        // Save to database
        database.userDao().insert(user)

        return user
    }

    suspend fun saveUser(user: User) {
        logger.log("Saving user: ${user.id}")
        database.userDao().insert(user)
    }
}

// Application-level providers
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database: AppDatabase by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    override val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    override val logger: Logger = AndroidLogger()
}

// Usage
class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) {
        UserRepository()
    }

    fun loadUser(userId: String) {
        viewModelScope.launch {
            val user = userRepository.getUser(userId)
            // Update UI
        }
    }
}
```

---

### DSL BUILDERS

```kotlin
// HTML DSL with context receivers
interface HtmlContext {
    fun tag(name: String, content: HtmlContext.() -> Unit)
    fun text(content: String)
}

class HtmlBuilder : HtmlContext {
    private val stringBuilder = StringBuilder()

    override fun tag(name: String, content: HtmlContext.() -> Unit) {
        stringBuilder.append("<$name>")
        content()
        stringBuilder.append("</$name>")
    }

    override fun text(content: String) {
        stringBuilder.append(content)
    }

    override fun toString() = stringBuilder.toString()
}

context(HtmlContext)
fun head(content: HtmlContext.() -> Unit) {
    tag("head", content)
}

context(HtmlContext)
fun body(content: HtmlContext.() -> Unit) {
    tag("body", content)
}

context(HtmlContext)
fun title(text: String) {
    tag("title") {
        text(text)
    }
}

context(HtmlContext)
fun h1(text: String) {
    tag("h1") {
        text(text)
    }
}

context(HtmlContext)
fun p(text: String) {
    tag("p") {
        text(text)
    }
}

// Build HTML
fun html(content: HtmlContext.() -> Unit): String {
    val builder = HtmlBuilder()
    builder.content()
    return builder.toString()
}

// Usage
val htmlContent = html {
    head {
        title("My Page")
    }
    body {
        h1("Welcome")
        p("This is a paragraph")
    }
}

// Output: <head><title>My Page</title></head><body><h1>Welcome</h1><p>This is a paragraph</p></body>
```

---

### COMPOSE-STYLE DSL

```kotlin
interface LayoutScope {
    fun component(content: @Composable () -> Unit)
}

class ColumnScope : LayoutScope {
    private val children = mutableListOf<@Composable () -> Unit>()

    override fun component(content: @Composable () -> Unit) {
        children.add(content)
    }

    @Composable
    fun render() {
        Column {
            children.forEach { it() }
        }
    }
}

context(LayoutScope)
fun text(text: String) {
    component {
        Text(text)
    }
}

context(LayoutScope)
fun button(text: String, onClick: () -> Unit) {
    component {
        Button(onClick = onClick) {
            Text(text)
        }
    }
}

context(LayoutScope)
fun image(imageRes: Int) {
    component {
        Image(
            painter = painterResource(imageRes),
            contentDescription = null
        )
    }
}

// Usage
@Composable
fun MyScreen() {
    val scope = ColumnScope()

    with(scope) {
        text("Welcome to my app")
        button("Click me") {
            println("Button clicked")
        }
        image(R.drawable.logo)
    }

    scope.render()
}
```

---

### TRANSACTION MANAGEMENT

```kotlin
interface TransactionContext {
    suspend fun <T> execute(block: suspend () -> T): T
    suspend fun rollback()
}

class DatabaseTransaction(private val db: AppDatabase) : TransactionContext {
    override suspend fun <T> execute(block: suspend () -> T): T {
        return db.withTransaction {
            block()
        }
    }

    override suspend fun rollback() {
        // Rollback logic
    }
}

context(TransactionContext)
suspend fun transferMoney(fromAccount: String, toAccount: String, amount: Double) {
    execute {
        // Deduct from source account
        val fromAcc = accountDao.getAccount(fromAccount)
        if (fromAcc.balance < amount) {
            rollback()
            throw InsufficientFundsException()
        }

        accountDao.updateBalance(fromAccount, fromAcc.balance - amount)

        // Add to destination account
        val toAcc = accountDao.getAccount(toAccount)
        accountDao.updateBalance(toAccount, toAcc.balance + amount)

        // Log transaction
        transactionDao.insert(
            Transaction(
                from = fromAccount,
                to = toAccount,
                amount = amount,
                timestamp = System.currentTimeMillis()
            )
        )
    }
}

// Usage
suspend fun performTransfer() {
    val transaction = DatabaseTransaction(database)

    with(transaction) {
        transferMoney("account1", "account2", 100.0)
    }
}
```

---

### VALIDATION CONTEXT

```kotlin
interface ValidationContext {
    fun addError(field: String, message: String)
    val errors: List<ValidationError>
    val isValid: Boolean
}

data class ValidationError(val field: String, val message: String)

class Validator : ValidationContext {
    private val _errors = mutableListOf<ValidationError>()

    override fun addError(field: String, message: String) {
        _errors.add(ValidationError(field, message))
    }

    override val errors: List<ValidationError>
        get() = _errors.toList()

    override val isValid: Boolean
        get() = _errors.isEmpty()
}

context(ValidationContext)
fun validateEmail(email: String) {
    if (email.isBlank()) {
        addError("email", "Email is required")
    } else if (!email.contains("@")) {
        addError("email", "Invalid email format")
    }
}

context(ValidationContext)
fun validatePassword(password: String) {
    if (password.length < 8) {
        addError("password", "Password must be at least 8 characters")
    }
    if (!password.any { it.isDigit() }) {
        addError("password", "Password must contain a digit")
    }
    if (!password.any { it.isUpperCase() }) {
        addError("password", "Password must contain uppercase letter")
    }
}

context(ValidationContext)
fun validateAge(age: Int) {
    if (age < 18) {
        addError("age", "Must be 18 or older")
    } else if (age > 120) {
        addError("age", "Invalid age")
    }
}

// Usage
data class RegistrationForm(
    val email: String,
    val password: String,
    val age: Int
)

fun validateRegistration(form: RegistrationForm): ValidationContext {
    val validator = Validator()

    with(validator) {
        validateEmail(form.email)
        validatePassword(form.password)
        validateAge(form.age)
    }

    return validator
}

// In ViewModel
fun register(form: RegistrationForm) {
    val validation = validateRegistration(form)

    if (validation.isValid) {
        // Proceed with registration
    } else {
        // Show errors
        validation.errors.forEach { error ->
            println("${error.field}: ${error.message}")
        }
    }
}
```

---

### ANDROID-SPECIFIC USE CASES

#### Resource Access

```kotlin
interface ResourceContext {
    val context: Context
    val resources: Resources
}

class AppResourceContext(override val context: Context) : ResourceContext {
    override val resources: Resources
        get() = context.resources
}

context(ResourceContext)
fun getString(@StringRes resId: Int): String {
    return resources.getString(resId)
}

context(ResourceContext)
fun getColor(@ColorRes resId: Int): Int {
    return resources.getColor(resId, null)
}

context(ResourceContext)
fun formatString(@StringRes resId: Int, vararg args: Any): String {
    return resources.getString(resId, *args)
}

// Usage
class MyViewModel(private val resourceContext: ResourceContext) : ViewModel() {
    fun getWelcomeMessage(): String {
        with(resourceContext) {
            return formatString(
                R.string.welcome_message,
                getString(R.string.app_name)
            )
        }
    }
}
```

---

#### Navigation

```kotlin
interface NavigationContext {
    fun navigate(destination: String)
    fun navigateBack()
    fun navigateUp()
}

class NavControllerContext(private val navController: NavController) : NavigationContext {
    override fun navigate(destination: String) {
        navController.navigate(destination)
    }

    override fun navigateBack() {
        navController.popBackStack()
    }

    override fun navigateUp() {
        navController.navigateUp()
    }
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

context(NavigationContext)
fun navigateToSettings() {
    navigate("settings")
}

context(NavigationContext)
fun closeScreen() {
    navigateBack()
}

// In Composable
@Composable
fun MyScreen(navController: NavController) {
    val navigationContext = NavControllerContext(navController)

    with(navigationContext) {
        Column {
            Button(onClick = { navigateToProfile("user123") }) {
                Text("View Profile")
            }

            Button(onClick = { navigateToSettings() }) {
                Text("Settings")
            }

            Button(onClick = { closeScreen() }) {
                Text("Back")
            }
        }
    }
}
```

---

### PERMISSIONS

```kotlin
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

class AndroidPermissionContext(
    private val activity: Activity
) : PermissionContext {
    override fun hasPermission(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            activity,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    override fun requestPermission(permission: String) {
        ActivityCompat.requestPermissions(
            activity,
            arrayOf(permission),
            1001
        )
    }
}

context(PermissionContext)
fun checkCameraPermission(): Boolean {
    return hasPermission(Manifest.permission.CAMERA)
}

context(PermissionContext)
fun requestCameraPermission() {
    if (!checkCameraPermission()) {
        requestPermission(Manifest.permission.CAMERA)
    }
}

context(PermissionContext, Context)
fun openCamera() {
    if (checkCameraPermission()) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestCameraPermission()
    }
}
```

---

### BEST PRACTICES

```kotlin
//  Use context receivers for cross-cutting concerns
context(Logger)
fun performOperation() {
    log("Starting operation")
    // ...
    log("Operation complete")
}

//  Combine with regular parameters
context(Context)
fun showNotification(title: String, message: String) {
    val notification = NotificationCompat.Builder(this@Context, "channel_id")
        .setContentTitle(title)
        .setContentText(message)
        .build()

    // Show notification
}

//  Use for DSLs
context(HtmlContext)
fun customComponent(data: String) {
    tag("div") {
        tag("span") {
            text(data)
        }
    }
}

//  Don't overuse - keep it simple
// Bad: too many contexts
context(Context, Logger, Database, Network, Cache, Analytics)
fun complexOperation() {
    // This is hard to understand and maintain
}

//  Better: group related contexts
interface AppContext : Logger, Database, Network {
    val context: Context
}

context(AppContext)
fun betterOperation() {
    // Cleaner with single context
}
```

---

### KEY TAKEAWAYS

1. **Context receivers** allow declaring context dependencies for functions
2. **Experimental feature** - requires compiler flag
3. **Multiple contexts** possible (unlike extension functions)
4. **Cleaner DSLs** compared to extension functions with receivers
5. **Dependency injection** pattern without framework overhead
6. **Cross-cutting concerns** like logging, validation, transactions
7. **Use with** to provide context at call site
8. **Better than** passing parameters repeatedly
9. **Compose well** with other Kotlin features
10. **Don't overuse** - keep contexts focused and cohesive

---

## Ответ (RU)

### Постановка задачи

Context receivers - экспериментальная возможность Kotlin, позволяющая объявлять контекстные зависимости для функций и свойств. Они предоставляют более чистую альтернативу extension функциям с receivers, обеспечивая более выразительные DSL и паттерны dependency injection.

**Вопрос:** Что такое context receivers? Чем они отличаются от extension функций? Когда их использовать? Какие реальные use cases в Android?

### Подробный ответ

---

### ОСНОВЫ CONTEXT RECEIVERS

**Включение в build.gradle:**

```kotlin
compilerOptions {
    freeCompilerArgs.add("-Xcontext-receivers")
}
```

**Базовый синтаксис:**

```kotlin
// Традиционная extension функция
fun Context.showToast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}

// С context receiver
context(Context)
fun showToast(message: String) {
    Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
}

// Использование (одинаково для обоих)
fun Activity.someMethod() {
    showToast("Hello")
}
```

**Ключевые отличия:**

```
Extension функция:
 Один receiver
 Стабильная возможность языка
 Сложно комбинировать несколько контекстов

Context receiver:
 Множественные контексты возможны
 Более гибкий
 Лучше для DSL
 Экспериментальная возможность
```

---

### МНОЖЕСТВЕННЫЕ CONTEXT RECEIVERS

Context receivers позволяют объявлять зависимость от нескольких контекстов одновременно:

```kotlin
// Множественные контексты
context(Context, CoroutineScope)
fun launchAndShowToast(message: String) {
    launch {
        delay(1000)
        Toast.makeText(this@Context, message, Toast.LENGTH_SHORT).show()
    }
}

// Использование с тремя контекстами
context(Context, LifecycleOwner, CoroutineScope)
fun observeAndShowData() {
    launch {
        // Можем использовать Context
        val resources = this@Context.resources

        // Можем использовать LifecycleOwner
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onResume(owner: LifecycleOwner) {
                // Обработка resume
            }
        })

        // Можем использовать CoroutineScope
        delay(1000)
    }
}
```

---

### ЛОГИРОВАНИЕ С CONTEXT RECEIVERS

```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

// Функции, требующие логирования
context(Logger)
fun processData(data: String) {
    log("Processing data: $data")

    try {
        // Обработка
        log("Data processed successfully")
    } catch (e: Exception) {
        error("Failed to process data", e)
    }
}

context(Logger)
suspend fun fetchUser(userId: String): User {
    log("Fetching user: $userId")

    return try {
        val user = apiService.getUser(userId)
        log("User fetched: ${user.name}")
        user
    } catch (e: Exception) {
        error("Failed to fetch user", e)
        throw e
    }
}

// Использование
class UserRepository(private val logger: Logger) {
    suspend fun loadUser(userId: String): User {
        with(logger) {
            return fetchUser(userId)
        }
    }
}
```

---

### ПАТТЕРН DEPENDENCY INJECTION

Context receivers предоставляют элегантный способ внедрения зависимостей без overhead DI-фреймворков:

```kotlin
interface DatabaseProvider {
    val database: AppDatabase
}

interface NetworkProvider {
    val apiService: ApiService
}

interface LoggerProvider {
    val logger: Logger
}

// Repository с context receivers
context(DatabaseProvider, NetworkProvider, LoggerProvider)
class UserRepository {
    suspend fun getUser(userId: String): User {
        logger.log("Getting user: $userId")

        // Сначала проверяем локальную БД
        database.userDao().getUser(userId)?.let {
            logger.log("User found in database")
            return it
        }

        // Загружаем из сети
        logger.log("Fetching from network")
        val user = apiService.getUser(userId)

        // Сохраняем в БД
        database.userDao().insert(user)

        return user
    }
}

// Провайдеры на уровне приложения
class AppDependencies : DatabaseProvider, NetworkProvider, LoggerProvider {
    override val database: AppDatabase by lazy {
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    override val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
    }

    override val logger: Logger = AndroidLogger()
}

// Использование
class MyViewModel(private val deps: AppDependencies) : ViewModel() {
    private val userRepository = with(deps) {
        UserRepository()
    }
}
```

---

### DSL BUILDERS

Context receivers идеально подходят для создания DSL:

```kotlin
interface HtmlContext {
    fun tag(name: String, content: HtmlContext.() -> Unit)
    fun text(content: String)
}

context(HtmlContext)
fun head(content: HtmlContext.() -> Unit) {
    tag("head", content)
}

context(HtmlContext)
fun body(content: HtmlContext.() -> Unit) {
    tag("body", content)
}

context(HtmlContext)
fun title(text: String) {
    tag("title") {
        text(text)
    }
}

context(HtmlContext)
fun h1(text: String) {
    tag("h1") {
        text(text)
    }
}

// Использование
val htmlContent = html {
    head {
        title("My Page")
    }
    body {
        h1("Welcome")
        p("This is a paragraph")
    }
}
```

---

### УПРАВЛЕНИЕ ТРАНЗАКЦИЯМИ

```kotlin
interface TransactionContext {
    suspend fun <T> execute(block: suspend () -> T): T
    suspend fun rollback()
}

context(TransactionContext)
suspend fun transferMoney(fromAccount: String, toAccount: String, amount: Double) {
    execute {
        // Снимаем со счёта-источника
        val fromAcc = accountDao.getAccount(fromAccount)
        if (fromAcc.balance < amount) {
            rollback()
            throw InsufficientFundsException()
        }

        accountDao.updateBalance(fromAccount, fromAcc.balance - amount)

        // Добавляем на счёт-получатель
        val toAcc = accountDao.getAccount(toAccount)
        accountDao.updateBalance(toAccount, toAcc.balance + amount)

        // Логируем транзакцию
        transactionDao.insert(
            Transaction(
                from = fromAccount,
                to = toAccount,
                amount = amount,
                timestamp = System.currentTimeMillis()
            )
        )
    }
}
```

---

### КОНТЕКСТ ВАЛИДАЦИИ

```kotlin
interface ValidationContext {
    fun addError(field: String, message: String)
    val errors: List<ValidationError>
    val isValid: Boolean
}

context(ValidationContext)
fun validateEmail(email: String) {
    if (email.isBlank()) {
        addError("email", "Email is required")
    } else if (!email.contains("@")) {
        addError("email", "Invalid email format")
    }
}

context(ValidationContext)
fun validatePassword(password: String) {
    if (password.length < 8) {
        addError("password", "Password must be at least 8 characters")
    }
    if (!password.any { it.isDigit() }) {
        addError("password", "Password must contain a digit")
    }
}

// Использование
fun validateRegistration(form: RegistrationForm): ValidationContext {
    val validator = Validator()

    with(validator) {
        validateEmail(form.email)
        validatePassword(form.password)
        validateAge(form.age)
    }

    return validator
}
```

---

### ANDROID-СПЕЦИФИЧНЫЕ USE CASES

#### Доступ к ресурсам

```kotlin
interface ResourceContext {
    val context: Context
    val resources: Resources
}

context(ResourceContext)
fun getString(@StringRes resId: Int): String {
    return resources.getString(resId)
}

context(ResourceContext)
fun getColor(@ColorRes resId: Int): Int {
    return resources.getColor(resId, null)
}

context(ResourceContext)
fun formatString(@StringRes resId: Int, vararg args: Any): String {
    return resources.getString(resId, *args)
}
```

---

#### Навигация

```kotlin
interface NavigationContext {
    fun navigate(destination: String)
    fun navigateBack()
    fun navigateUp()
}

context(NavigationContext)
fun navigateToProfile(userId: String) {
    navigate("profile/$userId")
}

context(NavigationContext)
fun navigateToSettings() {
    navigate("settings")
}

context(NavigationContext)
fun closeScreen() {
    navigateBack()
}
```

---

#### Разрешения (Permissions)

```kotlin
interface PermissionContext {
    fun hasPermission(permission: String): Boolean
    fun requestPermission(permission: String)
}

context(PermissionContext)
fun checkCameraPermission(): Boolean {
    return hasPermission(Manifest.permission.CAMERA)
}

context(PermissionContext)
fun requestCameraPermission() {
    if (!checkCameraPermission()) {
        requestPermission(Manifest.permission.CAMERA)
    }
}

context(PermissionContext, Context)
fun openCamera() {
    if (checkCameraPermission()) {
        val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        this@Context.startActivity(intent)
    } else {
        requestCameraPermission()
    }
}
```

---

### ЛУЧШИЕ ПРАКТИКИ

```kotlin
//  Используйте context receivers для cross-cutting concerns
context(Logger)
fun performOperation() {
    log("Starting operation")
    // ...
    log("Operation complete")
}

//  Комбинируйте с обычными параметрами
context(Context)
fun showNotification(title: String, message: String) {
    val notification = NotificationCompat.Builder(this@Context, "channel_id")
        .setContentTitle(title)
        .setContentText(message)
        .build()
}

//  Используйте для DSL
context(HtmlContext)
fun customComponent(data: String) {
    tag("div") {
        tag("span") {
            text(data)
        }
    }
}

//  Не злоупотребляйте - держите простым
// Плохо: слишком много контекстов
context(Context, Logger, Database, Network, Cache, Analytics)
fun complexOperation() {
    // Это сложно понять и поддерживать
}

//  Лучше: группируйте связанные контексты
interface AppContext : Logger, Database, Network {
    val context: Context
}

context(AppContext)
fun betterOperation() {
    // Чище с единым контекстом
}
```

---

### КЛЮЧЕВЫЕ ВЫВОДЫ

1. **Context receivers** позволяют объявлять контекстные зависимости для функций
2. **Экспериментальная возможность** - требует compiler flag `-Xcontext-receivers`
3. **Множественные контексты** возможны (в отличие от extension функций)
4. **Более чистые DSL** по сравнению с extension функциями с receivers
5. **Dependency injection** паттерн без overhead фреймворка
6. **Cross-cutting concerns** как logging, validation, transactions
7. **Используйте with** для предоставления контекста в месте вызова
8. **Лучше чем** передавать параметры многократно
9. **Хорошо комбинируются** с другими возможностями Kotlin
10. **Не злоупотребляйте** - держите контексты сфокусированными и связными

**Основные преимущества:**
- Чище чем extension функции для множественных зависимостей
- Отлично подходят для DSL и builder паттернов
- Упрощают dependency injection без фреймворков
- Уменьшают количество параметров функций
- Делают код более выразительным и читаемым

**Когда использовать:**
- Cross-cutting concerns (логирование, валидация)
- DSL builders
- Транзакционная логика
- Зависимости от Android компонентов (Context, Resources, NavController)
- Множественные связанные зависимости

---

## Follow-ups

1. How do context receivers affect binary compatibility?
2. What's the performance impact of context receivers?
3. How do you test code with context receivers?
4. What's the difference between context receivers and scope functions?
5. How do context receivers work with inline functions?
6. Can you use context receivers with suspend functions?
7. How do context receivers interact with coroutine context?
8. What are the limitations of context receivers?
9. How do you document APIs using context receivers?
10. When will context receivers become stable?

---

## Related Questions

### Prerequisites (Easier)

-   [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
-   [[q-context-types-android--android--medium]] - Fundamentals
-   [[q-how-to-register-broadcastreceiver-to-receive-messages--android--medium]] - Broadcast

### Related (Hard)

-   [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Fundamentals
