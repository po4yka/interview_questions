---
id: android-019
title: "How to implement Voice/Video Call in Android? / Как реализовать голосовой/видеозвонок в Android?"
aliases: [Voice Video Call Android, WebRTC Android, Голосовой видеозвонок Android]

# Classification
topic: android
subtopics: [media, networking-http, websockets]
question_kind: coding
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://github.com/amitshekhariitbhu/android-interview-questions]

# Workflow & relations
status: draft
moc: moc-android
related: [c-webrtc, c-websockets, q-http-protocols-comparison--android--medium, q-parallel-network-calls-coroutines--kotlin--medium]

# Timestamps
created: 2025-10-06
updated: 2025-10-31

tags: [android/media, android/networking-http, android/websockets, difficulty/hard]
date created: Tuesday, October 28th 2025, 9:11:50 pm
date modified: Thursday, October 30th 2025, 3:10:25 pm
---

# Вопрос (RU)
> Как бы вы реализовали функции голосовых и видеозвонков в Android приложении?

# Question (EN)
> How would you implement voice and video calling features in an Android application?

---

## Ответ (RU)

**Подход**: Использование WebRTC для peer-to-peer аудио/видео связи с низкой задержкой

**Ключевые компоненты**:
- **PeerConnection** - управление P2P соединением
- **MediaStream** - обработка аудио/видео потоков
- **ICE/STUN/TURN** - проход через NAT/файрволы
- **Signaling Server** - обмен метаданными (WebSocket)

**Архитектура**:
```
Устройство А                    Устройство Б
    ↓                                ↓
Signaling Server ← WebSocket → Offer/Answer/ICE
    ↓                                ↓
Media P2P (WebRTC) ←──────────→ Audio/Video Stream
    ↓
STUN/TURN Server (NAT traversal)
```

### Основная реализация

**Менеджер WebRTC**:
```kotlin
class WebRTCManager(
    context: Context,
    private val signalingClient: SignalingClient
) {
    private var peerConnection: PeerConnection? = null
    private var localVideoTrack: VideoTrack? = null
    private var localAudioTrack: AudioTrack? = null

    private val _callState = MutableStateFlow(CallState())
    val callState = _callState.asStateFlow()

    fun startCall(isVideoCall: Boolean, remotePeerId: String) {
        createPeerConnection()
        createMediaStreams(isVideoCall)

        // ✅ Создание offer
        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(this, sdp)
                signalingClient.sendOffer(remotePeerId, sdp.description)
            }
            // ... обработка ошибок
        }, MediaConstraints())
    }

    private fun createPeerConnection() {
        val iceServers = listOf(
            // ✅ STUN для определения публичного IP
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302")
                .createIceServer(),
            // ✅ TURN для прохода через строгие NAT
            PeerConnection.IceServer.builder("turn:your-turn-server.com:3478")
                .setUsername("username")
                .setPassword("password")
                .createIceServer()
        )

        val rtcConfig = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
        }

        peerConnection = factory.createPeerConnection(rtcConfig, observer)
    }

    private fun createMediaStreams(isVideoCall: Boolean) {
        // ✅ Аудио трек (всегда)
        val audioSource = factory.createAudioSource(MediaConstraints())
        localAudioTrack = factory.createAudioTrack("audio", audioSource)

        // ✅ Видео трек (опционально)
        if (isVideoCall) {
            val videoCapturer = createVideoCapturer()
            val videoSource = factory.createVideoSource(false)
            videoCapturer?.initialize(helper, context, videoSource.capturerObserver)
            videoCapturer?.startCapture(1280, 720, 30)

            localVideoTrack = factory.createVideoTrack("video", videoSource)
        }

        peerConnection?.addTrack(localAudioTrack)
        peerConnection?.addTrack(localVideoTrack)
    }

    fun toggleMute() {
        val muted = !_callState.value.isMuted
        localAudioTrack?.setEnabled(!muted)
        _callState.value = _callState.value.copy(isMuted = muted)
    }

    fun toggleVideo() {
        val enabled = !_callState.value.isVideoEnabled
        localVideoTrack?.setEnabled(enabled)
        _callState.value = _callState.value.copy(isVideoEnabled = enabled)
    }
}
```

