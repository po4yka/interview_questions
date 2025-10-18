---
id: 20251016-161629
title: "What Is The Layout Called Where Objects Can Overlay Each Other / Как называется layout где объекты могут перекрывать друг друга"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-compose-gesture-detection--jetpack-compose--medium, q-16kb-dex-page-size--android--medium, q-api-rate-limiting-throttling--android--medium]
created: 2025-10-15
tags: [Jetpack Compose, android, ui, layouts, framelayout, difficulty/medium]
---
# What is the layout called where objects can overlay each other?

# Вопрос (RU)

Как называется лейаут, в котором объекты могут наслаиваться друг на друга?

## Answer (EN)
In Android, there are two main approaches for creating layouts where UI elements can overlay each other: **FrameLayout** (traditional View system) and **Box** (Jetpack Compose).

### FrameLayout (Traditional View System)

`FrameLayout` is designed to display a single view, but it can hold multiple children that stack on top of each other, with the last child drawn on top.

#### Basic FrameLayout Example (XML)

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="300dp">

    <!-- Background image (bottom layer) -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background"
        android:scaleType="centerCrop" />

    <!-- Middle layer - semi-transparent overlay -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#80000000" />

    <!-- Top layer - text -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text"
        android:textColor="@android:color/white"
        android:textSize="24sp" />
</FrameLayout>
```

#### FrameLayout with Positioning

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- Base layer -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="@color/blue" />

    <!-- Top-left corner -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="top|start"
        android:layout_margin="16dp"
        android:text="Top Left" />

    <!-- Center -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Center" />

    <!-- Bottom-right corner -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:text="Bottom Right" />
</FrameLayout>
```

#### Programmatic FrameLayout

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val frameLayout = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                800
            )
        }

        // Add background image
        val imageView = ImageView(this).apply {
            setImageResource(R.drawable.background)
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        // Add overlay text
        val textView = TextView(this).apply {
            text = "Overlay Text"
            setTextColor(Color.WHITE)
            textSize = 24f
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER
            )
        }

        frameLayout.addView(imageView)
        frameLayout.addView(textView)

        setContentView(frameLayout)
    }
}
```

### Common FrameLayout Use Cases

#### 1. Image with Overlay Badge

```xml
<FrameLayout
    android:layout_width="100dp"
    android:layout_height="100dp">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/user_avatar"
        android:scaleType="centerCrop" />

    <!-- Badge overlay -->
    <TextView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="4dp"
        android:background="@drawable/circle_red"
        android:gravity="center"
        android:text="5"
        android:textColor="@android:color/white"
        android:textSize="12sp" />
</FrameLayout>
```

#### 2. Loading Overlay

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Main content -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">
        <!-- Content here -->
    </LinearLayout>

    <!-- Loading overlay -->
    <FrameLayout
        android:id="@+id/loadingOverlay"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#CC000000"
        android:visibility="gone">

        <ProgressBar
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center" />
    </FrameLayout>
</FrameLayout>
```

```kotlin
// Show/hide loading overlay
fun showLoading(show: Boolean) {
    findViewById<View>(R.id.loadingOverlay).visibility =
        if (show) View.VISIBLE else View.GONE
}
```

### Box in Jetpack Compose

`Box` is the Compose equivalent of `FrameLayout`, providing a composable that places its children on top of each other.

#### Basic Box Example

