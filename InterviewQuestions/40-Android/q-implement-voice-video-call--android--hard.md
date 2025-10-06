---
id: 20251006-000005
title: "How to implement Voice/Video Call in Android? / Как реализовать голосовой/видеозвонок в Android?"
aliases: []

# Classification
topic: android
subtopics: [webrtc, real-time, media, networking, peer-to-peer]
question_kind: implementation
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository

# Workflow & relations
status: draft
moc: moc-android
related: [webrtc, real-time-communication, websocket, media-streaming]

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [android, webrtc, voice-call, video-call, real-time, peer-to-peer, difficulty/hard]
---

# Question (EN)
> How would you implement voice and video calling features in an Android application?

# Вопрос (RU)
> Как бы вы реализовали функции голосовых и видеозвонков в Android приложении?

---

## Answer (EN)

Implementing voice and video calling in Android typically uses **WebRTC (Web Real-Time Communication)**, which provides peer-to-peer audio and video communication with low latency.

### 1. Core Concepts

**WebRTC Components:**
- **PeerConnection**: Manages peer-to-peer connection
- **MediaStream**: Handles audio/video streams
- **ICE (Interactive Connectivity Establishment)**: NAT traversal
- **STUN/TURN Servers**: Help establish connections through firewalls
- **SDP (Session Description Protocol)**: Describes media sessions
- **Signaling Server**: Exchanges connection information (not part of WebRTC)

**Architecture:**
```
┌─────────────┐                    ┌─────────────┐
│  Caller     │                    │  Callee     │
│  Device     │                    │  Device     │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       ├──── Signaling (WebSocket) ──────┤
       │      (Offer/Answer/ICE)          │
       │                                  │
       └──── Media (WebRTC P2P) ─────────┘
              (Audio/Video Stream)

┌──────────────────┐
│ Signaling Server │  (WebSocket/Socket.IO)
│ (Your Backend)   │
└──────────────────┘

┌──────────────────┐
│ STUN/TURN Server │  (Google/Twilio/Custom)
│ (NAT Traversal)  │
└──────────────────┘
```

### 2. Implementation

#### Dependencies

```gradle
// build.gradle (app)
dependencies {
    // WebRTC
    implementation 'org.webrtc:google-webrtc:1.0.32006'

    // Signaling (WebSocket)
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'

    // JSON parsing
    implementation 'org.jetbrains.kotlinx:kotlinx-serialization-json:1.5.1'

    // Coroutines
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
```

#### Data Models

```kotlin
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

    @Serializable
    data class CallOffer(
        val callerId: String,
        val callType: CallType
    ) : SignalingMessage()

    @Serializable
    data class CallAnswer(val accepted: Boolean) : SignalingMessage()

    @Serializable
    object CallEnd : SignalingMessage()
}

enum class CallType {
    AUDIO, VIDEO
}

data class CallState(
    val isConnected: Boolean = false,
    val isMuted: Boolean = false,
    val isVideoEnabled: Boolean = true,
    val isSpeakerOn: Boolean = false,
    val duration: Long = 0
)
```

#### WebRTC Manager

