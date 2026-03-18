# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Audit log context resolvers."""

from flask import has_request_context, request
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_users_resources.entity_resolvers import UserResolver
from sqlalchemy import desc


class UserContext(object):
    """Payload generator for audit log using the user entity resolver."""

    def __init__(self, key="user"):
        """Ctor."""
        self.key = key
        self.resolver = UserResolver()

    def __call__(self, data, lookup_key="user_id", **kwargs):
        """Update data with resolved user data."""
        entity_ref = dict_lookup(data, lookup_key)
        entity_proxy = self.resolver.get_entity_proxy({self.key: entity_ref})
        entity_data = entity_proxy.resolve()
        dict_set(data, self.key, entity_data)


class RecordContext(object):
    """Payload generator for audit log to get record auditing metadata."""

    def __call__(self, data, **kwargs):
        """Update data with resolved record data."""
        record = kwargs.get("record", None)
        if record is None:
            return
        latest_revision = (
            record.model.versions.order_by(None)
            .order_by(desc("transaction_id"))
            .first()
        )
        dict_set(data, "metadata.revision_id", latest_revision.transaction_id)


class ParentContext(object):
    """Payload generator for audit log to get parent data."""

    def __call__(self, data, **kwargs):
        """Update data with resolved parent data."""
        parent = kwargs.get("parent", None)
        if parent is None:
            return
        dict_set(data, "metadata.parent_pid", parent.pid.pid_value)


class RequestContext(object):
    """Payload generator for audit log using the request context."""

    def __call__(self, data, **kwargs):
        """Update data with resolved request data."""
        # IMPORTANT! DON'T COPY THIS, PLEASE DON'T DO THIS EVER...
        if has_request_context():
            ip = request.headers.get("REMOTE_ADDR") or request.remote_addr
            dict_set(data, "metadata.ip_address", ip)

            session = request.cookies.get("SESSION") or request.cookies.get("session")
            dict_set(data, "metadata.session", session)
