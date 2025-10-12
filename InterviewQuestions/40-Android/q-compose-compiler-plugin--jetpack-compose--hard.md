---
tags:
  - jetpack-compose
  - compiler
  - internals
  - plugin
  - kotlin-compiler
difficulty: hard
status: draft
---

# Compose Compiler Plugin Transformations

# Question (EN)
> What transformations does the Compose compiler plugin apply to @Composable functions? Explain the role of the Composer parameter.

# Вопрос (RU)
> Какие трансформации применяет плагин компилятора Compose к @Composable функциям? Объясните роль параметра Composer.

---

## Answer (EN)

The **Compose Compiler Plugin** is a Kotlin compiler plugin that transforms `@Composable` functions to enable Compose's reactive runtime. It adds hidden parameters, wraps code in groups, and generates tracking logic for efficient recomposition.

### Key Transformations

The compiler plugin performs these major transformations:

1. **Adds hidden parameters** (`$composer`, `$changed`)
2. **Wraps function body** in start/end restart groups
3. **Generates change tracking** logic
4. **Creates restart lambdas** for recomposition
5. **Transforms control flow** to track composition

---

### The $composer Parameter

Every `@Composable` function receives a hidden **`$composer: Composer`** parameter - the bridge to Compose's runtime.

**Your code:**

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name!")
}
```

**After compiler transformation:**

```kotlin
@Composable
fun Greeting(
    name: String,
    $composer: Composer,      // Hidden parameter 1
    $changed: Int             // Hidden parameter 2
) {
    $composer = $composer.startRestartGroup(123)

    if ($changed and 0b0001 === 0) {
        $composer.skipToGroupEnd()
    } else {
        Text("Hello, $name!", $composer, 0)
    }

    $composer.endRestartGroup()?.updateScope { next$composer, next$changed ->
        Greeting(name, next$composer, next$changed or 0b0001)
    }
}
```

---

### What is the Composer?

The `Composer` is the runtime interface that:
- **Writes to the Slot Table** (stores state and structure)
- **Tracks state reads** (registers observers)
- **Manages recomposition** (invalidation and scheduling)
- **Handles control flow** (groups, keys, effects)

```kotlin
// Simplified Composer interface
interface Composer {
    // Group management
    fun startRestartGroup(key: Int): Composer
    fun endRestartGroup(): ScopeUpdateScope?
    fun startReplaceableGroup(key: Int)
    fun endReplaceableGroup()

    // State and remembering
    fun <T> cache(invalid: Boolean, block: () -> T): T
    fun rememberedValue(): Any?
    fun updateRememberedValue(value: Any?)

    // Change tracking
    fun changed(value: Any?): Boolean
    fun skipToGroupEnd()
    fun skipCurrentGroup()

    // Materialization
    fun <T> startNode(): T
    fun endNode()
    fun useNode()
}
```

---

### Transformation Deep Dive

#### 1. Basic Function Transformation

**Original:**

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

**Transformed (simplified):**

```kotlin
@Composable
fun Counter($composer: Composer, $changed: Int) {
    $composer = $composer.startRestartGroup(keyHash)

    // remember transformation
    val count = $composer.cache($changed == 0) {
        mutableStateOf(0)
    }

    // Button call with hidden parameters
    Button(
        onClick = { count.value++ },
        $composer = $composer,
        $changed = 0
    ) {
        // Lambda also receives composer
        Text(
            text = "Count: ${count.value}",
            $composer = $composer,
            $changed = 0
        )
    }

    val scope = $composer.endRestartGroup()
    scope?.updateScope { next$composer, _ ->
        Counter(next$composer, $changed or 0b0001)
    }
}
```

---

#### 2. Parameter Change Tracking ($changed)

The `$changed` parameter is a bitfield tracking which parameters have changed:

```kotlin
@Composable
fun UserCard(
    name: String,      // bit 0
    age: Int,          // bit 1
    email: String,     // bit 2
    $composer: Composer,
    $changed: Int
) {
    // Check if name changed
    val nameChanged = $changed and 0b0001 !== 0

    // Check if age changed
    val ageChanged = $changed and 0b0010 !== 0

    // Check if email changed
    val emailChanged = $changed and 0b0100 !== 0

    // Skip recomposition if nothing changed
    if ($changed and 0b0111 === 0 && $composer.skipping) {
        $composer.skipToGroupEnd()
        return
    }

    // ... actual composable body
}
```

**Bitfield encoding:**

```
$changed = 0b00000101
           ││││││││
           │││││││└─ bit 0: name changed
           ││││││└── bit 1: age unchanged
           │││││└─── bit 2: email changed
           ││││└──── bit 3-6: reserved
           │││└───── bit 7: uncertain/default params
