# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio User Resources module to create REST APIs."""

from flask import abort, g
from flask_resources import CollectionResource
from flask_resources.context import resource_requestctx
from invenio_records_resources.config import ConfigLoaderMixin

from ...services import RecordDraftService
from .config import UserRecordResourceConfig



class UserRecordsResource(CollectionResource, ConfigLoaderMixin):
    """Draft version resource."""

    default_config = UserRecordResourceConfig

    def __init__(self, service=None, config=None):
        """Constructor."""
        super(UserRecordsResource, self).__init__(
            config=self.load_config(config))
        self.service = service or RecordDraftService()

    def search(self):
        """Perform a search over the records and drafts the user has access to.

        GET /user/records
        """
        # TODO: Revisit, some extra filtering for access might be needed.
        identity = g.identity
        hits = self.service.search(
            identity=identity,
            params=resource_requestctx.url_args,
            links_config=self.config.links_config,
        )
        return hits.to_dict(), 200

    def create(self):
        """Creation is not allowed on this endpoint."""
        raise abort(405)
