#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import click
from flask.cli import FlaskGroup

from . import app


def create_cli():
    """Define a Wrapper creation of Flask App in order to attach into flask click.
    Args:
         create_app (function) - Create app factory (Flask)
    """
    def create_cli_app():
        """Describe flask factory to create click command."""
        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app)
    def cli(**params):
        """Command line interface for bdc_oauth."""
        pass

    return cli


cli = create_cli()
