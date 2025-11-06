---
id: android-209
title: Unified Android Components / Объединение компонентов Android
aliases:
- Unified Components
- Объединение компонентов
topic: android
subtopics:
- activity
- fragment
- service
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- c-context
- c-intent
- c-lifecycle
created: 2025-10-15
updated: 2025-10-31
tags:
- android/activity
- android/fragment
- android/service
- components
- context
- difficulty/easy
- intent
date created: Saturday, November 1st 2025, 1:26:06 pm
date modified: Saturday, November 1st 2025, 5:43:30 pm
---

# Вопрос (RU)
> Объединение компонентов Android

# Question (EN)
> Unified Android Components

---

## Answer (EN)
Main Android components are unified by **three key aspects**:

**1. Context** - Resource Access

All components **inherit or receive Context** for accessing resources and system services.

```kotlin
// Activity extends Context
class MainActivity : AppCompatActivity() {
    fun accessResources() {
        // Context methods available directly
        val string = getString(R.string.app_name)
        val color = getColor(R.color.primary)
        val packageManager = packageManager
    }
}

// Service extends Context
class MusicService : Service() {
    fun accessSystemServices() {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
    }
}

// BroadcastReceiver receives Context
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Use context parameter
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }
}

// Fragment has context
class ProfileFragment : Fragment() {
    fun useContext() {
        requireContext().getString(R.string.title)
    }
}
```

**2. AndroidManifest.xml** - Declaration

All main components **must be declared** in the manifest file.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application>
        <!-- Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service -->
        <service
            android:name=".MusicService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".NetworkReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".NotesProvider"
            android:authorities="com.example.notes"
            android:exported="true" />
    </application>

</manifest>
```

**3. Intent** - Communication

All components **interact through Intent**.

```kotlin
// Start Activity
val intent = Intent(this, ProfileActivity::class.java)
startActivity(intent)

// Start Service
startService(Intent(this, MusicService::class.java))

// Send Broadcast
sendBroadcast(Intent("com.example.CUSTOM_ACTION"))

// Access ContentProvider (implicit Intent usage)
contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)
```

**Unified Component Diagram:**

```

        AndroidManifest.xml
  (All components declared here)





    Activity   Service  Receiver


            All inherit/receive Context




           Context & Intent
          (Unified access &
           communication)

```

**Main Components Included:**

- - **Activity** - UI screens
- - **Fragment** - UI portions (not in manifest, but has Context)
- - **Service** - Background operations
- - **BroadcastReceiver** - Event listeners
- - **ContentProvider** - Data sharing

**Summary:**

**Three Pillars of Unity:**

1. **Context**: All access resources/services through Context
2. **Manifest**: All declared in AndroidManifest.xml
3. **Intent**: All communicate via Intent messaging


# Question (EN)
> Unified Android Components

---


---


## Answer (EN)
Main Android components are unified by **three key aspects**:

**1. Context** - Resource Access

All components **inherit or receive Context** for accessing resources and system services.

```kotlin
// Activity extends Context
class MainActivity : AppCompatActivity() {
    fun accessResources() {
        // Context methods available directly
        val string = getString(R.string.app_name)
        val color = getColor(R.color.primary)
        val packageManager = packageManager
    }
}

// Service extends Context
class MusicService : Service() {
    fun accessSystemServices() {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val audioManager = getSystemService(Context.AUDIO_SERVICE) as AudioManager
    }
}

// BroadcastReceiver receives Context
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Use context parameter
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }
}

// Fragment has context
class ProfileFragment : Fragment() {
    fun useContext() {
        requireContext().getString(R.string.title)
    }
}
```

**2. AndroidManifest.xml** - Declaration

All main components **must be declared** in the manifest file.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application>
        <!-- Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service -->
        <service
            android:name=".MusicService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".NetworkReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".NotesProvider"
            android:authorities="com.example.notes"
            android:exported="true" />
    </application>

</manifest>
```

**3. Intent** - Communication

All components **interact through Intent**.

```kotlin
// Start Activity
val intent = Intent(this, ProfileActivity::class.java)
startActivity(intent)

// Start Service
startService(Intent(this, MusicService::class.java))

// Send Broadcast
sendBroadcast(Intent("com.example.CUSTOM_ACTION"))

// Access ContentProvider (implicit Intent usage)
contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)
```

**Unified Component Diagram:**

```

        AndroidManifest.xml
  (All components declared here)





    Activity   Service  Receiver


            All inherit/receive Context




           Context & Intent
          (Unified access &
           communication)

```

**Main Components Included:**

- - **Activity** - UI screens
- - **Fragment** - UI portions (not in manifest, but has Context)
- - **Service** - Background operations
- - **BroadcastReceiver** - Event listeners
- - **ContentProvider** - Data sharing

**Summary:**

**Three Pillars of Unity:**

1. **Context**: All access resources/services through Context
2. **Manifest**: All declared in AndroidManifest.xml
3. **Intent**: All communicate via Intent messaging

## Ответ (RU)
Основные компоненты Android-приложения объединяет то, что они все наследуют или получают **Context** для доступа к ресурсам и системным сервисам, объявляются в **AndroidManifest.xml** и взаимодействуют друг с другом через **Intent**.

Основные компоненты включают: Activity, Fragment, Service, BroadcastReceiver и ContentProvider.


---


## Follow-ups

- [[c-android-components]]
- [[c-context]]
- [[c-intent]]


## References

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)


## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-android-components-besides-activity--android--easy]] - Fundamentals
- [[q-main-android-components--android--easy]] - Fundamentals
- [[q-material3-components--ui-ux-accessibility--easy]] - Fundamentals
- [[q-android-app-components--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
- [[q-hilt-components-scope--android--medium]] - Fundamentals
