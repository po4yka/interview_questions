---
id: android-380
title: "Vulkan RenderScript / Vulkan и RenderScript"
aliases: [Vulkan RenderScript]
topic: android
subtopics: [performance-rendering]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gpu-rendering, c-performance, q-surfaceview-rendering--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/performance-rendering, compute, difficulty/hard, gpu, graphics, renderscript, vulkan]
---

# Vulkan and RenderScript Alternatives for GPU Computing

---

## Answer (EN)
# Question (EN)
How do you use Vulkan for low-level GPU operations in Android? What are the alternatives to deprecated RenderScript? How do you implement compute shaders and GPU-accelerated image processing?

## Answer (EN)
With RenderScript deprecated in Android 12, developers need alternative approaches for GPU computing. Vulkan provides low-level GPU access, while other options include GPU Compute shaders, OpenGL ES compute, and platform-specific solutions.

#### 1. Vulkan Basics for Android

**Vulkan Setup and Initialization:**
```kotlin
import android.view.Surface
import org.lwjgl.vulkan.*
import org.lwjgl.system.MemoryStack
import java.nio.ByteBuffer
import java.nio.IntBuffer

class VulkanRenderer {

    private var instance: VkInstance? = null
    private var physicalDevice: VkPhysicalDevice? = null
    private var device: VkDevice? = null
    private var graphicsQueue: VkQueue? = null
    private var surface: Long = 0

    /**
     * Initialize Vulkan instance
     */
    fun initVulkan(surface: Surface): Boolean {
        return try {
            // Create Vulkan instance
            MemoryStack.stackPush().use { stack ->
                val appInfo = VkApplicationInfo.calloc(stack)
                    .sType(VK10.VK_STRUCTURE_TYPE_APPLICATION_INFO)
                    .pApplicationName(stack.UTF8("Android Vulkan App"))
                    .applicationVersion(VK10.VK_MAKE_VERSION(1, 0, 0))
                    .pEngineName(stack.UTF8("No Engine"))
                    .engineVersion(VK10.VK_MAKE_VERSION(1, 0, 0))
                    .apiVersion(VK11.VK_API_VERSION_1_1)

                val createInfo = VkInstanceCreateInfo.calloc(stack)
                    .sType(VK10.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO)
                    .pApplicationInfo(appInfo)

                val pInstance = stack.mallocPointer(1)
                val result = VK10.vkCreateInstance(createInfo, null, pInstance)

                if (result != VK10.VK_SUCCESS) {
                    throw RuntimeException("Failed to create Vulkan instance: $result")
                }

                instance = VkInstance(pInstance.get(0), createInfo)
            }

            // Select physical device (GPU)
            selectPhysicalDevice()

            // Create logical device
            createLogicalDevice()

            // Create surface from Android Surface
            createSurface(surface)

            true
        } catch (e: Exception) {
            Log.e("Vulkan", "Initialization failed", e)
            false
        }
    }

    private fun selectPhysicalDevice() {
        MemoryStack.stackPush().use { stack ->
            val deviceCount = stack.mallocInt(1)
            VK10.vkEnumeratePhysicalDevices(instance, deviceCount, null)

            if (deviceCount.get(0) == 0) {
                throw RuntimeException("No Vulkan-compatible GPU found")
            }

            val devices = stack.mallocPointer(deviceCount.get(0))
            VK10.vkEnumeratePhysicalDevices(instance, deviceCount, devices)

            // Select first suitable device
            for (i in 0 until deviceCount.get(0)) {
                val device = VkPhysicalDevice(devices.get(i), instance)
                if (isDeviceSuitable(device)) {
                    physicalDevice = device
                    break
                }
            }

            if (physicalDevice == null) {
                throw RuntimeException("No suitable GPU found")
            }
        }
    }

    private fun isDeviceSuitable(device: VkPhysicalDevice): Boolean {
        MemoryStack.stackPush().use { stack ->
            val deviceProperties = VkPhysicalDeviceProperties.malloc(stack)
            VK10.vkGetPhysicalDeviceProperties(device, deviceProperties)

            val deviceFeatures = VkPhysicalDeviceFeatures.malloc(stack)
            VK10.vkGetPhysicalDeviceFeatures(device, deviceFeatures)

            // Check if device supports required features
            return deviceFeatures.geometryShader() &&
                   findQueueFamilies(device) != -1
        }
    }

    private fun findQueueFamilies(device: VkPhysicalDevice): Int {
        MemoryStack.stackPush().use { stack ->
            val queueFamilyCount = stack.mallocInt(1)
            VK10.vkGetPhysicalDeviceQueueFamilyProperties(device, queueFamilyCount, null)

            val queueFamilies = VkQueueFamilyProperties.malloc(queueFamilyCount.get(0), stack)
            VK10.vkGetPhysicalDeviceQueueFamilyProperties(device, queueFamilyCount, queueFamilies)

            for (i in 0 until queueFamilies.capacity()) {
                if (queueFamilies[i].queueFlags() and VK10.VK_QUEUE_GRAPHICS_BIT != 0) {
                    return i
                }
            }

            return -1
        }
    }

    private fun createLogicalDevice() {
        MemoryStack.stackPush().use { stack ->
            val queueFamilyIndex = findQueueFamilies(physicalDevice!!)

            val queuePriority = stack.floats(1.0f)
            val queueCreateInfo = VkDeviceQueueCreateInfo.calloc(1, stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO)
                .queueFamilyIndex(queueFamilyIndex)
                .pQueuePriorities(queuePriority)

            val deviceFeatures = VkPhysicalDeviceFeatures.calloc(stack)

            val createInfo = VkDeviceCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO)
                .pQueueCreateInfos(queueCreateInfo)
                .pEnabledFeatures(deviceFeatures)

            val pDevice = stack.mallocPointer(1)
            val result = VK10.vkCreateDevice(physicalDevice, createInfo, null, pDevice)

            if (result != VK10.VK_SUCCESS) {
                throw RuntimeException("Failed to create logical device: $result")
            }

            device = VkDevice(pDevice.get(0), physicalDevice, createInfo)

            // Get queue handle
            val pQueue = stack.mallocPointer(1)
            VK10.vkGetDeviceQueue(device, queueFamilyIndex, 0, pQueue)
            graphicsQueue = VkQueue(pQueue.get(0), device)
        }
    }

    private fun createSurface(androidSurface: Surface) {
        // Create Vulkan surface from Android Surface
        // This requires platform-specific code (VK_KHR_android_surface)
        MemoryStack.stackPush().use { stack ->
            val surfaceCreateInfo = VkAndroidSurfaceCreateInfoKHR.calloc(stack)
                .sType(KHRAndroidSurface.VK_STRUCTURE_TYPE_ANDROID_SURFACE_CREATE_INFO_KHR)
                .window(androidSurface.nativeWindow)

            val pSurface = stack.mallocLong(1)
            val result = KHRAndroidSurface.vkCreateAndroidSurfaceKHR(
                instance,
                surfaceCreateInfo,
                null,
                pSurface
            )

            if (result != VK10.VK_SUCCESS) {
                throw RuntimeException("Failed to create surface: $result")
            }

            surface = pSurface.get(0)
        }
    }

    fun cleanup() {
        device?.let { VK10.vkDestroyDevice(it, null) }
        if (surface != 0L) {
            KHRSurface.vkDestroySurfaceKHR(instance, surface, null)
        }
        instance?.let { VK10.vkDestroyInstance(it, null) }
    }
}
```

