---
id: 20251012-1227111166
title: MVP Pattern (Model-View-Presenter)
topic: architecture-patterns
difficulty: medium
status: draft
created: 2025-10-15
tags: []
related:   - mvvm-pattern
  - mvi-pattern
  - clean-architecture
subtopics:   - android-architecture
  - separation-of-concerns
  - testability
---
# MVP Pattern / Паттерн MVP (Model-View-Presenter)

# Question (EN)
> What is the MVP pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн MVP? Когда и зачем его следует использовать?

---

## Answer (EN)


### Definition
MVP is an architectural pattern engineered to facilitate automated unit testing and improve the separation of concerns in presentation logic.

### Components
Role of components:
- **Model** - the data layer. Responsible for handling the business logic and communication with the network and database layers
- **View** - the UI layer. Displays the data and notifies the Presenter about user actions
- **Presenter** - retrieves the data from the Model, applies the UI logic and manages the state of the View, decides what to display and reacts to user input notifications from the View

Since the View and the Presenter work closely together, they need to have a reference to one another. To make the Presenter unit testable with JUnit, the View is abstracted and an interface for it is used. The relationship between the Presenter and its corresponding View is defined in a `Contract` interface class, making the code more readable and the connection between the two easier to understand.

### Why Use MVP?
This MVP design pattern helps to segregate code into three different parts: business logic (Presenter); UI (View); data interaction (Model). This modulation of code is easy to understand and maintain.

For example: In our application, if we use a content provider to persist our data and later we want to upgrade it with a SQLite database, the MVP design pattern will make this very easy.

### Advantages
Advantages of MVP Architecture:
- No conceptual relationship in android components
- Easy code maintenance and testing as the application's model, view, and presenter layers are separated

### Disadvantages
Disadvantages of MVP Architecture:
- If the developer does not follow the single responsibility principle to break the code then the Presenter layer tends to expand to a huge all-knowing class
- The Model-View-Presenter pattern brings with it a very good separation of concerns. While this is for sure a pro, when developing a small app or a prototype, this can seem like an overhead
- To decrease the number of interfaces used, some developers remove the `Contract` interface class, and the interface for the Presenter
- One of the pitfalls of MVP appears when moving the UI logic to the Presenter: this becomes now an all-knowing class, with thousands of lines of code. To solve this, split the code even more and remember to create classes that have only one responsibility and are unit testable

### Key Principles
1. **Separation of Concerns**: Clear separation between UI, business logic, and data
2. **Testability**: Presenter can be tested independently from Android framework
3. **Contract Interface**: Defines the connection between View and Presenter
4. **Passive View**: View is passive and doesn't contain business logic

### Example Structure

```kotlin
// Contract interface defining View and Presenter
interface LoginContract {
    interface View {
        fun showProgress()
        fun hideProgress()
        fun showLoginSuccess(user: User)
        fun showLoginError(message: String)
    }

    interface Presenter {
        fun onLoginClicked(email: String, password: String)
        fun onDestroy()
    }
}

// Model
class LoginModel {
    fun login(email: String, password: String): User? {
        // Business logic for login
        // Network/Database calls
        return null
    }
}

// Presenter implementation
class LoginPresenter(private val view: LoginContract.View) : LoginContract.Presenter {
    private val model = LoginModel()

    override fun onLoginClicked(email: String, password: String) {
        view.showProgress()

        // Validate input
        if (email.isEmpty() || password.isEmpty()) {
            view.hideProgress()
            view.showLoginError("Email and password cannot be empty")
            return
        }

        // Call model
        val user = model.login(email, password)
        view.hideProgress()

        if (user != null) {
            view.showLoginSuccess(user)
        } else {
            view.showLoginError("Invalid credentials")
        }
    }

    override fun onDestroy() {
        // Clean up resources
    }
}

// View implementation (Activity/Fragment)
class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        presenter = LoginPresenter(this)

        loginButton.setOnClickListener {
            presenter.onLoginClicked(emailEditText.text.toString(), passwordEditText.text.toString())
        }
    }

    override fun showProgress() {
        progressBar.visibility = View.VISIBLE
    }

    override fun hideProgress() {
        progressBar.visibility = View.GONE
    }

    override fun showLoginSuccess(user: User) {
        Toast.makeText(this, "Welcome ${user.name}", Toast.LENGTH_SHORT).show()
        // Navigate to main screen
    }

    override fun showLoginError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}

data class User(val name: String, val email: String)
```

### Use Cases in Android
- Applications requiring high testability
- Projects with complex business logic
- Teams following clean architecture principles
- Applications where UI logic needs to be separated from Android framework

---



## Ответ (RU)

### Определение
MVP - это архитектурный паттерн, разработанный для упрощения автоматизированного unit-тестирования и улучшения разделения ответственности в логике представления.

### Компоненты
Роль компонентов:
- **Model (Модель)** - слой данных. Отвечает за обработку бизнес-логики и коммуникацию со слоями сети и базы данных
- **View (Представление)** - слой UI. Отображает данные и уведомляет Presenter о действиях пользователя
- **Presenter (Представитель)** - извлекает данные из Model, применяет логику UI и управляет состоянием View, решает что отображать и реагирует на уведомления о пользовательском вводе от View

Поскольку View и Presenter работают в тесном контакте, им нужна ссылка друг на друга. Чтобы сделать Presenter unit-тестируемым с JUnit, View абстрагируется и используется интерфейс для него. Отношение между Presenter и его соответствующим View определяется в интерфейсном классе `Contract`, что делает код более читаемым, а связь между ними легче для понимания.

