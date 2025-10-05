---
tags:
  - android
  - fragments
  - ui-architecture
difficulty: medium
---

# Для чего нужны фрагменты если есть Activity?

**English**: Why use Fragments if we have Activities?

## Answer

Фрагменты (Fragments) представляют собой модульные части пользовательского интерфейса в Activity, которые имеют собственный жизненный цикл, получают собственные входящие события и могут быть добавлены или удалены при выполнении активности.

### Основные преимущества фрагментов

#### 1. Модульность

Фрагменты позволяют разбить сложный пользовательский интерфейс на управляемые части, что облегчает разработку и поддержку.

```kotlin
class UserListFragment : Fragment() {
    // Отображение списка пользователей
}

class UserDetailFragment : Fragment() {
    // Отображение деталей пользователя
}
```

Каждый фрагмент может быть разработан и оттестирован независимо от других.

#### 2. Переиспользование компонентов

Фрагменты можно использовать в нескольких активностях, что способствует повторному использованию кода.

```kotlin
// Один и тот же фрагмент в разных Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, UserFormFragment())
            .commit()
    }
}

class SettingsActivity : AppCompatActivity() {
    // Тот же фрагмент для редактирования профиля
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, UserFormFragment())
            .commit()
    }
}
```

#### 3. Адаптивный интерфейс

Упрощает создание адаптивных интерфейсов, которые корректно работают на устройствах с различными размерами экранов и ориентациями.

```kotlin
// На планшете - два фрагмента рядом
class TabletActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tablet)  // Два контейнера

        supportFragmentManager.beginTransaction()
            .replace(R.id.list_container, UserListFragment())
            .replace(R.id.detail_container, UserDetailFragment())
            .commit()
    }
}

// На смартфоне - один фрагмент
class PhoneActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_phone)  // Один контейнер

        supportFragmentManager.beginTransaction()
            .replace(R.id.container, UserListFragment())
            .commit()
    }
}
```

#### 4. Управление жизненным циклом

Фрагменты имеют собственный жизненный цикл, но при этом тесно связаны с жизненным циклом хост-Activity.

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Фрагмент привязан к Activity
    }

    override fun onCreateView(inflater: LayoutInflater, ...): View {
        // Создание UI фрагмента
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // UI уничтожен, но фрагмент может быть восстановлен
    }

    override fun onDetach() {
        super.onDetach()
        // Фрагмент отсоединён от Activity
    }
}
```

#### 5. Упрощение обработки взаимодействий

Фрагменты могут взаимодействовать друг с другом через Activity.

```kotlin
// Фрагмент списка
class UserListFragment : Fragment() {
    private var listener: OnUserSelectedListener? = null

    interface OnUserSelectedListener {
        fun onUserSelected(userId: Int)
    }

    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? OnUserSelectedListener
    }

    private fun selectUser(userId: Int) {
        listener?.onUserSelected(userId)
    }
}

// Activity координирует взаимодействие
class MainActivity : AppCompatActivity(), UserListFragment.OnUserSelectedListener {
    override fun onUserSelected(userId: Int) {
        val detailFragment = UserDetailFragment.newInstance(userId)
        supportFragmentManager.beginTransaction()
            .replace(R.id.detail_container, detailFragment)
            .commit()
    }
}
```

#### 6. Поддержка динамических и гибких интерфейсов

Фрагменты можно добавлять, удалять, заменять во время выполнения активности.

```kotlin
// Динамическая замена фрагментов
supportFragmentManager.beginTransaction()
    .replace(R.id.container, NewFragment())
    .addToBackStack(null)  // Добавить в back stack
    .commit()

// Пользователь может вернуться назад кнопкой "Назад"
```

#### 7. Navigation Component

Современная навигация в Android основана на фрагментах.

```kotlin
// Navigation Graph
<navigation ...>
    <fragment
        android:id="@+id/userListFragment"
        android:name="com.example.UserListFragment">
        <action
            android:id="@+id/action_to_detail"
            app:destination="@id/userDetailFragment" />
    </fragment>

    <fragment
        android:id="@+id/userDetailFragment"
        android:name="com.example.UserDetailFragment" />
</navigation>

// Навигация
findNavController().navigate(R.id.action_to_detail)
```

**English**: Fragments provide modularity (break complex UI into manageable parts), reusability (use in multiple activities), adaptive interfaces (support different screen sizes), independent lifecycle management, simplified inter-component communication, and dynamic UI capabilities. Modern Android navigation is built on fragments.
