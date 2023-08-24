# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service tests.

Test to add:
- Read a tombstone page
- Read with missing permissions
- Read with missing pid
"""

from datetime import timedelta

import pytest


#
# Fixtures
#
@pytest.fixture()
def input_data(input_data):
    """Enable files."""
    input_data["files"]["enabled"] = False
    return input_data


def test_hard_delete_soft_deleted(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft_model = service.draft_cls.model_cls

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
    service.cleanup_drafts(timedelta(seconds=0), search_gc_deletes=0)

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 0  # noqa
    )


def test_hard_delete_soft_deleted_not_enough_time(
    app, service, identity_simple, input_data
):
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft_model = service.draft_cls.model_cls

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
    service.cleanup_drafts(timedelta(seconds=10), search_gc_deletes=0)

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
