import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    mercado_pago_access_token: str
    mercado_pago_webhook_secret: str
    rabbitmq_url: str
    frontend_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        values = {
            "database_url": os.environ.get("DATABASE_URL", ""),
            "mercado_pago_access_token": os.environ.get("MERCADO_PAGO_ACCESS_TOKEN", ""),
            "mercado_pago_webhook_secret": os.environ.get("MERCADO_PAGO_WEBHOOK_SECRET", ""),
            "rabbitmq_url": os.environ.get("AMQP_URL", ""),
            "frontend_origins": tuple(
                origin.strip()
                for origin in os.environ.get("FRONTEND_ORIGINS", "").split(",")
                if origin.strip()
            ),
        }
        missing = [
            name
            for name, value in values.items()
            if not value or (name == "frontend_origins" and not value)
        ]
        if missing:
            raise RuntimeError("Required application configuration is missing")
        if not values["database_url"].startswith("postgresql+asyncpg://"):
            raise RuntimeError("DATABASE_URL must use the asyncpg PostgreSQL driver")
        if not values["rabbitmq_url"].startswith(("amqp://", "amqps://")):
            raise RuntimeError("AMQP_URL must use the AMQP protocol")
        if "*" in values["frontend_origins"]:
            raise RuntimeError("FRONTEND_ORIGINS must list explicit origins")
        return cls(**values)
