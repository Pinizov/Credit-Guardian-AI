"""Add User and Contract models

Revision ID: 0002
Revises: 0001
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('egn', sa.String(length=10), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_email', 'users', ['email'])
    op.create_index('ix_user_egn', 'users', ['egn'])
    
    # Create contracts table
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('creditor_id', sa.Integer(), nullable=True),
        sa.Column('contract_number', sa.String(length=50), nullable=True),
        sa.Column('creditor_name', sa.String(length=255), nullable=False),
        sa.Column('creditor_eik', sa.String(length=20), nullable=True),
        sa.Column('principal', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('interest_rate', sa.Float(), nullable=True),
        sa.Column('stated_apr', sa.Float(), nullable=True),
        sa.Column('calculated_apr', sa.Float(), nullable=True),
        sa.Column('contract_date', sa.DateTime(), nullable=True),
        sa.Column('maturity_date', sa.DateTime(), nullable=True),
        sa.Column('term_months', sa.Integer(), nullable=True),
        sa.Column('total_owed', sa.Float(), nullable=True),
        sa.Column('total_paid', sa.Float(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('document_text', sa.Text(), nullable=True),
        sa.Column('document_path', sa.String(length=500), nullable=True),
        sa.Column('analysis_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('analysis_result', sa.JSON(), nullable=True),
        sa.Column('ai_model_used', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contract_user', 'contracts', ['user_id'])
    op.create_index('ix_contract_creditor', 'contracts', ['creditor_id'])
    op.create_index('ix_contract_number', 'contracts', ['contract_number'])
    op.create_index('ix_contract_status', 'contracts', ['analysis_status'])
    
    # Create fees table
    op.create_table(
        'fees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('fee_type', sa.String(length=100), nullable=False),
        sa.Column('fee_amount', sa.Float(), nullable=False),
        sa.Column('fee_date', sa.DateTime(), nullable=True),
        sa.Column('is_illegal', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('legal_basis', sa.String(length=255), nullable=True),
        sa.Column('paid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fee_contract', 'fees', ['contract_id'])
    op.create_index('ix_fee_illegal', 'fees', ['is_illegal'])
    
    # Create contract_violations table
    op.create_table(
        'contract_violations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('violation_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('legal_basis', sa.String(length=255), nullable=True),
        sa.Column('financial_impact', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contract_violation_contract', 'contract_violations', ['contract_id'])
    op.create_index('ix_contract_violation_severity', 'contract_violations', ['severity'])
    
    # Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('complaint_type', sa.String(length=50), nullable=False, server_default='КЗП'),
        sa.Column('complaint_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('submitted_date', sa.DateTime(), nullable=True),
        sa.Column('response_date', sa.DateTime(), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_complaint_user', 'complaints', ['user_id'])
    op.create_index('ix_complaint_contract', 'complaints', ['contract_id'])
    op.create_index('ix_complaint_status', 'complaints', ['status'])
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_amount', sa.Float(), nullable=False),
        sa.Column('payment_type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payment_contract', 'payments', ['contract_id'])
    op.create_index('ix_payment_date', 'payments', ['payment_date'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_payment_date', 'payments')
    op.drop_index('ix_payment_contract', 'payments')
    op.drop_table('payments')
    
    op.drop_index('ix_complaint_status', 'complaints')
    op.drop_index('ix_complaint_contract', 'complaints')
    op.drop_index('ix_complaint_user', 'complaints')
    op.drop_table('complaints')
    
    op.drop_index('ix_contract_violation_severity', 'contract_violations')
    op.drop_index('ix_contract_violation_contract', 'contract_violations')
    op.drop_table('contract_violations')
    
    op.drop_index('ix_fee_illegal', 'fees')
    op.drop_index('ix_fee_contract', 'fees')
    op.drop_table('fees')
    
    op.drop_index('ix_contract_status', 'contracts')
    op.drop_index('ix_contract_number', 'contracts')
    op.drop_index('ix_contract_creditor', 'contracts')
    op.drop_index('ix_contract_user', 'contracts')
    op.drop_table('contracts')
    
    op.drop_index('ix_user_egn', 'users')
    op.drop_index('ix_user_email', 'users')
    op.drop_table('users')
