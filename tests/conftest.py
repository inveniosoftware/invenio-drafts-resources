# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_api as _create_api

pytest_plugins = ("celery.contrib.pytest", )


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        'invenio_db.model': [
            'mock_module = mock_module.models',
        ],
        'invenio_jsonschemas.schemas': [
            'mock_module = mock_module.jsonschemas',
        ],
        'invenio_search.mappings': [
            'draftsresources = mock_module.mappings',
        ]
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_api


@pytest.fixture()
def input_data():
    """Input data (as coming from the view layer).

    Most tests don't care about files, so files are disabled in the fixture.
    """
    return {
        'metadata': {
            'title': 'Test'
        },
        'files': {
            'enabled': False
        }
    }
