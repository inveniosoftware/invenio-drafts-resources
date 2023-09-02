# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data access layer tests."""
from datetime import timedelta

import pytest
from invenio_search import current_search_client
from jsonschema import ValidationError
from mock_module.api import Draft, ParentRecord, Record
from mock_module.models import (
    DraftMetadata,
    ParentRecordMetadata,
    ParentState,
    RecordMetadata,
)
from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound


#
# Create
#
def test_draft_create_empty(app, db, location):
    """Test draft creation."""
    # Empty draft creation works, and injects a schema.
    draft = Draft.create({})
    db.session.commit()
    assert draft.schema

    # JSONSchema validation works.
    pytest.raises(ValidationError, Draft.create, {"metadata": {"title": 1}})


def test_draft_create_parent(app, db, location):
    """Test draft creation of the parent record."""
    draft = Draft.create({})
    db.session.commit()
    assert draft.schema.endswith("record-v1.0.0.json")
    assert draft.pid
    assert draft.parent.schema.endswith("parent-v1.0.0.json")
    assert draft.parent.pid

    assert draft.model.parent_id == draft.model.parent.id
    assert draft.pid.object_uuid != draft.parent.pid.object_uuid


def test_draft_create_parent_state(app, db, location):
    """Test draft creation of the parent record."""
    draft = Draft.create({})
    db.session.commit()

    # Assert that associated objects were created
    assert ParentState.query.count() == 1
    assert DraftMetadata.query.count() == 1
    assert ParentRecordMetadata.query.count() == 1
    assert RecordMetadata.query.count() == 0

    def assert_state(d):
        # An initial draft is not published, so latest_id/index is None
        assert d.model.index == 1
        assert d.versions.index == 1
        assert d.versions.latest_id is None
        assert d.versions.latest_index is None
        assert d.versions.next_draft_id == d.id

    assert_state(draft)
    assert_state(Draft.get_record(draft.id))


def test_record_create_parent_state(app, db, location):
    """Test draft creation of the parent record."""
    draft = Draft.create({})
    draft.commit()
    db.session.commit()
    record = Record.publish(draft)
    record.commit()
    db.session.commit()

    def assert_state(r):
        # An initial draft is not published, so latest_id/index is None
        assert r.versions.latest_id == r.id
        assert r.versions.latest_index == 1
        assert r.versions.next_draft_id is None
        assert r.versions.index == 1
        assert r.versions.is_latest is True
        assert r.versions.is_latest_draft is True
        assert r.model.index == 1
        assert r.model.parent_id == draft.model.parent_id

    assert_state(record)
    assert_state(Record.get_record(record.id))


def test_draft_create_new_version(app, db, location):
    """Test draft creation of the parent record."""
    # A published record.
    record = Record.publish(Draft.create({}))
    db.session.commit()
    # Create a draft for a new version (happens in service.new_version())
    draft = Draft.new_version(record)
    draft.commit()
    db.session.commit()

    record = Record.get_record(record.id)
    draft = Draft.get_record(draft.id)

    assert record.id != draft.id  # different uuids
    assert record.parent.id == draft.parent.id  # same parent
    assert draft.versions.is_latest_draft is True
    assert draft.versions.is_latest is False
    assert record.versions.is_latest_draft is False
    assert record.versions.is_latest is True


def test_draft_parent_state_hard_delete(app, db, location):
    """Test force deletion of a draft."""
    # Initial state: Only draft exists (i.e. no other record versions)
    draft = Draft.create({})
    db.session.commit()
    # happens on:
    # - service.delete_draft for an *unpublished* record
    draft.delete(force=True)
    db.session.commit()
    # Make sure no parent and no parent state is left-behind
    assert ParentState.query.count() == 0
    assert ParentRecordMetadata.query.count() == 0
    assert DraftMetadata.query.count() == 0
    assert RecordMetadata.query.count() == 0


def test_new_draft_of_published_record_doesnt_override_next_draft_id(app, db, location):
    """Test multiple drafts when editing multiple versions of the same record."""
    # Classic draft of published record having been cleaned up scenario
    record_1 = Record.publish(Draft.create({}))
    db.session.commit()
    Draft.cleanup_drafts(timedelta(0))

    # Wider test for any situation where draft of record doesn't exist anymore
    # e.g. admin force deletion
    parent = ParentRecord.create({})
    record_2 = Record.create({}, parent=parent)
    record_2.register()

    db.session.commit()

    for record in [record_1, record_2]:
        # Create new_version before a record's draft exists
        new_version_draft = Draft.new_version(record)
        db.session.commit()
        assert record.versions.next_draft_id == new_version_draft.id
        assert record.versions.latest_id == record.id

        # Check next_draft_id still holds after edit
        Draft.edit(record)
        db.session.commit()
        assert record.versions.next_draft_id == new_version_draft.id
        assert record.versions.latest_id == record.id


