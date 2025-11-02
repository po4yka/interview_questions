---
id: android-357
title: "Dialog vs Fragment / Диалог против Фрагмента"
aliases:
  - Dialog vs Fragment
  - Диалог против Фрагмента
topic: android
subtopics:
  - lifecycle
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-11-02
tags:
  - android/lifecycle
  - android/ui-views
  - dialog
  - difficulty/medium
  - fragment
  - lifecycle
  - ui
sources:
  - https://developer.android.com/develop/ui/views/components/dialogs
  - https://developer.android.com/guide/fragments
---

# Вопрос (RU)
> Какая разница между диалогом и фрагментом?

# Question (EN)
> What is the difference between dialog and fragment?

---

## Ответ (RU)

**Концепция:**

`Dialog` и `Fragment` решают разные задачи в Android UI. `Dialog` — модальное окно для краткосрочных взаимодействий (подтверждения, ввод данных, уведомления об ошибках). `Fragment` — модульная часть UI с полным жизненным циклом для построения экранов и навигации между ними. Понимание различий критично для выбора правильного компонента при проектировании UI.

**Ключевые различия:**

| Аспект | Dialog | Fragment |
|--------|--------|----------|
| **Назначение** | Временные взаимодействия (подтверждения, ошибки, короткий ввод) | Переиспользуемые экраны и модули UI |
| **Lifecycle** | Упрощенный (show/dismiss, нет полного lifecycle) | Полный lifecycle (onCreate → onViewCreated → onDestroy) |
| **Navigation** | Не входит в back stack, закрывается dismiss | Часть Navigation Component, управляется back stack |
| **Сложность** | Простые формы, один экран | Сложные UI с состоянием, может содержать вложенные компоненты |
| **Состояние** | Теряется при rotation без DialogFragment | Сохраняется через `onSaveInstanceState` |
| **Переиспользование** | Ограниченное, обычно создается заново | Высокое, может использоваться на разных экранах |
| **Compose эквивалент** | `AlertDialog`, `Dialog` composable | `Screen` composable, навигация через NavController |

**Dialog (Views):**

Простые диалоги через `AlertDialog.Builder` для быстрых подтверждений и уведомлений:

```kotlin
// ✅ Простые подтверждения без lifecycle
AlertDialog.Builder(context)
    .setTitle("Удалить?")
    .setMessage("Действие нельзя отменить")
    .setPositiveButton("Да") { _, _ -> delete() }
    .setNegativeButton("Нет", null)
    .show()

// ⚠️ Проблема: состояние теряется при rotation
// Решение: использовать DialogFragment
```

**DialogFragment (Views):**

`DialogFragment` — `Fragment`, который отображает диалог. Предоставляет полный lifecycle для управления состоянием при rotation и конфигурационных изменениях:

```kotlin
// ✅ Управление lifecycle и rotation через DialogFragment
class ConfirmDialog : DialogFragment() {
    override fun onCreateDialog(saved: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setTitle("Подтверждение")
            .setPositiveButton("Да") { _, _ -> confirm() }
            .setNegativeButton("Нет", null)
            .create()
    }
    
    // Состояние сохраняется автоматически при rotation
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранение кастомного состояния
    }
}

// Show через FragmentManager
ConfirmDialog().show(supportFragmentManager, "confirm")

// ⚠️ Важно: использовать getChildFragmentManager() для вложенных диалогов
```

**Fragment (Views):**

`Fragment` — модульная часть UI с полным lifecycle для построения сложных экранов:

```kotlin
// ✅ Сложные экраны с состоянием и ViewModel
class ProfileFragment : Fragment(R.layout.fragment_profile) {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onViewCreated(view: View, saved: Bundle?) {
        super.onViewCreated(view, saved)
        
        // Использование viewLifecycleOwner для корректного lifecycle
        viewModel.profile.observe(viewLifecycleOwner) { profile ->
            bind(profile)
        }
        
        // Обработка событий
        view.findViewById<Button>(R.id.editButton).setOnClickListener {
            navigateToEdit()
        }
    }
    
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Сохранение UI состояния
    }
}

// ⚠️ Важно: использовать viewLifecycleOwner для LiveData/Flow,
// чтобы избежать утечек при уничтожении View
```

**Compose equivalents:**

В Jetpack Compose концепции диалога и экрана реализованы через composable функции:

```kotlin
// ✅ Dialog в Compose с state management
@Composable
fun ConfirmDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text("Да")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Нет")
            }
        },
        title = { Text("Подтверждение") },
        text = { Text("Действие нельзя отменить") }
    )
}

// Использование с state
var showDialog by remember { mutableStateOf(false) }
if (showDialog) {
    ConfirmDialog(
        onConfirm = { 
            confirm()
            showDialog = false
        },
        onDismiss = { showDialog = false }
    )
}

// ✅ Screen (аналог Fragment) с ViewModel
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel()
) {
    val profile by viewModel.profile.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        ProfileHeader(profile)
        ProfileContent(profile)
    }
}

// Навигация через NavController
NavHost(navController, startDestination = "profile") {
    composable("profile") { ProfileScreen() }
    composable("edit") { EditScreen() }
}
```

