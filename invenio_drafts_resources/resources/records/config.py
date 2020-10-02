# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft aware Record Resource Config override."""

from invenio_records_resources.resources import \
    RecordResourceConfig as _RecordResourceConfig

from ..drafts.schemas_links import DraftLinksSchema


class RecordResourceConfig(_RecordResourceConfig):
    """Draft aware Record resource config."""

    draft_links_config = {
        "record": DraftLinksSchema
    }
