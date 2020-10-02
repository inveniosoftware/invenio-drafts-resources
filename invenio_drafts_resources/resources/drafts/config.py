# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from invenio_records_resources.resources import RecordResourceConfig

from ..records import RecordLinksSchema
from .schemas_links import DraftLinksSchema


class DraftResourceConfig(RecordResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/draft"
    item_route = None

    links_config = {
        "record": DraftLinksSchema
    }


class DraftActionResourceConfig(RecordResourceConfig):
    """Draft action resource config."""

    list_route = "/records/<pid_value>/draft/actions/<action>"
    item_route = None  # To avoid issues, due to inheritance.

    actions = {
        "publish": "publish",
    }

    record_links_config = {
        "record": RecordLinksSchema
    }


class DraftVersionResourceConfig(RecordResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/versions"
    # TODO: REVISIT
