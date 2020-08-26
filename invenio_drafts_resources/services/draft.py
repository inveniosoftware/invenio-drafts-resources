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
from invenio_records_resources.services import MarshmallowDataValidator, \
    RecordService, RecordServiceConfig

from ..links import DraftPublishLinkBuilder, DraftSelfHtmlLinkBuilder, \
    DraftSelfLinkBuilder, RecordEditLinkBuilder
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
        DraftSelfHtmlLinkBuilder,
        DraftPublishLinkBuilder
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

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(RecordDraftService, self).__init__(*args, **kwargs)
        self.linker.register_link_builders({
            "draft": [
                lb(self.config) for lb in self.config.draft_link_builders
            ]
        })

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

        links = self.linker.links(
            "draft", identity, pid_value=pid.pid_value, record=draft
        )

        # Todo: how do we deal with tombstone pages
        return self.resource_unit(pid=pid, record=draft, links=links)

    def update_draft(self, identity, id_, data):
        """Replace a draft."""
        # TODO: etag and versioning
        pid, draft = self.pid_manager.resolve(id_, draft=True)
        # Permissions
        self.require_permission(identity, "update", record=draft)
        validated_data = self.data_validator.validate(data, partial=True)
        # FIXME: extract somewhere else
        self._patch_data(draft, validated_data)
        draft.update(draft.dumps())
        draft.commit()

        if self.indexer:
            self.indexer.index(draft)

        links = self.linker.links(
            "draft", identity, pid_value=pid.pid_value, record=draft
        )

        return self.resource_unit(pid=pid, record=draft, links=links)

    def create(self, identity, data):
        """Create a draft for a new record.

        It does not eagerly create the associated record.
        """
        self.require_permission(identity, "create")
        validated_data = self.data_validator.validate(data, partial=True)
        rec_uuid = uuid.uuid4()
        pid = self.pid_manager.mint(record_uuid=rec_uuid, data=validated_data)
        draft = self.draft_cls.create(validated_data, id_=rec_uuid)

        db.session.commit()  # Persist DB
        if self.indexer:
            self.indexer.index(draft)

        links = self.linker.links(
            "draft", identity, pid_value=pid.pid_value, record=draft
        )

        return self.resource_unit(pid=pid, record=draft, links=links)

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
        validated_data = self.data_validator.validate(data, partial=True)
        self._patch_data(record, validated_data)
        draft = self.draft_cls.create(record.dumps(), id_=record.id,
                                      fork_version_id=record.revision_id)
        db.session.commit()  # Persist DB
        if self.indexer:
            self.indexer.index(draft)

        links = self.linker.links(
            "draft", identity, pid_value=pid.pid_value, record=draft
        )

        return self.resource_unit(pid=pid, record=draft, links=links)

    def _publish_revision(self, validated_data, pid):
        """Publish draft of existing record (edition)."""
        pid, record = self.pid_manager.resolve(pid.pid_value)
        record.clear()
        record.update(validated_data)
        record.commit()

        return record

    def _publish_new_version(self, validated_data, draft):
        """Publish draft of a new record."""
        record = self.record_cls.create(validated_data, id_=draft.id)
        conceptrecid = record['conceptrecid']

        # FIXME: This implies two db queries for the same in pid_manager
        if self.pid_manager.is_first_version(
            pid_value=conceptrecid
        ):
            self.pid_manager.register_pid(record['conceptrecid'])

        self.pid_manager.register_pid(record['recid'])

        return record

    def publish(self, identity, id_):
        """Publish a draft."""
        self.require_permission(identity, "publish")
        # Get draft
        pid, draft = self.pid_manager.resolve(id_, draft=True)
        # Validate against record schema
        validated_data = self.data_validator.validate(draft.dumps())
        # Publish it
        if self.pid_manager.is_published(pid):  # Then we publish a revision
            record = self._publish_revision(validated_data, pid)
        else:
            record = self._publish_new_version(validated_data, draft)
        # Remove draft
        draft.delete(force=True)
        db.session.commit()  # Persist DB
        # Index the record
        if self.indexer:
            self.indexer.delete(draft)
            self.indexer.index(record)

        links = self.linker.links(
            "record", identity, pid_value=pid.pid_value, record=record
        )

        return self.resource_unit(pid=pid, record=record, links=links)

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
        db.session.commit()  # Persist DB
        # Index the record
        if self.indexer:
            self.indexer.index(draft)

        links = self.linker.links(
            "draft", identity, pid_value=pid.pid_value, record=draft
        )

        return self.resource_unit(pid=pid, record=draft, links=links)
