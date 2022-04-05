"""Basic DB scheme

Revision ID: 8f1574ced5a7
Revises: 
Create Date: 2022-04-05 16:53:11.675676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from app.core.model.seed import seed_data

revision = '8f1574ced5a7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('athlete',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
    sa.Column('last_modified', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('athlete_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=25), nullable=True),
    sa.Column('total_places', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=40), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('duration', sa.Time(), nullable=True),
    sa.Column('exp_level', sa.Integer(), nullable=True),
    sa.Column('time_created', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_update', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('athlete_roles_assoc',
    sa.Column('athlete_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('skill_level', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['athlete_id'], ['athlete.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['athlete_role.id'], ),
    sa.PrimaryKeyConstraint('athlete_id', 'role_id')
    )
    op.create_table('event_goalies',
    sa.Column('athlete_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['athlete_id'], ['athlete.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('athlete_id', 'event_id')
    )
    op.create_table('event_organizers',
    sa.Column('athlete_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['athlete_id'], ['athlete.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('athlete_id', 'event_id')
    )
    op.create_table('event_players',
    sa.Column('athlete_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['athlete_id'], ['athlete.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('athlete_id', 'event_id')
    )
    op.create_table('event_referees',
    sa.Column('athlete_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['athlete_id'], ['athlete.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('athlete_id', 'event_id')
    )
    # ### end Alembic commands ###
    seed_data()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event_referees')
    op.drop_table('event_players')
    op.drop_table('event_organizers')
    op.drop_table('event_goalies')
    op.drop_table('athlete_roles_assoc')
    op.drop_table('event')
    op.drop_table('athlete_role')
    op.drop_table('athlete')
    # ### end Alembic commands ###