import hmac
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.accounts import service
from app.accounts.schemas import (
    AccountChangeEventResponse,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    EventPage,
    NicheDNARevisionCreate,
    NicheDNARevisionResponse,
)
from app.config import Settings, get_settings
from app.db import session_factory

logger = logging.getLogger("nichepilot")
logging.basicConfig(level=logging.INFO, format="%(message)s")


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app_settings.validate_startup()
        app.state.sessions = session_factory(app_settings.database_url)
        yield
        app.state.sessions.kw["bind"].dispose()

    app = FastAPI(title="NichePilot API", version="0.1.0", lifespan=lifespan)
    app.state.settings = app_settings

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = uuid.uuid4()
        request.state.request_id = request_id
        started = time.monotonic()
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = str(request_id)
        logger.info(
            json.dumps(
                {
                    "operation": "http_request",
                    "request_id": str(request_id),
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000, 1),
                }
            )
        )
        return response

    def db_session(request: Request):
        with request.app.state.sessions() as db:
            yield db

    def require_admin(
        request: Request, authorization: Annotated[str | None, Header()] = None
    ) -> str:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="administrator bearer token required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization.removeprefix("Bearer ")
        expected = request.app.state.settings.admin_api_token
        if not expected or not hmac.compare_digest(token, expected):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return "admin"

    def request_id(request: Request) -> uuid.UUID:
        return request.state.request_id

    Db = Annotated[Session, Depends(db_session)]
    Admin = Annotated[str, Depends(require_admin)]
    RequestId = Annotated[uuid.UUID, Depends(request_id)]

    @app.exception_handler(service.NotFound)
    async def not_found(_request: Request, _exc: service.NotFound):
        return Response(
            content='{"detail":"not found"}',
            status_code=404,
            media_type="application/json",
        )

    @app.exception_handler(service.Conflict)
    async def conflict(_request: Request, _exc: service.Conflict):
        return Response(
            content='{"detail":"conflict"}',
            status_code=409,
            media_type="application/json",
        )

    @app.exception_handler(IntegrityError)
    async def integrity_conflict(_request: Request, _exc: IntegrityError):
        return Response(
            content='{"detail":"conflict"}',
            status_code=409,
            media_type="application/json",
        )

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready(db: Db):
        try:
            db.execute(text("SELECT 1"))
        except Exception:
            raise HTTPException(status_code=503, detail="unavailable") from None
        return {"status": "ok"}

    @app.post("/api/v1/accounts", response_model=AccountResponse, status_code=201)
    def create_account(data: AccountCreate, db: Db, _admin: Admin, rid: RequestId):
        return service.create_account(db, data, rid)

    @app.get("/api/v1/accounts", response_model=list[AccountResponse])
    def list_accounts(
        db: Db,
        _admin: Admin,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        return service.list_accounts(db, limit, offset)

    @app.get("/api/v1/accounts/{account_id}", response_model=AccountResponse)
    def get_account(account_id: uuid.UUID, db: Db, _admin: Admin):
        return service.get_account(db, account_id)

    @app.patch("/api/v1/accounts/{account_id}", response_model=AccountResponse)
    def update_account(
        account_id: uuid.UUID, data: AccountUpdate, db: Db, _admin: Admin, rid: RequestId
    ):
        return service.update_account(db, account_id, data, rid)

    @app.post("/api/v1/accounts/{account_id}/pause", response_model=AccountResponse)
    def pause_account(account_id: uuid.UUID, db: Db, _admin: Admin, rid: RequestId):
        return service.set_paused(db, account_id, True, rid)

    @app.post("/api/v1/accounts/{account_id}/resume", response_model=AccountResponse)
    def resume_account(account_id: uuid.UUID, db: Db, _admin: Admin, rid: RequestId):
        return service.set_paused(db, account_id, False, rid)

    @app.get(
        "/api/v1/accounts/{account_id}/niche-dna",
        response_model=NicheDNARevisionResponse,
    )
    def get_active_revision(account_id: uuid.UUID, db: Db, _admin: Admin):
        return service.get_active_revision(db, account_id)

    @app.get(
        "/api/v1/accounts/{account_id}/niche-dna/revisions",
        response_model=list[NicheDNARevisionResponse],
    )
    def list_revisions(
        account_id: uuid.UUID,
        db: Db,
        _admin: Admin,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        return service.list_revisions(db, account_id, limit, offset)

    @app.post(
        "/api/v1/accounts/{account_id}/niche-dna/revisions",
        response_model=NicheDNARevisionResponse,
        status_code=201,
    )
    def create_revision(
        account_id: uuid.UUID, data: NicheDNARevisionCreate, db: Db, _admin: Admin, rid: RequestId
    ):
        return service.create_revision(db, account_id, data, rid)

    @app.get("/api/v1/accounts/{account_id}/events", response_model=EventPage)
    def list_events(
        account_id: uuid.UUID,
        db: Db,
        _admin: Admin,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        cursor: Annotated[str | None, Query(max_length=256)] = None,
    ):
        try:
            items, next_cursor = service.list_events(db, account_id, limit, cursor)
        except ValueError:
            raise HTTPException(status_code=422, detail="invalid cursor") from None
        return EventPage(
            items=[AccountChangeEventResponse.model_validate(item) for item in items],
            next_cursor=next_cursor,
        )

    return app


app = create_app()
