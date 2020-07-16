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
from invenio_records.api import Record
from invenio_records_resources.resource_units import IdentifiedRecord
from invenio_records_resources.services import MarshmallowDataValidator, \
    RecordService, RecordServiceConfig

from ..drafts.api import Draft
from ..resource_units import IdentifiedDraft
from .permissions import DraftPermissionPolicy
from .schemas import DraftMetadataSchemaJSONV1


class DraftServiceConfig(RecordServiceConfig):
    """Draft Service configuration."""

    # Service configuration
    permission_policy_cls = DraftPermissionPolicy
    resource_unit_cls = IdentifiedDraft

    # RecordService configuration
    # TODO: FILL ME!

    # DraftService configuration
    # TODO: FILL ME!
    draft_of_resource_unit_cls = IdentifiedRecord
    draft_of_cls = Record
    draft_cls = Draft  # As `service_object_cls`
    data_validator = MarshmallowDataValidator(
        schema=DraftMetadataSchemaJSONV1
    )


class DraftService(RecordService):
    """Draft Service interface."""

    default_config = DraftServiceConfig

    # High-level API
    def read(self, id_, identity):
        """Retrieve a draft."""
        # TODO: IMPLEMENT ME!
        # High likelihood that we can just rely on RecordService here
        # and simply configure DraftServiceConfig appropriately
        return self.resource_unit_cls()

    def search(self, querystring, identity, pagination=None, *args, **kwargs):
        """Search for drafts matching the querystring."""
        # TODO: IMPLEMENT ME!
        # High likelihood that we can just rely on RecordService here
        # and simply configure DraftServiceConfig appropriately
        return self.resource_list_cls()

    def create(self, data, identity):
        """Create a draft."""
        # TODO: IMPLEMENT ME!
        # # Check permissions: Can create draft of said record/resource
        self.require_permission(identity, "create")
        # Create record if new
        # TODO: The `draft_of` class is set in the Draft API
        # Creating the record class is business logic, but it is
        # being set in the data access layer

        # Get UUID, and version_id of forked record
        # Create draft based on that

        # # Validate draft data
        self.data_validator().validate(data)

        draft = self.config.draft_cls.create(data)  # Create draft in DB

        # TODO: Do we need to mint here? Tending for No
        pid = self.minter()(record_uuid=draft.id, data=draft)   # Mint PID
        # Create draft state
        draft_state = self.resource_unit(pid=pid, record=draft)
        db.session.commit()  # Persist DB
        # Index the draft
        indexer = self.indexer()
        if indexer:
            indexer.index(draft)

        return draft_state

    def delete(self, id_, identity):
        """Delete a draft from database and search indexes."""
        # TODO: IMPLEMENT ME!
        # High likelihood that we can just rely on RecordService here
        # and simply configure DraftServiceConfig appropriately
        return self.resource_unit_cls()

    def update(self, id_, data, identity):
        """Replace a draft."""
        # TODO: IMPLEMENT ME!
        # High likelihood that we can just rely on RecordService here
        # and simply configure DraftServiceConfig appropriately
        return self.resource_unit_cls()

    def publish(self, id_, identity):
        """Publish a draft."""
        # TODO: IMPLEMENT ME!
        return self.draft_of_resource_unit_cls()