```kotlin
class WebRTCManager(
    private val context: Context,
    private val signalingClient: SignalingClient
) {
    private var peerConnectionFactory: PeerConnectionFactory? = null
    private var peerConnection: PeerConnection? = null
    private var localVideoTrack: VideoTrack? = null
    private var localAudioTrack: AudioTrack? = null
    private var videoCapturer: VideoCapturer? = null

    private val _remoteVideoTrack = MutableStateFlow<VideoTrack?>(null)
    val remoteVideoTrack = _remoteVideoTrack.asStateFlow()

    private val _localVideoTrack = MutableStateFlow<VideoTrack?>(null)
    val localVideoTrack = _localVideoTrack.asStateFlow()

    private val _callState = MutableStateFlow(CallState())
    val callState = _callState.asStateFlow()

    init {
        initializePeerConnectionFactory()
    }

    private fun initializePeerConnectionFactory() {
        val options = PeerConnectionFactory.InitializationOptions.builder(context)
            .setEnableInternalTracer(true)
            .setFieldTrials("WebRTC-H264HighProfile/Enabled/")
            .createInitializationOptions()

        PeerConnectionFactory.initialize(options)

        val encoderFactory = DefaultVideoEncoderFactory(
            EglBase.create().eglBaseContext,
            true,  // enableIntelVp8Encoder
            true   // enableH264HighProfile
        )

        val decoderFactory = DefaultVideoDecoderFactory(
            EglBase.create().eglBaseContext
        )

        peerConnectionFactory = PeerConnectionFactory.builder()
            .setVideoEncoderFactory(encoderFactory)
            .setVideoDecoderFactory(decoderFactory)
            .setOptions(PeerConnectionFactory.Options())
            .createPeerConnectionFactory()
    }

    fun startCall(
        isVideoCall: Boolean,
        remotePeerId: String
    ) {
        createPeerConnection()
        createMediaStreams(isVideoCall)

        // Create offer
        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(object : SdpObserver {
                    override fun onSetSuccess() {
                        // Send offer to remote peer
                        signalingClient.sendOffer(remotePeerId, sdp.description)
                    }

                    override fun onSetFailure(error: String?) {
                        Log.e("WebRTC", "Failed to set local description: $error")
                    }

                    override fun onCreateSuccess(p0: SessionDescription?) {}
                    override fun onCreateFailure(p0: String?) {}
                }, sdp)
            }

            override fun onCreateFailure(error: String?) {
                Log.e("WebRTC", "Failed to create offer: $error")
            }

            override fun onSetSuccess() {}
            override fun onSetFailure(p0: String?) {}
        }, MediaConstraints())
    }

    fun answerCall(isVideoCall: Boolean) {
        createPeerConnection()
        createMediaStreams(isVideoCall)

        // Create answer
        peerConnection?.createAnswer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                peerConnection?.setLocalDescription(object : SdpObserver {
                    override fun onSetSuccess() {
                        // Send answer to remote peer
                        signalingClient.sendAnswer(sdp.description)
                    }

                    override fun onSetFailure(error: String?) {
                        Log.e("WebRTC", "Failed to set local description: $error")
                    }

                    override fun onCreateSuccess(p0: SessionDescription?) {}
                    override fun onCreateFailure(p0: String?) {}
                }, sdp)
            }

            override fun onCreateFailure(error: String?) {
                Log.e("WebRTC", "Failed to create answer: $error")
            }

            override fun onSetSuccess() {}
            override fun onSetFailure(p0: String?) {}
        }, MediaConstraints())
    }

    private fun createPeerConnection() {
        val iceServers = listOf(
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302")
                .createIceServer(),
            // TURN server (required for some networks)
            PeerConnection.IceServer.builder("turn:your-turn-server.com:3478")
                .setUsername("username")
                .setPassword("password")
                .createIceServer()
        )

        val rtcConfig = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
            tcpCandidatePolicy = PeerConnection.TcpCandidatePolicy.ENABLED
            bundlePolicy = PeerConnection.BundlePolicy.MAXBUNDLE
            rtcpMuxPolicy = PeerConnection.RtcpMuxPolicy.REQUIRE
            continualGatheringPolicy =
                PeerConnection.ContinualGatheringPolicy.GATHER_CONTINUALLY
        }

        peerConnection = peerConnectionFactory?.createPeerConnection(
            rtcConfig,
            object : PeerConnection.Observer {
                override fun onIceCandidate(candidate: IceCandidate) {
                    // Send ICE candidate to remote peer
                    signalingClient.sendIceCandidate(
                        candidate.sdpMid,
                        candidate.sdpMLineIndex,
                        candidate.sdp
                    )
                }

                override fun onAddStream(stream: MediaStream) {
                    // Remote stream added
                    stream.videoTracks?.firstOrNull()?.let { videoTrack ->
                        _remoteVideoTrack.value = videoTrack
                    }
                }

                override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
                    when (state) {
                        PeerConnection.IceConnectionState.CONNECTED -> {
                            _callState.value = _callState.value.copy(isConnected = true)
                        }
                        PeerConnection.IceConnectionState.DISCONNECTED,
                        PeerConnection.IceConnectionState.FAILED,
                        PeerConnection.IceConnectionState.CLOSED -> {
                            _callState.value = _callState.value.copy(isConnected = false)
                            endCall()
                        }
                        else -> {}
                    }
                }

                override fun onIceGatheringChange(state: PeerConnection.IceGatheringState) {}
                override fun onSignalingChange(state: PeerConnection.SignalingState) {}
                override fun onIceCandidatesRemoved(candidates: Array<out IceCandidate>?) {}
                override fun onRemoveStream(stream: MediaStream?) {}
                override fun onDataChannel(dataChannel: DataChannel?) {}
                override fun onRenegotiationNeeded() {}
                override fun onAddTrack(receiver: RtpReceiver?, streams: Array<out MediaStream>?) {}
            }
        )
    }

    private fun createMediaStreams(isVideoCall: Boolean) {
        val mediaStreamId = "local_stream"
        val localStream = peerConnectionFactory?.createLocalMediaStream(mediaStreamId)

        // Audio track
        val audioSource = peerConnectionFactory?.createAudioSource(MediaConstraints())
        localAudioTrack = peerConnectionFactory?.createAudioTrack("audio_track", audioSource)
        localStream?.addTrack(localAudioTrack)

        // Video track (if video call)
        if (isVideoCall) {
            videoCapturer = createVideoCapturer()
            val surfaceTextureHelper = SurfaceTextureHelper.create(
                "CaptureThread",
                EglBase.create().eglBaseContext
            )

            val videoSource = peerConnectionFactory?.createVideoSource(
                videoCapturer?.isScreencast ?: false
            )

            videoCapturer?.initialize(
                surfaceTextureHelper,
                context,
                videoSource?.capturerObserver
            )

            videoCapturer?.startCapture(1280, 720, 30)

            localVideoTrack = peerConnectionFactory?.createVideoTrack("video_track", videoSource)
            localStream?.addTrack(localVideoTrack)

            _localVideoTrack.value = localVideoTrack
        }

        peerConnection?.addStream(localStream)
    }

    private fun createVideoCapturer(): VideoCapturer? {
        val enumerator = Camera2Enumerator(context)

        // Try front camera first
        for (deviceName in enumerator.deviceNames) {
            if (enumerator.isFrontFacing(deviceName)) {
                return enumerator.createCapturer(deviceName, null)
            }
        }

        // Fallback to back camera
        for (deviceName in enumerator.deviceNames) {
            if (enumerator.isBackFacing(deviceName)) {
                return enumerator.createCapturer(deviceName, null)
            }
        }

        return null
    }

    fun handleRemoteOffer(sdp: String) {
        val sessionDescription = SessionDescription(
            SessionDescription.Type.OFFER,
            sdp
        )

        peerConnection?.setRemoteDescription(object : SdpObserver {
            override fun onSetSuccess() {
                Log.d("WebRTC", "Remote offer set successfully")
            }

            override fun onSetFailure(error: String?) {
                Log.e("WebRTC", "Failed to set remote offer: $error")
            }

            override fun onCreateSuccess(p0: SessionDescription?) {}
            override fun onCreateFailure(p0: String?) {}
        }, sessionDescription)
    }

    fun handleRemoteAnswer(sdp: String) {
        val sessionDescription = SessionDescription(
            SessionDescription.Type.ANSWER,
            sdp
        )

        peerConnection?.setRemoteDescription(object : SdpObserver {
            override fun onSetSuccess() {
                Log.d("WebRTC", "Remote answer set successfully")
            }

            override fun onSetFailure(error: String?) {
                Log.e("WebRTC", "Failed to set remote answer: $error")
            }

            override fun onCreateSuccess(p0: SessionDescription?) {}
            override fun onCreateFailure(p0: String?) {}
        }, sessionDescription)
    }

    fun handleRemoteIceCandidate(
        sdpMid: String,
        sdpMLineIndex: Int,
        sdp: String
    ) {
        val iceCandidate = IceCandidate(sdpMid, sdpMLineIndex, sdp)
        peerConnection?.addIceCandidate(iceCandidate)
    }

    fun toggleMute() {
        val newMuteState = !_callState.value.isMuted
        localAudioTrack?.setEnabled(!newMuteState)
        _callState.value = _callState.value.copy(isMuted = newMuteState)
    }

    fun toggleVideo() {
        val newVideoState = !_callState.value.isVideoEnabled
        localVideoTrack?.setEnabled(newVideoState)
        _callState.value = _callState.value.copy(isVideoEnabled = newVideoState)
    }

    fun switchCamera() {
        (videoCapturer as? CameraVideoCapturer)?.switchCamera(null)
    }

    fun endCall() {
        localAudioTrack?.dispose()
        localVideoTrack?.dispose()
        videoCapturer?.stopCapture()
        videoCapturer?.dispose()
        peerConnection?.close()
        peerConnection = null

        _callState.value = CallState()
        _localVideoTrack.value = null
        _remoteVideoTrack.value = null

        signalingClient.sendCallEnd()
    }
}
```