```

---

#### 3. Restart Groups

**Restart groups** define recomposition boundaries:

```kotlin
@Composable
fun Parent() {
    var state by remember { mutableStateOf(0) }

    // Group 1: restart boundary
    Child1(state)

    // Group 2: another restart boundary
    Child2()
}
```

**Transformed:**

```kotlin
@Composable
fun Parent($composer: Composer, $changed: Int) {
    $composer.startRestartGroup(keyHash)

    val state = $composer.cache { mutableStateOf(0) }

    // Child1 gets its own restart group
    Child1(
        state = state.value,
        $composer = $composer,
        $changed = 0
    )

    // Child2 gets its own restart group
    Child2($composer = $composer, $changed = 0)

    val scope = $composer.endRestartGroup()
    scope?.updateScope { next$composer, _ ->
        Parent(next$composer, $changed or 0b0001)
    }
}
```

When `state` changes:
1. `Parent` is invalidated
2. `updateScope` lambda is called
3. Only `Parent` and `Child1` recompose
4. `Child2` is skipped (no parameter changes)

---

#### 4. Control Flow Transformation

**If/else branches:**

```kotlin
@Composable
fun Conditional(show: Boolean) {
    if (show) {
        Text("Visible")
    } else {
        Text("Hidden")
    }
}
```

**Transformed:**

```kotlin
@Composable
fun Conditional(
    show: Boolean,
    $composer: Composer,
    $changed: Int
) {
    $composer.startRestartGroup(keyHash)

    if (show) {
        $composer.startReplaceableGroup(keyHash1)
        Text("Visible", $composer, 0)
        $composer.endReplaceableGroup()
    } else {
        $composer.startReplaceableGroup(keyHash2)
        Text("Hidden", $composer, 0)
        $composer.endReplaceableGroup()
    }

    $composer.endRestartGroup()
}
```

Each branch gets a **replaceable group** to track which branch is active.

---

#### 5. Remember Transformation

```kotlin
@Composable
fun Example() {
    val value = remember { expensiveOperation() }
}
```

**Transformed:**

```kotlin
@Composable
fun Example($composer: Composer, $changed: Int) {
    $composer.startRestartGroup(keyHash)

    val value = $composer.cache(
        invalid = $changed and 0b0001 == 0
    ) {
        expensiveOperation()
    }

    $composer.endRestartGroup()
}
```

The `cache` function:
1. Checks if value exists in Slot Table
2. If yes and still valid, returns cached value
3. If no or invalid, runs lambda and stores result

---

#### 6. Key Transformation

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    items.forEach { item ->
        key(item.id) {
            ItemView(item)
        }
    }
}
```

**Transformed:**

```kotlin
@Composable
fun ItemList(
    items: List<Item>,
    $composer: Composer,
    $changed: Int
) {
    $composer.startRestartGroup(keyHash)

    items.forEach { item ->
        $composer.startMovableGroup(
            key = item.id,  // Stable identity
            dataKey = item.id
        )

        ItemView(
            item = item,
            $composer = $composer,
            $changed = 0
        )

        $composer.endMovableGroup()
    }

    $composer.endRestartGroup()
}
```

**Movable groups** allow Compose to track identity across reorderings.

---

### Real-World Example: Complete Transformation

**Original code:**

```kotlin
@Composable
fun UserProfile(
    user: User,
    onEdit: () -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    Card {
        Column {
            Text(user.name)

            if (expanded) {
                Text(user.email)
                Button(onClick = onEdit) {
                    Text("Edit")
                }
            }

            Button(onClick = { expanded = !expanded }) {
                Text(if (expanded) "Collapse" else "Expand")
            }
        }
    }
}
```

**Transformed (simplified):**

