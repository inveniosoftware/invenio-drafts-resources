# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from flask import g
from flask_resources import CollectionResource, SingletonResource
from flask_resources.context import resource_requestctx

from ..services import DraftVersionService, RecordDraftService
from .draft_config import DraftActionResourceConfig, DraftResourceConfig, \
    DraftVersionResourceConfig


class DraftResource(SingletonResource):
    """Draft resource."""

    default_config = DraftResourceConfig

    def __init__(self, service=None, *args, **kwargs):
        """Constructor."""
        super(DraftResource, self).__init__(*args, **kwargs)
        self.service = service or RecordDraftService()

    def read(self, *args, **kwargs):
        """Read an item."""
        identity = g.identity
        id_ = resource_requestctx.route["pid_value"]

        return self.service.read_draft(id_, identity), 200

    def create(self, *args, **kwargs):
        """Create an item."""
        data = resource_requestctx.request_content
        identity = g.identity
        id_ = resource_requestctx.route["pid_value"]

        return self.service.edit(id_, data, identity), 201

    def update(self, *args, **kwargs):
        """Update an item."""
        # TODO: IMPLEMENT ME!
        return self.service.update(), 200

    def delete(self, *args, **kwargs):
        """Delete an item."""
        # TODO: IMPLEMENT ME!
        return self.service.delete(), 200


class DraftVersionResource(CollectionResource):
    """Draft version resource."""

    default_config = DraftVersionResourceConfig

    def __init__(self, service=None, *args, **kwargs):
        """Constructor."""
        super(DraftVersionResource, self).__init__(*args, **kwargs)
        self.service = service or DraftVersionService()

    def search(self, *args, **kwargs):
        """Perform a search over the items."""
        # TODO: IMPLEMENT ME!
        return self.service.search()

    def create(self, *args, **kwargs):
        """Create an item."""
        identity = g.identity
        id_ = resource_requestctx.route["pid_value"]

        return self.service.new_version(id_, identity), 201


class DraftActionResource(SingletonResource):
    """Draft action resource."""

    default_config = DraftActionResourceConfig

    def __init__(self, service=None, *args, **kwargs):
        """Constructor."""
        super(DraftActionResource, self).__init__(*args, **kwargs)
        self.service = service or RecordDraftService()

    def create(self, *args, **kwargs):
        """Any POST business logic."""
        # FIXME: Implement as CMD patter loaded from config
        if resource_requestctx.route["action"] == "publish":
            identity = g.identity
            id_ = resource_requestctx.route["pid_value"]
            return self.service.publish(id_, identity), 202
        return {}, 202
