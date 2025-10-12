---
title: MVVM Pattern (Model-View-ViewModel)
topic: architecture-patterns
subtopics:
  - android-architecture
  - data-binding
  - reactive-programming
difficulty: medium
related:
  - mvp-pattern
  - mvi-pattern
  - clean-architecture
  - livedata
status: draft
---

# MVVM Pattern / Паттерн MVVM (Model-View-ViewModel)

# Question (EN)
> What is the MVVM pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн MVVM? Когда и зачем его следует использовать?

---

## Answer (EN)


### Definition
**Model-View-ViewModel (MVVM)** is a software architectural pattern that facilitates the separation of the development of the UI from the development of the business logic or back-end logic (the model) so that the view is not dependent on any specific model platform.

### Components
The separate code layers of MVVM are:
- **Model**: This layer is responsible for the abstraction of the data sources. Model and ViewModel work together to get and save the data
- **View**: The purpose of this layer is to inform the ViewModel about the user's action. This layer observes the ViewModel and does not contain any kind of application logic
- **ViewModel**: It exposes those data streams which are relevant to the View. Moreover, it serves as a link between the Model and the View

### Key Characteristics
It is important to note that in MVVM:
- The view doesn't maintain state information; instead, it is synchronized with the ViewModel
- The ViewModel isolates the presentation layer and offers methods and commands for managing the state of a view and manipulating the model
- The view and the ViewModel communicate using methods, properties, and events
- The view and the ViewModel have bi-directional data binding, or two-way data binding, which guarantees that the ViewModel's models and properties are in sync with the view

### Advantages
Advantages of MVVM:
- **Maintainability** - Can remain agile and keep releasing successive versions quickly
- **Extensibility** - Have the ability to replace or add new pieces of code
- **Testability** - Easier to write unit tests against a core logic
- **Transparent Communication** - The view model provides a transparent interface to the view controller, which it uses to populate the view layer and interact with the model layer, which results in a transparent communication between the layers of your application

### Disadvantages
Disadvantages of MVVM:
- Some people think that for simple UIs, MVVM can be overkill
- In bigger cases, it can be hard to design the ViewModel
- Debugging would be a bit difficult when we have complex data bindings

### Key Principles
1. **Separation of Concerns**: Clear separation between UI, business logic, and data
2. **Observable Pattern**: ViewModel exposes observable data that View subscribes to
3. **No View Reference**: ViewModel has no reference to View
4. **Lifecycle Awareness**: ViewModel survives configuration changes

### Example Structure

```kotlin
// Model - Data class and repository
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        // Fetch from network/database
        return User(userId, "John Doe", "john@example.com")
    }
}

// ViewModel
class UserViewModel : ViewModel() {
    private val repository = UserRepository()

    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        _loading.value = true

        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
                _loading.value = false
            } catch (e: Exception) {
                _error.value = e.message
                _loading.value = false
            }
        }
    }
}

// View - Activity/Fragment
class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel
    private lateinit var binding: ActivityUserBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Initialize ViewModel
        viewModel = ViewModelProvider(this).get(UserViewModel::class.java)

        // Observe LiveData
        viewModel.user.observe(this) { user ->
            binding.nameTextView.text = user.name
            binding.emailTextView.text = user.email
        }

        viewModel.loading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        viewModel.error.observe(this) { errorMessage ->
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show()
        }

        // Load user data
        viewModel.loadUser(1)
    }
}
```

### Android Jetpack Components
MVVM in Android is typically implemented using:
- **ViewModel**: Stores and manages UI-related data in a lifecycle-conscious way
- **LiveData**: Observable data holder class that is lifecycle-aware
- **Data Binding**: Allows you to bind UI components to data sources declaratively
- **Repository Pattern**: Mediates between different data sources

### Use Cases in Android
- Modern Android applications following Google's recommended architecture
- Applications using Jetpack components (ViewModel, LiveData, Room)
- Projects requiring reactive UI updates
- Applications with complex state management
- Apps needing to survive configuration changes

---



## Ответ (RU)

### Определение
**Model-View-ViewModel (MVVM)** - это программный архитектурный паттерн, который облегчает разделение разработки UI от разработки бизнес-логики или бэкенд-логики (модели), так что представление не зависит от какой-либо конкретной платформы модели.

### Компоненты
Отдельные слои кода MVVM:
- **Model (Модель)**: Этот слой отвечает за абстракцию источников данных. Model и ViewModel работают вместе для получения и сохранения данных
- **View (Представление)**: Цель этого слоя - информировать ViewModel о действиях пользователя. Этот слой наблюдает за ViewModel и не содержит никакой логики приложения
- **ViewModel (Модель Представления)**: Она предоставляет те потоки данных, которые релевантны для View. Более того, она служит связью между Model и View

### Ключевые Характеристики
Важно отметить, что в MVVM:
- View не поддерживает информацию о состоянии; вместо этого она синхронизирована с ViewModel
- ViewModel изолирует слой представления и предлагает методы и команды для управления состоянием представления и манипулирования моделью
- View и ViewModel общаются, используя методы, свойства и события
- View и ViewModel имеют двунаправленную привязку данных, или двустороннюю привязку данных, которая гарантирует, что модели и свойства ViewModel синхронизированы с представлением

