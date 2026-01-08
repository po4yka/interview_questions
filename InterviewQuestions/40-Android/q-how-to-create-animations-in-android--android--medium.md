---\
id: android-394
title: How To Create Animations In Android / Как создавать анимации в Android
aliases: [How To Create Animations In Android, Как создавать анимации в Android]
topic: android
subtopics: [ui-animation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-custom-views, q-android-lint-tool--android--medium, q-app-start-types-android--android--medium, q-compose-custom-animations--android--medium, q-data-sync-unstable-network--android--hard, q-parsing-optimization-android--android--medium, q-stable-classes-compose--android--hard]
created: 2025-10-15
updated: 2025-10-31
tags: [android/ui-animation, animations, difficulty/medium]

---\
# Вопрос (RU)
> Как создавать анимации в Android

# Question (EN)
> How To Create Animations In Android

---

## Ответ (RU)
Android предоставляет несколько мощных механизмов для создания анимаций под разные сценарии: Property Animations, `View` Animations, `Drawable` Animations, Animated Vector Drawables, MotionLayout, Transitions и физические (spring/fling) анимации.

### 1. Property Animations (современный подход)

Property Animations (android.animation.*) изменяют реальные свойства объектов во времени и являются основным API.

#### ObjectAnimator

- Позволяет анимировать свойства `View` и любых объектов с сеттерами.

```kotlin
// Анимация исчезновения (fade out)
val fadeOut = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
fadeOut.duration = 1000
fadeOut.start()

// Анимация перемещения по оси X
val moveRight = ObjectAnimator.ofFloat(view, "translationX", 0f, 200f)
moveRight.duration = 500
moveRight.start()

// Анимация вращения
val rotate = ObjectAnimator.ofFloat(view, "rotation", 0f, 360f)
rotate.duration = 1000
rotate.repeatCount = ValueAnimator.INFINITE
rotate.start()

// Анимация масштабирования (обычно scaleX вместе с scaleY)
val scaleUp = ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.5f)
scaleUp.duration = 300
scaleUp.start()
```

#### ViewPropertyAnimator

- Упрощённый fluent-API для типичных анимаций `View`.

```kotlin
// Цепочка анимаций над View
view.animate()
    .alpha(0f)
    .translationY(100f)
    .scaleX(0.5f)
    .scaleY(0.5f)
    .rotation(180f)
    .setDuration(500)
    .setInterpolator(AccelerateDecelerateInterpolator())
    .setListener(object : AnimatorListenerAdapter() {
        override fun onAnimationEnd(animation: Animator) {
            // Анимация завершена
        }
    })
    .start()
```

#### AnimatorSet

- Комбинация нескольких анимаций параллельно или последовательно.

```kotlin
val fadeOut = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
val scaleX = ObjectAnimator.ofFloat(view, "scaleX", 1f, 0.5f)
val scaleY = ObjectAnimator.ofFloat(view, "scaleY", 1f, 0.5f)

AnimatorSet().apply {
    playTogether(fadeOut, scaleX, scaleY)
    duration = 500
    start()
}

// Последовательные анимации
AnimatorSet().apply {
    playSequentially(
        ObjectAnimator.ofFloat(view, "translationX", 0f, 100f),
        ObjectAnimator.ofFloat(view, "translationY", 0f, 100f),
        ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
    )
    duration = 300
    start()
}
```

#### ValueAnimator

- Для анимации «произвольных» значений и ручного обновления состояний.

```kotlin
val animator = ValueAnimator.ofInt(0, 100)
animator.duration = 1000
animator.addUpdateListener { animation ->
    val value = animation.animatedValue as Int
    // Обновляем любое пользовательское свойство
    customView.progress = value
}
animator.start()
```

### 2. `View` Animations (устаревший API)

- XML / код (android.view.animation.*), влияют только на отрисовку, не меняют реальные layout-параметры.
- Используются реже, в основном для простых эффектов.

