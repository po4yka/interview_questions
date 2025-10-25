---
id: 20251020-200000
title: Dagger Scope Explained / Объяснение скоупов Dagger
aliases:
- Dagger Scope Explained
- Объяснение скоупов Dagger
topic: android
subtopics:
- di-hilt
- lifecycle
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-dagger-custom-scopes--android--hard
- q-dagger-framework-overview--android--hard
- q-dagger-main-elements--android--medium
created: 2025-10-20
updated: 2025-10-20
tags:
- android/di-hilt
- android/lifecycle
- dagger
- hilt
- scope
- lifecycle
- difficulty/medium
source: https://dagger.dev/api/latest/dagger/Scope.html
source_note: Dagger Scope API documentation
---

# Вопрос (RU)
> Что такое scope в Dagger и как они работают?

# Question (EN)
> What is scope in Dagger and how do they work?

## Ответ (RU)

**Scopes** в Dagger контролируют **время жизни** зависимостей. Они обеспечивают повторное использование объектов в рамках определенного жизненного цикла, предотвращая ненужное создание объектов.

### Теория: Принципы работы Scopes

**Основные концепции:**
- **Время жизни объекта** - как долго существует экземпляр зависимости
- **Повторное использование** - один экземпляр в рамках скоупа
- **Привязка к компонентам** - скоупы связаны с Dagger компонентами
- **Управление памятью** - предотвращение утечек и оптимизация производительности

**Принципы работы:**
- Объекты живут столько, сколько живет их компонент
- Один экземпляр на скоуп
- Автоматическое управление жизненным циклом
- Проверка на этапе компиляции

### 1. @Singleton - Глобальный скоуп

**@Singleton** живет в течение всего жизненного цикла приложения:

```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService
)

@Singleton
class ApiService @Inject constructor(
    private val retrofit: Retrofit
)
```

**Использование:**
```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    @Inject
    lateinit var repository: UserRepository // Один экземпляр на все приложение
}
```

### 2. @ActivityScoped - Скоуп Activity

**@ActivityScoped** живет в течение жизненного цикла Activity:

```kotlin
@ActivityScoped
class UserViewModel @Inject constructor(
    private val repository: UserRepository
)

@ActivityScoped
class UserAdapter @Inject constructor()
```

**Использование:**
```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var viewModel: UserViewModel // Один экземпляр на Activity
}
```

### 3. @FragmentScoped - Скоуп Fragment

**@FragmentScoped** живет в течение жизненного цикла Fragment:

```kotlin
@FragmentScoped
class UserListFragment @Inject constructor()

@FragmentScoped
class UserListAdapter @Inject constructor()
```

**Использование:**
```kotlin
@AndroidEntryPoint
class UserListFragment : Fragment() {
    @Inject
    lateinit var adapter: UserListAdapter // Один экземпляр на Fragment
}
```

### 4. @ViewModelScoped - Скоуп ViewModel

**@ViewModelScoped** живет в течение жизненного цикла ViewModel:

```kotlin
@ViewModelScoped
class UserRepository @Inject constructor(
    private val apiService: ApiService
)

@ViewModelScoped
class UserCache @Inject constructor()
```

**Использование:**
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

### 5. @ServiceScoped - Скоуп Service

**@ServiceScoped** живет в течение жизненного цикла Service:

```kotlin
@ServiceScoped
class LocationService @Inject constructor()

@ServiceScoped
class NotificationManager @Inject constructor()
```

**Использование:**
```kotlin
@AndroidEntryPoint
class MyService : Service() {
    @Inject
    lateinit var locationService: LocationService // Один экземпляр на Service
}
```

### Сравнение скоупов

**Иерархия скоупов:**
- `@Singleton` - самый долгий, живет с приложением
- `@ActivityScoped` - живет с Activity
- `@FragmentScoped` - живет с Fragment
- `@ViewModelScoped` - живет с ViewModel
- `@ServiceScoped` - живет с Service

**Правила наследования:**
- Дочерние скоупы могут использовать объекты из родительских скоупов
- Родительские скоупы не могут использовать объекты из дочерних скоупов
- Объекты создаются в самом узком скоупе, где они нужны

### Практические примеры

**Правильное использование скоупов:**
```kotlin
// Глобальные объекты
@Singleton
class Database @Inject constructor()

@Singleton
class ApiService @Inject constructor()

// Объекты уровня Activity
@ActivityScoped
class UserViewModel @Inject constructor(
    private val repository: UserRepository
)

// Объекты уровня Fragment
@FragmentScoped
class UserAdapter @Inject constructor()
```

