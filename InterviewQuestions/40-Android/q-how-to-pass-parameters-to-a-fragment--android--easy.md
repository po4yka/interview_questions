---
topic: android
tags:
  - fragments
  - bundle
  - android
  - ui
  - data-passing
difficulty: medium
status: draft
---

# How to pass parameters to a fragment?

## Question (RU)

Как передать параметры во фрагмент

## Answer

The recommended and safe way to pass parameters to a Fragment in Android is using **Bundle** with the fragment's `arguments` property. This approach is supported by the Android system and survives configuration changes.

### 1. Basic Approach - Using Bundle

```kotlin
class DetailsFragment : Fragment() {

    companion object {
        private const val ARG_ITEM_ID = "item_id"
        private const val ARG_ITEM_NAME = "item_name"

        // Factory method to create fragment with arguments
        fun newInstance(itemId: Int, itemName: String): DetailsFragment {
            return DetailsFragment().apply {
                arguments = Bundle().apply {
                    putInt(ARG_ITEM_ID, itemId)
                    putString(ARG_ITEM_NAME, itemName)
                }
            }
        }
    }

    private var itemId: Int = -1
    private var itemName: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Extract arguments
        arguments?.let {
            itemId = it.getInt(ARG_ITEM_ID, -1)
            itemName = it.getString(ARG_ITEM_NAME)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_details, container, false)

        // Use the parameters
        view.findViewById<TextView>(R.id.textView).text = "ID: $itemId, Name: $itemName"

        return view
    }
}

// Usage in Activity or another Fragment
class MainActivity : AppCompatActivity() {
    private fun showDetailsFragment() {
        val fragment = DetailsFragment.newInstance(
            itemId = 42,
            itemName = "Sample Item"
        )

        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .addToBackStack(null)
            .commit()
    }
}
```

### 2. Using requireArguments() - Kotlin Way

```kotlin
class UserFragment : Fragment() {

    companion object {
        private const val ARG_USER_ID = "user_id"
        private const val ARG_USER_EMAIL = "user_email"
        private const val ARG_IS_PREMIUM = "is_premium"

        fun newInstance(userId: Long, email: String, isPremium: Boolean) = UserFragment().apply {
            arguments = Bundle().apply {
                putLong(ARG_USER_ID, userId)
                putString(ARG_USER_EMAIL, email)
                putBoolean(ARG_IS_PREMIUM, isPremium)
            }
        }
    }

    // Lazy initialization from arguments
    private val userId: Long by lazy {
        requireArguments().getLong(ARG_USER_ID)
    }

    private val userEmail: String by lazy {
        requireArguments().getString(ARG_USER_EMAIL) ?: ""
    }

    private val isPremium: Boolean by lazy {
        requireArguments().getBoolean(ARG_IS_PREMIUM, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Use the arguments
        view.findViewById<TextView>(R.id.tvUserId).text = "User ID: $userId"
        view.findViewById<TextView>(R.id.tvEmail).text = "Email: $userEmail"
        view.findViewById<TextView>(R.id.tvPremium).text = "Premium: $isPremium"
    }
}
```

### 3. Passing Complex Objects - Parcelable/Serializable

```kotlin
// Data class with Parcelable
@Parcelize
data class User(
    val id: Long,
    val name: String,
    val email: String,
    val age: Int
) : Parcelable

class ProfileFragment : Fragment() {

    companion object {
        private const val ARG_USER = "user"

        fun newInstance(user: User) = ProfileFragment().apply {
            arguments = Bundle().apply {
                putParcelable(ARG_USER, user)
            }
        }
    }

    private val user: User by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelable(ARG_USER, User::class.java)!!
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelable(ARG_USER)!!
        }
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<TextView>(R.id.tvName).text = user.name
        view.findViewById<TextView>(R.id.tvEmail).text = user.email
        view.findViewById<TextView>(R.id.tvAge).text = "Age: ${user.age}"
    }
}

// Usage
val user = User(id = 1L, name = "John Doe", email = "john@example.com", age = 30)
val fragment = ProfileFragment.newInstance(user)
```

### 4. Passing Lists and Arrays

```kotlin
class ItemListFragment : Fragment() {

    companion object {
        private const val ARG_ITEM_IDS = "item_ids"
        private const val ARG_ITEM_NAMES = "item_names"
        private const val ARG_ITEMS = "items"

        // Passing primitive arrays
        fun newInstance(ids: IntArray, names: Array<String>) = ItemListFragment().apply {
            arguments = Bundle().apply {
                putIntArray(ARG_ITEM_IDS, ids)
                putStringArray(ARG_ITEM_NAMES, names)
            }
        }

        // Passing ArrayList of Parcelable
        fun newInstance(items: ArrayList<Item>) = ItemListFragment().apply {
            arguments = Bundle().apply {
                putParcelableArrayList(ARG_ITEMS, items)
            }
        }
    }

    private val itemIds: IntArray by lazy {
        requireArguments().getIntArray(ARG_ITEM_IDS) ?: intArrayOf()
    }

    private val itemNames: Array<String> by lazy {
        requireArguments().getStringArray(ARG_ITEM_NAMES) ?: emptyArray()
    }

    private val items: ArrayList<Item> by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireArguments().getParcelableArrayList(ARG_ITEMS, Item::class.java) ?: arrayListOf()
        } else {
            @Suppress("DEPRECATION")
            requireArguments().getParcelableArrayList(ARG_ITEMS) ?: arrayListOf()
        }
    }
}

@Parcelize
data class Item(val id: Int, val name: String) : Parcelable
```

### 5. Type-Safe Arguments with Kotlin Extensions

