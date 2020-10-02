# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft aware Record Links Schema."""

from marshmallow import Schema
from marshmallow_utils.fields import Link
from uritemplate import URITemplate


class RecordLinksSchema(Schema):
    """Schema for a record's links."""

    self = Link(
        template=URITemplate("/api/records/{pid_value}"),
        permission="read",
        params=lambda record: {'pid_value': record.pid.pid_value}
    )
