---
tags:
  - jetpack-compose
  - animations
  - navigation
  - transitions
  - shared-elements
  - hero-animations
difficulty: hard
status: draft
---

# Shared Element Transitions in Compose

# Question (EN)
> How do you implement shared element transitions between composables? Explain the SharedTransitionLayout API.

# Вопрос (RU)
> Как реализовать переходы с общими элементами между composables? Объясните API SharedTransitionLayout.

---

## Answer (EN)

**Shared Element Transitions** (also known as hero animations) create visual continuity when an element transitions between two screens. Compose 1.6+ provides the **SharedTransitionLayout** API for implementing these transitions declaratively.

---

### Basic Shared Element Transition

```kotlin
@Composable
fun SharedElementExample() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout {
        AnimatedContent(
            targetState = showDetails,
            label = "main_content"
        ) { isShowingDetails ->
            if (!isShowingDetails) {
                ListScreen(
                    onItemClick = { showDetails = true },
                    animatedVisibilityScope = this@AnimatedContent
                )
            } else {
                DetailsScreen(
                    onBack = { showDetails = false },
                    animatedVisibilityScope = this@AnimatedContent
                )
            }
        }
    }
}

@Composable
private fun SharedTransitionScope.ListScreen(
    onItemClick: () -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .clickable { onItemClick() }
    ) {
        Image(
            painter = painterResource(R.drawable.image),
            contentDescription = null,
            modifier = Modifier
                .size(100.dp)
                .sharedElement(
                    state = rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
        )
    }
}

@Composable
private fun SharedTransitionScope.DetailsScreen(
    onBack: () -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .clickable { onBack() }
    ) {
        Image(
            painter = painterResource(R.drawable.image),
            contentDescription = null,
            modifier = Modifier
                .fillMaxWidth()
                .height(300.dp)
                .sharedElement(
                    state = rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
        )
    }
}
```

---

### With Navigation Component

```kotlin
@Composable
fun SharedElementNav() {
    val navController = rememberNavController()

    SharedTransitionLayout {
        NavHost(
            navController = navController,
            startDestination = "list"
        ) {
            composable("list") {
                ListScreen(
                    onItemClick = { itemId ->
                        navController.navigate("details/$itemId")
                    },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedContentScope = this@composable
                )
            }

            composable(
                route = "details/{itemId}",
                arguments = listOf(navArgument("itemId") { type = NavType.StringType })
            ) { backStackEntry ->
                val itemId = backStackEntry.arguments?.getString("itemId")
                DetailsScreen(
                    itemId = itemId,
                    onBack = { navController.popBackStack() },
                    sharedTransitionScope = this@SharedTransitionLayout,
                    animatedContentScope = this@composable
                )
            }
        }
    }
}

@Composable
fun ListScreen(
    onItemClick: (String) -> Unit,
    sharedTransitionScope: SharedTransitionScope,
    animatedContentScope: AnimatedContentScope
) {
    LazyColumn {
        items(items) { item ->
            with(sharedTransitionScope) {
                ItemCard(
                    item = item,
                    onClick = { onItemClick(item.id) },
                    modifier = Modifier
                        .sharedElement(
                            state = rememberSharedContentState(key = "item-${item.id}"),
                            animatedVisibilityScope = animatedContentScope
                        )
                )
            }
        }
    }
}

@Composable
fun DetailsScreen(
    itemId: String?,
    onBack: () -> Unit,
    sharedTransitionScope: SharedTransitionScope,
    animatedContentScope: AnimatedContentScope
) {
    with(sharedTransitionScope) {
        Column {
            Image(
                painter = painterResource(R.drawable.image),
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .sharedElement(
                        state = rememberSharedContentState(key = "item-$itemId"),
                        animatedVisibilityScope = animatedContentScope
                    )
            )

            Text(
                "Details for $itemId",
                modifier = Modifier
                    .padding(16.dp)
                    .skipToLookaheadSize()
            )
        }
    }
}
```

---

### Multiple Shared Elements