**Когда использовать:**
- **Dialog**: Подтверждения, ошибки, короткий ввод данных
- **DialogFragment**: Те же случаи + нужен lifecycle (rotation, state)
- **Fragment**: Полноценные экраны, навигация, сложное состояние

## Answer (EN)

**Concept:**

`Dialog` and `Fragment` solve different problems in Android UI. `Dialog` is a modal window for short-term interactions (confirmations, data input, error notifications). `Fragment` is a modular UI part with full lifecycle for building screens and navigation between them. Understanding the differences is critical for choosing the right component when designing UI.

**Key differences:**

| Aspect | Dialog | Fragment |
|--------|--------|----------|
| **Purpose** | Temporary interactions (confirmations, errors, short input) | Reusable screens and UI modules |
| **Lifecycle** | Simplified (show/dismiss, no full lifecycle) | Full lifecycle (onCreate → onViewCreated → onDestroy) |
| **Navigation** | Not in back stack, dismissed on close | Part of Navigation Component, managed by back stack |
| **Complexity** | Simple forms, single screen | Complex UI with state, can contain nested components |
| **State** | Lost on rotation without DialogFragment | Preserved via `onSaveInstanceState` |
| **Reusability** | Limited, usually recreated | High, can be used on different screens |
| **Compose equivalent** | `AlertDialog`, `Dialog` composable | `Screen` composable, navigation via NavController |

**Dialog (Views):**

Simple dialogs via `AlertDialog.Builder` for quick confirmations and notifications:

```kotlin
// ✅ Simple confirmations without lifecycle
AlertDialog.Builder(context)
    .setTitle("Delete?")
    .setMessage("Cannot be undone")
    .setPositiveButton("Yes") { _, _ -> delete() }
    .setNegativeButton("No", null)
    .show()

// ⚠️ Problem: state lost on rotation
// Solution: use DialogFragment
```

**DialogFragment (Views):**

`DialogFragment` is a `Fragment` that displays a dialog. Provides full lifecycle for state management on rotation and configuration changes:

```kotlin
// ✅ Lifecycle and rotation management via DialogFragment
class ConfirmDialog : DialogFragment() {
    override fun onCreateDialog(saved: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setTitle("Confirmation")
            .setPositiveButton("Yes") { _, _ -> confirm() }
            .setNegativeButton("No", null)
            .create()
    }
    
    // State automatically preserved on rotation
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save custom state
    }
}

// Show via FragmentManager
ConfirmDialog().show(supportFragmentManager, "confirm")

// ⚠️ Important: use getChildFragmentManager() for nested dialogs
```

**Fragment (Views):**

`Fragment` is a modular UI part with full lifecycle for building complex screens:

```kotlin
// ✅ Complex screens with state and ViewModel
class ProfileFragment : Fragment(R.layout.fragment_profile) {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onViewCreated(view: View, saved: Bundle?) {
        super.onViewCreated(view, saved)
        
        // Use viewLifecycleOwner for correct lifecycle
        viewModel.profile.observe(viewLifecycleOwner) { profile ->
            bind(profile)
        }
        
        // Handle events
        view.findViewById<Button>(R.id.editButton).setOnClickListener {
            navigateToEdit()
        }
    }
    
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        // Save UI state
    }
}

// ⚠️ Important: use viewLifecycleOwner for LiveData/Flow
// to avoid leaks on View destruction
```

**Compose equivalents:**
```kotlin
// ✅ Dialog in Compose
@Composable
fun ConfirmDialog(onConfirm: () -> Unit, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { TextButton(onClick = onConfirm) { Text("Yes") } },
        dismissButton = { TextButton(onClick = onDismiss) { Text("No") } },
        title = { Text("Confirmation") }
    )
}

// ✅ Screen (Fragment equivalent)
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val profile by viewModel.profile.collectAsState()

    Column {
        ProfileHeader(profile)
        ProfileContent(profile)
    }
}
```

**When to use:**
- **Dialog**: Confirmations, errors, short data input
- **DialogFragment**: Same cases + need lifecycle (rotation, state)
- **Fragment**: Full screens, navigation, complex state

---

## Follow-ups

- Why use DialogFragment over regular Dialog for rotation handling?
- How to pass data between DialogFragment and parent Fragment?
- What happens to Dialog state during configuration changes?
- Can Fragment handle modal behavior like Dialog?
- How does Compose Dialog differ from Views AlertDialog?

## References

- [[c-dialog]] - Dialog patterns
- [[c-fragment]] - Fragment architecture
- https://developer.android.com/guide/fragments
- https://developer.android.com/develop/ui/views/components/dialogs
- https://developer.android.com/develop/ui/compose/components/dialog

## Related Questions

### Prerequisites (Easier)
- [[q-activity-vs-fragment--android--easy]] - Activity vs Fragment basics
- [[q-fragment-basics--android--easy]] - Fragment fundamentals

### Related (Same Level)
- [[q-bottomsheet-vs-dialog--android--medium]] - BottomSheet vs Dialog
- [[q-dialog-vs-fragment--android--medium]] - Dialog state

### Advanced (Harder)
- [[q-fragment-result-api--android--hard]] - Fragment communication
- [[q-custom-dialog-implementation--android--hard]] - Custom dialogs
