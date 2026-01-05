---
id: dp-003
title: "Template Method Pattern / Template Method Паттерн"
aliases: [Template Method Pattern, Template Method Паттерн]
topic: cs
subtopics: [inheritance, patterns]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-architecture-patterns]
created: 2025-10-15
updated: 2025-11-11
tags: [behavioral-patterns, design-patterns, difficulty/medium, gof-patterns, hook-method, template-method]

---
# Вопрос (RU)
> Что такое паттерн Template Method? Когда и зачем его следует использовать?

# Question (EN)
> What is the Template Method pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

Шаблонный метод (Template Method) — это метод в суперклассе (обычно абстрактном), который **определяет скелет операции в терминах нескольких высокоуровневых шагов**. Эти шаги реализуются дополнительными *вспомогательными методами* в том же классе, что и шаблонный метод.

*Вспомогательные методы* могут быть:
- **Абстрактными методами** — подклассы обязаны предоставить конкретные реализации
- **Hook-методами** — имеют пустые или дефолтные реализации в суперклассе, подклассы могут опционально их переопределить
- **Конкретными переопределяемыми методами** — не-абстрактные методы, которые могут быть переопределены для уточнения поведения

Цель состоит в том, чтобы определить общую структуру операции, позволяя подклассам уточнять или переопределять отдельные шаги без изменения последовательности алгоритма.

### Основные Компоненты

Этот паттерн состоит из двух основных частей:

1. **Template method (шаблонный метод)** — реализуется в базовом классе, содержит код для инвариантных частей алгоритма, вызывает вспомогательные методы для вариативных частей и обычно объявляется `final` (или оставляется не `open` в Kotlin), чтобы подклассы не меняли последовательность.
2. **Подклассы** — переопределяют абстрактные, hook- или специально разрешённые методы конкретными алгоритмами. **Не должны переопределять сам шаблонный метод.**

### Почему Используется?

Шаблонный метод используется во фреймворках и библиотеках по следующим причинам:

1. **Позволяет подклассам реализовывать различное поведение** — через переопределение абстрактных и hook-методов.
2. **Избегает дублирования** — общий workflow реализован один раз в абстрактном классе, вариации — в подклассах.
3. **Контролирует точки специализации** — запрет переопределения шаблонного метода сохраняет общий workflow и явно задаёт точки расширения.

### Пример: Операция С Файлом (File Operation)

```java
public abstract class Operation {
    abstract void start();
    abstract void work();
    abstract void finish();

    // Template method - определяет скелет алгоритма
    public final void execute() {
        start();
        work();
        finish();
    }
}

// Конкретные реализации
public final class CreateFileOperation extends Operation {
    private final String fileName;

    public CreateFileOperation(String fileName) {
        this.fileName = fileName;
    }

    @Override
    void start() {
        System.out.println("Start creating file with name = " + fileName);
    }

    @Override
    void work() {
        System.out.println("Creating file with name = " + fileName);
    }

    @Override
    void finish() {
        System.out.println("Finish creating file with name = " + fileName);
    }
}

public final class DeleteFileOperation extends Operation {
    private final String fileName;

    public DeleteFileOperation(String fileName) {
        this.fileName = fileName;
    }

    @Override
    void start() {
        System.out.println("Start deleting file with name = " + fileName);
    }

    @Override
    void work() {
        System.out.println("Deleting file with name = " + fileName);
    }

    @Override
    void finish() {
        System.out.println("Finish deleting file with name = " + fileName);
    }
}

// Использование
public static void main(String[] args) {
    String fileName = "SomeFileName";
    Operation create = new CreateFileOperation(fileName);
    Operation delete = new DeleteFileOperation(fileName);

    create.execute();
    delete.execute();
}
```

### Android Пример: Загрузка Данных (Data Loading)

