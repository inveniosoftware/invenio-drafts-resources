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
from invenio_db import db
from invenio_records.api import Record
from invenio_records.models import RecordMetadataBase
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies.records import RecordPermissionPolicy
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.services import RecordService, \
    RecordServiceConfig

from invenio_drafts_resources.drafts import DraftBase, DraftMetadataBase
from invenio_drafts_resources.resources import DraftResource
from invenio_drafts_resources.services import RecordDraftService, \
    RecordDraftServiceConfig


class AnyUserPermissionPolicy(RecordPermissionPolicy):
    """Custom permission policy."""

    can_list = [AnyUser()]
    can_create = [AnyUser()]
    can_read = [AnyUser()]
    can_update = [AnyUser()]
    can_delete = [AnyUser()]
    can_read_files = [AnyUser()]
    can_update_files = [AnyUser()]


class CustomDraftMetadata(db.Model, DraftMetadataBase):
    """Represent a custom draft metadata."""

    __tablename__ = 'custom_drafts_metadata'


class CustomDraft(DraftBase):
    """Custom draft API."""

    model_cls = CustomDraftMetadata


class CustomRecordMetadata(db.Model, RecordMetadataBase):
    """Represent a custom draft metadata."""

    __tablename__ = 'custom_record_metadata'


class CustomRecord(Record):
    """Custom draft API."""

    model_cls = CustomRecordMetadata


class CustomRecordServiceConfig(RecordServiceConfig):
    """Custom draft service config."""

    record_cls = CustomRecord
    permission_policy_cls = AnyUserPermissionPolicy


class CustomRecordDraftServiceConfig(RecordDraftServiceConfig):
    """Custom draft service config."""

    draft_cls = CustomDraft
    record_cls = CustomRecord
    permission_policy_cls = AnyUserPermissionPolicy


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def app(app):
    """Application factory fixture."""
    with app.app_context():
        record_bp = RecordResource(
            service=RecordService(config=CustomRecordServiceConfig)
        ).as_blueprint("record_resource")
        draft_bp = DraftResource(
            service=RecordDraftService(config=CustomRecordDraftServiceConfig)
        ).as_blueprint("draft_resource")

        app.register_blueprint(record_bp)
        app.register_blueprint(draft_bp)
        yield app


@pytest.fixture(scope="module")
def draft_service():
    """Application factory fixture."""
    draft_service = RecordDraftService(config=CustomRecordDraftServiceConfig)

    return draft_service


@pytest.fixture(scope="module")
def record_service():
    """Application factory fixture."""
    record_service = RecordService(config=CustomRecordServiceConfig)

    return record_service


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
