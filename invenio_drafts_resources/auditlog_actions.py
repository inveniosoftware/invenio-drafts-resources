# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

from invenio_audit_logs.services import AuditLogBuilder


class RecordBaseAuditLog(AuditLogBuilder):
    """Base class for audit log builders."""

    resource_type = "record"

    @classmethod
    def build(cls, resource_id, identity):
        """Build the log."""
        return super().build(
            resource={
                "id": resource_id,
                "type": cls.resource_type,
            },
            action=cls.action,
            identity=identity,
        )


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