def test_draft_parent_state_hard_delete_with_parent(app, db, location):
    """Test force deletion of a draft."""
    # Initial state: A previous reccord version exists, in addition to draft
    draft = Draft.create({})
    record = Record.create({}, parent=draft.parent)
    db.session.commit()
    # happens on:
    # - service.delete_draft for an *unpublished* record
    draft.delete(force=True)
    db.session.commit()
    # Make sure parent/parent state is still there
    assert ParentState.query.count() == 1
    assert ParentRecordMetadata.query.count() == 1
    assert RecordMetadata.query.count() == 1
    assert DraftMetadata.query.count() == 0

    record = Record.get_record(record.id)
    assert record.versions.next_draft_id is None
    assert record.versions.latest_id == record.id


def test_draft_parent_state_soft_delete(app, db, location):
    """Test soft deletion of a draft."""
    # Simulate a record being edited.
    draft = Draft.create({})
    record = Record.create({}, parent=draft.parent)
    db.session.commit()
    # happens on:
    # - service.publish()
    # - service.delete_draft() for a *published* record
    draft.delete(force=False)
    db.session.commit()

    assert ParentState.query.count() == 1
    assert ParentRecordMetadata.query.count() == 1
    assert RecordMetadata.query.count() == 1

    record = Record.get_record(record.id)
    assert record.versions.next_draft_id is None
    assert record.versions.latest_id == record.id


#
# Create/Update from draft
#
def test_create_record_from_draft(app, db, example_draft):
    """Test create a record from a draft.

    This is used e.g. when publishing a new draft as a record.
    """
    record = Record.publish(example_draft)
    db.session.commit()
    assert example_draft.pid == record.pid
    assert example_draft.parent == record.parent


#
# Get
#
def test_draft_get_record(app, db, example_draft):
    """Test draft retrival."""
    draft = Draft.get_record(example_draft.id)
    # Test that the parent record is properly fetched.
    assert draft.parent == example_draft.parent


#
# Delete
#
def test_draft_force_delete(app, db, example_draft):
    """Test draft hard deletion."""
    parent_id = example_draft.parent.id
    example_draft.delete(force=True)
    db.session.commit()

    # Both parent and draft is deleted
    pytest.raises(NoResultFound, ParentRecord.get_record, parent_id)
    pytest.raises(NoResultFound, Draft.get_record, example_draft.id)


def test_draft_soft_delete(app, db, example_draft):
    """Test draft soft deletion."""
    parent_id = example_draft.parent.id
    example_draft.delete(force=False)
    db.session.commit()

    # Parent not deleted, but draft is soft deleted.
    assert ParentRecord.get_record(parent_id)
    pytest.raises(NoResultFound, Draft.get_record, example_draft.id)
    draft = Draft.get_record(example_draft.id, with_deleted=True)
    assert draft.parent.id == parent_id


def test_draft_undelete(app, db, example_draft):
    """Test undeleting a draft."""
    example_draft.delete()
    db.session.commit()

    draft = Draft.get_record(example_draft.id, with_deleted=True)
    assert draft.is_deleted
    draft.undelete()
    assert draft.parent.id == example_draft.parent.id


#
# Dumps/loads
#
def test_draft_dump_load_idempotence(app, db, example_draft):
    """Test idempotence of dumps/loads."""
    loaded_draft = Draft.loads(example_draft.dumps())
    assert example_draft == loaded_draft
    # Parent was dumped and loaded
    assert example_draft.parent == loaded_draft.parent
    assert (
        example_draft.versions.is_latest_draft == loaded_draft.versions.is_latest_draft
    )
    # Test that SQLAlchemy model was loaded from the JSON and not DB.
    assert not inspect(loaded_draft.parent.model).persistent
    assert not inspect(loaded_draft.versions._state).persistent


#
# Indexing
#
def test_draft_indexing(app, db, search, example_draft, indexer):
    """Test indexing of a draft."""
    # Index document in search cluster
    assert indexer.index(example_draft)["result"] == "created"
    # Retrieve document from search cluster
    data = current_search_client.get(
        "draftsresources-drafts-draft-v1.0.0", id=example_draft.id
    )

    # Loads the search cluster data and compare
    draft = Draft.loads(data["_source"])

    assert draft == example_draft
    assert draft.id == example_draft.id
    assert draft.revision_id == example_draft.revision_id
    assert draft.created == example_draft.created
    assert draft.updated == example_draft.updated
    assert draft.expires_at == example_draft.expires_at
    assert draft.parent == example_draft.parent
    assert draft.versions.is_latest_draft == example_draft.versions.is_latest_draft
    assert draft.versions.index == example_draft.versions.index
    # Check system fields
    assert draft.metadata == example_draft["metadata"]


