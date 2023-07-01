# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
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

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from invenio_files_rest.errors import BucketLockedError, InvalidOperationError
from invenio_files_rest.models import Bucket, FileInstance, ObjectVersion
from invenio_records_resources.services.files.transfer import TransferType
from marshmallow.exceptions import ValidationError
from mock_module.models import DraftMetadata, FileDraftMetadata, FileRecordMetadata
from mock_module.permissions import PermissionPolicy
from mock_module.service import ServiceConfig

from invenio_drafts_resources.services import RecordService


#
# Fixtures
#
@pytest.fixture()
def input_data(input_data):
    """Enable files."""
    input_data["files"]["enabled"] = True
    input_data["media_files"] = {"enabled": False}
    return input_data


@pytest.fixture(scope="module")
def service(file_service, draft_file_service):
    """Service instance."""
    return RecordService(
        ServiceConfig,
        files_service=file_service,
        draft_files_service=draft_file_service,
    )


@pytest.fixture(scope="module")
def base_app(
    base_app,
    service,
    file_service,
    draft_file_service,
    service_with_media_files,
    media_file_service,
    media_draft_file_service,
):
    """Application factory fixture."""
    registry = base_app.extensions["invenio-records-resources"].registry
    registry.register(service, service_id="mock-records-service")
    registry.register(service, service_id="mock-records-media-files,service")
    registry.register(file_service, service_id="mock-files-service")
    registry.register(draft_file_service, service_id="mock-draftfiles-service")
    registry.register(
        service_with_media_files, service_id="mock-record-media-files-service"
    )
    registry.register(media_draft_file_service, service_id="mock-draft-media-files")
    registry.register(media_file_service, service_id="mock-media-files-service")
    yield base_app


#
# Helpers
#
def add_file_to_draft(draft_file_service, draft_id, file_id, identity):
    """Add a file to the record."""
    draft_file_service.init_files(identity, draft_id, data=[{"key": file_id}])
    draft_file_service.set_file_content(
        identity, draft_id, file_id, BytesIO(b"test file content")
    )
    result = draft_file_service.commit_file(identity, draft_id, file_id)
    return result


def assert_counts(buckets=0, objs=0, fileinstances=0, filedrafts=0, filerecords=0):
    """Helper to assert counts of file related tables."""
    assert FileDraftMetadata.query.count() == filedrafts
    assert FileRecordMetadata.query.count() == filerecords
    assert Bucket.query.count() == buckets
    assert ObjectVersion.query.count() == objs
    assert FileInstance.query.count() == fileinstances


#
# Files tests (ensure proper management of all related objects)
#
def test_create_delete_draft(app, db, service, input_data, identity_simple):
    """Test creation and deletion of a draft."""
    assert_counts(buckets=0, objs=0, fileinstances=0, filedrafts=0)

    # Create draft
    draft = service.create(identity_simple, input_data)
    assert_counts(buckets=2, objs=0, fileinstances=0, filedrafts=0)

    # Add file
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=1)

    # Delete draft
    service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=0, objs=0, fileinstances=1, filedrafts=0)


def test_create_publish(app, db, service, input_data, identity_simple):
    """Test creation and publish of a draft."""
    # Create draft and file
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=1)

    # Publish
    record = service.publish(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)
    assert record._record.bucket.locked is True


def test_edit_delete(app, db, service, input_data, identity_simple, monkeypatch):
    """Test edit with delete of a published draft."""
    # Create and publish
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    record = service.publish(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)

    # Edit draft (when soft-deleted draft record exists)
    draft = service.edit(identity_simple, record.id)
    assert_counts(buckets=4, objs=2, fileinstances=1, filedrafts=1, filerecords=1)
    assert record._record.bucket.locked is True
    # we don't want to allow modifying files on the draft - go through new version
    assert draft._record.bucket.locked is True

    # Delete draft
    draft = service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)

    # Cleanup deleted drafts.
    c = DraftMetadata.query.filter(DraftMetadata.is_deleted == True).delete()  # noqa
    assert c == 1
    db.session.commit()

    # Search engine will complain if we try we don't wait a minute, so disable
    # the indexer.
    monkeypatch.setattr(service.config, "indexer_cls", MagicMock())

    # Edit draft (when no soft-deleted draft record exists)
    draft = service.edit(identity_simple, record.id)
    assert_counts(buckets=4, objs=2, fileinstances=1, filedrafts=1, filerecords=1)

    # Delete draft
    draft = service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)


