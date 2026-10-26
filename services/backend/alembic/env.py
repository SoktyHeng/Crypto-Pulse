"""Alembic environment. Uses DATABASE_URL from settings unless a URL is passed in config."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.db.base import Base
from app.models import *  # noqa: F403  (registers every model on Base.metadata)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _database_url() -> str:
    # Tests and tooling may inject an explicit URL; otherwise use application settings.
    explicit = config.attributes.get("database_url")
    if isinstance(explicit, str) and explicit:
        return explicit
    return get_settings().database_url.get_secret_value()


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(
        _database_url(),
        poolclass=pool.NullPool,
        connect_args={"options": "-c timezone=UTC"},
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
