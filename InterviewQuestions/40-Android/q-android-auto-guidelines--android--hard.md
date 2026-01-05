---
id: android-622
title: Android Auto Guidelines / Руководство Android Auto
aliases: [Android Auto Guidelines, Руководство Android Auto]
topic: android
subtopics: [auto]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-auto, q-android-auto-guidelines--android--hard, q-android-lint-tool--android--medium, q-main-thread-android--android--medium, q-parsing-optimization-android--android--medium]
created: 2025-11-02
updated: 2025-11-11
tags: [android/auto, difficulty/hard]
sources:
  - "https://developer.android.com/training/cars/apps"
  - "https://developer.android.com/training/cars/apps/media"

---
# Вопрос (RU)
> Как спроектировать и сертифицировать Android Auto / Automotive OS приложение: соблюсти ограничений по отвлечению, шаблонам, голосовому управлению и процессу ревью?

# Question (EN)
> How do you design and certify an Android Auto / Automotive OS app, meeting distraction guidelines, template constraints, voice requirements, and review processes?

---

## Ответ (RU)

## Краткая Версия
- Выбрать поддерживаемую категорию и использовать только шаблоны Car App Library.
- Соблюдать правила снижения отвлечения водителя, опираться на ограничения платформы.
- Интегрировать голос / Assistant и поддерживаемые API вместо кастомного UI.
- Учитывать различия Android Auto (phone-based) и Android Automotive OS (standalone).
- Пройти чек-листы, self-review и ревью Google, затем мониторить качество и соблюдение политик.

## Подробная Версия
#### Требования

- Функциональные:
  - Соответствие поддерживаемым категориям (навигация, медиа, сообщения, POI и т.п.).
  - Использование шаблонов Car App Library, корректная навигация, голосовые сценарии.
  - Поддержка безопасных сценариев взаимодействия при движении.
- Нефункциональные:
  - Минимизация отвлечения: ограниченные действия, предсказуемые паттерны UI.
  - Высокая стабильность, низкий уровень ANR/crash, быстрый отклик.
  - Соответствие политикам Google Play и гайдам Android Auto/Automotive OS.

#### Архитектура

- Клиент (car app) на основе Car App Library / `CarAppService`.
- Бизнес-логика и данные вынесены в общие модули (reuse между Auto и Automotive OS, а также handheld-приложением).
- Интеграция с backend при необходимости (контент, маршруты, аккаунты) с учётом ограничений сети и времени отклика.
- Использование OEM/vehicle API (Automotive OS) через `CarHardwareManager` и др. с строгими разрешениями.

#### Категория И Шаблоны

- Android Auto поддерживает ограниченный набор категорий (Navigation, POI, Media, Messaging и др., согласно актуальной документации).
- Используйте Car App Library (`ListTemplate`, `PaneTemplate`, `MapTemplate`, `NavigationTemplate` и т.п.); произвольного кастомного UI и произвольных жестов нет — только шаблоны.
- Навигационные приложения обязаны предоставлять маршруты и поддерживать turn-by-turn через соответствующие навигационные шаблоны (например, `NavigationTemplate`).

#### Правила Отвлечения Водителя (Driver Distraction)

- Логика безопасности задаётся библиотекой и шаблонами: ограничены длины списков, количество интеракций, ввод текста и доступные действия при движении.
- Длинные формы, произвольный текстовый ввод и сложные пошаговые флоу при движении запрещены; используйте голос, упрощённые шаблоны или companion app для сложных операций.
- При движении часть UI и действий автоматически блокируется или урезается в зависимости от политики Android Auto/Automotive OS (например, ограничения на длину списков, ввод, мультимедиа).

#### Голос И Assistant