```kotlin
@Composable
fun UserProfile(
    user: User,
    onEdit: () -> Unit,
    $composer: Composer,
    $changed: Int
) {
    $composer = $composer.startRestartGroup(keyHash = 123456)

    // Change tracking
    val dirty = $changed
    if ($changed and 0b0110 === 0) {
        dirty = dirty or if ($composer.changed(user)) 0b0010 else 0b0001
        dirty = dirty or if ($composer.changed(onEdit)) 0b1000 else 0b0100
    }

    // Skip if possible
    if (dirty and 0b1011 === 0 && $composer.skipping) {
        $composer.skipToGroupEnd()
        return
    }

    // Remember expanded state
    val expanded$delegate = $composer.cache(
        invalid = $changed and 0b0001 == 0
    ) {
        mutableStateOf(false)
    }

    // Card composable
    Card($composer = $composer, $changed = 0) {
        Column($composer = $composer, $changed = 0) {
            Text(
                text = user.name,
                $composer = $composer,
                $changed = 0
            )

            // Conditional group
            if (expanded$delegate.value) {
                $composer.startReplaceableGroup(keyHash1)

                Text(
                    text = user.email,
                    $composer = $composer,
                    $changed = 0
                )

                Button(
                    onClick = onEdit,
                    $composer = $composer,
                    $changed = 0
                ) {
                    Text("Edit", $composer, 0)
                }

                $composer.endReplaceableGroup()
            } else {
                $composer.startReplaceableGroup(keyHash2)
                $composer.endReplaceableGroup()
            }

            // Toggle button
            Button(
                onClick = {
                    expanded$delegate.value = !expanded$delegate.value
                },
                $composer = $composer,
                $changed = 0
            ) {
                val text = if (expanded$delegate.value) "Collapse" else "Expand"
                Text(text, $composer, 0)
            }
        }
    }

    val scope = $composer.endRestartGroup()
    scope?.updateScope { next$composer, next$changed ->
        UserProfile(
            user = user,
            onEdit = onEdit,
            $composer = next$composer,
            $changed = next$changed or 0b0001
        )
    }
}
```

---

### Viewing Transformed Code

**Method 1: Compose Compiler Reports**

```gradle
// build.gradle.kts
android {
    kotlinOptions {
        freeCompilerArgs += listOf(
            "-P",
            "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=" +
                "${project.buildDir}/compose_compiler"
        )
    }
}
```

**Method 2: Decompile with Android Studio**

1. Build your project
2. Tools → Kotlin → Show Kotlin Bytecode
3. Click "Decompile"
4. Search for your `@Composable` function

**Method 3: Compose Compiler Gradle Plugin**

```gradle
plugins {
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.0"
}

composeCompiler {
    enableMetricsProvider = true
    enableReportsProvider = true
    reportsDestination = layout.buildDirectory.dir("compose_compiler")
}
```

---

### Compiler Report Example

```
restartable skippable scheme("[androidx.compose.ui.UiComposable]")
fun Counter(
  stable %composer: Composer?,
  stable %changed: Int
)
  %composer = %composer.startRestartGroup(<>)
  sourceInformation(%composer, "C(Counter):Counter.kt#2487m")
  if (%changed !== 0 || !%composer.skipping) {
    val tmp0_remember = remember({
      mutableStateOf(0)
    }, %composer, 0)
    Button({ tmp0_remember.value = tmp0_remember.value + 1 }, null, false,
      null, null, null, null, null, ComposableLambda(<>, %composer, 54) {
        %composer: Composer?,
        %changed: Int
        ->
        Text("Count: %{tmp0_remember.value}", null, <unsafe-coerce>(0),
          <unsafe-coerce>(0), null, null, null, <unsafe-coerce>(0), null,
          null, <unsafe-coerce>(0), false, 0, 0, null, null, %composer, 0, 0,
          65534)
      }, %composer, 0b0110000000000000000000110000, 510)
  } else {
    %composer.skipToGroupEnd()
  }
  %composer.endRestartGroup()?.updateScope { %composer: Composer?, %force: Int ->
    Counter(%composer, %changed or 0b0001)
  }
```

---

### Performance Implications

**1. Smart Recomposition:**

```kotlin
@Composable
fun ExpensiveList(
    items: List<String>,
    selected: String
) {
    items.forEach { item ->
        // Only recomposes when item == selected changes
        ListItem(
            text = item,
            selected = item == selected
        )
    }
}
```

The compiler tracks that each `ListItem` depends only on its specific `item` and whether `item == selected`.

**2. Skipping Optimization:**

```kotlin
@Composable
fun SkippableItem(
    name: String,  // Stable
    count: Int     // Stable
) {
    // If name and count haven't changed:
    // $composer.skipping == true
    // → entire function skipped
}
```

**3. Change Propagation:**

```kotlin
@Composable
fun Parent() {
    var state by remember { mutableStateOf(0) }

    // Only Child1 recomposes when state changes
    Child1(state)
    Child2() // Skipped
}
```

---

### Advanced: Non-Restartable Composables

