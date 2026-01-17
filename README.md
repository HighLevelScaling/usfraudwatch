# USFraudWatch

A fraud monitoring and detection system for tracking and analyzing suspicious activities.

## Overview

USFraudWatch provides real-time monitoring and analysis capabilities to detect and prevent fraudulent activities.

## Prerequisites

- Docker and Docker Compose
- Auth0 account for authentication

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd usfraudwatch
   ```

2. Copy the environment template and configure your settings:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your Auth0 credentials and other configuration.

4. Start the application using Docker:
   ```bash
   docker-compose up -d
   ```

## Project Structure

```
usfraudwatch/
├── src/
│   ├── api/          # API endpoints
│   ├── services/     # Business logic services
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── tests/            # Test files
├── config/           # Configuration files
└── docker-compose.yml
```

## Development

```bash
# Run tests
docker-compose exec app pytest

# View logs
docker-compose logs -f
```

## License

MIT
