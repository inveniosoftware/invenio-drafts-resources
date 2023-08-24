# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service tasks tests."""

import pytest

from invenio_drafts_resources.services.records.tasks import cleanup_drafts


#
# Fixtures
#
@pytest.fixture()
def input_data(input_data):
    """Enable files."""
    input_data["files"]["enabled"] = False
    return input_data


@pytest.fixture(scope="module")
def base_app(base_app, service):
    """Application factory fixture."""
    registry = base_app.extensions["invenio-records-resources"].registry
    registry.register(service, service_id="records")
    yield base_app


def test_hard_delete_soft_deleted_task(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft_model = service.draft_cls.model_cls

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
    cleanup_drafts(seconds=0, search_gc_deletes=0)

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 0  # noqa
    )
