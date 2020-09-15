# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Draft Service."""

import uuid

from invenio_db import db
from invenio_records_resources.linker.base import LinkStore
from invenio_records_resources.services import RecordService, \
    RecordServiceConfig
from invenio_records_resources.services.records.components import \
    AccessComponent, FilesComponent, MetadataComponent, PIDSComponent

from ..links import DraftPublishLinkBuilder, DraftSelfLinkBuilder, \
    RecordEditLinkBuilder
from .components import RelationsComponent
from .permissions import DraftPermissionPolicy
from .pid_manager import PIDManager
from .search import draft_record_to_index


class RecordDraftServiceConfig(RecordServiceConfig):
    """Draft Service configuration."""

    # Service configuration
    permission_policy_cls = DraftPermissionPolicy

    # RecordService configuration
    pid_manager = PIDManager()
    record_link_builders = RecordServiceConfig.record_link_builders + [
        RecordEditLinkBuilder
    ]

    # DraftService configuration.
    record_to_index = draft_record_to_index
    # WHY: We want to force user input choice here.
    draft_cls = None
    draft_route = None
    draft_action_route = None
    draft_link_builders = [
        DraftSelfLinkBuilder,
        DraftPublishLinkBuilder
    ]

    components = [
        MetadataComponent,
        PIDSComponent,
        RelationsComponent,
        AccessComponent,
        FilesComponent,
    ]


