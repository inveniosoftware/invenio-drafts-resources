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
    input_data['files']['enabled'] = False
    return input_data


def test_hard_delete_soft_deleted_task(
    app, service, identity_simple, input_data
):
    draft = service.create(identity_simple, input_data)
    service.publish(draft.id, identity_simple)
    draft_model = service.draft_cls.model_cls

    assert len(draft_model.query.filter(
        draft_model.is_deleted == True  # noqa
    ).all()) == 1
    cleanup_drafts(current_service_imp=service, seconds=0)

    assert len(draft_model.query.filter(
        draft_model.is_deleted == True  # noqa
    ).all()) == 0
