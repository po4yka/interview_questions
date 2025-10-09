---
topic: android
tags:
  - android
  - android/networking
  - get-request
  - networking
  - path-parameter
  - path-parameters
  - rest-api
  - retrofit
difficulty: medium
status: reviewed
---

# Как в Ретрофите в гет методе поставить атрибут в путь в конкретном месте?

**English**: How to put a parameter in a specific place in the path for a GET method in Retrofit?

## Answer

In Retrofit, to pass a value into a specific place in the URL for a GET request, use the **`@Path`** annotation.

**Steps:**
1. Define a placeholder in `@GET` using curly braces: `{parameterName}`
2. Use `@Path("parameterName")` to bind the method parameter to the placeholder

```kotlin
@GET("users/{userId}/posts/{postId}")
suspend fun getPost(
    @Path("userId") userId: String,
    @Path("postId") postId: String
): Response<Post>
```

**Example call:**
```kotlin
api.getPost("123", "456")
// Resolves to: GET /users/123/posts/456
```

---

## @Path Annotation Basics

### Simple Example

```kotlin
interface ApiService {

    @GET("users/{id}")
    suspend fun getUserById(
        @Path("id") userId: String
    ): Response<User>
}

// Usage
val response = api.getUserById("42")
// URL: https://api.example.com/users/42
```

**How it works:**
1. `{id}` is a placeholder in the URL path
2. `@Path("id")` binds the `userId` parameter to the `{id}` placeholder
3. Retrofit replaces `{id}` with the actual value `"42"`

---

### Multiple Path Parameters

```kotlin
interface ApiService {

    @GET("users/{userId}/posts/{postId}")
    suspend fun getUserPost(
        @Path("userId") userId: String,
        @Path("postId") postId: Int
    ): Response<Post>

    @GET("categories/{category}/products/{productId}")
    suspend fun getProduct(
        @Path("category") category: String,
        @Path("productId") productId: String
    ): Response<Product>
}

// Usage
val post = api.getUserPost("user123", 456)
// URL: https://api.example.com/users/user123/posts/456

val product = api.getProduct("electronics", "prod789")
// URL: https://api.example.com/categories/electronics/products/prod789
```

---

## Path Parameters vs Query Parameters

### @Path - Part of URL Path

```kotlin
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String): Response<User>

// Call
api.getUser("123")
// URL: https://api.example.com/users/123
```

**When to use:**
- Resource identification (user ID, post ID, etc.)
- Required parameters
- RESTful URLs

---

### @Query - Query String

```kotlin
@GET("users")
suspend fun searchUsers(@Query("name") userName: String): Response<List<User>>

// Call
api.searchUsers("John")
// URL: https://api.example.com/users?name=John
```

**When to use:**
- Filtering, searching, sorting
- Optional parameters
- Multiple values

---

### Combining @Path and @Query

```kotlin
@GET("users/{userId}/posts")
suspend fun getUserPosts(
    @Path("userId") userId: String,
    @Query("page") page: Int,
    @Query("limit") limit: Int
): Response<List<Post>>

// Call
api.getUserPosts("user123", 1, 20)
// URL: https://api.example.com/users/user123/posts?page=1&limit=20
```

---

## Real-World Examples

### Example 1: GitHub API

```kotlin
interface GitHubApi {

    // Get user profile
    @GET("users/{username}")
    suspend fun getUser(
        @Path("username") username: String
    ): Response<GitHubUser>

    // Get user repositories
    @GET("users/{username}/repos")
    suspend fun getUserRepos(
        @Path("username") username: String,
        @Query("sort") sort: String = "updated",
        @Query("per_page") perPage: Int = 30
    ): Response<List<Repo>>

    // Get specific repository
    @GET("repos/{owner}/{repo}")
    suspend fun getRepository(
        @Path("owner") owner: String,
        @Path("repo") repoName: String
    ): Response<Repo>
}

// Usage
val api = retrofit.create(GitHubApi::class.java)

// Get user
val user = api.getUser("octocat")
// URL: https://api.github.com/users/octocat

// Get repositories
val repos = api.getUserRepos("octocat", "updated", 50)
// URL: https://api.github.com/users/octocat/repos?sort=updated&per_page=50

// Get specific repo
val repo = api.getRepository("square", "retrofit")
// URL: https://api.github.com/repos/square/retrofit
```

---

### Example 2: E-Commerce API

```kotlin
interface ShopApi {

    // Get category products
    @GET("categories/{categoryId}/products")
    suspend fun getCategoryProducts(
        @Path("categoryId") categoryId: String,
        @Query("page") page: Int = 1,
        @Query("sort") sortBy: String = "name"
    ): Response<ProductList>

    // Get product details
    @GET("products/{productId}")
    suspend fun getProductDetails(
        @Path("productId") productId: String
    ): Response<Product>

    // Get product reviews
    @GET("products/{productId}/reviews")
    suspend fun getProductReviews(
        @Path("productId") productId: String,
        @Query("rating") minRating: Int? = null
    ): Response<List<Review>>
}

// Usage
val products = api.getCategoryProducts("electronics", 1, "price")
// URL: https://api.shop.com/categories/electronics/products?page=1&sort=price

val product = api.getProductDetails("prod123")
// URL: https://api.shop.com/products/prod123

val reviews = api.getProductReviews("prod123", 4)
// URL: https://api.shop.com/products/prod123/reviews?rating=4
```