**Signaling через WebSocket**:
```kotlin
class SignalingClient(private val okHttpClient: OkHttpClient) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<SignalingMessage>()
    val messages = _messages.asSharedFlow()

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://your-server.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<SignalingMessage>(text)
                scope.launch { _messages.emit(message) }
            }
        })
    }

    fun sendOffer(remotePeerId: String, sdp: String) {
        send(SignalingMessage.Offer(sdp))
    }
}

// ✅ Модели signaling сообщений
@Serializable
sealed class SignalingMessage {
    @Serializable
    data class Offer(val sdp: String) : SignalingMessage()

    @Serializable
    data class Answer(val sdp: String) : SignalingMessage()

    @Serializable
    data class IceCandidate(
        val sdpMid: String,
        val sdpMLineIndex: Int,
        val sdp: String
    ) : SignalingMessage()
}
```

**UI (Jetpack Compose)**:
```kotlin
@Composable
fun VideoCallScreen(viewModel: CallViewModel) {
    val callState by viewModel.callState.collectAsState()
    val localVideo by viewModel.localVideoTrack.collectAsState()
    val remoteVideo by viewModel.remoteVideoTrack.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // ✅ Удаленное видео (полный экран)
        remoteVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        track.addSink(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // ✅ Локальное видео (PiP)
        localVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        setZOrderMediaOverlay(true)
                        track.addSink(this)
                    }
                },
                modifier = Modifier
                    .size(120.dp, 160.dp)
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            )
        }

        // ✅ Элементы управления
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
        ) {
            CallButton(
                icon = if (callState.isMuted) Icons.Default.MicOff else Icons.Default.Mic,
                isActive = callState.isMuted,
                onClick = { viewModel.toggleMute() }
            )

            CallButton(
                icon = Icons.Default.CallEnd,
                isActive = true,
                onClick = { viewModel.endCall() }
            )

            CallButton(
                icon = if (callState.isVideoEnabled) Icons.Default.Videocam
                       else Icons.Default.VideocamOff,
                isActive = !callState.isVideoEnabled,
                onClick = { viewModel.toggleVideo() }
            )
        }
    }
}
```

### Лучшие практики

**1. Серверная инфраструктура**:
- STUN серверы для определения публичного IP
- TURN серверы для прохода через строгие NAT (критично!)
- Signaling сервер для обмена метаданными

**2. Управление ресурсами**:
- Остановка видео при переходе в фон
- Правильный dispose всех треков и connection
- Управление audio focus через AudioManager

**3. Производительность**:
- Адаптивный битрейт в зависимости от сети
- Использование FLAG_KEEP_SCREEN_ON
- Мониторинг качества соединения (ICE state)

**4. Обработка ошибок**:
```kotlin
// ✅ Обработка состояний ICE
override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
    when (state) {
        CONNECTED -> _callState.value = _callState.value.copy(isConnected = true)
        FAILED, DISCONNECTED -> {
            _callState.value = _callState.value.copy(isConnected = false)
            endCall()
        }
    }
}
```

### Типичные ошибки

**❌ Не настроен TURN сервер**:
- Звонки не работают за NAT/файрволом
- Решение: всегда настраивать TURN в дополнение к STUN

**❌ Не запрошены runtime разрешения**:
```kotlin
// ✅ Правильно
val permissions = arrayOf(
    Manifest.permission.CAMERA,
    Manifest.permission.RECORD_AUDIO
)
requestPermissions(permissions, REQUEST_CODE)
```

