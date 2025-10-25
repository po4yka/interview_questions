---
id: 20251016-164357
title: "Until What Point Does Viewmodel Guarantee State Preservation / До какого момента ViewModel гарантирует сохранение состояния"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-flow-testing-turbine--testing--medium, q-sparsearray-optimization--android--medium, q-hilt-components-scope--android--medium]
created: 2025-10-15
tags:
  - android
---

# Until what point does ViewModel guarantee state preservation

## Answer (EN)
ViewModel guarantees state preservation until the Activity finishes completely or the process is killed. It survives configuration changes like screen rotation but does not survive process termination.

### ViewModel Lifetime Guarantees

#### - Survives (Data Preserved)

1. **Configuration Changes**:
   ```kotlin
   class MyActivity : AppCompatActivity() {
       private val viewModel: MyViewModel by viewModels()

       override fun onCreate(savedInstanceState: Bundle?) {
           super.onCreate(savedInstanceState)
           // viewModel persists through:
           // - Screen rotation
           // - Language change
           // - Dark mode toggle
           // - Font size change
       }
   }
   ```

2. **Fragment Transactions**:
   - Fragment replacement in same Activity
   - Fragment added to back stack
   - Fragment recreation during parent Activity configuration change

3. **Activity in Background** (onStop):
   - Activity moved to background but process alive
   - Another Activity started on top

#### - Does Not Survive (Data Lost)

1. **Activity.finish() Called**:
   ```kotlin
   class MyActivity : AppCompatActivity() {
       private val viewModel: MyViewModel by viewModels()

       fun closeActivity() {
           finish() // ViewModel.onCleared() will be called
       }
   }
   ```

2. **Process Death**:
   - System kills app process due to memory pressure
   - User force-stops app from settings
   - System runs out of memory
   - App crashes

3. **Back Navigation**:
   - User presses back button on root Activity
   - `finish()` is called internally

### ViewModel Lifecycle Visualization

```
Activity Created → ViewModel Created
       ↓
Configuration Change → ViewModel RETAINED
       ↓
Activity Recreated → Same ViewModel Instance
       ↓
Activity.finish() → ViewModel.onCleared()
       ↓
ViewModel Destroyed
```

### Handling Process Death

To survive process death, combine ViewModel with SavedStateHandle:

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Automatically saved and restored across process death
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // Regular property - lost on process death
    var temporaryData: String = ""

    // LiveData with saved state
    val userNameLiveData: MutableLiveData<String> =
        savedStateHandle.getLiveData("user_name_live", "")
}
```

### Fragment-Scoped ViewModel

Fragment ViewModel lifetime:

```kotlin
class MyFragment : Fragment() {
    // Scoped to Fragment lifecycle
    private val fragmentViewModel: MyViewModel by viewModels()

    // Scoped to parent Activity - survives Fragment recreation
    private val activityViewModel: SharedViewModel by activityViewModels()

    override fun onDestroyView() {
        super.onDestroyView()
        // fragmentViewModel still alive if Fragment in back stack
    }
}
```

**Fragment ViewModel cleared when**:
- Fragment permanently removed (not in back stack)
- Parent Activity finishes
- `clearFragmentResult()` with `FragmentManager.popBackStack()`

### Best Practices

1. **Critical Data**: Use SavedStateHandle for data that must survive process death
2. **Large Data**: Store in Repository/Database, reference in ViewModel
3. **Temporary UI State**: Use regular ViewModel properties
4. **Monitor Lifecycle**: Implement `onCleared()` for cleanup

```kotlin
class MyViewModel : ViewModel() {
    private val disposables = CompositeDisposable()

