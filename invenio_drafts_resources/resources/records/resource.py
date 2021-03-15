# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

import hashlib

from flask import g, request
from flask_resources import CollectionResource
from flask_resources.context import resource_requestctx
from invenio_records_resources.config import ConfigLoaderMixin
from invenio_records_resources.resources import \
    RecordResource as _RecordResource

from invenio_drafts_resources.services.records import RecordDraftService

from .config import RecordResourceConfig, RecordVersionsResourceConfig


class RecordResource(_RecordResource):
    """Draft-aware RecordResource."""

    default_config = RecordResourceConfig

    def create(self):
        """Create an item."""
        data = resource_requestctx.request_content
        item = self.service.create(
            g.identity, data, links_config=self.config.draft_links_config)
        return item.to_dict(), 201


class RecordVersionsResource(CollectionResource, ConfigLoaderMixin):
    """Record versions resource."""

    default_config = RecordVersionsResourceConfig

    def __init__(self, service=None, config=None):
        """Constructor."""
        super(RecordVersionsResource, self).__init__(
            config=self.load_config(config))
        self.service = service or RecordDraftService()

    def _get_es_preference(self):
        user_agent = request.headers.get('User-Agent', '')
        ip = request.remote_addr
        user_hash = f"{ip}-{user_agent}".encode('utf8')
        alg = hashlib.md5()
        alg.update(user_hash)
        return alg.hexdigest()

    def search(self):
        """Perform a search over the record's versions.

        GET /records/:pid_value/versions
        """
        identity = g.identity
        hits = self.service.search_versions(
            resource_requestctx.route["pid_value"],
            identity=identity,
            params=resource_requestctx.url_args,
            links_config=self.config.links_config,
            es_preference=self._get_es_preference()
        )
        return hits.to_dict(), 200

    def create(self):
        """Create a new version.

        POST /records/:pid_value/versions
        """
        item = self.service.new_version(
            resource_requestctx.route["pid_value"],
            g.identity
        )
        return item.to_dict(), 201