**❌ Утечка ресурсов**:
```kotlin
// ✅ Правильно - dispose всего
fun endCall() {
    localAudioTrack?.dispose()
    localVideoTrack?.dispose()
    videoCapturer?.stopCapture()
    videoCapturer?.dispose()
    peerConnection?.close()
}
```

---

## Answer (EN)

**Approach**: Use WebRTC for peer-to-peer audio/video communication with low latency

**Core Components**:
- **PeerConnection** - manages P2P connection
- **MediaStream** - handles audio/video streams
- **ICE/STUN/TURN** - NAT traversal
- **Signaling Server** - exchanges metadata (WebSocket)

**Architecture**:
```
Device A                        Device B
    ↓                               ↓
Signaling Server ← WebSocket → Offer/Answer/ICE
    ↓                               ↓
Media P2P (WebRTC) ←──────────→ Audio/Video Stream
    ↓
STUN/TURN Server (NAT traversal)
```

### Core Implementation

**WebRTC Manager**:
```kotlin
class WebRTCManager(
    context: Context,
    private val signalingClient: SignalingClient
) {
    private var peerConnection: PeerConnection? = null
    private var localVideoTrack: VideoTrack? = null
    private var localAudioTrack: AudioTrack? = null

    private val _callState = MutableStateFlow(CallState())
    val callState = _callState.asStateFlow()

    fun startCall(isVideoCall: Boolean, remotePeerId: String) {
        createPeerConnection()
        createMediaStreams(isVideoCall)

        // ✅ Create offer
        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(this, sdp)
                signalingClient.sendOffer(remotePeerId, sdp.description)
            }
            // ... error handling
        }, MediaConstraints())
    }

    private fun createPeerConnection() {
        val iceServers = listOf(
            // ✅ STUN for public IP discovery
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302")
                .createIceServer(),
            // ✅ TURN for strict NAT traversal
            PeerConnection.IceServer.builder("turn:your-turn-server.com:3478")
                .setUsername("username")
                .setPassword("password")
                .createIceServer()
        )

        val rtcConfig = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
        }

        peerConnection = factory.createPeerConnection(rtcConfig, observer)
    }

    private fun createMediaStreams(isVideoCall: Boolean) {
        // ✅ Audio track (always)
        val audioSource = factory.createAudioSource(MediaConstraints())
        localAudioTrack = factory.createAudioTrack("audio", audioSource)

        // ✅ Video track (optional)
        if (isVideoCall) {
            val videoCapturer = createVideoCapturer()
            val videoSource = factory.createVideoSource(false)
            videoCapturer?.initialize(helper, context, videoSource.capturerObserver)
            videoCapturer?.startCapture(1280, 720, 30)

            localVideoTrack = factory.createVideoTrack("video", videoSource)
        }

        peerConnection?.addTrack(localAudioTrack)
        peerConnection?.addTrack(localVideoTrack)
    }

    fun toggleMute() {
        val muted = !_callState.value.isMuted
        localAudioTrack?.setEnabled(!muted)
        _callState.value = _callState.value.copy(isMuted = muted)
    }

    fun toggleVideo() {
        val enabled = !_callState.value.isVideoEnabled
        localVideoTrack?.setEnabled(enabled)
        _callState.value = _callState.value.copy(isVideoEnabled = enabled)
    }
}
```

**Signaling via WebSocket**:
```kotlin
class SignalingClient(private val okHttpClient: OkHttpClient) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<SignalingMessage>()
    val messages = _messages.asSharedFlow()

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://your-server.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<SignalingMessage>(text)
                scope.launch { _messages.emit(message) }
            }
        })
    }

    fun sendOffer(remotePeerId: String, sdp: String) {
        send(SignalingMessage.Offer(sdp))
    }
}

// ✅ Signaling message models
@Serializable
sealed class SignalingMessage {
    @Serializable
    data class Offer(val sdp: String) : SignalingMessage()

    @Serializable
    data class Answer(val sdp: String) : SignalingMessage()

    @Serializable
    data class IceCandidate(
        val sdpMid: String,
        val sdpMLineIndex: Int,
        val sdp: String
    ) : SignalingMessage()
}
```

