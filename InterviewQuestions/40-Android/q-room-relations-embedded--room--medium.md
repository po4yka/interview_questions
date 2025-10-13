---
topic: room
tags:
  - room
  - database
  - relations
  - embedded
  - modeling
  - junction-table
  - difficulty/medium
difficulty: medium
status: draft
---

# Room Relations and Embedded / Отношения и Embedded в Room

**English**: Implement @Relation for one-to-many and many-to-many relationships. Use @Embedded for flattening data classes.

## Answer (EN)
**Room Relations** allow you to model relationships between entities without storing nested objects directly. Room provides the `@Relation` annotation for querying related entities and `@Embedded` for embedding objects into a single table.

### Understanding Room Relations

Room supports three types of relationships:
1. **One-to-One**: A single entity relates to another single entity
2. **One-to-Many**: A single entity relates to multiple entities
3. **Many-to-Many**: Multiple entities relate to multiple entities (requires junction table)

### @Embedded Annotation

`@Embedded` allows you to flatten an object's fields into a single table, avoiding the need for separate tables or JSON serialization.

#### Basic @Embedded Example

```kotlin
// Address is NOT an entity, just a data class
data class Address(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)

// User entity with embedded address
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val name: String,
    val email: String,

    @Embedded
    val address: Address  // Fields will be flattened into users table
)

// Generated SQL:
// CREATE TABLE users (
//     userId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
//     name TEXT NOT NULL,
//     email TEXT NOT NULL,
//     street TEXT NOT NULL,
//     city TEXT NOT NULL,
//     state TEXT NOT NULL,
//     zipCode TEXT NOT NULL,
//     country TEXT NOT NULL
// )
```

#### @Embedded with Prefix

When you have multiple embedded objects of the same type, use `prefix` to avoid column name conflicts:

```kotlin
data class Coordinates(
    val latitude: Double,
    val longitude: Double
)

@Entity(tableName = "stores")
data class Store(
    @PrimaryKey(autoGenerate = true)
    val storeId: Long = 0,
    val name: String,

    @Embedded(prefix = "pickup_")
    val pickupLocation: Coordinates,

    @Embedded(prefix = "delivery_")
    val deliveryLocation: Coordinates
)

// Generated columns:
// pickup_latitude, pickup_longitude
// delivery_latitude, delivery_longitude
```

### One-to-Many Relationship

The most common relationship type where one entity relates to multiple entities.

#### Entities Definition

```kotlin
// Parent entity
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val name: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
)

// Child entity with foreign key
@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE,  // Delete posts when user is deleted
            onUpdate = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["authorId"])]  // Important for query performance
)
data class Post(
    @PrimaryKey(autoGenerate = true)
    val postId: Long = 0,
    val authorId: Long,  // Foreign key to users.userId
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis()
)
```

#### Relation Container

```kotlin
// Container class to hold user with their posts
data class UserWithPosts(
    @Embedded
    val user: User,

    @Relation(
        parentColumn = "userId",    // Column in parent (User)
        entityColumn = "authorId"   // Column in child (Post)
    )
    val posts: List<Post>
)
```

#### DAO Queries

```kotlin
@Dao
interface UserDao {
    // Insert operations
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPost(post: Post): Long

    // Get user with all their posts
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?

    // Get all users with their posts
    @Transaction
    @Query("SELECT * FROM users")
    suspend fun getAllUsersWithPosts(): List<UserWithPosts>

    // Get users who have posted in last 30 days
    @Transaction
    @Query("""
        SELECT DISTINCT users.* FROM users
        INNER JOIN posts ON users.userId = posts.authorId
        WHERE posts.createdAt > :since
    """)
    suspend fun getActiveUsersWithPosts(since: Long): List<UserWithPosts>

    // Get user with posts filtered by keyword
    @Transaction
    @Query("""
        SELECT * FROM users
        WHERE userId IN (
            SELECT DISTINCT authorId FROM posts
            WHERE title LIKE '%' || :keyword || '%'
            OR content LIKE '%' || :keyword || '%'
        )
    """)
    suspend fun searchUsersWithPosts(keyword: String): List<UserWithPosts>
}
```

### Many-to-Many Relationship

Many-to-many relationships require a **junction table** (also called cross-reference table) to store the associations.

#### Example: Students and Courses

