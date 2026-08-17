# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Celery tasks to manage drafts."""

from datetime import timedelta

from celery import shared_task
from invenio_records_resources.proxies import current_service_registry


@shared_task(ignore_result=True)
def cleanup_drafts(seconds=3600, search_gc_deletes=60, batch_size=1000):
    """Hard delete of soft deleted drafts.

    :param int seconds: numbers of seconds that should pass since the
        last update of the draft in order to be hard deleted.
    :param int search_gc_deletes: time in seconds, corresponding to the search cluster
        setting `index.gc_deletes` (see https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete.html#delete-versioning),
        default to 60 seconds. Search cluster caches deleted documents for `index.gc_deletes` seconds.
    :param int batch_size: number of drafts to delete per batch (bounds memory).
    """
    timedelta_param = timedelta(seconds=seconds)
    service = current_service_registry.get("records")
    service.cleanup_drafts(
        timedelta_param, search_gc_deletes=search_gc_deletes, batch_size=batch_size
    )
