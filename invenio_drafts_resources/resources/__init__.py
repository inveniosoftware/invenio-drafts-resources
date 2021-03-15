# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from .drafts import DraftActionResource, DraftActionResourceConfig, \
    DraftLinksSchema, DraftResource, DraftResourceConfig
from .files import DraftFileActionResource, DraftFileActionResourceConfig, \
    DraftFileResource, DraftFileResourceConfig, RecordFileActionResource, \
    RecordFileActionResourceConfig, RecordFileResource, \
    RecordFileResourceConfig
from .records import RecordResource, RecordResourceConfig, \
    RecordVersionsResource, RecordVersionsResourceConfig
from .userrecords import UserRecordsResource
from .userrecords_config import UserRecordsResourceConfig

__all__ = (
    "DraftFileResourceConfig",
    "DraftFileResource",
    "DraftFileActionResourceConfig",
    "DraftFileActionResource",
    "RecordFileResourceConfig",
    "RecordFileResource",
    "RecordFileActionResourceConfig",
    "RecordFileActionResource",
    "DraftActionResource",
    "DraftActionResourceConfig",
    "DraftLinksSchema",
    "DraftResource",
    "DraftResourceConfig",
    "RecordResource",
    "RecordResourceConfig",
    "RecordVersionsResource",
    "RecordVersionsResourceConfig",
    "UserRecordsResource",
    "UserRecordsResourceConfig",
)
