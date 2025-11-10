---
id: android-624
title: Android Enterprise MDM Architecture / Архитектура Android Enterprise MDM
aliases:
- Android Enterprise MDM Architecture
- Архитектура Android Enterprise MDM
topic: android
subtopics:
- permissions
- keystore-crypto
- processes
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- q-android-security-best-practices--android--medium
created: 2025-11-02
updated: 2025-11-10
tags:
- android/permissions
- android/keystore-crypto
- android/processes
- difficulty/hard
sources:
- "https://developer.android.com/work/overview"
- "https://developer.android.com/work/managed-configurations"

---

# Вопрос (RU)
> Как спроектировать MDM-решение на Android Enterprise: DPC-приложение, режимы управления (Work Profile, Fully Managed, COPE), политики безопасности и интеграция с Play EMM API?

# Question (EN)
> How do you architect an Android Enterprise MDM solution covering the DPC app, management modes (Work Profile, Fully Managed, COPE), security policies, and Play EMM API integration?

---

## Ответ (RU)

## Краткий вариант

Спроектируйте решение вокруг DPC как profile/device owner, стандартных режимов управления (Work Profile, Fully Managed, COPE, Dedicated), Managed Provisioning (QR, zero-touch, `afw#`), применения политик через `DevicePolicyManager` и managed configurations, с backend-сервером, который хранит политики, статусы соответствия, сертификаты и управляет взаимодействием с Managed Google Play и Android Management API. Обеспечьте чёткое разделение личных/рабочих данных, подробный аудит и использование современных механизмов целостности устройства.

## Подробный вариант

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

- **Device Policy Controller (DPC)**: приложение, регистрируемое как профайл- или владелец устройства через Managed Provisioning (`DevicePolicyManager`), использующее соответствующие API для применения политик. Поддержка только `DeviceAdminReceiver` как основного механизма управления считается легаси для Android Enterprise, поэтому фокус на owner-режимах.
- **Backend**: хранит политики, устройства, сертификаты, статусы соответствия; управляет привязкой устройств и параметрами zero-touch / QR-провижининга.
- **Play EMM API / Android Management API**:
  - управление публикацией приватных приложений и каналами распространения;
  - управление managed configurations;
  - тихая установка/обновление через Managed Google Play.
  - Отметить, что Play EMM API устаревает в пользу Android Management API.

### 2. Режимы управления

- **Work Profile (BYOD)**: личное устройство, управляемый рабочий профиль. DPC выступает профайл-владельцем (profile owner) только в рабочем профиле; доступ к личным данным ограничен.
- **Fully Managed**: корпоративное устройство, DPC — владелец устройства (device owner), полный контроль над системными политиками и приложениями.
- **COPE**: корпоративное устройство с личным профилем. DPC — владелец устройства + управляет рабочим профилем; ограничения и сбор данных на личном профиле ограничены согласно требованиям Android Enterprise (нельзя читать личные данные/приложения).
- **Dedicated**: киоски и single-purpose; device owner с Lock Task Mode, ограниченный набор приложений.

### 3. Provisioning

- Используйте стандартный **Managed Provisioning**:
  - QR-код (Android 9+), содержащий extras для установки DPC / регистрации в EMM;
  - NFC bump (legacy) для старых устройств;
  - zero-touch provisioning через партнёров: привязка DPC / EMM-профиля на уровне поставщика;
  - `afw#dpc` / идентификатор для загрузки DPC из Managed Google Play.
- В provisioning-интент передаются параметры: идентификатор DPC, токен регистрации, URL/endpoint бэкенда, начальная конфигурация; не полагаться только на прямой APK URL вне управляемого сценария.

### 4. Политики

```kotlin
val dpm = context.getSystemService(DevicePolicyManager::class.java)

dpm.setPasswordQuality(adminComponent, DevicePolicyManager.PASSWORD_QUALITY_NUMERIC_COMPLEX)
dpm.addUserRestriction(adminComponent, UserManager.DISALLOW_CONFIG_WIFI)
dpm.setLockTaskPackages(adminComponent, arrayOf("com.company.app"))
```

- Используйте managed configurations для настройки приложений через Managed Google Play (на уровне EMM), а на устройстве — через соответствующие API (`RestrictionsManager`/app restrictions) для чтения значений.
- Сертификаты и ключи:
  - установка клиентских сертификатов через `installKeyPair`/KeyChain в зависимость от режима управления;
  - ограничение функций локскрина через `setKeyguardDisabledFeatures` и другие политики.