**Vulkan Compute Shader:**
```kotlin
class VulkanComputeProcessor {

    private var device: VkDevice? = null
    private var commandPool: Long = 0
    private var computePipeline: Long = 0
    private var pipelineLayout: Long = 0
    private var descriptorSetLayout: Long = 0

    /**
     * Create compute pipeline for image processing
     */
    fun createComputePipeline(device: VkDevice, shaderPath: String) {
        this.device = device

        MemoryStack.stackPush().use { stack ->
            // Load compute shader (SPIR-V bytecode)
            val shaderCode = loadShader(shaderPath)

            val shaderModuleCreateInfo = VkShaderModuleCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO)
                .pCode(shaderCode)

            val pShaderModule = stack.mallocLong(1)
            VK10.vkCreateShaderModule(device, shaderModuleCreateInfo, null, pShaderModule)
            val shaderModule = pShaderModule.get(0)

            // Create descriptor set layout
            val layoutBinding = VkDescriptorSetLayoutBinding.calloc(2, stack)

            // Input image
            layoutBinding[0]
                .binding(0)
                .descriptorType(VK10.VK_DESCRIPTOR_TYPE_STORAGE_IMAGE)
                .descriptorCount(1)
                .stageFlags(VK10.VK_SHADER_STAGE_COMPUTE_BIT)

            // Output image
            layoutBinding[1]
                .binding(1)
                .descriptorType(VK10.VK_DESCRIPTOR_TYPE_STORAGE_IMAGE)
                .descriptorCount(1)
                .stageFlags(VK10.VK_SHADER_STAGE_COMPUTE_BIT)

            val layoutInfo = VkDescriptorSetLayoutCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO)
                .pBindings(layoutBinding)

            val pDescriptorSetLayout = stack.mallocLong(1)
            VK10.vkCreateDescriptorSetLayout(device, layoutInfo, null, pDescriptorSetLayout)
            descriptorSetLayout = pDescriptorSetLayout.get(0)

            // Create pipeline layout
            val pipelineLayoutInfo = VkPipelineLayoutCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO)
                .pSetLayouts(stack.longs(descriptorSetLayout))

            val pPipelineLayout = stack.mallocLong(1)
            VK10.vkCreatePipelineLayout(device, pipelineLayoutInfo, null, pPipelineLayout)
            pipelineLayout = pPipelineLayout.get(0)

            // Create compute pipeline
            val shaderStageInfo = VkPipelineShaderStageCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO)
                .stage(VK10.VK_SHADER_STAGE_COMPUTE_BIT)
                .module(shaderModule)
                .pName(stack.UTF8("main"))

            val pipelineInfo = VkComputePipelineCreateInfo.calloc(1, stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO)
                .stage(shaderStageInfo)
                .layout(pipelineLayout)

            val pPipeline = stack.mallocLong(1)
            VK10.vkCreateComputePipelines(
                device,
                VK10.VK_NULL_HANDLE,
                pipelineInfo,
                null,
                pPipeline
            )
            computePipeline = pPipeline.get(0)

            // Cleanup shader module
            VK10.vkDestroyShaderModule(device, shaderModule, null)
        }
    }

    /**
     * Execute compute shader
     */
    fun executeCompute(
        inputImage: VulkanImage,
        outputImage: VulkanImage,
        width: Int,
        height: Int
    ) {
        MemoryStack.stackPush().use { stack ->
            // Create command buffer
            val allocInfo = VkCommandBufferAllocateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO)
                .commandPool(commandPool)
                .level(VK10.VK_COMMAND_BUFFER_LEVEL_PRIMARY)
                .commandBufferCount(1)

            val pCommandBuffer = stack.mallocPointer(1)
            VK10.vkAllocateCommandBuffers(device, allocInfo, pCommandBuffer)
            val commandBuffer = VkCommandBuffer(pCommandBuffer.get(0), device)

            // Begin recording
            val beginInfo = VkCommandBufferBeginInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO)
                .flags(VK10.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT)

            VK10.vkBeginCommandBuffer(commandBuffer, beginInfo)

            // Bind pipeline
            VK10.vkCmdBindPipeline(
                commandBuffer,
                VK10.VK_PIPELINE_BIND_POINT_COMPUTE,
                computePipeline
            )

            // Bind descriptor sets (input/output images)
            // ... descriptor set binding code ...

            // Dispatch compute shader
            val workGroupSize = 16
            val groupCountX = (width + workGroupSize - 1) / workGroupSize
            val groupCountY = (height + workGroupSize - 1) / workGroupSize

            VK10.vkCmdDispatch(commandBuffer, groupCountX, groupCountY, 1)

            // End recording
            VK10.vkEndCommandBuffer(commandBuffer)

            // Submit command buffer
            val submitInfo = VkSubmitInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_SUBMIT_INFO)
                .pCommandBuffers(pCommandBuffer)

            VK10.vkQueueSubmit(graphicsQueue, submitInfo, VK10.VK_NULL_HANDLE)
            VK10.vkQueueWaitIdle(graphicsQueue)
        }
    }

    private fun loadShader(path: String): ByteBuffer {
        // Load SPIR-V shader bytecode
        // This would load from assets or compiled shaders
        return ByteBuffer.allocateDirect(0)
    }

    fun cleanup() {
        device?.let { dev ->
            if (computePipeline != 0L) {
                VK10.vkDestroyPipeline(dev, computePipeline, null)
            }
            if (pipelineLayout != 0L) {
                VK10.vkDestroyPipelineLayout(dev, pipelineLayout, null)
            }
            if (descriptorSetLayout != 0L) {
                VK10.vkDestroyDescriptorSetLayout(dev, descriptorSetLayout, null)
            }
        }
    }
}

data class VulkanImage(
    val image: Long,
    val memory: Long,
    val view: Long
)
```

**Example Compute Shader (GLSL):**
```glsl
#version 450

// Compute shader for image blur

layout (local_size_x = 16, local_size_y = 16) in;

layout (binding = 0, rgba8) uniform readonly image2D inputImage;
layout (binding = 1, rgba8) uniform writeonly image2D outputImage;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(inputImage);

    if (pos.x >= size.x || pos.y >= size.y) {
        return;
    }

    // Simple box blur
    vec4 color = vec4(0.0);
    int radius = 2;
    int count = 0;

    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            ivec2 samplePos = pos + ivec2(x, y);
            if (samplePos.x >= 0 && samplePos.x < size.x &&
                samplePos.y >= 0 && samplePos.y < size.y) {
                color += imageLoad(inputImage, samplePos);
                count++;
            }
        }
    }

    color /= float(count);
    imageStore(outputImage, pos, color);
}
```

#### 2. RenderScript Alternatives

**Using RenderScript Intrinsics (still works but deprecated):**
```kotlin
class RenderScriptProcessor(private val context: Context) {

    private val renderScript = RenderScript.create(context)

    /**
     * Apply blur using RenderScript
     * Note: RenderScript is deprecated in Android 12+
     */
    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            input.config
        )

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        val blurScript = ScriptIntrinsicBlur.create(
            renderScript,
            Element.U8_4(renderScript)
        )

        blurScript.setRadius(radius.coerceIn(0f, 25f))
        blurScript.setInput(inputAllocation)
        blurScript.forEach(outputAllocation)

        outputAllocation.copyTo(output)

        // Cleanup
        inputAllocation.destroy()
        outputAllocation.destroy()
        blurScript.destroy()

        return output
    }

    /**
     * Custom RenderScript kernel
     */
    fun applyCustomKernel(input: Bitmap): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            input.config
        )

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        // Load custom script (would be compiled from .rs file)
        // val script = ScriptC_custom(renderScript)
        // script._input = inputAllocation
        // script.forEach_process(outputAllocation)

        outputAllocation.copyTo(output)

        inputAllocation.destroy()
        outputAllocation.destroy()

        return output
    }

    fun cleanup() {
        renderScript.destroy()
    }
}
```

