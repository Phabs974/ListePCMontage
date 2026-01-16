"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "VENDOR", "BUILDER", name="user_role"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("invoice_number", sa.String(), nullable=False),
        sa.Column("store", sa.String(), nullable=True),
        sa.Column("client_name", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prepared", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("built", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("delivered", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("created_by", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("invoice_number"),
    )
    op.create_index(op.f("ix_orders_invoice_number"), "orders", ["invoice_number"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_orders_invoice_number"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_role")
