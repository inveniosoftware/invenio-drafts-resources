# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marshmallow JSON schema."""


from invenio_records_resources.schemas import RecordSchemaJSONV1
from invenio_records_resources.schemas.fields import SanitizedUnicode
from marshmallow import fields


class RecordDraftSchemaJSONV1(RecordSchemaJSONV1):
    """Schema for drafts v1 in JSON."""

    conceptrecid = SanitizedUnicode(
        attribute='metadata.conceptrecid',
        dump_only=True
    )
    expires_at = fields.Str()