    override fun onCleared() {
        super.onCleared()
        disposables.clear()
        // Clean up resources
    }
}
```

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| ViewModel survives app restart | - Lost on process death |
| ViewModel survives back press | - Cleared when Activity finishes |
| ViewModel is singleton | - Scoped to Activity/Fragment |
| ViewModel thread-safe by default | - Must implement thread safety |

## Ответ (RU)

ViewModel гарантирует сохранение состояния до тех пор, пока Activity не завершится полностью или процесс не будет убит. Она переживает изменения конфигурации такие как поворот экрана, но не переживает уничтожение процесса.

### Гарантии времени жизни ViewModel

#### Переживает (Данные сохраняются)

1. **Изменения конфигурации**:
   ```kotlin
   class MyActivity : AppCompatActivity() {
       private val viewModel: MyViewModel by viewModels()

       override fun onCreate(savedInstanceState: Bundle?) {
           super.onCreate(savedInstanceState)
           // viewModel переживает:
           // - Поворот экрана
           // - Смену языка
           // - Переключение темной темы
           // - Изменение размера шрифта
       }
   }
   ```

2. **Транзакции Fragment**:
   - Замена Fragment в той же Activity
   - Fragment добавлен в back stack
   - Пересоздание Fragment при изменении конфигурации родительской Activity

3. **Activity в фоне** (onStop):
   - Activity перемещена в фон но процесс жив
   - Другая Activity запущена поверх

#### Не переживает (Данные теряются)

1. **Activity.finish() вызван**:
   ```kotlin
   class MyActivity : AppCompatActivity() {
       private val viewModel: MyViewModel by viewModels()

       fun closeActivity() {
           finish() // ViewModel.onCleared() будет вызван
       }
   }
   ```

2. **Смерть процесса**:
   - Система убивает процесс приложения из-за нехватки памяти
   - Пользователь принудительно останавливает приложение из настроек
   - Системе не хватает памяти
   - Приложение падает

3. **Навигация назад**:
   - Пользователь нажимает кнопку назад на корневой Activity
   - `finish()` вызывается внутренне

### Визуализация жизненного цикла ViewModel

```
Activity создан → ViewModel создан
       ↓
Изменение конфигурации → ViewModel СОХРАНЕН
       ↓
Activity пересоздан → Тот же экземпляр ViewModel
       ↓
Activity.finish() → ViewModel.onCleared()
       ↓
ViewModel уничтожен
```

### Обработка смерти процесса

Чтобы пережить смерть процесса, комбинируйте ViewModel с SavedStateHandle:

```kotlin
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Автоматически сохраняется и восстанавливается при смерти процесса
    var userName: String
        get() = savedStateHandle["user_name"] ?: ""
        set(value) { savedStateHandle["user_name"] = value }

    // Обычное свойство - теряется при смерти процесса
    var temporaryData: String = ""

    // LiveData с сохраненным состоянием
    val userNameLiveData: MutableLiveData<String> =
        savedStateHandle.getLiveData("user_name_live", "")
}
```

### Fragment-Scoped ViewModel

Время жизни Fragment ViewModel:

```kotlin
class MyFragment : Fragment() {
    // Привязан к жизненному циклу Fragment
    private val fragmentViewModel: MyViewModel by viewModels()

    // Привязан к родительской Activity - переживает пересоздание Fragment
    private val activityViewModel: SharedViewModel by activityViewModels()

    override fun onDestroyView() {
        super.onDestroyView()
        // fragmentViewModel все еще жив если Fragment в back stack
    }
}
```

**Fragment ViewModel очищается когда**:
- Fragment окончательно удален (не в back stack)
- Родительская Activity завершается
- `clearFragmentResult()` с `FragmentManager.popBackStack()`

### Лучшие практики

1. **Критичные данные**: Используйте SavedStateHandle для данных, которые должны пережить смерть процесса
2. **Большие данные**: Храните в Repository/Database, ссылайтесь в ViewModel
3. **Временное UI состояние**: Используйте обычные свойства ViewModel
4. **Мониторинг жизненного цикла**: Реализуйте `onCleared()` для очистки

```kotlin
class MyViewModel : ViewModel() {
    private val disposables = CompositeDisposable()

    override fun onCleared() {
        super.onCleared()
        disposables.clear()
        // Очистить ресурсы
    }
}
```

### Частые заблуждения

| Заблуждение | Реальность |
|-------------|-----------|
| ViewModel переживает перезапуск приложения | Теряется при смерти процесса |
| ViewModel переживает нажатие назад | Очищается когда Activity завершается |
| ViewModel это singleton | Привязан к Activity/Fragment |
| ViewModel thread-safe по умолчанию | Должна быть реализована thread safety |

**Резюме**: ViewModel гарантирует сохранение состояния пока связанная Activity или Fragment не будут окончательно уничтожены. Данные сохраняются при изменениях конфигурации (например поворот экрана), но удаляются если:
1. Activity завершается (finish() или back navigation)
2. Приложение закрывается или процесс убивается системой
3. Пользователь принудительно останавливает приложение

Для сохранения данных через смерть процесса используйте **SavedStateHandle** в комбинации с ViewModel. Для больших данных храните их в Repository/Database и только ссылайтесь из ViewModel.

## Related Topics
- ViewModel lifecycle
- SavedStateHandle
- Configuration changes
- Process death
- onSaveInstanceState


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-what-is-viewmodel--android--medium]] - What is ViewModel
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose & internals
- [[q-viewmodel-vs-onsavedinstancestate--android--medium]] - ViewModel vs onSavedInstanceState

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture

