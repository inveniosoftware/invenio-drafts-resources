# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import pytest


def _create_and_publish(service, input_data, identity_simple):
    """Creates a draft and publishes it."""
    draft = service.create(identity_simple, input_data)
    record = service.publish(draft.id, identity_simple)

    assert record.id == draft.id
    assert record._record.revision_id == 1

    return record


# NOTE: We override the function-scoped input_data fixture by a module-scoped
#       one, so it can be used in the module-scoped fixture below.
#       (changing the function-scoped one breaks existing tests)
@pytest.fixture(scope="module")
def input_data():
    """Input data (as coming from the view layer)."""
    return {
        'metadata': {
            'title': 'Test'
        },
    }


@pytest.fixture(scope="module")
def two_versions(app, identity_simple, input_data, service):
    """Create 2 versions."""
    # NOTE: We use app fixture to create/teardown the index only once for
    #       this module.
    record = _create_and_publish(service, input_data, identity_simple)
    recid = record.id
    draft = service.new_version(recid, identity_simple)
    record_2 = service.publish(draft.id, identity_simple)
    service.record_cls.index.refresh()
    return [record, record_2]


def test_search_defaults_to_latest_version(
        service, identity_simple, two_versions):
    results = service.search(identity_simple)

    v1, v2 = two_versions
    assert set([v2.id]) == set([r["id"] for r in results])


def test_search_all_versions(service, identity_simple, two_versions):
    results = service.search(identity_simple, params={"allversions": True})

    v1, v2 = two_versions
    assert set([v1.id, v2.id]) == set([r["id"] for r in results])
