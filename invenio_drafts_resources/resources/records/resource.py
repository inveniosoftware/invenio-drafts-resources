# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask import g
from flask_resources.context import resource_requestctx
from invenio_records_resources.resources import \
    RecordResource as _RecordResource

from .config import RecordResourceConfig


class RecordResource(_RecordResource):
    """Draft-aware RecordResource."""

    default_config = RecordResourceConfig

    def create(self):
        """Create an item."""
        data = resource_requestctx.request_content
        item = self.service.create(
            g.identity, data, links_config=self.config.draft_links_config)
        return item.to_dict(), 201
