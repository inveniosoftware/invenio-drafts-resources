# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service API."""

from invenio_db import db
from invenio_records.api import Record
from invenio_records_resources.service import MarshmallowDataValidator

from ..drafts import Draft
from .permission import DraftPermissionPolicy
from .schemas import DraftMetadataSchemaJSONV1


class DraftServiceConfig:
    """Service factory configuration."""

    # FIXME: Should be a service class to allow internal
    # data validation etc.
    draft_of_cls = Record

    # ------------------------------
    # Common with DraftServiceConfig
    # ------------------------------
    draft_cls = Draft  # As `service_object_cls`
    data_validator = MarshmallowDataValidator(
        schema=DraftMetadataSchemaJSONV1
    )
    permission_policy_cls = DraftPermissionPolicy
    # ------------------------------


class DraftService:
    """Draft Service interface."""

    default_config = DraftServiceConfig

    def __init__(self, config=None):
        """Initialize the base resource."""
        self.config = config or self.default_config

    # --------------------------
    # Common with RecordService
    # --------------------------
    @classmethod
    def permission(cls, action_name, **kwargs):
        """Factory for creating permissions from a permission policy."""
        if cls.config.permission_policy_cls:
            return cls.config.permission_policy_cls(action_name, **kwargs)
        else:
            return RecordPermissionPolicy(action=action_name, **kwargs)

    @classmethod
    def require_permission(cls, identity, action_name, **kwargs):
        """Require a specific permission from the permission policy."""
        if not cls.permission(action_name, **kwargs).allows(identity):
            raise PermissionDeniedError(action_name)
    # --------------------------

    # High-level API
    def get(self, id_, identity):
        """Retrieve a draft."""
        pass

    def search(self, querystring, identity, pagination=None, *args, **kwargs):
        """Search for drafts matching the querystring."""
        pass

    def create(self, data, identity):
        """Create a draft."""
        # Check permissions: Can create draft of said record/resource
        self.require_permission(identity, "create")
        # Create record if new
        # TODO: The `draft_of` class is set in the Draft API
        # Creating the record class is business logic, but it is
        # being set in the data access layer

        # Get UUID, and version_id of forked record
        # Create draft based on that

        # # Validate draft data
        self.data_validator().validate(data)

        draft = self.draft_cls().create(data)  # Create draft in DB

        # TODO: Do we need to mint here? Tending for No
        pid = self.minter()(record_uuid=draft.id, data=draft)   # Mint PID
        # Create draft state
        draft_state = self.record_state(pid=pid, record=draft)
        db.session.commit()  # Persist DB
        # Index the draft
        indexer = self.indexer()
        if indexer:
            indexer.index(draft)

        return draft_state

    def delete(self, id_, identity):
        """Delete a draft from database and search indexes."""
        pass

    def update(self, id_, data, identity):
        """Replace a draft."""
        pass