### Зачем Использовать MVP?
Этот паттерн проектирования MVP помогает разделить код на три различные части: бизнес-логика (Presenter); UI (View); взаимодействие с данными (Model). Такая модуляция кода легка для понимания и поддержки.

Например: В нашем приложении, если мы используем content provider для сохранения наших данных, а позже хотим обновить его до SQLite базы данных, паттерн проектирования MVP сделает это очень легко.

### Преимущества
Преимущества архитектуры MVP:
- Нет концептуальной связи в android-компонентах
- Легкая поддержка и тестирование кода, поскольку слои модели, представления и presenter приложения разделены

### Недостатки
Недостатки архитектуры MVP:
- Если разработчик не следует принципу единственной ответственности для разбиения кода, то слой Presenter имеет тенденцию расширяться до огромного всезнающего класса
- Паттерн Model-View-Presenter приносит очень хорошее разделение ответственности. Хотя это определенно плюс, при разработке небольшого приложения или прототипа это может показаться излишним
- Чтобы уменьшить количество используемых интерфейсов, некоторые разработчики удаляют интерфейсный класс `Contract` и интерфейс для Presenter
- Одна из ловушек MVP появляется при перемещении логики UI в Presenter: это становится теперь всезнающим классом с тысячами строк кода. Чтобы решить это, разбейте код еще больше и помните о создании классов, которые имеют только одну ответственность и являются unit-тестируемыми

### Ключевые Принципы
1. **Разделение ответственности**: Четкое разделение между UI, бизнес-логикой и данными
2. **Тестируемость**: Presenter может быть протестирован независимо от Android фреймворка
3. **Contract-интерфейс**: Определяет связь между View и Presenter
4. **Пассивное представление**: View пассивно и не содержит бизнес-логику

### Пример Структуры

```kotlin
// Contract-интерфейс, определяющий View и Presenter
interface LoginContract {
    interface View {
        fun showProgress()
        fun hideProgress()
        fun showLoginSuccess(user: User)
        fun showLoginError(message: String)
    }

    interface Presenter {
        fun onLoginClicked(email: String, password: String)
        fun onDestroy()
    }
}

// Model
class LoginModel {
    fun login(email: String, password: String): User? {
        // Бизнес-логика для логина
        // Сетевые/БД вызовы
        return null
    }
}

// Реализация Presenter
class LoginPresenter(private val view: LoginContract.View) : LoginContract.Presenter {
    private val model = LoginModel()

    override fun onLoginClicked(email: String, password: String) {
        view.showProgress()

        // Валидация ввода
        if (email.isEmpty() || password.isEmpty()) {
            view.hideProgress()
            view.showLoginError("Email и пароль не могут быть пустыми")
            return
        }

        // Вызов модели
        val user = model.login(email, password)
        view.hideProgress()

        if (user != null) {
            view.showLoginSuccess(user)
        } else {
            view.showLoginError("Неверные учетные данные")
        }
    }

    override fun onDestroy() {
        // Очистка ресурсов
    }
}

// Реализация View (Activity/Fragment)
class LoginActivity : AppCompatActivity(), LoginContract.View {
    private lateinit var presenter: LoginContract.Presenter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        presenter = LoginPresenter(this)

        loginButton.setOnClickListener {
            presenter.onLoginClicked(emailEditText.text.toString(), passwordEditText.text.toString())
        }
    }

    override fun showProgress() {
        progressBar.visibility = View.VISIBLE
    }

    override fun hideProgress() {
        progressBar.visibility = View.GONE
    }

    override fun showLoginSuccess(user: User) {
        Toast.makeText(this, "Добро пожаловать ${user.name}", Toast.LENGTH_SHORT).show()
        // Переход на главный экран
    }

    override fun showLoginError(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroy() {
        presenter.onDestroy()
        super.onDestroy()
    }
}

data class User(val name: String, val email: String)
```

### Примеры Использования в Android
- Приложения, требующие высокой тестируемости
- Проекты со сложной бизнес-логикой
- Команды, следующие принципам чистой архитектуры
- Приложения, где логика UI должна быть отделена от Android фреймворка

---

## References
- [Model–view–presenter - Wikipedia](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93presenter)
- [Android Architecture Patterns Part 2: Model-View-Presenter - Medium](https://medium.com/upday-devs/android-architecture-patterns-part-2-model-view-presenter-8a6faaae14a5)
- [MVP Architecture Pattern in Android - GeeksforGeeks](https://www.geeksforgeeks.org/mvp-model-view-presenter-architecture-pattern-in-android-with-example/)
- [Model-View-Presenter for Android - DZone](https://dzone.com/articles/model-view-presenter-for-andriod)
- [Building An Application With MVP - Android Essence](https://androidessence.com/building-an-app-with-mvp)
- [Android MVP Architecture for Beginners](https://androidwave.com/android-mvp-architecture-for-beginners-demo-app/)
- [Android MVP - JournalDev](https://www.journaldev.com/14886/android-mvp)
- [Android Model View Presenter MVP Pattern Example](https://www.zoftino.com/android-model-view-presenter-mvp-pattern-example)

---

**Source:** Kirchhoff-Android-Interview-Questions
**Attribution:** Content adapted from the Kirchhoff repository


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Architecture Patterns
- [[q-mvvm-pattern--architecture-patterns--medium]] - MVVM pattern
- [[q-mvi-pattern--architecture-patterns--hard]] - MVI pattern