```kotlin
// First entity
@Entity(tableName = "students")
data class Student(
    @PrimaryKey(autoGenerate = true)
    val studentId: Long = 0,
    val name: String,
    val email: String,
    val enrollmentYear: Int
)

// Second entity
@Entity(tableName = "courses")
data class Course(
    @PrimaryKey(autoGenerate = true)
    val courseId: Long = 0,
    val code: String,
    val name: String,
    val credits: Int,
    val semester: String
)

// Junction table (cross-reference entity)
@Entity(
    tableName = "student_course_cross_ref",
    primaryKeys = ["studentId", "courseId"],  // Composite primary key
    foreignKeys = [
        ForeignKey(
            entity = Student::class,
            parentColumns = ["studentId"],
            childColumns = ["studentId"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = Course::class,
            parentColumns = ["courseId"],
            childColumns = ["courseId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["studentId"]),
        Index(value = ["courseId"])
    ]
)
data class StudentCourseCrossRef(
    val studentId: Long,
    val courseId: Long,
    val enrolledAt: Long = System.currentTimeMillis(),
    val grade: String? = null  // Additional data in junction table
)
```

#### Relation Containers

```kotlin
// Student with their courses
data class StudentWithCourses(
    @Embedded
    val student: Student,

    @Relation(
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val courses: List<Course>
)

// Course with enrolled students
data class CourseWithStudents(
    @Embedded
    val course: Course,

    @Relation(
        parentColumn = "courseId",
        entityColumn = "studentId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val students: List<Student>
)

// Complete enrollment data with junction info
data class EnrollmentDetails(
    @Embedded
    val student: Student,

    @Relation(
        entity = Course::class,
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(
            value = StudentCourseCrossRef::class,
            parentColumn = "studentId",
            entityColumn = "courseId"
        )
    )
    val coursesWithGrades: List<CourseWithGrade>
)

data class CourseWithGrade(
    @Embedded
    val course: Course,

    @Relation(
        parentColumn = "courseId",
        entityColumn = "courseId"
    )
    val crossRef: StudentCourseCrossRef
)
```

#### DAO for Many-to-Many

```kotlin
@Dao
interface StudentCourseDao {
    // Insert operations
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStudent(student: Student): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCourse(course: Course): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enrollStudentInCourse(crossRef: StudentCourseCrossRef)

    @Delete
    suspend fun unenrollStudentFromCourse(crossRef: StudentCourseCrossRef)

    // Query student's courses
    @Transaction
    @Query("SELECT * FROM students WHERE studentId = :studentId")
    suspend fun getStudentWithCourses(studentId: Long): StudentWithCourses?

    @Transaction
    @Query("SELECT * FROM students")
    suspend fun getAllStudentsWithCourses(): List<StudentWithCourses>

    // Query course's students
    @Transaction
    @Query("SELECT * FROM courses WHERE courseId = :courseId")
    suspend fun getCourseWithStudents(courseId: Long): CourseWithStudents?

    @Transaction
    @Query("SELECT * FROM courses")
    suspend fun getAllCoursesWithStudents(): List<CourseWithStudents>

    // Complex queries
    @Transaction
    @Query("""
        SELECT * FROM students
        WHERE studentId IN (
            SELECT studentId FROM student_course_cross_ref
            WHERE courseId = :courseId AND grade IS NOT NULL
        )
    """)
    suspend fun getStudentsWithGradesForCourse(courseId: Long): List<StudentWithCourses>

    @Transaction
    @Query("""
        SELECT * FROM courses
        WHERE courseId IN (
            SELECT courseId FROM student_course_cross_ref
            WHERE studentId = :studentId
        )
        AND semester = :semester
    """)
    suspend fun getStudentCoursesForSemester(
        studentId: Long,
        semester: String
    ): List<Course>

    // Update grade
    @Query("""
        UPDATE student_course_cross_ref
        SET grade = :grade
        WHERE studentId = :studentId AND courseId = :courseId
    """)
    suspend fun updateGrade(studentId: Long, courseId: Long, grade: String)

    // Check if student is enrolled
    @Query("""
        SELECT EXISTS(
            SELECT 1 FROM student_course_cross_ref
            WHERE studentId = :studentId AND courseId = :courseId
        )
    """)
    suspend fun isStudentEnrolled(studentId: Long, courseId: Long): Boolean

    // Get enrollment count
    @Query("SELECT COUNT(*) FROM student_course_cross_ref WHERE courseId = :courseId")
    suspend fun getCourseEnrollmentCount(courseId: Long): Int
}
```

