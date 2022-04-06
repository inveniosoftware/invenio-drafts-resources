# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Celery tasks to manage drafts."""

from datetime import timedelta

from celery import shared_task
from invenio_records_resources.proxies import current_service_registry


@shared_task(ignore_result=True)
def cleanup_drafts(seconds=3600):
    """Hard delete of soft deleted drafts.

    :param int seconds: numbers of seconds that should pass since the
        last update of the draft in order to be hard deleted.
    """
    timedelta_param = timedelta(seconds=seconds)
    service = current_service_registry.get("records")
    service.cleanup_drafts(timedelta_param)
