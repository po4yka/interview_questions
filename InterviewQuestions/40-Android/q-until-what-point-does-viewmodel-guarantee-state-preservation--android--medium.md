---
topic: android
tags:
  - android
difficulty: medium
---

# Until what point does ViewModel guarantee state preservation

## Answer

ViewModel guarantees state preservation until the Activity finishes completely or the process is killed. It survives configuration changes like screen rotation but does not survive process termination.

### ViewModel Lifetime Guarantees

#### ✅ Survives (Data Preserved)

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

#### ❌ Does Not Survive (Data Lost)

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
| ViewModel survives app restart | ❌ Lost on process death |
| ViewModel survives back press | ❌ Cleared when Activity finishes |
| ViewModel is singleton | ❌ Scoped to Activity/Fragment |
| ViewModel thread-safe by default | ❌ Must implement thread safety |

## Answer (RU)
ViewModel сохраняет данные до тех пор, пока связанная Activity или Fragment не будут уничтожены навсегда Например данные сохраняются при изменении конфигурации например поворот экрана но удаляются если приложение закрывается или выгружается из памяти

## Related Topics
- ViewModel lifecycle
- SavedStateHandle
- Configuration changes
- Process death
- onSaveInstanceState
