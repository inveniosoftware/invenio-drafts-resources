# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records service copmonent base classes."""

from invenio_records_resources.services.components import ServiceComponent


class RelationsComponent(ServiceComponent):
    """Service component for PID relations integration."""
