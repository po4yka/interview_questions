---
tags:
  - design-patterns
  - behavioral-patterns
  - template-method
  - gof-patterns
  - hook-method
difficulty: medium
status: draft
---

# Template Method Pattern

# Question (EN)
> What is the Template Method pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Template Method? Когда и зачем его следует использовать?

---

## Answer (EN)



### Definition


The template method is a method in a superclass (usually an abstract superclass) that **defines the skeleton of an operation in terms of a number of high-level steps**. These steps are themselves implemented by additional *helper methods* in the same class as the template method.

The *helper methods* may be either:
- **Abstract methods** - Subclasses are required to provide concrete implementations
- **Hook methods** - Have empty bodies in the superclass, subclasses can optionally override them

The intent is to define the overall structure of the operation, while allowing subclasses to refine or redefine certain steps.

### Main Components


This pattern has two main parts:

1. **Template method** - Implemented in a base class, contains code for invariant parts of the algorithm. Calls helper methods for variant parts
2. **Subclasses** - Override empty or variant parts with specific algorithms. **Must not override the template method itself**

### Why is it Used?


The template method is used in frameworks for the following reasons:

1. **Lets subclasses implement varying behavior** - Through overriding of hook methods
2. **Avoids duplication** - General workflow implemented once in abstract class, variations in subclasses
3. **Controls specialization points** - If subclasses could override template method, they could make radical changes to workflow

## Пример: File Operation

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

**Output**:
```
Start creating file with name = SomeFileName
Creating file with name = SomeFileName
Finish creating file with name = SomeFileName
Start deleting file with name = SomeFileName
Deleting file with name = SomeFileName
Finish deleting file with name = SomeFileName
```

## Android Example: Data Loading

```kotlin
// Template class
abstract class DataLoader<T> {
    // Template method
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

## Kotlin Example: Report Generation

```kotlin
abstract class ReportGenerator {
    // Template method
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

## Android ViewModel Example

```kotlin
abstract class BaseViewModel<T> : ViewModel() {
    protected val _uiState = MutableStateFlow<UiState<T>>(UiState.Loading)
    val uiState: StateFlow<UiState<T>> = _uiState.asStateFlow()

    // Template method
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

// Concrete ViewModels
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


**Explanation**:

- **Template method** (`execute()`, `loadData()`, `generateReport()`) defines algorithm structure
- **Abstract methods** must be implemented by subclasses
- **Hook methods** can optionally be overridden
- **Concrete methods** are the same for all subclasses
- **Android**: Base ViewModels, Fragment lifecycles, data loading patterns

## Преимущества и недостатки

### Pros (Преимущества)


1. **Code reuse** - Common code in one place
2. **Control over algorithm** - Subclasses can't change overall structure
3. **Easy to extend** - Add new variations without changing algorithm
4. **Inversion of Control** - Framework calls subclass methods, not vice versa
5. **Open/Closed Principle** - Open for extension through subclasses

### Cons (Недостатки)


1. **Limited flexibility** - Clients can only change certain parts
2. **Inheritance required** - Requires extending a class
3. **Liskov Substitution** - Can violate if subclass changes behavior significantly
4. **Maintenance** - More classes to maintain
5. **Rigid structure** - Template method defines fixed sequence

## Best Practices

```kotlin
// - DO: Mark template method as final
abstract class DataProcessor {
    final fun process(data: String) {
        validate(data)
        transform(data)
        save(data)
    }
}

// - DO: Provide reasonable defaults for hooks
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

// - DO: Use for algorithms with common structure
abstract class AuthenticationFlow {
    fun authenticate(credentials: Credentials) {
        val validated = validateCredentials(credentials)
        val user = performLogin(validated)
        storeSession(user)
        navigateToHome()
    }
}

// - DON'T: Put business logic in template method
// Keep it focused on orchestration

// - DON'T: Make template method overrideable
// It defeats the purpose

// - DON'T: Have too many abstract methods
// Consider Strategy pattern instead
```

**English**: **Template Method** is a behavioral pattern that defines algorithm skeleton in base class, letting subclasses override specific steps without changing structure. **Problem**: Need to define algorithm structure while allowing customization of certain steps. **Solution**: Create template method with fixed sequence calling abstract/hook methods that subclasses implement. **Use when**: (1) Multiple algorithms share common structure, (2) Want to control specialization points, (3) Avoid code duplication in similar algorithms. **Android**: Base ViewModels, Activity/Fragment lifecycle, data loaders. **Pros**: code reuse, controlled extension, inversion of control. **Cons**: limited flexibility, requires inheritance. **Examples**: Data loading, report generation, authentication flows.

## Links

- [Template method pattern](https://en.wikipedia.org/wiki/Template_method_pattern)

## Further Reading

- [Template Method](https://refactoring.guru/design-patterns/template-method)
- [Template Method Design Pattern](https://sourcemaking.com/design_patterns/template_method)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение


The template method is a method in a superclass (usually an abstract superclass) that **defines the skeleton of an operation in terms of a number of high-level steps**. These steps are themselves implemented by additional *helper methods* in the same class as the template method.

The *helper methods* may be either:
- **Abstract methods** - Subclasses are required to provide concrete implementations
- **Hook methods** - Have empty bodies in the superclass, subclasses can optionally override them

The intent is to define the overall structure of the operation, while allowing subclasses to refine or redefine certain steps.

### Основные компоненты


This pattern has two main parts:

1. **Template method** - Implemented in a base class, contains code for invariant parts of the algorithm. Calls helper methods for variant parts
2. **Subclasses** - Override empty or variant parts with specific algorithms. **Must not override the template method itself**

### Почему используется?


The template method is used in frameworks for the following reasons:

1. **Lets subclasses implement varying behavior** - Through overriding of hook methods
2. **Avoids duplication** - General workflow implemented once in abstract class, variations in subclasses
3. **Controls specialization points** - If subclasses could override template method, they could make radical changes to workflow

### Объяснение


**Explanation**:

- **Template method** (`execute()`, `loadData()`, `generateReport()`) defines algorithm structure
- **Abstract methods** must be implemented by subclasses
- **Hook methods** can optionally be overridden
- **Concrete methods** are the same for all subclasses
- **Android**: Base ViewModels, Fragment lifecycles, data loading patterns

### Pros (Преимущества)


1. **Code reuse** - Common code in one place
2. **Control over algorithm** - Subclasses can't change overall structure
3. **Easy to extend** - Add new variations without changing algorithm
4. **Inversion of Control** - Framework calls subclass methods, not vice versa
5. **Open/Closed Principle** - Open for extension through subclasses

### Cons (Недостатки)


1. **Limited flexibility** - Clients can only change certain parts
2. **Inheritance required** - Requires extending a class
3. **Liskov Substitution** - Can violate if subclass changes behavior significantly
4. **Maintenance** - More classes to maintain
5. **Rigid structure** - Template method defines fixed sequence


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Behavioral Patterns
- [[q-strategy-pattern--design-patterns--medium]] - Strategy pattern
- [[q-observer-pattern--design-patterns--medium]] - Observer pattern
- [[q-command-pattern--design-patterns--medium]] - Command pattern
- [[q-iterator-pattern--design-patterns--medium]] - Iterator pattern
- [[q-state-pattern--design-patterns--medium]] - State pattern

### Creational Patterns
- [[q-factory-method-pattern--design-patterns--medium]] - Factory Method pattern

### Structural Patterns
- [[q-adapter-pattern--design-patterns--medium]] - Adapter pattern

