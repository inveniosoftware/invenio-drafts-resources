# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from invenio_records_resources.resources import RecordResourceConfig

from ..records import RecordLinksSchema
from ..drafts import DraftLinksSchema


class UserRecordResourceConfig(RecordResourceConfig):
    """User resource config."""

    list_route = "/user/records"
    item_route = None

    links_config = {
        "record": RecordLinksSchema,
        "draft": DraftLinksSchema
    }