**RenderScript Migration to GPU Compute:**
```kotlin
/**
 * Modern alternative to RenderScript using GPU Compute APIs
 */
class GPUComputeProcessor(private val context: Context) {

    // Choose implementation based on availability
    private val processor: ImageProcessor = when {
        isVulkanSupported() -> VulkanImageProcessor(context)
        isOpenGLES31Supported() -> OpenGLES31ComputeProcessor(context)
        else -> CPUImageProcessor() // Fallback
    }

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        return processor.blur(input, radius)
    }

    fun applyConvolution(input: Bitmap, kernel: FloatArray): Bitmap {
        return processor.convolve(input, kernel)
    }

    private fun isVulkanSupported(): Boolean {
        return context.packageManager.hasSystemFeature(
            PackageManager.FEATURE_VULKAN_HARDWARE_VERSION,
            0x00400000 // Vulkan 1.0
        )
    }

    private fun isOpenGLES31Supported(): Boolean {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        return activityManager.deviceConfigurationInfo.reqGlEsVersion >= 0x00030001
    }

    fun cleanup() {
        processor.cleanup()
    }
}

interface ImageProcessor {
    fun blur(input: Bitmap, radius: Float): Bitmap
    fun convolve(input: Bitmap, kernel: FloatArray): Bitmap
    fun cleanup()
}
```

#### 3. OpenGL ES Compute Shaders

**OpenGL ES 3.1 Compute Implementation:**
```kotlin
class OpenGLES31ComputeProcessor(private val context: Context) : ImageProcessor {

    private var computeProgram = 0
    private val eglHelper = EGLHelper()

    init {
        eglHelper.initialize()
        setupComputeShader()
    }

    private fun setupComputeShader() {
        val computeShaderCode = """
            #version 310 es

            layout (local_size_x = 16, local_size_y = 16) in;

            layout (binding = 0, rgba8) uniform readonly highp image2D inputImage;
            layout (binding = 1, rgba8) uniform writeonly highp image2D outputImage;

            uniform float radius;

            void main() {
                ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
                ivec2 size = imageSize(inputImage);

                if (pos.x >= size.x || pos.y >= size.y) {
                    return;
                }

                // Box blur implementation
                vec4 color = vec4(0.0);
                int r = int(radius);
                int count = 0;

                for (int y = -r; y <= r; y++) {
                    for (int x = -r; x <= r; x++) {
                        ivec2 samplePos = clamp(
                            pos + ivec2(x, y),
                            ivec2(0),
                            size - ivec2(1)
                        );
                        color += imageLoad(inputImage, samplePos);
                        count++;
                    }
                }

                color /= float(count);
                imageStore(outputImage, pos, color);
            }
        """.trimIndent()

        computeProgram = createComputeProgram(computeShaderCode)
    }

    private fun createComputeProgram(shaderCode: String): Int {
        val shader = GLES31.glCreateShader(GLES31.GL_COMPUTE_SHADER)
        GLES31.glShaderSource(shader, shaderCode)
        GLES31.glCompileShader(shader)

        // Check compilation status
        val status = IntArray(1)
        GLES31.glGetShaderiv(shader, GLES31.GL_COMPILE_STATUS, status, 0)
        if (status[0] == GLES31.GL_FALSE) {
            val log = GLES31.glGetShaderInfoLog(shader)
            throw RuntimeException("Shader compilation failed: $log")
        }

        val program = GLES31.glCreateProgram()
        GLES31.glAttachShader(program, shader)
        GLES31.glLinkProgram(program)

        // Check link status
        GLES31.glGetProgramiv(program, GLES31.GL_LINK_STATUS, status, 0)
        if (status[0] == GLES31.GL_FALSE) {
            val log = GLES31.glGetProgramInfoLog(program)
            throw RuntimeException("Program linking failed: $log")
        }

        GLES31.glDeleteShader(shader)
        return program
    }

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            Bitmap.Config.ARGB_8888
        )

        // Create textures
        val textures = IntArray(2)
        GLES31.glGenTextures(2, textures, 0)

        // Upload input texture
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[0])
        GLUtils.texImage2D(GLES31.GL_TEXTURE_2D, 0, input, 0)
        GLES31.glBindImageTexture(
            0,
            textures[0],
            0,
            false,
            0,
            GLES31.GL_READ_ONLY,
            GLES31.GL_RGBA8
        )

        // Setup output texture
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[1])
        GLES31.glTexImage2D(
            GLES31.GL_TEXTURE_2D,
            0,
            GLES31.GL_RGBA8,
            input.width,
            input.height,
            0,
            GLES31.GL_RGBA,
            GLES31.GL_UNSIGNED_BYTE,
            null
        )
        GLES31.glBindImageTexture(
            1,
            textures[1],
            0,
            false,
            0,
            GLES31.GL_WRITE_ONLY,
            GLES31.GL_RGBA8
        )

        // Use compute shader
        GLES31.glUseProgram(computeProgram)
        val radiusLocation = GLES31.glGetUniformLocation(computeProgram, "radius")
        GLES31.glUniform1f(radiusLocation, radius)

        // Dispatch compute
        val workGroupSize = 16
        val groupsX = (input.width + workGroupSize - 1) / workGroupSize
        val groupsY = (input.height + workGroupSize - 1) / workGroupSize
        GLES31.glDispatchCompute(groupsX, groupsY, 1)

        // Wait for completion
        GLES31.glMemoryBarrier(GLES31.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        // Read result
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[1])
        val buffer = ByteBuffer.allocateDirect(input.width * input.height * 4)
        GLES31.glGetTexImage(
            GLES31.GL_TEXTURE_2D,
            0,
            GLES31.GL_RGBA,
            GLES31.GL_UNSIGNED_BYTE,
            buffer
        )

        output.copyPixelsFromBuffer(buffer)

        // Cleanup
        GLES31.glDeleteTextures(2, textures, 0)

        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        // Similar implementation with convolution kernel
        return input
    }

    override fun cleanup() {
        if (computeProgram != 0) {
            GLES31.glDeleteProgram(computeProgram)
        }
        eglHelper.cleanup()
    }
}

class EGLHelper {
    private var eglDisplay: EGLDisplay? = null
    private var eglContext: EGLContext? = null
    private var eglSurface: EGLSurface? = null

    fun initialize() {
        eglDisplay = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY)
        val version = IntArray(2)
        EGL14.eglInitialize(eglDisplay, version, 0, version, 1)

        val configAttribs = intArrayOf(
            EGL14.EGL_RENDERABLE_TYPE, EGLExt.EGL_OPENGL_ES3_BIT_KHR,
            EGL14.EGL_RED_SIZE, 8,
            EGL14.EGL_GREEN_SIZE, 8,
            EGL14.EGL_BLUE_SIZE, 8,
            EGL14.EGL_ALPHA_SIZE, 8,
            EGL14.EGL_NONE
        )

        val configs = arrayOfNulls<EGLConfig>(1)
        val numConfigs = IntArray(1)
        EGL14.eglChooseConfig(
            eglDisplay,
            configAttribs, 0,
            configs, 0, 1,
            numConfigs, 0
        )

        val contextAttribs = intArrayOf(
            EGL14.EGL_CONTEXT_CLIENT_VERSION, 3,
            EGL14.EGL_NONE
        )

        eglContext = EGL14.eglCreateContext(
            eglDisplay,
            configs[0],
            EGL14.EGL_NO_CONTEXT,
            contextAttribs, 0
        )

        val surfaceAttribs = intArrayOf(
            EGL14.EGL_WIDTH, 1,
            EGL14.EGL_HEIGHT, 1,
            EGL14.EGL_NONE
        )

        eglSurface = EGL14.eglCreatePbufferSurface(
            eglDisplay,
            configs[0],
            surfaceAttribs, 0
        )

        EGL14.eglMakeCurrent(eglDisplay, eglSurface, eglSurface, eglContext)
    }

    fun cleanup() {
        EGL14.eglMakeCurrent(
            eglDisplay,
            EGL14.EGL_NO_SURFACE,
            EGL14.EGL_NO_SURFACE,
            EGL14.EGL_NO_CONTEXT
        )
        eglSurface?.let { EGL14.eglDestroySurface(eglDisplay, it) }
        eglContext?.let { EGL14.eglDestroyContext(eglDisplay, it) }
        eglDisplay?.let { EGL14.eglTerminate(it) }
    }
}
```

