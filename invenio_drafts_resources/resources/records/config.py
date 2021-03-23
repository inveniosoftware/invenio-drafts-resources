# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft aware Record Resource Config override."""

from flask_resources.errors import create_errormap_handler
from flask_resources.parsers import HeadersParser
from invenio_records_resources.resources import \
    RecordResourceConfig as _RecordResourceConfig
from invenio_records_resources.resources.records.schemas_links import \
    ItemLinksSchema, SearchLinksSchema

from ..drafts.schemas_links import DraftLinksSchema


class RecordResourceConfig(_RecordResourceConfig):
    """Draft aware Record resource config."""

    draft_links_config = {
        "record": DraftLinksSchema
    }


class RecordVersionsResourceConfig(RecordResourceConfig):
    """Record resource version config."""

    list_route = "/records/<pid_value>/versions"

    item_route = "/records/<pid_value>/versions/latest"

    links_config = {
        "record": ItemLinksSchema.create(template='/api/records/{pid_value}'),
        # TODO: fix search links schema to pass the <pid_value>
        "search":  SearchLinksSchema.create(
            template='/api/records/{pid_value}/versions{?params*}')
    }

    request_headers_parser = {
        "search": HeadersParser(None),
    }
