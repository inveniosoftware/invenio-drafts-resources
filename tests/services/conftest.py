# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_resources.services.files import FileService
from mock_module.api import Draft
from mock_module.service import FileServiceConfig, ServiceConfig

from invenio_drafts_resources.services.records import RecordService


@pytest.fixture(scope="module")
def service():
    """Service instance."""
    return RecordService(ServiceConfig)


@pytest.fixture(scope="module")
def file_service():
    """File service fixture."""
    return FileService(FileServiceConfig)


@pytest.fixture()
def example_record(app, db):
    """Example record."""
    record = Draft.create({}, metadata={'title': 'Test'})
    db.session.commit()
    return record


@pytest.fixture()
def app(app, location):
    """Auto-use location fixture."""
    return app
