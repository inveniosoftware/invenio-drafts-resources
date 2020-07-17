# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Draft Service."""

from invenio_db import db
from invenio_records_resources.services import MarshmallowDataValidator, \
    RecordService, RecordServiceConfig

from ..resource_units import IdentifiedDraft
from .permissions import DraftPermissionPolicy
from .schemas import DraftMetadataSchemaJSONV1


class DraftServiceConfig(RecordServiceConfig):
    """Draft Service configuration."""

    # Service configuration
    permission_policy_cls = DraftPermissionPolicy
    resource_unit_cls = IdentifiedDraft

    # RecordService configuration
    data_validator = MarshmallowDataValidator(
        schema=DraftMetadataSchemaJSONV1
    )

    # DraftService configuration.
    # WHY: We want to force user input choice here.
    draft_cls = None


class DraftService(RecordService):
    """Draft Service interface."""

    default_config = DraftServiceConfig

    # High-level API
    # Inherits record read, search, create, delete and update

    def _index_draft(self, draft):
        indexer = self.indexer()
        if indexer:
            indexer.index(draft)

    def create_new(self, data, identity):
        """Create a draft and the associated record (new)."""
        self.require_permission(identity, "create")
        record = self.config.record_cls.create(data=data)
        pid = self.minter()(record_uuid=record.id, data=record)
        validated_data = self.data_validator().validate(data)
        draft = self.config.draft_cls.create(record, validated_data)
        db.session.commit()  # Persist DB
        self._index_draft(draft)

        return self.config.resource_unit_cls(pid=pid, draft=draft)

    def create_from(self, id_, data, identity):
        """Create a draft for an existing record.

        :param id_: record PID value.
        """
        self.require_permission(identity, "create")
        pid, record = self.resolve(id_)
        validated_data = self.data_validator().validate(data)
        draft = self.config.draft_cls.create(record, validated_data)
        db.session.commit()  # Persist DB
        self._index_draft(draft)

        return self.config.resource_unit_cls(pid=pid, draft=draft)

    def publish(self, id_, identity):
        """Publish a draft."""
        # TODO: IMPLEMENT ME!
        return self.config.draft_of_resource_unit_cls()
