---
id: "20251015082237271"
title: "How To Choose Layout For Fragment / Как выбрать layout для Fragment"
topic: android
difficulty: easy
status: draft
created: 2025-10-15
tags: - android
  - android/fragments
  - android/layouts
  - android/ui
  - fragment
  - fragments
  - layoutinflater
  - layouts
  - ui
---

# Каким образом ты выбираешь layout?

**English**: How do you choose a layout?

## Answer (EN)

In Android fragments, layout selection is performed in the **onCreateView()** method using **LayoutInflater**. This is the standard approach for inflating XML layouts into View objects.

### Basic Layout Inflation

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_example, container, false)
    }
}
```

### Key Parameters Explained

1. **inflater**: LayoutInflater provided by the system
2. **container**: Parent ViewGroup that the fragment's UI will be attached to
3. **attachToRoot**: Should be **false** for fragments (FragmentManager handles attachment)

### Modern Approach with View Binding

```kotlin
class MyFragment : Fragment() {
    private var _binding: FragmentExampleBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentExampleBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Access views through binding
        binding.textView.text = "Hello"
        binding.button.setOnClickListener {
            // Handle click
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Prevent memory leaks
    }
}
```

### Alternative: Programmatic Layout Creation

For dynamic or custom layouts, you can create views programmatically:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Create layout programmatically
        return LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )

            addView(TextView(requireContext()).apply {
                text = "Dynamic TextView"
                textSize = 18f
            })

            addView(Button(requireContext()).apply {
                text = "Dynamic Button"
                setOnClickListener {
                    // Handle click
                }
            })
        }
    }
}
```

### Conditional Layout Selection

Choose different layouts based on device characteristics:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
            R.layout.fragment_example_tablet
        } else {
            R.layout.fragment_example_phone
        }

        return inflater.inflate(layoutId, container, false)
    }
}
```

### Using Different Layouts for Orientation

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val layoutId = when (resources.configuration.orientation) {
            Configuration.ORIENTATION_LANDSCAPE -> R.layout.fragment_landscape
            else -> R.layout.fragment_portrait
        }

        return inflater.inflate(layoutId, container, false)
    }
}
```

### Jetpack Compose Alternative

Modern approach using Compose:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setContent {
                MaterialTheme {
                    Column {
                        Text("Hello from Compose")
                        Button(onClick = { /* Handle click */ }) {
                            Text("Click Me")
                        }
                    }
                }
            }
        }
    }
}
```

### Best Practices

1. **Always return non-null View** from onCreateView (unless using old patterns)
2. **Use View Binding** over findViewById for type safety
3. **Set attachToRoot to false** when inflating in fragments
4. **Clean up binding references** in onDestroyView
5. **Consider Compose** for new projects
6. **Use resource qualifiers** (layout-land, layout-sw600dp) instead of runtime checks

### Common Mistakes to Avoid

```kotlin
// WRONG - attachToRoot = true
return inflater.inflate(R.layout.fragment_example, container, true)

// CORRECT - attachToRoot = false
return inflater.inflate(R.layout.fragment_example, container, false)

// WRONG - Not cleaning up binding
private val binding: FragmentExampleBinding? = null // Memory leak

// CORRECT - Clean up in onDestroyView
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

## Ответ (RU)

В Android фрагментах выбор макета выполняется в методе **onCreateView()** с использованием **LayoutInflater**. Это стандартный подход для преобразования XML макетов в объекты View.

### Базовое преобразование макета

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Преобразовать макет для этого фрагмента
        return inflater.inflate(R.layout.fragment_example, container, false)
    }
}
```

### Объяснение ключевых параметров

1. **inflater**: LayoutInflater предоставленный системой
2. **container**: Родительский ViewGroup к которому UI фрагмента будет присоединен
3. **attachToRoot**: Должен быть **false** для фрагментов (FragmentManager управляет присоединением)

### Современный подход с View Binding

```kotlin
class MyFragment : Fragment() {
    private var _binding: FragmentExampleBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentExampleBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Доступ к view через binding
        binding.textView.text = "Привет"
        binding.button.setOnClickListener {
            // Обработка нажатия
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // Предотвращение утечек памяти
    }
}
```

### Альтернатива: Программное создание макета

Для динамических или кастомных макетов можно создавать view программно:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Создать макет программно
        return LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )

            addView(TextView(requireContext()).apply {
                text = "Динамический TextView"
                textSize = 18f
            })

            addView(Button(requireContext()).apply {
                text = "Динамическая кнопка"
                setOnClickListener {
                    // Обработка нажатия
                }
            })
        }
    }
}
```

### Условный выбор макета

Выбор различных макетов на основе характеристик устройства:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
            R.layout.fragment_example_tablet
        } else {
            R.layout.fragment_example_phone
        }

        return inflater.inflate(layoutId, container, false)
    }
}
```

### Использование разных макетов для ориентации

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val layoutId = when (resources.configuration.orientation) {
            Configuration.ORIENTATION_LANDSCAPE -> R.layout.fragment_landscape
            else -> R.layout.fragment_portrait
        }

        return inflater.inflate(layoutId, container, false)
    }
}
```

### Альтернатива Jetpack Compose

Современный подход с использованием Compose:

```kotlin
class MyFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return ComposeView(requireContext()).apply {
            setContent {
                MaterialTheme {
                    Column {
                        Text("Привет из Compose")
                        Button(onClick = { /* Обработка нажатия */ }) {
                            Text("Нажми меня")
                        }
                    }
                }
            }
        }
    }
}
```

### Лучшие практики

1. **Всегда возвращайте non-null View** из onCreateView (если не используете старые паттерны)
2. **Используйте View Binding** вместо findViewById для безопасности типов
3. **Устанавливайте attachToRoot в false** при преобразовании во фрагментах
4. **Очищайте ссылки binding** в onDestroyView
5. **Рассмотрите Compose** для новых проектов
6. **Используйте resource qualifiers** (layout-land, layout-sw600dp) вместо runtime проверок

### Частые ошибки, которых следует избегать

```kotlin
// НЕПРАВИЛЬНО - attachToRoot = true
return inflater.inflate(R.layout.fragment_example, container, true)

// ПРАВИЛЬНО - attachToRoot = false
return inflater.inflate(R.layout.fragment_example, container, false)

// НЕПРАВИЛЬНО - Не очищается binding
private val binding: FragmentExampleBinding? = null // Утечка памяти

// ПРАВИЛЬНО - Очистка в onDestroyView
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

**Резюме**: Выбор макета для фрагмента осуществляется в методе **onCreateView()** с помощью **LayoutInflater**. Стандартный подход: `inflater.inflate(R.layout.fragment_example, container, false)`. Современный подход использует **View Binding** для type-safe доступа к views. Альтернативно можно создавать макеты программно или использовать Jetpack Compose. Всегда устанавливайте `attachToRoot = false` для фрагментов и очищайте binding ссылки в onDestroyView для предотвращения утечек памяти.

---

## Related Questions
