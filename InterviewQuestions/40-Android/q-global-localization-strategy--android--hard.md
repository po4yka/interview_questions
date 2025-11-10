---
id: android-641
title: Global Localization Strategy / Стратегия глобальной локализации
aliases:
- Global Localization Strategy
- Стратегия глобальной локализации
topic: android
subtopics:
- i18n-l10n
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
- q-android-architectural-patterns--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/i18n-l10n
- difficulty/hard
sources:
- url: "https://developer.android.com/guide/topics/resources/localization"
  note: Android localization guide
- url: "https://developer.android.com/guide/topics/resources/pseudolocales"
  note: Pseudo-localization documentation

---

# Вопрос (RU)
> Как построить стратегию глобальной локализации Android-приложения: управление ресурсами, процесс перевода, псевдолокализация, тестирование и автоматизация в CI/CD?

# Question (EN)
> How do you design a global localization strategy for an Android app, including resource management, translation workflow, pseudo-localization, testing, and CI/CD automation?

---

## Ответ (RU)

### Краткий вариант

- Четкая структура ресурсов и master-строк.
- Псевдолокализация и автоматические UI-тесты.
- Интеграция с TMS и review носителями языка.
- Корректное форматирование, plurals, числа/валюты.
- Lint и кастомные CI-проверки.
- Осознанное использование per-app/per-activity локалей.
- QA-матрица и мониторинг по локалям.

### Детальный вариант

#### 1. Каталог ресурсов и структура

- Используйте `res/values-<locale>` + `res/xml/locales_config` для декларации поддерживаемых локалей (и интеграции с per-app locales API).
- Устанавливайте `tools:ignore="MissingTranslation"` только временно; CI должен падать при отсутствии перевода для обязательных локалей.
- Разделяйте ключи по доменам (`auth_`, `billing_`) и избегайте конкатенаций.

#### 2. Псевдолокализация и проверка длины

- Включите псевдолокали (`en-XA`, `ar-XB`) в `locales_config`.
- Отдельная CI job (кастомная) запускает Espresso/UI тесты с псевдолокалью → ловит обрезания, hard-coded строки, проблемы c RTL.
- При дизайне учитывайте увеличение длины строк (закладывайте минимум +30%).

#### 3. Процесс перевода

- Ведите master strings в репозитории (`strings.xml`) и экспортируйте/импортируйте их в TMS (Smartling, Lokalise и т.п.) через кастомные `gradle`-tasks.
- Используйте translation memory и контекстные скриншоты для снижения ошибок перевода.
- Включайте reviewer loop: локальные носители языка/маркетинговые команды проверяют критичные рынки.

#### 4. Форматирование и pluralization

- Используйте `getString(R.string.key, formatArgs)` и форматные плейсхолдеры; избегайте ручной конкатенации форматированных строк.
- Для множественных форм → `<plurals>` с корректными `quantity` (например, `one`, `other`; учитывайте, что набор форм зависит от языка).
- Числа/валюты: `NumberFormat.getCurrencyInstance(locale)`, `NumberFormat.getInstance(locale)` для общего форматирования чисел, `MeasureFormat` для единиц.

#### 5. Автоматизация в CI/CD

- Статический анализ: Android Lint → правила `HardcodedText`, `MissingTranslation`, `UnusedResources`.
- Добавьте кастомные CI-стадии, например `./gradlew lintPseudoLocales` и `verifyTranslations` (имена условные), для проверки псевдолокалей и консистентности переводов.
- Перед релизом: генерируйте diff переводов и отправляйте на review владельцам контента/локальных рынков.

#### 6. Запросы от runtime

- Уважайте пользовательский выбор: используйте `AppCompatDelegate.setApplicationLocales` / per-app locale API (Android 13+).
- При необходимости учитывайте per-activity локали (API Android 13 Locale Manager и связанные API), но избегайте избыточной сложности, если достаточно per-app.
- Позвольте пользователю менять язык in-app для поддерживаемых локалей и при необходимости синхронизируйте выбор с сервером.

#### 7. QA и мониторинг

- QA-матрица: топ-рынки, псевдолокали, RTL, разные плотности и экраны.
- Собирайте фидбек в приложении по языку/региону (ошибки перевода, некорректные форматы).
- Мониторинг crash/ANR по локалям → может выявить форматные ошибки (например, неверные плейсхолдеры в строках или парсинг дат/чисел).

### Требования

#### Функциональные требования

- Поддержка нескольких локалей с централизованным управлением строками.
- Интеграция с TMS и автоматизированный импорт/экспорт переводов.
- Возможность выбора языка пользователем (per-app/per-activity где нужно).
- Поддержка псевдолокалей для тестирования.

#### Нефункциональные требования

