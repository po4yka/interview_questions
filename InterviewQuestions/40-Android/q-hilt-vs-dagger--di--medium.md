---
id: android-747
title: Hilt vs Dagger Simplifications / Упрощения Hilt по сравнению с Dagger
aliases:
- Hilt vs Dagger
- Hilt Simplifications
- Упрощения Hilt
- Hilt против Dagger
topic: android
subtopics:
- di-hilt
- di-dagger
question_kind: comparison
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-dagger
- c-dependency-injection
- c-hilt
- q-what-is-hilt--android--medium
- q-dagger-framework-overview--android--hard
- q-dagger-scope-explained--android--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- android/di-hilt
- android/di-dagger
- dependency-injection
- difficulty/medium
- hilt
- dagger
---
# Вопрос (RU)
> Какие упрощения предоставляет `Hilt` по сравнению с чистым `Dagger`? Когда имеет смысл использовать чистый `Dagger` вместо `Hilt`?

# Question (EN)
> What simplifications does `Hilt` provide over pure `Dagger`? When does it make sense to use pure `Dagger` instead of `Hilt`?

---

## Ответ (RU)

### Упрощения Hilt

`Hilt` построен поверх `Dagger` и убирает большую часть boilerplate-кода, необходимого для настройки DI в Android.

| Аспект | Чистый `Dagger` | `Hilt` |
|--------|-----------------|--------|
| **Компоненты** | Ручное создание и связывание | Предопределённые компоненты |
| **Scopes** | Кастомные аннотации | Стандартные (@Singleton, @ActivityScoped) |
| **Жизненный цикл** | Ручное управление | Автоматическое |
| **ViewModel** | AssistedInject + Factory | @HiltViewModel |
| **Application** | Ручной DaggerAppComponent | @HiltAndroidApp |
| **Тестирование** | Тестовые компоненты вручную | @TestInstallIn, @BindValue |

### Код: Чистый Dagger vs Hilt

**Чистый Dagger (много boilerplate):**

```kotlin
// 1. Создание компонента
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
    fun activityComponentFactory(): ActivityComponent.Factory
}

// 2. Субкомпонент для Activity
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }
    fun inject(activity: MainActivity)
}

// 3. Кастомный scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

// 4. Инициализация в Application
class MyApp : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .appModule(AppModule(this))
            .build()
    }
}

// 5. Инъекция в Activity
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent
            .activityComponentFactory()
            .create(this)
            .inject(this)
        super.onCreate(savedInstanceState)
    }
}
```

**Hilt (минимум boilerplate):**

```kotlin
// 1. Application
@HiltAndroidApp
class MyApp : Application()

// 2. Модуль (аналогичен Dagger)
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(api: ApiService): UserRepository {
        return UserRepositoryImpl(api)
    }
}

// 3. Инъекция в Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
    // Готово! Hilt автоматически создаёт компоненты
}
```

### Когда Использовать Чистый Dagger

| Сценарий | Причина |
|----------|---------|
| **Не-Android проекты** | Hilt работает только на Android |
| **Kotlin Multiplatform** | Dagger поддерживает JVM-таргеты |
| **Кастомные иерархии компонентов** | Hilt ограничивает структуру |
| **Нужен полный контроль над графом** | Hilt скрывает детали реализации |
| **SDK/библиотеки** | Hilt требует @HiltAndroidApp в приложении |
| **Legacy-миграция** | Постепенный переход с существующего Dagger |

### Пример: Кастомная Иерархия (только Dagger)

```kotlin
// Hilt не поддерживает произвольные субкомпоненты
@FeatureScope
@Subcomponent(modules = [FeatureModule::class])
interface FeatureComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance config: FeatureConfig): FeatureComponent
    }
}

// Зависимость одной фичи от другой
@Component(
    dependencies = [CoreComponent::class],
    modules = [FeatureAModule::class]
)
interface FeatureAComponent
```

### Рекомендации (2026)

**Используйте Hilt:**
- Новые Android-приложения
- Команды, незнакомые с Dagger
- Проекты с типовой архитектурой (MVVM, Clean Architecture)
- Интеграция с Jetpack (ViewModel, WorkManager, Navigation)

**Используйте чистый Dagger:**
- Backend/Desktop на Kotlin
- SDK и библиотеки без зависимости от Application
- Сложные multi-feature архитектуры с динамическими модулями
- Когда Hilt ограничивает архитектурные решения

---

## Answer (EN)

### Hilt Simplifications

`Hilt` is built on top of `Dagger` and removes most of the boilerplate code required for DI setup in Android.

