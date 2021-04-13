# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record schema."""

from marshmallow import Schema, fields, validate

from invenio_drafts_resources.services.records.schema import \
    RecordSchema as BaseRecordSchema


class MetadataSchema(Schema):
    """Basic metadata schema class."""

    title = fields.Str(required=True, validate=validate.Length(min=3))


class FilesOptionsSchema(Schema):
    """Basic files options schema class."""

    enabled = fields.Bool(missing=True)


class RecordSchema(BaseRecordSchema):
    """Schema for records in JSON."""

    metadata = fields.Nested(MetadataSchema)
    files = fields.Nested(FilesOptionsSchema)
