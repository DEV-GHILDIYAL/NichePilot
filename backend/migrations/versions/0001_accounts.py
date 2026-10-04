"""Account and Niche DNA foundation.

Revision ID: 0001_accounts
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_accounts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False),
        sa.Column("platform_handle", sa.String(60)),
        sa.Column("paused", sa.Boolean(), nullable=False),
        sa.Column("active_niche_revision_id", sa.Uuid()),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("platform = 'instagram'", name="ck_accounts_platform"),
        sa.CheckConstraint("version >= 1", name="ck_accounts_version"),
        sa.UniqueConstraint("platform", "platform_handle", name="uq_accounts_platform_handle"),
    )
    op.create_table(
        "niche_dna_revisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("niche_name", sa.String(120), nullable=False),
        sa.Column("niche_description", sa.Text(), nullable=False),
        sa.Column("target_audience", sa.String(500), nullable=False),
        sa.Column("language", sa.String(35), nullable=False),
        sa.Column("tone", sa.String(500), nullable=False),
        sa.Column("content_pillars", sa.JSON(), nullable=False),
        sa.Column("forbidden_topics", sa.JSON(), nullable=False),
        sa.Column("trend_transformation_guidance", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("actor", sa.String(80), nullable=False),
        sa.Column("change_note", sa.String(500), nullable=False),
        sa.CheckConstraint("revision_number >= 1", name="ck_niche_revision_number"),
        sa.UniqueConstraint("account_id", "id", name="uq_niche_revision_account_id"),
        sa.UniqueConstraint("account_id", "revision_number", name="uq_niche_revision_number"),
    )
    op.create_foreign_key(
        "fk_accounts_active_revision_owner",
        "accounts",
        "niche_dna_revisions",
        ["id", "active_niche_revision_id"],
        ["account_id", "id"],
    )
    op.create_table(
        "account_change_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("actor", sa.String(80), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.String(300), nullable=False),
        sa.Column("old_revision_id", sa.Uuid()),
        sa.Column("new_revision_id", sa.Uuid()),
    )
    op.create_index(
        "ix_account_events_page",
        "account_change_events",
        ["account_id", "occurred_at", "id"],
    )
    op.execute(
        """
        CREATE FUNCTION prevent_niche_revision_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          RAISE EXCEPTION 'Niche DNA revisions are immutable';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER niche_revision_immutable
        BEFORE UPDATE OR DELETE ON niche_dna_revisions
        FOR EACH ROW EXECUTE FUNCTION prevent_niche_revision_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER niche_revision_immutable ON niche_dna_revisions")
    op.execute("DROP FUNCTION prevent_niche_revision_mutation()")
    op.drop_index("ix_account_events_page", table_name="account_change_events")
    op.drop_table("account_change_events")
    op.drop_constraint("fk_accounts_active_revision_owner", "accounts", type_="foreignkey")
    op.drop_table("niche_dna_revisions")
    op.drop_table("accounts")