### 5. Compliance & Telemetry

- События: `DeviceAdminReceiver.onPasswordFailed`, `ACTION_MANAGED_PROFILE_PROVISIONED`, события смены политики и т.п.
- Backend должен фиксировать состояние compliance (root/jailbreak сигналы, версии ОС, применённые политики), инициировать ремедиацию и уведомления.
- Для проверки целостности устройства и анти-рут/эмуляция проверок использовать **Play Integrity API** (SafetyNet Attestation считается легаси и не рекомендован для новых реализаций).

### 6. Play EMM API интеграция

- Регистрация enterprise и получение `enterpriseId` (для существующих интеграций); для новых решений — рассмотреть Android Management API как рекомендуемый путь.
- Управление приватным каналом приложений, rollout версий через Managed Google Play.
- Управление managed configurations (app restrictions) для поддерживаемых приложений через соответствующие API/консоль, на устройстве — через `ManagedConfigurationsSettings`/чтение конфигураций приложением.

### 7. Безопасность и UX

- Чётко объясняйте пользователю границы контроля (иконка Work Profile, уведомления, политика конфиденциальности).
- В режиме Work Profile личные данные и приложения остаются вне доступа DPC (sandbox профиля); на COPE-устройствах соблюдайте ограничения доступа к личному профилю.
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
  - perform silent installs/updates where allowed.
  - Note: Play EMM API is being superseded by Android Management API.

### 2. Management modes

- **Work Profile (BYOD)**: personal device, managed work profile. DPC is profile owner only inside the work profile; personal data remains isolated.
- **Fully Managed**: corporate-only device; DPC is device owner with full policy and app control.
- **COPE**: corporate-owned with personal profile; DPC is device owner and controls the work profile while respecting strict limits on access to personal side data.
- **Dedicated**: kiosk / single-purpose devices using device owner and Lock Task Mode.

### 3. Provisioning

- Use standard **Managed Provisioning** flows:
  - QR code (Android 9+) with provisioning extras to install/configure the DPC and register with your backend;
  - NFC bump (legacy) for older devices;
  - zero-touch provisioning via resellers to auto-assign the DPC/EMM configuration;
  - `afw#<dpc-id>` identifier to fetch the DPC from Managed Google Play.
- Pass provisioning parameters such as DPC identifier, enrollment token, backend endpoint, and initial policies; do not rely solely on raw APK URLs outside the managed flow.

### 4. Policies

```kotlin
val dpm = context.getSystemService(DevicePolicyManager::class.java)

dpm.setPasswordQuality(adminComponent, DevicePolicyManager.PASSWORD_QUALITY_NUMERIC_COMPLEX)
dpm.addUserRestriction(adminComponent, UserManager.DISALLOW_CONFIG_WIFI)
dpm.setLockTaskPackages(adminComponent, arrayOf("com.company.app"))
```

- Use managed configurations via Managed Google Play/EMM to configure apps; on-device apps consume these via `RestrictionsManager`/app restrictions.
- Certificates and keys:
  - install client certificates using `installKeyPair` / KeyChain as applicable to the ownership mode;
  - adjust lockscreen/security UX via `setKeyguardDisabledFeatures` and related policies.

### 5. Compliance & Telemetry

- Listen to events such as `DeviceAdminReceiver.onPasswordFailed`, `ACTION_MANAGED_PROFILE_PROVISIONED`, and policy change signals.
- Backend should evaluate compliance (OS version, policy status, signals of compromise), trigger remediation, and send alerts.
- Prefer **Play Integrity API** for device integrity and tamper checks; treat SafetyNet Attestation as legacy.

### 6. Play EMM API integration

- Register an enterprise and obtain `enterpriseId` for existing Play EMM API-based flows; for new implementations, favor Android Management API.
- Manage private app channels and staged rollouts via Managed Google Play.
- Configure managed app settings (managed configurations) via the appropriate EMM / Play APIs, surfaced on-device as `ManagedConfigurationsSettings`/app restrictions.

### 7. Security and UX

- Be transparent about control boundaries (Work Profile badge, notifications, clear privacy documentation).
- In Work Profile mode, ensure personal data/apps remain inaccessible to the DPC; on COPE devices, respect platform-imposed separation and do not over-collect from the personal profile.
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