#### Signaling Client

```kotlin
class SignalingClient(
    private val okHttpClient: OkHttpClient
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<SignalingMessage>()
    val messages = _messages.asSharedFlow()

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://your-signaling-server.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<SignalingMessage>(text)
                viewModelScope.launch {
                    _messages.emit(message)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e("Signaling", "Connection failed", t)
            }
        })
    }

    fun sendOffer(remotePeerId: String, sdp: String) {
        val message = SignalingMessage.Offer(sdp)
        send(message)
    }

    fun sendAnswer(sdp: String) {
        val message = SignalingMessage.Answer(sdp)
        send(message)
    }

    fun sendIceCandidate(sdpMid: String, sdpMLineIndex: Int, sdp: String) {
        val message = SignalingMessage.IceCandidate(sdpMid, sdpMLineIndex, sdp)
        send(message)
    }

    fun sendCallEnd() {
        send(SignalingMessage.CallEnd)
    }

    private fun send(message: SignalingMessage) {
        val json = Json.encodeToString(message)
        webSocket?.send(json)
    }

    fun disconnect() {
        webSocket?.close(1000, "Client closing")
    }
}
```

#### UI (Jetpack Compose)

```kotlin
@Composable
fun VideoCallScreen(
    viewModel: CallViewModel,
    onEndCall: () -> Unit
) {
    val callState by viewModel.callState.collectAsState()
    val localVideoTrack by viewModel.localVideoTrack.collectAsState()
    val remoteVideoTrack by viewModel.remoteVideoTrack.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // Remote video (full screen)
        remoteVideoTrack?.let { videoTrack ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FILL)
                        videoTrack.addSink(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // Local video (picture-in-picture)
        localVideoTrack?.let { videoTrack ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(EglBase.create().eglBaseContext, null)
                        setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FILL)
                        setZOrderMediaOverlay(true)
                        videoTrack.addSink(this)
                    }
                },
                modifier = Modifier
                    .size(120.dp, 160.dp)
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
                    .clip(RoundedCornerShape(8.dp))
            )
        }

        // Call controls
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Call duration
            Text(
                text = formatDuration(callState.duration),
                color = Color.White,
                fontSize = 18.sp
            )

            Spacer(modifier = Modifier.height(24.dp))

            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Mute button
                IconButton(
                    onClick = { viewModel.toggleMute() },
                    modifier = Modifier
                        .size(56.dp)
                        .background(
                            color = if (callState.isMuted) Color.Red else Color.Gray,
                            shape = CircleShape
                        )
                ) {
                    Icon(
                        imageVector = if (callState.isMuted)
                            Icons.Default.MicOff else Icons.Default.Mic,
                        contentDescription = "Mute",
                        tint = Color.White
                    )
                }

                // End call button
                IconButton(
                    onClick = {
                        viewModel.endCall()
                        onEndCall()
                    },
                    modifier = Modifier
                        .size(56.dp)
                        .background(color = Color.Red, shape = CircleShape)
                ) {
                    Icon(
                        imageVector = Icons.Default.CallEnd,
                        contentDescription = "End call",
                        tint = Color.White
                    )
                }

                // Video toggle button
                IconButton(
                    onClick = { viewModel.toggleVideo() },
                    modifier = Modifier
                        .size(56.dp)
                        .background(
                            color = if (!callState.isVideoEnabled) Color.Red else Color.Gray,
                            shape = CircleShape
                        )
                ) {
                    Icon(
                        imageVector = if (callState.isVideoEnabled)
                            Icons.Default.Videocam else Icons.Default.VideocamOff,
                        contentDescription = "Toggle video",
                        tint = Color.White
                    )
                }

                // Switch camera button
                IconButton(
                    onClick = { viewModel.switchCamera() },
                    modifier = Modifier
                        .size(56.dp)
                        .background(color = Color.Gray, shape = CircleShape)
                ) {
                    Icon(
                        imageVector = Icons.Default.Cameraswitch,
                        contentDescription = "Switch camera",
                        tint = Color.White
                    )
                }
            }
        }
    }
}
```

