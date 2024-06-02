from __future__ import with_statement

import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Retrieve the database URL from the Flask application configuration
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.get_engine().url).replace(
        '%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    In this mode, a connection to the database is not established, and
    migrations are generated based solely on the metadata.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this mode, a connection to the database is established, and
    migrations are executed against the actual database.
    """
    def process_revision_directives(context, revision, directives):
        """
        Callback function to prevent auto-generation of migrations
        when there are no changes to the schema.
        """
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = current_app.extensions['migrate'].db.get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            **current_app.extensions['migrate'].configure_args
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
