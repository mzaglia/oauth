#
# This file is part of OBT OAuth 2.0
# Copyright (C) 2019-2020 INPE.
#
# OBT OAuth 2.0 free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""OBT OAuth 2.0"""

import os
from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

docs_require = [
    'Sphinx>=2.2',
]

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40',
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = [ req for exts, reqs in extras_require.items() for req in reqs ]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'bdc-core @ git+git://github.com/brazil-data-cube/bdc-core.git@v0.2.0#egg=bdc-core',
    'Flask>=1.0.3',
    'flask_bcrypt==0.7.1',
    'flask_restplus==0.12.1',
    'Flask-Cors==3.0.8',
    'Flask-JWT==0.3.2',
    'Flask-RESTful==0.3.6',
    'pytz==2017.3',
    'six==1.12.0',
    'requests==2.20.0',
    'workalendar==2.3.1',
    'marshmallow==2.15.1',
    'cerberus==1.3.1',
    'pymongo==3.8.0',
    'flask_pymongo==2.3.0',
    'flask_redis==0.4.0',
    'cryptography==2.7',
    'flask-redoc==0.1.0',
    'elastic-apm[flask]==5.6.0'
]

packages = find_packages()

with open(os.path.join('bdc_oauth', 'version.py'), 'rt') as fp:
    g = {}
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='bdc-oauth',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='INPE - OBT OAuth 2.0',
    license='MIT',
    author='INPE',
    author_email='gribeiro@dpi.inpe.br',
    url='https://github.com/brazil-data-cube/bdc-ouath.py',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            'bdc-oauth = bdc_oauth.cli:cli'
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)