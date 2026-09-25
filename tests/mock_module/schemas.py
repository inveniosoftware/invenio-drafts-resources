# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Record schema."""

from marshmallow import Schema, fields, validate
from marshmallow.utils import get_value
from marshmallow_utils.fields import SanitizedUnicode

from invenio_drafts_resources.services.records.schema import (
    RecordSchema as BaseRecordSchema,
)


class MetadataSchema(Schema):
    """Basic metadata schema class."""

    title = fields.Str(required=True, validate=validate.Length(min=3))


class FilesSchema(Schema):
    """Basic files schema class."""

    enabled = fields.Bool(load_default=True)
    # allow unsetting
    default_preview = SanitizedUnicode(allow_none=True)
    order = fields.List(SanitizedUnicode())

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        value = getattr(obj, attr, default)

        if attr in ("default_preview", "order") and not value:
            return default

        return value


class RecordSchema(BaseRecordSchema):
    """Schema for records in JSON."""

    metadata = fields.Nested(MetadataSchema)
    files = fields.Nested(FilesSchema)
    media_files = fields.Nested(FilesSchema)

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        if attr == "files":
            return getattr(obj, attr, default)
        else:
            return get_value(obj, attr, default)
