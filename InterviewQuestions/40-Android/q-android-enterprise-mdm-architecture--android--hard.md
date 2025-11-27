---
id: android-624
title: Android Enterprise MDM Architecture / Архитектура Android Enterprise MDM
aliases: [Android Enterprise MDM Architecture, Архитектура Android Enterprise MDM]
topic: android
subtopics:
  - keystore-crypto
  - permissions
  - processes
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - q-android-lint-tool--android--medium
  - q-android-security-best-practices--android--medium
  - q-clean-architecture-android--android--hard
  - q-quick-settings-tiles-architecture--android--medium
created: 2025-11-02
updated: 2025-11-10
tags: [android/keystore-crypto, android/permissions, android/processes, difficulty/hard]
sources:
  - "https://developer.android.com/work/managed-configurations"
  - "https://developer.android.com/work/overview"

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---
# Вопрос (RU)
> Как спроектировать MDM-решение на Android Enterprise: DPC-приложение, режимы управления (Work Profile, Fully Managed, COPE), политики безопасности и интеграция с Play EMM API?

# Question (EN)
> How do you architect an Android Enterprise MDM solution covering the DPC app, management modes (Work Profile, Fully Managed, COPE), security policies, and Play EMM API integration?

---

## Ответ (RU)

## Краткая Версия
Спроектируйте решение вокруг DPC как profile/device owner, стандартных режимов управления (Work Profile, Fully Managed, COPE, Dedicated), Managed Provisioning (QR, zero-touch, `afw#`), применения политик через `DevicePolicyManager` и managed configurations, с backend-сервером, который хранит политики, статусы соответствия, сертификаты и управляет взаимодействием с Managed Google Play и Android Management API. Обеспечьте чёткое разделение личных/рабочих данных, подробный аудит и использование современных механизмов проверки целостности устройства.

## Подробная Версия
### Требования

- Функциональные:
  - Регистрация и управление устройствами во всех режимах Android Enterprise.
  - Применение политик безопасности (пароль, шифрование, ограничения функций, приложения).
  - Управление установкой и конфигурацией корпоративных приложений.
  - Защита и управление корпоративными сертификатами и ключами.
  - Мониторинг соответствия (compliance), сбор телеметрии и ремедиация.
  - Интеграция с Managed Google Play / Android Management API.
- Нефункциональные:
  - Масштабируемость для большого парка устройств.
  - Высокая надёжность и отказоустойчивость backend.
  - Минимальное влияние на UX и батарею.
  - Соответствие требованиям конфиденциальности и регуляторики.

### Архитектура

### 1. Архитектура

- **Device Policy Controller (DPC)**: приложение, регистрируемое как владелец профиля или устройства через Managed Provisioning, использующее `DevicePolicyManager` для применения политик. Поддержка только `DeviceAdminReceiver` как основного механизма управления считается легаси для Android Enterprise, поэтому фокус на owner-режимах.
- **Backend**: хранит политики, устройства, сертификаты, статусы соответствия; управляет привязкой устройств и параметрами zero-touch / QR-провижининга.
- **Play EMM API / Android Management API**:
  - управление публикацией приватных приложений и каналами распространения через Managed Google Play;
  - управление managed configurations;
  - тихая установка/обновление через Managed Google Play там, где это разрешено политикой;
  - отметить, что Play EMM API считается устаревающим и заменяется Android Management API для новых реализаций.

### 2. Режимы Управления

- **Work Profile (BYOD)**: личное устройство, управляемый рабочий профиль. DPC выступает владельцем профиля (profile owner) только в рабочем профиле; доступ к личным данным запрещён платформой.
- **Fully Managed**: корпоративное устройство, DPC — владелец устройства (device owner), полный контроль над системными политиками и приложениями.
- **COPE**: корпоративное устройство с личным профилем. DPC — владелец устройства и владелец рабочего профиля; при этом доступ к данным и приложениям личного профиля строго ограничен требованиями Android Enterprise (нельзя читать личные данные/приложения или ослаблять их защиту).
- **Dedicated**: киоски и single-purpose; device owner с Lock Task Mode, ограниченный набор приложений.

### 3. Provisioning

- Используйте стандартный **Managed Provisioning**:
  - QR-код (Android 9+), содержащий extras для установки DPC / регистрации в EMM;
  - NFC bump (legacy) для старых устройств;
  - zero-touch provisioning через партнёров: привязка DPC / EMM-профиля на уровне поставщика;
  - использование идентификатора `afw#<dpc-id>` на экране первичной настройки для загрузки DPC из Managed Google Play.
