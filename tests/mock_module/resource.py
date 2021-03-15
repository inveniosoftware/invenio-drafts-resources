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
    DraftFileActionResource as DraftFileActionResourceBase
from invenio_drafts_resources.resources import \
    DraftFileActionResourceConfig as DraftFileActionResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftFileResource as DraftFileResourceBase
from invenio_drafts_resources.resources import \
    DraftFileResourceConfig as DraftFileResourceConfigBase
from invenio_drafts_resources.resources import \
    DraftResource as DraftResourceBase
from invenio_drafts_resources.resources import \
    DraftResourceConfig as DraftResourceConfigBase
from invenio_drafts_resources.resources import \
    RecordFileActionResource as RecordFileActionResourceBase
from invenio_drafts_resources.resources import \
    RecordFileActionResourceConfig as RecordFileActionResourceConfigBase
from invenio_drafts_resources.resources import \
    RecordFileResource as RecordRecordFileResourceBase
from invenio_drafts_resources.resources import \
    RecordFileResourceConfig as RecordFileResourceConfigBase
from invenio_drafts_resources.resources import \
    RecordResource as RecordResourceBase
from invenio_drafts_resources.resources import \
    RecordResourceConfig as RecordResourceConfigBase
from invenio_drafts_resources.resources import \
    RecordVersionsResource as RecordVersionsResource
from invenio_drafts_resources.resources import \
    RecordVersionsResourceConfig as RecordVersionsResourceConfigBase


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


##
# RECORDS
##
class RecordResourceConfig(RecordResourceConfigBase):
    """Mock record resource configuration."""

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
    """Mock record resource."""

    default_config = RecordResourceConfig


class RecordFileResourceConfig(RecordFileResourceConfigBase):
    """Mock record file resource."""

    item_route = "/mocks/<pid_value>/files/<key>"
    list_route = "/mocks/<pid_value>/files"


class RecordFileResource(RecordRecordFileResourceBase):
    """Mock record file resource config."""

    default_config = RecordFileResourceConfig


class RecordFileActionResourceConfig(RecordFileActionResourceConfigBase):
    """Mock record file resource."""

    list_route = "/mocks/<pid_value>/files/<key>/<action>"


class RecordFileActionResource(RecordFileActionResourceBase):
    """Mock record file resource config."""

    default_config = RecordFileActionResourceConfig


##
# DRAFTS
##
class DraftResourceConfig(DraftResourceConfigBase):
    """Mock draft resource configuration."""

    list_route = "/mocks/<pid_value>/draft"

    links_config = {
        # TODO: Revisit naming for "record"?
        "record": DraftLinksSchema
    }


class DraftResource(DraftResourceBase):
    """Mock draft resource."""

    default_config = DraftResourceConfig


class DraftActionResourceConfig(DraftActionResourceConfigBase):
    """Mock draft action resource configuration."""

    list_route = "/mocks/<pid_value>/draft/actions/<action>"

    action_commands = {
        "create": {
            "publish": "publish",
            "command": "not_implemented"
        }
    }

    links_config = {
        "record": DraftLinksSchema
    }

    record_links_config = {
        "record": RecordLinksSchema
    }


class DraftActionResource(DraftActionResourceBase):
    """Mock draft action resource."""

    default_config = DraftActionResourceConfig

    def create_command(self, action, operation):
        """Dummy handler."""
        return self._get_cmd_func(action, operation).to_dict(), 200


class DraftFileResourceConfig(DraftFileResourceConfigBase):
    """Mock record file resource."""

    item_route = "/mocks/<pid_value>/draft/files/<key>"
    list_route = "/mocks/<pid_value>/draft/files"


class DraftFileResource(DraftFileResourceBase):
    """Mock record file resource config."""

    default_config = DraftFileResourceConfig


class DraftFileActionResourceConfig(DraftFileActionResourceConfigBase):
    """Mock record file resource."""

    list_route = "/mocks/<pid_value>/draft/files/<key>/<action>"


class DraftFileActionResource(DraftFileActionResourceBase):
    """Mock record file resource config."""

    default_config = DraftFileActionResourceConfig


##
# VERSIONING
##
class RecordVersionsResourceConfig(RecordVersionsResourceConfigBase):
    """Mock draft version resource configuration."""

    list_route = "/mocks/<pid_value>/versions"


class RecordVersionsResource(RecordVersionsResource):
    """Mock draft version resource."""

    default_config = RecordVersionsResourceConfig
