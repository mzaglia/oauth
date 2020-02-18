import click
from flask.cli import FlaskGroup, with_appcontext

from . import create_app
from .config import Config


def create_cli(create_app=None):
    """Define a Wrapper creation of Flask App in order to attach into flask click.
    Args:
         create_app (function) - Create app factory (Flask)
    """
    def create_cli_app(info):
        """Describe flask factory to create click command."""
        if create_app is None:
            info.create_app = None

            app = info.load_app()
        else:
            app = create_app()

        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app)
    def cli(**params):
        """Command line interface for bdc_collection_builder."""
        pass

    return cli


cli = create_cli(create_app=create_app)
