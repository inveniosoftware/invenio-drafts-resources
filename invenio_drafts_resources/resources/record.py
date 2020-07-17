# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask import g
from flask_resources.context import resource_requestctx
from invenio_records_resources.resources import \
    RecordResource as _RecordResource

from ..services import DraftService


class RecordResource(_RecordResource):
    """Record resource compatible with draft creation."""

    def __init__(self, service=None, *args, **kwargs):
        """Constructor."""
        super(RecordResource, self).__init__(*args, **kwargs)
        self.service = service or DraftService()

    def create(self, *args, **kwargs):
        """Create an item."""
        data = resource_requestctx.request_content
        identity = g.identity
        return self.service.create_new(data, identity), 200
