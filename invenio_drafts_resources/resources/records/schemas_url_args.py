# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schemas for parameter parsing."""


from invenio_records_resources.resources.records.schemas_url_args import \
    SearchURLArgsSchema as _SearchURLArgsSchema
from marshmallow import fields


class SearchURLArgsSchema(_SearchURLArgsSchema):
    """Schema for search URL args."""

    allversions = fields.Boolean()
