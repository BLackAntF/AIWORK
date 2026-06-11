# Backend API Template

A Next.js API backend template with MySQL and Redis.

## Features

- **Next.js API Routes** - Serverless API endpoints
- **MySQL Database** - Relational database integration
- **Redis Cache** - In-memory caching for performance
- **JWT Authentication** - Secure token-based authentication
- **Rate Limiting** - Request rate limiting middleware
- **TypeScript** - Type-safe development
- **Zod Validation** - Input validation (ready for use)

## Tech Stack

- Next.js 13+
- TypeScript
- MySQL 8+
- Redis 7+
- JWT (jsonwebtoken)
- bcryptjs (password hashing)

## Getting Started

### Prerequisites

- Node.js 18+
- MySQL 8+
- Redis 7+

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy and configure environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRES_IN=7d
```

4. Initialize the database:
```bash
mysql -u root -p < scripts/init-db.sql
```

5. Run the development server:
```bash
npm run dev
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login user |
| GET | `/api/auth/me` | Get current user (requires auth) |

### Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/items` | Get all items (requires auth) |
| GET | `/api/items?id={id}` | Get single item (requires auth) |
| POST | `/api/items` | Create item (requires auth) |
| PUT | `/api/items?id={id}` | Update item (requires auth) |
| DELETE | `/api/items?id={id}` | Delete item (requires auth) |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check server status |

## Project Structure

```
├── src/
│   ├── lib/           # Utility libraries
│   │   ├── auth.ts    # JWT authentication
│   │   ├── db.ts      # MySQL database connection
│   │   ├── redis.ts   # Redis cache connection
│   │   ├── error.ts   # Error handling
│   │   ├── logger.ts  # Logging
│   │   └── rateLimiter.ts
│   ├── middleware/    # Custom middleware
│   │   ├── auth.ts    # Authentication middleware
│   │   ├── rateLimit.ts
│   │   └── index.ts
│   └── pages/
│       └── api/       # API routes
│           ├── auth/  # Authentication endpoints
│           ├── items.ts
│           └── health.ts
├── scripts/           # Database scripts
│   └── init-db.sql    # Initial database setup
├── .env.example       # Environment variables template
└── package.json
```

## Usage

### Register User

```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Login

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Get Items (Authenticated)

```bash
curl -X GET http://localhost:3000/api/items \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Item

```bash
curl -X POST http://localhost:3000/api/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name": "New Item", "description": "Item description"}'
```

## Security

- Passwords are hashed using bcrypt
- JWT tokens are signed with a secret key
- Rate limiting prevents brute force attacks
- Input validation should be added for all endpoints
- Use HTTPS in production

## License

MIT
