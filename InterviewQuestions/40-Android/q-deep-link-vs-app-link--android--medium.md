---
topic: android
tags:
  - android
  - android/navigation
  - app-linking
  - app-links
  - deep-linking
  - https
  - navigation
  - uri
  - verification
difficulty: medium
status: draft
---

# Какие особенности отличия deep link от app link?

**English**: What are the differences between deep links and app links?

## Answer (EN)
**Deep Link** works through a **custom URI scheme** (e.g., `myapp://`) and requires `intent-filter` configuration.

**App Link** uses **HTTP/HTTPS URLs** and requires **domain ownership verification** through the `assetlinks.json` file.

## Key Differences

| Feature | Deep Link | App Link |
|---------|-----------|----------|
| **Scheme** | Custom (`myapp://`) | HTTPS only (`https://`) |
| **Verification** | None | Domain verification required ✅ |
| **User Experience** | Shows app chooser dialog | Opens app directly |
| **Android Version** | All versions | Android 6.0+ (API 23+) |
| **Security** | Low (anyone can claim scheme) | High (verified ownership) |
| **Setup Complexity** | Simple | Complex (requires server file) |
| **Use Case** | Internal navigation | Verified web content |

---

## Deep Links

### Characteristics

- ✅ Custom URI scheme (e.g., `myapp://`, `mydomain://`)
- ✅ Works on all Android versions
- ✅ Simple setup (no server configuration)
- ❌ Not verified - any app can claim the same scheme
- ❌ Shows disambiguation dialog if multiple apps handle the URI

### Implementation

**AndroidManifest.xml:**

```xml
<activity android:name=".DetailActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <!-- Custom scheme -->
        <data
            android:scheme="myapp"
            android:host="product"
            android:pathPrefix="/detail" />
    </intent-filter>
</activity>
```

**Example URLs:**

```
myapp://product/detail/123
myapp://user/profile/456
shopping://checkout/cart
```

**Handle in Activity:**

```kotlin
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Get the URI
        val uri: Uri? = intent.data

        uri?.let {
            // Extract data from URI
            val scheme = it.scheme        // "myapp"
            val host = it.host            // "product"
            val path = it.path            // "/detail/123"
            val productId = it.lastPathSegment  // "123"

            // Use the data
            loadProduct(productId)
        }
    }
}
```

**Testing:**

```bash

# From terminal/ADB
adb shell am start -W -a android.intent.action.VIEW \
    -d "myapp://product/detail/123" \
    com.example.myapp
```

**Problems with Deep Links:**

```kotlin
// Problem 1: Disambiguation dialog
// If multiple apps claim "myapp://" scheme, user sees chooser

// Problem 2: No verification
// Malicious app can register same scheme and intercept links

// Problem 3: Not clickable in web browsers
// Custom schemes don't work in web content
```

---

## App Links

### Characteristics

- ✅ Uses HTTPS URLs (standard web links)
- ✅ Verified domain ownership
- ✅ Opens app directly (no disambiguation dialog)
- ✅ Clickable in web browsers and emails
- ✅ Secure - only verified app can handle the domain
- ❌ Android 6.0+ only (API 23+)
- ❌ Requires server configuration (assetlinks.json)

### Implementation

**1. Configure AndroidManifest.xml:**

```xml
<activity android:name=".DetailActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <!-- HTTPS URLs only -->
        <data
            android:scheme="https"
            android:host="www.example.com"
            android:pathPrefix="/product" />
    </intent-filter>
</activity>
```

**Key difference:** `android:autoVerify="true"` enables automatic verification.

**2. Create Digital Asset Links file:**

**Location:** `https://www.example.com/.well-known/assetlinks.json`

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "com.example.myapp",
    "sha256_cert_fingerprints": [
      "14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5"
    ]
  }
}]
```

**Get SHA256 fingerprint:**

```bash

# Debug keystore
keytool -list -v -keystore ~/.android/debug.keystore \
    -alias androiddebugkey -storepass android -keypass android

# Release keystore
keytool -list -v -keystore my-release-key.jks \
    -alias my-key-alias
```

**3. Handle in Activity:**

```kotlin
class DetailActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Handle app link
        val appLinkUri: Uri? = intent.data

        appLinkUri?.let { uri ->
            // Extract data from HTTPS URL
            // https://www.example.com/product/123
            val productId = uri.lastPathSegment  // "123"

            loadProduct(productId)
        }
    }
}
```

**Example URLs:**

```
https://www.example.com/product/123
https://www.example.com/user/profile/456
https://shop.example.com/checkout/cart
```

**Testing:**

```bash

# Test with ADB
adb shell am start -W -a android.intent.action.VIEW \
    -d "https://www.example.com/product/123" \
    com.example.myapp

