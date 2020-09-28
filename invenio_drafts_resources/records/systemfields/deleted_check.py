# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record deleted check field.

The DeletedCheck is used to check if an associated PID is in a given state.
For instance:

.. code-block:: python

    class Record():
        is_published = DeletedCheck()

"""

from invenio_records.systemfields import SystemField


class DeletedCheck(SystemField):
    """PID status field which checks against an expected status."""

    def __init__(self, key='is_deleleted'):
        """Initialize the PIDField.

        :param key: Attribute name of the PIDField to use for status check.
        :param status: The status or list of statuses which will return true.
        """
        super().__init__(key=key)

    #
    # Data descriptor methods (i.e. attribute access)
    #
    def __get__(self, record, owner=None):
        """Get the current status."""
        return getattr(record, self.key)

    def post_create(self, record):
        """Called after a record is created."""
        setattr(record, self.attr_name, True)

    def post_delete(self, record, force=False):
        """Called after a record is deleted."""
        setattr(record, self.attr_name, False)
