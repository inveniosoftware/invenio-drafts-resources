"""Example resource."""

from uritemplate import URITemplate
from marshmallow import Schema
from marshmallow_utils.fields import Link

from invenio_drafts_resources.resources import \
    DraftActionResource as DraftActionResourceBase, \
    DraftActionResourceConfig as DraftActionResourceConfigBase, \
    DraftResource as DraftResourceBase, \
    DraftResourceConfig as DraftResourceConfigBase, \
    DraftVersionResource as DraftVersionResourceBase, \
    DraftVersionResourceConfig as DraftVersionResourceConfigBase, \
    RecordResource as RecordResourceBase, \
    RecordResourceConfig as RecordResourceConfigBase


class DraftLinksSchema(Schema):
    """Schema for a record's links."""

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

    # NOTE: Developers using drafts-resources need to do this
    draft_links_config = {
        "record": DraftLinksSchema()
    }


class RecordResource(RecordResourceBase):
    """Mock service."""

    default_config = RecordResourceConfig


class DraftResourceConfig(DraftResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/draft"

    links_config = {
        # TODO: Revisit naming for "record"?
        "record": DraftLinksSchema()
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


class DraftActionResource(DraftActionResourceBase):
    """Mock service."""

    default_config = DraftActionResourceConfig


class DraftVersionResourceConfig(DraftVersionResourceConfigBase):
    """Mock service configuration."""

    list_route = "/mocks/<pid_value>/versions"


class DraftVersionResource(DraftVersionResourceBase):
    """Mock service."""

    default_config = DraftVersionResourceConfig
