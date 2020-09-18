# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft API."""

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.systemfields import ModelField
from invenio_records_resources.records import Record as RecordBase
from invenio_records_resources.records.systemfields import PIDField



class Record(RecordBase):
    """Record base API."""

    # Configuration
    model_cls = None

    pid = PIDField('id', provider=RecordIdProviderV2)


class Draft(Record):
    """Draft base API for metadata creation and manipulation."""

    # WHY: We want to force the model_cls to be specified by the user
    # No default one is given, only the base.
    model_cls = None

    expires_at = ModelField()

    fork_version_id = ModelField()

    conceptpid = PIDField('conceptpid', provider=RecordIdProviderV2)
