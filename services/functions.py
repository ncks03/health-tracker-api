from datetime import date
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from alembic.config import Config

from main import get_db
db = get_db()

# Alembic upgrade for main script
def run_migrations_online():
    """
    Run migrations in 'online' mode.
    In this scenario, we need to create an Engine and associate a connection with the context.
    """
    configuration = Config("alembic.ini")
    fileConfig(configuration.config_file_name)

    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Functions
def calculate_age(born):
    today = date.today()
    print(today)
    birth_date = date(year=int(born[0:4]), month=int(born[5:7]), day=int(born[8:10]))
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def calculate_daily_calorie_intake():
    pass