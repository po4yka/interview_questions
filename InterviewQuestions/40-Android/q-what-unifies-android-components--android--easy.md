---
id: 20251012-122711178
title: "What Unifies Android Components / Что объединяет компоненты Android"
topic: android
difficulty: easy
status: draft
moc: moc-android
related: [q-how-navigation-is-implemented-in-android--android--medium, q-architecture-components-libraries--android--easy, q-recyclerview-async-list-differ--recyclerview--medium]
created: 2025-10-15
tags: [android-components, android/android-components, android/context, android/manifest, components, context, intent, manifest, difficulty/easy]
---
# What unifies Android components?

**Russian**: Что объединяет основные компоненты Android-приложения?

**English**: What unifies the main Android application components?

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

## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-android-components-besides-activity--android--easy]] - Fundamentals
- [[q-main-android-components--android--easy]] - Fundamentals
- [[q-material3-components--material-design--easy]] - Fundamentals
- [[q-android-app-components--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
- [[q-hilt-components-scope--android--medium]] - Fundamentals