def test_edit_delete_media_files(
    app, db, service, service_with_media_files, input_data, identity_simple, monkeypatch
):
    """Test edit with delete of a published draft."""
    input_data["media_files"] = {"enabled": True}
    # Create and publish
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    # add media file
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test2", identity_simple
    )
    record = service.publish(identity_simple, draft.id)
    assert_counts(buckets=2, objs=2, fileinstances=2, filedrafts=0, filerecords=1)

    # Edit draft (when soft-deleted draft record exists)
    draft = service.edit(identity_simple, record.id)

    assert_counts(buckets=4, objs=4, fileinstances=2, filedrafts=1, filerecords=1)
    assert record._record.bucket.locked is True
    # we don't want to allow modifying files on the draft - go through new version
    assert draft._record.bucket.locked is True
    # make sure we can modify media files
    assert draft._record.media_bucket.locked is False

    # Delete draft
    draft = service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=2, fileinstances=2, filedrafts=0, filerecords=1)

    # Cleanup deleted drafts.
    c = DraftMetadata.query.filter(DraftMetadata.is_deleted == True).delete()  # noqa
    assert c == 1
    db.session.commit()

    # Search engine will complain if we try we don't wait a minute, so disable
    # the indexer.
    monkeypatch.setattr(service.config, "indexer_cls", MagicMock())

    # Edit draft (when no soft-deleted draft record exists)
    draft = service.edit(identity_simple, record.id)
    assert_counts(buckets=4, objs=4, fileinstances=2, filedrafts=1, filerecords=1)

    # Delete draft
    draft = service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=2, fileinstances=2, filedrafts=0, filerecords=1)


def test_edit_publish(app, db, service, input_data, identity_simple, monkeypatch):
    """Test edit and publish."""
    # Create, publish and edit draft.
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    record = service.publish(identity_simple, draft.id)
    draft = service.edit(identity_simple, record.id)
    assert_counts(buckets=4, objs=2, fileinstances=1, filedrafts=1, filerecords=1)

    # Publish the edits
    record = service.publish(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)

    # Cleanup deleted drafts.
    c = DraftMetadata.query.filter(DraftMetadata.is_deleted == True).delete()  # noqa
    assert c == 1
    db.session.commit()

    # engine will complain if we try we don't wait a minute, so disable
    # the indexer.
    monkeypatch.setattr(service.config, "indexer_cls", MagicMock())

    # Edit
    draft = service.edit(identity_simple, record.id)
    assert_counts(buckets=4, objs=2, fileinstances=1, filedrafts=1, filerecords=1)

    # Publish
    record = service.publish(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=1, filedrafts=0, filerecords=1)


def test_edit_draft_files(
    app, db, service, service_with_media_files, input_data, identity_simple, monkeypatch
):
    """Test edit and publish."""
    input_data["media_files"] = {"enabled": True}
    # Create, publish and edit draft.
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test2", identity_simple
    )
    record = service.publish(identity_simple, draft.id)
    draft = service.edit(identity_simple, record.id)

    # expected to go via new version after initial publish
    with pytest.raises(BucketLockedError):
        add_file_to_draft(service.draft_files, draft.id, "test2", identity_simple)

    # add media file - the media files bucket should not be locked
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test23", identity_simple
    )


def test_new_version(app, db, service, input_data, identity_simple, monkeypatch):
    """Test new version."""
    # Create and publish
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    service.publish(identity_simple, draft.id)

    # New version
    draft = service.new_version(identity_simple, draft.id)
    assert_counts(buckets=4, objs=1, fileinstances=1, filedrafts=0, filerecords=1)

    # Add file
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    assert_counts(buckets=4, objs=2, fileinstances=2, filedrafts=1, filerecords=1)

    # Publish
    service.publish(identity_simple, draft.id)
    assert_counts(buckets=4, objs=2, fileinstances=2, filedrafts=0, filerecords=2)


