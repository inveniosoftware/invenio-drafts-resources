# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Versions field."""

import uuid
from copy import copy

from invenio_db import db
from invenio_records.systemfields import RelatedModelField
from invenio_records.systemfields.base import SystemField
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError


def uuid_or_none(val):
    """Convert string to UUID object."""
    if val is not None and not isinstance(val, uuid.UUID):
        return uuid.UUID(val)
    return val


class VersionsManager:
    """Versions state manager."""

    def __init__(self, record, dump=None):
        """Initialize the versions manager."""
        self._record = record
        self._state = None
        if dump is not None:
            self.load(dump)

    def copy_to(self, record):
        """Create a copy of the version manager and set on another record."""
        record.model.index = self.index
        version_manager = self.__class__(record)
        version_manager._state = self._state
        return version_manager

    #
    # Record managed attributes
    #
    @property
    def model_cls(self):
        """Get versions state management model."""
        return self._record.versions_model_cls

    @property
    def parent_id(self):
        """Get versions state management model."""
        return self._record.model.parent_id

    @property
    def index(self):
        """Get the version index of the record/draft."""
        return self._record.model.index

    #
    # Parent managed attributes
    #
    @property
    def latest_id(self):
        """The id of the latest published record/draft."""
        return self.state().latest_id

    @property
    def latest_index(self):
        """The version index of the latest published record/draft."""
        return self.state().latest_index

    @property
    def next_draft_id(self):
        """The id of the next draft (and record)."""
        return self.state().next_draft_id

    #
    # Computed attributes
    #
    @property
    def is_latest(self):
        """Check if the record/draft id is the latest published record id."""
        return self.latest_id == self._record.id

    @property
    def is_latest_draft(self):
        """Check if the record/draft id is the latest draft id."""
        if self.next_draft_id:
            return self.next_draft_id == self._record.id
        else:
            return self.latest_id == self._record.id

    @property
    def next_index(self):
        """Get the next parent index."""
        return self.latest_index + 1 if self.latest_index is not None else 1

    #
    # State management methods
    #
    def state(self, refresh=False):
        """Retrieve the versions state."""
        if self._state is None or refresh:
            # Get object if it exists
            self._state = self.model_cls.query.filter_by(
                parent_id=self.parent_id).one_or_none()
            if self._state is None:
                # Object doesn't exists, so create it.
                self._state = self.model_cls(parent_id=self.parent_id)
                db.session.add(self._state)
        return self._state

    def set_next(self):
        """Set this record as the next draft."""
        self.state().next_draft_id = self._record.id
        self._record.model.index = self.next_index

    def clear_next(self):
        """Unset this record as the next draft."""
        self.state().next_draft_id = None
        self._record.model.index = None

    def set_latest(self):
        """Set this record as the latest published record."""
        self.state().latest_id = self._record.id
        self.state().latest_index = self.index
        self.state().next_draft_id = None

    #
    # Dump/load
    #
    def dump(self):
        """Dump the versions state to the index."""
        return dict(
            latest_id=self.latest_id,
            latest_index=self.latest_index,
            next_draft_id=self.next_draft_id,
            is_latest=self.is_latest,
            is_latest_draft=self.is_latest_draft,
            index=self.index,
        )

    def load(self, dump):
        """Load the state."""
        self._state = self.model_cls(
            parent_id=self.parent_id,
            latest_id=uuid_or_none(dump['latest_id']),
            latest_index=dump['latest_index'],
            next_draft_id=uuid_or_none(dump['next_draft_id']),
        )
        if self.index != dump['index']:
            self._record.model.index = dump['index']

    def __repr__(self):
        """Return repr(self)."""
        return (
            f"<{type(self).__name__} (parent_id: {self.parent_id}, "
            f"index: {self.index}, latest_id: {self.latest_id}, "
            f"latest_index: {self.latest_index}, "
            f"next_draft_id: {self.next_draft_id})>"
        )


class VersionsField(SystemField):
    """Versions field."""

    def __init__(self, create=True, set_next=False, set_latest=False):
        """Initialise the versions field."""
        self._create = create
        self._set_next = set_next
        self._set_latest = set_latest
        super().__init__()

    def obj(self, record):
        """Get the version manager."""
        obj = self._get_cache(record)
        if obj is not None:
            return obj
        obj = VersionsManager(record)
        self._set_cache(record, obj)
        return obj

    def set_obj(self, record, versions):
        """Set an version manager on the record."""
        assert isinstance(versions, VersionsManager)
        versions = versions.copy_to(record)
        self._set_cache(record, versions)

    #
    # Record life-cycle hooks
    #
    def post_create(self, record):
        """Called after a record is created."""
        # The parent record is created on pre_create.
        versions = self.obj(record)
        if self._create and self._set_next:
            # if fork is none - it's a new?
            versions.set_next()
        elif self._create and self._set_latest:
            versions.set_latest()

    def pre_delete(self, record, force=False):
        """Called before a record is deleted."""
        if force:
            versions = self.obj(record)
            versions.clear_next()

    def pre_dump(self, record, data, dumper=None):
        """Called before a record is dumped."""
        parent = getattr(record, self.attr_name)
        if parent:
            data[self.attr_name] = self.obj(record).dump()

    def post_load(self, record, data, loader=None):
        """Called after a record was loaded."""
        dump = record.pop(self.attr_name, None)
        if dump:
            versions = VersionsManager(record, dump=dump)
            setattr(record, self.attr_name, versions)

    #
    # Data descriptor API
    #
    def __get__(self, record, owner=None):
        """Get the value for the field.

        Called when the field is accessed, e.g:

        .. code-block:: python

            # Access by object
            record.versions
            # Access by object
            Record.versions
        """
        if record is None:
            # access by class
            return self
        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Assign a value to the field.

        Called when a value is assigned to the field, e.g.:

        .. code-block:: python

            record.versions = <obj>
        """
        self.set_obj(record, obj)
