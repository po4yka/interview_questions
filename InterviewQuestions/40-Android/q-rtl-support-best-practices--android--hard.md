---
id: android-642
title: RTL Support Best Practices / Лучшие практики поддержки RTL
aliases:
  - RTL Support Best Practices
  - Лучшие практики поддержки RTL
topic: android
subtopics:
  - globalization
  - rtl
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-globalization
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/globalization
  - rtl
  - accessibility
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/resources/layout-direction
    note: Layout direction guide
  - url: https://material.io/design/usability/bidirectionality.html
    note: Material Design bidirectionality
---

# Вопрос (RU)
> Как обеспечить поддержку RTL (справа налево) в Android-приложении: макеты View/Compose, зеркалирование ресурсов, BiDi-текст, тестирование и интеграция с локалями?

# Question (EN)
> How do you ensure robust RTL (right-to-left) support in an Android app, covering View/Compose layouts, resource mirroring, BiDi text handling, testing, and locale integration?

---

## Ответ (RU)

### 1. Включение поддержки RTL

- В `AndroidManifest` → `android:supportsRtl="true"`.
- Используйте `AppCompatDelegate.setApplicationLocales` для установки локалей.
- Для Compose: `CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl)`.

### 2. Layout и ресурсы

- View system: используйте `start`/`end`, `paddingStart/paddingEnd`, `Gravity.START`.
- Compose: `Arrangement.Start`/`Alignment.Start` автоматически учитывают `LayoutDirection`.
- Автоматическое зеркалирование: `drawable` с `android:autoMirrored="true"` для векторных ресурсов.
- Специальные ресурсы: `drawable-ldrtl`/`layout-ldrtl` при необходимости нестандартного зеркалирования.

### 3. BiDi текст и форматирование

- Используйте `BidiFormatter` или `TextUtils.getLayoutDirectionFromLocale`.
- Для Compose → `rememberTextMeasurer` учитывает BiDi; добавляйте Unicode direction marks при вставке пользовательского текста.
- Избегайте конкатенации: `%1$s · %2$s`, чтобы BiDi мог корректно перестроить порядок.

### 4. Тестирование

- UI tests: запускайте pseudo-locale `ar-XB` или реальные (`ar`, `he`).
- Espresso: `LocaleTestRule` + snapshot tests.
- Screenshot диффы: сравнивайте LTR vs RTL.

### 5. Интерэктивные элементы

- Gestures: учитывайте, что Swipe-to-go-back может быть справа налево.
- Icons: используйте mirrored assets (например, arrows).
- Compose Navigation: убедитесь, что transitions не ломают direction.

### 6. Edge cases

- Mixed content (LTR text в RTL UI): применяйте `unicodeWrap` для email/URL.
- Charts/graphs: подписывайте оси локализованными строками, учитывая направление.
- Animations: invert direction для Sliding transitions.

### 7. Pipeline и контроль

- Включите RTL тестирование в CI (pseudo locale).
- Создайте checklist для дизайнеров (icons, typography).
- Сбор фидбека от носителей языка (LQA с пользователями).

---

## Answer (EN)

- Enable RTL in the manifest, rely on start/end attributes, and leverage AppCompat/Compose APIs to respect layout direction.
- Mirror resources automatically with `android:autoMirrored`, and provide RTL-specific drawables/layouts only when necessary.
- Handle BiDi text with `BidiFormatter` and format strings properly; avoid concatenation and wrap mixed-direction strings.
- Run UI tests with RTL locales/pseudo-locales, compare screenshots, and ensure gestures, icons, and transitions adapt directionally.
- Manage edge cases (emails, charts, animations), and bake RTL checks into CI plus design reviews with native speakers.

---

## Follow-ups
- Как адаптировать Compose Navigation анимации под RTL?
- Как обрабатывать смешанный ввод (латиница + арабский) в поисковых полях?
- Какие UX паттерны специфичны для RTL (tab bars, pagination)?

## References
- [[c-globalization]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/resources/layout-direction

## Related Questions

- [[c-globalization]]
- [[q-android-coverage-gaps--android--hard]]