### Advanced: Nested Relations

You can nest relations to model complex hierarchies.

```kotlin
// Comment entity
@Entity(
    tableName = "comments",
    foreignKeys = [
        ForeignKey(
            entity = Post::class,
            parentColumns = ["postId"],
            childColumns = ["postId"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("postId"), Index("authorId")]
)
data class Comment(
    @PrimaryKey(autoGenerate = true)
    val commentId: Long = 0,
    val postId: Long,
    val authorId: Long,
    val text: String,
    val createdAt: Long = System.currentTimeMillis()
)

// Post with comments
data class PostWithComments(
    @Embedded
    val post: Post,

    @Relation(
        parentColumn = "postId",
        entityColumn = "postId"
    )
    val comments: List<Comment>
)

// User with posts and comments
data class UserWithPostsAndComments(
    @Embedded
    val user: User,

    @Relation(
        entity = Post::class,
        parentColumn = "userId",
        entityColumn = "authorId"
    )
    val posts: List<PostWithComments>
)

@Dao
interface ComplexDao {
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPostsAndComments(userId: Long): UserWithPostsAndComments?
}
```

### Complete Working Example

```kotlin
// Database setup
@Database(
    entities = [
        User::class,
        Post::class,
        Comment::class,
        Student::class,
        Course::class,
        StudentCourseCrossRef::class
    ],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun studentCourseDao(): StudentCourseDao
    abstract fun complexDao(): ComplexDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                    .fallbackToDestructiveMigration()
                    .build()

                INSTANCE = instance
                instance
            }
        }
    }
}

// Repository usage
class UserRepository(private val userDao: UserDao) {

    suspend fun createUserWithPosts(userName: String, postTitles: List<String>) {
        val userId = userDao.insertUser(
            User(name = userName, email = "$userName@example.com")
        )

        postTitles.forEach { title ->
            userDao.insertPost(
                Post(authorId = userId, title = title, content = "Content for $title")
            )
        }
    }

    suspend fun getUserWithPosts(userId: Long): UserWithPosts? {
        return userDao.getUserWithPosts(userId)
    }

    fun getAllUsersWithPostsFlow(): Flow<List<UserWithPosts>> {
        return flow {
            emit(userDao.getAllUsersWithPosts())
        }
    }
}

class StudentCourseRepository(private val dao: StudentCourseDao) {

    suspend fun enrollStudent(studentId: Long, courseId: Long) {
        dao.enrollStudentInCourse(
            StudentCourseCrossRef(studentId = studentId, courseId = courseId)
        )
    }

    suspend fun unenrollStudent(studentId: Long, courseId: Long) {
        dao.unenrollStudentFromCourse(
            StudentCourseCrossRef(studentId = studentId, courseId = courseId)
        )
    }

    suspend fun assignGrade(studentId: Long, courseId: Long, grade: String) {
        dao.updateGrade(studentId, courseId, grade)
    }

    suspend fun getStudentSchedule(studentId: Long, semester: String): List<Course> {
        return dao.getStudentCoursesForSemester(studentId, semester)
    }
}
```

### Usage in ViewModel

```kotlin
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    fun getUserWithPosts(userId: Long): LiveData<UserWithPosts?> = liveData {
        emit(repository.getUserWithPosts(userId))
    }

    fun getAllUsersWithPosts(): LiveData<List<UserWithPosts>> = liveData {
        repository.getAllUsersWithPostsFlow().collect {
            emit(it)
        }
    }
}

class StudentCourseViewModel(
    private val repository: StudentCourseRepository
) : ViewModel() {

    private val _enrollmentStatus = MutableLiveData<Result<Unit>>()
    val enrollmentStatus: LiveData<Result<Unit>> = _enrollmentStatus

    fun enrollStudentInCourse(studentId: Long, courseId: Long) {
        viewModelScope.launch {
            try {
                repository.enrollStudent(studentId, courseId)
                _enrollmentStatus.value = Result.success(Unit)
            } catch (e: Exception) {
                _enrollmentStatus.value = Result.failure(e)
            }
        }
    }

    fun assignGrade(studentId: Long, courseId: Long, grade: String) {
        viewModelScope.launch {
            repository.assignGrade(studentId, courseId, grade)
        }
    }
}
```

### Performance Considerations

#### Use @Transaction

Always use `@Transaction` annotation when querying relations to ensure:
- Consistency: All related data is fetched atomically
- Performance: Room optimizes multiple queries