**UI (Jetpack Compose)**:
```kotlin
@Composable
fun VideoCallScreen(viewModel: CallViewModel) {
    val callState by viewModel.callState.collectAsState()
    val localVideo by viewModel.localVideoTrack.collectAsState()
    val remoteVideo by viewModel.remoteVideoTrack.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // ✅ Remote video (full screen)
        remoteVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        track.addSink(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // ✅ Local video (PiP)
        localVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        setZOrderMediaOverlay(true)
                        track.addSink(this)
                    }
                },
                modifier = Modifier
                    .size(120.dp, 160.dp)
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            )
        }

        // ✅ Call controls
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
        ) {
            CallButton(
                icon = if (callState.isMuted) Icons.Default.MicOff else Icons.Default.Mic,
                isActive = callState.isMuted,
                onClick = { viewModel.toggleMute() }
            )

            CallButton(
                icon = Icons.Default.CallEnd,
                isActive = true,
                onClick = { viewModel.endCall() }
            )

            CallButton(
                icon = if (callState.isVideoEnabled) Icons.Default.Videocam
                       else Icons.Default.VideocamOff,
                isActive = !callState.isVideoEnabled,
                onClick = { viewModel.toggleVideo() }
            )
        }
    }
}
```

### Best Practices

**1. Server Infrastructure**:
- STUN servers for public IP discovery
- TURN servers for strict NAT traversal (critical!)
- Signaling server for metadata exchange

**2. Resource Management**:
- Stop video when app goes to background
- Proper disposal of all tracks and connections
- Manage audio focus via AudioManager

**3. Performance**:
- Adaptive bitrate based on network quality
- Use FLAG_KEEP_SCREEN_ON
- Monitor connection quality (ICE state)

**4. Error Handling**:
```kotlin
// ✅ Handle ICE connection states
override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
    when (state) {
        CONNECTED -> _callState.value = _callState.value.copy(isConnected = true)
        FAILED, DISCONNECTED -> {
            _callState.value = _callState.value.copy(isConnected = false)
            endCall()
        }
    }
}
```

### Common Pitfalls

**❌ No TURN server configured**:
- Calls fail behind NAT/firewall
- Solution: always configure TURN in addition to STUN

**❌ Missing runtime permissions**:
```kotlin
// ✅ Correct
val permissions = arrayOf(
    Manifest.permission.CAMERA,
    Manifest.permission.RECORD_AUDIO
)
requestPermissions(permissions, REQUEST_CODE)
```

**❌ Resource leaks**:
```kotlin
// ✅ Correct - dispose everything
fun endCall() {
    localAudioTrack?.dispose()
    localVideoTrack?.dispose()
    videoCapturer?.stopCapture()
    videoCapturer?.dispose()
    peerConnection?.close()
}
```

---

## Follow-ups

- How to implement screen sharing during a video call?
- How to handle network reconnection during an active call?
- How to implement group video calls (multiple participants)?
- How to optimize battery consumption during long video calls?
- How to handle call quality adaptation based on network conditions?

## References

- [WebRTC Official](https://webrtc.org/)
- [WebRTC for Android](https://webrtc.github.io/webrtc-org/native-code/android/)
- [Google Codelabs - WebRTC](https://codelabs.developers.google.com/codelabs/webrtc-web)
- [STUN/TURN Server Setup](https://www.metered.ca/tools/openrelay/)

## Related Questions

### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Understanding HTTP/WebSocket protocols
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Async network operations

### Related (Same Level)
- [[q-design-instagram-stories--android--hard]] - Media handling
- [[q-data-sync-unstable-network--android--hard]] - Network reliability
- [[q-design-whatsapp-app--android--hard]] - Real-time messaging

### Advanced (Harder)
- Design a scalable video conferencing system
- Implement end-to-end encryption for video calls
