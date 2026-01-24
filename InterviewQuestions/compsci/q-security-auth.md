---
id: cs-sec-auth
title: Security - Authentication and Authorization
topic: security
difficulty: medium
tags:
- cs_security
- authentication
- authorization
anki_cards:
- slug: cs-sec-auth-0-en
  language: en
  anki_id: 1769160676575
  synced_at: '2026-01-23T13:31:18.944237'
- slug: cs-sec-auth-0-ru
  language: ru
  anki_id: 1769160676600
  synced_at: '2026-01-23T13:31:18.945527'
- slug: cs-sec-auth-1-en
  language: en
  anki_id: 1769160676624
  synced_at: '2026-01-23T13:31:18.948972'
- slug: cs-sec-auth-1-ru
  language: ru
  anki_id: 1769160676649
  synced_at: '2026-01-23T13:31:18.950202'
- slug: cs-sec-auth-2-en
  language: en
  anki_id: 1769160676675
  synced_at: '2026-01-23T13:31:18.951361'
- slug: cs-sec-auth-2-ru
  language: ru
  anki_id: 1769160676699
  synced_at: '2026-01-23T13:31:18.952671'
---
# Authentication and Authorization

## Authentication vs Authorization

| Authentication | Authorization |
|----------------|---------------|
| Who are you? | What can you do? |
| Identity verification | Access control |
| Comes first | Comes after auth |

## Password Authentication

### Secure Password Storage

**Never store plaintext!**

```
Good:   hash(password + salt) + salt
Bad:    password
Bad:    hash(password)  (no salt)
Bad:    encrypt(password)  (reversible)
```

### Password Requirements

**NIST recommendations** (modern):
- Minimum 8 characters
- Check against breached passwords
- No complexity requirements (they don't help)
- No periodic rotation (unless compromised)
- Allow paste (password managers)

### Multi-Factor Authentication (MFA)

Something you:
- **Know**: Password, PIN
- **Have**: Phone, hardware key
- **Are**: Fingerprint, face

**Types**:
- TOTP (Time-based One-Time Password)
- SMS codes (less secure, SIM swapping)
- Hardware tokens (YubiKey)
- Push notifications
- Biometrics

### TOTP (Time-based OTP)

```
TOTP = HMAC(secret_key, time_step)

time_step = floor(current_time / 30)
```

**Apps**: Google Authenticator, Authy.

## Session-Based Authentication

```
1. User submits credentials
2. Server validates, creates session
3. Server sends session ID in cookie
4. Client sends cookie with requests
5. Server looks up session, identifies user
```

**Session storage**: Memory, database, Redis.

**Cookie attributes**:
```
Set-Cookie: session=abc123;
  HttpOnly;     -- No JavaScript access
  Secure;       -- HTTPS only
  SameSite=Lax; -- CSRF protection
  Path=/;
  Max-Age=3600
```

### Session Security

1. **Regenerate session ID** on login (prevent fixation)
2. **Set expiration** (idle and absolute)
3. **Invalidate on logout**
4. **Secure cookie settings**

## Token-Based Authentication

### JWT (JSON Web Token)

```
header.payload.signature

Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "user123",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622
}

Signature:
HMACSHA256(base64(header) + "." + base64(payload), secret)
```

**Verification**: Recalculate signature, compare.

**Advantages**:
- Stateless (no session storage)
- Can contain claims
- Works across services

**Disadvantages**:
- Can't revoke (until expiry)
- Payload not encrypted (only signed)
- Larger than session ID

### Access and Refresh Tokens

```
Access token:  Short-lived (15 min), used for API calls
Refresh token: Long-lived (7 days), used to get new access token
```

**Flow**:
```
1. Login -> access token + refresh token
2. API call with access token
3. Access token expires
4. Use refresh token to get new access token
5. Refresh token expires -> re-login
```

### Token Storage

| Location | XSS Risk | CSRF Risk |
|----------|----------|-----------|
| localStorage | High | None |
| Cookie (HttpOnly) | None | Needs protection |
| Memory | None | None (but lost on refresh) |

**Best practice**: HttpOnly cookie with CSRF protection.

## OAuth 2.0

**Delegated authorization** - grant access without sharing password.

### Roles

- **Resource Owner**: User
- **Client**: Application requesting access
- **Authorization Server**: Issues tokens
- **Resource Server**: API with protected data

### Authorization Code Flow

```
1. User clicks "Login with Google"
2. Redirect to authorization server
   /authorize?client_id=X&redirect_uri=Y&scope=Z&response_type=code

3. User authenticates and consents
4. Redirect back with authorization code
   callback?code=AUTH_CODE

5. Client exchanges code for tokens (server-side)
   POST /token
   {code, client_id, client_secret, redirect_uri}

6. Receive access token (and optionally refresh token)
```

### PKCE (Proof Key for Code Exchange)

For public clients (mobile apps, SPAs).

```
1. Generate code_verifier (random string)
2. code_challenge = SHA256(code_verifier)
3. Send code_challenge in authorize request
4. Send code_verifier in token request
5. Server verifies: SHA256(code_verifier) == code_challenge
```

### OAuth Flows

| Flow | Use Case |
|------|----------|
| Authorization Code | Server-side apps |
| Authorization Code + PKCE | Mobile, SPA |
| Client Credentials | Machine-to-machine |
| ~~Implicit~~ | Deprecated |
| ~~Password~~ | Deprecated |

## OpenID Connect (OIDC)

**Authentication layer on top of OAuth 2.0.**

Adds:
- ID token (JWT with user info)
- UserInfo endpoint
- Standard scopes (openid, profile, email)

```
ID Token payload:
{
  "iss": "https://auth.example.com",
  "sub": "user123",
  "aud": "client_app",
  "exp": 1516242622,
  "iat": 1516239022,
  "name": "John Doe",
  "email": "john@example.com"
}
```

## Authorization

### Role-Based Access Control (RBAC)

Permissions assigned to roles, roles assigned to users.

```
Roles:
  admin:  [create, read, update, delete]
  editor: [create, read, update]
  viewer: [read]

Users:
  john -> admin
  jane -> editor
```

### Attribute-Based Access Control (ABAC)

Decisions based on attributes of user, resource, environment.

```
Policy: "Allow if user.department == resource.department
         AND time.hour >= 9 AND time.hour <= 17"
```

### Permission Checking

```python
# Check before action
if user.has_permission('posts:delete'):
    delete_post(post_id)
else:
    raise Forbidden()

# Or use decorators
@require_permission('posts:delete')
def delete_post(post_id):
    ...
```

## Security Best Practices

1. **Hash passwords** with bcrypt/Argon2 + salt
2. **Use HTTPS** everywhere
3. **Implement rate limiting** on login
4. **Log authentication events**
5. **Require MFA** for sensitive operations
6. **Validate redirect URIs** (OAuth)
7. **Use short-lived tokens**
8. **Implement proper logout** (invalidate all tokens)

## Interview Questions

1. **JWT vs Session?**
   - JWT: Stateless, scalable, can't revoke easily
   - Session: Stateful, server storage, easy revocation

2. **How to securely store passwords?**
   - Hash with bcrypt/Argon2 + unique salt
   - Never plaintext, never reversible encryption

3. **What is OAuth 2.0?**
   - Delegated authorization protocol
   - Grant third-party access without sharing password
   - Defines flows for different client types

4. **How to implement "Remember Me"?**
   - Separate long-lived token
   - Store hashed in DB
   - Require re-auth for sensitive actions
