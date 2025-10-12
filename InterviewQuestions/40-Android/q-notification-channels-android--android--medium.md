---
id: q-notification-channels-android--android--medium--1728115260000
title: "Notification Channels / Каналы уведомлений"
topic: android
aliases:
  - Notification Channels
  - Каналы уведомлений
date_created: 2025-10-05
date_modified: 2025-10-05
status: draft
original_language: en
language_tags:
  - en
  - ru
type: question
category: android
difficulty: medium
subtopics:
  - notifications
  - ui-widgets
tags:
  - android
  - notifications
  - notification-channels
  - android8
  - importance
  - difficulty/medium
moc: moc-android
source: "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20do%20you%20know%20about%20notification.md"
---

# Notification Channels / Каналы уведомлений

# Question (EN)
> 

What do you know about notification channels?

## Answer (EN)
A notification is a message that Android displays outside your app's UI to provide the user with reminders, communication from other people, or other timely information from your app. Users can tap the notification to open your app or take an action directly from the notification.

### Notification Usage

Notifications are intended to inform users about events in your app. These two types of notifications are the most effective:
- Communication from other users
- Well-timed and informative task reminders

**Notification Anatomy:**
- Header area
- Content area
- Action area

**How notifications may be noticed:**
- Showing a status bar icon
- Appearing on the lock screen
- Playing a sound or vibrating
- Peeking onto the current screen
- Blinking the device's LED

### Notification Drawer

The notification drawer in Android typically shows notifications in reverse-chronological order, with adjustments influenced by:
- The app's stated notification priority or importance
- Whether the notification recently alerted the user with a sound or vibration
- Any people attached to the notification and whether they are starred contacts
- Whether the notification represents an important ongoing activity, such as a phone call in progress or music playing

Starting in Android O, the Android system may alter the appearance of some notifications at the top and bottom of the list by adding emphasis or deemphasis, to help the user scan content.

### Grouping

Your app can present multiple notifications according to hierarchy:
- A parent notification displays a summary of its child notifications
- If the parent notification is expanded by the user, all child notifications are revealed
- A child notification may be expanded to reveal its entire content

Child notifications are presented without duplicate header information. For example, if a child notification has the same app icon as its parent, then the child's header doesn't include an icon.

Child notifications should be understandable if they appear solo, as the system may show them outside of the group when they arrive.

### Types of Notifications

Notifications are considered either transactional or non-transactional.

#### Transactional

Transactional notifications provide content that a user must receive at a specific time in order to do one of the following:
- Enable human-to-human interaction
- Function better in daily life
- Control or resolve transient device states

If none of the above situations describe your notification, then it is non-transactional.

#### Non-transactional opt-out and opt-in

Non-transactional notifications should be optional, as they may not appeal to all users. You can make them optional in one of two ways:

- **Opt-out**: Users receive opt-out notifications by default, but they may stop receiving them by turning off a setting
- **Opt-in**: Users only receive opt-in notifications by turning on a setting in your app

### Channels in Android O

When you upgrade your app to Android O, you'll be required to define channels for your notifications – one for each type of notification you want to send.

Users control app notifications in Android O with channels. If a user doesn't want a certain notification from your app, they can block that channel rather than all notifications.

### Channel Importance Levels

For each channel you define, you'll assign it an importance level. Starting in Android O, importance levels control the behavior of each channel (taking the place of priority levels).

Importance levels have the following restrictions:
- The importance level you assign will be the channel's default. Users can change a channel's importance level in Android Settings
- Once you choose an importance level, you're limited in how you can change it: you may only lower the importance, and only if the user hasn't explicitly changed it

Channel importance should be chosen with consideration for the user's time and attention. When an unimportant notification is disguised as urgent, it can produce unnecessary alarm.

| Importance | Behavior | Usage | Examples |
|------------|----------|-------|----------|
| HIGH | Makes a sound and appears on screen | Time-critical information that the user must know, or act on, immediately | Text messages, alarms, phone calls |
| DEFAULT | Makes a sound | Information that should be seen at the user's earliest convenience, but not interrupt what they're doing | Traffic alerts, task reminders |
| LOW | No sound | Notification channels that don't meet the requirements of other importance levels | New content the user has subscribed to, social network invitations |
| MIN | No sound or visual interruption | Non-essential information that can wait or isn't specifically relevant to the user | Nearby places of interest, weather, promotional content |

### Create a Basic Notification

A notification in its most basic and compact form (also known as collapsed form) displays an icon, a title, and a small amount of content text.

#### Set the notification content

To get started, you need to set the notification's content and channel using a `NotificationCompat.Builder` object. The following example shows how to create a notification with the following:
- A small icon, set by `setSmallIcon()`. This is the only user-visible content that's required
- A title, set by `setContentTitle()`
- The body text, set by `setContentText()`
- The notification priority, set by `setPriority()`. The priority determines how intrusive the notification should be on Android 7.1 and lower