```xml
<!-- res/anim/fade_in.xml -->
<alpha
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="500"
    android:fromAlpha="0.0"
    android:toAlpha="1.0" />

<!-- res/anim/slide_up.xml -->
<translate
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="500"
    android:fromYDelta="100%"
    android:toYDelta="0%" />

<!-- res/anim/rotate.xml -->
<rotate
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="1000"
    android:fromDegrees="0"
    android:toDegrees="360"
    android:pivotX="50%"
    android:pivotY="50%" />
```

```kotlin
// Загрузка и запуск анимации из XML
val fadeIn = AnimationUtils.loadAnimation(this, R.anim.fade_in)
view.startAnimation(fadeIn)

// Программный пример анимации вращения
val rotateAnimation = RotateAnimation(
    0f, 360f,
    Animation.RELATIVE_TO_SELF, 0.5f,
    Animation.RELATIVE_TO_SELF, 0.5f
)
rotateAnimation.duration = 1000
view.startAnimation(rotateAnimation)
```

### 3. Drawable Animations (анимация кадров)

- Последовательность drawable-ресурсов (AnimationDrawable), создающая эффект покадровой анимации.

```xml
<!-- res/drawable/animation_list.xml -->
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="false">
    <item android:drawable="@drawable/frame1" android:duration="100" />
    <item android:drawable="@drawable/frame2" android:duration="100" />
    <item android:drawable="@drawable/frame3" android:duration="100" />
    <item android:drawable="@drawable/frame4" android:duration="100" />
</animation-list>
```

```kotlin
// Применение к ImageView
val imageView: ImageView = findViewById(R.id.imageView)
imageView.setBackgroundResource(R.drawable.animation_list)

val frameAnimation = imageView.background as AnimationDrawable
frameAnimation.start()
// frameAnimation.stop()
```

### 4. MotionLayout

- Расширение `ConstraintLayout` для сложных, декларативных анимаций и переходов между состояниями.
- Логика описывается в MotionScene (обычно в res/xml), а сам MotionLayout в layout.

```xml
<!-- Пример MotionScene: res/xml/motion_scene.xml -->
<MotionScene xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:motion="http://schemas.android.com/apk/res-auto">

    <Transition
        motion:constraintSetStart="@+id/start"
        motion:constraintSetEnd="@+id/end"
        motion:duration="1000">
        <OnSwipe
            motion:touchAnchorId="@+id/button"
            motion:touchAnchorSide="right"
            motion:dragDirection="dragRight" />
    </Transition>

    <ConstraintSet android:id="@+id/start">
        <Constraint
            android:id="@+id/button"
            android:layout_width="64dp"
            android:layout_height="64dp"
            motion:layout_constraintStart_toStartOf="parent"
            motion:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>

    <ConstraintSet android:id="@+id/end">
        <Constraint
            android:id="@+id/button"
            android:layout_width="64dp"
            android:layout_height="64dp"
            motion:layout_constraintEnd_toEndOf="parent"
            motion:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>
</MotionScene>
```

```kotlin
// Управление MotionLayout программно
val motionLayout: MotionLayout = findViewById(R.id.motionLayout)

// Переход к конечному состоянию
motionLayout.transitionToEnd()

// Переход к начальному состоянию
motionLayout.transitionToStart()

// Установка прогресса вручную
motionLayout.progress = 0.5f
```

### 5. Animated Vector Drawables

- Анимация векторных иконок (пути/группы в VectorDrawable) через ObjectAnimator.

```xml
<!-- res/drawable/animated_check.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_check">
    <target
        android:name="check_path"
        android:animation="@animator/check_animation" />
</animated-vector>
```

```kotlin
val imageView: ImageView = findViewById(R.id.imageView)
imageView.setImageResource(R.drawable.animated_check)

val drawable = imageView.drawable as AnimatedVectorDrawable
drawable.start()
```

(Важно: значение `android:name` должно совпадать с именем path/group в `ic_check`.)

### 6. Transitions Framework

- Анимация изменений layout и переходов между сценами.

```kotlin
// Переходы между сценами
val sceneRoot: ViewGroup = findViewById(R.id.scene_root)
val scene1 = Scene.getSceneForLayout(sceneRoot, R.layout.scene1, this)
val scene2 = Scene.getSceneForLayout(sceneRoot, R.layout.scene2, this)

// Переход между сценами с анимацией
TransitionManager.go(scene2, ChangeBounds())

// Анимация изменений внутри одного layout
val root = findViewById<ViewGroup>(R.id.root)
TransitionManager.beginDelayedTransition(root)
view.visibility = View.GONE // Изменение будет анимировано
```

