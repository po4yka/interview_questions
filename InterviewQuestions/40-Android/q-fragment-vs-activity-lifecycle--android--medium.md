---
topic: android
tags:
  - android
  - fragments
  - lifecycle
difficulty: medium
---

# Чем жизненный цикл фрагмента отличается от Activity

**English**: How does Fragment lifecycle differ from Activity lifecycle?

## Answer

Жизненный цикл фрагмента похож на жизненный цикл активити, но имеет дополнительные состояния и события, отражающие его уникальную способность быть добавленным, удалённым, заменённым или восстановленным в рамках активити.

### Основные отличия

#### 1. Вложенность в Activity

Фрагменты существуют внутри активити и зависят от её жизненного цикла.

```kotlin
class MyFragment : Fragment() {
    override fun onAttach(context: Context) {
        super.onAttach(context)
        // Фрагмент связывается с Activity
    }

    override fun onDetach() {
        super.onDetach()
        // Фрагмент отсоединяется от Activity
    }
}
```

Фрагменты имеют дополнительные события:
- `onAttach()` - когда фрагмент связывается с активити
- `onDetach()` - когда фрагмент отсоединяется от активити

#### 2. Управление представлением (View)

Фрагменты имеют отдельный жизненный цикл для управления своим представлением.

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Создание представления фрагмента
        return inflater.inflate(R.layout.fragment_my, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // View создан, можно инициализировать UI
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // View удаляется, но фрагмент может быть восстановлен
    }
}
```

**Важно**: Фрагмент может быть удалён из UI и затем вновь добавлен без уничтожения самого фрагмента.

#### 3. Более гранулярное управление состоянием

**Жизненный цикл Activity**:

```
onCreate() → onStart() → onResume() → onPause() → onStop() → onDestroy()
```

**Жизненный цикл Fragment** (расширенный):

```
onAttach() →
onCreate() →
onCreateView() →
onViewCreated() →
onStart() →
onResume() →
onPause() →
onStop() →
onDestroyView() →  ← Дополнительное состояние
onDestroy() →
onDetach()
```

#### 4. Взаимодействие с другими фрагментами

Фрагменты взаимодействуют через родительскую активити или через shared ViewModel.

```kotlin
// Через Activity
class ListFragment : Fragment() {
    interface OnItemSelectedListener {
        fun onItemSelected(id: Int)
    }

    private var listener: OnItemSelectedListener? = null

    override fun onAttach(context: Context) {
        super.onAttach(context)
        listener = context as? OnItemSelectedListener
    }
}

// Через shared ViewModel (современный подход)
class ListFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    private fun selectItem(id: Int) {
        sharedViewModel.selectItem(id)
    }
}

class DetailFragment : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        sharedViewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            // Обновить UI
        }
    }
}
```

#### 5. Множественное использование и повторное встраивание

Фрагменты разработаны для многократного встраивания в различные активити или даже в другие фрагменты.

```kotlin
// Один фрагмент, несколько мест использования
class ProfileFragment : Fragment() {
    companion object {
        fun newInstance(userId: Int): ProfileFragment {
            return ProfileFragment().apply {
                arguments = Bundle().apply {
                    putInt("USER_ID", userId)
                }
            }
        }
    }
}

// Использование в MainActivity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ProfileFragment.newInstance(123))
            .commit()
    }
}

// Использование в SettingsActivity
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, ProfileFragment.newInstance(456))
            .commit()
    }
}
```

#### 6. Back Stack управление

Фрагменты поддерживают back stack, позволяя пользователю вернуться к предыдущему состоянию.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack("detail")  // Добавить в back stack
    .commit()

// Пользователь нажимает "Назад" - вернётся к предыдущему фрагменту
```

### Сравнительная таблица

| Аспект | Activity | Fragment |
|--------|----------|----------|
| **Зависимость** | Независима | Зависит от Activity |
| **Количество состояний** | 7 основных | 11 (включая onAttach, onCreateView и т.д.) |
| **View lifecycle** | Привязан к активити | Отдельный от фрагмента |
| **Переиспользование** | Сложно | Легко |
| **Back stack** | Системный | Управляемый программно |
| **Вложенность** | Нет | Может содержать child fragments |

**English**: Fragment lifecycle is more granular than Activity, with additional states like onAttach/onDetach for Activity binding and onCreateView/onDestroyView for view management. Fragments can be reused across activities, support programmatic back stack, and have separate view lifecycle allowing view destruction without fragment destruction.
