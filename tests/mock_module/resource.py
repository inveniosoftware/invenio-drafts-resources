# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Example resource."""

from invenio_records_resources.resources import (
    FileResource,
)
from invenio_records_resources.resources import (
    FileResourceConfig as FileResourceConfigBase,
)

from invenio_drafts_resources.resources import RecordResource, RecordResourceConfig

from .service import (
    draft_file_service,
    file_service,
    record_service,
)


# Config
class RecordResourceConfig(RecordResourceConfig):
    """Mock record resource configuration."""

    blueprint_name = "mocks"
    url_prefix = "/mocks"


class FileResourceConfig(FileResourceConfigBase):
    """Mock record file resource."""

    blueprint_name = "mocks_files"
    url_prefix = "/mocks/<pid_value>"


class DraftFileResourceConfig(FileResourceConfigBase):
    """Mock record file resource."""

    blueprint_name = "mocks_draft_files"
    url_prefix = "/mocks/<pid_value>/draft"


# Resources
resource_for_mocks_draft_files = FileResource(
    DraftFileResourceConfig,
    draft_file_service,
)
resource_for_mocks_files = FileResource(FileResourceConfig, file_service)
resource_for_mocks_records = RecordResource(RecordResourceConfig, record_service)
