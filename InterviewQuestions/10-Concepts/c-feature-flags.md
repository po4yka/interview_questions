---\
id: "20251110-150359"
title: "Feature Flags / Feature Flags"
aliases: ["Feature Flags"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-ci-cd"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---\

# Summary (EN)

Feature flags (feature toggles) are a technique for enabling or disabling application behavior at runtime via configuration rather than code changes or redeployments. They allow teams to ship code safely behind toggles, perform gradual rollouts, run A/B tests, and quickly revert problematic features. Widely used in continuous delivery, they decouple deployment from release, reducing risk and improving control over production behavior.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Feature flags (feature toggles, фиче-флаги) — это техника, позволяющая включать и отключать функциональность приложения во время выполнения через конфигурацию, без изменения кода и повторного деплоя. Они позволяют безопасно выкатывать функционал под флагами, делать поэтапные раскатки, проводить A/B-тесты и быстро отключать проблемные фичи. Широко применяются в процессах непрерывной поставки, разделяя деплой и релиз и снижая риски в продакшене.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Controlled rollout: Enable features gradually (by percentage, region, platform, user segment) to reduce risk and monitor impact before full release.
- Safe rollback: Disable a feature instantly via configuration if issues appear in production, without hotfix builds or redeploys.
- Experimentation: Support A/B testing and canary releases by routing different users to different behaviors under separate flags.
- Configuration-driven: Implemented via configuration files, remote config services, or dedicated flag platforms; must be designed for low latency and high availability.
- `Lifecycle` & tech debt: Flags should have clear ownership and expiry; long-lived or forgotten flags complicate code, tests, and reasoning.

## Ключевые Моменты (RU)

- Контролируемый rollout: Позволяют включать функциональность постепенно (по проценту пользователей, региону, платформе, сегментам), снижая риск и отслеживая эффект.
- Безопасный откат: Дают возможность мгновенно выключить проблемную фичу конфигурацией, без срочных патчей и повторных деплоев.
- Эксперименты: Используются для A/B-тестов и canary-релизов, направляя разных пользователей на разные варианты поведения под разными флагами.
- Управление конфигурацией: Реализуются через конфиги, удалённые конфигурационные сервисы или специализированные платформы; важно обеспечить низкие задержки и надёжность.
- Жизненный цикл и технический долг: Для каждого флага нужны владелец и сроки удаления; «забытые» флаги усложняют кодовую базу, тестирование и понимание системы.

## References

- https://martinfowler.com/articles/feature-toggles.html