Example:

```kotlin
var builder = NotificationCompat.Builder(this, CHANNEL_ID)
        .setSmallIcon(R.drawable.notification_icon)
        .setContentTitle(textTitle)
        .setContentText(textContent)
        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
```

Notice that the `NotificationCompat.Builder` constructor requires that you provide a channel ID. This is required for compatibility with Android 8.0 (API level 26) and higher, but is ignored by older versions.

### Update a Notification

To update this notification after you've issued it, call `NotificationManagerCompat.notify()` again, passing it a notification with the same ID you used previously. If the previous notification has been dismissed, a new notification is created instead.

You can optionally call `setOnlyAlertOnce()` so your notification interrupts the user (with sound, vibration, or visual clues) only the first time the notification appears and not for later updates.

### Remove a Notification

Notifications remain visible until one of the following happens:
- The user dismisses the notification
- The user clicks the notification, and you called `setAutoCancel()` when you created the notification
- You call `cancel()` for a specific notification ID. This method also deletes ongoing notifications
- You call `cancelAll()`, which removes all of the notifications you previously issued
- If you set a timeout when creating a notification using `setTimeoutAfter()`, the system cancels the notification after the specified duration elapses. If required, you can cancel a notification before the specified timeout duration elapses

### When Not to Use a Notification

Notifications should not be the primary communication channel with your users, as frequent interruptions may cause irritation. The following cases do not warrant notification:
- Cross-promotion, or advertising another product within a notification, which is strictly prohibited by the Play Store
- An app that a user has never opened
- Messages that encourage the user to return to an app, but provide no direct value, such as "Haven't seen you in a while"
- Requests to rate an app
- Operations that don't require user involvement, like syncing information
- Error states from which the app may recover without user interaction

---

# Вопрос (RU)
> 

Что вы знаете о каналах уведомлений?

## Ответ (RU)
Уведомление - это сообщение, которое Android отображает вне пользовательского интерфейса вашего приложения, чтобы предоставить пользователю напоминания, сообщения от других людей или другую своевременную информацию из вашего приложения. Пользователи могут нажать на уведомление, чтобы открыть ваше приложение или выполнить действие непосредственно из уведомления.

### Использование уведомлений

Уведомления предназначены для информирования пользователей о событиях в вашем приложении. Наиболее эффективными являются следующие два типа уведомлений:
- Сообщения от других пользователей
- Своевременные и информативные напоминания о задачах

**Анатомия уведомления:**
- Область заголовка
- Область контента
- Область действий

**Как уведомления могут быть замечены:**
- Отображение значка в строке состояния
- Появление на экране блокировки
- Воспроизведение звука или вибрация
- Всплывающее отображение на текущем экране
- Мигание светодиода устройства

### Панель уведомлений

Панель уведомлений в Android обычно показывает уведомления в обратном хронологическом порядке с корректировками, зависящими от:
- Заявленного приоритета или важности уведомления приложения
- Недавно ли уведомление оповестило пользователя звуком или вибрацией
- Прикреплены ли к уведомлению люди и являются ли они избранными контактами
- Представляет ли уведомление важную текущую активность, такую как продолжающийся телефонный звонок или воспроизведение музыки

Начиная с Android O, система Android может изменять внешний вид некоторых уведомлений в верхней и нижней части списка, добавляя акцент или снижая акцент, чтобы помочь пользователю сканировать контент.

### Группировка

Ваше приложение может представлять несколько уведомлений в соответствии с иерархией:
- Родительское уведомление отображает сводку своих дочерних уведомлений
- Если родительское уведомление раскрывается пользователем, открываются все дочерние уведомления
- Дочернее уведомление может быть раскрыто для отображения всего его содержимого

Дочерние уведомления представляются без дублирования информации заголовка. Например, если дочернее уведомление имеет тот же значок приложения, что и его родитель, то заголовок дочернего уведомления не включает значок.

Дочерние уведомления должны быть понятны, если они появляются отдельно, так как система может показывать их вне группы при их поступлении.

### Типы уведомлений

Уведомления считаются либо транзакционными, либо нетранзакционными.

#### Транзакционные

Транзакционные уведомления предоставляют контент, который пользователь должен получить в определенное время, чтобы:
- Обеспечить взаимодействие между людьми
- Лучше функционировать в повседневной жизни
- Контролировать или разрешать временные состояния устройства

Если ни одна из вышеуказанных ситуаций не описывает ваше уведомление, то оно является нетранзакционным.

#### Нетранзакционные с отказом и согласием

Нетранзакционные уведомления должны быть опциональными, так как они могут не привлекать всех пользователей. Вы можете сделать их опциональными одним из двух способов:

- **Отказ**: Пользователи получают уведомления с отказом по умолчанию, но могут прекратить их получать, отключив настройку
- **Согласие**: Пользователи получают уведомления с согласием только после включения настройки в вашем приложении

### Каналы в Android O

