#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import json
from fixture import test_client

def test_status_page(test_client):
    response = test_client.get('/oauth/')
    assert response.status_code == 200
    r_json = json.loads(response.data)
    assert 'description' in r_json
    assert r_json['version'] == '0.4.0'