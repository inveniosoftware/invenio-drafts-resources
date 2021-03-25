# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Custom service results."""

from flask import current_app
from invenio_records_resources.services.records.results import RecordList
from marshmallow_utils.links import LinksFactory


def _current_host():
    """Function used to provide the current hostname to the link store."""
    if current_app:
        return current_app.config['SITE_HOSTNAME']
    return None


class VersionsList(RecordList):
    """A specialized Result List class made for search versions links.

    The sole reason this exists is to be able to pass the pid_value
    to the dict that is used to generate links.
    """

    def __init__(self, service, identity, results, params,
                 links_config=None, pid_value=None):
        """Overridden RecordList Constructor.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the search results
        :params params: dictionary of the query parameters
        :params links_config: a links store config
        :params pid_value: pid_value of record
        """
        super().__init__(
            service,
            identity,
            results,
            params,
            links_config=links_config
        )
        self._pid_value = pid_value

    @property
    def links(self):
        """Get the search result links."""
        links = LinksFactory(host=_current_host, config=self._links_config)
        schema = self._service.schema_search_links

        # TODO: Implements a gradual refactoring of schema dumping
        data = schema.dump(
            # It ain't pretty but it will do
            {
                **self._params,
                "_pagination": self.pagination,
                "pid_value": self._pid_value
            },
            context=dict(
                identity=self._identity,
                links_factory=links,
                links_namespace="search",
            )
        )

        return data.get("links")
