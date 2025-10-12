---
topic: android
tags:
  - android
  - compose
  - compositionlocal
  - state-management
  - implicit-data
  - difficulty/hard
subtopics:
  - ui-compose
  - ui-state
difficulty: hard
status: draft
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20CompositionLocal.md
---

# CompositionLocal in Jetpack Compose / CompositionLocal в Jetpack Compose

**English**: What do you know about CompositionLocal?

**Russian**: Что вы знаете о CompositionLocal?

## Answer (EN)
Usually in Compose, data flows down through the UI tree as parameters to each composable function. This makes a composable's dependencies explicit. This can however be cumbersome for data that is very frequently and widely used such as colors or type styles. See the following example:

```kotlin
@Composable
fun MyApp() {
    // Theme information tends to be defined near the root of the application
    val colors = colors()
}

// Some composable deep in the hierarchy
@Composable
fun SomeTextLabel(labelText: String) {
    Text(
        text = labelText,
        color = colors.onPrimary // ← need to access colors here
    )
}
```

To support not needing to pass the colors as an explicit parameter dependency to most composables, **Compose offers** `CompositionLocal` **which allows you to create tree-scoped named objects that can be used as an implicit way to have data flow through the UI tree**.

`CompositionLocal` elements are usually provided with a value in a certain node of the UI tree. That value can be used by its composable descendants without declaring the `CompositionLocal` as a parameter in the composable function.

## Example of usage

```kotlin
data class UserPreferences(val isDarkModeEnabled: Boolean, val fontSize: Float)

// Define a dynamic Composition Local with default preferences
val LocalUserPreferences = compositionLocalOf {
    UserPreferences(isDarkModeEnabled = false, fontSize = 14f)
}

@Composable
fun PreferencesProvider(content: @Composable () -> Unit) {
    var isDarkMode by remember { mutableStateOf(false) }
    val preferences = UserPreferences(isDarkMode, 16f)
    CompositionLocalProvider(LocalUserPreferences provides preferences) {
        content()
    }
}

@Composable
fun SettingsScreen() {
    val preferences = LocalUserPreferences.current
    Text("Dark Mode: ${if (preferences.isDarkModeEnabled) "Enabled" else "Disabled"}")
}
```

### Explanation

- **Definition**: The `UserPreferences` data class holds dynamic user settings;
- **Provision**: The `PreferencesProvider` dynamically updates and provides the preferences based on the user's actions;
- **Consumption**: The `SettingsScreen` consumes and displays the preferences, updating reactively when changes occur.

## Key Concepts and Benefits of CompositionLocal

### Implicit Sharing

`CompositionLocal` enables data to be shared across composables without explicitly passing it as a parameter. This allows easier management of globally relevant data, such as theme styles, user settings, or app-wide configurations.

### Localized Context

`CompositionLocal` allows for different parts of the UI to have their own context, which can vary depending on the scope in which the `CompositionLocal` is provided. This is useful for customizing different sections of the UI while maintaining overall consistency.

### Reactivity

For dynamic values, `CompositionLocal` can trigger recompositions when its value changes. This means that when a value is updated, only the parts of the UI that depend on this value will be recomposed, keeping the UI efficient and responsive.

### Decoupled Components

`CompositionLocal` decouples UI components from their direct dependencies. This enhances the modularity and reusability of composables, as they don't need to be aware of the specific data provided higher in the composition tree. This makes testing and reusing components easier.

## Why Are Composition Locals Important?

### Reduced Boilerplate

Provide data once at a higher level, consume it wherever necessary.

### Better Encapsulation

Intermediate composables don't need to manage data they don't directly use.

### Easier Testing

You can override Composition Locals in tests without changing public APIs.

### Scoped Values

Data is only available to composables within the specific composition scope.

## Types of CompositionLocal Providers

Jetpack Compose offers two APIs to create a `CompositionLocal`, each suited to different scenarios:

### compositionLocalOf

**Fine-grained Control**: This API allows fine control over recompositions. When the value changes, only the parts of the UI that read this value are recomposed. This makes it ideal for frequently changing data like dynamic themes or user preferences.

**Use Case**: Situations where data changes regularly, such as dynamic UI themes, localization settings, or user-specific configurations.

```kotlin
val LocalTheme = compositionLocalOf { LightTheme }
```

### staticCompositionLocalOf

**Static Data Handling**: In contrast to `compositionLocalOf`, Compose does not track the places where `staticCompositionLocalOf` is read. When the value changes, the entire content block where the `CompositionLocal` is provided gets recomposed, instead of just the places where the `current` value is read in the Composition. It is best used for data that rarely changes.

**Use Case**: Suitable for stable configurations like API endpoints, debug flags, or static UI themes that remain constant during the app lifecycle.

```kotlin
val LocalApiEndpoint = staticCompositionLocalOf { "https://api.example.com" }
```

If the value provided to the `CompositionLocal` is highly unlikely to change or will never change, use `staticCompositionLocalOf` to get performance benefits.

## What Composition Locals Are (and Aren't)

### Are For:

- Design system tokens (themes, spacing, typography);
- UI infrastructure (keyboard controller, focus management);
- Cross-cutting UI concerns that follow the visual hierarchy;
- Values that need different overrides at different levels of your UI tree.

### Aren't For:

- Business logic or application state;
- Data that should be managed by state management solutions;
- Values that affect application behavior;
- Database connections, repositories, or other non-UI dependencies;
- Avoiding proper dependency injection.

Think of Composition Locals as part of your UI toolkit, not as a general dependency injection mechanism. They shine when dealing with UI-related values that naturally follow your component hierarchy, but shouldn't be used to bypass proper architecture patterns or hide important dependencies.