### 3. Best Practices

1. **STUN/TURN Servers**: Always configure both for reliability
2. **Permissions**: Request camera/microphone permissions at runtime
3. **Battery Optimization**: Stop video when app goes to background
4. **Network Quality**: Implement adaptive bitrate based on connection
5. **Error Handling**: Handle connection failures gracefully
6. **Audio Focus**: Manage audio focus properly
7. **Keep Screen On**: Use FLAG_KEEP_SCREEN_ON during calls

### Common Pitfalls

1. Not configuring TURN servers (calls fail behind NAT)
2. Missing runtime permissions
3. Not disposing resources properly
4. Poor error handling for network failures
5. Not testing on different network conditions
6. Ignoring battery drain from video

## Ответ (RU)

Реализация голосовых и видеозвонков в Android обычно использует **WebRTC (Web Real-Time Communication)**, который обеспечивает peer-to-peer аудио и видео связь с низкой задержкой.

### Ключевые компоненты WebRTC:

- **PeerConnection**: Управляет peer-to-peer соединением
- **MediaStream**: Обрабатывает аудио/видео потоки
- **ICE**: Проход через NAT
- **STUN/TURN серверы**: Помогают установить соединения через файрволы
- **SDP**: Описывает медиа сессии
- **Signaling Server**: Обмен информацией о соединении

