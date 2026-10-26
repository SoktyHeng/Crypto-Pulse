"""FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import REQUEST_ID_HEADER, RequestContextMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, component="api")

    app = FastAPI(
        title="CryptoPulse AI API",
        version=__version__,
        description=(
            "Read-only market analysis API for Binance Spot USDT markets. "
            "Informational only; not financial advice."
        ),
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url=None,
    )
    # Route dependencies must see the settings this app was built with, not a global copy.
    app.dependency_overrides[get_settings] = lambda: settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=[REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
    )
    # Added last so it is outermost: every response, including CORS rejections, gets an id.
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
