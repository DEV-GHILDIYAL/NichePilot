import base64
import binascii
import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.accounts.models import Account, AccountChangeEvent, NicheDNARevision
from app.accounts.schemas import AccountCreate, AccountUpdate, NicheDNAInput, NicheDNARevisionCreate


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


def _account(db: Session, account_id: uuid.UUID, *, lock: bool = False) -> Account:
    query = select(Account).where(Account.id == account_id)
    if lock:
        query = query.with_for_update()
    account = db.scalar(query)
    if account is None:
        raise NotFound()
    return account


def _revision(
    db: Session, account_id: uuid.UUID, revision_id: uuid.UUID | None
) -> NicheDNARevision:
    revision = db.scalar(
        select(NicheDNARevision).where(
            NicheDNARevision.account_id == account_id,
            NicheDNARevision.id == revision_id,
        )
    )
    if revision is None:
        raise NotFound()
    return revision


def _new_revision(
    account_id: uuid.UUID, number: int, data: NicheDNAInput, actor: str
) -> NicheDNARevision:
    return NicheDNARevision(
        account_id=account_id,
        revision_number=number,
        niche_name=data.niche_name,
        niche_description=data.niche_description,
        target_audience=data.target_audience,
        language=data.language,
        tone=data.tone,
        content_pillars=[pillar.model_dump() for pillar in data.content_pillars],
        forbidden_topics=data.forbidden_topics,
        trend_transformation_guidance=data.trend_transformation_guidance,
        actor=actor,
        change_note=data.change_note,
    )


def _event(
    db: Session,
    account_id: uuid.UUID,
    request_id: uuid.UUID,
    action: str,
    summary: str,
    old_revision_id: uuid.UUID | None = None,
    new_revision_id: uuid.UUID | None = None,
) -> None:
    db.add(
        AccountChangeEvent(
            account_id=account_id,
            actor="admin",
            action=action,
            request_id=request_id,
            summary=summary,
            old_revision_id=old_revision_id,
            new_revision_id=new_revision_id,
        )
    )


def create_account(db: Session, data: AccountCreate, request_id: uuid.UUID) -> Account:
    with db.begin():
        account = Account(
            display_name=data.display_name,
            platform=data.platform,
            platform_handle=data.platform_handle,
            paused=True,
        )
        db.add(account)
        db.flush()
        revision = _new_revision(account.id, 1, data.niche_dna, "admin")
        db.add(revision)
        db.flush()
        account.active_niche_revision_id = revision.id
        _event(
            db,
            account.id,
            request_id,
            "account_created",
            "Account and initial Niche DNA created",
            new_revision_id=revision.id,
        )
        db.flush()
    db.refresh(account)
    return account


def list_accounts(db: Session, limit: int, offset: int) -> list[Account]:
    return list(
        db.scalars(
            select(Account)
            .order_by(Account.created_at.desc(), Account.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def get_account(db: Session, account_id: uuid.UUID) -> Account:
    return _account(db, account_id)


def update_account(
    db: Session, account_id: uuid.UUID, data: AccountUpdate, request_id: uuid.UUID
) -> Account:
    with db.begin():
        account = _account(db, account_id, lock=True)
        if account.version != data.expected_version:
            raise Conflict("account version changed")
        changed = False
        for field in data.model_fields_set - {"expected_version"}:
            value = getattr(data, field)
            if getattr(account, field) != value:
                setattr(account, field, value)
                changed = True
        if changed:
            account.version += 1
            _event(db, account.id, request_id, "account_updated", "Account metadata updated")
    db.refresh(account)
    return account


def set_paused(db: Session, account_id: uuid.UUID, paused: bool, request_id: uuid.UUID) -> Account:
    with db.begin():
        account = _account(db, account_id, lock=True)
        if account.paused != paused:
            account.paused = paused
            account.version += 1
            action = "account_paused" if paused else "account_resumed"
            _event(db, account.id, request_id, action, action.replace("_", " ").capitalize())
    db.refresh(account)
    return account


def get_active_revision(db: Session, account_id: uuid.UUID) -> NicheDNARevision:
    account = _account(db, account_id)
    return _revision(db, account_id, account.active_niche_revision_id)


def list_revisions(
    db: Session, account_id: uuid.UUID, limit: int, offset: int
) -> list[NicheDNARevision]:
    _account(db, account_id)
    return list(
        db.scalars(
            select(NicheDNARevision)
            .where(NicheDNARevision.account_id == account_id)
            .order_by(NicheDNARevision.revision_number.desc())
            .limit(limit)
            .offset(offset)
        )
    )


def create_revision(
    db: Session, account_id: uuid.UUID, data: NicheDNARevisionCreate, request_id: uuid.UUID
) -> NicheDNARevision:
    with db.begin():
        account = _account(db, account_id, lock=True)
        active = _revision(db, account_id, account.active_niche_revision_id)
        if active.revision_number != data.expected_active_revision_number:
            raise Conflict("active revision changed")
        revision = _new_revision(account.id, active.revision_number + 1, data, "admin")
        db.add(revision)
        db.flush()
        account.active_niche_revision_id = revision.id
        account.version += 1
        _event(
            db,
            account.id,
            request_id,
            "niche_dna_revised",
            "Niche DNA revision activated",
            old_revision_id=active.id,
            new_revision_id=revision.id,
        )
    db.refresh(revision)
    return revision


def _decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)).decode()
        timestamp, event_id = raw.split("|", 1)
        result = datetime.fromisoformat(timestamp), uuid.UUID(event_id)
        if result[0].tzinfo is None:
            raise ValueError("timezone required")
        return result
    except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
        raise ValueError("invalid cursor") from exc


def _encode_cursor(event: AccountChangeEvent) -> str:
    raw = f"{event.occurred_at.isoformat()}|{event.id}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def list_events(
    db: Session, account_id: uuid.UUID, limit: int, cursor: str | None
) -> tuple[list[AccountChangeEvent], str | None]:
    _account(db, account_id)
    query = select(AccountChangeEvent).where(AccountChangeEvent.account_id == account_id)
    if cursor:
        timestamp, event_id = _decode_cursor(cursor)
        query = query.where(
            or_(
                AccountChangeEvent.occurred_at < timestamp,
                and_(
                    AccountChangeEvent.occurred_at == timestamp,
                    AccountChangeEvent.id < event_id,
                ),
            )
        )
    items = list(
        db.scalars(
            query.order_by(
                AccountChangeEvent.occurred_at.desc(), AccountChangeEvent.id.desc()
            ).limit(limit + 1)
        )
    )
    has_more = len(items) > limit
    page = items[:limit]
    return page, _encode_cursor(page[-1]) if has_more else None
