from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5db2586a83e6'
down_revision = '5db2586a83e7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('booking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day', sa.String(length=10), nullable=False),
    sa.Column('hour', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=25), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.Constraint('teacher')
    )

    op.create_table('request',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hour', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=25), nullable=False),
    sa.Column('goal_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.Constraint('goal')
    )

    op.create_table('goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('alias', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('alias')
    )

    op.create_table('teachers_goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('teacher_id', sa.String(length=255), nullable=False),
    sa.Column('goal_id', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.Constraint('teacher'),
    sa.Constraint('goal')
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('booking')
    op.drop_table('request')
    op.drop_table('goals')
    # ### end Alembic commands ###
