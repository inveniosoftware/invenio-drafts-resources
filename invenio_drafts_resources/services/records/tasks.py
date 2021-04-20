
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks to curate records."""

@async.shared_task(ignore_result=True)
def async_hard_delete(cls, record)
   hard_delete(cls, record)

def hard_delete(cls, record):
  pass