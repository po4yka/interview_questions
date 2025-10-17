---
id: 20251012-1227174
title: "How To Create Animations In Android / Как создавать анимации в Android"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [MotionLayout, Property Animations, View Animations, android, android/animations, android/ui, animations, ui, difficulty/medium]
---
# Как в Android можно сделать анимацию?

**English**: How to create animations in Android?

## Answer (EN)
Android provides several powerful systems for creating animations, each suited for different use cases. The main approaches include Property Animations, View Animations, Drawable Animations, and MotionLayout.

### 1. Property Animations (Modern Approach)

Property animations are the most powerful and flexible way to animate in Android. They work by changing property values over time.

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

// Scale animation
val scaleUp = ObjectAnimator.ofFloat(view, "scaleX", 1f, 1.5f)
scaleUp.duration = 300
scaleUp.start()
```

#### Using ViewPropertyAnimator (Simpler API)

```kotlin
// Chained animations
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

### 2. View Animations (XML-based, Legacy)

Simpler but less flexible animations defined in XML or code.

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

MotionLayout is a layout type that helps create complex motion and widget animations.

```xml
<!-- res/layout/motion_scene.xml -->
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

Animate SVG paths for icon animations.

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

### 6. Transitions Framework

Animate layout changes automatically.

```kotlin
// Scene transitions
val sceneRoot: ViewGroup = findViewById(R.id.scene_root)
val scene1 = Scene.getSceneForLayout(sceneRoot, R.layout.scene1, this)
val scene2 = Scene.getSceneForLayout(sceneRoot, R.layout.scene2, this)

// Transition between scenes
TransitionManager.go(scene2, ChangeBounds())

// AutoTransition for layout changes
val root = findViewById<ViewGroup>(R.id.root)
TransitionManager.beginDelayedTransition(root)
view.visibility = View.GONE // Animated automatically
```

### 7. Spring Animations (Physics-based)

Natural, physics-based animations.

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

1. **Use Property Animations** for most use cases
2. **Prefer ViewPropertyAnimator** for simple view animations
3. **Use MotionLayout** for complex, interactive animations
4. **Keep animations short**: 200-400ms
5. **Cancel animations** when views are destroyed
6. **Test on low-end devices** for performance
7. **Respect accessibility settings** (reduce motion)

```kotlin
// Cancel animations properly
override fun onDestroyView() {
    super.onDestroyView()
    view?.animate()?.cancel()
}
```

## Ответ (RU)
В Android анимации можно создавать с помощью Property Animations, View Animations, Drawable Animations и MotionLayout. Для Property Animations используйте ObjectAnimator для анимации свойств объектов. Для View Animations создайте XML-анимацию и примените её через AnimationUtils.loadAnimation. Для Drawable Animations используйте анимацию кадров в XML и запустите её через AnimationDrawable. Для MotionLayout определите анимацию в MotionScene и примените её к элементам интерфейса.