def test_new_version_with_media_files(
    app, db, service, service_with_media_files, input_data, identity_simple, monkeypatch
):
    """Test new version."""
    # Create and publish
    input_data["media_files"] = {"enabled": True}
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test2", identity_simple
    )
    service.publish(identity_simple, draft.id)

    # New version
    draft = service.new_version(identity_simple, draft.id)

    # objects: 1 media file of the record + 1 file of the record
    # + 1 media file of the draft (copied to new version) = 3
    # file instances: 1 media file of the draft, 1 media file of the new version record
    assert_counts(buckets=4, objs=3, fileinstances=2, filedrafts=0, filerecords=1)

    # Add file
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    # add media file
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test23", identity_simple
    )

    # objects: added 1 file and 1 media file = 5
    assert_counts(buckets=4, objs=5, fileinstances=4, filedrafts=1, filerecords=1)

    # Publish
    service.publish(identity_simple, draft.id)
    assert_counts(buckets=4, objs=5, fileinstances=4, filedrafts=0, filerecords=2)


def test_new_version_delete(app, db, service, input_data, identity_simple):
    """Test new version."""
    # Create, publish, new_version, add_file
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    service.publish(identity_simple, draft.id)
    draft = service.new_version(identity_simple, draft.id)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    assert_counts(buckets=4, objs=2, fileinstances=2, filedrafts=1, filerecords=1)

    # Delete new version
    service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=1, fileinstances=2, filedrafts=0, filerecords=1)


def test_new_version_with_media_files_delete(
    app, db, service, service_with_media_files, input_data, identity_simple
):
    """Test new version."""
    # Create, publish, new_version, add_file
    input_data["media_files"] = {"enabled": True}
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test2", identity_simple
    )
    service.publish(identity_simple, draft.id)
    draft = service.new_version(identity_simple, draft.id)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    add_file_to_draft(
        service_with_media_files.draft_files, draft.id, "test23", identity_simple
    )

    # objects: 1 media file of the record + 1 file of the record
    #           + 1 media file of the draft (copied to new version) = 3
    #           + 1 media file in a new version + 1 regular file in a new version
    assert_counts(buckets=4, objs=5, fileinstances=4, filedrafts=1, filerecords=1)

    # Delete new version
    service.delete_draft(identity_simple, draft.id)
    assert_counts(buckets=2, objs=2, fileinstances=4, filedrafts=0, filerecords=1)


#
# Test import files
#
def test_import_files(app, db, service, input_data, identity_simple):
    """Test new version."""
    # Create, publish, new_version
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    service.publish(identity_simple, draft.id)
    draft = service.new_version(identity_simple, draft.id)
    assert_counts(buckets=4, objs=1, fileinstances=1, filedrafts=0, filerecords=1)

    # Import files
    service.import_files(identity_simple, draft.id)
    assert_counts(buckets=4, objs=2, fileinstances=1, filedrafts=1, filerecords=1)


def test_import_files_disabled(app, db, service, input_data, identity_simple):
    """Test new version."""
    # Create, publish, new_version
    input_data["files"]["enabled"] = False
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft = service.new_version(identity_simple, draft.id)
    assert_counts(buckets=4, objs=0, fileinstances=0, filedrafts=0, filerecords=0)

    with pytest.raises(ValidationError):
        service.import_files(identity_simple, draft.id)


#
# Default preview
#
def test_edit_publish_default_preview(app, service, input_data, identity_simple):
    """Test edit and publish."""
    # Create, publish and edit draft.
    input_data["media_files"] = {"enabled": False}
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, "test", identity_simple)
    record = service.publish(identity_simple, draft.id)
    draft = service.edit(identity_simple, record.id)
    assert "default_preview" not in draft.data["files"]

    # Set the default preview
    data = draft.to_dict()
    data["files"]["default_preview"] = "test"
    data["media_files"] = {"enabled": False}
    draft = service.update_draft(identity_simple, draft.id, data)
    # TODO: fails because it needs schema to load the value.
    assert draft.data["files"]["default_preview"] == "test"

    # Publish change
    record = service.publish(identity_simple, draft.id)
    assert record.data["files"]["default_preview"] == "test"


def test_update_draft_set_default_file_preview(
    app, location, service, identity_simple, input_data
):
    default_file = "file.txt"

    # Create and add file
    draft = service.create(identity_simple, input_data)
    add_file_to_draft(service.draft_files, draft.id, default_file, identity_simple)

    # Update draft to set default preview
    input_data["files"] = {"enabled": True, "default_preview": default_file}
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Default preview should have been updated
    assert draft.data["files"] == {"enabled": True, "default_preview": default_file}
    assert default_file == draft._record.files.default_preview