```kotlin
@Composable
fun MultipleSharedElements() {
    var showDetails by remember { mutableStateOf(false) }

    SharedTransitionLayout {
        AnimatedContent(
            targetState = showDetails,
            label = "content"
        ) { isDetails ->
            if (!isDetails) {
                Card(
                    modifier = Modifier
                        .padding(16.dp)
                        .clickable { showDetails = true }
                ) {
                    Row {
                        Image(
                            painter = painterResource(R.drawable.avatar),
                            contentDescription = null,
                            modifier = Modifier
                                .size(64.dp)
                                .sharedElement(
                                    rememberSharedContentState(key = "avatar"),
                                    animatedVisibilityScope = this@AnimatedContent
                                )
                        )

                        Column {
                            Text(
                                "John Doe",
                                modifier = Modifier.sharedElement(
                                    rememberSharedContentState(key = "name"),
                                    animatedVisibilityScope = this@AnimatedContent
                                )
                            )

                            Text(
                                "Software Engineer",
                                modifier = Modifier.sharedElement(
                                    rememberSharedContentState(key = "title"),
                                    animatedVisibilityScope = this@AnimatedContent
                                )
                            )
                        }
                    }
                }
            } else {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .clickable { showDetails = false }
                ) {
                    Image(
                        painter = painterResource(R.drawable.avatar),
                        contentDescription = null,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp)
                            .sharedElement(
                                rememberSharedContentState(key = "avatar"),
                                animatedVisibilityScope = this@AnimatedContent
                            )
                    )

                    Text(
                        "John Doe",
                        style = MaterialTheme.typography.headlineLarge,
                        modifier = Modifier
                            .padding(16.dp)
                            .sharedElement(
                                rememberSharedContentState(key = "name"),
                                animatedVisibilityScope = this@AnimatedContent
                            )
                    )

                    Text(
                        "Software Engineer",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier
                            .padding(horizontal = 16.dp)
                            .sharedElement(
                                rememberSharedContentState(key = "title"),
                                animatedVisibilityScope = this@AnimatedContent
                            )
                    )

                    Text(
                        "Full bio text here...",
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }
        }
    }
}
```

---

### Custom Transition Specs

```kotlin
@Composable
fun CustomSharedTransition() {
    SharedTransitionLayout {
        AnimatedContent(targetState = showDetails) { isDetails ->
            Image(
                painter = painterResource(R.drawable.image),
                contentDescription = null,
                modifier = Modifier.sharedElement(
                    state = rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = this@AnimatedContent,
                    boundsTransform = { initialBounds, targetBounds ->
                        // Custom spring animation
                        spring(
                            dampingRatio = Spring.DampingRatioMediumBouncy,
                            stiffness = Spring.StiffnessLow
                        )
                    },
                    placeHolderSize = SharedTransitionScope.PlaceHolderSize.animatedSize,
                    renderInOverlayDuringTransition = true
                )
            )
        }
    }
}
```

---

### skipToLookaheadSize for Non-Shared Content

```kotlin
@Composable
fun SharedTransitionScope.DetailScreenWithSkip(
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    Column {
        Image(
            painter = painterResource(R.drawable.image),
            contentDescription = null,
            modifier = Modifier
                .sharedElement(
                    rememberSharedContentState(key = "image"),
                    animatedVisibilityScope = animatedVisibilityScope
                )
        )

        // Non-shared content: skip to final size immediately
        Text(
            "Description",
            modifier = Modifier
                .padding(16.dp)
                .skipToLookaheadSize()
        )

        // Animate bounds of non-shared content
        Text(
            "More info",
            modifier = Modifier
                .padding(16.dp)
                .animateBounds()
        )
    }
}
```

---

### Real-World Example: Image Gallery

