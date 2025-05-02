# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

from invenio_audit_logs.actions import AuditAction


def record_actions():
    """Function to add actions to the registry."""
    return {
        "draft.create": AuditAction(
            name="draft.create",
            message_template="User {user_id} created the draft {resource_id}.",
        ),
        "draft.edit": AuditAction(
            name="draft.edit",
            message_template="User {user_id} updated the draft {resource_id}.",
        ),
        "record.publish": AuditAction(
            name="record.publish",
            message_template="User {user_id} published the record {resource_id}.",
        ),
        "draft.delete": AuditAction(
            name="draft.delete",
            message_template="User {user_id} deleted the draft {resource_id}.",
        ),
        "draft.new_version": AuditAction(
            name="draft.new_version",
            message_template="User {user_id} created a new version {resource_id}.",
        ),
    }
