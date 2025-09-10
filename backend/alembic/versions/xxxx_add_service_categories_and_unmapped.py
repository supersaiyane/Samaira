"""add service_categories and unmapped_services, normalize services

Revision ID: xxxx_add_service_categories
Revises: <previous_revision_id>
Create Date: 2025-09-08

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "xxxx_add_service_categories"
down_revision = "<previous_revision_id>"
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create service_categories table
    op.create_table(
        "service_categories",
        sa.Column("category_id", sa.Integer, primary_key=True),
        sa.Column("category_name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text),
    )

    # 2. Create unmapped_services table
    op.create_table(
        "unmapped_services",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cloud_provider", sa.String(20), nullable=False),
        sa.Column("service_name", sa.String(255), nullable=False),
        sa.Column("first_seen", sa.TIMESTAMP, default=datetime.utcnow),
        sa.Column("last_seen", sa.TIMESTAMP, default=datetime.utcnow),
    )

    # 3. Add category_id column to services
    op.add_column("services", sa.Column("category_id", sa.Integer, sa.ForeignKey("service_categories.category_id")))

    # 4. Migrate old "category" values into service_categories
    conn = op.get_bind()
    if conn.dialect.has_table(conn, "services"):
        existing_services = conn.execute(sa.text("SELECT DISTINCT category FROM services WHERE category IS NOT NULL"))
        categories = {row[0] for row in existing_services if row[0]}

        for cat in categories:
            conn.execute(
                sa.text("INSERT INTO service_categories (category_name, description) VALUES (:name, :desc) ON CONFLICT DO NOTHING"),
                {"name": cat, "desc": f"Migrated category {cat}"}
            )

        # Link services to categories
        for cat in categories:
            conn.execute(
                sa.text("""
                    UPDATE services s
                    SET category_id = sc.category_id
                    FROM service_categories sc
                    WHERE s.category = :cat AND sc.category_name = :cat
                """),
                {"cat": cat}
            )

    # 5. Drop old "category" column
    with op.batch_alter_table("services") as batch_op:
        batch_op.drop_column("category")

def downgrade():
    # Re-add old category column
    op.add_column("services", sa.Column("category", sa.String(100)))

    # Drop new tables and column
    with op.batch_alter_table("services") as batch_op:
        batch_op.drop_column("category_id")

    op.drop_table("unmapped_services")
    op.drop_table("service_categories")