#### 4. CPU Fallback Implementation

**Software Image Processing:**
```kotlin
class CPUImageProcessor : ImageProcessor {

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val output = input.copy(input.config, true)
        val pixels = IntArray(input.width * input.height)
        input.getPixels(pixels, 0, input.width, 0, 0, input.width, input.height)

        val r = radius.toInt()

        for (y in 0 until input.height) {
            for (x in 0 until input.width) {
                var red = 0
                var green = 0
                var blue = 0
                var alpha = 0
                var count = 0

                for (ky in -r..r) {
                    for (kx in -r..r) {
                        val px = (x + kx).coerceIn(0, input.width - 1)
                        val py = (y + ky).coerceIn(0, input.height - 1)
                        val pixel = pixels[py * input.width + px]

                        alpha += Color.alpha(pixel)
                        red += Color.red(pixel)
                        green += Color.green(pixel)
                        blue += Color.blue(pixel)
                        count++
                    }
                }

                pixels[y * input.width + x] = Color.argb(
                    alpha / count,
                    red / count,
                    green / count,
                    blue / count
                )
            }
        }

        output.setPixels(pixels, 0, input.width, 0, 0, input.width, input.height)
        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        require(kernel.size == 9) { "Only 3x3 kernels supported" }

        val output = input.copy(input.config, true)
        val pixels = IntArray(input.width * input.height)
        input.getPixels(pixels, 0, input.width, 0, 0, input.width, input.height)

        for (y in 1 until input.height - 1) {
            for (x in 1 until input.width - 1) {
                var red = 0f
                var green = 0f
                var blue = 0f

                var ki = 0
                for (ky in -1..1) {
                    for (kx in -1..1) {
                        val pixel = pixels[(y + ky) * input.width + (x + kx)]
                        val k = kernel[ki++]

                        red += Color.red(pixel) * k
                        green += Color.green(pixel) * k
                        blue += Color.blue(pixel) * k
                    }
                }

                pixels[y * input.width + x] = Color.rgb(
                    red.toInt().coerceIn(0, 255),
                    green.toInt().coerceIn(0, 255),
                    blue.toInt().coerceIn(0, 255)
                )
            }
        }

        output.setPixels(pixels, 0, input.width, 0, 0, input.width, input.height)
        return output
    }

    override fun cleanup() {
        // Nothing to cleanup for CPU implementation
    }
}
```

#### 5. Platform-Specific GPU Libraries

**Using Android NDK and GPU libraries:**
```kotlin
class NativeGPUProcessor(context: Context) {

    init {
        System.loadLibrary("native-gpu-processor")
    }

    /**
     * Process image using native GPU code
     */
    fun processImage(input: Bitmap): Bitmap {
        val width = input.width
        val height = input.height
        val pixels = IntArray(width * height)
        input.getPixels(pixels, 0, width, 0, 0, width, height)

        // Call native method
        nativeProcessImage(pixels, width, height)

        val output = Bitmap.createBitmap(width, height, input.config)
        output.setPixels(pixels, 0, width, 0, 0, width, height)

        return output
    }

    private external fun nativeProcessImage(pixels: IntArray, width: Int, height: Int)
}
```

**Native C++ GPU Processing (NDK):**
```cpp
// native-gpu-processor.cpp

#include <jni.h>
#include <android/log.h>
#include <GLES3/gl31.h>
#include <EGL/egl.h>

#define LOG_TAG "GPUProcessor"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

extern "C" JNIEXPORT void JNICALL
Java_com_example_NativeGPUProcessor_nativeProcessImage(
    JNIEnv* env,
    jobject /* this */,
    jintArray pixels,
    jint width,
    jint height
) {
    jint* pixelData = env->GetIntArrayElements(pixels, nullptr);

    // Initialize EGL and OpenGL ES context
    // Create compute shader
    // Upload texture
    // Dispatch compute
    // Read back results

    // Process image using GPU...

    env->ReleaseIntArrayElements(pixels, pixelData, 0);
}
```

### Best Practices

1. **Choose Right API:**
   - Vulkan: Maximum control, lowest overhead, most complex
   - OpenGL ES 3.1+: Compute shaders, easier than Vulkan
   - CPU fallback: Compatibility for older devices

2. **RenderScript Migration:**
   - Evaluate device capabilities at runtime
   - Provide CPU fallback for older devices
   - Consider platform-specific optimizations

3. **Performance:**
   - Use appropriate work group sizes (typically 8x8 or 16x16)
   - Minimize CPU-GPU transfers
   - Batch operations when possible
   - Profile on target devices

4. **Memory Management:**
   - Release GPU resources properly
   - Use texture/buffer pooling
   - Monitor memory usage

5. **Shader Optimization:**
   - Minimize divergent branches
   - Use appropriate precision (mediump vs highp)
   - Optimize memory access patterns
   - Leverage shared memory when possible

### Common Pitfalls

1. **Not checking device capabilities** → Crashes on unsupported devices
   - Always check Vulkan/OpenGL ES version

2. **Synchronization issues** → Race conditions
   - Use proper barriers and fences

3. **Not cleaning up resources** → Memory leaks
   - Release all GPU resources in cleanup()

4. **CPU-GPU transfer overhead** → Poor performance
   - Minimize transfers, keep data on GPU

5. **Incorrect work group sizes** → Inefficient execution
   - Match hardware capabilities

6. **No fallback implementation** → App unusable on older devices
   - Always provide CPU fallback

### Summary

With RenderScript deprecated, Vulkan and OpenGL ES compute shaders are modern alternatives for GPU computing on Android. Vulkan provides maximum control but with complexity, while OpenGL ES 3.1+ offers compute capabilities with easier integration. Always implement CPU fallbacks for compatibility and choose the appropriate API based on device capabilities and performance requirements.

---



## Ответ (RU)


---


## Answer (EN)
# Question (EN)
How do you use Vulkan for low-level GPU operations in Android? What are the alternatives to deprecated RenderScript? How do you implement compute shaders and GPU-accelerated image processing?

## Answer (EN)
With RenderScript deprecated in Android 12, developers need alternative approaches for GPU computing. Vulkan provides low-level GPU access, while other options include GPU Compute shaders, OpenGL ES compute, and platform-specific solutions.

#### 1. Vulkan Basics for Android