### 7. Физические Анимации (Spring/Fling)

- Используют физическую модель для более естественных движений (DynamicAnimation, SpringAnimation, FlingAnimation).

```kotlin
// Пример spring-анимации
val springAnim = SpringAnimation(view, DynamicAnimation.TRANSLATION_Y, 0f)
springAnim.spring.apply {
    dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
    stiffness = SpringForce.STIFFNESS_LOW
}
springAnim.start()

// Пример fling-анимации
val flingAnim = FlingAnimation(view, DynamicAnimation.SCROLL_X)
flingAnim.setStartVelocity(-2000f)
flingAnim.start()
```

### Интерполяторы Анимации

Интерполяторы управляют тем, как изменяется скорость анимации во времени (тайминг-кривая):

```kotlin
view.animate()
    .alpha(0f)
    .setInterpolator(AccelerateDecelerateInterpolator()) // Медленно -> быстро -> медленно
    .start()

// Другие популярные интерполяторы:
// LinearInterpolator() - постоянная скорость
// AccelerateInterpolator() - старт медленный, затем ускорение
// DecelerateInterpolator() - старт быстрый, затем замедление
// BounceInterpolator() - «пружинит» в конце
// OvershootInterpolator() - выходит за предел и возвращается
// AnticipateInterpolator() - делает небольшое движение назад перед основным
```

### Лучшие Практики

- Использовать Property Animations как основной инструмент.
- Для простых анимаций `View` использовать ViewPropertyAnimator.
- Для сложных интерактивных сценариев — MotionLayout.
- Длительность большинства UI-анимаций держать в районе 200–400 мс.
- Отменять анимации при уничтожении `View`/`Activity`/`Fragment`, чтобы избежать утечек.
- Тестировать производительность на слабых устройствах.
- Учитывать настройки доступности (уменьшенное движение и т.п.).

```kotlin
// Пример: отмена анимаций во Fragment
override fun onDestroyView() {
    view?.animate()?.cancel()
    super.onDestroyView()
}
```

---

## Answer (EN)
Android provides several powerful systems for creating animations, each suited for different use cases. The main approaches include Property Animations, `View` Animations, `Drawable` Animations, Animated Vector Drawables, MotionLayout, the Transitions framework, and physics-based (spring/fling) animations.

### 1. Property Animations (Modern Approach)

Property animations are the most powerful and flexible way to animate in Android (android.animation.*). They work by changing property values over time and actually update the underlying properties of objects.

#### Using ObjectAnimator

```kotlin
// Fade out animation
val fadeOut = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
fadeOut.duration = 1000
fadeOut.start()

// Translation animation
val moveRight = ObjectAnimator.ofFloat(view, "translationX", 0f, 200f)
moveRight.duration = 500
moveRight.start()

// Rotation animation
val rotate = ObjectAnimator.ofFloat(view, "rotation", 0f, 360f)
rotate.duration = 1000
rotate.repeatCount = ValueAnimator.INFINITE
rotate.start()

// Scale animation (note: scaleX only, usually pair with scaleY)
val scaleUp = ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.5f)
scaleUp.duration = 300
scaleUp.start()
```

#### Using ViewPropertyAnimator (Simpler API)

```kotlin
// Chained animations on a View
view.animate()
    .alpha(0f)
    .translationY(100f)
    .scaleX(0.5f)
    .scaleY(0.5f)
    .rotation(180f)
    .setDuration(500)
    .setInterpolator(AccelerateDecelerateInterpolator())
    .setListener(object : AnimatorListenerAdapter() {
        override fun onAnimationEnd(animation: Animator) {
            // Animation completed
        }
    })
    .start()
```

#### Using AnimatorSet for Multiple Animations