```kotlin
// Шаблонный класс
abstract class DataLoader<T> {
    // Template method: определяет скелет алгоритма и не должен переопределяться
    fun loadData(id: String): Result<T> {
        showLoading()
        validateInput(id)
        val result = fetchData(id)
        processResult(result)
        hideLoading()
        return result
    }

    // Конкретные методы (общие для всех)
    private fun showLoading() {
        println("Showing loading indicator...")
    }

    private fun hideLoading() {
        println("Hiding loading indicator...")
    }

    // Абстрактные методы (обязательны к реализации)
    protected abstract fun validateInput(id: String)
    protected abstract fun fetchData(id: String): Result<T>

    // Hook-метод (может быть переопределён)
    protected open fun processResult(result: Result<T>) {
        println("Processing result: $result")
    }
}

// Конкретные реализации
class UserDataLoader : DataLoader<User>() {
    override fun validateInput(id: String) {
        require(id.isNotBlank()) { "User ID cannot be blank" }
    }

    override fun fetchData(id: String): Result<User> {
        println("Fetching user data from API...")
        return Result.success(User(id, "User $id"))
    }

    override fun processResult(result: Result<User>) {
        result.onSuccess { user ->
            System.out.println("User loaded: " + user.getName())
        }
    }
}

class ProductDataLoader : DataLoader<Product>() {
    override fun validateInput(id: String) {
        require(id.matches(Regex("\\d+"))) { "Product ID must be numeric" }
    }

    override fun fetchData(id: String): Result<Product> {
        println("Fetching product data from database...")
        return Result.success(Product(id, "Product $id"))
    }
}
```

### Kotlin Пример: Генерация Отчета (Report Generation)

```kotlin
abstract class ReportGenerator {
    // Template method: оркестрирует полный алгоритм
    fun generateReport(data: List<String>) {
        prepareData(data)
        val header = createHeader()
        val body = createBody(data)
        val footer = createFooter()

        val report = buildString {
            appendLine(header)
            appendLine(body)
            appendLine(footer)
        }

        outputReport(report)
        logGeneration()
    }

    // Конкретные методы
    private fun prepareData(data: List<String>) {
        println("Preparing data: ${data.size} items")
    }

    private fun logGeneration() {
        println("Report generation logged at ${System.currentTimeMillis()}")
    }

    // Абстрактные методы
    protected abstract fun createHeader(): String
    protected abstract fun createBody(data: List<String>): String
    protected abstract fun createFooter(): String

    // Hook-метод
    protected open fun outputReport(report: String) {
        println(report)
    }
}
```

### Android Пример: `ViewModel`

```kotlin
abstract class BaseViewModel<T> : ViewModel() {
    protected val _uiState = MutableStateFlow<UiState<T>>(UiState.Loading)
    val uiState: StateFlow<UiState<T>> = _uiState.asStateFlow()

    // Template method (final по умолчанию): определяет алгоритм загрузки данных
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            validatePreconditions()

            try {
                val data = fetchData()
                val processed = processData(data)
                _uiState.value = UiState.Success(processed)
                onDataLoaded(processed)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
                onError(e)
            }
        }
    }

    // Hook-методы
    protected open fun validatePreconditions() {}
    protected open fun onDataLoaded(data: T) {}
    protected open fun onError(error: Exception) {}

    // Абстрактные методы
    protected abstract suspend fun fetchData(): T
    protected abstract suspend fun processData(data: T): T
}
```

### Объяснение По Примерам

- **Template method** (`execute()`, `loadData()`, `generateReport()`) определяет структуру алгоритма и, как правило, не должен быть переопределяемым.
- **Абстрактные методы** реализуются в подклассах и задают вариативные шаги.
- **Hook-методы** дают возможность опционально изменять отдельные шаги.
- **Конкретные вспомогательные методы** инкапсулируют общее поведение. Некоторые из них могут быть осознанно сделаны переопределяемыми (например, помечены `open` в Kotlin) как расширяемые точки, в то время как остальные следует оставлять не переопределяемыми, если они не предназначены для изменения.
- В Android этот паттерн часто встречается в базовых `ViewModel`, жизненном цикле `Activity` / `Fragment`, потоках загрузки данных.

### Best Practices (Лучшие практики)