```kotlin
@Dao
interface UserDao {
    // GOOD: Uses @Transaction
    @Transaction
    @Query("SELECT * FROM users")
    suspend fun getAllUsersWithPosts(): List<UserWithPosts>

    // BAD: No @Transaction, might have inconsistent data
    @Query("SELECT * FROM users")
    suspend fun getAllUsersWithPostsUnsafe(): List<UserWithPosts>
}
```

#### Lazy Loading

For large datasets, consider loading relations on demand:

```kotlin
@Dao
interface UserDao {
    // Load users without posts (lightweight)
    @Query("SELECT * FROM users")
    suspend fun getAllUsers(): List<User>

    // Load specific user's posts when needed
    @Query("SELECT * FROM posts WHERE authorId = :userId")
    suspend fun getPostsForUser(userId: Long): List<Post>
}
```

#### Pagination

For relations with many children, use Paging 3:

```kotlin
@Dao
interface PostDao {
    @Query("SELECT * FROM posts WHERE authorId = :userId ORDER BY createdAt DESC")
    fun getPostsForUserPaged(userId: Long): PagingSource<Int, Post>
}
```

### Best Practices

1. **Use Foreign Keys**: Enforce referential integrity at database level
2. **Add Indices**: Index foreign key columns for query performance
3. **Use @Transaction**: Ensure consistency when loading relations
4. **Cascade Operations**: Use `onDelete = CASCADE` for parent-child relationships
5. **Avoid Deep Nesting**: Limit relation depth to 2-3 levels for performance
6. **Consider Lazy Loading**: Don't always load all relations upfront
7. **Use Junction Tables**: For many-to-many, always use a proper junction entity
8. **Prefix Embedded Objects**: Avoid column name conflicts with prefix parameter
9. **Document Relationships**: Comment why relationships exist and their cardinality
10. **Test Cascading Deletes**: Ensure data integrity when deleting parent entities

### Common Pitfalls

1. **Missing @Transaction**: Inconsistent data when loading relations
2. **No Indices on Foreign Keys**: Poor query performance
3. **Circular References**: Avoid infinite loops in nested relations
4. **N+1 Query Problem**: Room handles this, but be aware in custom queries
5. **Not Using ForeignKey Constraints**: Data integrity issues
6. **Too Many Nested Relations**: Performance degradation
7. **Ignoring Cascade Behavior**: Orphaned records or unintended deletions
8. **Column Name Conflicts**: When embedding multiple objects of same type

### Comparison Table: @Embedded vs @Relation

| Feature | @Embedded | @Relation |
|---------|-----------|-----------|
| Purpose | Flatten object into single table | Link separate entities |
| Tables | Single table | Multiple tables |
| Foreign Keys | Not needed | Required |
| Query Complexity | Simple (single table) | Complex (JOINs) |
| Performance | Fast (no JOINs) | Slower (requires JOINs) |
| Data Duplication | Possible | Minimal |
| Normalization | Denormalized | Normalized |
| Use Case | Address, Coordinates | One-to-many, Many-to-many |
| Transactional | No | Yes (@Transaction) |

### Summary

Room Relations provide powerful ways to model relationships:

- **@Embedded**: Flatten objects into single table (composition)
- **@Relation**: Link separate entities (association)
- **One-to-Many**: Parent entity → multiple children
- **Many-to-Many**: Junction table to link entities
- **Foreign Keys**: Enforce referential integrity
- **@Transaction**: Ensure atomic operations
- **Indices**: Optimize query performance
- **Cascade**: Control delete/update behavior

Always consider performance implications, use appropriate relationship types, and test cascading operations thoroughly.

---

## Ответ (RU)
**Отношения в Room** позволяют моделировать связи между сущностями без прямого хранения вложенных объектов. Room предоставляет аннотацию `@Relation` для запроса связанных сущностей и `@Embedded` для встраивания объектов в одну таблицу.

### Понимание отношений в Room

Room поддерживает три типа отношений:
1. **Один к одному**: Одна сущность связана с другой одной сущностью
2. **Один ко многим**: Одна сущность связана с множеством сущностей
3. **Многие ко многим**: Множество сущностей связаны с множеством сущностей (требуется junction table)

### Аннотация @Embedded

`@Embedded` позволяет встроить поля объекта в одну таблицу, избегая необходимости отдельных таблиц или JSON сериализации.

#### Базовый пример @Embedded

