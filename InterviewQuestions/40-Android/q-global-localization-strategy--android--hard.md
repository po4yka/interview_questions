---
id: android-641
title: Global Localization Strategy / Стратегия глобальной локализации
aliases:
  - Global Localization Strategy
  - Стратегия глобальной локализации
topic: android
subtopics:
  - globalization
  - localization
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
  - localization
  - release
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/resources/localization
    note: Android localization guide
  - url: https://developer.android.com/guide/topics/resources/pseudolocales
    note: Pseudo-localization documentation
---

# Вопрос (RU)
> Как построить стратегию глобальной локализации Android-приложения: управление ресурсами, процесс перевода, псевдолокализация, тестирование и автоматизация в CI/CD?

# Question (EN)
> How do you design a global localization strategy for an Android app, including resource management, translation workflow, pseudo-localization, testing, and CI/CD automation?

---

## Ответ (RU)

### 1. Каталог ресурсов и структура

- Используйте `res/values-<locale>` + `res/xml/locales_config`.
- Устанавливайте `tools:ignore="MissingTranslation"` только временно; CI должен падать при отсутствии перевода.
- Разделяйте ключи по доменам (`auth_`, `billing_`) и избегайте конкатенаций.

### 2. Псевдолокализация и проверка длины

- Включите pseudo-locales (`en-XA`, `ar-XB`) в `locales_config`.
- CI job запускает Espresso/UI тесты с pseudo-locale → ловит обрезания, hard-coded строки.
- Применяйте expansion ratio (минимум +30%) при дизайне.

### 3. Процесс перевода

- Ведите master strings в repo (`strings.xml`) и экспортируйте в TMS (Smartling, Lokalise) через `gradle` task.
- Используйте translation memory и контекстные скриншоты.
- Включайте reviewer loop: локальные proofreaders проверяют критичные рынки.

### 4. Форматирование и pluralization

- Используйте `getString(R.string.key, formatArgs)`; избегайте ручных форматированных строк.
- Для множественных форм → `<plurals>` с `quantity` (zero, one, other).
- Числа/валюты: `NumberFormat.getCurrencyInstance(locale)`, `MeasureFormat` для единиц.

### 5. Автоматизация в CI/CD

- Статический анализ: lint → `HardcodedText`, `UnusedResources`.
- CI step `./gradlew lintPseudoLocales` (custom task) + `verifyTranslations`.
- Перед релизом: generate translation diff, отправить на review.

### 6. Запросы от runtime

- Уважайте пользовательский выбор: `AppCompatDelegate.setApplicationLocales`.
- Учитывайте per-activity локали (Android 13 Locale API).
- Позвольте пользователю менять язык in-app, синхронизируйте с сервером.

### 7. QA и мониторинг

- QA matrix: top markets, pseudo-locales, RTL.
- Собирайте фидбек в приложении (language-specific issues).
- Мониторинг crash/ANR по локалям → может выявить форматные ошибки.

---

## Answer (EN)

- Structure resources per locale, keep a strict master strings file, and fail CI on missing translations; use descriptive keys and avoid string concatenation.
- Enable pseudo-locales (`en-XA`, `ar-XB`) to catch truncation and hard-coded text; run automated UI tests with them.
- Integrate with a translation management system, exporting/importing via Gradle tasks, and include contextual metadata plus reviewer loops.
- Use Android formatting APIs (`plurals`, `NumberFormat`, `MeasureFormat`) to handle pluralization, currencies, and measurement units correctly.
- Automate lint checks for hardcoded text, track translation diffs in CI, and require approvals before release.
- Respect per-app locale APIs (Android 13), allow in-app language switching, and sync preferences with backend where needed.
- Maintain QA matrices across locales, collect localized feedback, and monitor crashes by locale to detect format issues.

---

## Follow-ups
- Как синхронизировать переводы для dynamic feature modules и PAD?
- Как управлять юридическими текстами (ToS, Privacy) в разных странах?
- Какие метрики эффективности локализации (LQA defects, time-to-market)?

## References
- [[c-globalization]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/resources/localization

## Related Questions

- [[c-globalization]]
- [[q-android-coverage-gaps--android--hard]]
