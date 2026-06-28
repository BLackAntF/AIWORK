# Backend API Template

A Next.js API backend template with MySQL and Redis.

## Features

- **Next.js API Routes** - Serverless API endpoints
- **MySQL Database** - Relational database integration
- **Redis Cache** - In-memory caching for performance
- **JWT Authentication** - Secure token-based authentication
- **Rate Limiting** - Request rate limiting middleware
- **TypeScript** - Type-safe development

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

3. Update `.env` with your database credentials

4. Initialize the database:
```bash
mysql -u root -p < scripts/init-db.sql
```

5. Run the development server:
```bash
npm run dev
```

## API Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.
