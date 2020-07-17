# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs"""

import json

from invenio_db import db
from invenio_records.api import Record
from invenio_records.models import RecordMetadataBase
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies.records import RecordPermissionPolicy
from invenio_records_resources.services import RecordService, \
    RecordServiceConfig

from invenio_drafts_resources.drafts import DraftBase, DraftMetadataBase
from invenio_drafts_resources.services import DraftService, DraftServiceConfig

HEADERS = {"content-type": "application/json", "accept": "application/json"}


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


class CustomDraftServiceConfig(DraftServiceConfig):
    """Custom draft service config."""
    draft_cls = CustomDraft
    record_cls = CustomRecord
    permission_policy_cls = AnyUserPermissionPolicy


def test_create_draft_of_new_record(app, input_draft, fake_identity):
    """Test draft creation of a non-existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    draft_service = DraftService(config=CustomDraftServiceConfig)

    identified_draft = draft_service.create_new(
        data=input_draft, identity=fake_identity
    )

    assert identified_draft.id

    for key, value in input_draft.items():
        assert identified_draft.draft[key] == value


def test_create_draft_of_existing_record(app, input_record, fake_identity):
    """Test draft creation of an existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    # Create new record
    record_service = RecordService(config=CustomRecordServiceConfig)
    identified_record = record_service.create(
        data=input_record, identity=fake_identity
    )

    recid = identified_record.id
    assert recid

    for key, value in input_record.items():
        assert identified_record.record[key] == value

    # Create new draft of said record
    input_record['title'] = "Edited title"
    draft_service = DraftService(config=CustomDraftServiceConfig)
    identified_draft = draft_service.create_from(
        data=input_record,
        identity=fake_identity,
        id_=recid
    )

    assert identified_draft.id == recid

    for key, value in input_record.items():
        assert identified_draft.draft[key] == value
