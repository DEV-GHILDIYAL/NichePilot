import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("platform", "platform_handle", name="uq_accounts_platform_handle"),
        ForeignKeyConstraint(
            ["id", "active_niche_revision_id"],
            ["niche_dna_revisions.account_id", "niche_dna_revisions.id"],
            name="fk_accounts_active_revision_owner",
            use_alter=True,
        ),
        CheckConstraint("platform = 'instagram'", name="ck_accounts_platform"),
        CheckConstraint("version >= 1", name="ck_accounts_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False, default="instagram")
    platform_handle: Mapped[str | None] = mapped_column(String(60))
    paused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active_niche_revision_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class NicheDNARevision(Base):
    __tablename__ = "niche_dna_revisions"
    __table_args__ = (
        UniqueConstraint("account_id", "id", name="uq_niche_revision_account_id"),
        UniqueConstraint("account_id", "revision_number", name="uq_niche_revision_number"),
        CheckConstraint("revision_number >= 1", name="ck_niche_revision_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    niche_name: Mapped[str] = mapped_column(String(120), nullable=False)
    niche_description: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(500), nullable=False)
    language: Mapped[str] = mapped_column(String(35), nullable=False)
    tone: Mapped[str] = mapped_column(String(500), nullable=False)
    content_pillars: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False)
    forbidden_topics: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    trend_transformation_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor: Mapped[str] = mapped_column(String(80), nullable=False)
    change_note: Mapped[str] = mapped_column(String(500), nullable=False)


class AccountChangeEvent(Base):
    __tablename__ = "account_change_events"
    __table_args__ = (Index("ix_account_events_page", "account_id", "occurred_at", "id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    actor: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    request_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    summary: Mapped[str] = mapped_column(String(300), nullable=False)
    old_revision_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    new_revision_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