---

### Example 3: Social Media API

```kotlin
interface SocialApi {

    // Get user profile
    @GET("users/{userId}")
    suspend fun getUserProfile(
        @Path("userId") userId: String
    ): Response<UserProfile>

    // Get user posts
    @GET("users/{userId}/posts/{postId}")
    suspend fun getPost(
        @Path("userId") userId: String,
        @Path("postId") postId: String
    ): Response<Post>

    // Get post comments
    @GET("users/{userId}/posts/{postId}/comments")
    suspend fun getPostComments(
        @Path("userId") userId: String,
        @Path("postId") postId: String,
        @Query("limit") limit: Int = 10
    ): Response<List<Comment>>

    // Like a post
    @POST("users/{userId}/posts/{postId}/like")
    suspend fun likePost(
        @Path("userId") userId: String,
        @Path("postId") postId: String
    ): Response<LikeResponse>
}

// Usage
val profile = api.getUserProfile("user456")
// URL: https://api.social.com/users/user456

val post = api.getPost("user456", "post789")
// URL: https://api.social.com/users/user456/posts/post789

val comments = api.getPostComments("user456", "post789", 20)
// URL: https://api.social.com/users/user456/posts/post789/comments?limit=20

val likeResult = api.likePost("user456", "post789")
// URL: POST https://api.social.com/users/user456/posts/post789/like
```

---

## Advanced: URL Encoding

### Automatic Encoding

Retrofit automatically encodes path parameters:

```kotlin
@GET("search/{query}")
suspend fun search(@Path("query") query: String): Response<SearchResults>

// Call
api.search("hello world")
// URL: https://api.example.com/search/hello%20world (space encoded as %20)

api.search("user@example.com")
// URL: https://api.example.com/search/user%40example.com (@ encoded as %40)
```

---

### Disable Encoding

Use `@Path(encoded = true)` to pass already-encoded values:

```kotlin
@GET("files/{path}")
suspend fun getFile(
    @Path(value = "path", encoded = true) filePath: String
): Response<FileContent>

// Call
api.getFile("folder/subfolder/file.txt")
// URL: https://api.example.com/files/folder/subfolder/file.txt
// (slashes are NOT encoded)

// Without encoded = true:
// URL would be: https://api.example.com/files/folder%2Fsubfolder%2Ffile.txt
```

---

## Common Patterns

### Pattern 1: Resource by ID

```kotlin
// REST pattern: GET /resource/{id}
@GET("users/{id}")
suspend fun getUser(@Path("id") id: String): Response<User>

@GET("posts/{id}")
suspend fun getPost(@Path("id") id: String): Response<Post>

@GET("products/{id}")
suspend fun getProduct(@Path("id") id: String): Response<Product>
```

---

### Pattern 2: Nested Resources

```kotlin
// REST pattern: GET /parent/{parentId}/child/{childId}
@GET("users/{userId}/posts/{postId}")
suspend fun getUserPost(
    @Path("userId") userId: String,
    @Path("postId") postId: String
): Response<Post>

@GET("categories/{categoryId}/subcategories/{subcategoryId}")
suspend fun getSubcategory(
    @Path("categoryId") categoryId: String,
    @Path("subcategoryId") subcategoryId: String
): Response<Subcategory>
```

---

### Pattern 3: Dynamic Endpoints

```kotlin
// Different endpoints for different resource types
@GET("{type}/{id}")
suspend fun getResource(
    @Path("type") resourceType: String,
    @Path("id") resourceId: String
): Response<JsonObject>

// Call
api.getResource("users", "123")  // GET /users/123
api.getResource("posts", "456")  // GET /posts/456
```

---

## Complete Example: Movie Database API

