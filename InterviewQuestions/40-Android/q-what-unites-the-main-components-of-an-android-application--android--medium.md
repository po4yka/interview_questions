---
topic: android
tags:
  - android
  - components
  - activity
  - service
  - broadcastreceiver
  - contentprovider
difficulty: medium
status: reviewed
---

# What unites the main components of an Android application?

## Answer

The main Android components (Activity, Service, BroadcastReceiver, ContentProvider) share several fundamental characteristics that unite them in the Android framework.

### Four Main Components

```
Android Application Components
├── Activity        → UI screens
├── Service         → Background operations
├── BroadcastReceiver → System/app events
└── ContentProvider   → Data sharing
```

### Common Characteristics

#### 1. AndroidManifest.xml Declaration

All components must be declared in the manifest:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

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
            android:name=".MyService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".MyReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".MyContentProvider"
            android:authorities="com.example.app.provider"
            android:exported="false" />
    </application>
</manifest>
```

#### 2. System Management

All components are **created and managed by the Android system**, not by the developer:

```kotlin
// - You don't do this:
val activity = MainActivity()
activity.onCreate()

// - System does this:
// startActivity(Intent(this, MainActivity::class.java))
// System creates and calls lifecycle methods
```

**System responsibilities**:
- Component instantiation
- Lifecycle management
- Process allocation
- Memory management
- Component destruction

#### 3. Intent Communication

Components interact through **Intents**:

```kotlin
// Start Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// Start Service
val serviceIntent = Intent(this, DownloadService::class.java)
startService(serviceIntent)

// Send Broadcast
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Query ContentProvider (uses ContentResolver, not direct Intent)
val uri = Uri.parse("content://com.example.app.provider/users")
contentResolver.query(uri, null, null, null, null)
```

#### 4. Context Access

All components have access to **Context**:

```kotlin
class MainActivity : AppCompatActivity() {
    // Activity IS a Context
    fun example() {
        val context: Context = this
        val appContext = applicationContext
    }
}

class MyService : Service() {
    // Service IS a Context
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val context: Context = this
        return START_STICKY
    }
}

class MyReceiver : BroadcastReceiver() {
    // Receiver RECEIVES a Context
    override fun onReceive(context: Context, intent: Intent) {
        // Use context parameter
    }
}

class MyProvider : ContentProvider() {
    // Provider HAS context property
    override fun onCreate(): Boolean {
        val ctx = context
        return true
    }
}
```

#### 5. Defined Lifecycles

Each component has a **specific lifecycle** managed by the system:

```kotlin
// Activity Lifecycle
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { }
    override fun onStart() { }
    override fun onResume() { }
    override fun onPause() { }
    override fun onStop() { }
    override fun onDestroy() { }
}

// Service Lifecycle
class MyService : Service() {
    override fun onCreate() { }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int { }
    override fun onBind(intent: Intent?): IBinder? { }
    override fun onDestroy() { }
}

// BroadcastReceiver Lifecycle
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Short-lived: must complete within 10 seconds
    }
}

// ContentProvider Lifecycle
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean { }
    // No explicit destroy - lives with application process
}
```

#### 6. Run in Application Process

All components run in the **same process** by default:

```xml
<!-- Default: all components in same process -->
<application android:process=":main">
    <activity android:name=".MainActivity" />
    <service android:name=".MyService" />
</application>

<!-- Can specify separate process -->
<service
    android:name=".HeavyService"
    android:process=":background" />
```

#### 7. Permission Requirements

Components can require **permissions**:

```xml
<!-- Activity requiring permission -->
<activity
    android:name=".AdminActivity"
    android:permission="android.permission.ADMIN_PRIVILEGES" />

<!-- Service requiring permission to bind -->
<service
    android:name=".SecureService"
    android:permission="com.example.app.BIND_SERVICE" />

<!-- BroadcastReceiver requiring permission to send -->
<receiver
    android:name=".SecureReceiver"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- ContentProvider requiring permissions -->
<provider
    android:name=".SecureProvider"
    android:readPermission="com.example.app.READ_DATA"
    android:writePermission="com.example.app.WRITE_DATA" />
```

### Component Comparison Table

| Characteristic | Activity | Service | BroadcastReceiver | ContentProvider |
|----------------|----------|---------|-------------------|-----------------|
| Purpose | UI screen | Background work | Event handling | Data sharing |
| Has UI | Yes | No | No | No |
| Lifecycle | Complex (7 states) | Medium (4 states) | Simple (1 method) | Minimal |
| Created by | System | System | System | System |
| Manifest required | Yes | Yes | Yes (for static) | Yes |
| Intent interaction | Yes | Yes | Yes | No (uses ContentResolver) |
| Context access | IS Context | IS Context | RECEIVES Context | HAS context |
| Process | App process | App/separate | App process | App process |
| Max runtime | User-controlled | Indefinite | 10 seconds | Process lifetime |

### Unified Architecture Pattern

```kotlin
// All components follow similar patterns:

// 1. Manifest declaration
// 2. Extend base class
// 3. Override lifecycle methods
// 4. Access Context
// 5. Interact via Intent/ContentResolver

// Example Service
class DownloadService : Service() {  // 2. Extend base
    override fun onCreate() {         // 3. Lifecycle
        super.onCreate()
        val ctx: Context = this       // 4. Context access
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Intent received                  5. Intent interaction
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// 1. Manifest:
// <service android:name=".DownloadService" />
```

### Communication Between Components

```kotlin
// Activity → Service
val intent = Intent(this, MyService::class.java)
startService(intent)

// Activity → BroadcastReceiver
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)

// Service → Activity (via notification)
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0)

// Any component → ContentProvider
val uri = Uri.parse("content://authority/path")
contentResolver.query(uri, null, null, null, null)

// BroadcastReceiver → Service
override fun onReceive(context: Context, intent: Intent) {
    val serviceIntent = Intent(context, MyService::class.java)
    context.startService(serviceIntent)
}
```

### Summary

Main Android components are united by:
1. **Manifest declaration** - all must be declared
2. **System management** - lifecycle controlled by OS
3. **Intent/ContentResolver communication** - standard interaction pattern
4. **Context access** - all have access to Android context
5. **Defined lifecycles** - predictable state transitions
6. **Process execution** - run in application process
7. **Permission system** - consistent security model

## Answer (RU)
Все компоненты Android управляются системой через Context. Они взаимодействуют через Intent, который передает команды и данные. Каждый компонент регистрируется в AndroidManifest.xml.

## Related Topics
- AndroidManifest.xml
- Intent system
- Context and Application
- Component lifecycles
- Process management
