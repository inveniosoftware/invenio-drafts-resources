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
from flask_resources.resources import ResourceConfig
from invenio_records_resources.responses import RecordResponse
from invenio_records_resources.serializers import RecordJSONSerializer

from ..service import DraftService
from ..service.schemas import DraftSchemaJSONV1

# TODO: Get rid of them when implementation is done
STUB_ITEM_RESULT = ({"TODO": "IMPLEMENT ME"}, 200)
STUB_LIST_RESULT = ([{"TODO": "IMPLEMENT ME"}], 200)


class DraftResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/draft"
    response_handlers = {
        "application/json": RecordResponse(
            RecordJSONSerializer(schema=DraftSchemaJSONV1)
        )
    }


class DraftResource(SingletonResource):
    """Draft resource."""

    default_config = DraftResourceConfig

    def __init__(self, config=None, service_cls=DraftService,
                 *args, **kwargs):
        """Constructor."""
        super(DraftResource, self).__init__(
            config=config if config else self.default_config,
            *args,
            **kwargs
        )
        self.service_cls = service_cls

    def read(self, *args, **kwargs):
        """Read an item."""
        return STUB_ITEM_RESULT

    def create(self, *args, **kwargs):
        """Create an item."""
        data = resource_requestctx.request_content
        identity = g.identity
        return self.service_cls.create(data, identity), 200

    def update(self, *args, **kwargs):
        """Update an item."""
        return STUB_ITEM_RESULT

    def delete(self, *args, **kwargs):
        """Delete an item."""
        return STUB_ITEM_RESULT


class DraftVersionResourceConfig(ResourceConfig):
    """Draft resource config."""

    list_route = "/records/<pid_value>/versions"


class DraftVersionResource(CollectionResource):
    """Draft version resource."""

    default_config = DraftVersionResourceConfig

    def search(self, *args, **kwargs):
        """Perform a search over the items."""
        return STUB_LIST_RESULT

    def create(self, *args, **kwargs):
        """Create an item."""
        return STUB_ITEM_RESULT


class DraftActionResourceConfig(ResourceConfig):
    """Draft action resource config."""

    list_route = "/records/<pid_value>/draft/actions/<action>"


class DraftActionResource(SingletonResource):
    """Draft action resource."""

    default_config = DraftActionResourceConfig

    def create(self, *args, **kwargs):
        """Any POST business logic."""
        if resource_requestctx.route["action"] == "publish":
            return STUB_ITEM_RESULT
        return {}, 200
