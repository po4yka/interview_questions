---
id: android-127
title: "How Dialog Differs From Other Navigation / Чем Dialog отличается от другой навигации"
aliases: ["How Dialog Differs From Other Navigation", "Чем Dialog отличается от другой навигации"]
topic: android
subtopics: [ui-compose, ui-navigation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-navigation, q-main-thread-android--android--medium, q-what-is-layout-performance-measured-in--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/ui-compose, android/ui-navigation, dialog, difficulty/medium, navigation]
sources: []

date created: Saturday, November 1st 2025, 1:30:38 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---
# Вопрос (RU)

> Чем dialog отличается от остальной навигации?

# Question (EN)

> How does dialog differ from other navigation?

---

## Ответ (RU)

Dialog — это UI-компонент, который отображается поверх текущего экрана как временный оверлей и концептуально отличается от экранов-назначений (navigation destinations):

**Ключевые отличия:**

1. **Overlay vs Replacement** — Dialog отображается поверх текущего экрана; обычная навигация переходит на новый экран (destination) или изменяет back stack.
2. **Back `Stack`** — Классический Dialog (вьюшный/Compose `AlertDialog`) сам по себе не добавляется в back stack навигации. Однако:
   - `DialogFragment` может быть добавлен в back stack `FragmentManager`.
   - В Navigation Component и Compose Navigation существуют dialog-destinations, которые становятся частью back stack `NavController`.
3. **State Preservation** — Под Dialog обычно сохраняется состояние родительского экрана (он остаётся в памяти и в иерархии/compose tree), тогда как при навигации на другой экран состояние может потребовать сохранения/восстановления через `SavedStateHandle`, `rememberSaveable` и т.п.
4. **Scope** — Dialog используется для кратких, фокусированных взаимодействий (подтверждения, выбор опций, простые формы), а навигация — для полноценных экранов и сложных сценариев.
5. **Lifecycle** — Dialog имеет собственный UI-жизненный цикл, но он привязан к родительскому `Activity`/`Fragment`/компоновке: при уничтожении родителя диалог должен быть корректно закрыт/воссоздан согласно их жизненному циклу.

**Использование:** подтверждения действий, простые формы, выбор опций (date/time picker), индикаторы прогресса.

### Jetpack Compose

```kotlin
@Composable
fun MyScreen() {
    var showDialog by remember { mutableStateOf(false) } // ✅ Локальное состояние для управления видимостью

    // ... контент экрана

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false }, // ✅ Обновляем состояние при закрытии (back/тап вовне/gesture)
            title = { Text("Confirm") },
            text = { Text("Delete item?") },
            confirmButton = {
                TextButton(onClick = {
                    // ✅ Обрабатываем действие, затем закрываем
                    showDialog = false
                }) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

// ❌ Плохо: состояние диалога не управляется корректно
@Composable
fun BadExample() {
    AlertDialog(
        onDismissRequest = {
            // ❌ Состояние не обновляется: пользовательские жесты закрытия (back, тап вне) лишь вызовут этот колбэк,
            // но сам диалог останется на экране, если вы не измените состояние.
        },
        // ...
    )
}
```

### Traditional Android (Views)

```kotlin
// ✅ Хорошо: DialogFragment с привязкой к lifecycle и возможностью работы с back stack
class ConfirmDialogFragment : DialogFragment() {
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setMessage("Confirm action?")
            .setPositiveButton("OK") { _, _ -> /* action */ }
            .setNegativeButton("Cancel", null)
            .create()
    }
}

// ⚠️ Ограничение: прямой AlertDialog не привязан к FragmentManager/NavController
// и не будет автоматически пересоздан при конфигурационных изменениях.
// При смене конфигурации такой диалог обычно будет закрыт, и если нужно восстановление,
// это требуется делать вручную.
AlertDialog.Builder(context)
    .setMessage("Confirm?")
    .show() // ⚠️ Потеряется при повороте экрана без доп. логики
```

**Связь с [[c-compose-navigation]]:** По умолчанию обычные диалоги (например, `AlertDialog` в Compose) не считаются отдельными навигационными destinations и напрямую не управляют back stack `NavController`. Отдельные dialog-destinations в навигации — это явный механизм, когда вы хотите, чтобы диалог был частью навигационного графа.

---

## Answer (EN)

A dialog is a UI component shown on top of the current screen as a temporary overlay and is conceptually different from navigation destinations (screens):

**Key Differences:**

