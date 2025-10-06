---
id: q-view-composition-strategy-compose--android--medium--1728115560000
title: "ViewCompositionStrategy in Compose / ViewCompositionStrategy в Compose"
topic: android
aliases:
  - ViewCompositionStrategy in Compose
  - ViewCompositionStrategy в Compose
date_created: 2025-10-05
date_modified: 2025-10-05
status: draft
original_language: en
language_tags:
  - en
  - ru
type: question
category: android
difficulty: medium
subtopics:
  - ui-compose
  - lifecycle
  - performance-memory
tags:
  - android
  - compose
  - viewcompositionstrategy
  - lifecycle
  - interop
  - difficulty/medium
moc: moc-android
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20ViewCompositionStrategy.md"
---

# ViewCompositionStrategy in Compose / ViewCompositionStrategy в Compose

## EN

### Question

What do you know about ViewCompositionStrategy?

### Answer

`ViewCompositionStrategy` defines when the Composition should be disposed. The default, `ViewCompositionStrategy.Default`, disposes the Composition when the underlying `ComposeView` detaches from the window, unless it is part of a pooling container such as a `RecyclerView`. In a single-Activity Compose-only app, this default behavior is what you would want, however, if you are incrementally adding Compose in your codebase, this behavior may cause state loss in some scenarios.

To change the `ViewCompositionStrategy`, call the `setViewCompositionStrategy()` method and provide a different strategy.

### Available Strategies

There are four different options for `ViewCompositionStrategy`:

#### 1. DisposeOnDetachedFromWindow

The Composition will be disposed when the underlying `ComposeView` is detached from the window. Has since been superseded by `DisposeOnDetachedFromWindowOrReleasedFromPool`.

**Interop scenario:**
- `ComposeView` whether it's the sole element in the View hierarchy, or in the context of a mixed View/Compose screen (not in Fragment)

#### 2. DisposeOnDetachedFromWindowOrReleasedFromPool (Default)

Similar to `DisposeOnDetachedFromWindow`, when the Composition is not in a pooling container, such as a `RecyclerView`. If it is in a pooling container, it will dispose when either the pooling container itself detaches from the window, or when the item is being discarded (i.e. when the pool is full).

**Interop scenario:**
- `ComposeView` whether it's the sole element in the View hierarchy, or in the context of a mixed View/Compose screen (not in Fragment)
- `ComposeView` as an item in a pooling container such as `RecyclerView`

#### 3. DisposeOnLifecycleDestroyed

The Composition will be disposed when the provided `Lifecycle` is destroyed.

**Interop scenario:**
- `ComposeView` in a Fragment's View

#### 4. DisposeOnViewTreeLifecycleDestroyed

The Composition will be disposed when the `Lifecycle` owned by the `LifecycleOwner` returned by `ViewTreeLifecycleOwner.get` of the next window the View is attached to is destroyed.

**Interop scenario:**
- `ComposeView` in a Fragment's View
- `ComposeView` in a View wherein the Lifecycle is not known yet

### When to Use Each Strategy

Choose the appropriate strategy based on your use case:

- **Default strategy** works well for most cases, especially in pooling containers
- **DisposeOnLifecycleDestroyed** is ideal when using `ComposeView` in Fragments
- **DisposeOnViewTreeLifecycleDestroyed** is useful when the lifecycle is not immediately known
- **DisposeOnDetachedFromWindow** is the legacy option, now mostly replaced by the default

### Example Usage

```kotlin
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(lifecycle)
)
```

### Important Considerations

- The default strategy prevents memory leaks in pooling containers
- Choosing the wrong strategy can lead to state loss or memory leaks
- In Fragment scenarios, prefer lifecycle-based strategies
- For RecyclerView items, the default strategy handles disposal correctly

---

## RU

### Вопрос

Что вы знаете о ViewCompositionStrategy?

### Ответ

`ViewCompositionStrategy` определяет, когда Composition должна быть уничтожена. По умолчанию, `ViewCompositionStrategy.Default`, уничтожает Composition, когда базовый `ComposeView` отсоединяется от окна, если только он не является частью контейнера с пулом, такого как `RecyclerView`. В одноактивити приложении, использующем только Compose, это поведение по умолчанию является желаемым, однако, если вы постепенно добавляете Compose в вашу кодовую базу, это поведение может вызвать потерю состояния в некоторых сценариях.

Чтобы изменить `ViewCompositionStrategy`, вызовите метод `setViewCompositionStrategy()` и предоставьте другую стратегию.

### Доступные стратегии

Существует четыре различных варианта для `ViewCompositionStrategy`:

#### 1. DisposeOnDetachedFromWindow

Composition будет уничтожена, когда базовый `ComposeView` отсоединяется от окна. С тех пор была заменена `DisposeOnDetachedFromWindowOrReleasedFromPool`.

**Сценарий взаимодействия:**
- `ComposeView`, будь то единственный элемент в иерархии View или в контексте смешанного экрана View/Compose (не во Fragment)

#### 2. DisposeOnDetachedFromWindowOrReleasedFromPool (по умолчанию)

Аналогично `DisposeOnDetachedFromWindow`, когда Composition не находится в контейнере с пулом, таком как `RecyclerView`. Если она находится в контейнере с пулом, она будет уничтожена, когда либо сам контейнер с пулом отсоединяется от окна, либо когда элемент отбрасывается (т.е. когда пул заполнен).

**Сценарий взаимодействия:**
- `ComposeView`, будь то единственный элемент в иерархии View или в контексте смешанного экрана View/Compose (не во Fragment)
- `ComposeView` как элемент в контейнере с пулом, таком как `RecyclerView`

#### 3. DisposeOnLifecycleDestroyed

Composition будет уничтожена, когда предоставленный `Lifecycle` будет уничтожен.

**Сценарий взаимодействия:**
- `ComposeView` во View Fragment

#### 4. DisposeOnViewTreeLifecycleDestroyed

Composition будет уничтожена, когда `Lifecycle`, принадлежащий `LifecycleOwner`, возвращенному `ViewTreeLifecycleOwner.get` следующего окна, к которому прикреплен View, будет уничтожен.

**Сценарий взаимодействия:**
- `ComposeView` во View Fragment
- `ComposeView` во View, где Lifecycle еще не известен

### Когда использовать каждую стратегию

Выберите подходящую стратегию в зависимости от вашего случая использования:

- **Стратегия по умолчанию** хорошо работает для большинства случаев, особенно в контейнерах с пулом
- **DisposeOnLifecycleDestroyed** идеальна при использовании `ComposeView` во фрагментах
- **DisposeOnViewTreeLifecycleDestroyed** полезна, когда жизненный цикл не сразу известен
- **DisposeOnDetachedFromWindow** - это устаревший вариант, теперь в основном заменен стратегией по умолчанию

### Пример использования

```kotlin
composeView.setViewCompositionStrategy(
    ViewCompositionStrategy.DisposeOnLifecycleDestroyed(lifecycle)
)
```

### Важные соображения

- Стратегия по умолчанию предотвращает утечки памяти в контейнерах с пулом
- Выбор неправильной стратегии может привести к потере состояния или утечкам памяти
- В сценариях с Fragment предпочтительны стратегии, основанные на жизненном цикле
- Для элементов RecyclerView стратегия по умолчанию правильно обрабатывает уничтожение