## Ответ (RU)
Обычно в Compose данные передаются вниз по дереву UI в качестве параметров каждой composable функции. Это делает зависимости composable явными. Однако это может быть неудобно для данных, которые используются очень часто и широко, таких как цвета или стили типографики.

Чтобы не передавать эти данные в качестве явной зависимости параметра большинству composables, **Compose предлагает** `CompositionLocal`, **который позволяет создавать именованные объекты с областью видимости дерева, которые могут использоваться как неявный способ передачи данных через дерево UI**.

Элементы `CompositionLocal` обычно предоставляются со значением в определенном узле дерева UI. Это значение может использоваться его composable потомками без объявления `CompositionLocal` в качестве параметра в composable функции.

## Пример использования

```kotlin
data class UserPreferences(val isDarkModeEnabled: Boolean, val fontSize: Float)

// Определяем динамический Composition Local с настройками по умолчанию
val LocalUserPreferences = compositionLocalOf {
    UserPreferences(isDarkModeEnabled = false, fontSize = 14f)
}

@Composable
fun PreferencesProvider(content: @Composable () -> Unit) {
    var isDarkMode by remember { mutableStateOf(false) }
    val preferences = UserPreferences(isDarkMode, 16f)
    CompositionLocalProvider(LocalUserPreferences provides preferences) {
        content()
    }
}

@Composable
fun SettingsScreen() {
    val preferences = LocalUserPreferences.current
    Text("Темная тема: ${if (preferences.isDarkModeEnabled) "Включена" else "Выключена"}")
}
```

## Ключевые концепции и преимущества CompositionLocal

### Неявное совместное использование

`CompositionLocal` позволяет данным совместно использоваться между composables без явной передачи их в качестве параметра. Это упрощает управление глобально важными данными, такими как стили темы, пользовательские настройки или конфигурации приложения.

### Локализованный контекст

`CompositionLocal` позволяет различным частям UI иметь свой собственный контекст, который может варьироваться в зависимости от области, в которой предоставляется `CompositionLocal`. Это полезно для настройки различных разделов UI при сохранении общей согласованности.

### Реактивность

Для динамических значений `CompositionLocal` может запускать перекомпозицию при изменении его значения. Это означает, что при обновлении значения будут перекомпонованы только те части UI, которые зависят от этого значения, сохраняя эффективность и отзывчивость UI.

### Разделенные компоненты

`CompositionLocal` отделяет UI компоненты от их прямых зависимостей. Это повышает модульность и повторное использование composables, так как им не нужно знать о конкретных данных, предоставляемых выше в дереве композиции. Это упрощает тестирование и повторное использование компонентов.

## Типы провайдеров CompositionLocal

### compositionLocalOf

Позволяет точно контролировать перекомпозиции. Когда значение изменяется, перекомпонуются только те части UI, которые читают это значение. Идеально подходит для часто меняющихся данных, таких как динамические темы или пользовательские настройки.

**Применение**: Ситуации, когда данные регулярно изменяются, такие как динамические темы UI, настройки локализации или пользовательские конфигурации.

### staticCompositionLocalOf

В отличие от `compositionLocalOf`, Compose не отслеживает места, где читается `staticCompositionLocalOf`. Когда значение изменяется, перекомпонуется весь блок контента, где предоставляется `CompositionLocal`, а не только места, где читается значение `current` в Composition. Лучше всего использовать для редко меняющихся данных.

**Применение**: Подходит для стабильных конфигураций, таких как конечные точки API, флаги отладки или статические темы UI, которые остаются постоянными в течение жизненного цикла приложения.

Если значение, предоставляемое `CompositionLocal`, крайне маловероятно изменится или никогда не изменится, используйте `staticCompositionLocalOf` для получения преимуществ в производительности.

## Для чего предназначены (и не предназначены) Composition Locals

### Предназначены для:

- Токены системы дизайна (темы, отступы, типографика);
- UI инфраструктура (контроллер клавиатуры, управление фокусом);
- Сквозные UI задачи, следующие визуальной иерархии;
- Значения, требующие различных переопределений на разных уровнях дерева UI.

### Не предназначены для:

- Бизнес-логики или состояния приложения;
- Данных, которые должны управляться решениями для управления состоянием;
- Значений, влияющих на поведение приложения;
- Подключений к базе данных, репозиториев или других не-UI зависимостей;
- Избежания правильной инъекции зависимостей.

Думайте о Composition Locals как о части вашего UI инструментария, а не как об общем механизме инъекции зависимостей. Они отлично работают при работе с UI-связанными значениями, которые естественно следуют иерархии ваших компонентов, но не должны использоваться для обхода правильных архитектурных паттернов или скрытия важных зависимостей.

## Links

- [Locally scoped data with CompositionLocal](https://developer.android.com/develop/ui/compose/compositionlocal)
- [Composition Local in Jetpack Compose](https://medium.com/@ramadan123sayed/composition-local-in-jetpack-compose-4d0a54afa67c)
- [Composition Locals in Jetpack Compose: A Beginner-to-Advanced Guide](https://proandroiddev.com/composition-locals-in-jetpack-compose-a-beginner-to-advanced-guide-e6a812ca7620)
- [Jetpack Compose CompositionLocal - What You Need to Know](https://medium.com/geekculture/jetpack-compose-compositionlocal-what-you-need-to-know-979a4aef6412)
- [A Jetpack Compose Composition Local Tutorial](https://www.answertopia.com/jetpack-compose/a-jetpack-compose-composition-local-tutorial/)
