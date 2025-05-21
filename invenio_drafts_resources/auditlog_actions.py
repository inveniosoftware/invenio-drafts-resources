# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

from invenio_access.permissions import system_user_id
from invenio_audit_logs.services import AuditLogAction
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_users_resources.entity_resolvers import UserResolver


class UserContext:
    """Payload generator for audit log using the user entity resolver."""

    def __init__(self, key="user"):
        """Ctor."""
        self.key = key
        self.resolver = UserResolver()

    def __call__(self, data, lookup_key="user_id", **kwargs):
        """Update data with resolved user data."""
        entity_ref = dict_lookup(data, lookup_key)
        entity_proxy = self.resolver.get_entity_proxy({self.key: entity_ref})
        if entity_ref == system_user_id:
            entity_data = entity_proxy.system_record()
            entity_data = {
                "id": str(entity_data["id"]),
                "name": str(entity_data["username"]),
                "email": str(entity_data["email"]),
            }
        else:
            entity_data = entity_proxy.resolve()
            entity_data = {
                "id": str(entity_data.id),
                "name": entity_data.username,
                "email": entity_data.email,
            }
        dict_set(data, self.key, entity_data)


class RecordContext:
    """Payload generator for audit log to get record auditing metadata."""

    def __init__(self, revision_id=False, parent_pid=False):
        """Ctor."""
        # Enable or Disable adding metadata
        self.revision_id = revision_id
        self.parent_pid = parent_pid

    def __call__(self, data, **kwargs):
        """Update data with resolved record data."""
        record = kwargs.get("record", None)
        if record is None:
            return
        if self.revision_id:
            record_versions = record.model.versions.all()
            dict_set(data, "metadata.revision_id", record_versions[-1].transaction_id)
        if self.parent_pid:
            dict_set(data, "metadata.parent_pid", record.parent.pid.pid_value)


class RecordBaseAuditLog(AuditLogAction):
    """Base class for audit log builders."""

    context = [
        UserContext(),
    ]

    resource_type = "record"

    @classmethod
    def build(cls, identity, resource_id, **kwargs):
        """Build the log."""
        return super().build(
            resource={
                "id": resource_id,
                "type": cls.resource_type,
            },
            action=cls.id,
            identity=identity,
            **kwargs,
        )


class DraftCreateAuditLog(RecordBaseAuditLog):
    """Audit log for draft creation."""

    id = "draft.create"
    message_template = "User {user_id} created the draft {resource_id}."


class DraftEditAuditLog(RecordBaseAuditLog):
    """Audit log for draft editing."""

    id = "draft.edit"
    message_template = "User {user_id} updated the draft {resource_id}."


class RecordPublishAuditLog(RecordBaseAuditLog):
    """Audit log for record publication."""

    context = RecordBaseAuditLog.context + [
        RecordContext(revision_id=True, parent_pid=True),
    ]

    id = "record.publish"
    message_template = "User {user_id} published the record {resource_id}."


class DraftDeleteAuditLog(RecordBaseAuditLog):
    """Audit log for draft deletion."""

    id = "draft.delete"
    message_template = "User {user_id} deleted the draft {resource_id}."


class DraftNewVersionAuditLog(RecordBaseAuditLog):
    """Audit log for new draft version creation."""

    id = "draft.new_version"
    message_template = "User {user_id} created a new version {resource_id}."
