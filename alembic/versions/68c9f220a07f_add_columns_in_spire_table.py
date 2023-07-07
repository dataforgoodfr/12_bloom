"""add columns in spire table

Revision ID: 68c9f220a07f
Revises: 1fd83d22bd1e
Create Date: 2023-07-07 11:15:16.516122

"""


# revision identifiers, used by Alembic.
revision = "68c9f220a07f"
down_revision = "1fd83d22bd1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass

    # taille : VesselStaticData -> VesselDimensions -> length, width (Int) ,
    # voyage (destination: String , draught: Float eta: DateTime)
    # rm : fishing, at_port, port_name, status


def downgrade() -> None:
    pass