Some composables are **non-restartable** (can't be individually recomposed):

```kotlin
@Composable
@NonRestartableComposable
inline fun InlineComposable(content: @Composable () -> Unit) {
    content()
}
```

**Why:**
- Inline functions don't have their own frame
- Can't create restart scope
- Always recompose with parent

**Transformed:**

```kotlin
@Composable
@NonRestartableComposable
inline fun InlineComposable(
    content: @Composable () -> Unit,
    $composer: Composer,
    $changed: Int
) {
    // No startRestartGroup/endRestartGroup
    content($composer, 0)
    // No updateScope
}
```

---

### Best Practices

**1. Trust the compiler:**

```kotlin
// ✅ DO: Let compiler handle parameters
@Composable
fun MyComposable(data: Data) {
    // Compiler automatically tracks changes
}

// ❌ DON'T: Manually track changes
@Composable
fun MyComposable(data: Data) {
    var cached by remember { mutableStateOf(data) }
    if (cached != data) cached = data // Unnecessary!
}
```

**2. Understand skippability:**

```kotlin
// Compiler can skip this
@Composable
fun Skippable(name: String) {
    Text(name)
}

// Compiler CANNOT skip this (unstable parameter)
data class User(var name: String)

@Composable
fun NotSkippable(user: User) {
    Text(user.name)
}
```

**3. Use composition locals efficiently:**

```kotlin
// ✅ DO: Compiler tracks composition local reads
@Composable
fun UseLocal() {
    val value = LocalValue.current
    Text(value)
}

// ❌ DON'T: Reading in multiple places
@Composable
fun IneffcientLocal() {
    Text(LocalValue.current) // Read 1
    Text(LocalValue.current) // Read 2
}
```

---

### Debugging Compiler Issues

**Enable compiler metrics:**

```gradle
composeCompiler {
    enableMetricsProvider = true
    stabilityConfigurationFile = rootProject.layout.projectDirectory.file("stability_config.conf")
}
```

**stability_config.conf:**

```
// Mark specific classes as stable
com.example.User
com.example.data.*
```

**Check generated reports:**

```bash
# View skippability report
cat build/compose_compiler/app_debug-module.json

# Check for unstable parameters
grep "unstable" build/compose_compiler/*.txt
```

---

## Ответ (RU)

**Плагин компилятора Compose** — это плагин компилятора Kotlin, который трансформирует `@Composable` функции для работы с реактивной средой выполнения Compose. Он добавляет скрытые параметры, оборачивает код в группы и генерирует логику отслеживания для эффективной перекомпозиции.

### Ключевые трансформации

Компилятор выполняет следующие основные трансформации:

1. **Добавляет скрытые параметры** (`$composer`, `$changed`)
2. **Оборачивает тело функции** в start/end restart группы
3. **Генерирует логику отслеживания** изменений
4. **Создает restart лямбды** для перекомпозиции
5. **Трансформирует поток управления** для отслеживания композиции

### Параметр $composer

Каждая `@Composable` функция получает скрытый параметр **`$composer: Composer`** - мост к runtime Compose.

**Ваш код:**

```kotlin
@Composable
fun Greeting(name: String) {
    Text("Hello, $name!")
}
```

**После трансформации компилятора:**

```kotlin
@Composable
fun Greeting(
    name: String,
    $composer: Composer,      // Скрытый параметр 1
    $changed: Int             // Скрытый параметр 2
) {
    $composer = $composer.startRestartGroup(123)

    if ($changed and 0b0001 === 0) {
        $composer.skipToGroupEnd()
    } else {
        Text("Hello, $name!", $composer, 0)
    }

    $composer.endRestartGroup()?.updateScope { next$composer, next$changed ->
        Greeting(name, next$composer, next$changed or 0b0001)
    }
}
```

### Что такое Composer?

`Composer` — это интерфейс runtime, который:
- **Пишет в Slot Table** (хранит состояние и структуру)
- **Отслеживает чтения состояния** (регистрирует наблюдателей)
- **Управляет перекомпозицией** (инвалидация и планирование)
- **Обрабатывает поток управления** (группы, ключи, эффекты)

### Отслеживание изменений параметров

Параметр `$changed` — это битовое поле, отслеживающее, какие параметры изменились. Компилятор использует его для определения, можно ли пропустить перекомпозицию.

### Restart группы

**Restart группы** определяют границы перекомпозиции. Когда состояние изменяется, перекомпонуются только затронутые группы.

### Трансформация управляющих конструкций

Компилятор оборачивает ветки if/else и циклы в специальные группы для отслеживания, какая ветвь активна.

### Просмотр трансформированного кода

Используйте Compose Compiler Reports или декомпилируйте байткод в Android Studio для просмотра трансформированного кода.

Понимание этих трансформаций помогает писать более эффективные Compose функции и отлаживать проблемы с производительностью.


---

## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Slot table internals
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