**Vulkan Setup and Initialization:**
```kotlin
import android.view.Surface
import org.lwjgl.vulkan.*
import org.lwjgl.system.MemoryStack
import java.nio.ByteBuffer
import java.nio.IntBuffer

class VulkanRenderer {

    private var instance: VkInstance? = null
    private var physicalDevice: VkPhysicalDevice? = null
    private var device: VkDevice? = null
    private var graphicsQueue: VkQueue? = null
    private var surface: Long = 0

    /**
     * Initialize Vulkan instance
     */
    fun initVulkan(surface: Surface): Boolean {
        return try {
            // Create Vulkan instance
            MemoryStack.stackPush().use { stack ->
                val appInfo = VkApplicationInfo.calloc(stack)
                    .sType(VK10.VK_STRUCTURE_TYPE_APPLICATION_INFO)
                    .pApplicationName(stack.UTF8("Android Vulkan App"))
                    .applicationVersion(VK10.VK_MAKE_VERSION(1, 0, 0))
                    .pEngineName(stack.UTF8("No Engine"))
                    .engineVersion(VK10.VK_MAKE_VERSION(1, 0, 0))
                    .apiVersion(VK11.VK_API_VERSION_1_1)

                val createInfo = VkInstanceCreateInfo.calloc(stack)
                    .sType(VK10.VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO)
                    .pApplicationInfo(appInfo)

                val pInstance = stack.mallocPointer(1)
                val result = VK10.vkCreateInstance(createInfo, null, pInstance)

                if (result != VK10.VK_SUCCESS) {
                    throw RuntimeException("Failed to create Vulkan instance: $result")
                }

                instance = VkInstance(pInstance.get(0), createInfo)
            }

            // Select physical device (GPU)
            selectPhysicalDevice()

            // Create logical device
            createLogicalDevice()

            // Create surface from Android Surface
            createSurface(surface)

            true
        } catch (e: Exception) {
            Log.e("Vulkan", "Initialization failed", e)
            false
        }
    }

    private fun selectPhysicalDevice() {
        MemoryStack.stackPush().use { stack ->
            val deviceCount = stack.mallocInt(1)
            VK10.vkEnumeratePhysicalDevices(instance, deviceCount, null)

            if (deviceCount.get(0) == 0) {
                throw RuntimeException("No Vulkan-compatible GPU found")
            }

            val devices = stack.mallocPointer(deviceCount.get(0))
            VK10.vkEnumeratePhysicalDevices(instance, deviceCount, devices)

            // Select first suitable device
            for (i in 0 until deviceCount.get(0)) {
                val device = VkPhysicalDevice(devices.get(i), instance)
                if (isDeviceSuitable(device)) {
                    physicalDevice = device
                    break
                }
            }

            if (physicalDevice == null) {
                throw RuntimeException("No suitable GPU found")
            }
        }
    }

    private fun isDeviceSuitable(device: VkPhysicalDevice): Boolean {
        MemoryStack.stackPush().use { stack ->
            val deviceProperties = VkPhysicalDeviceProperties.malloc(stack)
            VK10.vkGetPhysicalDeviceProperties(device, deviceProperties)

            val deviceFeatures = VkPhysicalDeviceFeatures.malloc(stack)
            VK10.vkGetPhysicalDeviceFeatures(device, deviceFeatures)

            // Check if device supports required features
            return deviceFeatures.geometryShader() &&
                   findQueueFamilies(device) != -1
        }
    }

    private fun findQueueFamilies(device: VkPhysicalDevice): Int {
        MemoryStack.stackPush().use { stack ->
            val queueFamilyCount = stack.mallocInt(1)
            VK10.vkGetPhysicalDeviceQueueFamilyProperties(device, queueFamilyCount, null)

            val queueFamilies = VkQueueFamilyProperties.malloc(queueFamilyCount.get(0), stack)
            VK10.vkGetPhysicalDeviceQueueFamilyProperties(device, queueFamilyCount, queueFamilies)

            for (i in 0 until queueFamilies.capacity()) {
                if (queueFamilies[i].queueFlags() and VK10.VK_QUEUE_GRAPHICS_BIT != 0) {
                    return i
                }
            }

            return -1
        }
    }

    private fun createLogicalDevice() {
        MemoryStack.stackPush().use { stack ->
            val queueFamilyIndex = findQueueFamilies(physicalDevice!!)

            val queuePriority = stack.floats(1.0f)
            val queueCreateInfo = VkDeviceQueueCreateInfo.calloc(1, stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO)
                .queueFamilyIndex(queueFamilyIndex)
                .pQueuePriorities(queuePriority)

            val deviceFeatures = VkPhysicalDeviceFeatures.calloc(stack)

            val createInfo = VkDeviceCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO)
                .pQueueCreateInfos(queueCreateInfo)
                .pEnabledFeatures(deviceFeatures)

            val pDevice = stack.mallocPointer(1)
            val result = VK10.vkCreateDevice(physicalDevice, createInfo, null, pDevice)

            if (result != VK10.VK_SUCCESS) {
                throw RuntimeException("Failed to create logical device: $result")
            }

            device = VkDevice(pDevice.get(0), physicalDevice, createInfo)

            // Get queue handle
            val pQueue = stack.mallocPointer(1)
            VK10.vkGetDeviceQueue(device, queueFamilyIndex, 0, pQueue)
            graphicsQueue = VkQueue(pQueue.get(0), device)
        }
    }

    private fun createSurface(androidSurface: Surface) {
        // Create Vulkan surface from Android Surface
        // This requires platform-specific code (VK_KHR_android_surface)
        MemoryStack.stackPush().use { stack ->
            val surfaceCreateInfo = VkAndroidSurfaceCreateInfoKHR.calloc(stack)
                .sType(KHRAndroidSurface.VK_STRUCTURE_TYPE_ANDROID_SURFACE_CREATE_INFO_KHR)
                .window(androidSurface.nativeWindow)

            val pSurface = stack.mallocLong(1)
            val result = KHRAndroidSurface.vkCreateAndroidSurfaceKHR(
                instance,
                surfaceCreateInfo,
                null,
                pSurface
            )

            if (result != VK10.VK_SUCCESS) {
                throw RuntimeException("Failed to create surface: $result")
            }

            surface = pSurface.get(0)
        }
    }

    fun cleanup() {
        device?.let { VK10.vkDestroyDevice(it, null) }
        if (surface != 0L) {
            KHRSurface.vkDestroySurfaceKHR(instance, surface, null)
        }
        instance?.let { VK10.vkDestroyInstance(it, null) }
    }
}
```