- Интегрируйте голосовые сценарии через стандартные механизмы: обработка поиска, навигационных запросов и действий медиаплеера, совместимых с Assistant (например, поддержка поиска и команд через соответствующие callback'и Car App Library и интент-фильтры).
- Для сообщений используйте поддерживаемые API (например, интеграция с SMS/MMS/notification messaging и соответствующими car messaging шаблонами), а не кастомные UI решения.
- Media-приложения должны корректно обрабатывать голосовой поиск и команды (search / play / pause и т.п.) через предусмотренные методы (например, `onSearch`/intent-based запросы), чтобы работать с Assistant и голосом автомобиля.

#### Automotive OS Vs Android Auto

- Для Android Auto на телефоне вы создаёте car app, использующую Car App Library и шаблоны; UI рендерится на головном устройстве и подчиняется ограничениям безопасности.
- Для Android Automotive OS (AAOS) можно создавать standalone-приложения, которые устанавливаются напрямую на головное устройство; для шаблонных приложений также используется Car App Library и `CarAppService`.
- Для доступа к данным автомобиля на Automotive OS используйте соответствующие API (например, `CarHardwareManager` и связанные интерфейсы), с учётом разрешений, OEM-ограничений и конфиденциальности.
- Требуется взаимодействие с OEM: требования к UI, плотности экрана, брендингу и, при необходимости, OEM-сертификация.

#### Процесс Сертификации / Ревью

1. Соберите car app в соответствии с требованиями Car App Library и пройдите внутренний QA по официальным чек-листам (Media, Navigation, Messaging и др.).
2. Выполните self-review в Play Console: заполните форму для автомобильных приложений, подтвердите соответствие категориям и политикам.
3. Пройдите ревью Google: проверка использования шаблонов, отсутствия нарушений driver distraction, корректной голосовой интеграции и общего качества (стабильность, отклик UI).
4. После запуска отслеживайте метрики (ANR, crash rate, latency взаимодействий) и обновления политик/гайдлайнов Android Auto и Automotive OS; при необходимости вносите корректировки.

#### Тестирование

- Используйте актуальный эмулятор Android for Cars / Android Automotive OS и инструменты, рекомендованные Google (вместо устаревшего Desktop Head Unit, если он недоступен в текущем стеке).
- Тестируйте на эмуляторе с нужным уровнем Car App Library / Car API и различными конфигурациями дисплея.
- По возможности прогоните сценарии на реальных головных устройствах или тестовых стендах (touch target size, читаемость, блики, поведение при движении).

#### Монетизация И Policy

- Нельзя показывать отвлекающую рекламу или видео-контент на экранах, доступных при движении, и нарушать driver distraction policy.
- Флоу покупок и ввода платёжных данных должен соответствовать политикам безопасности: избегайте сложных транзакций при движении, переносите их в безопасный контекст (остановка, companion app, голосовые сценарии, если разрешены).
- Для цифровых товаров применяется стандартное требование использования Play Billing (если релевантно для вашего сценария и поддерживается на целевой платформе).

---

## Answer (EN)

## Short Version
- Pick a supported category and use only Car App Library templates.
- Rely on platform driver distraction rules and avoid complex flows while driving.
- Integrate voice/Assistant and supported APIs instead of custom in-car UI.
- Distinguish between Android Auto (phone-based) and Android Automotive OS (standalone).
- Pass checklists, self-review, Google review, and then monitor quality and policy compliance.

## Detailed Version
#### Requirements

- Functional:
  - Fit one of the allowed categories (navigation, media, messaging, POI, etc.).
  - Use Car App Library templates with proper navigation and voice flows.
  - Support safe in-car interaction patterns while driving.
- Non-functional:
  - Minimize distraction: constrained actions, predictable layouts.
  - High stability, low ANR/crash rates, fast response.
  - Compliance with Google Play policies and Android Auto/Automotive OS guidelines.

#### Architecture

- Car app client built with Car App Library / `CarAppService`.
- Shared business logic/data modules reused across Android Auto, Automotive OS, and handheld app.
- Backend integration (routes, content, accounts) designed for constrained networks and latency.
- Use OEM/vehicle APIs on Automotive OS via `CarHardwareManager` etc., guarded by strict permissions.

#### Category and Templates

- Choose an allowed car app category (Navigation, POI, Media, Messaging, etc.).
- Build only with Car App Library templates (`ListTemplate`, `PaneTemplate`, `MapTemplate`, `NavigationTemplate`, etc.); arbitrary custom UI and free-form layouts/gestures are not allowed.
- Navigation apps must provide routes and turn-by-turn guidance via the appropriate navigation templates (e.g., `NavigationTemplate`).

#### Driver Distraction Rules

- Rely on the built-in safety model: templates and platform rules cap list length, interactions, text input, and available actions while driving.
- Long forms, free-form text input, and complex multi-step flows while driving are prohibited; offload them to voice, simplified templates, or a companion app.
- While the vehicle is in motion, parts of the UI/actions are automatically blocked or constrained based on Android Auto/Automotive OS policies (e.g., list size limits, input restrictions, media constraints).

#### Voice and Assistant

- Implement voice flows via supported mechanisms: handle search, navigation, and media commands in a way compatible with Assistant and in-car voice (Car App Library callbacks, intent filters).
- For messaging, use supported APIs and car messaging templates (e.g., notification-based messaging integration), not custom conversation UIs.
- Media apps must properly handle voice search and playback commands (search / play / pause, etc.) through the provided methods (e.g., `onSearch`/intent-based requests) to work well with Assistant and car voice systems.

#### Automotive OS Vs Android Auto

- Android Auto (phone-based): you build a car app that uses Car App Library and templates; it runs on the phone, renders UI on the head unit, and is strictly constrained by safety and templates.
- Android Automotive OS (AAOS): you can ship standalone APKs installed directly on the head unit; for template-based experiences you still use Car App Library and `CarAppService`.
- Use Automotive OS vehicle data APIs (e.g., `CarHardwareManager` and related interfaces) with proper permissions, OEM constraints, and privacy protections.
- Coordinate with OEMs regarding UI requirements, densities, branding, and any OEM-specific certification.

#### Certification / Review Process

1. Build your car app according to Car App Library requirements and run internal QA using official quality checklists (Media, Navigation, Messaging, etc.).
2. Complete the car app self-review in Play Console: declare category, answer policy questions, and confirm compliance.
3. Undergo Google review: validation of template usage, distraction compliance, correct voice integration, and overall quality (stability, responsiveness).
4. Post-launch, continuously monitor metrics (ANR, crash rate, interaction latency) and track Android Auto/Automotive OS policy/guideline updates; update the app as needed.

#### Testing

- Test on the official Android for Cars / Android Automotive OS emulators and tools recommended by Google instead of the deprecated Desktop Head Unit.
- Validate behavior across different Car App Library/API levels and multiple display configurations.
- When possible, test on real head units or test rigs (touch target size, readability, glare, behavior while driving).

#### Monetization and Policy

- Do not show distracting ads or video content on screens available while driving; comply with driver distraction policies.
- Purchase and payment flows must be safe: avoid complex transactions while the vehicle is moving; move them to safe contexts (vehicle stopped, companion app, or permitted voice flows).
- For digital goods, use Play Billing when required and when supported for the target platform.

---

## Дополнительные Вопросы (RU)

- Как реализовать гибридный подход (Auto + Automotive) с общим кодом?
- Какие метрики latency отслеживает Google при ревью?
- Как организовать интеграцию с Assistant для кастомных команд?

## Follow-ups

- How to implement a hybrid (Auto + Automotive) approach with shared code?
- Which latency metrics does Google track during review?
- How to integrate with Assistant for custom commands?

## Ссылки (RU)

- [[c-android-auto]]
- https://developer.android.com/training/cars/apps
- https://developer.android.com/training/cars/apps/media

## References

- [[c-android-auto]]
- https://developer.android.com/training/cars/apps
- https://developer.android.com/training/cars/apps/media

## Связанные Вопросы (RU)

- [[c-android-auto]]
- [[q-android-auto-guidelines--android--hard]]
- [[q-android-lint-tool--android--medium]]
- [[q-main-thread-android--android--medium]]
- [[q-parsing-optimization-android--android--medium]]

## Related Questions

- [[c-android-auto]]
- [[q-android-auto-guidelines--android--hard]]
- [[q-android-lint-tool--android--medium]]
- [[q-main-thread-android--android--medium]]
- [[q-parsing-optimization-android--android--medium]]