### Процесс установки соединения:

1. Caller создает PeerConnection и MediaStream
2. Caller создает offer (SDP) и отправляет через signaling server
3. Callee получает offer, создает answer (SDP)
4. Обмен ICE candidates для NAT traversal
5. Установка прямого P2P соединения
6. Начало передачи аудио/видео

### Основные функции:

- Переключение мут/размут микрофона
- Включение/выключение видео
- Переключение камеры (фронтальная/задняя)
- Завершение звонка
- Отображение локального и удаленного видео

### Лучшие практики:

1. Использовать STUN и TURN серверы для надежности
2. Запрашивать разрешения камеры/микрофона
3. Останавливать видео при переходе в фон
4. Адаптивный битрейт в зависимости от сети
5. Правильное управление аудио фокусом
6. Держать экран включенным во время звонка

---

## References
- [WebRTC Official](https://webrtc.org/)
- [WebRTC for Android](https://webrtc.github.io/webrtc-org/native-code/android/)
- [Google WebRTC Library](https://bintray.com/google/webrtc/google-webrtc)
- [Agora WebRTC Guide](https://docs.agora.io/en/video-calling/overview/product-overview)

## Related Questions
- What is WebRTC and how does it work?
- How to handle NAT traversal in P2P connections?
- What is the difference between STUN and TURN servers?
- How to optimize video quality based on network conditions?