**Vulkan Compute Shader:**
```kotlin
class VulkanComputeProcessor {

    private var device: VkDevice? = null
    private var commandPool: Long = 0
    private var computePipeline: Long = 0
    private var pipelineLayout: Long = 0
    private var descriptorSetLayout: Long = 0

    /**
     * Create compute pipeline for image processing
     */
    fun createComputePipeline(device: VkDevice, shaderPath: String) {
        this.device = device

        MemoryStack.stackPush().use { stack ->
            // Load compute shader (SPIR-V bytecode)
            val shaderCode = loadShader(shaderPath)

            val shaderModuleCreateInfo = VkShaderModuleCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO)
                .pCode(shaderCode)

            val pShaderModule = stack.mallocLong(1)
            VK10.vkCreateShaderModule(device, shaderModuleCreateInfo, null, pShaderModule)
            val shaderModule = pShaderModule.get(0)

            // Create descriptor set layout
            val layoutBinding = VkDescriptorSetLayoutBinding.calloc(2, stack)

            // Input image
            layoutBinding[0]
                .binding(0)
                .descriptorType(VK10.VK_DESCRIPTOR_TYPE_STORAGE_IMAGE)
                .descriptorCount(1)
                .stageFlags(VK10.VK_SHADER_STAGE_COMPUTE_BIT)

            // Output image
            layoutBinding[1]
                .binding(1)
                .descriptorType(VK10.VK_DESCRIPTOR_TYPE_STORAGE_IMAGE)
                .descriptorCount(1)
                .stageFlags(VK10.VK_SHADER_STAGE_COMPUTE_BIT)

            val layoutInfo = VkDescriptorSetLayoutCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO)
                .pBindings(layoutBinding)

            val pDescriptorSetLayout = stack.mallocLong(1)
            VK10.vkCreateDescriptorSetLayout(device, layoutInfo, null, pDescriptorSetLayout)
            descriptorSetLayout = pDescriptorSetLayout.get(0)

            // Create pipeline layout
            val pipelineLayoutInfo = VkPipelineLayoutCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO)
                .pSetLayouts(stack.longs(descriptorSetLayout))

            val pPipelineLayout = stack.mallocLong(1)
            VK10.vkCreatePipelineLayout(device, pipelineLayoutInfo, null, pPipelineLayout)
            pipelineLayout = pPipelineLayout.get(0)

            // Create compute pipeline
            val shaderStageInfo = VkPipelineShaderStageCreateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO)
                .stage(VK10.VK_SHADER_STAGE_COMPUTE_BIT)
                .module(shaderModule)
                .pName(stack.UTF8("main"))

            val pipelineInfo = VkComputePipelineCreateInfo.calloc(1, stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO)
                .stage(shaderStageInfo)
                .layout(pipelineLayout)

            val pPipeline = stack.mallocLong(1)
            VK10.vkCreateComputePipelines(
                device,
                VK10.VK_NULL_HANDLE,
                pipelineInfo,
                null,
                pPipeline
            )
            computePipeline = pPipeline.get(0)

            // Cleanup shader module
            VK10.vkDestroyShaderModule(device, shaderModule, null)
        }
    }

    /**
     * Execute compute shader
     */
    fun executeCompute(
        inputImage: VulkanImage,
        outputImage: VulkanImage,
        width: Int,
        height: Int
    ) {
        MemoryStack.stackPush().use { stack ->
            // Create command buffer
            val allocInfo = VkCommandBufferAllocateInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO)
                .commandPool(commandPool)
                .level(VK10.VK_COMMAND_BUFFER_LEVEL_PRIMARY)
                .commandBufferCount(1)

            val pCommandBuffer = stack.mallocPointer(1)
            VK10.vkAllocateCommandBuffers(device, allocInfo, pCommandBuffer)
            val commandBuffer = VkCommandBuffer(pCommandBuffer.get(0), device)

            // Begin recording
            val beginInfo = VkCommandBufferBeginInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO)
                .flags(VK10.VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT)

            VK10.vkBeginCommandBuffer(commandBuffer, beginInfo)

            // Bind pipeline
            VK10.vkCmdBindPipeline(
                commandBuffer,
                VK10.VK_PIPELINE_BIND_POINT_COMPUTE,
                computePipeline
            )

            // Bind descriptor sets (input/output images)
            // ... descriptor set binding code ...

            // Dispatch compute shader
            val workGroupSize = 16
            val groupCountX = (width + workGroupSize - 1) / workGroupSize
            val groupCountY = (height + workGroupSize - 1) / workGroupSize

            VK10.vkCmdDispatch(commandBuffer, groupCountX, groupCountY, 1)

            // End recording
            VK10.vkEndCommandBuffer(commandBuffer)

            // Submit command buffer
            val submitInfo = VkSubmitInfo.calloc(stack)
                .sType(VK10.VK_STRUCTURE_TYPE_SUBMIT_INFO)
                .pCommandBuffers(pCommandBuffer)

            VK10.vkQueueSubmit(graphicsQueue, submitInfo, VK10.VK_NULL_HANDLE)
            VK10.vkQueueWaitIdle(graphicsQueue)
        }
    }

    private fun loadShader(path: String): ByteBuffer {
        // Load SPIR-V shader bytecode
        // This would load from assets or compiled shaders
        return ByteBuffer.allocateDirect(0)
    }

    fun cleanup() {
        device?.let { dev ->
            if (computePipeline != 0L) {
                VK10.vkDestroyPipeline(dev, computePipeline, null)
            }
            if (pipelineLayout != 0L) {
                VK10.vkDestroyPipelineLayout(dev, pipelineLayout, null)
            }
            if (descriptorSetLayout != 0L) {
                VK10.vkDestroyDescriptorSetLayout(dev, descriptorSetLayout, null)
            }
        }
    }
}

data class VulkanImage(
    val image: Long,
    val memory: Long,
    val view: Long
)
```

**Example Compute Shader (GLSL):**
```glsl
#version 450

// Compute shader for image blur

layout (local_size_x = 16, local_size_y = 16) in;

layout (binding = 0, rgba8) uniform readonly image2D inputImage;
layout (binding = 1, rgba8) uniform writeonly image2D outputImage;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(inputImage);

    if (pos.x >= size.x || pos.y >= size.y) {
        return;
    }

    // Simple box blur
    vec4 color = vec4(0.0);
    int radius = 2;
    int count = 0;

    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            ivec2 samplePos = pos + ivec2(x, y);
            if (samplePos.x >= 0 && samplePos.x < size.x &&
                samplePos.y >= 0 && samplePos.y < size.y) {
                color += imageLoad(inputImage, samplePos);
                count++;
            }
        }
    }

    color /= float(count);
    imageStore(outputImage, pos, color);
}
```

#### 2. RenderScript Alternatives

**Using RenderScript Intrinsics (still works but deprecated):**
```kotlin
class RenderScriptProcessor(private val context: Context) {

    private val renderScript = RenderScript.create(context)

    /**
     * Apply blur using RenderScript
     * Note: RenderScript is deprecated in Android 12+
     */
    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            input.config
        )

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        val blurScript = ScriptIntrinsicBlur.create(
            renderScript,
            Element.U8_4(renderScript)
        )

        blurScript.setRadius(radius.coerceIn(0f, 25f))
        blurScript.setInput(inputAllocation)
        blurScript.forEach(outputAllocation)

        outputAllocation.copyTo(output)

        // Cleanup
        inputAllocation.destroy()
        outputAllocation.destroy()
        blurScript.destroy()

        return output
    }

    /**
     * Custom RenderScript kernel
     */
    fun applyCustomKernel(input: Bitmap): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            input.config
        )

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        // Load custom script (would be compiled from .rs file)
        // val script = ScriptC_custom(renderScript)
        // script._input = inputAllocation
        // script.forEach_process(outputAllocation)

        outputAllocation.copyTo(output)

        inputAllocation.destroy()
        outputAllocation.destroy()

        return output
    }

    fun cleanup() {
        renderScript.destroy()
    }
}
```

**RenderScript Migration to GPU Compute:**
```kotlin
/**
 * Modern alternative to RenderScript using GPU Compute APIs
 */
class GPUComputeProcessor(private val context: Context) {

    // Choose implementation based on availability
    private val processor: ImageProcessor = when {
        isVulkanSupported() -> VulkanImageProcessor(context)
        isOpenGLES31Supported() -> OpenGLES31ComputeProcessor(context)
        else -> CPUImageProcessor() // Fallback
    }

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        return processor.blur(input, radius)
    }

    fun applyConvolution(input: Bitmap, kernel: FloatArray): Bitmap {
        return processor.convolve(input, kernel)
    }

    private fun isVulkanSupported(): Boolean {
        return context.packageManager.hasSystemFeature(
            PackageManager.FEATURE_VULKAN_HARDWARE_VERSION,
            0x00400000 // Vulkan 1.0
        )
    }

    private fun isOpenGLES31Supported(): Boolean {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        return activityManager.deviceConfigurationInfo.reqGlEsVersion >= 0x00030001
    }

    fun cleanup() {
        processor.cleanup()
    }
}

interface ImageProcessor {
    fun blur(input: Bitmap, radius: Float): Bitmap
    fun convolve(input: Bitmap, kernel: FloatArray): Bitmap
    fun cleanup()
}
```

#### 3. OpenGL ES Compute Shaders

