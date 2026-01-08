---
id: c-stateflow
title: StateFlow / StateFlow
aliases: [StateFlow]
topic: kotlin
subtopics: [coroutines, flow, ui-state]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-flow, c-livedata, c-sharedflow]
created: 2025-01-08
updated: 2025-01-08
tags: [kotlin, coroutines, flow, concept, difficulty/medium]
---

# Summary (EN)

**StateFlow** is a state-holder observable flow that emits the current and new state updates to its collectors. It is part of Kotlin Coroutines' Flow API and is designed to replace `LiveData` in modern Android development. Unlike a standard `Flow`, `StateFlow` is hot (always active) and always has a value.

# Сводка (RU)

**StateFlow** - это observable flow, хранящий состояние, который эмитит текущие и новые обновления состояния своим подписчикам. Является частью API Kotlin Coroutines Flow и предназначен для замены `LiveData` в современной Android разработке. В отличие от обычного `Flow`, `StateFlow` является "горячим" (всегда активным) и всегда имеет значение.
