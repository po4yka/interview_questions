---
id: android-248
title: "How To Create List Like RecyclerView In Compose / Как создать список как RecyclerView в Compose"
aliases: [How To Create List Like RecyclerView In Compose, Как создать список как RecyclerView в Compose]
topic: android
subtopics: [ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-testing--android--medium, q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-compose, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# How to Create a List like RecyclerView in Jetpack Compose?

**Russian**: Как в Jetpack Compose создать список аналогичный RecyclerView?

## Answer (EN)
In Jetpack Compose, **LazyColumn** and **LazyRow** replace RecyclerView. They efficiently create and display items on demand, similar to RecyclerView's recycling behavior.

### Basic LazyColumn

```kotlin
@Composable
fun SimpleList() {
    val items = remember { (1..100).toList() }

    LazyColumn {
        items(items) { item ->
            Text(
                text = "Item $item",
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}
```

### LazyColumn with Custom Items

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String
)

@Composable
fun UserList(users: List<User>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = users,
            key = { it.id } // Important for performance
        ) { user ->
            UserItem(user)
        }
    }
}

@Composable
fun UserItem(user: User) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Avatar
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )

            Spacer(modifier = Modifier.width(16.dp))

            // User info
            Column {
                Text(
                    text = user.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = user.email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = Color.Gray
                )
            }
        }
    }
}
```

### Different Item Types

```kotlin
sealed class ListItem {
    data class Header(val title: String) : ListItem()
    data class User(val user: UserData) : ListItem()
    data class Divider(val id: String) : ListItem()
}

@Composable
fun MixedList(items: List<ListItem>) {
    LazyColumn {
        items(
            items = items,
            key = { item ->
                when (item) {
                    is ListItem.Header -> "header_${item.title}"
                    is ListItem.User -> "user_${item.user.id}"
                    is ListItem.Divider -> "divider_${item.id}"
                }
            }
        ) { item ->
            when (item) {
                is ListItem.Header -> HeaderItem(item.title)
                is ListItem.User -> UserItem(item.user)
                is ListItem.Divider -> DividerItem()
            }
        }
    }
}

@Composable
fun HeaderItem(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.headlineSmall,
        fontWeight = FontWeight.Bold,
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.LightGray)
            .padding(16.dp)
    )
}

@Composable
fun DividerItem() {
    Divider(
        modifier = Modifier.padding(vertical = 8.dp),
        thickness = 1.dp,
        color = Color.Gray
    )
}
```

### LazyColumn with Sections

```kotlin
@Composable
fun SectionedList(sections: Map<String, List<User>>) {
    LazyColumn {
        sections.forEach { (header, users) ->
            // Section header
            item {
                Text(
                    text = header,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.primaryContainer)
                        .padding(16.dp)
                )
            }

            // Section items
            items(
                items = users,
                key = { it.id }
            ) { user ->
                UserItem(user)
            }
        }
    }
}
```

### LazyColumn with Load More

```kotlin
@Composable
fun PaginatedList(
    viewModel: ListViewModel = viewModel()
) {
    val items by viewModel.items.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemView(item)
        }

        // Loading indicator
        if (isLoading) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
        }
    }

    // Load more when reaching bottom
    LaunchedEffect(items.size) {
        snapshotFlow { items.size }
            .collect {
                if (it > 0 && !isLoading) {
                    viewModel.loadMore()
                }
            }
    }
}
```

### LazyColumn with Sticky Headers

```kotlin
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun ListWithStickyHeaders(groupedItems: Map<String, List<Item>>) {
    LazyColumn {
        groupedItems.forEach { (header, items) ->
            stickyHeader {
                Text(
                    text = header,
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.primary)
                        .padding(16.dp),
                    style = MaterialTheme.typography.titleMedium,
                    color = Color.White
                )
            }

            items(
                items = items,
                key = { it.id }
            ) { item ->
                ItemRow(item)
            }
        }
    }
}
```

### LazyRow (Horizontal List)

```kotlin
@Composable
fun HorizontalList(items: List<Product>) {
    LazyRow(
        contentPadding = PaddingValues(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = items,
            key = { it.id }
        ) { product ->
            ProductCard(product)
        }
    }
}

@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .width(160.dp)
            .height(200.dp)
    ) {
        Column(modifier = Modifier.padding(8.dp)) {
            AsyncImage(
                model = product.imageUrl,
                contentDescription = null,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(120.dp)
            )
            Text(
                text = product.name,
                style = MaterialTheme.typography.titleSmall
            )
            Text(
                text = "$${product.price}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}
```

### LazyVerticalGrid (Grid Layout)

```kotlin
@Composable
fun GridList(items: List<Item>) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            GridItemCard(item)
        }
    }
}

// Adaptive columns based on minimum width
@Composable
fun AdaptiveGrid(items: List<Item>) {
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 128.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(items, key = { it.id }) { item ->
            GridItemCard(item)
        }
    }
}
```

### List with Item Animations

```kotlin
@Composable
fun AnimatedList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            AnimatedItemRow(item)
        }
    }
}

