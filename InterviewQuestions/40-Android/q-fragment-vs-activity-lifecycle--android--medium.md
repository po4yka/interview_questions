---
id: 20251017-144927
title: "Fragment Vs Activity Lifecycle"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-to-write-recyclerview-cache-ahead--android--medium, q-is-layoutinflater-a-singleton-and-why--programming-languages--medium, q-privacy-sandbox-fledge--privacy--hard]
created: 2025-10-15
tags: [difficulty/medium, fragments, lifecycle]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:47:11 pm
---

# Чем Жизненный Цикл Фрагмента Отличается От Activity

**English**: How does Fragment lifecycle differ from Activity lifecycle?

## Answer (EN)
Жизненный цикл фрагмента похож на жизненный цикл активити, но имеет дополнительные состояния и события, отражающие его уникальную способность быть добавленным, удалённым, заменённым или восстановленным в рамках активити.

### Key Differences

#### 1. Nesting within Activity

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

#### 2. View Management

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

#### 3. More Granular State Management

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

#### 4. Interaction with Other Fragments

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

#### 5. Reusability and Multiple Embedding

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

#### 6. Back Stack Management

Фрагменты поддерживают back stack, позволяя пользователю вернуться к предыдущему состоянию.

```kotlin
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack("detail")  // Добавить в back stack
    .commit()

// Пользователь нажимает "Назад" - вернётся к предыдущему фрагменту
```

### Comparison Table

| Аспект | Activity | Fragment |
|--------|----------|----------|
| **Зависимость** | Независима | Зависит от Activity |
| **Количество состояний** | 7 основных | 11 (включая onAttach, onCreateView и т.д.) |
| **View lifecycle** | Привязан к активити | Отдельный от фрагмента |
| **Переиспользование** | Сложно | Легко |
| **Back stack** | Системный | Управляемый программно |
| **Вложенность** | Нет | Может содержать child fragments |

**English**: Fragment lifecycle is more granular than Activity, with additional states like onAttach/onDetach for Activity binding and onCreateView/onDestroyView for view management. Fragments can be reused across activities, support programmatic back stack, and have separate view lifecycle allowing view destruction without fragment destruction.

---

## Related Questions

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, Activity
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Lifecycle, Activity
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Activity, Fragment
