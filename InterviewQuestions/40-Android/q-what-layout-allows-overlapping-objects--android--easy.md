---
id: android-186
title: Layout Overlapping Objects / Макет для перекрывающихся объектов
aliases: [Overlapping Layout, Макет для перекрывания]
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
  - q-how-to-choose-layout-for-fragment--android--easy
  - q-viewgroup-vs-view-differences--android--easy
  - q-what-is-layout-types-and-when-to-use--android--easy
  - q-what-is-the-layout-called-where-objects-can-overlay-each-other--android--easy
  - q-what-methods-redraw-views--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/easy, framelayout, layouts, ui, view-positioning]

date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)
> Макет для перекрывающихся объектов

# Question (EN)
> Layout Overlapping Objects

---

## Ответ (RU)
Для перекрывающихся элементов в традиционной `View`-системе используют `FrameLayout`. В Jetpack Compose аналогичную роль играет `Box`.

## Answer (EN)
For overlapping elements in the traditional `View` system, you use `FrameLayout`. In Jetpack Compose, the equivalent is `Box`.

## RU (расширенный)

### FrameLayout (традиционная View-система)

В традиционной `View`-системе Android для перекрывающихся элементов используется `FrameLayout`:

```xml
<FrameLayout
    android:layout_width="match_parent"
    android:layout_height="200dp">

    <!-- Фоновое изображение -->
    <ImageView
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/background"
        android:scaleType="centerCrop" />

    <!-- Текст поверх -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Overlay Text"
        android:textColor="@android:color/white" />

    <!-- Бейдж в углу -->
    <ImageView
        android:layout_width="24dp"
        android:layout_height="24dp"
        android:layout_gravity="top|end"
        android:layout_margin="8dp"
        android:src="@drawable/badge" />
</FrameLayout>
```

Ключевые моменты:
- По умолчанию дочерние элементы располагаются в левом верхнем углу.
- Элементы рисуются по порядку: последний дочерний элемент отображается поверх остальных.
- Для позиционирования внутри `FrameLayout` используется `layout_gravity`.
- Подходит для оверлеев и простого наслаивания элементов.

### Box (Jetpack Compose)

В Jetpack Compose `Box` выполняет ту же роль для перекрывающихся элементов (Compose-only API):

```kotlin
@Composable
fun OverlayExample() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
    ) {
        // Фоновое изображение
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // Текст по центру поверх
        Text(
            text = "Overlay Text",
            color = Color.White,
            modifier = Modifier.align(Alignment.Center)
        )

        // Бейдж в правом верхнем углу
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

### Типичные Случаи Использования

#### 1. Изображение С Полупрозрачным Оверлеем
```kotlin
@Composable
fun ImageWithOverlay() {
    Box {
        Image(
            painter = painterResource(R.drawable.photo),
            contentDescription = null,
            modifier = Modifier.fillMaxSize()
        )

        // Темный оверлей
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.3f))
        )

        // Контент поверх
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

#### 2. Оверлей Загрузки Поверх Контента
```kotlin
@Composable
fun ContentWithLoading(isLoading: Boolean) {
    Box(modifier = Modifier.fillMaxSize()) {
        // Основной контент
        ContentView()

        // Оверлей загрузки
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

#### 3. Бейдж На Иконке
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

#### 4. Плавающая Кнопка Действия Над Контентом
```kotlin
@Composable
fun ScreenWithFAB() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Основной список
        LazyColumn(modifier = Modifier.fillMaxSize()) {
            items(50) { index ->
                Text("Item $index")
            }
        }

        // FAB поверх в правом нижнем углу
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

### Z-Index И Порядок Отрисовки

В `Box` слои располагаются в порядке объявления:

```kotlin
@Composable
fun LayeringExample() {
    Box(modifier = Modifier.size(200.dp)) {
        // Нижний слой (рисуется первым)
        Box(
            modifier = Modifier
                .size(150.dp)
                .background(Color.Red)
        )

        // Средний слой
        Box(
            modifier = Modifier
                .size(100.dp)
                .align(Alignment.Center)
                .background(Color.Green)
        )

        // Верхний слой (рисуется последним)
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

## EN (expanded)

### FrameLayout (Traditional Views)

In the traditional Android `View` system, `FrameLayout` is used for overlapping elements:

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

Key points:
- Children are positioned at the top-left corner by default.
- Children are drawn in order: the last child is on top.
- Use `layout_gravity` to position children inside the `FrameLayout`.
- Simple and efficient for overlays and stacking views.

### Box (Jetpack Compose)

In Jetpack Compose, `Box` serves a similar purpose to `FrameLayout` for overlapping elements (Compose-only API):

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

#### 4. Floating Action Button over Content
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

In `Box`, children are layered in order of declaration:

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

## Follow-ups

- [[c-layouts]]
- [[q-viewgroup-vs-view-differences--android--easy]]

## References

- [Views](https://developer.android.com/develop/ui/views)
- [Android Documentation](https://developer.android.com/docs)

## Related Questions

- [[q-room-database-migrations--android--medium]]
- [[q-server-sent-events-sse--android--medium]]
- [[q-retrofit-call-adapter-advanced--networking--medium]]
