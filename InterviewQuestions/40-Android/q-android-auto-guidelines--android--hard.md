---
id: android-622
title: Android Auto Guidelines / Руководство Android Auto
aliases:
  - Android Auto Guidelines
  - Руководство Android Auto
topic: android
subtopics:
  - automotive
  - android-auto
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-android-auto
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/automotive
  - android/android-auto
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/cars/apps
    note: Car app guidelines
  - url: https://developer.android.com/training/cars/apps/media
    note: Media app quality checklist
---

# Вопрос (RU)
> Как спроектировать и сертифицировать Android Auto / Automotive OS приложение: соблюсти ограничений по отвлечению, шаблонам, голосовому управлению и процессу ревью?

# Question (EN)
> How do you design and certify an Android Auto / Automotive OS app, meeting distraction guidelines, template constraints, voice requirements, and review processes?

---

## Ответ (RU)

### Категория и шаблоны

- Android Auto поддерживает 4 категории: Navigation, POI, Media, Messaging.
- Используйте Car App Library (`ListTemplate`, `PaneTemplate`, `MapTemplate`); произвольного UI нет.
- Navigation требует предоставления маршрутов и поддерживает turn-by-turn через `NavigationTemplate`.

### Driver Distraction Rules

- Водитель не должен выполнять больше двух тачей для ключевых задач.
- Длинные формы запрещены; используйте голос или companion app.
- На скорости >5 км/ч UI автоматически урезается (list lengths, carousel).

### Голос и Assistant

- Интегрируйте voice commands (`CarContext.getCarAppService().setVoiceControlCommand`).
- Для сообщений — `CarMessageCallback`.
- Media apps должны поддерживать search via Assistant (`onSearch`).

### Automotive OS vs Auto

- Automotive OS — отдельный APK, lifecycle `CarAppService`.
- `CarHardwareManager` для доступа к сенсорам (скорость, топливо).
- Требуется работа с OEM: настройки UI, плотность экрана, сертификация.

### Процесс сертификации

1. Сборка car-app bundle и QA по чеклисту (Media/Navigation).
2. Предварительная проверка (self-review в Play Console).
3. Google review (latency, voice, driver distraction tests).
4. Постоянный мониторинг (ANR, latency, policy updates).

### Тестирование

- Эмулятор Android Auto + Desktop Head Unit.
- Automotive OS emulator (Car API Level).
- Прогоните сценарии на реальном авто/rig (touch target size, glare).

### Монетизация/Policy

- Нельзя показывать рекламу/видео на главном экране (policy).
- Покупки разрешены только через голос/companion (например, fueling).
- Play Billing обязателен для digital goods (если применимо).

---

## Answer (EN)

- Choose the correct app category and build UI via Car App Library templates, enforcing driver distraction limits.
- Implement voice-first flows, assistant search, and message replies via the provided callbacks.
- For Automotive OS, ship a dedicated APK, integrate with `CarHardwareManager`, and coordinate with OEM for certification.
- Pass Google’s quality checklist, run on emulators and real hardware, and monitor policies for updates.

---

## Follow-ups
- Как реализовать гибридный подход (Auto + Automotive) с общим кодом?
- Какие метрики latency отслеживает Google при ревью?
- Как организовать интеграцию с Assistant для кастомных команд?

## References
- [[c-android-auto]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/training/cars/apps
- https://developer.android.com/training/cars/apps/media