@Composable
fun AnimatedItemRow(item: Item) {
    var isVisible by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        isVisible = true
    }

    AnimatedVisibility(
        visible = isVisible,
        enter = slideInHorizontally() + fadeIn(),
        exit = slideOutHorizontally() + fadeOut()
    ) {
        ItemRow(item)
    }
}
```

### Swipe to Delete

```kotlin
@OptIn(ExperimentalMaterialApi::class)
@Composable
fun SwipeableList(
    items: List<Item>,
    onDelete: (Item) -> Unit
) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            val dismissState = rememberDismissState(
                confirmStateChange = {
                    if (it == DismissValue.DismissedToEnd || it == DismissValue.DismissedToStart) {
                        onDelete(item)
                        true
                    } else {
                        false
                    }
                }
            )

            SwipeToDismiss(
                state = dismissState,
                background = {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(Color.Red)
                            .padding(16.dp),
                        contentAlignment = Alignment.CenterEnd
                    ) {
                        Icon(
                            imageVector = Icons.Default.Delete,
                            contentDescription = "Delete",
                            tint = Color.White
                        )
                    }
                },
                dismissContent = {
                    ItemRow(item)
                }
            )
        }
    }
}
```

### Performance Tips

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            // 1. Use stable keys for better performance
            key = { it.id }
        ) { item ->
            // 2. Extract composables to reduce recomposition scope
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
    // Stable composable with stable parameters
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(text = item.name)
        Text(text = item.description)
    }
}
```

### Comparison: RecyclerView Vs LazyColumn

| Feature | RecyclerView | LazyColumn |
|---------|-------------|------------|
| **Adapter** | Required | Not needed |
| **ViewHolder** | Required | Not needed |
| **DiffUtil** | Manual | Automatic with keys |
| **Item types** | getItemViewType() | Conditional composables |
| **Dividers** | ItemDecoration | itemsIndexed + Divider |
| **Headers** | Item type | stickyHeader {} |
| **Animations** | ItemAnimator | Built-in |
| **Code** | Verbose | Concise |

---

## RU (original)
В Jetpack Compose аналогом RecyclerView является LazyColumn и LazyRow.

**Базовое использование LazyColumn:**

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            UserItem(user)
        }
    }
}

@Composable
fun UserItem(user: User) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Text(text = user.name)
    }
}
```

**С индексами:**

```kotlin
LazyColumn {
    itemsIndexed(users) { index, user ->
        UserItem(user, index)
    }
}
```

**Разные типы элементов:**

```kotlin
LazyColumn {
    item {
        HeaderItem()
    }

    items(users) { user ->
        UserItem(user)
    }

    item {
        FooterItem()
    }
}
```

**С ключами для производительности:**

```kotlin
LazyColumn {
    items(
        items = users,
        key = { user -> user.id } // Уникальный ключ
    ) { user ->
        UserItem(user)
    }
}
```

**Sticky Headers:**

```kotlin
LazyColumn {
    groupedUsers.forEach { (category, users) ->
        stickyHeader {
            CategoryHeader(category)
        }
        items(users) { user ->
            UserItem(user)
        }
    }
}
```

**LazyGrid для сетки:**

```kotlin
LazyVerticalGrid(
    columns = GridCells.Fixed(2),
    contentPadding = PaddingValues(16.dp)
) {
    items(products) { product ->
        ProductCard(product)
    }
}
```

**Адаптивная сетка:**

```kotlin
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 128.dp)
) {
    items(photos) { photo ->
        PhotoItem(photo)
    }
}
```

**Горизонтальный список:**

```kotlin
LazyRow(
    horizontalArrangement = Arrangement.spacedBy(8.dp)
) {
    items(items) { item ->
        ItemCard(item)
    }
}
```

**Управление состоянием прокрутки:**

```kotlin
@Composable
fun RememberScrollState() {
    val listState = rememberLazyListState()

    LazyColumn(state = listState) {
        items(items) { item ->
            ItemView(item)
        }
    }

    // Прокрутить к позиции
    LaunchedEffect(Unit) {
        listState.scrollToItem(10)
    }
}
```

**Best Practices:**

1. ✅ Всегда используйте ключи для элементов списка
2. ✅ LazyColumn для вертикальных списков
3. ✅ LazyRow для горизонтальных списков
4. ✅ LazyVerticalGrid для сеток
5. ✅ Избегайте вложенных Lazy компонентов

## Follow-ups

- [[q-animated-visibility-vs-content--jetpack-compose--medium]]
- [[q-compose-testing--android--medium]]
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]]


## References

- https://developer.android.com/docs
- https://developer.android.com/develop/ui/compose


## Related Questions

### Hub
- [[q-jetpack-compose-basics--android--medium]] - Comprehensive Compose introduction

### Related (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - How Compose works
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Essential Compose components
- [[q-mutable-state-compose--android--medium]] - MutableState basics
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--android--medium]] - Derived state patterns

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability & skippability
- [[q-stable-classes-compose--android--hard]] - @Stable annotation
- [[q-stable-annotation-compose--android--hard]] - Stability annotations

