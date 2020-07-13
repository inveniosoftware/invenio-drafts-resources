# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs"""


from invenio_drafts_resources.resources import DraftFileActionResource, \
    DraftFileActionResourceConfig, DraftFileResource, \
    DraftFileResourceConfig

HEADERS = {"content-type": "application/json", "accept": "application/json"}

# TODO: IMPLEMENT ME!
