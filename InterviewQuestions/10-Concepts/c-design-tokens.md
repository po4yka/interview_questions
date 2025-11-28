---
id: "20251110-180059"
title: "Design Tokens / Design Tokens"
aliases: ["Design Tokens"]
summary: "Foundational concept for interview preparation"
topic: "system-design"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-system-design"
related: [c-design-systems, c-theming, c-material-design, c-design-variables, c-styling]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "system-design"]
date created: Monday, November 10th 2025, 8:37:44 pm
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

Design tokens are platform-agnostic variables that store the atomic design decisions of a product—such as colors, typography, spacing, radii, and shadows—in a structured, reusable format. They provide a single source of truth that can be translated into code for multiple platforms (web, iOS, Android, design tools), ensuring visual consistency and easier theming. Design tokens are central to modern design systems, enabling scalable UI maintenance, brand updates, and dark/light mode support.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Design tokens (дизайн-токены) — это платформенно-независимые переменные, в которых зафиксированы базовые дизайн-решения продукта: цвета, типографика, отступы, скругления, тени и другие визуальные параметры. Они служат единственным источником правды, который автоматически переводится в код для разных платформ (web, iOS, Android, дизайн-инструменты), обеспечивая единообразие интерфейсов и упрощая поддержку тем и брендинга. Дизайн-токены являются ключевым элементом современных дизайн-систем.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Single source of truth: Centralize core visual decisions (colors, typography, spacing, etc.) as data instead of hard-coded values in components.
- Platform agnostic: Stored in neutral formats (e.g., JSON) and then transformed into platform-specific artifacts (CSS variables, SCSS, Android/iOS tokens).
- Consistency and scalability: Reduce visual drift, simplify global changes (e.g., rebranding, accessibility adjustments), and keep large multi-team codebases aligned.
- Theming and customization: Make it easy to implement dark/light modes, brand variants, and product-specific themes without rewriting components.
- Automation and governance: Integrate with design tools and CI pipelines to synchronize tokens, review changes, and enforce design system rules.

## Ключевые Моменты (RU)

- Единый источник правды: Базовые визуальные значения (цвета, шрифты, отступы и др.) хранятся как данные, а не как "захардкоженные" значения в компонентах.
- Платформенная нейтральность: Токены сохраняются в нейтральном формате (например, JSON) и конвертируются в CSS-переменные, SCSS-переменные, ресурсы для Android/iOS и др.
- Последовательность и масштабируемость: Снижают визуальные расхождения, упрощают глобальные изменения (ребрендинг, улучшение доступности) и поддерживают согласованность в больших командах.
- Темизация и кастомизация: Облегчают поддержку светлой/тёмной темы, брендовых вариаций и продуктовых тем без изменений логики компонентов.
- Автоматизация и управление: Интегрируются с дизайн-инструментами и CI/CD, упрощают ревью изменений и помогают применять правила дизайн-системы.

## References

- W3C Design Tokens Community Group Draft: https://design-tokens.github.io/community-group/format/
- Figma Tokens / Design tokens documentation (Figma Help Center)
