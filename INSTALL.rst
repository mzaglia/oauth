..
    This file is part of OBT OAuth 2.0.
    Copyright (C) 2019-2020 INPE.

    OBT OAuth 2.0 is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Installation
============

Clone the software repository:

.. code-block:: shell

        $ git clone https://github.com/brazil-data-cube/bdc-oauth.git


Go to the source code folder:

.. code-block:: shell

        $ cd bdc-oauth


Install in development mode:

.. code-block:: shell

        $ pip3 install -e .[all]


Generate the documentation:

.. code-block:: shell

        $ python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under:

.. code-block:: shell

    doc/sphinx/_build/html/