- В provisioning-интент передаются параметры: идентификатор DPC, токен регистрации, URL/endpoint бэкенда, начальная конфигурация; не полагаться только на прямой APK URL вне управляемого сценария.

### 4. Политики

```kotlin
val dpm = context.getSystemService(DevicePolicyManager::class.java)

// Требуется корректно зарегистрированный компонент администратора (DeviceAdminReceiver)
// и соответствующие права владельца профиля или устройства.

dpm.setPasswordQuality(adminComponent, DevicePolicyManager.PASSWORD_QUALITY_NUMERIC_COMPLEX)
dpm.addUserRestriction(adminComponent, UserManager.DISALLOW_CONFIG_WIFI)
dpm.setLockTaskPackages(adminComponent, arrayOf("com.company.app"))
```

- Используйте managed configurations для настройки приложений через Managed Google Play (на уровне EMM), а на устройстве — через соответствующие API (`RestrictionsManager`/app restrictions) для чтения значений.
- Сертификаты и ключи:
  - установка клиентских сертификатов через `installKeyPair` / KeyChain в зависимости от режима управления и наличия прав владельца;
  - ограничение функций локскрина через `setKeyguardDisabledFeatures` и другие политики.

### 5. Compliance & Telemetry

- События: `DeviceAdminReceiver.onPasswordFailed`, `ACTION_MANAGED_PROFILE_PROVISIONED`, события смены политики и т.п.
- Backend должен фиксировать состояние compliance (сигналы рутования/компрометации устройства, версии ОС, применённые политики), инициировать ремедиацию и уведомления.
- Для проверки целостности устройства и анти-root/эмуляция проверок использовать Play Integrity API (SafetyNet Attestation считается легаси и не рекомендован для новых реализаций).

### 6. Play EMM API Интеграция

- Для существующих интеграций: регистрация enterprise и получение `enterpriseId` в рамках Play EMM API; для новых решений — предпочтительно использовать Android Management API как рекомендуемый путь.
- Управление приватным каналом приложений и rollout версий через Managed Google Play.
- Управление managed configurations (app restrictions) для поддерживаемых приложений через соответствующие API/консоль; на устройстве приложения читают значения через `RestrictionsManager` / app restrictions (системный UI «Managed configurations» выступает только как точка просмотра/изменения, если включён).

### 7. Безопасность И UX

- Чётко объясняйте пользователю границы контроля (иконка Work Profile, уведомления, политика конфиденциальности).
- В режиме Work Profile личные данные и приложения остаются вне доступа DPC (sandbox профиля); на COPE-устройствах соблюдайте ограничения доступа к личному профилю и не пытайтесь обходить платформенные механизмы разделения.
- Аудит: логируйте действия администраторов и критичные операции (wipe, reset, изменение политик), обеспечьте экспорт журналов и контроль доступа.

---

## Answer (EN)

## Short Version
Center the solution around a DPC acting as profile/device owner, standard Android Enterprise modes (Work Profile, Fully Managed, COPE, Dedicated), Managed Provisioning (QR, zero-touch, `afw#`), and policy enforcement via `DevicePolicyManager` plus managed configurations, backed by a server that stores policies, compliance state, certificates, and integrates with Managed Google Play and Android Management API. Ensure strict work/personal separation, strong integrity checks, and comprehensive auditing.

## Detailed Version
### Requirements

- Functional:
  - Enroll and manage devices across Android Enterprise modes.
  - Enforce security policies (password, encryption, restrictions, apps).
  - Manage deployment and configuration of corporate apps.
  - Protect and manage corporate certificates and keys.
  - Monitor compliance and collect telemetry with remediation flows.
  - Integrate with Managed Google Play / Android Management API.
- Non-functional:
  - Scalability for large device fleets.
  - High availability and reliability of the backend.
  - Minimal impact on UX and battery.
  - Compliance with privacy/regulatory requirements.

### Architecture

### 1. Architecture

