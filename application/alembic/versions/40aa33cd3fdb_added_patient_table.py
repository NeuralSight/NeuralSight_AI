"""Added patient table

Revision ID: 40aa33cd3fdb
Revises: e4ab6f930855
Create Date: 2022-12-05 10:50:16.038700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40aa33cd3fdb'
down_revision = 'e4ab6f930855'
branch_labels = None
depends_on = None



def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "report",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("patient_id", sa.String(), nullable=False),
        sa.Column("report", sa.String(), nullable=True),
        sa.Column("inference_path", sa.String(), nullable=True),
        sa.Column("annotation_path", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patient.id"],),
        sa.PrimaryKeyConstraint("id"),
    )



    op.create_table(
            "patient",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("patient")
    # ### end Alembic commands ###