```kotlin
@Composable
fun OverlayExample() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
    ) {
        // Background layer
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize()
        )

        // Semi-transparent overlay
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.5f))
        )

        // Top layer - text
        Text(
            text = "Overlay Text",
            color = Color.White,
            fontSize = 24.sp,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

#### Box with Multiple Alignments

```kotlin
@Composable
fun MultiAlignmentBox() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .background(Color.Blue)
    ) {
        // Top-left
        Text(
            text = "Top Left",
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
        )

        // Center
        Text(
            text = "Center",
            modifier = Modifier.align(Alignment.Center)
        )

        // Bottom-right
        Text(
            text = "Bottom Right",
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        )
    }
}
```

#### Practical Compose Examples

##### Card with Badge

```kotlin
@Composable
fun BadgedProfileImage(
    imageUrl: String,
    badgeCount: Int
) {
    Box(
        modifier = Modifier.size(100.dp)
    ) {
        // Profile image
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Badge
        if (badgeCount > 0) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .align(Alignment.TopEnd)
                    .offset(x = (-4).dp, y = 4.dp)
                    .background(Color.Red, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = badgeCount.toString(),
                    color = Color.White,
                    fontSize = 12.sp
                )
            }
        }
    }
}
```

##### Loading Overlay

```kotlin
@Composable
fun ScreenWithLoading(
    isLoading: Boolean,
    content: @Composable () -> Unit
) {
    Box(modifier = Modifier.fillMaxSize()) {
        // Main content
        content()

        // Loading overlay
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.8f))
                    .clickable(enabled = false) { }, // Block interactions
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Color.White)
            }
        }
    }
}
```

##### Floating Action Button

```kotlin
@Composable
fun ContentWithFAB() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Scrollable content
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(50) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.padding(16.dp)
                )
            }
        }

        // Floating Action Button overlay
        FloatingActionButton(
            onClick = { /* Action */ },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Add,
                contentDescription = "Add"
            )
        }
    }
}
```

### Comparison: FrameLayout vs Box

| Feature | FrameLayout | Box (Compose) |
|---------|-------------|---------------|
| System | View System | Jetpack Compose |
| Definition | XML or Kotlin | Kotlin @Composable |
| Children Order | Last child on top | Last child on top |
| Alignment | `layout_gravity` | `Modifier.align()` |
| Z-index Control | Add order | Add order / `zIndex()` |

### Advanced Box Features

```kotlin
@Composable
fun AdvancedBoxExample() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Layer 1 (bottom)
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Blue)
        )

        // Layer 2 (middle) - with custom z-index
        Box(
            modifier = Modifier
                .size(200.dp)
                .align(Alignment.Center)
                .zIndex(1f) // Explicit z-ordering
                .background(Color.Green)
        )

        // Layer 3 (top by default)
        Box(
            modifier = Modifier
                .size(100.dp)
                .align(Alignment.Center)
                .background(Color.Red)
        )
    }
}
```

### Summary

- **FrameLayout** (View System): Simple container for overlaying views
- **Box** (Jetpack Compose): Modern declarative approach for stacking composables
- Both place children on top of each other in the order they are added
- Use `layout_gravity` (FrameLayout) or `Modifier.align()` (Box) for positioning
- Common uses: badges, overlays, floating buttons, loading indicators

## Ответ (RU)

В Android существует два основных подхода для создания макетов, где элементы интерфейса могут накладываться друг на друга: **FrameLayout** (традиционная система View) и **Box** (Jetpack Compose).

### FrameLayout (Традиционная система View)

`FrameLayout` предназначен для отображения одного view, но может содержать несколько дочерних элементов, которые накладываются друг на друга, при этом последний дочерний элемент рисуется сверху.

#### Основной пример FrameLayout (XML)

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="300dp">

    <!-- Фоновое изображение (нижний слой) -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background"
        android:scaleType="centerCrop" />

    <!-- Средний слой - полупрозрачное наложение -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#80000000" />

    <!-- Верхний слой - текст -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text"
        android:textColor="@android:color/white"
        android:textSize="24sp" />
</FrameLayout>
```

#### FrameLayout с позиционированием

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- Базовый слой -->
    <View
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="@color/blue" />

    <!-- Верхний левый угол -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="top|start"
        android:layout_margin="16dp"
        android:text="Top Left" />

    <!-- Центр -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Center" />

    <!-- Правый нижний угол -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="bottom|end"
        android:layout_margin="16dp"
        android:text="Bottom Right" />
</FrameLayout>
```

#### Программное создание FrameLayout

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val frameLayout = FrameLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                800
            )
        }

        // Добавление фонового изображения
        val imageView = ImageView(this).apply {
            setImageResource(R.drawable.background)
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
            )
        }

        // Добавление текста поверх
        val textView = TextView(this).apply {
            text = "Overlay Text"
            setTextColor(Color.WHITE)
            textSize = 24f
            layoutParams = FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT,
                Gravity.CENTER
            )
        }

        frameLayout.addView(imageView)
        frameLayout.addView(textView)

        setContentView(frameLayout)
    }
}
```

### Типичные случаи использования FrameLayout

#### 1. Изображение со значком

```xml
<FrameLayout
    android:layout_width="100dp"
    android:layout_height="100dp">

    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/user_avatar"
        android:scaleType="centerCrop" />

    <!-- Значок поверх изображения -->
    <TextView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="4dp"
        android:background="@drawable/circle_red"
        android:gravity="center"
        android:text="5"
        android:textColor="@android:color/white"
        android:textSize="12sp" />
</FrameLayout>
```

