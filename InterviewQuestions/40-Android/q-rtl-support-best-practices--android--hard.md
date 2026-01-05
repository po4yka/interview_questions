---
id: android-642
title: RTL Support Best Practices / 1b4347483835 3f40303a42383a38 3f3e34343540363a38 RTL
aliases: [1b4347483835 3f40303a42383a38 3f3e34343540363a38 RTL, RTL Support Best Practices]
topic: android
subtopics: [i18n-l10n, ui-views]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-android-resources, q-app-security-best-practices--android--medium, q-multi-module-best-practices--android--hard, q-runtime-permissions-best-practices--android--medium]
created: 2025-10-02
updated: 2025-11-11
tags: [accessibility, android/i18n-l10n, android/ui-views, difficulty/hard]
sources:
  - "https://developer.android.com/guide/topics/resources/layout-direction"
  - "https://material.io/design/usability/bidirectionality.html"

---
# Вопрос (RU)
> Как обеспечить поддержку RTL (справа налево) в Android-приложении: макеты `View`/Compose, зеркалирование ресурсов, BiDi-текст, тестирование и интеграция с локалями?

# Question (EN)
> How do you ensure robust RTL (right-to-left) support in an Android app, covering `View`/Compose layouts, resource mirroring, BiDi text handling, testing, and locale integration?

---

## Ответ (RU)

### 1. Включение Поддержки RTL

- В `AndroidManifest` → `android:supportsRtl="true"` (для API 17+).
- Полагайтесь на системное направление разметки: оно задаётся локалью устройства или локалью приложения.
- Для установки локалей приложения используйте `AppCompatDelegate.setApplicationLocales` (AndroidX AppCompat 1.6+), учитывая влияние на направление макета.
- В Compose: обычно доверяйте `LocalLayoutDirection`, который предоставляется системой/Material-темой. Явное `CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl)` применяйте точечно для отдельных компонентов, а не всего приложения.

### 2. Layout И Ресурсы

- `View` system: используйте `start`/`end` вместо `left`/`right` (`layout_marginStart`, `paddingStart`, `Gravity.START`, `layout_alignParentStart` и т.п.).
- Compose: `Arrangement.Start`/`Alignment.Start` и `Modifier.padding(start = ...)` учитывают `LayoutDirection` и автоматически инвертируются в RTL.
- Автоматическое зеркалирование: используйте `android:autoMirrored="true"` для подходящих векторных/drawable-ресурсов (иконки стрелок и т.п.) в API 17+.
- Специальные ресурсы: при сложных случаях, когда простое авто-зеркалирование неверно, можно использовать RTL-специфичные ресурсы с квалификатором `-ldrtl` (например, `drawable-ldrtl`). Для layout предпочтительнее добиваться корректного поведения через `start`/`end` и `layoutDirection`, а не дублировать разметку.

### 3. BiDi Текст И Форматирование

- Для смешанных направлений используйте `BidiFormatter` (или `androidx.core.text.BidiFormatter`) для корректного оборачивания LTR-текста внутри RTL-контекста и наоборот.
- `TextUtils.getLayoutDirectionFromLocale(locale)` помогает определить направление для выбранной локали; не подменяет работу `BidiFormatter`.
- В Compose и `View` стандартные текстовые компоненты (например, `Text`) поддерживают BiDi на уровне движка рендеринга; не полагайтесь на `rememberTextMeasurer` как на основной механизм для BiDi.
- Избегайте строковой конкатенации с переменным направлением. Используйте форматированные строки (например, "%1$s — %2$s"), чтобы движок макета и BiDi-алгоритм могли корректно упорядочить фрагменты.
- Для кусков явно LTR-текста (email, URL, code) в RTL-контексте применяйте `unicodeWrap` из `BidiFormatter` или соответствующие Unicode direction marks, чтобы предотвратить "разъезд" текста.

### 4. Тестирование

- Запускайте приложение с реальными RTL-локалями (`ar`, `fa`, `he`) и псевдолокалью RTL (`ar-XB`, если доступна в окружении) для визуальной проверки.
- В инженерной практике используйте UI-тесты (Espresso/Compose UI), которые устанавливают нужную локаль (через настройки устройства, тестовый раннер или прикладной API). Если используете `LocaleTestRule`, явно оформляйте её как кастомный утилитарный класс.
- Используйте screenshot-тесты/визуальные диффы для сравнения LTR и RTL экранов, чтобы выявлять неверные выравнивания, незеркальные иконки и обрезанный текст.

### 5. Интерактивные Элементы

- Жесты: учитывайте, что "leading edge" и "trailing edge" зависят от направления. Например, жест "swipe-to-go-back" или edge-swipe логично располагать с ведущей стороны: слева в LTR и справа в RTL.
- Иконки: используйте авто-зеркалирование или отдельные RTL-варианты для направленных иконок (стрелки "назад", "вперёд" и т.п.), чтобы семантика сохранялась.
- Compose Navigation / анимации навигации: убедитесь, что анимации, основанные на "start"/"end" (slide in/out), зависят от `LayoutDirection`, чтобы направление анимации корректно менялось для RTL.

### 6. Edge Cases

- Смешанный контент (LTR-текст в RTL UI и наоборот): применяйте `BidiFormatter.unicodeWrap` или явные Unicode-символы направления для email/URL/идентификаторов.
- Диаграммы и графики: локализуйте подписи осей и легенды, учитывайте направление подписи и порядок серий, если он зависит от чтения слева-направо/справа-налево.
- Анимации: для слайдов/перелистываний используйте start/end-ориентированные API, чтобы направление автоматически инвертировалось в RTL, а не жёстко кодируйте left/right.