```kotlin
// DO: помечать шаблонный метод как final (или не делать open в Kotlin), чтобы не переопределяли
abstract class DataProcessor {
    final fun process(data: String) {
        validate(data)
        transform(data)
        save(data)
    }

    protected abstract fun validate(data: String)
    protected abstract fun transform(data: String)
    protected abstract fun save(data: String)
}

// DO: предоставлять разумные значения по умолчанию для hook-методов
abstract class BaseActivity : AppCompatActivity() {
    final override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setupView()
        initializeData()
        setupListeners() // Hook с реализацией по умолчанию
    }

    protected abstract fun setupView()
    protected abstract fun initializeData()
    protected open fun setupListeners() {} // Необязательный hook
}

// DO: использовать для алгоритмов с общим скелетом
abstract class AuthenticationFlow {
    fun authenticate(credentials: Credentials) {
        val validated = validateCredentials(credentials)
        val user = performLogin(validated)
        storeSession(user)
        navigateToHome()
    }

    protected abstract fun validateCredentials(credentials: Credentials): Credentials
    protected abstract fun performLogin(credentials: Credentials): User
    protected abstract fun storeSession(user: User)
    protected abstract fun navigateToHome()
}

// DON'T: размещать сложную бизнес-логику непосредственно в шаблонном методе.
// DON'T: делать шаблонный метод переопределяемым без веской причины.
// DON'T: иметь слишком много абстрактных методов — в таких случаях рассмотрите Strategy или композицию.
```

### Краткое Резюме (RU)

Паттерн Template Method относится к поведенческим. Он решает задачу: нужно зафиксировать структуру алгоритма, разрешив изменять отдельные шаги. Решение: вынести общий алгоритм в шаблонный метод базового класса, а вариативные части оформить как абстрактные или hook-методы. Использовать, когда:
- есть несколько алгоритмов с общим скелетом;
- важно контролировать точки расширения и избежать дублирования;
- требуется инверсия управления и предсказуемый, контролируемый workflow (например, в Android-фреймворках).
Плюсы: переиспользование кода, контролируемое расширение, соответствие принципу открытости/закрытости, инверсия управления.
Минусы: жесткая структура, зависимость от наследования, возможный риск нарушения принципа подстановки Лисков при ошибочном переопределении шагов или изменении инвариантов базового алгоритма.

---

## Answer (EN)

### Definition

The template method is a method in a superclass (usually an abstract superclass) that **defines the skeleton of an operation in terms of a number of high-level steps**. These steps are themselves implemented by additional *helper methods* in the same class as the template method.

The *helper methods* may be:
- **Abstract methods** - Subclasses are required to provide concrete implementations
- **Hook methods** - Often have empty or default implementations in the superclass; subclasses can optionally override them
- **Concrete overridable methods** - Non-abstract methods that subclasses may override to refine behavior

The intent is to define the overall structure of the operation, while allowing subclasses to refine or redefine certain steps without changing the algorithm's sequence.

### Main Components

This pattern has two main parts:

1. **Template method** - Implemented in a base class, contains code for invariant parts of the algorithm. Calls helper methods for variant parts and is typically declared `final` so subclasses cannot change the sequence.
2. **Subclasses** - Override abstract, hook, or designated overridable methods with specific algorithms. **Should not override the template method itself.**

### Why is it Used?

The template method is used in frameworks and libraries for the following reasons:

1. **Lets subclasses implement varying behavior** - Through overriding of abstract and hook methods.
2. **Avoids duplication** - General workflow implemented once in abstract class, variations in subclasses.
3. **Controls specialization points** - By preventing overriding of the template method, the framework keeps the workflow consistent while exposing controlled extension points.

### File Operation

```java
public abstract class Operation {
    abstract void start();
    abstract void work();
    abstract void finish();

    // Template method - defines algorithm skeleton
    public final void execute() {
        start();
        work();
        finish();
    }
}

// Concrete implementations
public final class CreateFileOperation extends Operation {
    private final String fileName;

    public CreateFileOperation(String fileName) {
        this.fileName = fileName;
    }

    @Override
    void start() {
        System.out.println("Start creating file with name = " + fileName);
    }

    @Override
    void work() {
        System.out.println("Creating file with name = " + fileName);
    }

    @Override
    void finish() {
        System.out.println("Finish creating file with name = " + fileName);
    }
}

public final class DeleteFileOperation extends Operation {
    private final String fileName;

    public DeleteFileOperation(String fileName) {
        this.fileName = fileName;
    }

    @Override
    void start() {
        System.out.println("Start deleting file with name = " + fileName);
    }

    @Override
    void work() {
        System.out.println("Deleting file with name = " + fileName);
    }

    @Override
    void finish() {
        System.out.println("Finish deleting file with name = " + fileName);
    }
}

// Usage
public static void main(String[] args) {
    String fileName = "SomeFileName";
    Operation create = new CreateFileOperation(fileName);
    Operation delete = new DeleteFileOperation(fileName);

    create.execute();
    delete.execute();
}
```

