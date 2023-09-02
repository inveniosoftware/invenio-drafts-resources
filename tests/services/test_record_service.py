# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service tests.

Test to add:
- Read a tombstone page
- Read with missing permissions
- Read with missing pid
"""

import pytest
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError, PIDUnregistered
from invenio_pidstore.models import PIDStatus
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from .utils import create_and_publish

#
# Operations tests
#


def test_create_draft(app, service, identity_simple, input_data):
    """Test draft creation of a non-existing record."""
    draft = service.create(identity_simple, input_data)
    draft_dict = draft.to_dict()

    assert draft.id

    for key, value in input_data.items():
        assert draft[key] == value

    # Check for pid and parent pid
    assert draft["id"]
    assert draft["parent"]["id"]
    assert draft["is_published"] is False
    assert draft["versions"]["is_latest_draft"] is True
    assert draft["versions"]["is_latest"] is False
    assert "errors" not in draft_dict


def test_create_empty_draft(app, service, identity_simple):
    """Test an empty draft can be created.

    Errors (missing required fields) are reported, but don't prevent creation.
    """
    input_data = {"metadata": {}}

    draft = service.create(identity_simple, input_data)
    draft_dict = draft.to_dict()

    assert draft["id"]
    assert draft["is_published"] is False
    assert draft_dict["errors"][0]["field"] == "metadata.title"


def test_read_draft(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    assert draft.id

    draft_2 = service.read_draft(identity_simple, draft.id)
    assert draft.id == draft_2.id


def test_update_draft(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    assert draft.id

    orig_title = input_data["metadata"]["title"]
    edited_title = "Edited title"
    input_data["metadata"]["title"] = edited_title

    # Update draft content
    update_draft = service.update_draft(identity_simple, draft.id, input_data)
    assert update_draft["metadata"]["title"] == edited_title
    assert draft.id == update_draft.id

    # Check the updates where saved
    update_draft = service.read_draft(identity_simple, draft.id)
    assert draft.id == update_draft.id
    assert update_draft["metadata"]["title"] == edited_title


def test_update_draft_invalid_field(app, service, identity_simple, input_data):
    """Update with invalid field reports rather than raises errors."""
    draft = service.create(identity_simple, input_data)
    orig_title = input_data["metadata"]["title"]
    edited_title = 100
    input_data["metadata"]["title"] = edited_title

    updated_draft = service.update_draft(identity_simple, draft.id, input_data)
    updated_draft_dict = updated_draft.to_dict()

    assert draft.id == updated_draft.id
    assert "title" not in updated_draft["metadata"]
    assert updated_draft_dict["errors"][0]["field"] == "metadata.title"


def test_delete_draft(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    assert draft.id

    assert service.delete_draft(identity_simple, draft.id)

    # Check draft deletion
    with pytest.raises(PIDDoesNotExistError):
        # NOTE: Draft and Record have the same `id`
        service.read_draft(identity_simple, draft.id)


def test_publish_draft(app, service, identity_simple, input_data):
    """Test draft publishing of a non-existing record.

    Note that the publish action requires a draft to be created first.
    """
    # Needs `app` context because of invenio_access/permissions.py#166
    record = create_and_publish(service, identity_simple, input_data)
    assert record._record.pid.status == PIDStatus.REGISTERED
    assert record._record.parent.pid.status == PIDStatus.REGISTERED

    for key, value in input_data.items():
        assert record[key] == value

    # Check draft deletion
    with pytest.raises(NoResultFound):
        # NOTE: Draft and Record have the same `id`
        draft = service.read_draft(identity_simple, record.id)

    # Test record exists
    record = service.read(identity_simple, record.id)

    assert record.id
    assert record._record.pid.status == PIDStatus.REGISTERED
    assert record._record.parent.pid.status == PIDStatus.REGISTERED

    for key, value in input_data.items():
        assert record[key] == value


def test_fail_to_publish_invalid_draft(app, service, identity_simple):
    """Publishing an incomplete draft should fail.

    Note that the publish action requires a draft to be created first.
    """
    # Needs `app` context because of invenio_access/permissions.py#166
    input_data = {"metadata": {}}
    draft = service.create(identity_simple, input_data)

    with pytest.raises(ValidationError) as e:
        record = service.publish(identity_simple, draft.id)

    exception = e.value
    assert "metadata" not in exception.valid_data

    # Draft still there
    draft = service.read_draft(identity_simple, draft.id)
    assert draft
    assert draft._record.pid.status == PIDStatus.NEW
    assert draft._record.parent.pid.status == PIDStatus.NEW

    # Test no published record exists
    with pytest.raises(PIDUnregistered) as e:
        record = service.read(identity_simple, draft.id)


#
# Flow tests (Note that operations are tested above
# therefore these tests do not assert their output)
#


def test_create_publish_new_revision(app, service, identity_simple, input_data):
    """Test creating a new revision of a record.

    This tests the `edit` service method.
    """
    # Needs `app` context because of invenio_access/permissions.py#166
    record = create_and_publish(service, identity_simple, input_data)
    recid = record.id

    # Create new draft of said record
    draft = service.edit(identity_simple, recid)
    assert draft.id == recid
    assert draft._record.fork_version_id == record._record.revision_id
    # create, soft-delete, undelete, update
    assert draft._record.revision_id == 5

    # Update the content
    orig_title = input_data["metadata"]["title"]
    edited_title = "Edited title"
    input_data["metadata"]["title"] = edited_title

    update_draft = service.update_draft(identity_simple, draft.id, input_data)

    # Check the actual record was not modified
    record = service.read(identity_simple, recid)
    assert record["metadata"]["title"] == orig_title

    # Publish it to check the increment in version_id
    record = service.publish(identity_simple, recid)

    assert record.id == recid
    assert record._record.revision_id == 2
    assert record["metadata"]["title"] == edited_title

    # Check it was actually edited
    record = service.read(identity_simple, recid)
    assert record["metadata"]["title"] == edited_title


def test_multiple_edit(app, service, identity_simple, input_data):
    """Test the revision_id when editing record multiple times..

    This tests the `edit` service method.
    """
    # Needs `app` context because of invenio_access/permissions.py#166
    record = create_and_publish(service, identity_simple, input_data)
    recid = record.id

    # Create new draft of said record
    draft = service.edit(identity_simple, recid)
    assert draft.id == recid
    assert draft._record.fork_version_id == record._record.revision_id
    assert draft._record.revision_id == 5

    draft = service.edit(identity_simple, recid)
    assert draft.id == recid
    assert draft._record.fork_version_id == record._record.revision_id
    assert draft._record.revision_id == 5

    # Publish it to check the increment in version_id
    record = service.publish(identity_simple, recid)

    draft = service.edit(identity_simple, recid)
    assert draft.id == recid
    assert draft._record.fork_version_id == record._record.revision_id
    assert draft._record.revision_id == 8  # soft-delete, undelete, update


def test_create_publish_new_version(app, service, identity_simple, input_data):
    """Test creating a new version of a record.

    This tests the `new_version` service method.
    """
    record = create_and_publish(service, identity_simple, input_data)
    recid = record.id

    # Create new version
    draft = service.new_version(identity_simple, recid)

    assert draft._record.revision_id == 2
    assert draft["id"] != record["id"]
    assert draft._record.pid.status == PIDStatus.NEW
    assert draft._record.parent.pid.status == PIDStatus.REGISTERED

    # Re-disable files
    input_data["files"] = {"enabled": False}
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Publish it
    record_2 = service.publish(identity_simple, draft.id)

    assert record_2.id
    assert record_2._record.pid.status == PIDStatus.REGISTERED
    assert record_2._record.parent.pid.status == PIDStatus.REGISTERED
    assert record_2._record.revision_id == 1
    assert record_2["id"] != record["id"]


def test_multi_version_delete_draft(app, service, identity_simple, input_data):
    """Test deleting drafts of a multi-version record.

    Both individual version PIDs and parent PID should stay 'REGISTERED' when deleting
    drafts of a multi-version record.
    """
    record = create_and_publish(service, identity_simple, input_data)
    recid_v1 = record.id

    def assert_record_pids_status(recid):
        record = service.read(identity_simple, recid)
        assert record._record.pid.status == PIDStatus.REGISTERED
        assert record._record.parent.pid.status == PIDStatus.REGISTERED

    # Edit record v1
    draft = service.edit(identity_simple, recid_v1)
    assert_record_pids_status(recid_v1)

    # Delete edit draft of record v1
    service.delete_draft(identity_simple, draft.id)
    assert_record_pids_status(recid_v1)

    # Create new version (v2)
    draft = service.new_version(identity_simple, recid_v1)
    assert_record_pids_status(recid_v1)

    # Delete new version (v2) draft
    service.delete_draft(identity_simple, draft.id)
    assert_record_pids_status(recid_v1)

    # Create new version (v2) and publish
    draft = service.new_version(identity_simple, recid_v1)
    record_v2 = service.publish(identity_simple, draft.id)
    recid_v2 = record_v2.id
    assert_record_pids_status(recid_v1)
    assert_record_pids_status(recid_v2)

    # Edit both record v1 and v2
    draft_v1 = service.edit(identity_simple, recid_v1)
    draft_v2 = service.edit(identity_simple, recid_v2)
    assert_record_pids_status(recid_v1)
    assert_record_pids_status(recid_v2)

    # Delete draft v1
    service.delete_draft(identity_simple, draft_v1.id)
    assert_record_pids_status(recid_v1)
    assert_record_pids_status(recid_v2)

    # Delete draft v2
    service.delete_draft(identity_simple, draft_v2.id)
    assert_record_pids_status(recid_v1)
    assert_record_pids_status(recid_v2)


def test_read_latest_version(app, service, identity_simple, input_data):
    """Test read the latest version of a record.

    This tests the `read_latest` service method.
    """
    record = create_and_publish(service, identity_simple, input_data)
    recid = record.id
    parent_recid = record.data["parent"]["id"]

    # Create new version
    draft = service.new_version(identity_simple, recid)

    # Re-disable files
    input_data["files"] = {"enabled": False}
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Publish it
    record_2 = service.publish(identity_simple, draft.id)
    recid_2 = record_2.id

    latest = service.read_latest(identity_simple, recid)
    assert latest["id"] == recid_2
    latest = service.read_latest(identity_simple, recid_2)
    assert latest["id"] == recid_2
    # Check that parent returns latest version
    latest = service.read_latest(identity_simple, parent_recid)
    assert latest["id"] == recid_2