### 7. Pipeline И Контроль

- Включите RTL-проверки в CI: автозапуск UI-тестов/скриншот-тестов под RTL-локалью.
- Подготовьте checklist для дизайнеров и разработчиков: проверка иконок, типографики, отступов, навигации и жестов в RTL.
- Проводите LQA/досмотры с носителями RTL-языков, чтобы поймать нюансы реального использования.

---

## Answer (EN)

### 1. Enabling RTL Support

- In `AndroidManifest`: set `android:supportsRtl="true"` (API 17+).
- Rely on system/app locale to drive layout direction.
- To set app-specific locales, use `AppCompatDelegate.setApplicationLocales` (AndroidX AppCompat 1.6+), understanding it affects layout direction.
- In Compose, rely on `LocalLayoutDirection` provided by the system/Material theme. Use `CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl)` only for targeted components, not as a global override.

### 2. Layouts and Resources

- `View` system: use `start`/`end` instead of `left`/`right` (`layout_marginStart`, `paddingStart`, `Gravity.START`, `layout_alignParentStart`, etc.).
- Compose: `Arrangement.Start`/`Alignment.Start` and `Modifier.padding(start = ...)` are aware of `LayoutDirection` and flip automatically in RTL.
- Automatic mirroring: use `android:autoMirrored="true"` for appropriate vector/drawable resources (e.g., arrows) on API 17+.
- Specialized resources: for complex cases where auto-mirroring is wrong, use RTL-specific resources with the `-ldrtl` qualifier (e.g., `drawable-ldrtl`). For layouts, prefer correct use of `start`/`end` and `layoutDirection` rather than duplicating XML layouts.

### 3. BiDi Text and Formatting

- For mixed-direction content, use `BidiFormatter` (or `androidx.core.text.BidiFormatter`) to wrap LTR text in RTL context and vice versa.
- `TextUtils.getLayoutDirectionFromLocale(locale)` derives layout direction; it does not replace `BidiFormatter`.
- Standard text components in `View` and Compose handle BiDi at the rendering engine level; do not treat `rememberTextMeasurer` as a primary BiDi mechanism.
- Avoid naive string concatenation with mixed directions; use formatted strings (e.g., "%1$s — %2$s") so the BiDi algorithm can order segments correctly.
- For explicitly LTR segments (emails, URLs, codes) in RTL UI, use `BidiFormatter.unicodeWrap` or explicit Unicode direction marks to prevent mis-ordering.

### 4. Testing

- Run the app with real RTL locales (`ar`, `fa`, `he`) and RTL pseudo-locale (e.g., `ar-XB` where available) for visual verification.
- Use UI tests (Espresso/Compose UI) that set the desired locale via device/emulator settings, test runner, or app-level APIs. If you use a `LocaleTestRule`, keep it as a clearly defined custom utility.
- Use screenshot/visual diff tests to compare LTR vs RTL screens and catch misaligned elements, non-mirrored icons, and clipped text.

### 5. Interactive Elements

- Gestures: ensure "leading/trailing edge" interactions (swipe-to-go-back, edge swipes, drawers) adapt to layout direction: leading edge is left in LTR and right in RTL.
- Icons: use auto-mirroring or dedicated RTL variants for directional icons (back/forward arrows, chevrons) so their meaning stays correct.
- Compose Navigation / navigation animations: ensure slide/transition directions are based on `start`/`end` and `LayoutDirection` so they reverse appropriately for RTL.

### 6. Edge Cases

- Mixed content (LTR text in RTL UI and vice versa): use `BidiFormatter.unicodeWrap` or Unicode direction marks for emails/URLs/IDs.
- Charts/graphs: localize axis labels and legends; consider whether logical order/read direction should be reversed for RTL.
- Animations: implement horizontal slides/pages using start/end-based APIs instead of hardcoded left/right so they invert naturally for RTL.

### 7. Pipeline and Quality Control

- Integrate RTL checks into CI: run UI/screenshot tests under RTL locales.
- Maintain an RTL checklist for designers and engineers (icons, typography, spacing, navigation, gestures).
- Run LQA/reviews with native RTL speakers to validate real-world usability.

---

## Дополнительные Вопросы (RU)
- Как адаптировать Compose Navigation анимации под RTL?
- Как обрабатывать смешанный ввод (латиница + арабский) в поисковых полях?
- Какие UX-паттерны специфичны для RTL (tab bar, pagination и т.п.)?

## Follow-ups
- How to adapt Compose Navigation animations for RTL?
- How to handle mixed input (Latin + Arabic) in search fields?
- Which UX patterns are RTL-specific (tab bars, pagination, etc.)?

## Ссылки (RU)
- [[c-android]] — общий обзор основных аспектов Android.
- [[c-android-resources]] — управление ресурсами (включая alternative ресурсы для RTL).
- Layout direction guide: https://developer.android.com/guide/topics/resources/layout-direction — руководство по направлению макета и поддержке RTL.

## References
- [[c-android]]
- [[c-android-resources]]
- Layout direction guide: https://developer.android.com/guide/topics/resources/layout-direction
- Material Design: Bidirectionality: https://material.io/design/usability/bidirectionality.html

## Related Questions

- [[c-android]]
- [[c-android-resources]]
