"""Initial migration - create payments and rent_records tables

Revision ID: 001
Revises: 
Create Date: 2026-01-09 10:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables"""
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('phone_number', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create rent_records table
    op.create_table(
        'rent_records',
        sa.Column('phone_number', sa.Text(), nullable=True),
        sa.Column('reply', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Drop tables"""
    op.drop_table('rent_records')
    op.drop_table('payments')