### Android Example: Data Loading

```kotlin
// Template class
abstract class DataLoader<T> {
    // Template method: defines the algorithm skeleton and should not be overridden
    fun loadData(id: String): Result<T> {
        showLoading()
        validateInput(id)
        val result = fetchData(id)
        processResult(result)
        hideLoading()
        return result
    }

    // Concrete methods (same for all)
    private fun showLoading() {
        println("Showing loading indicator...")
    }

    private fun hideLoading() {
        println("Hiding loading indicator...")
    }

    // Abstract methods (must be implemented)
    protected abstract fun validateInput(id: String)
    protected abstract fun fetchData(id: String): Result<T>

    // Hook method (can be overridden)
    protected open fun processResult(result: Result<T>) {
        println("Processing result: $result")
    }
}

// Concrete implementations
class UserDataLoader : DataLoader<User>() {
    override fun validateInput(id: String) {
        require(id.isNotBlank()) { "User ID cannot be blank" }
    }

    override fun fetchData(id: String): Result<User> {
        println("Fetching user data from API...")
        return Result.success(User(id, "User $id"))
    }

    override fun processResult(result: Result<User>) {
        result.onSuccess { user ->
            println("User loaded: ${user.name}")
        }
    }
}

class ProductDataLoader : DataLoader<Product>() {
    override fun validateInput(id: String) {
        require(id.matches(Regex("\\d+"))) { "Product ID must be numeric" }
    }

    override fun fetchData(id: String): Result<Product> {
        println("Fetching product data from database...")
        return Result.success(Product(id, "Product $id"))
    }
}

// Usage
fun main() {
    val userLoader = UserDataLoader()
    userLoader.loadData("123")

    val productLoader = ProductDataLoader()
    productLoader.loadData("456")
}
```

### Kotlin Example: Report Generation

```kotlin
abstract class ReportGenerator {
    // Template method: orchestrates the full algorithm
    fun generateReport(data: List<String>) {
        prepareData(data)
        val header = createHeader()
        val body = createBody(data)
        val footer = createFooter()

        val report = buildString {
            appendLine(header)
            appendLine(body)
            appendLine(footer)
        }

        outputReport(report)
        logGeneration()
    }

    // Concrete methods
    private fun prepareData(data: List<String>) {
        println("Preparing data: ${data.size} items")
    }

    private fun logGeneration() {
        println("Report generation logged at ${System.currentTimeMillis()}")
    }

    // Abstract methods
    protected abstract fun createHeader(): String
    protected abstract fun createBody(data: List<String>): String
    protected abstract fun createFooter(): String

    // Hook method
    protected open fun outputReport(report: String) {
        println(report)
    }
}

class PdfReportGenerator : ReportGenerator() {
    override fun createHeader() = "=== PDF REPORT ==="

    override fun createBody(data: List<String>) =
        data.joinToString("\n") { "• $it" }

    override fun createFooter() = "=== END OF REPORT ==="

    override fun outputReport(report: String) {
        println("Saving PDF to file...")
        super.outputReport(report)
    }
}

class HtmlReportGenerator : ReportGenerator() {
    override fun createHeader() = "<html><head><title>Report</title></head><body>"

    override fun createBody(data: List<String>) =
        "<ul>${data.joinToString("") { "<li>$it</li>" }}</ul>"

    override fun createFooter() = "</body></html>"

    override fun outputReport(report: String) {
        println("Opening HTML in browser...")
        super.outputReport(report)
    }
}
```

### Android `ViewModel` Example

```kotlin
abstract class BaseViewModel<T> : ViewModel() {
    protected val _uiState = MutableStateFlow<UiState<T>>(UiState.Loading)
    val uiState: StateFlow<UiState<T>> = _uiState.asStateFlow()

    // Template method (final by default): defines the data loading algorithm
    fun loadData() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            validatePreconditions()

            try {
                val data = fetchData()
                val processed = processData(data)
                _uiState.value = UiState.Success(processed)
                onDataLoaded(processed)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
                onError(e)
            }
        }
    }

    // Hook methods
    protected open fun validatePreconditions() {}
    protected open fun onDataLoaded(data: T) {}
    protected open fun onError(error: Exception) {}

    // Abstract methods
    protected abstract suspend fun fetchData(): T
    protected abstract suspend fun processData(data: T): T
}

// Concrete ViewModel
class UserListViewModel(
    private val repository: UserRepository
) : BaseViewModel<List<User>>() {

    override suspend fun fetchData() = repository.getUsers()

    override suspend fun processData(data: List<User>) =
        data.sortedBy { it.name }

    override fun onDataLoaded(data: List<User>) {
        println("Loaded ${data.size} users")
    }
}
```

