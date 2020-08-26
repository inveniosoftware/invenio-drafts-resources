# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs"""

import time

import pytest
from invenio_pidstore.models import PIDStatus
from invenio_search import current_search
from sqlalchemy.orm.exc import NoResultFound


def _create_and_publish(draft_service, input_record, fake_identity):
    """Creates a draft and publishes it."""
    # Cannot create with record service due to the lack of versioning
    identified_draft = draft_service.create(
        data=input_record, identity=fake_identity
    )

    identified_record = draft_service.publish(
        id_=identified_draft.id, identity=fake_identity
    )

    assert identified_record.id == identified_draft.id
    assert identified_record.record.revision_id == 0

    return identified_record


def test_create_new_record_draft(app, draft_service, input_draft,
                                 fake_identity):
    """Test draft creation of a non-existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    identified_draft = draft_service.create(
        data=input_draft, identity=fake_identity
    )

    assert identified_draft.id

    for key, value in input_draft.items():
        assert identified_draft.record[key] == value

    # Check for pid and parent pid
    assert identified_draft.record['recid']
    assert identified_draft.record['conceptrecid']

    for pid in identified_draft.pids:
        assert pid.status == PIDStatus.RESERVED


def test_create_publish_new_record_draft(app, draft_service, input_record,
                                         fake_identity):
    """Test draft creation and publishing of a non-existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    identified_record = _create_and_publish(
        draft_service, input_record, fake_identity)

    for pid in identified_record.pids:
        assert pid.status == PIDStatus.REGISTERED

    for key, value in input_record.items():
        assert identified_record.record[key] == value

    # Check draft deletion
    # TODO: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        # NOTE: Draft and Record have the same `id`
        identified_draft = draft_service.read_draft(
            fake_identity, identified_record.id
        )

    # Test record exists
    identified_record = draft_service.read(
        fake_identity, identified_record.id
    )

    assert identified_record.id
    for pid in identified_record.pids:
        assert pid.status == PIDStatus.REGISTERED

    for key, value in input_record.items():
        assert identified_record.record[key] == value


def test_create_publish_record_new_revision(app, draft_service, input_record,
                                            fake_identity):
    """Test draft creation of an existing record and publish it."""
    # Needs `app` context because of invenio_access/permissions.py#166
    identified_record = _create_and_publish(
        draft_service, input_record, fake_identity)

    recid = identified_record.id

    # FIXME: Allow ES to clean deleted documents.
    # Flush is not the same. Default collection time is 1 minute.
    time.sleep(70)

    # Create new draft of said record
    orig_title = input_record['title']
    input_record['title'] = "Edited title"
    identified_draft = draft_service.edit(
        data=input_record,
        identity=fake_identity,
        id_=recid
    )

    assert identified_draft.id == recid
    assert identified_draft.record.revision_id == 0

    # Check the actual record was not modified
    identified_record = draft_service.read(id_=recid, identity=fake_identity)
    assert identified_record.record['title'] == orig_title

    # Publish it to check the increment in version_id
    identified_record = draft_service.publish(
        id_=identified_draft.id, identity=fake_identity
    )

    assert identified_record.id == recid
    assert identified_record.record.revision_id == 1
    assert identified_record.record['title'] == input_record['title']

    # Check it was actually edited
    identified_record = draft_service.read(id_=recid, identity=fake_identity)
    assert identified_record.record['title'] == input_record['title']


def test_create_publish_record_new_version(app, draft_service, input_record,
                                           fake_identity):
    """Creates a new version of a record.

    Publishes the draft to obtain 2 versions of a record.
    """
    # Needs `app` context because of invenio_access/permissions.py#166
    identified_record_1 = _create_and_publish(
        draft_service, input_record, fake_identity)

    # Create new version
    identified_draft_2 = draft_service.new_version(
        id_=identified_record_1.id, identity=fake_identity
    )

    assert identified_draft_2.record.revision_id == 0

    # Publish it
    identified_record_2 = draft_service.publish(
        id_=identified_draft_2.id, identity=fake_identity
    )

    assert identified_record_2.id
    for pid in identified_record_2.pids:
        assert pid.status == PIDStatus.REGISTERED

    assert identified_record_2.record.revision_id == 0

    assert identified_record_1.record['conceptrecid'] == \
        identified_record_2.record['conceptrecid']
    assert identified_record_1.record['recid'] != \
        identified_record_2.record['recid']
