---
id: "20251015082237288"
title: "Shared Element Transitions / Переходы с общими элементами"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: - jetpack-compose
  - animations
  - navigation
  - transitions
  - shared-elements
  - hero-animations
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

## Follow-ups

-   How do shared element transitions interact with Navigation animations and back stack?
-   What are performance considerations and how to profile jank in hero animations?
-   How do you coordinate multiple shared elements and staggered transitions?

## References

-   `https://developer.android.com/jetpack/compose/animation/overview` — Compose animation
-   `https://developer.android.com/jetpack/compose/navigation` — Compose Navigation
-   `https://developer.android.com/guide/navigation/navigation-animate-transitions` — Navigation transitions

## Related Questions
