# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Drafts Resources module to create REST APIs"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "pytest-invenio>=1.3.2",
    "invenio-app>=1.3.0",
    "pytest>=4.6.1,<6.0.0"
]

# Should follow inveniosoftware/invenio versions
invenio_search_version = '>=1.2.0,<2.0.0'
invenio_db_version = '>=1.0.4,<2.0.0'

extras_require = {
    "docs": ["Sphinx>=1.5.1,<3"],
    # Elasticsearch version
    'elasticsearch6': [
        'invenio-search[elasticsearch6]{}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]{}'.format(invenio_search_version),
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql,versioning]{}'.format(invenio_db_version),
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]{}'.format(invenio_db_version),
    ],
    'sqlite': [
        'invenio-db[versioning]{}'.format(invenio_db_version),
    ],
    "tests": tests_require,
}

all_requires = []
for key, reqs in extras_require.items():
    if key in {"elasticsearch6", "elasticsearch7"}:
        continue
    all_requires.extend(reqs)
extras_require["all"] = all_requires

setup_requires = [
    "Babel>=1.3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "Flask-BabelEx>=0.9.4",
    "flask-resources>=0.2.1,<1.0.0",
    "invenio-base>=1.2.3",
    "invenio_pidrelations>=v1.0.0a7,<2.0.0",
    "invenio-pidstore>=1.2.1",
    "invenio-indexer>=1.1.1",
    "invenio-records>=1.3.2",
    "invenio-records-resources>=0.4.2,<0.5.0",
    "invenio-accounts>=1.3.0",
    "invenio-files-rest>=1.2.0",
    "invenio-records-permissions>=0.9.0",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_drafts_resources", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-drafts-resources",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio TODO",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/Invenio-Drafts-Resources",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "invenio_drafts_resources = invenio_drafts_resources:InvenioDraftsResources",
        ],
        "invenio_base.api_apps": [
            "invenio_drafts_resources = invenio_drafts_resources:InvenioDraftsResources",
        ],
        'invenio_config.module': [
            'invenio_drafts_resources = invenio_drafts_resources.config',
        ],
        "invenio_i18n.translations": ["messages = invenio_drafts_resources",],
        'invenio_db.models': [
            'invenio_drafts_resources = invenio_drafts_resources.drafts.models',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 1 - Planning",
    ],
)