def test_update_draft_set_default_file_preview_reports_error(
    app, location, service, identity_simple, input_data
):
    # Create and add file
    draft = service.create(identity_simple, input_data)
    default_file = "file.txt"
    add_file_to_draft(service.draft_files, draft.id, default_file, identity_simple)

    # Fail to set default preview to invalid file
    input_data["files"] = {"enabled": True, "default_preview": "inexisting_file.txt"}
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Default preview should NOT be set
    assert draft.errors[0]["field"] == "files.default_preview"
    assert draft.errors[0]["messages"]
    assert draft.data["files"] == {"enabled": True}


@patch("invenio_records_resources.services.files.transfer.fetch_file")
def test_publish_with_fetch_files(
    p_fetch_file, app, service, draft_file_service, input_data, identity_simple
):
    """Tests wether it is possible to submit a record if the file isn't fully downloaded."""
    draft = service.create(identity_simple, input_data)  # 1
    file_to_initialise = [
        {
            "key": "article.txt",
            "uri": "https://inveniordm.test/files/article.txt",
            "storage_class": "F",
        }
    ]

    files = draft_file_service.init_files(
        identity_simple, draft.id, data=file_to_initialise
    )

    for file_record in files.entries:
        assert file_record["storage_class"] == TransferType.FETCH

    with pytest.raises(ValidationError):
        service.publish(identity_simple, draft.id)


#
# Files validation tests
#
def test_missing_files(app, service, identity_simple, input_data):
    # Test files.enabled = True when no files
    draft = service.create(identity_simple, input_data)
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Files should be enabled
    assert draft.data["files"]["enabled"] is True

    # Missing files should be reported
    assert draft.errors[0]["field"] == "files.enabled"
    assert "Missing uploaded files." in draft.errors[0]["messages"][0]


def test_disable_files_error(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    assert draft.data["files"]["enabled"] is True

    # Add a file
    add_file_to_draft(service.draft_files, draft.id, "file.txt", identity_simple)

    # Try to set files.enabled = False
    input_data = draft.data
    input_data["files"] = {"enabled": False}
    draft = service.update_draft(identity_simple, draft.id, input_data)

    # Should not be possible to disable files, when files exists
    assert draft.data["files"]["enabled"] is True

    # Error should be reported
    assert draft.errors[0]["field"] == "files.enabled"
    assert "delete all" in draft.errors[0]["messages"][0]


def test_fail_to_publish_draft_with_no_files(app, service, identity_simple, input_data):
    input_data["files"] = {"enabled": True}
    draft = service.create(identity_simple, input_data)

    with pytest.raises(ValidationError) as e:
        service.publish(identity_simple, draft.id)

    assert e.value.field_name == "files.enabled"
    files_missing_msg = e.value.messages
    assert files_missing_msg is not None


def test_fail_to_add_files_to_draft_with_files_disabled(
    app, service, identity_simple, input_data
):
    # NOTE: It is impossible to publish a draft with files but
    #       files.enabled = False, because can't set files.enabled = False
    #       in that case (as seen in test above) and files can't be
    #       added if files.enabled = False as we confirm below:
    input_data["files"]["enabled"] = False
    draft = service.create(identity_simple, input_data)

    with pytest.raises(InvalidOperationError):
        add_file_to_draft(service.draft_files, draft.id, "file.txt", identity_simple)


def test_manage_files_permissions(
    app, service, identity_simple, input_data, monkeypatch
):
    class ManageFilesPermissionPolicy(PermissionPolicy):
        can_manage_files = []

    monkeypatch.setattr(
        service.config,
        "permission_policy_cls",
        ManageFilesPermissionPolicy,
    )

    # Not modifying files options (i.e. sending `files.enabled: true`) doesn't error
    draft = service.create(identity_simple, input_data)
    assert not draft.errors

    # Modyfing/disabling files should return an error
    input_data["files"]["enabled"] = False
    draft = service.create(identity_simple, input_data)
    assert draft.errors[0]["field"] == "files.enabled"
    assert draft.errors[0]["messages"] == [
        "You don't have permissions to manage files options.",
    ]
