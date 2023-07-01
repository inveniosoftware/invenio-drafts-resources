# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_resources.resources import FileResource
from mock_module.resource import (
    DraftFileResourceConfig,
    FileResourceConfig,
    RecordResourceConfig,
)
from mock_module.service import ServiceConfig

from invenio_drafts_resources.resources import RecordResource
from invenio_drafts_resources.services.records import RecordService


@pytest.fixture(scope="module")
def service(file_service, draft_file_service):
    """Service instance."""
    return RecordService(
        ServiceConfig,
        files_service=file_service,
        draft_files_service=draft_file_service,
    )


@pytest.fixture(scope="module")
def record_resource(service):
    """Record resource."""
    return RecordResource(config=RecordResourceConfig, service=service)


@pytest.fixture(scope="module")
def file_resource(file_service):
    """File resource."""
    return FileResource(config=FileResourceConfig, service=file_service)


@pytest.fixture(scope="module")
def draft_file_resource(draft_file_service):
    """Draft file resource."""
    return FileResource(config=DraftFileResourceConfig, service=draft_file_service)


@pytest.fixture(scope="module")
def base_app(
    base_app,
    record_resource,
    file_resource,
    draft_file_resource,
    service,
    file_service,
    draft_file_service,
):
    """Application factory fixture."""
    base_app.register_blueprint(record_resource.as_blueprint())
    base_app.register_blueprint(file_resource.as_blueprint())
    base_app.register_blueprint(draft_file_resource.as_blueprint())

    registry = base_app.extensions["invenio-records-resources"].registry
    registry.register(service, service_id="mock-records-service")

    registry.register(file_service, service_id="mock-files-service")
    registry.register(draft_file_service, service_id="mock-draftfiles-service")

    yield base_app


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }
