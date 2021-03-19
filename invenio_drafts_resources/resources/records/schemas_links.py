# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft aware Record Links Schema."""

from invenio_records_resources.resources.records.schemas_links import ItemLink
from marshmallow import Schema


class RecordLinksSchema(Schema):
    """Schema for a record's links."""

    self = ItemLink(template="/api/records/{pid_value}")