```kotlin
// API Interface
interface MovieApi {

    @GET("movies/{movieId}")
    suspend fun getMovie(
        @Path("movieId") movieId: String
    ): Response<Movie>

    @GET("movies/{movieId}/cast")
    suspend fun getMovieCast(
        @Path("movieId") movieId: String
    ): Response<List<Actor>>

    @GET("movies/{movieId}/reviews")
    suspend fun getMovieReviews(
        @Path("movieId") movieId: String,
        @Query("page") page: Int = 1
    ): Response<ReviewList>

    @GET("actors/{actorId}")
    suspend fun getActor(
        @Path("actorId") actorId: String
    ): Response<Actor>

    @GET("actors/{actorId}/movies")
    suspend fun getActorMovies(
        @Path("actorId") actorId: String,
        @Query("sort_by") sortBy: String = "release_date"
    ): Response<List<Movie>>
}

// Models
data class Movie(
    val id: String,
    val title: String,
    val releaseDate: String,
    val rating: Double
)

data class Actor(
    val id: String,
    val name: String,
    val bio: String
)

data class Review(
    val id: String,
    val author: String,
    val content: String,
    val rating: Int
)

data class ReviewList(
    val page: Int,
    val results: List<Review>
)

// Repository
class MovieRepository(private val api: MovieApi) {

    suspend fun getMovieDetails(movieId: String): Result<Movie> {
        return try {
            val response = api.getMovie(movieId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to fetch movie"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMovieCast(movieId: String): Result<List<Actor>> {
        return try {
            val response = api.getMovieCast(movieId)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(IOException("Failed to fetch cast"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ViewModel
class MovieViewModel(
    private val repository: MovieRepository
) : ViewModel() {

    private val _movie = MutableStateFlow<Movie?>(null)
    val movie: StateFlow<Movie?> = _movie

    private val _cast = MutableStateFlow<List<Actor>>(emptyList())
    val cast: StateFlow<List<Actor>> = _cast

    fun loadMovie(movieId: String) {
        viewModelScope.launch {
            repository.getMovieDetails(movieId)
                .onSuccess { _movie.value = it }
                .onFailure { /* handle error */ }

            repository.getMovieCast(movieId)
                .onSuccess { _cast.value = it }
                .onFailure { /* handle error */ }
        }
    }
}

// Usage
val viewModel = MovieViewModel(repository)
viewModel.loadMovie("tt0111161")  // The Shawshank Redemption
// Calls:
// GET https://api.movies.com/movies/tt0111161
// GET https://api.movies.com/movies/tt0111161/cast
```

---

## Common Mistakes

### Mistake 1: Forgetting Placeholder

```kotlin
// - BAD: No placeholder in URL
@GET("users/id")
suspend fun getUser(@Path("id") userId: String): Response<User>

// URL: https://api.example.com/users/id (literal "id", not replaced!)

// - GOOD: Use placeholder
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String): Response<User>

// URL: https://api.example.com/users/123
```

---

### Mistake 2: Mismatched Names

```kotlin
// - BAD: Placeholder name doesn't match @Path value
@GET("users/{userId}")
suspend fun getUser(@Path("id") userId: String): Response<User>
// Error: No path parameter {id} found

// - GOOD: Names match
@GET("users/{userId}")
suspend fun getUser(@Path("userId") userId: String): Response<User>
```

---

### Mistake 3: Using @Query for Path Parameters

```kotlin
// - BAD: Using @Query for path parameter
@GET("users")
suspend fun getUser(@Query("id") userId: String): Response<User>
// URL: https://api.example.com/users?id=123 (wrong!)

// - GOOD: Use @Path for path parameters
@GET("users/{id}")
suspend fun getUser(@Path("id") userId: String): Response<User>
// URL: https://api.example.com/users/123
```

---

## Summary

**@Path annotation in Retrofit:**

**Purpose:** Replace placeholders in URL path with actual values

**Syntax:**
```kotlin
@GET("endpoint/{placeholder}")
suspend fun apiCall(@Path("placeholder") value: String): Response<T>
```

**Key points:**
1. Use `{placeholder}` in `@GET` URL
2. Use `@Path("placeholder")` to bind parameter
3. Placeholder name must match `@Path` value
4. Automatic URL encoding (use `encoded = true` to disable)

**When to use:**
- Resource identification (IDs)
- Required parameters
- RESTful URLs

**Difference from @Query:**
- `@Path` - part of URL path (`/users/123`)
- `@Query` - query string (`/users?id=123`)

**Examples:**
```kotlin
// Simple
@GET("users/{id}")
getUser(@Path("id") id: String)
// → /users/123

// Multiple
@GET("users/{userId}/posts/{postId}")
getPost(@Path("userId") userId: String, @Path("postId") postId: String)
// → /users/123/posts/456

// Combined with @Query
@GET("users/{id}/posts")
getPosts(@Path("id") id: String, @Query("page") page: Int)
// → /users/123/posts?page=1
```

---

## Ответ

В Retrofit, чтобы передать значение в определённое место URL-адреса для GET-запроса, используйте аннотацию **`@Path`**.

**Шаги:**
1. В `@GET` укажите плейсхолдер в фигурных скобках: `{имяПараметра}`
2. Используйте `@Path("имяПараметра")` для связывания параметра метода с плейсхолдером

```kotlin
@GET("users/{userId}/posts/{postId}")
suspend fun getPost(
    @Path("userId") userId: String,
    @Path("postId") postId: String
): Response<Post>

// Вызов
api.getPost("123", "456")
// Преобразуется в: GET /users/123/posts/456
```

**Ключевые моменты:**
- Имя плейсхолдера должно совпадать со значением в `@Path`
- Автоматическое URL-кодирование (используйте `encoded = true` для отключения)
- Для идентификации ресурсов используйте `@Path`, для фильтров - `@Query`