| Aspect | Pure `Dagger` | `Hilt` |
|--------|---------------|--------|
| **Components** | Manual creation and wiring | Predefined components |
| **Scopes** | Custom annotations | Standard (@Singleton, @ActivityScoped) |
| **Lifecycle** | Manual management | Automatic |
| **ViewModel** | AssistedInject + Factory | @HiltViewModel |
| **Application** | Manual DaggerAppComponent | @HiltAndroidApp |
| **Testing** | Manual test components | @TestInstallIn, @BindValue |

### Code: Pure Dagger vs Hilt

**Pure Dagger (lots of boilerplate):**

```kotlin
// 1. Create component
@Singleton
@Component(modules = [AppModule::class, NetworkModule::class])
interface AppComponent {
    fun inject(activity: MainActivity)
    fun activityComponentFactory(): ActivityComponent.Factory
}

// 2. Activity subcomponent
@ActivityScope
@Subcomponent(modules = [ActivityModule::class])
interface ActivityComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance activity: Activity): ActivityComponent
    }
    fun inject(activity: MainActivity)
}

// 3. Custom scope
@Scope
@Retention(AnnotationRetention.RUNTIME)
annotation class ActivityScope

// 4. Initialize in Application
class MyApp : Application() {
    lateinit var appComponent: AppComponent

    override fun onCreate() {
        super.onCreate()
        appComponent = DaggerAppComponent.builder()
            .appModule(AppModule(this))
            .build()
    }
}

// 5. Inject in Activity
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        (application as MyApp).appComponent
            .activityComponentFactory()
            .create(this)
            .inject(this)
        super.onCreate(savedInstanceState)
    }
}
```

**Hilt (minimal boilerplate):**

```kotlin
// 1. Application
@HiltAndroidApp
class MyApp : Application()

// 2. Module (similar to Dagger)
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton
    fun provideRepository(api: ApiService): UserRepository {
        return UserRepositoryImpl(api)
    }
}

// 3. Inject in Activity
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    @Inject lateinit var repository: UserRepository
    // Done! Hilt creates components automatically
}
```

### When to Use Pure Dagger

| Scenario | Reason |
|----------|--------|
| **Non-Android projects** | Hilt is Android-only |
| **Kotlin Multiplatform** | Dagger supports JVM targets |
| **Custom component hierarchies** | Hilt restricts structure |
| **Need full graph control** | Hilt hides implementation details |
| **SDK/libraries** | Hilt requires @HiltAndroidApp in the app |
| **Legacy migration** | Gradual transition from existing Dagger |

### Example: Custom Hierarchy (Dagger only)

```kotlin
// Hilt doesn't support arbitrary subcomponents
@FeatureScope
@Subcomponent(modules = [FeatureModule::class])
interface FeatureComponent {
    @Subcomponent.Factory
    interface Factory {
        fun create(@BindsInstance config: FeatureConfig): FeatureComponent
    }
}

// Feature depending on another feature
@Component(
    dependencies = [CoreComponent::class],
    modules = [FeatureAModule::class]
)
interface FeatureAComponent
```

### Recommendations (2026)

**Use Hilt:**
- New Android applications
- Teams unfamiliar with Dagger
- Projects with typical architecture (MVVM, Clean Architecture)
- Integration with Jetpack (ViewModel, WorkManager, Navigation)

**Use pure Dagger:**
- Backend/Desktop Kotlin projects
- SDKs and libraries without Application dependency
- Complex multi-feature architectures with dynamic modules
- When Hilt constrains architectural decisions

---

## Follow-ups

- Как мигрировать с чистого Dagger на Hilt поэтапно?
- Как использовать Hilt Entry Points для интеграции с legacy Dagger-кодом?
- Какие ограничения Hilt накладывает на multi-module проекты?

## References

- [Hilt Documentation](https://dagger.dev/hilt/)
- [Dagger Documentation](https://dagger.dev/)
- [Migration from Dagger to Hilt](https://developer.android.com/training/dependency-injection/hilt-migration)

## Related Questions

### Prerequisites
- [[q-dagger-purpose--android--easy]] - Why use DI
- [[q-dagger-inject-annotation--android--easy]] - Basic Dagger annotations

### Related
- [[q-what-is-hilt--android--medium]] - Hilt overview
- [[q-dagger-scope-explained--android--medium]] - Dagger scopes
- [[q-hilt-components-scope--android--medium]] - Hilt scopes

### Advanced
- [[q-dagger-framework-overview--android--hard]] - Dagger internals
- [[q-dagger-custom-scopes--android--hard]] - Custom scope implementation