#### 2. Оверлей загрузки

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Основной контент -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical">
        <!-- Контент здесь -->
    </LinearLayout>

    <!-- Оверлей загрузки -->
    <FrameLayout
        android:id="@+id/loadingOverlay"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#CC000000"
        android:visibility="gone">

        <ProgressBar
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center" />
    </FrameLayout>
</FrameLayout>
```

```kotlin
// Показать/скрыть оверлей загрузки
fun showLoading(show: Boolean) {
    findViewById<View>(R.id.loadingOverlay).visibility =
        if (show) View.VISIBLE else View.GONE
}
```

### Box в Jetpack Compose

`Box` — это эквивалент `FrameLayout` в Compose, предоставляющий composable-элемент, который размещает своих потомков друг поверх друга.

#### Основной пример Box

```kotlin
@Composable
fun OverlayExample() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
    ) {
        // Фоновый слой
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize()
        )

        // Полупрозрачное наложение
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.5f))
        )

        // Верхний слой - текст
        Text(
            text = "Overlay Text",
            color = Color.White,
            fontSize = 24.sp,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}
```

#### Box с несколькими выравниваниями

```kotlin
@Composable
fun MultiAlignmentBox() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .background(Color.Blue)
    ) {
        // Верхний левый
        Text(
            text = "Top Left",
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
        )

        // Центр
        Text(
            text = "Center",
            modifier = Modifier.align(Alignment.Center)
        )

        // Правый нижний
        Text(
            text = "Bottom Right",
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        )
    }
}
```

#### Практические примеры в Compose

##### Карточка со значком

```kotlin
@Composable
fun BadgedProfileImage(
    imageUrl: String,
    badgeCount: Int
) {
    Box(
        modifier = Modifier.size(100.dp)
    ) {
        // Изображение профиля
        AsyncImage(
            model = imageUrl,
            contentDescription = "Profile",
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Значок
        if (badgeCount > 0) {
            Box(
                modifier = Modifier
                    .size(24.dp)
                    .align(Alignment.TopEnd)
                    .offset(x = (-4).dp, y = 4.dp)
                    .background(Color.Red, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = badgeCount.toString(),
                    color = Color.White,
                    fontSize = 12.sp
                )
            }
        }
    }
}
```

##### Оверлей загрузки

```kotlin
@Composable
fun ScreenWithLoading(
    isLoading: Boolean,
    content: @Composable () -> Unit
) {
    Box(modifier = Modifier.fillMaxSize()) {
        // Основной контент
        content()

        // Оверлей загрузки
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.8f))
                    .clickable(enabled = false) { }, // Блокировать взаимодействия
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Color.White)
            }
        }
    }
}
```

##### Плавающая кнопка действия

```kotlin
@Composable
fun ContentWithFAB() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Прокручиваемый контент
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(50) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.padding(16.dp)
                )
            }
        }

        // Плавающая кнопка действия поверх контента
        FloatingActionButton(
            onClick = { /* Действие */ },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Add,
                contentDescription = "Add"
            )
        }
    }
}
```

### Сравнение: FrameLayout vs Box

| Характеристика | FrameLayout | Box (Compose) |
|---------|-------------|---------------|
| Система | View System | Jetpack Compose |
| Определение | XML или Kotlin | Kotlin @Composable |
| Порядок потомков | Последний сверху | Последний сверху |
| Выравнивание | `layout_gravity` | `Modifier.align()` |
| Управление Z-index | Порядок добавления | Порядок добавления / `zIndex()` |

### Расширенные возможности Box

```kotlin
@Composable
fun AdvancedBoxExample() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Слой 1 (снизу)
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Blue)
        )

        // Слой 2 (средний) - с пользовательским z-index
        Box(
            modifier = Modifier
                .size(200.dp)
                .align(Alignment.Center)
                .zIndex(1f) // Явное упорядочивание по z
                .background(Color.Green)
        )

        // Слой 3 (сверху по умолчанию)
        Box(
            modifier = Modifier
                .size(100.dp)
                .align(Alignment.Center)
                .background(Color.Red)
        )
    }
}
```

### Резюме

- **FrameLayout** (View System): простой контейнер для наложения view
- **Box** (Jetpack Compose): современный декларативный подход для наложения composable-элементов
- Оба размещают потомков друг поверх друга в порядке их добавления
- Используйте `layout_gravity` (FrameLayout) или `Modifier.align()` (Box) для позиционирования
- Типичные применения: значки, оверлеи, плавающие кнопки, индикаторы загрузки

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-testing-viewmodels-turbine--testing--medium]] - View
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- [[q-rxjava-pagination-recyclerview--android--medium]] - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--jetpack-compose--hard]] - View
