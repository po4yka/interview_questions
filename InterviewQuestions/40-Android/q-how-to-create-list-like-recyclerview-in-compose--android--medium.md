---\
id: android-248
title: How To Create List Like RecyclerView In Compose / Как создать список как RecyclerView в Compose
aliases: [How To Create List Like RecyclerView In Compose, Как создать список как RecyclerView в Compose]
topic: android
subtopics: [ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-jetpack-compose, q-compose-core-components--android--medium, q-compose-custom-animations--android--medium, q-compose-testing--android--medium, q-how-does-jetpackcompose-work--android--medium, q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [android/ui-compose, difficulty/medium]

---\
# Вопрос (RU)
> Как создать список как `RecyclerView` в Compose

# Question (EN)
> How To Create `List` Like `RecyclerView` In Compose

---

## Ответ (RU)
В Jetpack Compose для реализации списков, аналогичных `RecyclerView` (но в Compose-среде), используются ленивые компоненты: `LazyColumn`, `LazyRow` и `LazyVerticalGrid`.

Основные идеи:
- Композируются только видимые и ближайшие к ним элементы.
- Цель та же, что и у `RecyclerView` (эффективная работа с памятью и производительностью), но вместо ручного ресайклинга `View` используется декларативная композиция и состояние.
- Идентичность элементов поддерживается с помощью стабильных ключей, а управление отображением выполняется декларативно, без адаптеров и `ViewHolder`.

### Базовый Пример LazyColumn

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

### Кастомные Элементы И Ключи

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
            key = { it.id } // стабильный уникальный ключ для корректной идентификации элементов
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
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )

            Spacer(modifier = Modifier.width(16.dp))

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

### Разные Типы Элементов

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

### Секции В Списке

