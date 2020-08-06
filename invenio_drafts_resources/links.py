# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Link Builders."""


from invenio_records_resources.links import RecordLinkBuilder, api_route


class DraftSelfLinkBuilder(RecordLinkBuilder):
    """Builds draft self link."""

    def __init__(self, config):
        """Constructor."""
        super(DraftSelfLinkBuilder, self).__init__(
            key="self",
            route=api_route(config.draft_route),
            action="read",
            permission_policy=config.permission_policy_cls
        )


class DraftSelfHtmlLinkBuilder(RecordLinkBuilder):
    """Builds draft "self_html" link."""

    def __init__(self, config):
        """Constructor."""
        super(DraftSelfHtmlLinkBuilder, self).__init__(
            key="self_html",
            # TODO: Invenio-App-RDM needs to set deposit page in config
            route="/deposits/<pid_value>/edit",
            action="read",
            permission_policy=config.permission_policy_cls
        )


class DraftPublishLinkBuilder(RecordLinkBuilder):
    """Builds draft "publish" link."""

    def __init__(self, config):
        """Constructor."""
        super(DraftPublishLinkBuilder, self).__init__(
            key="publish",
            route=api_route(
                config.draft_action_route.replace(
                    "<action>", "publish"
                )
            ),
            action="publish",
            permission_policy=config.permission_policy_cls
        )


class RecordEditLinkBuilder(RecordLinkBuilder):
    """Builds record "edit" link."""

    def __init__(self, config):
        """Constructor."""
        super(RecordEditLinkBuilder, self).__init__(
            key="edit",
            route=api_route(config.draft_route),
            action="create",
            permission_policy=config.permission_policy_cls
        )
