---
id: android-171
title: "Single Activity Pros Cons / Преимущества и недостатки Single Activity"
aliases: ["Single Activity Pros Cons", "Преимущества и недостатки Single Activity"]
topic: android
subtopics: [activity, fragment, ui-navigation]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: draft
moc: moc-android
related: [q-activity-lifecycle-methods--android--medium, q-what-is-activity-and-what-is-it-used-for--android--medium, q-why-are-fragments-needed-if-there-is-activity--android--hard]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android, android/activity, android/fragment, android/ui-navigation, fragment, single-activity, viewmodel, navigation, difficulty/medium]
---
# Вопрос (RU)

Какие у подхода Single Activity этого подхода плюсы и минусы?

# Question (EN)

What are the pros and cons of the Single Activity approach?

## Ответ (RU)

**Подход Single Activity** — использование **одной Activity** для всего приложения, где все экраны представлены как **Fragment**. Это противоположность традиционному подходу с множеством Activity.

### Плюсы (Advantages)

1. **Упрощенная навигация** — NavController вместо Intent
2. **Общий ViewModel** — легко делиться данными между экранами через `activityViewModels()`
3. **Общие UI элементы** — toolbar и bottom navigation не пересоздаются
4. **Лучшие анимации** — плавные shared element transitions между фрагментами
5. **Быстрые переходы** — нет overhead создания новой Activity (lifecycle, Window, theme)
6. **Легкие deep links** — Navigation Component автоматически обрабатывает
7. **Проще state management** — одно состояние на всё приложение через SavedStateHandle

**Пример навигации:**
```kotlin
// ✅ Single Activity - простая навигация
navController.navigate(R.id.profileFragment, bundleOf("userId" to userId))

// ❌ Multi-Activity - сложнее
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("userId", userId)
startActivityForResult(intent, REQUEST_CODE) // deprecated API
```

**Общий ViewModel:**
```kotlin
// ✅ Легко делиться данными между фрагментами
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun updateUser(user: User) {
        sharedViewModel.userData.value = user // Fragment B получит обновление
    }
}

class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels() // та же instance
}
```

### Минусы (Disadvantages)

1. **Сложность Fragment lifecycle** — больше callback методов (`onDestroyView`, `onDetach`), два lifecycle (Fragment + View)
2. **Утечки памяти** — ViewBinding нужно очищать в `onDestroyView`
3. **Сложность FragmentManager** — управление back stack может запутать
4. **State loss проблемы** — `IllegalStateException` при commit после `onSaveInstanceState`
5. **Вложенные фрагменты** — `childFragmentManager` vs `parentFragmentManager` confusion
6. **Сложность тестирования** — больше setup чем для Activity (`launchFragmentInContainer`)
7. **Обработка кнопки назад** — нужно перехватывать через `onBackPressedDispatcher`

**ViewBinding утечка:**
```kotlin
// ❌ Утечка памяти - binding не очищен
class MyFragment : Fragment() {
    private val binding: FragmentMyBinding? = null

    override fun onCreateView(...): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // View уничтожен, но binding ссылается на него = LEAK
}

// ✅ Правильный подход
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Must cleanup!
    }
}
```

### Сравнение

| Аспект | Single Activity | Multi-Activity |
|--------|----------------|----------------|
| Навигация | Fragment transactions (быстрая) | Activity intents (медленная) |
| Обмен данными | Shared ViewModel (легко) | Intent extras (сложно) |
| Memory | Меньше (одна Activity) | Больше (много Activity) |
| Кривая обучения | Fragment lifecycle (крутая) | Activity lifecycle (проще) |
| Утечки памяти | ViewBinding cleanup нужен | Менее подвержено |
| Тестирование | Больше setup | Проще |

### Когда использовать

**Хорошо для:**
- Приложений с общими UI элементами (toolbar, bottom nav)
- Сложной навигации с shared state
- Современных приложений с Jetpack Navigation/Compose

**Не идеально для:**
- Простых приложений с малым количеством экранов
- Legacy кодовых баз (дорогая миграция)
- Команд незнакомых с Fragment lifecycle

