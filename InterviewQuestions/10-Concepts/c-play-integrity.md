---
id: ivc-20251102-006
title: Play Integrity API / Play Integrity API
aliases:
  - Play Integrity
  - Play Integrity Attestation
kind: concept
summary: Google Play service providing device and account integrity verdicts replacing SafetyNet
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - security
  - integrity
  - attestation
---

# Summary (EN)

**Play Integrity API** delivers signed verdicts about device, app, and licensing integrity, replacing SafetyNet Attestation. It supports classic integrity levels, license checks, account activity evaluation, and capability tokens for offline scenarios.

# Сводка (RU)

**Play Integrity API** — сервис Google Play, предоставляющий подписанные вердикты о целостности устройства, приложения и лицензии, заменяющий SafetyNet. Он поддерживает уровни integrity, проверку лицензии, оценку активности аккаунта и capability-токены для офлайн сценарием.

## Components

- Client SDK (`IntegrityManager`) для запроса токена
- `IntegrityTokenRequest` + cloud project binding
- Backend verification через `playintegrity.googleapis.com/v1`
- Device integrity (MEETS_BASIC/MEETS_DEVICE) и account integrity verdicts

## Considerations

- Требует Play App Signing и связку с Google Cloud Project.
- Ответы подписаны; проверка должна происходить на сервере.
- Capability Tokens позволяют кешировать verdict до 24 часов.

