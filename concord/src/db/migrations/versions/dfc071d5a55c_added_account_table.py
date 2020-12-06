"""Added account table

Revision ID: dfc071d5a55c
Revises: 26801bcfd223
Create Date: 2020-12-06 13:13:15.996835

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dfc071d5a55c"
down_revision = "26801bcfd223"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.Column("fullname", sa.String(length=50), nullable=True),
        sa.Column("nickname", sa.String(length=12), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("email_address", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("address")
    op.drop_table("user")
    # ### end Alembic commands ###
