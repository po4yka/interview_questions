---
id: 20251012-122711193
title: "Why Fragment Callbacks Differ From Activity Callbacks / Почему колбэки Fragment отличаются от колбэков Activity"
topic: android
difficulty: hard
status: draft
moc: moc-android
related: [q-why-use-diffutil--android--medium, q-where-does-the-repeated-call-of-composable-function-come-from--android--medium, q-glide-image-loading-internals--android--medium]
created: 2025-10-15
tags:
  - android
date created: Saturday, October 18th 2025, 1:27:59 pm
date modified: Thursday, October 30th 2025, 3:17:30 pm
---

# Why Fragment callbacks differ from Activity callbacks?

## Answer (EN)


## Ответ (RU)

Колбэки Fragment отличаются от колбэков Activity потому что Fragment имеет более сложный жизненный цикл, который зависит от жизненного цикла хост-Activity. Fragment имеет дополнительные колбэки для управления присоединением к Activity (`onAttach`, `onDetach`) и создания/уничтожения View (`onCreateView`, `onDestroyView`), в то время как Activity имеет более простой жизненный цикл с основными методами (`onCreate`, `onStart`, `onResume`, `onPause`, `onStop`, `onDestroy`).


---

## Related Questions

### Prerequisites (Easier)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity, Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Activity, Fragment
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment

### Related (Medium)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard]] - Activity, Fragment
