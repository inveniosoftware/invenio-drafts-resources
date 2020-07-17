# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from .deposit import DepositResource, DepositResourceConfig
from .draft import DraftActionResource, DraftActionResourceConfig, \
    DraftResource, DraftResourceConfig, DraftVersionResource, \
    DraftVersionResourceConfig
from .draft_file import DraftFileActionResource, \
    DraftFileActionResourceConfig, DraftFileResource, \
    DraftFileResourceConfig

__all__ = (
    "DepositResource",
    "DepositResourceConfig",
    "DraftResource",
    "DraftResourceConfig",
    "DraftActionResource",
    "DraftActionResourceConfig",
    "DraftVersionResource",
    "DrafVersiontResourceConfig",
    "DraftFileActionResourceConfig",
    "DraftFileActionResource",
    "DraftFileResourceConfig",
    "DraftFileResource",
)
