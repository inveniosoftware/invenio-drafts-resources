# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask_resources.resources import ResourceConfig
from invenio_records_resources.responses import RecordResponse

from ..serializers import RecordDraftJSONSerializer


class DraftResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/draft"
    response_handlers = {
        "application/json": RecordResponse(RecordDraftJSONSerializer())
    }


class DraftVersionResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/versions"
    response_handlers = {
        "application/json": RecordResponse(RecordDraftJSONSerializer())
    }


class DraftActionResourceConfig(ResourceConfig):
    """Draft action resource config."""

    list_route = "/records/<pid_value>/draft/actions/<action>"
    response_handlers = {
        "application/json": RecordResponse(RecordDraftJSONSerializer())
    }
