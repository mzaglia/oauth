#
# This file is part of OBT OAuth 2.0.
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

import unittest
from bdc_oauth.utils.helpers import random_string


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.key = random_string(20)

    def test_random_string_size(self):
        self.assertEqual(40, len(self.key))

    def test_random_string_type(self):
        self.assertIsInstance(self.key, str)

    def test_random_string_error(self):
        self.assertNotEqual(22, len(self.key))
  