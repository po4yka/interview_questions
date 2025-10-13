---
topic: android
tags:
  - android
  - android/memory-management
  - heap-dump
  - leakcanary
  - memory-analysis
  - memory-management
  - shark
difficulty: medium
status: draft
date_created: 2025-10-13
date_updated: 2025-10-13
moc: moc-android
related_questions: []
---

# Как понять что в дампе есть утечка?

**English**: How to find a leak in a heap dump?

## Answer (EN)
If an object was not freed after attempts to trigger garbage collection, LeakCanary creates a **heap dump**. LeakCanary uses the **Shark library** to analyze the heap dump.

**Process:**

**1. Heap Dump Creation**

```kotlin
// When leak suspected
if (weakReference.get() != null) {
    // Object not collected - create heap dump
    val heapDumpFile = File(heapDumpsDir, "leak-${UUID.randomUUID()}.hprof")
    Debug.dumpHprofData(heapDumpFile.absolutePath)

    // Analyze heap dump
    analyzeHeap(heapDumpFile)
}
```

**2. Shark Library Analysis**

Checks all objects in the heap and their references.

```kotlin
import shark.AndroidObjectInspectors
import shark.HeapAnalyzer
import shark.OnAnalysisProgressListener

// Analyze heap dump with Shark
fun analyzeHeap(heapDumpFile: File) {
    val heapAnalyzer = HeapAnalyzer(
        OnAnalysisProgressListener.NO_OP
    )

    val analysis = heapAnalyzer.analyze(
        heapDumpFile = heapDumpFile,
        leakingObjectFinder = FilteringLeakingObjectFinder(
            AndroidObjectInspectors.appLeakingObjectFilters
        ),
        referenceMatchers = AndroidReferenceMatchers.appDefaults,
        computeRetainedHeapSize = true,
        objectInspectors = AndroidObjectInspectors.appDefaults,
        metadataExtractor = AndroidMetadataExtractor
    )

    when (analysis) {
        is HeapAnalysisSuccess -> {
            analysis.applicationLeaks.forEach { leak ->
                println("Leak found: ${leak.leakTraces.first()}")
            }
        }
        is HeapAnalysisFailure -> {
            println("Analysis failed: ${analysis.exception}")
        }
    }
}
```

**3. Reference Chain Verification**

Shark checks which references hold the object in memory.

**If an object should have been collected but is held by a reference chain, this indicates a leak.**

**4. Retention Chain Display**

The retention chain shows which objects and references prevent garbage collector from freeing memory.

**Example Leak Trace:**

```

 LEAK FOUND                                     

                                                
 GC Root: Local variable in thread             
     ↓                                          
 MyApplication (instance)                       
     ↓ static MyApplication.sInstance           
 MainActivity (instance)                        
     ↓ leaking                                  
                                                
 Leak: MainActivity leaked!                     
 Retained: 2.5 MB                               

```

**Leak Detection Logic:**

```kotlin
// Simplified Shark leak finding
fun findLeaks(heapGraph: HeapGraph): List<Leak> {
    val leaks = mutableListOf<Leak>()

    // Find objects that should be collected
    val leakingObjects = heapGraph.objects
        .filter { obj ->
            // Check if object is a known leaked type
            obj.instanceClassName == "android.app.Activity" &&
            obj.instance["mDestroyed"]?.value == true
        }

    leakingObjects.forEach { leakingObject ->
        // Find path from GC root to leaked object
        val path = heapGraph.findPathFromGcRoot(leakingObject)

        if (path != null) {
            // Leak found! Object held by reference chain
            leaks.add(Leak(
                leakingObject = leakingObject,
                retentionChain = path,
                retainedBytes = calculateRetainedSize(leakingObject)
            ))
        }
    }

    return leaks
}
```

**Leak Example:**

```kotlin
class MainActivity : AppCompatActivity() {
    private val handler = Handler()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // - Delayed runnable holds Activity reference
        handler.postDelayed({
            // This holds MainActivity even after destruction
            updateUI()
        }, 60000)  // 60 seconds
    }
}
```

**Shark finds:**

```
GC Root: Thread (main)
  ↓ HandlerThread.mQueue
  ↓ MessageQueue.mMessages
  ↓ Message.callback (Runnable)
  ↓ Lambda holding MainActivity reference
  ↓ MainActivity (LEAKED!)

Retained size: 3.2 MB
```

**Retention Chain Components:**

| Element | Description |
|---------|-------------|
| **GC Root** | Starting point (Thread, static field, etc.) |
| **Reference Chain** | Path of references from root to leaked object |
| **Leaked Object** | Object that should be collected but isn't |
| **Retained Size** | Memory held by leaked object and its references |

**Common Leak Patterns Detected:**

**1. Static Reference Leak:**
```kotlin
companion object {
    var activity: Activity? = null  // BAD
}
```

**Trace:**
```
GC Root: Class object
  ↓ static companion.activity
  ↓ MainActivity (LEAKED)
```

**2. Inner Class Leak:**
```kotlin
class MyActivity : AppCompatActivity() {
    inner class MyTask : AsyncTask<Void, Void, Void>() {
        // - Holds implicit reference to MyActivity
    }
}
```

**Trace:**
```
GC Root: Thread
  ↓ MyTask.this$0 (implicit outer class reference)
  ↓ MyActivity (LEAKED)
```

**3. Listener Leak:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // - Anonymous class holds Activity reference
    someService.addListener(object : Listener {
        override fun onEvent() {
            updateUI()
        }
    })
}
```

**LeakCanary Report Example:**

```

HEAP ANALYSIS RESULT


1 APPLICATION LEAKS

Leak pattern: Activity retained by static field

* GC ROOT static MyApp.sInstance
* MyApp
  ↓ MyApp.currentActivity
  ↓ MainActivity (leaked)

Retained: 5.4 MB

Leak trace:
  MyApp.currentActivity is holding MainActivity
  Fix: Set MyApp.currentActivity = null in onDestroy()

```

**Summary:**

1. **Object not collected** after GC → Create heap dump
2. **Shark library** analyzes heap dump
3. **Checks all objects** and their references in heap
4. **Finds retention chains** from GC roots to leaked objects
5. **Reports leak** with reference chain and retained size

## Ответ (RU)
Если объект не был освобожден после попыток вызвать сборку мусора, LeakCanary создает **дамп памяти**.

LeakCanary использует библиотеку **Shark** для анализа дампа памяти. Он проверяет все объекты в куче и их ссылки.

Shark проверяет какие ссылки удерживают объект в памяти. Если объект должен был быть собран но удерживается цепочкой ссылок это указывает на утечку.

Цепочка удержания показывает какие объекты и ссылки не позволяют сборщику мусора освободить память.


---

## Related Questions

### Kotlin Language Features
- [[q-heap-pollution-generics--kotlin--hard]] - Data Structures
- [[q-kotlin-collections--kotlin--medium]] - Data Structures
- [[q-kotlin-native--kotlin--hard]] - Memory Management
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Memory Management

### Related Algorithms
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Data Structures
- [[q-advanced-graph-algorithms--algorithms--hard]] - Data Structures
- [[q-binary-search-trees-bst--algorithms--hard]] - Data Structures