**Вердикт:**
Single Activity — это **современный Android стандарт** (особенно с Navigation Component и Compose), но требует понимания Fragment lifecycle и best practices.

## Answer (EN)

**Single Activity approach** uses **one Activity** for the entire application, with all screens represented as **Fragments**. This contrasts with traditional multi-Activity where each screen is a separate Activity.

### Advantages (Pros)

1. **Simplified navigation** — NavController instead of Intents
2. **Shared ViewModel** — easy data sharing between screens via `activityViewModels()`
3. **Shared UI elements** — toolbar and bottom navigation not recreated
4. **Better animations** — smooth shared element transitions between fragments
5. **Faster transitions** — no Activity recreation overhead (lifecycle, Window, theme)
6. **Easier deep linking** — Navigation Component handles automatically
7. **Simpler state management** — single state for entire app via SavedStateHandle

**Navigation example:**
```kotlin
// ✅ Single Activity - simple navigation
navController.navigate(R.id.profileFragment, bundleOf("userId" to userId))

// ❌ Multi-Activity - more complex
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("userId", userId)
startActivityForResult(intent, REQUEST_CODE) // deprecated API
```

**Shared ViewModel:**
```kotlin
// ✅ Easy data sharing between fragments
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun updateUser(user: User) {
        sharedViewModel.userData.value = user // Fragment B will receive update
    }
}

class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels() // same instance
}
```

### Disadvantages (Cons)

1. **Fragment lifecycle complexity** — more callbacks (`onDestroyView`, `onDetach`), two lifecycles (Fragment + View)
2. **Memory leaks** — ViewBinding requires cleanup in `onDestroyView`
3. **FragmentManager complexity** — back stack management can be confusing
4. **State loss issues** — `IllegalStateException` on commit after `onSaveInstanceState`
5. **Nested fragments** — `childFragmentManager` vs `parentFragmentManager` confusion
6. **Testing complexity** — more setup than Activity (`launchFragmentInContainer`)
7. **Back button handling** — need to intercept via `onBackPressedDispatcher`

**ViewBinding leak:**
```kotlin
// ❌ Memory leak - binding not cleaned
class MyFragment : Fragment() {
    private val binding: FragmentMyBinding? = null

    override fun onCreateView(...): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }
    // View destroyed but binding still references it = LEAK
}

// ✅ Correct approach
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Must cleanup!
    }
}
```

### Comparison

| Aspect | Single Activity | Multi-Activity |
|--------|----------------|----------------|
| Navigation | Fragment transactions (fast) | Activity intents (slow) |
| Data sharing | Shared ViewModel (easy) | Intent extras (complex) |
| Memory | Lower (one Activity) | Higher (multiple Activities) |
| Learning curve | Fragment lifecycle (steep) | Activity lifecycle (simpler) |
| Memory leaks | ViewBinding cleanup needed | Less prone |
| Testing | More setup required | Simpler |

### When to Use

**Good fit for:**
- Apps with shared UI elements (toolbar, bottom nav)
- Complex navigation with shared state
- Modern apps using Jetpack Navigation/Compose

**Not ideal for:**
- Simple apps with few screens
- Legacy codebases (expensive migration)
- Teams unfamiliar with Fragment lifecycle

**Verdict:**
Single Activity is the **modern Android standard** (especially with Navigation Component and Compose), but requires understanding Fragment lifecycle and best practices.

---

## Follow-ups

- How to handle configuration changes in Single Activity with Fragments?
- What are the memory implications of keeping Fragments in back stack?
- How does Navigation Component handle deep links and conditional navigation?
- What are best practices for ViewBinding cleanup in Fragments?
- How to implement nested navigation graphs in Single Activity?

## References

- Official Android documentation: Navigation Component
- Official Android documentation: Fragment best practices
- Official Android documentation: Single Activity architecture guide

## Related Questions

### Prerequisites
- [[q-activity-lifecycle-methods--android--medium]] — Activity lifecycle understanding needed

### Related
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]] — Activity fundamentals
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] — Fragment-Activity relationship

### Advanced
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] — Deep dive into Fragment architecture
