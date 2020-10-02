# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Example resource."""

from marshmallow import Schema
from marshmallow_utils.fields import Link
from uritemplate import URITemplate

from invenio_drafts_resources.resources import \
    DraftActionResource as DraftActionResourceBase
from invenio_drafts_resources.resources import \
    DraftActionResourceConfig as DraftActionResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftResource as DraftResourceBase
from invenio_drafts_resources.resources import \
    DraftResourceConfig as DraftResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftVersionResource as DraftVersionResourceBase
from invenio_drafts_resources.resources import \
    DraftVersionResourceConfig as DraftVersionResourceConfigBase
from invenio_drafts_resources.resources import \
    RecordResource as RecordResourceBase
from invenio_drafts_resources.resources import \
    RecordResourceConfig as RecordResourceConfigBase


class RecordLinksSchema(Schema):
    """Schema for a record's links."""

    self = Link(
        template=URITemplate("/api/mocks/{pid_value}"),
        permission="read",
        params=lambda record: {'pid_value': record.pid.pid_value}
    )
    # TODO: Add delete, files, ...


class DraftLinksSchema(Schema):
    """Schema for a draft's links."""

    self = Link(
        template=URITemplate("/api/mocks/{pid_value}/draft"),
        permission="read",
        params=lambda draft: {'pid_value': draft.pid.pid_value}
    )
    publish = Link(
        template=URITemplate("/api/mocks/{pid_value}/draft/actions/publish"),
        permission="publish",
        params=lambda draft: {'pid_value': draft.pid.pid_value}
    )


class RecordResourceConfig(RecordResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks"
    item_route = f"{list_route}/<pid_value>"

    links_config = {
        "record": RecordLinksSchema
    }

    # NOTE: Developers using drafts-resources need to do this
    draft_links_config = {
        "record": DraftLinksSchema
    }


class RecordResource(RecordResourceBase):
    """Mock service."""

    default_config = RecordResourceConfig


class DraftResourceConfig(DraftResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/draft"

    links_config = {
        # TODO: Revisit naming for "record"?
        "record": DraftLinksSchema
    }


class DraftResource(DraftResourceBase):
    """Mock service."""

    default_config = DraftResourceConfig


class DraftActionResourceConfig(DraftActionResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/draft/actions/<action>"

    action_commands = {
        "publish": "publish",
        "command": "not_implemented"
    }

    record_links_config = {
        "record": RecordLinksSchema
    }


class DraftActionResource(DraftActionResourceBase):
    """Mock service."""

    default_config = DraftActionResourceConfig


class DraftVersionResourceConfig(DraftVersionResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/versions"


class DraftVersionResource(DraftVersionResourceBase):
    """Mock service."""

    default_config = DraftVersionResourceConfig