def test_draft_delete_reindex(app, db, search, example_draft, indexer):
    """Test reindexing of a soft-deleted draft."""
    draft = example_draft

    # Index draft
    assert indexer.index(draft)["result"] == "created"

    # Delete record.
    draft.delete()
    db.session.commit()
    assert indexer.delete(draft)["result"] == "deleted"

    # Update draft and reindex (this will cause troubles unless proper
    # optimistic concurrency control is used).
    draft.undelete()
    draft.commit()
    db.session.commit()
    assert indexer.index(draft)["result"] == "created"


#
# Get by parent
#
def test_get_records_by_parent(app, db, location):
    """Test get by parent."""
    # Create two published records
    draft_v1 = Draft.create({})
    db.session.commit()
    parent = draft_v1.parent
    drafts = list(Draft.get_records_by_parent(parent))
    assert len(drafts) == 1
    assert id(parent) == id(drafts[0].parent)
    records = list(Record.get_records_by_parent(parent))
    assert len(records) == 0

    state = Draft.versions.resolve(parent_id=parent.id)
    assert state == Record.versions.resolve(parent_id=parent.id)
    assert state.latest_id is None
    assert state.latest_index is None
    assert state.next_draft_id == draft_v1.id

    record_v1 = Record.publish(draft_v1)
    draft_v1.delete()  # simulate service `publish`, will soft delete drafts
    db.session.commit()
    parent = record_v1.parent
    drafts = list(Draft.get_records_by_parent(parent))
    assert len(drafts) == 1
    assert id(parent) == id(drafts[0].parent)
    drafts = list(Draft.get_records_by_parent(parent, with_deleted=False))
    assert len(drafts) == 0
    records = list(Record.get_records_by_parent(parent))
    assert len(records) == 1
    assert id(parent) == id(records[0].parent)

    state = Record.versions.resolve(parent_id=parent.id)
    assert state == Draft.versions.resolve(parent_id=parent.id)
    assert state.latest_id == record_v1.id
    assert state.latest_index == 1
    assert state.next_draft_id is None

    draft_v2 = Draft.new_version(record_v1)
    draft_v2.commit()
    parent = draft_v2.parent
    db.session.commit()
    drafts = list(Draft.get_records_by_parent(parent))
    assert len(drafts) == 2
    assert id(parent) == id(drafts[0].parent)
    records = list(Record.get_records_by_parent(record_v1.parent))
    assert len(records) == 1
    assert id(record_v1.parent) == id(records[0].parent)

    state = Draft.versions.resolve(parent_id=parent.id)
    assert state == Record.versions.resolve(parent_id=parent.id)
    assert state.latest_id == record_v1.id
    assert state.latest_index == 1
    assert state.next_draft_id == draft_v2.id

    record_v2 = Record.publish(draft_v2)
    draft_v2.delete()  # simulate service `publish`, will soft delete drafts
    db.session.commit()
    parent = record_v2.parent
    drafts = list(Draft.get_records_by_parent(parent))
    assert len(drafts) == 2
    drafts = list(Draft.get_records_by_parent(parent, with_deleted=False))
    assert len(drafts) == 0
    records = list(Record.get_records_by_parent(parent))
    assert len(records) == 2
    assert id(parent) == id(records[0].parent) == id(records[1].parent)

    state = Record.versions.resolve(parent_id=parent.id)
    assert state == Draft.versions.resolve(parent_id=parent.id)
    assert state.latest_id == record_v2.id
    assert state.latest_index == 2
    assert state.next_draft_id is None


#
# Get latest by parent
#
def test_get_latest_by_parent(app, db, location):
    """Test get latest by parent."""
    draft_v1 = Draft.create({})
    db.session.commit()
    parent = draft_v1.parent

    # nothing published yet
    assert not Draft.get_latest_by_parent(parent)
    assert not Record.get_latest_by_parent(parent)

    record_v1 = Record.publish(draft_v1)
    draft_v1.delete()  # simulate service `publish`, will soft delete drafts
    db.session.commit()
    parent = record_v1.parent

    assert not Draft.get_latest_by_parent(parent)
    assert Record.get_latest_by_parent(parent).id == record_v1.id

    draft_v2 = Draft.new_version(record_v1)
    draft_v2.commit()
    db.session.commit()

    assert Draft.get_latest_by_parent(parent).id == record_v1.id
    assert Record.get_latest_by_parent(parent).id == record_v1.id

    record_v2 = Record.publish(draft_v2)
    draft_v2.delete()  # simulate service `publish`, will soft delete drafts
    db.session.commit()

    assert not Draft.get_latest_by_parent(parent)
    assert Record.get_latest_by_parent(parent).id == record_v2.id
