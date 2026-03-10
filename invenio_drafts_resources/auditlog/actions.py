# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

from invenio_audit_logs.services import AuditLogAction
from marshmallow import fields

from .context import (
    ParentContext,
    RecordContext,
    RequestContext,
    UserContext,
)


class BaseAuditLog(AuditLogAction):
    """Base class for audit log builders."""

    # NOTE: This lives here instead of the audit-logs module because it was decided to not make the module depend
    # on users-resources module to avoid circular dependencies and be able to add audit log actions for users in future.
    context = [
        UserContext(),
        RequestContext(),
    ]
    """Base content resolvers for all audit log builders."""

    metadata_schema = {
        "ip_address": fields.Str(
            required=True,
            metadata={
                "description": "IP address of the client.",
            },
        ),
        "session": fields.Str(
            required=True,
            metadata={
                "description": "Session identifier.",
            },
        ),
        "request_id": fields.Str(
            required=False,
            metadata={
                "description": "Unique identifier for the request.",
            },
        ),
    }


class RecordBaseAuditLog(BaseAuditLog):
    """Base class for audit log builders for record."""

    resource_type = "record"

    context = BaseAuditLog.context + [
        ParentContext(),
    ]

    metadata_schema = {
        **BaseAuditLog.metadata_schema,
        "parent_pid": fields.Str(
            required=True,
            metadata={
                "description": "Parent PID.",
            },
        ),
    }


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

    id = "record.publish"
    message_template = "User {user_id} published the record {resource_id}."

    context = RecordBaseAuditLog.context + [
        RecordContext(),
    ]

    metadata_schema = {
        **RecordBaseAuditLog.metadata_schema,
        "revision_id": fields.Int(
            required=True,
            metadata={
                "description": "Record revision ID.",
            },
        ),
    }


class DraftDeleteAuditLog(RecordBaseAuditLog):
    """Audit log for draft deletion."""

    id = "draft.delete"
    message_template = "User {user_id} deleted the draft {resource_id}."


class DraftNewVersionAuditLog(RecordBaseAuditLog):
    """Audit log for new draft version creation."""

    id = "draft.new_version"
    message_template = "User {user_id} created a new version {resource_id}."
