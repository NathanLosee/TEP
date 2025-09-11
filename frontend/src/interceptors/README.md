# HTTP Interceptors

This directory contains HTTP interceptors that are applied to all HTTP requests made by the Angular application.

## Interceptors

### 1. Base URL Interceptor (`baseurl.interceptor.ts`)
- Adds the base API URL from environment configuration to all requests
- Automatically adds the Bearer token from localStorage to the Authorization header

### 2. Form Data Interceptor (`formdata.interceptor.ts`)
- Removes Content-Type header from FormData requests to allow browser to set proper boundary

### 3. Auth Refresh Interceptor (`auth-refresh.interceptor.ts`)
- **Purpose**: Automatically handles expired access tokens by refreshing them and retrying failed requests
- **Triggers**: When an API call returns 401 Unauthorized (indicating expired access token)
- **Process**:
  1. Detects 401 error responses (excluding refresh endpoint to prevent loops)
  2. Calls `/users/refresh` endpoint with refresh token from httpOnly cookies
  3. Updates localStorage with new access token
  4. Retries the original request with the new token
  5. If refresh fails, clears tokens and redirects to login page
- **Concurrency Handling**: Prevents multiple simultaneous refresh attempts when multiple requests fail at once
- **Error Handling**: Gracefully handles refresh failures and redirects to login

## Interceptor Order

The interceptors are applied in this order (configured in `app.config.ts`):
1. `baseUrlInterceptor` - Adds base URL and auth headers
2. `formDataInterceptor` - Handles form data requests
3. `authRefreshInterceptor` - Handles token refresh logic

This order ensures that:
- Base URL and auth headers are added first
- Form data is properly handled
- Token refresh happens after the request is fully prepared and sent