```kotlin
data class Photo(val id: String, val url: String, val title: String)

@Composable
fun PhotoGallery() {
    var selectedPhoto by remember { mutableStateOf<Photo?>(null) }
    val photos = remember { generatePhotos() }

    SharedTransitionLayout {
        AnimatedContent(
            targetState = selectedPhoto,
            label = "photo_transition"
        ) { photo ->
            if (photo == null) {
                // Grid view
                LazyVerticalGrid(
                    columns = GridCells.Fixed(2),
                    contentPadding = PaddingValues(8.dp)
                ) {
                    items(photos, key = { it.id }) { item ->
                        PhotoGridItem(
                            photo = item,
                            onClick = { selectedPhoto = item },
                            animatedVisibilityScope = this@AnimatedContent
                        )
                    }
                }
            } else {
                // Detail view
                PhotoDetail(
                    photo = photo,
                    onClose = { selectedPhoto = null },
                    animatedVisibilityScope = this@AnimatedContent
                )
            }
        }
    }
}

@Composable
private fun SharedTransitionScope.PhotoGridItem(
    photo: Photo,
    onClick: () -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    AsyncImage(
        model = photo.url,
        contentDescription = photo.title,
        contentScale = ContentScale.Crop,
        modifier = Modifier
            .aspectRatio(1f)
            .padding(4.dp)
            .clip(RoundedCornerShape(8.dp))
            .clickable { onClick() }
            .sharedElement(
                state = rememberSharedContentState(key = "photo-${photo.id}"),
                animatedVisibilityScope = animatedVisibilityScope,
                boundsTransform = { _, _ ->
                    spring(
                        dampingRatio = Spring.DampingRatioMediumBouncy,
                        stiffness = Spring.StiffnessMedium
                    )
                }
            )
    )
}

@Composable
private fun SharedTransitionScope.PhotoDetail(
    photo: Photo,
    onClose: () -> Unit,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .clickable { onClose() }
    ) {
        Column {
            AsyncImage(
                model = photo.url,
                contentDescription = photo.title,
                contentScale = ContentScale.Fit,
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .sharedElement(
                        state = rememberSharedContentState(key = "photo-${photo.id}"),
                        animatedVisibilityScope = animatedVisibilityScope,
                        boundsTransform = { _, _ ->
                            spring(
                                dampingRatio = Spring.DampingRatioMediumBouncy,
                                stiffness = Spring.StiffnessMedium
                            )
                        }
                    )
            )

            Text(
                text = photo.title,
                color = Color.White,
                modifier = Modifier
                    .padding(16.dp)
                    .skipToLookaheadSize()
            )
        }

        IconButton(
            onClick = onClose,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
        ) {
            Icon(
                Icons.Default.Close,
                contentDescription = "Close",
                tint = Color.White
            )
        }
    }
}
```

---

### Best Practices

**1. Use unique keys:**

```kotlin
// ✅ DO: Unique keys per element
.sharedElement(
    rememberSharedContentState(key = "item-${item.id}"),
    animatedVisibilityScope = scope
)

// ❌ DON'T: Reuse keys
.sharedElement(
    rememberSharedContentState(key = "item"),
    animatedVisibilityScope = scope
)
```

**2. Handle non-shared content properly:**

```kotlin
// ✅ DO: Skip or animate non-shared content
.skipToLookaheadSize() // Skip to final size
.animateBounds() // Animate bounds
```

**3. Consider content scale:**

```kotlin
// ✅ DO: Match content scale
// Source: ContentScale.Crop
// Target: ContentScale.Fit
// Result: Smooth transition
```

**4. Use appropriate bounds transforms:**

```kotlin
// Natural motion
boundsTransform = { _, _ ->
    spring(
        dampingRatio = Spring.DampingRatioMediumBouncy,
        stiffness = Spring.StiffnessMedium
    )
}
```

---

## Ответ (RU)

**Переходы с общими элементами** (также известные как hero анимации) создают визуальную непрерывность, когда элемент переходит между двумя экранами. Compose 1.6+ предоставляет API **SharedTransitionLayout** для декларативной реализации этих переходов.

### Основной переход с общим элементом

Используйте `SharedTransitionLayout` в качестве родительского контейнера и применяйте модификатор `sharedElement` к элементам, которые должны анимироваться между экранами.

### С Navigation Component

SharedTransitionLayout можно интегрировать с Jetpack Navigation для переходов между экранами навигации.

### Несколько общих элементов

Можно анимировать несколько элементов одновременно, используя уникальные ключи для каждого общего элемента.

### Лучшие практики

1. Используйте уникальные ключи для каждого элемента
2. Правильно обрабатывайте необщий контент с помощью `skipToLookaheadSize`
3. Учитывайте масштаб контента
4. Используйте подходящие bounds transforms для естественного движения

Shared element transitions делают навигацию плавной и понятной для пользователей.
