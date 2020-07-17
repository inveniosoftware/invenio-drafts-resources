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

from ..resource_units import IdentifiedRecordDraft
from .permissions import DraftPermissionPolicy
from .schemas import DraftMetadataSchemaJSONV1


class RecordDraftServiceConfig(RecordServiceConfig):
    """Draft Service configuration."""

    # Service configuration
    permission_policy_cls = DraftPermissionPolicy

    # RecordService configuration
    resource_unit_cls = IdentifiedRecordDraft
    data_validator = MarshmallowDataValidator(
        schema=DraftMetadataSchemaJSONV1
    )

    # DraftService configuration.
    # WHY: We want to force user input choice here.
    draft_cls = None


class RecordDraftService(RecordService):
    """Draft Service interface."""

    default_config = RecordDraftServiceConfig

    # High-level API
    # Inherits record read, search, create, delete and update

    def _index_draft(self, draft):
        indexer = self.indexer()
        if indexer:
            indexer.index(draft)

    def create(self, data, identity):
        """Create a draft for a new record.

        It does not eagerly create the associated record.
        """
        self.require_permission(identity, "create")
        validated_data = self.data_validator().validate(data)
        draft = self.config.draft_cls.create(validated_data)
        db.session.commit()  # Persist DB
        self._index_draft(draft)

        return self.config.resource_unit_cls(pid=None, record=draft)

    def edit(self, id_, data, identity):
        """Create a draft for an existing record.

        :param id_: record PID value.
        """
        pid, record = self.resolve(id_)
        # FIXME: How to check permission on the record?
        self.require_permission(identity, "create")
        validated_data = self.data_validator().validate(data)
        draft = self.config.draft_cls.create(validated_data, record)
        db.session.commit()  # Persist DB
        self._index_draft(draft)

        return self.config.resource_unit_cls(pid=pid, record=draft)

    def publish(self, id_, identity):
        """Publish a draft."""
        # TODO: IMPLEMENT ME!
        return self.config.draft_of_resource_unit_cls()