- Build a **DPC app** that is set as profile owner or device owner via Managed Provisioning and enforces policies using `DevicePolicyManager`. Treat pure `DeviceAdminReceiver`-only control as legacy; focus on Android Enterprise owner modes.
- Have a **backend** that stores policies, devices, certificates, compliance states, and orchestrates zero-touch / QR provisioning parameters.
- Integrate with **Play EMM API / Android Management API** to:
  - distribute private apps via Managed Google Play;
  - control managed configurations;
  - perform silent installs/updates where allowed by policy and mode;
  - note that Play EMM API is effectively deprecated and superseded by Android Management API for new implementations.

### 2. Management Modes

- **Work Profile (BYOD)**: personal device, managed work profile. DPC is profile owner only inside the work profile; personal data is isolated by the platform.
- **Fully Managed**: corporate-only device; DPC is device owner with full policy and app control.
- **COPE**: corporate-owned with personal profile; DPC is device owner and work profile owner, but access to personal profile data/apps is strictly constrained by Android Enterprise (cannot read or weaken protection of personal data/apps).
- **Dedicated**: kiosk / single-purpose devices using device owner and Lock Task Mode.

### 3. Provisioning

- Use standard **Managed Provisioning** flows:
  - QR code (Android 9+) with provisioning extras to install/configure the DPC and register with your backend;
  - NFC bump (legacy) for older devices;
  - zero-touch provisioning via resellers to auto-assign the DPC/EMM configuration;
  - entering an `afw#<dpc-id>` identifier during initial setup to fetch the DPC from Managed Google Play.
- Pass provisioning parameters such as DPC identifier, enrollment token, backend endpoint, and initial policies; do not rely solely on raw APK URLs outside the managed flow.

### 4. Policies

```kotlin
val dpm = context.getSystemService(DevicePolicyManager::class.java)

// Requires a properly registered DeviceAdminReceiver component
// and appropriate profile/device owner privileges.

dpm.setPasswordQuality(adminComponent, DevicePolicyManager.PASSWORD_QUALITY_NUMERIC_COMPLEX)
dpm.addUserRestriction(adminComponent, UserManager.DISALLOW_CONFIG_WIFI)
dpm.setLockTaskPackages(adminComponent, arrayOf("com.company.app"))
```

- Use managed configurations via Managed Google Play/EMM to configure apps; on-device apps consume these via `RestrictionsManager` / app restrictions.
- Certificates and keys:
  - install client certificates using `installKeyPair` / KeyChain as applicable to the ownership mode and granted privileges;
  - tune lockscreen/security behavior via `setKeyguardDisabledFeatures` and related policies.

### 5. Compliance & Telemetry

- Listen to events such as `DeviceAdminReceiver.onPasswordFailed`, `ACTION_MANAGED_PROFILE_PROVISIONED`, and policy change broadcasts.
- Backend should evaluate compliance (OS version, applied policies, rooting/compromise signals), trigger remediation, and send alerts.
- Prefer Play Integrity API for device integrity and tamper checks; treat SafetyNet Attestation as legacy.

### 6. Play EMM API Integration

- For existing Play EMM API-based flows, register an enterprise and obtain `enterpriseId`; for new implementations, favor Android Management API as the recommended approach.
- Manage private app channels and staged rollouts via Managed Google Play.
- Configure managed app settings (managed configurations) via the appropriate EMM / Play APIs; on-device, applications read these values via `RestrictionsManager` / app restrictions (the system "Managed configurations" UI, where present, is just a surface for these values).

### 7. Security and UX

- Be transparent about control boundaries (Work Profile badge, notifications, clear privacy documentation).
- In Work Profile mode, ensure personal data/apps remain inaccessible to the DPC; on COPE devices, respect platform separation and do not attempt to circumvent it.
- Implement administrative audit logging for sensitive actions (remote wipe, reset, policy changes) and provide secure export/access to these logs.

---

## Follow-ups (RU)
- Как реализовать BYOD с автоматическим удалением work profile при увольнении?
- Как защитить корпоративные сертификаты на устройстве (KeyChain vs Keystore)?
- Какие требования Google предъявляет к zero-touch партнёрам?

## Follow-ups (EN)
- How to implement BYOD with automatic work profile removal upon offboarding?
- How to protect corporate certificates on the device (KeyChain vs Keystore)?
- What requirements does Google set for zero-touch resellers/partners?

## References (RU)
- https://developer.android.com/work/overview
- https://developer.android.com/work/managed-configurations

## References (EN)
- https://developer.android.com/work/overview
- https://developer.android.com/work/managed-configurations

## Related Questions

- [[q-android-security-best-practices--android--medium]]

## Concepts

- [[c-android]]