```kotlin
// Extension functions for type-safe argument handling
inline fun <reified T : Fragment> T.withArgs(
    argsBuilder: Bundle.() -> Unit
): T {
    return this.apply {
        arguments = Bundle().apply(argsBuilder)
    }
}

// Usage becomes cleaner
class ProductFragment : Fragment() {

    companion object {
        private const val ARG_PRODUCT_ID = "product_id"
        private const val ARG_PRODUCT_NAME = "product_name"
        private const val ARG_PRICE = "price"

        fun newInstance(productId: Long, name: String, price: Double) =
            ProductFragment().withArgs {
                putLong(ARG_PRODUCT_ID, productId)
                putString(ARG_PRODUCT_NAME, name)
                putDouble(ARG_PRICE, price)
            }
    }

    private val productId by lazy { requireArguments().getLong(ARG_PRODUCT_ID) }
    private val productName by lazy { requireArguments().getString(ARG_PRODUCT_NAME) ?: "" }
    private val price by lazy { requireArguments().getDouble(ARG_PRICE) }
}
```

### 6. Safe Args Plugin (Navigation Component)

With Navigation Component, use Safe Args for compile-time safety:

```kotlin
// In build.gradle
plugins {
    id("androidx.navigation.safeargs.kotlin")
}

// In navigation XML
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment"
    tools:layout="@layout/fragment_details">

    <argument
        android:name="itemId"
        app:argType="integer" />
    <argument
        android:name="itemName"
        app:argType="string" />
</fragment>

// Generated code usage
class DetailsFragment : Fragment() {

    private val args: DetailsFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Type-safe access
        val itemId = args.itemId
        val itemName = args.itemName

        view.findViewById<TextView>(R.id.textView).text = "ID: $itemId, Name: $itemName"
    }
}

// Navigating with Safe Args
class HomeFragment : Fragment() {
    private fun navigateToDetails() {
        val action = HomeFragmentDirections.actionHomeToDetails(
            itemId = 42,
            itemName = "Sample Item"
        )
        findNavController().navigate(action)
    }
}
```

### 7. Arguments Validation

```kotlin
class ValidatedFragment : Fragment() {

    companion object {
        private const val ARG_REQUIRED_ID = "required_id"
        private const val ARG_OPTIONAL_NAME = "optional_name"

        fun newInstance(id: Long, name: String? = null) = ValidatedFragment().apply {
            arguments = Bundle().apply {
                putLong(ARG_REQUIRED_ID, id)
                name?.let { putString(ARG_OPTIONAL_NAME, it) }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Validate required arguments
        val args = arguments ?: throw IllegalStateException("Fragment arguments are required")

        if (!args.containsKey(ARG_REQUIRED_ID)) {
            throw IllegalArgumentException("Required argument ARG_REQUIRED_ID is missing")
        }
    }

    private val requiredId: Long by lazy {
        requireArguments().getLong(ARG_REQUIRED_ID)
    }

    private val optionalName: String? by lazy {
        arguments?.getString(ARG_OPTIONAL_NAME)
    }
}
```

### 8. Bundle Extension Functions

```kotlin
// Helper extension functions
fun Bundle.putArguments(vararg pairs: Pair<String, Any?>) {
    pairs.forEach { (key, value) ->
        when (value) {
            is String -> putString(key, value)
            is Int -> putInt(key, value)
            is Long -> putLong(key, value)
            is Boolean -> putBoolean(key, value)
            is Float -> putFloat(key, value)
            is Double -> putDouble(key, value)
            is Parcelable -> putParcelable(key, value)
            is Serializable -> putSerializable(key, value)
            else -> throw IllegalArgumentException("Unsupported type: ${value?.javaClass}")
        }
    }
}

// Usage
class SimpleFragment : Fragment() {
    companion object {
        fun newInstance(id: Int, name: String, active: Boolean) = SimpleFragment().apply {
            arguments = Bundle().apply {
                putArguments(
                    "id" to id,
                    "name" to name,
                    "active" to active
                )
            }
        }
    }
}
```

### Best Practices

1. ✅ **Always use Bundle and arguments**
2. ✅ **Create factory methods** (newInstance) in companion object
3. ✅ **Extract arguments in onCreate()**, not in constructors
4. ✅ **Use requireArguments()** for required parameters
5. ✅ **Use constants** for argument keys
6. ✅ **Prefer Parcelable** over Serializable for better performance
7. ✅ **Use Safe Args** with Navigation Component for type safety
8. ❌ **Never pass data via constructor** - doesn't survive configuration changes
9. ❌ **Don't use setters** - not safe for configuration changes

### Common Mistakes to Avoid

```kotlin
// ❌ WRONG - Using constructor (doesn't survive configuration changes)
class WrongFragment(private val itemId: Int) : Fragment() {
    // This will lose data on configuration change!
}

// ❌ WRONG - Using setter methods
class WrongFragment : Fragment() {
    private var itemId: Int = 0

    fun setItemId(id: Int) {
        this.itemId = id  // Lost on configuration change
    }
}

// ✅ CORRECT - Using Bundle
class CorrectFragment : Fragment() {
    companion object {
        private const val ARG_ITEM_ID = "item_id"

        fun newInstance(itemId: Int) = CorrectFragment().apply {
            arguments = Bundle().apply {
                putInt(ARG_ITEM_ID, itemId)
            }
        }
    }

    private val itemId by lazy { requireArguments().getInt(ARG_ITEM_ID) }
}
```

## Answer (RU)

Рекомендуемый способ: создать Bundle, положить туда параметры через putString или putInt и установить arguments фрагменту. В onCreate() извлечь через requireArguments(). Это безопасный способ, поддерживаемый Android-системой
