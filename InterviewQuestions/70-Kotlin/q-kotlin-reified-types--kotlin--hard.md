---
topic: kotlin
tags:
  - kotlin
  - reified
  - generics
  - type-parameters
  - inline
difficulty: hard
status: draft
---

# Reified Type Parameters

**English**: Explain reified type parameters. Implement type-safe builders and factories using reified. What are the limitations?

**Russian**: Объясните reified type parameters. Реализуйте type-safe builders и factories используя reified. Каковы ограничения?

## Answer (EN)

Reified type parameters preserve type information at runtime in inline functions, overcoming Java's type erasure.

### Problem: Type Erasure

```kotlin
// Doesn't work - type erased at runtime
fun <T> isInstance(value: Any): Boolean {
    return value is T  //  Cannot check type T
}

// Workaround: Pass class explicitly
fun <T> isInstance(value: Any, clazz: Class<T>): Boolean {
    return clazz.isInstance(value)  //  Works but verbose
}
```

### Solution: Reified

```kotlin
// Reified - type available at runtime
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  //  Works!
}

// Usage
isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false
```

### Type-Safe JSON Parsing

```kotlin
inline fun <reified T> String.parseJson(): T {
    return Json.decodeFromString<T>(this)
}

// Usage
val user: User = jsonString.parseJson()
val users: List<User> = jsonString.parseJson()
```

### Fragment/Activity Creation

```kotlin
inline fun <reified T : Fragment> newFragment(args: Bundle? = null): T {
    return T::class.java.newInstance().apply {
        arguments = args
    }
}

// Usage
val fragment = newFragment<UserFragment>()

// Type-safe Intent
inline fun <reified T : Activity> Context.startActivity(extras: Bundle? = null) {
    val intent = Intent(this, T::class.java).apply {
        extras?.let { putExtras(it) }
    }
    startActivity(intent)
}

// Usage
context.startActivity<MainActivity>()
```

### ViewModel Factory

```kotlin
inline fun <reified VM : ViewModel> Fragment.viewModels(
    noinline factoryProducer: (() -> ViewModelProvider.Factory)? = null
): Lazy<VM> {
    return ViewModelLazy(
        VM::class,
        { viewModelStore },
        factoryProducer ?: { defaultViewModelProviderFactory }
    )
}

// Usage
class MyFragment : Fragment() {
    val viewModel: MyViewModel by viewModels()
}
```

### Type-Safe Builder

```kotlin
inline fun <reified T> buildList(builder: MutableList<T>.() -> Unit): List<T> {
    return mutableListOf<T>().apply(builder)
}

// Usage
val strings = buildList<String> {
    add("a")
    add("b")
    // add(1)  //  Compile error
}
```

### Limitations

1. **Must be inline function**
2. **Cannot be used in class type parameters**
3. **Cannot be passed to non-inline functions**
4. **Increases bytecode size** (inlining)
5. **Cannot create instances** without reflection

```kotlin
//  NOT ALLOWED
class Container<reified T>  // Can't use in class

fun <reified T> create(): T = T()  // Can't create instance

inline fun <reified T> process() {
    nonInlineFunction<T>()  // Can't pass to non-inline
}
```

### Best Practices

1. **Use for type checks and casts**
2. **Keep inline functions small**
3. **Document performance impact**
4. **Prefer explicit Class<T> for Android APIs**
5. **Test bytecode size impact**

## Ответ (RU)

Reified type parameters сохраняют информацию о типе в runtime в inline функциях, преодолевая type erasure Java.

[Полные примеры type-safe JSON parsing, Fragment creation, ViewModel factory и builders приведены в английском разделе]

### Ограничения

1. **Должна быть inline функция**
2. **Нельзя использовать в class type parameters**
3. **Нельзя передать в non-inline функции**
4. **Увеличивает размер bytecode**
5. **Нельзя создать экземпляр** без reflection