```kotlin
// Address НЕ является entity, просто data class
data class Address(
    val street: String,
    val city: String,
    val state: String,
    val zipCode: String,
    val country: String
)

// Entity User со встроенным адресом
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val name: String,
    val email: String,

    @Embedded
    val address: Address  // Поля будут встроены в таблицу users
)

// Сгенерированный SQL:
// CREATE TABLE users (
//     userId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
//     name TEXT NOT NULL,
//     email TEXT NOT NULL,
//     street TEXT NOT NULL,
//     city TEXT NOT NULL,
//     state TEXT NOT NULL,
//     zipCode TEXT NOT NULL,
//     country TEXT NOT NULL
// )
```

#### @Embedded с префиксом

При наличии нескольких встроенных объектов одного типа используйте `prefix` для избежания конфликтов имён колонок:

```kotlin
data class Coordinates(
    val latitude: Double,
    val longitude: Double
)

@Entity(tableName = "stores")
data class Store(
    @PrimaryKey(autoGenerate = true)
    val storeId: Long = 0,
    val name: String,

    @Embedded(prefix = "pickup_")
    val pickupLocation: Coordinates,

    @Embedded(prefix = "delivery_")
    val deliveryLocation: Coordinates
)

// Сгенерированные колонки:
// pickup_latitude, pickup_longitude
// delivery_latitude, delivery_longitude
```

### Отношение Один ко Многим

Наиболее распространённый тип отношений, где одна сущность связана с множеством сущностей.

#### Определение сущностей

```kotlin
// Родительская сущность
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val userId: Long = 0,
    val name: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
)

// Дочерняя сущность с внешним ключом
@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["userId"],
            childColumns = ["authorId"],
            onDelete = ForeignKey.CASCADE,  // Удалять посты при удалении пользователя
            onUpdate = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["authorId"])]  // Важно для производительности
)
data class Post(
    @PrimaryKey(autoGenerate = true)
    val postId: Long = 0,
    val authorId: Long,  // Внешний ключ к users.userId
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis()
)
```

#### Контейнер для отношения

```kotlin
// Класс-контейнер для пользователя с его постами
data class UserWithPosts(
    @Embedded
    val user: User,

    @Relation(
        parentColumn = "userId",    // Колонка в родителе (User)
        entityColumn = "authorId"   // Колонка в ребёнке (Post)
    )
    val posts: List<Post>
)
```

#### DAO запросы

```kotlin
@Dao
interface UserDao {
    @Insert
    suspend fun insertUser(user: User): Long

    @Insert
    suspend fun insertPost(post: Post): Long

    // Получить пользователя со всеми его постами
    @Transaction
    @Query("SELECT * FROM users WHERE userId = :userId")
    suspend fun getUserWithPosts(userId: Long): UserWithPosts?

    // Получить всех пользователей с их постами
    @Transaction
    @Query("SELECT * FROM users")
    suspend fun getAllUsersWithPosts(): List<UserWithPosts>

    // Получить пользователей, постивших за последние 30 дней
    @Transaction
    @Query("""
        SELECT DISTINCT users.* FROM users
        INNER JOIN posts ON users.userId = posts.authorId
        WHERE posts.createdAt > :since
    """)
    suspend fun getActiveUsersWithPosts(since: Long): List<UserWithPosts>
}
```

### Отношение Многие ко Многим

Отношения многие-ко-многим требуют **junction table** (также называемую таблицей перекрёстных ссылок) для хранения ассоциаций.

#### Пример: Студенты и Курсы

```kotlin
// Первая сущность
@Entity(tableName = "students")
data class Student(
    @PrimaryKey(autoGenerate = true)
    val studentId: Long = 0,
    val name: String,
    val email: String,
    val enrollmentYear: Int
)

// Вторая сущность
@Entity(tableName = "courses")
data class Course(
    @PrimaryKey(autoGenerate = true)
    val courseId: Long = 0,
    val code: String,
    val name: String,
    val credits: Int,
    val semester: String
)

// Junction table (сущность перекрёстных ссылок)
@Entity(
    tableName = "student_course_cross_ref",
    primaryKeys = ["studentId", "courseId"],  // Составной первичный ключ
    foreignKeys = [
        ForeignKey(
            entity = Student::class,
            parentColumns = ["studentId"],
            childColumns = ["studentId"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = Course::class,
            parentColumns = ["courseId"],
            childColumns = ["courseId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index(value = ["studentId"]),
        Index(value = ["courseId"])
    ]
)
data class StudentCourseCrossRef(
    val studentId: Long,
    val courseId: Long,
    val enrolledAt: Long = System.currentTimeMillis(),
    val grade: String? = null  // Дополнительные данные в junction table
)
```

