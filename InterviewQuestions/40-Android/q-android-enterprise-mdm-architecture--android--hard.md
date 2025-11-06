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
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-enterprise-mdm
created: 2025-11-02
updated: 2025-11-02
tags:
- android/permissions
- android/keystore-crypto
- difficulty/hard
sources:
- url: https://developer.android.com/work/overview
  note: Android Enterprise overview
- url: https://developer.android.com/work/managed-configurations
  note: Managed configurations guide
---

# Вопрос (RU)
> Как спроектировать MDM-решение на Android Enterprise: DPC-приложение, режимы управления (Work Profile, Fully Managed, COPE), политики безопасности и интеграция с Play EMM API?

# Question (EN)
> How do you architect an Android Enterprise MDM solution covering the DPC app, management modes (Work Profile, Fully Managed, COPE), security policies, and Play EMM API integration?

---

## Ответ (RU)

### 1. Архитектура

- **Device Policy Controller (DPC)**: приложение с `DeviceAdminReceiver`, управляющее `DevicePolicyManager`.
- **Backend**: хранит политики, устройства, сертификаты, управляет zero-touch provisioning.
- **Play EMM API**: публикация частных приложений, managed configurations, silent install.

### 2. Режимы управления

- **Work Profile**: личное устройство, управляемый рабочий профиль. DPC — профильный владелец.
- **Fully Managed**: корпоративное устройство, DPC — владелец устройства (Device Owner).
- **COPE**: корпоративное устройство с личным профилем, DPC владеет устройством + управляет work profile.
- **Dedicated**: киоски, single-purpose.

### 3. Provisioning

- QR-код (Android 9+), NFC bump (legacy), zero-touch (через партнёров).
- В provisioning-интент передаётся DPC APK URL, токен, конфигурация.

### 4. Политики

```kotlin
val dpm = context.getSystemService(DevicePolicyManager::class.java)
dpm.setPasswordQuality(adminComponent, DevicePolicyManager.PASSWORD_QUALITY_NUMERIC_COMPLEX)
dpm.addUserRestriction(adminComponent, UserManager.DISALLOW_CONFIG_WIFI)
dpm.setLockTaskPackages(adminComponent, arrayOf("com.company.app"))
```

- Managed configurations (`RestrictionsManager`) для настройки приложений.
- Сертификаты: `installKeyPair`, `setKeyguardDisabledFeatures`.

### 5. Compliance & Telemetry

- События: `DeviceAdminReceiver.onPasswordFailed`, `ACTION_MANAGED_PROFILE_PROVISIONED`.
- Backend должен фиксировать compliance, отправлять уведомления.
- Используйте SafetyNet/Play Integrity для проверки целостности устройства.

### 6. Play EMM API интеграция

- Регистрация enterprise, получение `enterpriseId`.
- Управление приватным каналом приложений, rollout версий.
- Managed config: `ManagedConfigurationsSettings`.

### 7. Безопасность и UX

- Объясните пользователю границы контроля (Work Profile badge).
- Личные данные остаются вне доступа DPC (Work Profile sandbox).
- Аудит: логируйте действия администраторов, обеспечьте экспорт журналов.

---

## Answer (EN)

- Build a DPC app that becomes profile/device owner, enforcing policies via `DevicePolicyManager`.
- Support provisioning via QR, NFC, or zero-touch; feed bootstrap data from your backend.
- Apply password, network, kiosk, and app restrictions; configure managed app settings via `RestrictionsManager`.
- Integrate Play EMM API to distribute private apps, staged rollouts, and managed configs.
- Track compliance events, leverage Play Integrity for device checks, and maintain transparent UX separating work/personal data.

---

## Follow-ups
- Как реализовать BYOD с автоматическим удалением work profile при увольнении?
- Как защитить корпоративные сертификаты на устройстве (KeyChain vs Keystore)?
- Какие требования Google предъявляет к zero-touch партнёрам?

## References
- [[c-enterprise-mdm]]
- https://developer.android.com/work/overview
- https://developer.android.com/work/managed-configurations

## Related Questions

- [[c-enterprise-mdm]]
