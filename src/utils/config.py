from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Federal Fraud Watch"
    app_env: str = "development"
    debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Database
    database_url: str = "postgresql://fraud_user:fraud_password@db:5432/usfraudwatch"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Auth0
    auth0_domain: str = ""
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_audience: str = ""
    auth0_callback_url: str = "http://localhost:8000/callback"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_patriot: str = ""  # $8/month price ID
    stripe_price_watchdog: str = ""  # $39/month price ID
    stripe_price_founder: str = ""  # $199/month price ID

    # Storage
    storage_type: str = "local"  # "local" or "s3"
    upload_dir: str = "/app/uploads"
    s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"

    # Email (Resend)
    resend_api_key: str = ""
    from_email: str = "contact@federalfraudwatch.com"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
