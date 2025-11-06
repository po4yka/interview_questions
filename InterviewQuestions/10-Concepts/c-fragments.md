---
id: ivc-20251030-122939
title: Fragments / Фрагменты
aliases: [Android Fragment, Fragment, Фрагмент, Фрагменты]
kind: concept
summary: Reusable UI component with its own lifecycle, part of an Activity
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, android-components, concept, fragments, ui]
---

# Summary (EN)

A **Fragment** is a modular, reusable UI component in Android that represents a portion of the user interface within an Activity. Fragments have their own lifecycle, receive their own input events, and can be added or removed while the Activity is running. They enable flexible UI designs, multi-pane layouts (tablets), and modular navigation patterns.

**Key Characteristics**:
- **Lifecycle**: Independent lifecycle nested within Activity lifecycle
- **Reusability**: Same Fragment can be used in multiple Activities or configurations
- **Modularity**: Encapsulates UI logic and behavior
- **BackStack**: FragmentManager handles transaction history and back navigation
- **Modern Pattern**: Single-Activity architecture with Fragment-based navigation (Navigation Component)

**Core Components**:
- `Fragment`: Base class for UI components
- `FragmentManager`: Manages Fragment transactions and back stack
- `FragmentTransaction`: API for adding, replacing, removing Fragments
- `FragmentContainerView`: Recommended container for hosting Fragments

# Сводка (RU)

**Fragment** — это модульный, переиспользуемый UI-компонент в Android, представляющий часть пользовательского интерфейса внутри Activity. Фрагменты имеют собственный жизненный цикл, получают собственные события ввода и могут добавляться или удаляться во время работы Activity. Они обеспечивают гибкий дизайн UI, многопанельные макеты (планшеты) и модульную навигацию.

**Ключевые характеристики**:
- **Жизненный цикл**: Независимый жизненный цикл, вложенный в жизненный цикл Activity
- **Переиспользуемость**: Один Fragment можно использовать в нескольких Activity или конфигурациях
- **Модульность**: Инкапсулирует UI-логику и поведение
- **BackStack**: FragmentManager управляет историей транзакций и навигацией назад
- **Современный паттерн**: Архитектура Single-Activity с навигацией на основе Fragment (Navigation Component)

**Основные компоненты**:
- `Fragment`: Базовый класс для UI-компонентов
- `FragmentManager`: Управляет транзакциями Fragment и стеком назад
- `FragmentTransaction`: API для добавления, замены, удаления Fragment
- `FragmentContainerView`: Рекомендуемый контейнер для размещения Fragment

## Fragment Lifecycle

**Lifecycle States** (relative to Activity):
```
Activity Created → Fragment:
  onAttach() → onCreate() → onCreateView() → onViewCreated() → onStart() → onResume()

Activity Paused/Stopped → Fragment:
  onPause() → onStop()

Activity Destroyed → Fragment:
  onDestroyView() → onDestroy() → onDetach()
```

**Key Methods**:
- `onCreateView()`: Inflate Fragment layout
- `onViewCreated()`: Initialize views after inflation (recommended place for view setup)
- `onDestroyView()`: Clean up view references (avoid memory leaks)
- `onAttach()`/`onDetach()`: Fragment attached/detached from Activity

**ViewLifecycleOwner**: Use `viewLifecycleOwner` for observing LiveData/Flow to avoid leaks after view destruction.

## FragmentManager and Transactions

**Adding/Replacing Fragments**:
```kotlin
// Modern approach
supportFragmentManager.commit {
    setReorderingAllowed(true)
    replace(R.id.fragment_container, MyFragment())
    addToBackStack("transaction_name")
}
```

**Best Practices**:
- Always call `setReorderingAllowed(true)` for optimized state changes
- Use `replace()` for single-pane, `add()` for multi-pane
- Add to back stack for navigation history
- Avoid nested transactions without proper lifecycle management

**FragmentContainerView**:
```xml
<androidx.fragment.app.FragmentContainerView
    android:id="@+id/fragment_container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

## Use Cases / Trade-offs

**Use Cases**:
- **Single-Activity Architecture**: Modern pattern with Navigation Component (primary use case)
- **Multi-pane Layouts**: Master-detail UI for tablets (list + detail in same screen)
- **Modular UI**: Reusable components across multiple screens
- **ViewPager**: Tab-based navigation with swipeable screens
- **Dialog Fragments**: Modal dialogs with Fragment lifecycle

**Modern Approach** (2025):
- **Preferred**: Single Activity + Fragments + Navigation Component
- **Jetpack Compose**: Fragments less necessary, but still used for interop and gradual migration
- **ViewModel Scoping**: Share ViewModels between Activity and Fragments using `activityViewModels()`

**Trade-offs**:
- **Complexity**: Additional lifecycle layer adds complexity vs simple Activities
- **Learning Curve**: Understanding nested lifecycles, transaction states, back stack
- **Compose Migration**: Fragments becoming legacy as Compose adoption grows
- **Benefits**: Better testability, reusability, navigation patterns, lifecycle management

**Deprecated Patterns**:
- Avoid `<fragment>` tag in XML (use `FragmentContainerView`)
- Avoid `setRetainInstance(true)` (use ViewModels instead)
- Avoid multiple Activities (prefer Single-Activity + Fragments)

## References

- [Android Fragments Official Guide](https://developer.android.com/guide/fragments)
- [Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [FragmentManager](https://developer.android.com/guide/fragments/fragmentmanager)
- [Navigation Component](https://developer.android.com/guide/navigation)
- [Single-Activity Architecture](https://www.youtube.com/watch?v=2k8x8V77CrU)
