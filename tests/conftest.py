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
from invenio_app.factory import create_api
from invenio_db import db
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies.records import RecordPermissionPolicy

from invenio_drafts_resources.drafts import DraftMetadataBase
from invenio_drafts_resources.resources import DraftResource
from invenio_drafts_resources.services import DraftService, DraftServiceConfig


class CustomDraftMetadata(db.Model, DraftMetadataBase):
    """Represent a custom draft metadata."""

    __tablename__ = 'custom_drafts_metadata'


class AnyUserPermissionPolicy(RecordPermissionPolicy):
    """Custom permission policy."""

    can_list = [AnyUser()]
    can_create = [AnyUser()]
    can_read = [AnyUser()]
    can_update = [AnyUser()]
    can_delete = [AnyUser()]
    can_read_files = [AnyUser()]
    can_update_files = [AnyUser()]


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def app(app):
    """Application factory fixture."""
    DraftServiceConfig.permission_policy_cls = AnyUserPermissionPolicy
    DraftService.config = DraftServiceConfig
    custom_bp = DraftResource(
        service=DraftService()).as_blueprint("base_resource")
    app.register_blueprint(custom_bp)
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
