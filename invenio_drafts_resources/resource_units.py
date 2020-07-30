# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resource units."""

from invenio_records_resources.resource_units import IdentifiedRecord


class IdentifiedRecordDraft(IdentifiedRecord):
    """Resource unit representing pid + Record data clump.

    Since a draft can be created for a non-existing record,
    it might not have a PID.
    """

    def __init__(self, pid=None, record=None, links=None):
        """Initialize the record state."""
        self.id = pid.pid_value if pid else None
        self.pids = [pid] if pid else []
        self.record = record
        self.links = links