**OpenGL ES 3.1 Compute Implementation:**
```kotlin
class OpenGLES31ComputeProcessor(private val context: Context) : ImageProcessor {

    private var computeProgram = 0
    private val eglHelper = EGLHelper()

    init {
        eglHelper.initialize()
        setupComputeShader()
    }

    private fun setupComputeShader() {
        val computeShaderCode = """
            #version 310 es

            layout (local_size_x = 16, local_size_y = 16) in;

            layout (binding = 0, rgba8) uniform readonly highp image2D inputImage;
            layout (binding = 1, rgba8) uniform writeonly highp image2D outputImage;

            uniform float radius;

            void main() {
                ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
                ivec2 size = imageSize(inputImage);

                if (pos.x >= size.x || pos.y >= size.y) {
                    return;
                }

                // Box blur implementation
                vec4 color = vec4(0.0);
                int r = int(radius);
                int count = 0;

                for (int y = -r; y <= r; y++) {
                    for (int x = -r; x <= r; x++) {
                        ivec2 samplePos = clamp(
                            pos + ivec2(x, y),
                            ivec2(0),
                            size - ivec2(1)
                        );
                        color += imageLoad(inputImage, samplePos);
                        count++;
                    }
                }

                color /= float(count);
                imageStore(outputImage, pos, color);
            }
        """.trimIndent()

        computeProgram = createComputeProgram(computeShaderCode)
    }

    private fun createComputeProgram(shaderCode: String): Int {
        val shader = GLES31.glCreateShader(GLES31.GL_COMPUTE_SHADER)
        GLES31.glShaderSource(shader, shaderCode)
        GLES31.glCompileShader(shader)

        // Check compilation status
        val status = IntArray(1)
        GLES31.glGetShaderiv(shader, GLES31.GL_COMPILE_STATUS, status, 0)
        if (status[0] == GLES31.GL_FALSE) {
            val log = GLES31.glGetShaderInfoLog(shader)
            throw RuntimeException("Shader compilation failed: $log")
        }

        val program = GLES31.glCreateProgram()
        GLES31.glAttachShader(program, shader)
        GLES31.glLinkProgram(program)

        // Check link status
        GLES31.glGetProgramiv(program, GLES31.GL_LINK_STATUS, status, 0)
        if (status[0] == GLES31.GL_FALSE) {
            val log = GLES31.glGetProgramInfoLog(program)
            throw RuntimeException("Program linking failed: $log")
        }

        GLES31.glDeleteShader(shader)
        return program
    }

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(
            input.width,
            input.height,
            Bitmap.Config.ARGB_8888
        )

        // Create textures
        val textures = IntArray(2)
        GLES31.glGenTextures(2, textures, 0)

        // Upload input texture
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[0])
        GLUtils.texImage2D(GLES31.GL_TEXTURE_2D, 0, input, 0)
        GLES31.glBindImageTexture(
            0,
            textures[0],
            0,
            false,
            0,
            GLES31.GL_READ_ONLY,
            GLES31.GL_RGBA8
        )

        // Setup output texture
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[1])
        GLES31.glTexImage2D(
            GLES31.GL_TEXTURE_2D,
            0,
            GLES31.GL_RGBA8,
            input.width,
            input.height,
            0,
            GLES31.GL_RGBA,
            GLES31.GL_UNSIGNED_BYTE,
            null
        )
        GLES31.glBindImageTexture(
            1,
            textures[1],
            0,
            false,
            0,
            GLES31.GL_WRITE_ONLY,
            GLES31.GL_RGBA8
        )

        // Use compute shader
        GLES31.glUseProgram(computeProgram)
        val radiusLocation = GLES31.glGetUniformLocation(computeProgram, "radius")
        GLES31.glUniform1f(radiusLocation, radius)

        // Dispatch compute
        val workGroupSize = 16
        val groupsX = (input.width + workGroupSize - 1) / workGroupSize
        val groupsY = (input.height + workGroupSize - 1) / workGroupSize
        GLES31.glDispatchCompute(groupsX, groupsY, 1)

        // Wait for completion
        GLES31.glMemoryBarrier(GLES31.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        // Read result
        GLES31.glBindTexture(GLES31.GL_TEXTURE_2D, textures[1])
        val buffer = ByteBuffer.allocateDirect(input.width * input.height * 4)
        GLES31.glGetTexImage(
            GLES31.GL_TEXTURE_2D,
            0,
            GLES31.GL_RGBA,
            GLES31.GL_UNSIGNED_BYTE,
            buffer
        )

        output.copyPixelsFromBuffer(buffer)

        // Cleanup
        GLES31.glDeleteTextures(2, textures, 0)

        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        // Similar implementation with convolution kernel
        return input
    }

    override fun cleanup() {
        if (computeProgram != 0) {
            GLES31.glDeleteProgram(computeProgram)
        }
        eglHelper.cleanup()
    }
}

class EGLHelper {
    private var eglDisplay: EGLDisplay? = null
    private var eglContext: EGLContext? = null
    private var eglSurface: EGLSurface? = null

    fun initialize() {
        eglDisplay = EGL14.eglGetDisplay(EGL14.EGL_DEFAULT_DISPLAY)
        val version = IntArray(2)
        EGL14.eglInitialize(eglDisplay, version, 0, version, 1)

        val configAttribs = intArrayOf(
            EGL14.EGL_RENDERABLE_TYPE, EGLExt.EGL_OPENGL_ES3_BIT_KHR,
            EGL14.EGL_RED_SIZE, 8,
            EGL14.EGL_GREEN_SIZE, 8,
            EGL14.EGL_BLUE_SIZE, 8,
            EGL14.EGL_ALPHA_SIZE, 8,
            EGL14.EGL_NONE
        )

        val configs = arrayOfNulls<EGLConfig>(1)
        val numConfigs = IntArray(1)
        EGL14.eglChooseConfig(
            eglDisplay,
            configAttribs, 0,
            configs, 0, 1,
            numConfigs, 0
        )

        val contextAttribs = intArrayOf(
            EGL14.EGL_CONTEXT_CLIENT_VERSION, 3,
            EGL14.EGL_NONE
        )

        eglContext = EGL14.eglCreateContext(
            eglDisplay,
            configs[0],
            EGL14.EGL_NO_CONTEXT,
            contextAttribs, 0
        )

        val surfaceAttribs = intArrayOf(
            EGL14.EGL_WIDTH, 1,
            EGL14.EGL_HEIGHT, 1,
            EGL14.EGL_NONE
        )

        eglSurface = EGL14.eglCreatePbufferSurface(
            eglDisplay,
            configs[0],
            surfaceAttribs, 0
        )

        EGL14.eglMakeCurrent(eglDisplay, eglSurface, eglSurface, eglContext)
    }

    fun cleanup() {
        EGL14.eglMakeCurrent(
            eglDisplay,
            EGL14.EGL_NO_SURFACE,
            EGL14.EGL_NO_SURFACE,
            EGL14.EGL_NO_CONTEXT
        )
        eglSurface?.let { EGL14.eglDestroySurface(eglDisplay, it) }
        eglContext?.let { EGL14.eglDestroyContext(eglDisplay, it) }
        eglDisplay?.let { EGL14.eglTerminate(it) }
    }
}
```

#### 4. CPU Fallback Implementation

**Software Image Processing:**
```kotlin
class CPUImageProcessor : ImageProcessor {

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val output = input.copy(input.config, true)
        val pixels = IntArray(input.width * input.height)
        input.getPixels(pixels, 0, input.width, 0, 0, input.width, input.height)

        val r = radius.toInt()

        for (y in 0 until input.height) {
            for (x in 0 until input.width) {
                var red = 0
                var green = 0
                var blue = 0
                var alpha = 0
                var count = 0

                for (ky in -r..r) {
                    for (kx in -r..r) {
                        val px = (x + kx).coerceIn(0, input.width - 1)
                        val py = (y + ky).coerceIn(0, input.height - 1)
                        val pixel = pixels[py * input.width + px]

                        alpha += Color.alpha(pixel)
                        red += Color.red(pixel)
                        green += Color.green(pixel)
                        blue += Color.blue(pixel)
                        count++
                    }
                }

                pixels[y * input.width + x] = Color.argb(
                    alpha / count,
                    red / count,
                    green / count,
                    blue / count
                )
            }
        }

        output.setPixels(pixels, 0, input.width, 0, 0, input.width, input.height)
        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        require(kernel.size == 9) { "Only 3x3 kernels supported" }

        val output = input.copy(input.config, true)
        val pixels = IntArray(input.width * input.height)
        input.getPixels(pixels, 0, input.width, 0, 0, input.width, input.height)

        for (y in 1 until input.height - 1) {
            for (x in 1 until input.width - 1) {
                var red = 0f
                var green = 0f
                var blue = 0f

                var ki = 0
                for (ky in -1..1) {
                    for (kx in -1..1) {
                        val pixel = pixels[(y + ky) * input.width + (x + kx)]
                        val k = kernel[ki++]

                        red += Color.red(pixel) * k
                        green += Color.green(pixel) * k
                        blue += Color.blue(pixel) * k
                    }
                }

                pixels[y * input.width + x] = Color.rgb(
                    red.toInt().coerceIn(0, 255),
                    green.toInt().coerceIn(0, 255),
                    blue.toInt().coerceIn(0, 255)
                )
            }
        }

        output.setPixels(pixels, 0, input.width, 0, 0, input.width, input.height)
        return output
    }

    override fun cleanup() {
        // Nothing to cleanup for CPU implementation
    }
}
```

