# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Draft API."""

from .models import DraftMetadata


class Draft(Record):
    """Draft API for metadata creation and manipulation."""

    # WHY: We want to force the model_cls to be specified by the user
    # No default one is given, only the base.
    def __init__(self, model_cls, *args, **kwargs):
        """Constructor."""
        super(Draft, self).__init__(model_cls=model_cls, *args, **kwargs)