```kotlin
@Composable
fun SectionedList(sections: Map<String, List<User>>) {
    LazyColumn {
        sections.forEach { (header, users) ->
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

### Пагинация (загрузка При Прокрутке К концу)

Упрощенный пример, который отслеживает позицию прокрутки и вызывает `loadMore()`, когда пользователь приближается к концу списка.

```kotlin
@Composable
fun PaginatedList(
    viewModel: ListViewModel = viewModel()
) {
    val items by viewModel.items.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val listState = rememberLazyListState()

    LazyColumn(state = listState) {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemView(item)
        }

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

    LaunchedEffect(listState, items.size, isLoading) {
        snapshotFlow { listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
            .collect { lastVisible ->
                val total = items.size
                if (!isLoading && total > 0 && lastVisible != null && lastVisible >= total - 5) {
                    viewModel.loadMore()
                }
            }
    }
}
```

### Sticky Headers

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

### LazyRow (горизонтальный список)

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
                text = "${'$'}${product.price}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}
```

### LazyVerticalGrid (сетка)

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

### Список С Анимациями Элементов

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

### Свайп Для Удаления (Material 2 пример)

Ниже используется `SwipeToDismiss` из Material 2 (`androidx.compose.material`). При использовании Material 3 следует применять соответствующие API из Material 3.

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
                confirmStateChange = { value ->
                    if (value == DismissValue.DismissedToEnd ||
                        value == DismissValue.DismissedToStart
                    ) {
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

### Управление Состоянием Прокрутки

```kotlin
@Composable
fun RememberScrollStateExample(items: List<Item>) {
    val listState = rememberLazyListState()

    LazyColumn(state = listState) {
        items(items) { item ->
            ItemView(item)
        }
    }

    LaunchedEffect(Unit) {
        listState.scrollToItem(10)
    }
}
```

### Рекомендации По Производительности

```kotlin
@Composable
fun OptimizedList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            // Используйте стабильные ключи, когда важна идентичность элементов (перестановки/обновления)
            key = { it.id }
        ) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
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

- Выносите сложные элементы в отдельные `@Composable`, чтобы уменьшить область рекомпозиции.
- Используйте стабильные `key`, когда элементы могут переставляться/вставляться/удаляться.
- Избегайте тяжелой логики и побочных эффектов внутри лямбд `items {}`, контролируйте работу со стейтом.

### Сравнение: RecyclerView Vs LazyColumn (в Compose UI)

| Возможность | `RecyclerView` | LazyColumn |
|------------|-------------|-----------|
| Адаптер | Обязателен | Не нужен, используется `items {}` DSL внутри LazyColumn |
| `ViewHolder` | Обязателен | Не нужен |
| `DiffUtil` / диффинг | Часто настраивается вручную через `DiffUtil` | Нет явного `DiffUtil`; поведение основано на декларативной композиции, `key` и идентичности элементов |
| Типы элементов | `getItemViewType()` | Условные composable / разные блоки `item` |
| Разделители | `ItemDecoration` | Компоненты `Divider` между элементами |
| Заголовки | Отдельные view-типы | `item {}` / `stickyHeader {}` |
| Анимации | `ItemAnimator`, кастомные | `AnimatedVisibility` и анимационные API Compose |
| Объем кода | Много шаблонного кода | Более декларативно и компактно |

---

## Answer (EN)
In Jetpack Compose, you use lazy layouts like `LazyColumn`, `LazyRow`, and `LazyVerticalGrid` to implement efficient scrollable lists and grids that cover the same use cases as `RecyclerView` in Compose-based UIs.

Key ideas:
- Only items that are visible or near-visible are composed.
- The goal is similar to `RecyclerView` (efficient memory/performance), but instead of manual view recycling you rely on declarative composition and state.
- Item identity is tracked via stable keys; there are no adapters or `ViewHolder`.

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
            key = { it.id } // Stable unique key improves item identity handling
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
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )

            Spacer(modifier = Modifier.width(16.dp))

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

### LazyColumn with "Load More" (pagination Trigger simplified)

Below is a simplified pattern that triggers loading more when the user scrolls near the end. It observes scroll position via `snapshotFlow`.

```kotlin
@Composable
fun PaginatedList(
    viewModel: ListViewModel = viewModel()
) {
    val items by viewModel.items.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val listState = rememberLazyListState()

    LazyColumn(state = listState) {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemView(item)
        }

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

    LaunchedEffect(listState, items.size, isLoading) {
        snapshotFlow { listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index }
            .collect { lastVisible ->
                val total = items.size
                if (!isLoading && total > 0 && lastVisible != null && lastVisible >= total - 5) {
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

### LazyRow (Horizontal `List`)

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
                text = "${'$'}${product.price}",
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

### Swipe to Delete (Material 2 API example)

The following uses `SwipeToDismiss` from Material 2 (`androidx.compose.material`). When using Material 3, use the corresponding Material 3 APIs.

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
                confirmStateChange = { value ->
                    if (value == DismissValue.DismissedToEnd ||
                        value == DismissValue.DismissedToStart
                    ) {
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

### Scroll State Management

```kotlin
@Composable
fun RememberScrollStateExample(items: List<Item>) {
    val listState = rememberLazyListState()

    LazyColumn(state = listState) {
        items(items) { item ->
            ItemView(item)
        }
    }

    LaunchedEffect(Unit) {
        listState.scrollToItem(10)
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
            // Use stable keys when item identity matters (e.g., reordering/updates)
            key = { it.id }
        ) { item ->
            ItemRow(item)
        }
    }
}

@Composable
fun ItemRow(item: Item) {
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

- Extract complex item UIs into separate `@Composable`s to reduce recomposition scope.
- Use stable `key` values when items can be reordered/inserted/removed.
- Avoid heavy work and uncontrolled side effects inside `items {}` lambdas; keep state handling explicit.

### Comparison: RecyclerView Vs LazyColumn (in Compose UIs)

| Feature | `RecyclerView` | LazyColumn |
|---------|-------------|------------|
| `Adapter` | Required | Not needed; use `items {}` DSL inside LazyColumn |
| `ViewHolder` | Required | Not needed |
| Diffing | Typically uses `DiffUtil` manually | No explicit `DiffUtil`; behavior relies on declarative composition plus `key`/item identity |
| Item types | `getItemViewType()` | Conditional composables / different `item` blocks |
| Dividers | `ItemDecoration` | `Divider` composables between items |
| Headers | Special view types | `item {}` / `stickyHeader {}` |
| Animations | `ItemAnimator`, custom | `AnimatedVisibility` / Compose animation APIs |
| Code | More boilerplate | More declarative and concise |

---

## Дополнительные Вопросы (RU)

- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-testing--android--medium]]
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]]

## Ссылки (RU)

- [Документация Android](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-compose-state]]
- [[c-jetpack-compose]]

### Хаб
- [[q-jetpack-compose-basics--android--medium]] - Базовое введение в Compose

### Похожие (Medium)
- [[q-how-does-jetpack-compose-work--android--medium]] - Как работает Compose
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Ключевые компоненты Compose
- [[q-mutable-state-compose--android--medium]] - Основы MutableState
- [[q-remember-vs-remembersaveable-compose--android--medium]] - remember vs rememberSaveable
- [[q-compose-remember-derived-state--android--medium]] - Паттерны derived state

### Продвинутое (Harder)
- [[q-compose-stability-skippability--android--hard]] - Stability и skippability
- [[q-stable-classes-compose--android--hard]] - Аннотация @Stable
- [[q-stable-annotation-compose--android--hard]] - Аннотации стабильности

---

## Follow-ups

- [[q-animated-visibility-vs-content--android--medium]]
- [[q-compose-testing--android--medium]]
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]]

## References

- [Android Documentation](https://developer.android.com/docs)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-jetpack-compose]]

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