```kotlin
val fadeOut = ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
val scaleX = ObjectAnimator.ofFloat(view, "scaleX", 1f, 0.5f)
val scaleY = ObjectAnimator.ofFloat(view, "scaleY", 1f, 0.5f)

AnimatorSet().apply {
    playTogether(fadeOut, scaleX, scaleY)
    duration = 500
    start()
}

// Sequential animations
AnimatorSet().apply {
    playSequentially(
        ObjectAnimator.ofFloat(view, "translationX", 0f, 100f),
        ObjectAnimator.ofFloat(view, "translationY", 0f, 100f),
        ObjectAnimator.ofFloat(view, "alpha", 1f, 0f)
    )
    duration = 300
    start()
}
```

#### ValueAnimator for Custom Properties

```kotlin
val animator = ValueAnimator.ofInt(0, 100)
animator.duration = 1000
animator.addUpdateListener { animation ->
    val value = animation.animatedValue as Int
    // Update any custom property
    customView.progress = value
}
animator.start()
```

### 2. `View` Animations (XML-based, Legacy)

Legacy animation API (android.view.animation.*): simpler but less flexible; it only affects rendering (not actual layout properties) and is generally superseded by Property Animations.

```xml
<!-- res/anim/fade_in.xml -->
<alpha
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="500"
    android:fromAlpha="0.0"
    android:toAlpha="1.0" />

<!-- res/anim/slide_up.xml -->
<translate
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="500"
    android:fromYDelta="100%"
    android:toYDelta="0%" />

<!-- res/anim/rotate.xml -->
<rotate
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:duration="1000"
    android:fromDegrees="0"
    android:toDegrees="360"
    android:pivotX="50%"
    android:pivotY="50%" />
```

```kotlin
// Load and apply animation
val fadeIn = AnimationUtils.loadAnimation(this, R.anim.fade_in)
view.startAnimation(fadeIn)

// Programmatic view animation
val rotateAnimation = RotateAnimation(
    0f, 360f,
    Animation.RELATIVE_TO_SELF, 0.5f,
    Animation.RELATIVE_TO_SELF, 0.5f
)
rotateAnimation.duration = 1000
view.startAnimation(rotateAnimation)
```

### 3. Drawable Animations (Frame Animation)

Animate through a sequence of drawable resources like a flip book.

```xml
<!-- res/drawable/animation_list.xml -->
<animation-list xmlns:android="http://schemas.android.com/apk/res/android"
    android:oneshot="false">
    <item android:drawable="@drawable/frame1" android:duration="100" />
    <item android:drawable="@drawable/frame2" android:duration="100" />
    <item android:drawable="@drawable/frame3" android:duration="100" />
    <item android:drawable="@drawable/frame4" android:duration="100" />
</animation-list>
```

```kotlin
// Apply to ImageView
val imageView: ImageView = findViewById(R.id.imageView)
imageView.setBackgroundResource(R.drawable.animation_list)

// Start animation
val frameAnimation = imageView.background as AnimationDrawable
frameAnimation.start()

// Stop animation
frameAnimation.stop()
```

### 4. MotionLayout (Advanced Declarative Animations)

MotionLayout (from `ConstraintLayout` library) is a layout that helps create complex, declarative motion and widget animations using a separate MotionScene.

```xml
<!-- Example MotionScene: typically placed in res/xml/ -->
<MotionScene xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:motion="http://schemas.android.com/apk/res-auto">

    <Transition
        motion:constraintSetStart="@+id/start"
        motion:constraintSetEnd="@+id/end"
        motion:duration="1000">
        <OnSwipe
            motion:touchAnchorId="@+id/button"
            motion:touchAnchorSide="right"
            motion:dragDirection="dragRight" />
    </Transition>

    <ConstraintSet android:id="@+id/start">
        <Constraint
            android:id="@+id/button"
            android:layout_width="64dp"
            android:layout_height="64dp"
            motion:layout_constraintStart_toStartOf="parent"
            motion:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>

    <ConstraintSet android:id="@+id/end">
        <Constraint
            android:id="@+id/button"
            android:layout_width="64dp"
            android:layout_height="64dp"
            motion:layout_constraintEnd_toEndOf="parent"
            motion:layout_constraintTop_toTopOf="parent" />
    </ConstraintSet>
</MotionScene>
```

