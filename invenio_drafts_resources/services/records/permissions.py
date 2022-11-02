# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2022 TU Wien.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Drafts permissions."""

from invenio_records_permissions.generators import AnyUser, DisableIfReadOnly
from invenio_records_permissions.policies.records import (
    RecordPermissionPolicy as RecordPermissionPolicyBase,
)


class RecordPermissionPolicy(RecordPermissionPolicyBase):
    """Custom permission policy."""

    # FIXME: Revist this along the development
    # Default create should be "authenticated"?
    # TODO: Subclass records-resources policy and add *_draft actions
    can_create = [AnyUser(), DisableIfReadOnly()]
    can_new_version = [AnyUser(), DisableIfReadOnly()]
    can_edit = [AnyUser(), DisableIfReadOnly()]
    can_publish = [AnyUser(), DisableIfReadOnly()]
    can_read_draft = [AnyUser()]
    can_update_draft = [AnyUser(), DisableIfReadOnly()]
    can_delete_draft = [AnyUser(), DisableIfReadOnly()]
