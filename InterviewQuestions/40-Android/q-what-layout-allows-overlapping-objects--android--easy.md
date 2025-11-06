---
id: android-186
title: Layout Overlapping Objects / Макет для перекрывающихся объектов
aliases:
- Overlapping Layout
- Макет для перекрывания
topic: android
subtopics:
- ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-layouts
- c-view-positioning
- q-viewgroup-vs-view-differences--android--easy
- q-what-methods-redraw-views--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- android/ui-views
- difficulty/easy
- framelayout
- layouts
- ui
- view-positioning
---

# Вопрос (RU)
> Макет для перекрывающихся объектов

# Question (EN)
> Layout Overlapping Objects

---

## Ответ (RU)

## Answer (EN)

## EN (expanded)

### `FrameLayout` (Traditional Views)

In the traditional Android `View` system, **`FrameLayout`** is used for overlapping elements:

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- Background image -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background"
        android:scaleType="centerCrop" />

    <!-- Overlay text -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text"
        android:textColor="@android:color/white" />

    <!-- Badge in corner -->
    <ImageView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="8dp"
        android:src="@drawable/badge" />
</FrameLayout>
```

**Key Features:**
- Elements positioned in top-left corner by default
- Children drawn in order (last child on top)
- Use `layout_gravity` to position children
- Simple and efficient for overlays

### Box (Jetpack Compose)

In Jetpack Compose, **Box** serves the same purpose as `FrameLayout`:

```kotlin
@Composable
fun OverlayExample() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
    ) {
        // Background image
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Overlay text (center)
        Text(
            text = "Overlay Text",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center)
        )

        // Badge (top-end corner)
        Image(
            painter = painterResource(R.drawable.badge),
            contentDescription = "Badge",
            modifier = Modifier
                .size(24.dp)
                .align(Alignment.TopEnd)
                .padding(8.dp)
        )
    }
}
```

### Common Use Cases

#### 1. Image with Overlay
```kotlin
@Composable
fun ImageWithOverlay() {
    Box {
        Image(
            painter = painterResource(R.drawable.photo),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )

        // Dark overlay
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.3f))
        )

        // Content on top
        Column(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(16.dp)
        ) {
            Text("Title", color = Color.White, fontSize = 24.sp)
            Text("Subtitle", color = Color.White.copy(alpha = 0.7f))
        }
    }
}
```

#### 2. Loading Overlay
```kotlin
@Composable
fun ContentWithLoading(isLoading: Boolean) {
    Box(modifier = Modifier.fillMaxSize()) {
        // Main content
        ContentView()

        // Loading overlay
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.5f))
                    .clickable(enabled = false) { }
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            }
        }
    }
}
```

#### 3. Badge on Icon
```kotlin
@Composable
fun IconWithBadge(badgeCount: Int) {
    Box {
        Icon(
            imageVector = Icons.Default.Notifications,
            contentDescription = "Notifications",
            modifier = Modifier.size(24.dp)
        )

        if (badgeCount > 0) {
            Box(
                modifier = Modifier
                    .size(16.dp)
                    .align(Alignment.TopEnd)
                    .offset(x = 4.dp, y = (-4).dp)
                    .background(Color.Red, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "$badgeCount",
                    color = Color.White,
                    fontSize = 10.sp
                )
            }
        }
    }
}
```

#### 4. Floating Action `Button` over Content
```kotlin
@Composable
fun ScreenWithFAB() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Main content
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(50) { index ->
                Text("Item $index")
            }
        }

        // FAB
        FloatingActionButton(
            onClick = { /* action */ },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp)
        ) {
            Icon(Icons.Default.Add, contentDescription = "Add")
        }
    }
}
```

### Z-Index and Ordering

In Box, children are layered in order of declaration:

```kotlin
@Composable
fun LayeringExample() {
    Box(modifier = Modifier.size(200.dp)) {
        // Bottom layer (drawn first)
        Box(
            modifier = Modifier
                .size(150.dp)
                .background(Color.Red)
        )

        // Middle layer
        Box(
            modifier = Modifier
                .size(100.dp)
                .align(Alignment.Center)
                .background(Color.Green)
        )

        // Top layer (drawn last)
        Box(
            modifier = Modifier
                .size(50.dp)
                .align(Alignment.Center)
                .background(Color.Blue)
        )
    }
}
```

---

## RU (original)

Как называется лейаут в котором объекты могут наслаиваться друг на друга

В Android для наложения элементов используется `FrameLayout` или Box в Jetpack Compose. `FrameLayout` — контейнер, где элементы располагаются в левом верхнем углу и могут накладываться друг на друга. Box в Jetpack Compose аналогичен `FrameLayout` и также позволяет наложение элементов.


## Follow-ups

- [[c-layouts]]
- [[c-view-positioning]]
- [[q-viewgroup-vs-view-differences--android--easy]]


## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)


## Related Questions

- [[q-room-database-migrations--android--medium]]
- [[q-server-sent-events-sse--android--medium]]
- [[q-retrofit-call-adapter-advanced--networking--medium]]