- Минимальное дублирование строк и стабильные ключи.
- Высокое покрытие тестами для локализации (UI, e2e, lint).
- Отсутствие регрессий при добавлении новых локалей.
- Масштабируемость процесса локализации под рост числа рынков.

### Архитектура

- Единый источник master-строк в репозитории, синхронизируемый с TMS.
- Конвейер CI/CD с шагами: валидация переводов, псевдолокали, линт, сборка релиза по локалям.
- Использование per-app locale API и `locales_config` как слоя конфигурации локалей.
- Наблюдаемость: логирование и метрики по локалям для раннего обнаружения проблем.

---

## Answer (EN)

### Short Version

- Clear resource structure and a single master strings source.
- Pseudo-localization with automated UI tests.
- Integration with a TMS and review by native speakers.
- Correct formatting, plurals, numbers/currencies.
- Lint and custom CI checks.
- Deliberate use of per-app vs per-activity locales.
- QA matrix and per-locale monitoring.

### Detailed Version

#### 1. Resource catalog and structure

- Use `res/values-<locale>` plus `res/xml/locales_config` to declare supported locales and integrate with per-app locale APIs.
- Apply `tools:ignore="MissingTranslation"` only temporarily; CI should fail on missing translations for required locales.
- Use domain-based keys (`auth_`, `billing_`) and avoid concatenating translatable segments.

#### 2. Pseudo-localization and length verification

- Enable pseudo-locales (`en-XA`, `ar-XB`) in `locales_config`.
- Run a dedicated CI job with Espresso/UI tests under pseudo-locales to catch truncation, hard-coded text, and RTL issues.
- Design layouts with at least a +30% text length buffer to avoid clipping in longer languages.

#### 3. Translation workflow

- Keep master strings (e.g., `strings.xml`) in the repository and integrate with a TMS (Smartling, Lokalise, etc.) via custom Gradle tasks for export/import.
- Use translation memory and contextual screenshots to reduce translation errors.
- Include a reviewer loop: native speakers/local market owners review critical-market content.

#### 4. Formatting and pluralization

- Use `getString(R.string.key, formatArgs)` with format placeholders; avoid manual concatenation of formatted segments.
- Use `<plurals>` with correct `quantity` rules for each language (`one`, `other`, etc., according to language-specific rules).
- Use `NumberFormat.getCurrencyInstance(locale)`, `NumberFormat.getInstance(locale)`, and `MeasureFormat` for locale-aware currencies, numbers, and measurement units.

#### 5. CI/CD automation

- Enable Android Lint checks such as `HardcodedText`, `MissingTranslation`, and `UnusedResources`.
- Add custom CI stages (e.g., `./gradlew lintPseudoLocales`, `verifyTranslations`) to validate pseudo-locales and translation consistency.
- Before release, generate translation diffs and require review/approval from content and local market owners.

#### 6. Runtime locale handling

- Respect user choice via per-app locale APIs (e.g., `AppCompatDelegate.setApplicationLocales`, Android 13+ APIs).
- Consider per-activity locales (Android 13 Locale Manager and related APIs) only when truly needed; avoid excessive complexity if a per-app locale suffices.
- Allow in-app language switching for supported locales and, when relevant, sync this preference with your backend.

#### 7. QA and monitoring

- Maintain a QA matrix covering key locales, pseudo-locales, RTL, and diverse screen densities/devices.
- Collect feedback in-app by language/region (translation issues, incorrect formats).
- Monitor crashes/ANRs per locale to catch formatting and placeholder bugs (e.g., mismatched string placeholders, date/number parsing issues).

### Requirements

#### Functional Requirements

- Support multiple locales with centralized string management.
- Integrate with a TMS and automate translation import/export.
- Allow user-selectable language (per-app/per-activity where needed).
- Support pseudo-locales for testing.

#### Non-functional Requirements

- Minimize string duplication and maintain stable keys.
- High localization test coverage (UI, e2e, lint).
- No regressions when adding new locales.
- Scalable localization workflow as markets grow.

### Architecture

- Single master strings source in the repo synchronized with the TMS.
- CI/CD pipeline stages for translation validation, pseudo-locales, lint, and localized release builds.
- Use per-app locale APIs and `locales_config` as the locale configuration layer.
- Observability: logging and metrics by locale to detect issues early.

---

## Follow-ups

- Как синхронизировать переводы для dynamic feature modules и PAD?
- Как управлять юридическими текстами (ToS, Privacy) в разных странах?
- Какие метрики эффективности локализации (LQA defects, time-to-market)?

## References

- [[c-globalization]]
- [Localization](https://developer.android.com/guide/topics/resources/localization)

## Related Questions

- [[c-globalization]]