1. **Overlay vs Replacement** - A dialog appears on top of the current screen; standard navigation moves to another screen (destination) or mutates the back stack.
2. **Back `Stack`** - A regular dialog (view-based or Compose `AlertDialog`) by itself is not added as a standard navigation back stack entry. However:
   - A `DialogFragment` can be added to the `FragmentManager` back stack.
   - Navigation Component and Compose Navigation provide dialog destinations that do participate in the `NavController` back stack.
3. **State Preservation** - The underlying screen state is typically preserved while a dialog is shown (the screen remains in memory / in the compose tree). With full navigation to another destination, you often rely on `SavedStateHandle`, `rememberSaveable`, etc., to restore state.
4. **Scope** - Dialogs are for short, focused interactions (confirmations, option picks, simple forms); navigation is for full screens and complex flows.
5. **Lifecycle** - A dialog has its own UI lifecycle but is tied to its parent `Activity`/`Fragment`/composition: when the parent is destroyed, the dialog must be closed or recreated consistently with that lifecycle.

**Use Cases:** Action confirmations, simple forms, option selection (date/time pickers), progress indicators.

### Jetpack Compose

```kotlin
@Composable
fun MyScreen() {
    var showDialog by remember { mutableStateOf(false) } // ✅ Local state controlling visibility

    // ... screen content

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false }, // ✅ Update state on dismiss (back/outside tap/gesture)
            title = { Text("Confirm") },
            text = { Text("Delete item?") },
            confirmButton = {
                TextButton(onClick = {
                    // ✅ Handle action then dismiss
                    showDialog = false
                }) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

// ❌ Bad: Dialog state not managed properly
@Composable
fun BadExample() {
    AlertDialog(
        onDismissRequest = {
            // ❌ If you don't update state here, user dismiss gestures (back, outside tap)
            // will invoke this callback, but the dialog will remain visible.
        },
        // ...
    )
}
```

### Traditional Android (Views)

```kotlin
// ✅ Good: DialogFragment with lifecycle awareness and optional back stack integration
class ConfirmDialogFragment : DialogFragment() {
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        return AlertDialog.Builder(requireContext())
            .setMessage("Confirm action?")
            .setPositiveButton("OK") { _, _ -> /* action */ }
            .setNegativeButton("Cancel", null)
            .create()
    }
}

// ⚠️ Limitation: Direct AlertDialog is not tied to FragmentManager/NavController
// and will not be automatically recreated across configuration changes.
// On configuration change, such a dialog is typically dismissed; if you need it back,
// you must handle recreation manually.
AlertDialog.Builder(context)
    .setMessage("Confirm?")
    .show() // ⚠️ Lost on rotation without additional handling
```

**Related to [[c-compose-navigation]]:** By default, regular dialogs (e.g., Compose `AlertDialog`) are not separate navigation destinations and do not directly manipulate the `NavController` back stack. Explicit dialog destinations in the navigation graph are used when you want a dialog to be part of navigation.

---

## Дополнительные Вопросы (RU)

- Как состояние диалога переживает изменения конфигурации в Compose и во вьюшном подходе?
- Что происходит с диалогом при уничтожении родительской activity/компоновки?
- Как реализовать вложенную навигацию с диалогами в Navigation Component?
- Каковы perf-аспекты частого показа диалогов?

## Follow-ups

- How does dialog state survive configuration changes in Compose vs Views?
- What happens to dialog when parent activity/composable is destroyed?
- How to implement nested navigation with dialogs in Navigation Component?
- What are the performance implications of showing dialogs frequently?

---

## Ссылки (RU)

- [[c-compose-navigation]]
- [[c-compose-state]]
- [[c-lifecycle]]

## References

- [[c-compose-navigation]] - Navigation in Jetpack Compose
- [[c-compose-state]] - State management in Compose
- [[c-lifecycle]] - Android lifecycle concepts

---

## Связанные Вопросы (RU)

### База (проще)

### Связанные (средние)
- [[q-main-thread-android--android--medium]]
- [[q-what-is-layout-performance-measured-in--android--medium]]

### Продвинутые (сложнее)
- Реализация собственных dialog-destinations в Navigation Component
- Управление состоянием диалогов при смерти процесса
- Построение переиспользуемых диалоговых систем в Compose

## Related Questions

### Prerequisites (Easier)

### Related (Medium)
- [[q-main-thread-android--android--medium]] - Main thread and UI operations
- [[q-what-is-layout-performance-measured-in--android--medium]] - Performance considerations

### Advanced (Harder)
- Implementing custom dialog destinations in Navigation Component
- Managing dialog state across process death
- Building reusable dialog systems with Compose
