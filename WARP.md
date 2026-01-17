# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Federal Fraud Watch is a conservative watchdog content platform for immigration policy accountability. It features subscription-based content management, FOIA request tracking, and source document management. Built with FastAPI, PostgreSQL, Redis, Auth0, and Stripe.

## Essential Commands

### Docker Operations
```bash
# Start all services (app, PostgreSQL, Redis)
docker-compose up -d

# Rebuild and restart after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Access container shell
docker-compose exec app bash
```

### Database Migrations
```bash
# Run migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Rollback
docker-compose exec app alembic downgrade -1
```

### Testing
```bash
# Run all tests
docker-compose exec app pytest

# Run with coverage
docker-compose exec app pytest --cov=src
```

## Architecture

### Stack
- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL 15 with SQLAlchemy ORM + Alembic migrations
- **Cache**: Redis 7
- **Auth**: Auth0 (JWT validation)
- **Payments**: Stripe (subscriptions)
- **Email**: Resend (newsletters)
- **Storage**: Local or S3 (documents)

### Code Structure
```
src/
├── api/
│   ├── main.py          # FastAPI app entry point
│   ├── deps.py          # Auth & DB dependencies (CurrentUser, DbSession, etc.)
│   └── routes/
│       ├── articles.py      # Content CRUD with tier-based access
│       ├── subscriptions.py # Stripe checkout, webhooks, tiers
│       ├── foia.py          # FOIA request tracking
│       └── documents.py     # File uploads & downloads
├── models/
│   ├── base.py          # DB session, Base class, TimestampMixin
│   ├── user.py          # User with SubscriptionTier enum
│   ├── article.py       # Article with ContentPillar enum
│   ├── subscription.py  # Stripe subscription tracking
│   ├── foia.py          # FOIA requests with status workflow
│   └── document.py      # Source documents
├── schemas/             # Pydantic request/response schemas
├── services/
│   ├── auth.py          # Auth0 JWT validation
│   ├── stripe_service.py    # Stripe API integration
│   ├── storage_service.py   # Local/S3 file storage
│   └── email_service.py     # SendGrid newsletters
└── utils/
    ├── config.py        # Pydantic Settings (env vars)
    └── security.py      # Slug generation, sanitization
```

### Subscription Tiers
- **FREE**: Friday newsletter, free articles only
- **PATRIOT ($8/mo)**: Mon/Wed/Fri newsletters, all articles
- **WATCHDOG ($39/mo)**: + video, Q&A, early access
- **FOUNDER ($199/mo)**: + roundtable, direct access

### Content Pillars
Articles are categorized into 5 pillars:
- `money_trail`: Government spending analysis
- `sanctuary`: Sanctuary city policies
- `loopholes`: Asylum system exploitation
- `border_complex`: Profiteers analysis
- `impact`: Community impact stories

## API Endpoints

### Articles
- `GET /api/articles` - List (filtered by user's tier)
- `GET /api/articles/{slug}` - Get article (tier check)
- `POST /api/articles` - Create (author/admin)
- `PUT /api/articles/{id}` - Update
- `POST /api/articles/{id}/publish` - Publish/unpublish

### Subscriptions
- `GET /api/subscriptions/tiers` - List available tiers
- `GET /api/subscriptions/status` - Current user's subscription
- `POST /api/subscriptions/checkout` - Create Stripe checkout
- `POST /api/subscriptions/portal` - Stripe customer portal
- `POST /api/subscriptions/webhook` - Stripe webhook handler

### FOIA
- `GET /api/foia` - List requests (admin)
- `GET /api/foia/reminders` - Overdue/due soon requests
- `POST /api/foia` - Create request (auto-calculates 20 business day deadline)
- `POST /api/foia/{id}/status` - Update status

### Documents
- `GET /api/documents` - List (tier-filtered)
- `POST /api/documents/upload` - Upload file (admin)
- `GET /api/documents/{id}/download` - Download (tier check)

## Authentication Flow

1. Client obtains JWT from Auth0
2. Include token in `Authorization: Bearer <token>` header
3. `deps.py` validates token and creates/retrieves user
4. Use `CurrentUser`, `CurrentAdmin`, `CurrentAuthor` dependencies
5. Tier access checked via `user.can_access_tier(required_tier)`

## Environment Variables

Required for production:
- `AUTH0_DOMAIN`, `AUTH0_AUDIENCE` - Auth0 config
- `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` - Stripe keys
- `STRIPE_PRICE_PATRIOT/WATCHDOG/FOUNDER` - Stripe price IDs
- `RESEND_API_KEY` - Email service
- `DATABASE_URL`, `REDIS_URL` - Already configured for Docker

## Port Mappings
- **8000**: FastAPI API
- **5432**: PostgreSQL
- **6379**: Redis
