---
topic: android
tags:
  - android
  - android/fragments
  - android/layouts
  - android/ui
  - fragment
  - fragments
  - layoutinflater
  - layouts
  - ui
difficulty: easy
status: reviewed
---

# Каким образом ты выбираешь layout?

**English**: How do you choose a layout?

## Answer

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

## Ответ

Выбор макета для фрагмента осуществляется в методе onCreateView с помощью LayoutInflater. Пример: override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? { return inflater.inflate(R.layout.fragment_example, container, false) }