**Неправильное использование:**
```kotlin
// Плохо: создание тяжелых объектов в узком скоупе
@FragmentScoped
class Database @Inject constructor() // Должен быть @Singleton

// Плохо: создание легких объектов в широком скоупе
@Singleton
class UserAdapter @Inject constructor() // Должен быть @FragmentScoped
```

## Answer (EN)

**Scopes** in Dagger control the **lifetime** of dependencies. They ensure object reuse within a specific lifecycle, preventing unnecessary object creation.

### Theory: Scope Working Principles

**Core Concepts:**
- **Object lifetime** - how long a dependency instance exists
- **Reuse** - one instance within scope
- **Component binding** - scopes are bound to Dagger components
- **Memory management** - prevent leaks and optimize performance

**Working Principles:**
- Objects live as long as their component lives
- One instance per scope
- Automatic lifecycle management
- Compile-time validation

### 1. @Singleton - Global Scope

**@Singleton** lives for the entire application lifecycle:

```kotlin
@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService
)

@Singleton
class ApiService @Inject constructor(
    private val retrofit: Retrofit
)
```

**Usage:**
```kotlin
@HiltAndroidApp
class MyApplication : Application() {
    @Inject
    lateinit var repository: UserRepository // One instance for entire app
}
```

### 2. @ActivityScoped - Activity Scope

**@ActivityScoped** lives for the Activity lifecycle:

```kotlin
@ActivityScoped
class UserViewModel @Inject constructor(
    private val repository: UserRepository
)

@ActivityScoped
class UserAdapter @Inject constructor()
```

**Usage:**
```kotlin
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject
    lateinit var viewModel: UserViewModel // One instance per Activity
}
```

### 3. @FragmentScoped - Fragment Scope

**@FragmentScoped** lives for the Fragment lifecycle:

```kotlin
@FragmentScoped
class UserListFragment @Inject constructor()

@FragmentScoped
class UserListAdapter @Inject constructor()
```

**Usage:**
```kotlin
@AndroidEntryPoint
class UserListFragment : Fragment() {
    @Inject
    lateinit var adapter: UserListAdapter // One instance per Fragment
}
```

### 4. @ViewModelScoped - ViewModel Scope

**@ViewModelScoped** lives for the ViewModel lifecycle:

```kotlin
@ViewModelScoped
class UserRepository @Inject constructor(
    private val apiService: ApiService
)

@ViewModelScoped
class UserCache @Inject constructor()
```

**Usage:**
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

### 5. @ServiceScoped - Service Scope

**@ServiceScoped** lives for the Service lifecycle:

```kotlin
@ServiceScoped
class LocationService @Inject constructor()

@ServiceScoped
class NotificationManager @Inject constructor()
```

**Usage:**
```kotlin
@AndroidEntryPoint
class MyService : Service() {
    @Inject
    lateinit var locationService: LocationService // One instance per Service
}
```

### Scope Comparison

**Scope hierarchy:**
- `@Singleton` - longest lived, lives with application
- `@ActivityScoped` - lives with Activity
- `@FragmentScoped` - lives with Fragment
- `@ViewModelScoped` - lives with ViewModel
- `@ServiceScoped` - lives with Service

**Inheritance rules:**
- Child scopes can use objects from parent scopes
- Parent scopes cannot use objects from child scopes
- Objects are created in the narrowest scope where they're needed

### Practical Examples

**Correct scope usage:**
```kotlin
// Global objects
@Singleton
class Database @Inject constructor()

@Singleton
class ApiService @Inject constructor()

// Activity-level objects
@ActivityScoped
class UserViewModel @Inject constructor(
    private val repository: UserRepository
)

// Fragment-level objects
@FragmentScoped
class UserAdapter @Inject constructor()
```

**Incorrect usage:**
```kotlin
// Bad: creating heavy objects in narrow scope
@FragmentScoped
class Database @Inject constructor() // Should be @Singleton

// Bad: creating light objects in wide scope
@Singleton
class UserAdapter @Inject constructor() // Should be @FragmentScoped
```

**See also:** [[c-dependency-injection]], c-singleton-pattern

## Follow-ups

- How do you create custom scopes in Dagger?
- What happens when you use the wrong scope?
- How do scopes affect memory usage?

## Related Questions

### Prerequisites (Easier)
- [[q-dagger-inject-annotation--android--easy]]

### Related (Same Level)
- [[q-dagger-main-elements--android--medium]]

### Advanced (Harder)
- [[q-dagger-custom-scopes--android--hard]]
- [[q-dagger-framework-overview--android--hard]]
