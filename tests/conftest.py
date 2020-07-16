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
from flask_principal import Identity
from invenio_access import any_user
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def app(app):
    """Application factory fixture."""
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def input_draft():
    """Minimal draft data as dict coming from the external world."""
    return {
        "_access": {"metadata_restricted": False, "files_restricted": False},
        "_owners": [1],
        "_created_by": 1
    }


@pytest.fixture(scope="function")
def input_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "_access": {"metadata_restricted": False, "files_restricted": False},
        "_owners": [1],
        "_created_by": 1,
        "title": "A Romans story",
        "description": "A looong description full of lorem ipsums"
    }


@pytest.fixture(scope="function")
def fake_identity():
    """Fake identity providing `any_user` system role."""
    identity = Identity(1)
    identity.provides.add(any_user)

    return identity
