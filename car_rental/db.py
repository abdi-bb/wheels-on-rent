from flask_sqlalchemy import SQLAlchemy
import click


db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')
