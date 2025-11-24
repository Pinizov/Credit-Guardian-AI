"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-23
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Creditor
    op.create_table(
        'creditors',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('bulstat', sa.String(15)),
        sa.Column('license_number', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('violations_count', sa.Integer(), server_default='0'),
        sa.Column('risk_score', sa.Float(), server_default='0'),
        sa.Column('is_blacklisted', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.UniqueConstraint('bulstat', name='uq_creditor_bulstat'),
    )
    op.create_index('ix_creditor_name', 'creditors', ['name'])

    # Violations
    op.create_table(
        'violations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('creditor_id', sa.Integer(), nullable=False),
        sa.Column('violation_type', sa.String(120)),
        sa.Column('description', sa.Text()),
        sa.Column('law_reference', sa.String(255)),
        sa.Column('decision_number', sa.String(120)),
        sa.Column('authority', sa.String(60)),
        sa.Column('penalty_amount', sa.Float()),
        sa.Column('decision_date', sa.DateTime()),
        sa.Column('source_url', sa.Text()),
        sa.Column('document_text', sa.Text()),
        sa.Column('severity', sa.String(20), server_default='low'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_violation_creditor', 'violations', ['creditor_id'])
    op.create_index('ix_violation_severity', 'violations', ['severity'])

    # Unfair Clauses
    op.create_table(
        'unfair_clauses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('creditor_id', sa.Integer(), nullable=False),
        sa.Column('clause_text', sa.Text(), nullable=False),
        sa.Column('clause_type', sa.String(120)),
        sa.Column('legal_basis', sa.String(255)),
        sa.Column('court_decision', sa.String(120)),
        sa.Column('is_confirmed_illegal', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('examples', sa.JSON()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_clause_creditor', 'unfair_clauses', ['creditor_id'])

    # Court Cases
    op.create_table(
        'court_cases',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('case_number', sa.String(120)),
        sa.Column('court_name', sa.String(255)),
        sa.Column('creditor_id', sa.Integer()),
        sa.Column('case_type', sa.String(100)),
        sa.Column('plaintiff', sa.String(255)),
        sa.Column('defendant', sa.String(255)),
        sa.Column('subject', sa.Text()),
        sa.Column('decision', sa.Text()),
        sa.Column('decision_date', sa.DateTime()),
        sa.Column('is_final', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('source_url', sa.Text()),
        sa.Column('document_path', sa.String(500)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('case_number', name='uq_case_number'),
    )
    op.create_index('ix_case_creditor', 'court_cases', ['creditor_id'])

    # Credit Products
    op.create_table(
        'credit_products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('creditor_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(255)),
        sa.Column('interest_rate', sa.Float()),
        sa.Column('gpr', sa.Float()),
        sa.Column('gpr_calculated', sa.Float()),
        sa.Column('gpr_mismatch', sa.Boolean(), server_default=sa.text('0')),
        sa.Column('fees', sa.JSON()),
        sa.Column('illegal_fees', sa.JSON()),
        sa.Column('min_amount', sa.Float()),
        sa.Column('max_amount', sa.Float()),
        sa.Column('term_months', sa.Integer()),
        sa.Column('analyzed_date', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_product_creditor', 'credit_products', ['creditor_id'])


def downgrade():
    op.drop_table('credit_products')
    op.drop_table('court_cases')
    op.drop_table('unfair_clauses')
    op.drop_table('violations')
    op.drop_table('creditors')
