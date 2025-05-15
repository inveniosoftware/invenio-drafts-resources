# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

from invenio_access.permissions import system_identity
from invenio_audit_logs.services import AuditLogBuilder
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_records_resources.references.entity_resolvers import ServiceResultResolver


class UserResolve:
    """Payload generator for audit log using the service result resolvers."""

    def __init__(self, key):
        """Ctor."""
        self.key = key

    def __call__(self, resolver, log_data):
        """Update required recipient information and add backend id."""
        entity_ref = dict_lookup(log_data, self.key)
        if entity_ref == system_identity.id:
            entity_data = {
                "id": str(system_identity.id),
                "name": "system",
                "email": "system@system.org",
            }
        else:
            entity = resolver.get_entity_proxy({self.key: entity_ref}).resolve()
            entity_data = {
                "id": str(entity["id"]),
                "name": entity["username"],
                "email": entity["email"],
            }
        dict_set(log_data, self.key, entity_data)


class RecordBaseAuditLog(AuditLogBuilder):
    """Base class for audit log builders."""

    context = [
        {
            "resolver": ServiceResultResolver(service_id="users", type_key="user"),
            "generator": UserResolve(key="user"),
        },
    ]

    resource_type = "record"

    @classmethod
    def build(cls, resource_id, identity, **kwargs):
        """Build the log."""
        return super().build(
            resource={
                "id": resource_id,
                "type": cls.resource_type,
            },
            action=cls.action,
            identity=identity,
            **kwargs,
        )

    def resolve_context(self, log_data, **kwargs):
        """Resolve all references in the audit log context."""
        for context in self.context:
            # Bypassing registry implementation (which matches the entity resolver to use)
            # Directly using the UserResolve generator to resolve the user
            # Cannot be kept in audit logs as it shouldn't depend on users service
            entity_resolver = context["generator"]
            entity_resolver(context["resolver"], log_data)
        return log_data


class DraftCreateAuditLog(RecordBaseAuditLog):
    """Audit log for draft creation."""

    action = "draft.create"
    message_template = ("User {user_id} created the draft {resource_id}.",)


class DraftEditAuditLog(RecordBaseAuditLog):
    """Audit log for draft editing."""

    action = "draft.edit"
    message_template = ("User {user_id} updated the draft {resource_id}.",)


class RecordPublishAuditLog(RecordBaseAuditLog):
    """Audit log for record publication."""

    action = "record.publish"
    message_template = ("User {user_id} published the record {resource_id}.",)


class DraftDeleteAuditLog(RecordBaseAuditLog):
    """Audit log for draft deletion."""

    action = "draft.delete"
    message_template = ("User {user_id} deleted the draft {resource_id}.",)


class DraftNewVersionAuditLog(RecordBaseAuditLog):
    """Audit log for new draft version creation."""

    action = "draft.new_version"
    message_template = ("User {user_id} created a new version {resource_id}.",)
