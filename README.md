# Instagram DM Automation - FastAPI Backend

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Instagram Account Management**: Connect and manage multiple Instagram business accounts
- **Conversation Tracking**: Track and manage conversations with Instagram users
- **Message Handling**: Send and receive messages via Instagram Messaging API
- **Webhook Processing**: Handle incoming messages and events from Meta
- **Role-Based Access Control**: User and admin roles with granular permissions

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **MongoDB** with **Beanie** - Async ODM for MongoDB
- **Pydantic** - Data validation and settings management
- **JWT** - Token-based authentication
- **httpx** - Async HTTP client for Meta API calls

## Project Structure

```
app/
├── main.py                 # FastAPI app initialization
├── config/                 # Configuration files
├── models/                 # Database models (Beanie)
├── schemas/                # Pydantic schemas
├── api/                    # API routes
├── core/                   # Core utilities (security, roles, exceptions)
├── services/               # Business logic layer
└── utils/                  # Utility functions (Meta API client)
```

## Setup

### Prerequisites

- Python 3.10+
- MongoDB (running locally or remote)
- Meta App with Instagram Messaging API access

### Installation

1. Clone the repository and navigate to the project directory

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
NODE_ENV=development
PORT=8000
MONGODB_URL=mongodb://127.0.0.1:27017/instagram-dm-automation
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_EXPIRATION_MINUTES=30
JWT_REFRESH_EXPIRATION_DAYS=30

# Meta Instagram API
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_VERIFY_TOKEN=your-webhook-verify-token
META_API_VERSION=v21.0

# CORS
CORS_ORIGINS=*
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication (`/v1/auth`)

- `POST /v1/auth/register` - Register a new user
- `POST /v1/auth/login` - Login user
- `POST /v1/auth/logout` - Logout user
- `POST /v1/auth/refresh-tokens` - Refresh access token
- `POST /v1/auth/forgot-password` - Request password reset
- `POST /v1/auth/reset-password` - Reset password
- `POST /v1/auth/verify-email` - Verify email

### Instagram Accounts (`/v1/instagram`)

- `POST /v1/instagram` - Connect Instagram account
- `GET /v1/instagram` - List user's Instagram accounts
- `GET /v1/instagram/{accountId}` - Get account details
- `PATCH /v1/instagram/{accountId}` - Update account
- `DELETE /v1/instagram/{accountId}` - Delete account
- `GET /v1/instagram/{accountId}/profile` - Get Instagram profile details

### Conversations (`/v1/conversations`)

- `GET /v1/conversations/{accountId}` - Get conversations for an account
- `GET /v1/conversations/detail/{conversationId}` - Get conversation details
- `DELETE /v1/conversations/detail/{conversationId}` - Delete conversation

### Messages (`/v1/messages`)

- `GET /v1/messages/{conversationId}` - Get messages for a conversation
- `POST /v1/messages/{conversationId}` - Send message
- `POST /v1/messages/{conversationId}/read` - Mark messages as read

### Webhook (`/v1/webhook`)

- `GET /v1/webhook` - Webhook verification (Meta)
- `POST /v1/webhook` - Handle webhook events

### Health Checks

- `GET /health-check` - Health check
- `GET /running` - Running status
- `GET /` - Root endpoint

## Authentication

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Permissions

### User Role
- `manage-instagram-accounts`
- `view-conversations`
- `send-messages`
- `view-messages`

### Admin Role
- All user permissions +
- `manage-users`
- `view-logs`

## Webhook Setup

To receive messages from Instagram, configure your Meta app webhook:

1. Set webhook URL: `https://your-domain.com/v1/webhook`
2. Set verify token: Must match `META_VERIFY_TOKEN` in `.env`
3. Subscribe to `messages` events

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Structure

- **Models**: Database models using Beanie ODM
- **Schemas**: Pydantic schemas for request/response validation
- **Services**: Business logic layer (separated from routes)
- **API Routes**: FastAPI route handlers
- **Core**: Security, roles, and exception handling utilities

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Input validation with Pydantic
- CORS configuration
- Sensitive data protection (access tokens never returned in responses)

## License

MIT