# Verify domain associations
adb shell pm get-app-links com.example.myapp

# Reset verification state
adb shell pm set-app-links --package com.example.myapp 0 all

# Verify domain
adb shell pm verify-app-links --re-verify com.example.myapp
```

**Benefits of App Links:**

```kotlin
// Benefit 1: Direct opening (no chooser dialog)
// User clicks https://example.com/product/123
// → App opens directly (if installed)
// → Otherwise, opens in browser

// Benefit 2: Verified security
// Only YOUR app can handle YOUR domain

// Benefit 3: Works everywhere
// Clickable in web browsers, emails, SMS, social media
```

---

## Comparison Examples

### Deep Link Flow

```
User clicks: myapp://product/123

Android:
  1. Find apps with intent-filter for "myapp://"
  2. If multiple apps found → Show chooser dialog
  3. User selects app
  4. App opens

Issues:
  ❌ Disambiguation dialog (poor UX)
  ❌ Any app can claim "myapp://" scheme
  ❌ Not clickable in web browsers
```

### App Link Flow

```
User clicks: https://www.example.com/product/123

Android:
  1. Check if domain is verified for any app
  2. If verified app found → Open app directly ✅
  3. If app not installed → Open in browser
  4. No disambiguation dialog

Benefits:
  ✅ Direct app opening (better UX)
  ✅ Verified ownership (secure)
  ✅ Works in browsers, emails, etc.
```

---

## Complete Example

### Deep Link + App Link Combined

```xml
<activity android:name=".MainActivity">
    <!-- App Link (verified HTTPS) -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <data
            android:scheme="https"
            android:host="www.example.com" />
    </intent-filter>

    <!-- Deep Link (custom scheme, fallback) -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <data
            android:scheme="myapp"
            android:host="open" />
    </intent-filter>
</activity>
```

**Handle both:**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri: Uri? = intent.data

        uri?.let {
            when (it.scheme) {
                "https" -> {
                    // App Link
                    Log.d("Link", "App Link: ${it.toString()}")
                    handleAppLink(it)
                }
                "myapp" -> {
                    // Deep Link
                    Log.d("Link", "Deep Link: ${it.toString()}")
                    handleDeepLink(it)
                }
            }
        }
    }

    private fun handleAppLink(uri: Uri) {
        // Parse HTTPS URL
        // https://www.example.com/product/123
        val path = uri.pathSegments  // ["product", "123"]
        when (path[0]) {
            "product" -> openProduct(path[1])
            "user" -> openUserProfile(path[1])
        }
    }

    private fun handleDeepLink(uri: Uri) {
        // Parse custom scheme
        // myapp://open?screen=settings
        val screen = uri.getQueryParameter("screen")
        when (screen) {
            "settings" -> openSettings()
            "profile" -> openProfile()
        }
    }
}
```

---

## Navigation Component Integration

### Deep Link in nav_graph.xml:

```xml
<fragment
    android:id="@+id/productDetailFragment"
    android:name="com.example.ProductDetailFragment">

    <argument
        android:name="productId"
        app:argType="string" />

    <!-- Deep Link -->
    <deepLink app:uri="myapp://product/{productId}" />

    <!-- App Link -->
    <deepLink app:uri="https://www.example.com/product/{productId}" />
</fragment>
```

**Automatic handling:** Navigation Component handles the link automatically and extracts arguments.

---

## Verification Status Check

```kotlin
// Check App Link verification status
fun checkAppLinkStatus(packageName: String) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val manager = getSystemService(DomainVerificationManager::class.java)
        val userState = manager.getDomainVerificationUserState(packageName)

        val verifiedDomains = userState?.hostToStateMap
            ?.filterValues { it == DomainVerificationUserState.DOMAIN_STATE_VERIFIED }
            ?.keys

        Log.d("AppLink", "Verified domains: $verifiedDomains")
    }
}
```

---

## Summary

**Deep Links:**
- Custom URI scheme (`myapp://`)
- Simple setup (no server file)
- Shows app chooser if multiple apps
- Works on all Android versions
- Not verified/secure

**App Links:**
- HTTPS URLs (`https://`)
- Requires domain verification (`assetlinks.json`)
- Opens app directly (no chooser)
- Android 6.0+ only
- Verified and secure

**When to use:**
- **Deep Links**: Internal navigation, custom schemes, backward compatibility
- **App Links**: Public shareable URLs, verified web content, better UX

**Best practice:** Use **App Links** for production apps with web presence, fall back to Deep Links for older Android versions.

## Ответ (RU)
Deep link работает через схему URI например myapp требует настройки intent-filter. App link использует HTTP HTTPS ссылки и требует подтверждения владения доменом через файл assetlinks.json.

