---
topic: android
tags:
  - FrameLayout
  - Jetpack Compose
  - android
  - ui
  - layouts
  - framelayout
difficulty: medium
status: draft
---

# What is the layout called where objects can overlay each other?

## Question (RU)

Как называется лейаут, в котором объекты могут наслаиваться друг на друга?

## Answer

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

## Answer (RU)

Такой тип называется FrameLayout в Android или Box в Jetpack Compose.
