# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Link Builders."""


from invenio_records_resources.linker.builders import LinkBuilder


class DraftSelfLinkBuilder(LinkBuilder):
    """Builds draft self link."""

    key = "self"
    action = "read"
    route_attr = "draft_route"


class DraftPublishLinkBuilder(LinkBuilder):
    """Builds draft "publish" link."""

    key = "publish"
    action = "publish"
    route_attr = "draft_action_route"


class RecordEditLinkBuilder(LinkBuilder):
    """Builds record "edit" link."""

    key = "edit"
    action = "create"
    route_attr = "draft_route"