#### Контейнеры для отношений

```kotlin
// Студент с его курсами
data class StudentWithCourses(
    @Embedded
    val student: Student,

    @Relation(
        parentColumn = "studentId",
        entityColumn = "courseId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val courses: List<Course>
)

// Курс с записанными студентами
data class CourseWithStudents(
    @Embedded
    val course: Course,

    @Relation(
        parentColumn = "courseId",
        entityColumn = "studentId",
        associateBy = Junction(StudentCourseCrossRef::class)
    )
    val students: List<Student>
)
```

#### DAO для Многие-ко-Многим

```kotlin
@Dao
interface StudentCourseDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStudent(student: Student): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCourse(course: Course): Long

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun enrollStudentInCourse(crossRef: StudentCourseCrossRef)

    @Delete
    suspend fun unenrollStudentFromCourse(crossRef: StudentCourseCrossRef)

    // Запрос курсов студента
    @Transaction
    @Query("SELECT * FROM students WHERE studentId = :studentId")
    suspend fun getStudentWithCourses(studentId: Long): StudentWithCourses?

    // Запрос студентов курса
    @Transaction
    @Query("SELECT * FROM courses WHERE courseId = :courseId")
    suspend fun getCourseWithStudents(courseId: Long): CourseWithStudents?

    // Проверить, записан ли студент на курс
    @Query("""
        SELECT EXISTS(
            SELECT 1 FROM student_course_cross_ref
            WHERE studentId = :studentId AND courseId = :courseId
        )
    """)
    suspend fun isStudentEnrolled(studentId: Long, courseId: Long): Boolean

    // Обновить оценку
    @Query("""
        UPDATE student_course_cross_ref
        SET grade = :grade
        WHERE studentId = :studentId AND courseId = :courseId
    """)
    suspend fun updateGrade(studentId: Long, courseId: Long, grade: String)
}
```

### Best Practices

1. **Использовать Foreign Keys**: Обеспечивать ссылочную целостность на уровне БД
2. **Добавлять индексы**: Индексировать колонки внешних ключей
3. **Использовать @Transaction**: Обеспечивать согласованность при загрузке отношений
4. **Каскадные операции**: Использовать `onDelete = CASCADE` для parent-child отношений
5. **Избегать глубокой вложенности**: Ограничить глубину отношений 2-3 уровнями
6. **Рассмотреть ленивую загрузку**: Не всегда загружать все отношения заранее
7. **Использовать Junction Tables**: Для многие-ко-многим всегда использовать правильную junction entity
8. **Префикс для встроенных объектов**: Избегать конфликтов имён колонок с параметром prefix

### Таблица сравнения: @Embedded vs @Relation

| Характеристика | @Embedded | @Relation |
|----------------|-----------|-----------|
| Назначение | Встроить объект в одну таблицу | Связать отдельные сущности |
| Таблицы | Одна таблица | Несколько таблиц |
| Внешние ключи | Не нужны | Обязательны |
| Сложность запросов | Простая (одна таблица) | Сложная (JOIN'ы) |
| Производительность | Быстрая (без JOIN'ов) | Медленнее (требуются JOIN'ы) |
| Дублирование данных | Возможно | Минимальное |
| Нормализация | Денормализованная | Нормализованная |
| Случай использования | Адрес, Координаты | Один-ко-многим, Многие-ко-многим |

### Резюме

Отношения в Room предоставляют мощные способы моделирования связей:

- **@Embedded**: Встраивание объектов в одну таблицу (композиция)
- **@Relation**: Связывание отдельных сущностей (ассоциация)
- **Один-ко-многим**: Родительская сущность → несколько детей
- **Многие-ко-многим**: Junction table для связи сущностей
- **Foreign Keys**: Обеспечение ссылочной целостности
- **@Transaction**: Обеспечение атомарных операций
- **Indices**: Оптимизация производительности запросов
- **Cascade**: Контроль поведения при удалении/обновлении

---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-room-library-definition--android--easy]] - Storage

### Related (Medium)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
- [[q-room-type-converters-advanced--room--medium]] - Storage
- [[q-room-vs-sqlite--android--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
