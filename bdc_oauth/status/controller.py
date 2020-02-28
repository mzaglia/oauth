#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

from bdc_core.utils.flask import APIResource

from bdc_oauth import __version__
from bdc_oauth.status import ns

api = ns

@api.route('/')
class StatusController(APIResource):
    
    def get(self):
        """
        Returns application status
        """
        return {
            'version': __version__,
            'message': 'Running',
            'description': 'Brazil Data Cube Project (http://brazildatacube.org)'
        }
        