```kotlin
// Control MotionLayout programmatically
val motionLayout: MotionLayout = findViewById(R.id.motionLayout)

// Transition to end state
motionLayout.transitionToEnd()

// Transition to start state
motionLayout.transitionToStart()

// Set progress manually
motionLayout.progress = 0.5f
```

### 5. Animated Vector Drawables

Animate vector drawables (paths, groups) for icon animations.

```xml
<!-- res/drawable/animated_check.xml -->
<animated-vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:drawable="@drawable/ic_check">
    <target
        android:name="check_path"
        android:animation="@animator/check_animation" />
</animated-vector>
```

```kotlin
val imageView: ImageView = findViewById(R.id.imageView)
imageView.setImageResource(R.drawable.animated_check)

val drawable = imageView.drawable as AnimatedVectorDrawable
drawable.start()
```

(Ensure that the target name matches a path/group name defined inside ic_check.)

### 6. Transitions Framework

Animate layout changes automatically.

```kotlin
// Scene transitions
val sceneRoot: ViewGroup = findViewById(R.id.scene_root)
val scene1 = Scene.getSceneForLayout(sceneRoot, R.layout.scene1, this)
val scene2 = Scene.getSceneForLayout(sceneRoot, R.layout.scene2, this)

// Transition between scenes
TransitionManager.go(scene2, ChangeBounds())

// AutoTransition for layout changes within a single layout
val root = findViewById<ViewGroup>(R.id.root)
TransitionManager.beginDelayedTransition(root)
view.visibility = View.GONE // ChangeBounds/AutoTransition animates this automatically
```

### 7. Spring Animations (Physics-based)

Physics-based animations from DynamicAnimation library.

```kotlin
// Spring animation
val springAnim = SpringAnimation(view, DynamicAnimation.TRANSLATION_Y, 0f)
springAnim.spring.apply {
    dampingRatio = SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY
    stiffness = SpringForce.STIFFNESS_LOW
}
springAnim.start()

// Fling animation
val flingAnim = FlingAnimation(view, DynamicAnimation.SCROLL_X)
flingAnim.setStartVelocity(-2000f)
flingAnim.start()
```

### Animation Interpolators

Control animation timing curves:

```kotlin
view.animate()
    .alpha(0f)
    .setInterpolator(AccelerateDecelerateInterpolator()) // Slow -> Fast -> Slow
    .start()

// Other interpolators:
// LinearInterpolator() - Constant speed
// AccelerateInterpolator() - Starts slow, accelerates
// DecelerateInterpolator() - Starts fast, decelerates
// BounceInterpolator() - Bounces at the end
// OvershootInterpolator() - Overshoots and comes back
// AnticipateInterpolator() - Backs up before going forward
```

### Best Practices

1. Use Property Animations for most view and property changes.
2. Prefer ViewPropertyAnimator for simple, chained view animations.
3. Use MotionLayout for complex, interactive scene transitions.
4. Keep animations short (around 200–400ms for typical UI actions).
5. Cancel animations when views/fragments/activities are destroyed to avoid leaks.
6. Test on low-end devices to verify performance.
7. Respect accessibility settings (e.g., reduce motion or disable non-essential animations when requested by the user/device).

```kotlin
// Example: cancel view animations in Fragment
override fun onDestroyView() {
    view?.animate()?.cancel()
    super.onDestroyView()
}
```

---

## Follow-ups (RU)

- [[q-app-start-types-android--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]
- [[q-stable-classes-compose--android--hard]]

## Follow-ups (EN)

- [[q-app-start-types-android--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]
- [[q-stable-classes-compose--android--hard]]

## References (RU)

- [Animations](https://developer.android.com/develop/ui/views/animations)

## References (EN)

- [Animations](https://developer.android.com/develop/ui/views/animations)

## Related Questions (RU)

### Prerequisites / Concepts

- [[c-custom-views]]

- [[q-stable-classes-compose--android--hard]]
- [[q-app-start-types-android--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]

## Related Questions (EN)

### Prerequisites / Concepts

- [[c-custom-views]]

- [[q-stable-classes-compose--android--hard]]
- [[q-app-start-types-android--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]