class RecordDraftService(RecordService):
    """Draft Service interface.

    This service provides an interface to business logic for
    published AND draft records. When creating a custom service
    for a specialized record (e.g. Authors), consider if you need
    draft functionality or not. If you do, inherit from this service;
    otherwise, inherit from the RecordService directly.

    This service includes versioning.
    """

    default_config = RecordDraftServiceConfig

    @property
    def pid_manager(self):
        """Factory for the pid manager."""
        return self.config.pid_manager

    @property
    def indexer(self):
        """Factory for creating an indexer instance."""
        return self.config.indexer_cls(
            record_to_index=self.config.record_to_index
        )

    # Draft attrs
    @property
    def draft_cls(self):
        """Factory for creating a record class."""
        return self.config.draft_cls

    # High-level API
    # Inherits record read, search, create, delete and update

    def read_draft(self, identity, id_):
        """Retrieve a draft."""
        pid, draft = self.pid_manager.resolve(id_, draft=True)
        # TODO: "read" is used here AND in inherited read() method
        #       but have different meanings: read a draft or read a record
        #       Permission mechanism should be per resource unit OR per
        #       service
        self.require_permission(identity, "read", record=draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'read_draft'):
                component.read_draft(identity, draft=draft)
        links = LinkStore()
        draft_projection = self.schema.dump(
            identity, draft, record=draft, links_store=links)

        # Todo: how do we deal with tombstone pages
        return self.result_item(
            pid=pid, record=draft_projection, links=links)

    def update_draft(self, identity, id_, data):
        """Replace a draft."""
        # TODO: etag and versioning
        pid, draft = self.pid_manager.resolve(id_, draft=True)
        # Permissions
        self.require_permission(identity, "update", record=draft)
        validated_data, errors = self.schema.load(
            identity, data, raise_errors=False)

        # Run components
        for component in self.components:
            if hasattr(component, 'update_draft'):
                component.update_draft(
                    identity, record=draft, data=validated_data)

        draft.commit()
        db.session.commit()

        if self.indexer:
            self.indexer.index(draft)

        links = LinkStore()
        draft_projection = self.schema.dump(
            identity, draft, record=draft, links_store=links)

        return self.result_item(
            pid=pid, record=draft_projection, links=links, errors=errors)

    def create(self, identity, data):
        """Create a draft for a new record.

        It does not eagerly create the associated record.
        """
        self.require_permission(identity, "create")
        validated_data, errors = self.schema.load(
            identity, data, raise_errors=False)

        # TODO (Alex): Replace with:
        #   draft = self.draft_cls.create(id_=rec_uuid, data={}, pid=pid)
        #
        # ...or even (and have the UUID, PID automatically created):
        #   draft = self.draft_cls.create()
        rec_uuid = uuid.uuid4()
        draft_data = {}
        pid = self.pid_manager.mint(record_uuid=rec_uuid, data=draft_data)
        draft = self.draft_cls.create(id_=rec_uuid, data=draft_data)

        # Run components
        for component in self.components:
            if hasattr(component, 'create'):
                component.create(identity, record=draft, data=validated_data)

        draft.commit()
        db.session.commit()  # Persist DB
        if self.indexer:
            self.indexer.index(draft)

        links = LinkStore()
        draft_projection = self.schema.dump(
            identity, draft, record=draft, links_store=links)

        return self.result_item(
            pid=pid, record=draft_projection, links=links, errors=errors)

    def _patch_data(self, record, data):
        """Temporarily here until the merge strategy is set."""
        # TODO: Implement better update/merge strategy
        for key in data.keys():
            record[key] = data[key]

    def edit(self, identity, id_, data):
        """Create a new revision or a draft for an existing record.

        :param id_: record PID value.
        """
        pid, record = self.pid_manager.resolve(id_)
        self.require_permission(identity, "create")
        validated_data, errors = self.schema.load(
            identity, data, raise_errors=False)

        # TODO (Alex): patch or keep existing data?
        self._patch_data(record, validated_data)
        # TODO (Alex): Check actually if the draft is already there before proceeding?
        draft = self.draft_cls.create(record.dumps(), id_=record.id,
                                      fork_version_id=record.revision_id)

        # Run components
        for component in self.components:
            if hasattr(component, 'edit'):
                component.edit(
                    identity, draft=draft, record=record, data=validated_data)

        db.session.commit()  # Persist DB
        if self.indexer:
            self.indexer.index(draft)

        links = LinkStore()
        draft_projection = self.schema.dump(
            identity, draft, pid=pid, record=draft, links_store=links)

        return self.result_item(
            pid=pid, record=draft_projection, links=links, errors=errors)

    def _publish_revision(self, validated_data, pid):
        """Publish draft of existing record (edition)."""
        pid, record = self.pid_manager.resolve(pid.pid_value)
        record.clear()
        record.update(validated_data)
        record.commit()

        return record

    def _publish_new_version(self, validated_data, draft):
        """Publish draft of a new record."""
        # TODO (Alex): Remove when we figure out how to copy system fields
        # from draft to record.
        validated_data['conceptrecid'] = draft['conceptrecid']
        validated_data['recid'] = draft['recid']
        record = self.record_cls.create(validated_data, id_=draft.id)
        conceptrecid = record['conceptrecid']

        # FIXME: This implies two db queries for the same in pid_manager
        if self.pid_manager.is_first_version(pid_value=conceptrecid):
            self.pid_manager.register_pid(record['conceptrecid'])

        self.pid_manager.register_pid(record['recid'])

        return record

    def publish(self, identity, id_):
        """Publish a draft."""
        self.require_permission(identity, "publish")
        # Get draft
        pid, draft = self.pid_manager.resolve(id_, draft=True)
        # Fully validate draft now
        # TODO: Add error_map for `ValidationError` in the resource config
        validated_data, _ = self.schema.load(
            identity, draft.dumps(), pid=pid, record=draft)
        # Publish it
        if self.pid_manager.is_published(pid):  # Then we publish a revision
            record = self._publish_revision(validated_data, pid)
        else:
            record = self._publish_new_version(validated_data, draft)

        # Run components
        for component in self.components:
            if hasattr(component, 'publish'):
                component.publish(identity, draft=draft, record=record)

        # Remove draft
        draft.delete(force=True)
        db.session.commit()  # Persist DB
        # Index the record
        if self.indexer:
            self.indexer.delete(draft)
            self.indexer.index(record)

        links = LinkStore()
        record_projection = self.schema.dump(
            identity, record, pid=pid, record=record, links_store=links)

        return self.result_item(
            pid=pid, record=record_projection, links=links)

    def new_version(self, identity, id_):
        """Create a new version of a record."""
        self.require_permission(identity, "create")
        # Get record
        pid, record = self.pid_manager.resolve(id_)
        data = record.dumps()
        # Create new record (relation done by minter)
        rec_uuid = uuid.uuid4()
        pid = self.pid_manager.mint(
            record_uuid=rec_uuid,
            data=data
        )
        draft = self.draft_cls.create(
            data=data,
            id_=rec_uuid
        )

        # Run components
        for component in self.components:
            if hasattr(component, 'new_version'):
                component.new_version(identity, draft=draft)

        db.session.commit()  # Persist DB
        # Index the record
        if self.indexer:
            self.indexer.index(draft)

        links = LinkStore()
        draft_projection = self.schema.dump(
            identity, draft, pid=pid, record=draft, links_store=links)

        return self.result_item(
            pid=pid, record=draft_projection, links=links)