#### 5. Platform-Specific GPU Libraries

**Using Android NDK and GPU libraries:**
```kotlin
class NativeGPUProcessor(context: Context) {

    init {
        System.loadLibrary("native-gpu-processor")
    }

    /**
     * Process image using native GPU code
     */
    fun processImage(input: Bitmap): Bitmap {
        val width = input.width
        val height = input.height
        val pixels = IntArray(width * height)
        input.getPixels(pixels, 0, width, 0, 0, width, height)

        // Call native method
        nativeProcessImage(pixels, width, height)

        val output = Bitmap.createBitmap(width, height, input.config)
        output.setPixels(pixels, 0, width, 0, 0, width, height)

        return output
    }

    private external fun nativeProcessImage(pixels: IntArray, width: Int, height: Int)
}
```

**Native C++ GPU Processing (NDK):**
```cpp
// native-gpu-processor.cpp

#include <jni.h>
#include <android/log.h>
#include <GLES3/gl31.h>
#include <EGL/egl.h>

#define LOG_TAG "GPUProcessor"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)

extern "C" JNIEXPORT void JNICALL
Java_com_example_NativeGPUProcessor_nativeProcessImage(
    JNIEnv* env,
    jobject /* this */,
    jintArray pixels,
    jint width,
    jint height
) {
    jint* pixelData = env->GetIntArrayElements(pixels, nullptr);

    // Initialize EGL and OpenGL ES context
    // Create compute shader
    // Upload texture
    // Dispatch compute
    // Read back results

    // Process image using GPU...

    env->ReleaseIntArrayElements(pixels, pixelData, 0);
}
```

### Best Practices

1. **Choose Right API:**
   - Vulkan: Maximum control, lowest overhead, most complex
   - OpenGL ES 3.1+: Compute shaders, easier than Vulkan
   - CPU fallback: Compatibility for older devices

2. **RenderScript Migration:**
   - Evaluate device capabilities at runtime
   - Provide CPU fallback for older devices
   - Consider platform-specific optimizations

3. **Performance:**
   - Use appropriate work group sizes (typically 8x8 or 16x16)
   - Minimize CPU-GPU transfers
   - Batch operations when possible
   - Profile on target devices

4. **Memory Management:**
   - Release GPU resources properly
   - Use texture/buffer pooling
   - Monitor memory usage

5. **Shader Optimization:**
   - Minimize divergent branches
   - Use appropriate precision (mediump vs highp)
   - Optimize memory access patterns
   - Leverage shared memory when possible

### Common Pitfalls

1. **Not checking device capabilities** → Crashes on unsupported devices
   - Always check Vulkan/OpenGL ES version

2. **Synchronization issues** → Race conditions
   - Use proper barriers and fences

3. **Not cleaning up resources** → Memory leaks
   - Release all GPU resources in cleanup()

4. **CPU-GPU transfer overhead** → Poor performance
   - Minimize transfers, keep data on GPU

5. **Incorrect work group sizes** → Inefficient execution
   - Match hardware capabilities

6. **No fallback implementation** → App unusable on older devices
   - Always provide CPU fallback

### Summary

With RenderScript deprecated, Vulkan and OpenGL ES compute shaders are modern alternatives for GPU computing on Android. Vulkan provides maximum control but with complexity, while OpenGL ES 3.1+ offers compute capabilities with easier integration. Always implement CPU fallbacks for compatibility and choose the appropriate API based on device capabilities and performance requirements.

---



## Ответ (RU)
# Вопрос (RU)
Как использовать Vulkan для низкоуровневых GPU операций в Android? Какие существуют альтернативы устаревшему RenderScript? Как реализовать вычислительные шейдеры и GPU-ускоренную обработку изображений?

## Ответ (RU)
С устареванием RenderScript в Android 12, разработчикам нужны альтернативные подходы для GPU вычислений. Vulkan предоставляет низкоуровневый доступ к GPU, в то время как другие опции включают GPU Compute шейдеры, OpenGL ES compute и платформо-специфичные решения.

#### Альтернативы RenderScript

**1. Vulkan:**
- Максимальный контроль над GPU
- Минимальные накладные расходы
- Сложная настройка и использование
- Требует Vulkan 1.0+ (Android 7.0+)

**2. OpenGL ES 3.1+ Compute Shaders:**
- Вычислительные шейдеры
- Проще чем Vulkan
- Хорошая производительность
- Требует OpenGL ES 3.1+ (Android 5.0+)

**3. CPU Fallback:**
- Для совместимости со старыми устройствами
- Программная реализация
- Медленнее, но универсально

**4. Платформо-специфичные решения:**
- Android NDK с GPU библиотеками
- Vendor-specific APIs (Mali, Adreno)

#### Основные Концепции Vulkan

**Vulkan Pipeline:**
1. Instance → Physical Device → Logical Device
2. Command Pool → Command Buffers
3. Pipeline (Shaders, Layout)
4. Descriptor Sets (Resources)
5. Submit & Execute

**Compute Shader Workflow:**
1. Create compute pipeline
2. Allocate descriptor sets (input/output images)
3. Record commands (dispatch)
4. Submit to queue
5. Wait for completion
6. Read results

#### OpenGL ES Compute Shaders

**Преимущества:**
- Проще интеграция чем Vulkan
- Меньше boilerplate кода
- Хорошая документация

**Ограничения:**
- Менее эффективно чем Vulkan
- Меньше контроля

### Лучшие Практики

1. **Выбор API:** Проверяйте возможности устройства
2. **Миграция RenderScript:** Постепенный переход с fallback
3. **Производительность:** Оптимизируйте размер work group
4. **Память:** Правильно освобождайте GPU ресурсы
5. **Шейдеры:** Минимизируйте ветвления, оптимизируйте доступ к памяти

### Распространённые Ошибки

1. Не проверять возможности устройства → краши
2. Проблемы синхронизации → гонки данных
3. Не очищать ресурсы → утечки памяти
4. Накладные расходы CPU-GPU → низкая производительность
5. Неправильные размеры work group → неэффективность
6. Нет fallback → неработоспособность на старых устройствах

### Резюме

С устареванием RenderScript, Vulkan и OpenGL ES compute шейдеры являются современными альтернативами для GPU вычислений на Android. Vulkan обеспечивает максимальный контроль но со сложностью, в то время как OpenGL ES 3.1+ предлагает вычислительные возможности с более простой интеграцией. Всегда реализуйте CPU fallback для совместимости и выбирайте подходящий API на основе возможностей устройства и требований производительности.


## Follow-ups

- [[c-gpu-rendering]]
- [[c-performance]]
- [[q-surfaceview-rendering--android--medium]]


## References

- [Rendering Performance](https://developer.android.com/topic/performance/rendering)


## Related Questions

- [[q-dagger-field-injection--android--medium]]
- [[q-accessibility-compose--android--medium]]
- [[q-compose-compiler-plugin--android--hard]]
