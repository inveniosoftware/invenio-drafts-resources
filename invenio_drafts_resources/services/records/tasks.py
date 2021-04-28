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
from invenio_base.utils import obj_or_import_string


@shared_task(ignore_result=True)
def cleanup_drafts(current_service_imp, seconds=3600):
    """Hard delete of soft deleted drafts.

    :param int seconds: numbers of seconds that should pass since the
        last update of the draft in order to be hard deleted.
    """
    timedelta_param = timedelta(seconds=seconds)
    current_service = obj_or_import_string(current_service_imp)
    current_service.cleanup_drafts(timedelta_param)
