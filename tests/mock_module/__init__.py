# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Mock test module."""

from .resource import (
    resource_for_mocks_draft_files,
    resource_for_mocks_files,
    resource_for_mocks_records,
)
from .service import (
    draft_file_service,
    file_service,
)


# Blueprints
def create_bp_of_mocks_records(app):
    """Create mocks API Blueprint."""
    return resource_for_mocks_records.as_blueprint()


def create_bp_of_mocks_draft_files(app):
    """Create mocks API Blueprint."""
    return resource_for_mocks_draft_files.as_blueprint()


def create_bp_of_mocks_files(app):
    """Create mocks API Blueprint."""
    return resource_for_mocks_files.as_blueprint()


# Finalize
def finalize_app(app):
    """Init app."""
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    registry = app.extensions["invenio-records-resources"].registry
    registry.register(file_service, service_id="service-for-mocks-files")
    registry.register(draft_file_service, service_id="service-for-mocks-draft-files")