### Explanation

- **Template method** (`execute()`, `loadData()`, `generateReport()`) defines algorithm structure and should not be overridden.
- **Abstract methods** must be implemented by subclasses.
- **Hook methods** can optionally be overridden.
- **Concrete helper methods** provide shared behavior and may be selectively overridable when explicitly marked (e.g., `open` in Kotlin) as extension points.
- **Concrete methods** that are not intended as extension points should remain non-overridable.
- **Android**: Base ViewModels, `Activity`/`Fragment` lifecycles, data loading patterns.

### Best Practices

```kotlin
// DO: Mark template method as final (or leave non-open in Kotlin) to prevent overriding
abstract class DataProcessor {
    final fun process(data: String) {
        validate(data)
        transform(data)
        save(data)
    }

    protected abstract fun validate(data: String)
    protected abstract fun transform(data: String)
    protected abstract fun save(data: String)
}

// DO: Provide reasonable defaults for hooks
abstract class BaseActivity : AppCompatActivity() {
    final override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setupView()
        initializeData()
        setupListeners() // Hook with default implementation
    }

    protected abstract fun setupView()
    protected abstract fun initializeData()
    protected open fun setupListeners() {} // Optional hook
}

// DO: Use for algorithms with common structure
abstract class AuthenticationFlow {
    fun authenticate(credentials: Credentials) {
        val validated = validateCredentials(credentials)
        val user = performLogin(validated)
        storeSession(user)
        navigateToHome()
    }

    protected abstract fun validateCredentials(credentials: Credentials): Credentials
    protected abstract fun performLogin(credentials: Credentials): User
    protected abstract fun storeSession(user: User)
    protected abstract fun navigateToHome()
}

// DON'T: Put complex business logic directly in the template method
// DON'T: Make template method overrideable without strong reason
// DON'T: Have too many abstract methods — consider Strategy or composition instead
```

### Summary (EN)

Template Method is a behavioral pattern that defines the algorithm skeleton in a base class, letting subclasses override specific steps without changing the overall structure.
- Problem: Need to define algorithm structure while allowing customization of certain steps.
- Solution: Create a template method with fixed sequence calling abstract/hook methods that subclasses implement.
- Use when: (1) Multiple algorithms share common structure, (2) You want to control specialization points, (3) You want to avoid code duplication, (4) You need inversion of control and a predictable, controlled workflow (e.g., in frameworks like Android).
- Android: Base ViewModels, `Activity`/`Fragment` lifecycle, data loaders.
- Pros: Code reuse, controlled extension, inversion of control.
- Cons: Limited flexibility, requires inheritance, and if extension points are misused or invariants are broken, there is a risk of violating the Liskov Substitution Principle.

---

## Дополнительные Вопросы (RU)

- Чем Template Method концептуально и по реализации отличается от паттерна Strategy?
- Когда предпочтительнее использовать композицию (например, Strategy), а не наследование с Template Method?
- Как неправильное использование Template Method может привести к нарушению принципа подстановки Лисков?

## Follow-ups

- How does Template Method differ from Strategy pattern conceptually and in implementation?
- When would you prefer composition (e.g., Strategy) over inheritance with Template Method?
- How can misuse of Template Method violate Liskov Substitution Principle?

---

## Ссылки (RU)

- [[c-architecture-patterns]]
- Статья "Template method pattern" на Wikipedia
- Материал "Template Method" на Refactoring Guru
- Обзор "Template Method Design Pattern" на Sourcemaking

## References

- [[c-architecture-patterns]]
- [Template method pattern](https://en.wikipedia.org/wiki/Template_method_pattern)
- [Template Method](https://refactoring.guru/design-patterns/template-method)
- [Template Method Design Pattern](https://sourcemaking.com/design_patterns/template_method)

---
*Source: Kirchhoff Android Interview Questions*