При обновлении вашего приложения до Android O вам потребуется определить каналы для ваших уведомлений – по одному для каждого типа уведомлений, которые вы хотите отправлять.

Пользователи управляют уведомлениями приложений в Android O с помощью каналов. Если пользователь не хочет получать определенное уведомление от вашего приложения, он может заблокировать этот канал, а не все уведомления.

### Уровни важности каналов

Для каждого определяемого вами канала вы назначите уровень важности. Начиная с Android O, уровни важности управляют поведением каждого канала (заменяя уровни приоритета).

Уровни важности имеют следующие ограничения:
- Назначенный вами уровень важности будет уровнем по умолчанию для канала. Пользователи могут изменить уровень важности канала в настройках Android
- После выбора уровня важности вы ограничены в том, как можете его изменить: вы можете только понизить важность, и только если пользователь не изменил ее явно

Важность канала должна быть выбрана с учетом времени и внимания пользователя. Когда неважное уведомление маскируется под срочное, это может вызвать ненужную тревогу.

| Важность | Поведение | Использование | Примеры |
|----------|-----------|---------------|---------|
| HIGH | Издает звук и появляется на экране | Критичная по времени информация, о которой пользователь должен знать или на которую должен немедленно отреагировать | Текстовые сообщения, будильники, телефонные звонки |
| DEFAULT | Издает звук | Информация, которую следует увидеть при первой удобной возможности, но не прерывая текущую деятельность | Оповещения о трафике, напоминания о задачах |
| LOW | Без звука | Каналы уведомлений, которые не соответствуют требованиям других уровней важности | Новый контент, на который пользователь подписан, приглашения в социальные сети |
| MIN | Без звука или визуального прерывания | Несущественная информация, которая может подождать или не имеет конкретного отношения к пользователю | Близлежащие места интереса, погода, рекламный контент |

### Создание базового уведомления

Уведомление в своей самой простой и компактной форме (также известной как свернутая форма) отображает значок, заголовок и небольшое количество текста контента.

#### Установка контента уведомления

Для начала вам нужно установить контент и канал уведомления, используя объект `NotificationCompat.Builder`. Следующий пример показывает, как создать уведомление со следующим:
- Маленький значок, установленный с помощью `setSmallIcon()`. Это единственный видимый пользователю контент, который является обязательным
- Заголовок, установленный с помощью `setContentTitle()`
- Текст тела, установленный с помощью `setContentText()`
- Приоритет уведомления, установленный с помощью `setPriority()`. Приоритет определяет, насколько навязчивым должно быть уведомление на Android 7.1 и ниже

Пример:

```kotlin
var builder = NotificationCompat.Builder(this, CHANNEL_ID)
        .setSmallIcon(R.drawable.notification_icon)
        .setContentTitle(textTitle)
        .setContentText(textContent)
        .setPriority(NotificationCompat.PRIORITY_DEFAULT)
```

Обратите внимание, что конструктор `NotificationCompat.Builder` требует предоставления ID канала. Это требуется для совместимости с Android 8.0 (уровень API 26) и выше, но игнорируется более старыми версиями.

### Обновление уведомления

Чтобы обновить это уведомление после его отправки, снова вызовите `NotificationManagerCompat.notify()`, передав ему уведомление с тем же ID, который вы использовали ранее. Если предыдущее уведомление было отклонено, вместо этого создается новое уведомление.

Вы можете опционально вызвать `setOnlyAlertOnce()`, чтобы ваше уведомление прерывало пользователя (звуком, вибрацией или визуальными подсказками) только при первом появлении уведомления, а не при последующих обновлениях.

### Удаление уведомления

Уведомления остаются видимыми до тех пор, пока не произойдет одно из следующих событий:
- Пользователь отклоняет уведомление
- Пользователь нажимает на уведомление, и вы вызвали `setAutoCancel()` при создании уведомления
- Вы вызываете `cancel()` для конкретного ID уведомления. Этот метод также удаляет текущие уведомления
- Вы вызываете `cancelAll()`, который удаляет все ранее выпущенные вами уведомления
- Если вы установили тайм-аут при создании уведомления с помощью `setTimeoutAfter()`, система отменяет уведомление после истечения указанной длительности. При необходимости вы можете отменить уведомление до истечения указанной длительности тайм-аута

### Когда не использовать уведомление

Уведомления не должны быть основным каналом связи с вашими пользователями, так как частые прерывания могут вызывать раздражение. Следующие случаи не требуют уведомления:
- Кросс-промоушн или реклама другого продукта в уведомлении, что строго запрещено Play Store
- Приложение, которое пользователь никогда не открывал
- Сообщения, которые поощряют пользователя вернуться в приложение, но не предоставляют прямой ценности, такие как "Давно вас не видели"
- Запросы на оценку приложения
- Операции, которые не требуют участия пользователя, такие как синхронизация информации
- Состояния ошибок, от которых приложение может восстановиться без взаимодействия с пользователем