### Преимущества
Преимущества MVVM:
- **Поддерживаемость** - Можно оставаться гибким и продолжать быстро выпускать последовательные версии
- **Расширяемость** - Есть возможность заменять или добавлять новые части кода
- **Тестируемость** - Легче писать unit-тесты для основной логики
- **Прозрачная коммуникация** - View model предоставляет прозрачный интерфейс для view controller, который он использует для заполнения слоя view и взаимодействия со слоем model, что приводит к прозрачной коммуникации между слоями вашего приложения

### Недостатки
Недостатки MVVM:
- Некоторые люди думают, что для простых UI MVVM может быть излишним
- В более крупных случаях может быть сложно спроектировать ViewModel
- Отладка была бы немного сложной, когда у нас есть сложные привязки данных

### Ключевые Принципы
1. **Разделение ответственности**: Четкое разделение между UI, бизнес-логикой и данными
2. **Паттерн наблюдателя**: ViewModel предоставляет наблюдаемые данные, на которые подписывается View
3. **Нет ссылки на View**: ViewModel не имеет ссылки на View
4. **Осведомленность о жизненном цикле**: ViewModel переживает изменения конфигурации

### Пример Структуры

```kotlin
// Model - Data-класс и репозиторий
data class User(val id: Int, val name: String, val email: String)

class UserRepository {
    fun getUser(userId: Int): User {
        // Получение из сети/базы данных
        return User(userId, "Иван Иванов", "ivan@example.com")
    }
}

// ViewModel
class UserViewModel : ViewModel() {
    private val repository = UserRepository()

    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    fun loadUser(userId: Int) {
        _loading.value = true

        viewModelScope.launch {
            try {
                val userData = repository.getUser(userId)
                _user.value = userData
                _loading.value = false
            } catch (e: Exception) {
                _error.value = e.message
                _loading.value = false
            }
        }
    }
}

// View - Activity/Fragment
class UserActivity : AppCompatActivity() {
    private lateinit var viewModel: UserViewModel
    private lateinit var binding: ActivityUserBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityUserBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Инициализация ViewModel
        viewModel = ViewModelProvider(this).get(UserViewModel::class.java)

        // Наблюдение за LiveData
        viewModel.user.observe(this) { user ->
            binding.nameTextView.text = user.name
            binding.emailTextView.text = user.email
        }

        viewModel.loading.observe(this) { isLoading ->
            binding.progressBar.visibility = if (isLoading) View.VISIBLE else View.GONE
        }

        viewModel.error.observe(this) { errorMessage ->
            Toast.makeText(this, errorMessage, Toast.LENGTH_SHORT).show()
        }

        // Загрузка данных пользователя
        viewModel.loadUser(1)
    }
}
```

### Компоненты Android Jetpack
MVVM в Android обычно реализуется с использованием:
- **ViewModel**: Хранит и управляет данными, связанными с UI, с учетом жизненного цикла
- **LiveData**: Класс-держатель наблюдаемых данных, который учитывает жизненный цикл
- **Data Binding**: Позволяет декларативно связывать UI-компоненты с источниками данных
- **Repository Pattern**: Посредник между различными источниками данных

### Примеры Использования в Android
- Современные Android-приложения, следующие рекомендуемой Google архитектуре
- Приложения, использующие компоненты Jetpack (ViewModel, LiveData, Room)
- Проекты, требующие реактивных обновлений UI
- Приложения со сложным управлением состоянием
- Приложения, которые должны пережить изменения конфигурации

---

## References
- [Model–view–viewmodel - Wikipedia](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)
- [MVVM Architecture Pattern in Android - GeeksforGeeks](https://www.geeksforgeeks.org/mvvm-model-view-viewmodel-architecture-pattern-in-android/)
- [Introduction to MVVM](https://www.geeksforgeeks.org/introduction-to-model-view-view-model-mvvm/)
- [Comparing MVC MVP and MVVM Design Patterns](https://www.developer.com/design/mvc-vs-mvp-vs-mvvm-design-patterns/)
- [Android Architecture Patterns Part 3: MVVM - Medium](https://medium.com/upday-devs/android-architecture-patterns-part-3-model-view-viewmodel-e7eeee76b73b)
- [MVVM Architecture - Android Tutorial - MindOrks](https://blog.mindorks.com/mvvm-architecture-android-tutorial-for-beginners-step-by-step-guide)
- [Guide to app architecture - Android Developers](https://developer.android.com/jetpack/guide)
- [Pokedex - Sample MVVM App](https://github.com/skydoves/Pokedex)
- [Foodium - Sample MVVM App](https://github.com/PatilShreyas/Foodium)
- [MVVM-Kotlin-Android-Architecture](https://github.com/ahmedeltaher/MVVM-Kotlin-Android-Architecture)
- [MVVM and DataBinding: Android Design Patterns](https://www.raywenderlich.com/636803-mvvm-and-databinding-android-design-patterns)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository
