# Centralized API Client Integration Guide

## Overview

The Kuwait Social AI React application now includes a centralized API client that handles:
- Authentication with Bearer tokens
- Structured error responses
- Token refresh logic
- Request/response interceptors
- File uploads with progress tracking

## Key Components

### 1. API Client (`src/services/api/apiClient.ts`)
- Built on Axios for robust HTTP handling
- Automatically adds Bearer token to requests
- Handles 401 errors with token refresh
- Provides user-friendly error messages
- Includes request/response logging in development

### 2. API Endpoints
Organized by feature area:
- **Authentication** (`endpoints/auth.ts`): Login, register, token refresh
- **Posts** (`endpoints/posts.ts`): CRUD operations, media upload, AI generation
- **Analytics** (`endpoints/analytics.ts`): Metrics, reports, insights

### 3. Type Definitions
Strong TypeScript types for all API interactions:
- `types/auth.ts`: User, login, authentication state
- `types/posts.ts`: Post models, filters, platforms
- `types/analytics.ts`: Metrics, insights, date ranges

## Usage Examples

### Basic API Calls

```typescript
import { api } from '@/services/api';

// Login
const login = async (email: string, password: string) => {
  try {
    const response = await api.auth.login({ email, password });
    // Response includes user, access_token, refresh_token
    console.log('Logged in:', response.user);
  } catch (error) {
    // Error is already formatted with user-friendly message
    console.error('Login failed:', error.message);
  }
};

// Create post
const createPost = async (postData: CreatePostData) => {
  try {
    const post = await api.posts.createPost(postData);
    console.log('Post created:', post);
  } catch (error) {
    // Handle validation errors or other issues
    console.error('Failed to create post:', error);
  }
};
```

### Using with Redux Toolkit

The auth slice now includes async thunks:

```typescript
import { useAppDispatch } from '@/store/hooks';
import { login, fetchCurrentUser } from '@/store/slices/authSlice';

const LoginComponent = () => {
  const dispatch = useAppDispatch();
  
  const handleLogin = async (credentials: LoginCredentials) => {
    try {
      await dispatch(login(credentials)).unwrap();
      // Success - user is now logged in
    } catch (error) {
      // Error handling done by Redux
    }
  };
};
```

### Error Handling Hook

Use the `useApiError` hook for consistent error handling:

```typescript
import { useApiError } from '@/hooks/useApiError';

const MyComponent = () => {
  const { handleError } = useApiError();
  
  const fetchData = async () => {
    try {
      const data = await api.posts.getPosts();
      // Handle success
    } catch (error) {
      handleError(error); // Shows snackbar with error message
    }
  };
};
```

### File Uploads

```typescript
const uploadImage = async (file: File) => {
  try {
    const result = await api.posts.uploadMedia(
      file,
      (progress) => {
        console.log(`Upload progress: ${progress}%`);
      }
    );
    console.log('Uploaded:', result.url);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

## Environment Configuration

### Development (.env)
```env
VITE_API_URL=/api
```

### Production (.env.production)
```env
# For same-domain deployment (recommended)
VITE_API_URL=/api

# For separate domains
VITE_API_URL=https://api.yourdomain.com
```

## State Management Integration

The API client integrates seamlessly with Redux Toolkit:

1. **Token Management**: Automatically reads token from Redux store
2. **Token Refresh**: Dispatches refresh action when needed
3. **Logout**: Clears Redux state on authentication failure
4. **Error State**: Updates Redux error state for UI feedback

## Error Response Structure

The backend returns structured errors that the client interprets:

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "code": "INVALID_INPUT",
  "details": {
    "validation_errors": {
      "email": ["Invalid email format"],
      "password": ["Password too short"]
    }
  }
}
```

The API client automatically:
- Extracts the main error message
- Formats validation errors for display
- Provides appropriate user feedback

## Security Features

1. **Token Storage**: Uses localStorage with Redux persistence
2. **Auto Refresh**: Refreshes tokens before expiry
3. **Session Management**: Tracks last activity for timeout
4. **CORS**: Properly configured for production domains
5. **HTTPS**: Enforced in production environments

## Best Practices

1. **Always use the centralized API client** instead of raw fetch/axios
2. **Handle errors at the component level** using try/catch or the error hook
3. **Use TypeScript types** for all API interactions
4. **Let Redux manage authentication state** - don't store tokens elsewhere
5. **Test API calls** with proper error scenarios

## Troubleshooting

### CORS Errors
- Ensure backend `CORS_ORIGINS` includes your frontend domain
- Check that `VITE_API_URL` is correctly configured
- Verify Nginx proxy configuration in production

### Authentication Issues
- Check token expiration in Redux DevTools
- Verify refresh token is stored correctly
- Look for 401 errors in Network tab

### API Connection Problems
- Confirm backend is running and accessible
- Check `VITE_API_URL` environment variable
- Verify proxy configuration in development