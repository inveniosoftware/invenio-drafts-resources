# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


from .utils import create_and_publish


def create_two_versions(service, identity_simple, input_data):
    """Create 2 versions."""
    record = create_and_publish(service, identity_simple, input_data)
    draft = service.new_version(record.id, identity_simple)
    # new_version resets files.enabled to True
    service.update_draft(draft.id, identity_simple, input_data)
    record_2 = service.publish(draft.id, identity_simple)
    service.record_cls.index.refresh()
    return [record, record_2]


def test_search_versions(app, identity_simple, input_data, service):
    v1, v2 = create_two_versions(service, identity_simple, input_data)

    # test search defaults to latest version
    results = service.search(identity_simple)
    assert set([v2.id]) == set([r["id"] for r in results])

    # test search all versions
    results = service.search(identity_simple, params={"allversions": True})
    assert set([v1.id, v2.id]) == set([r["id"] for r in results])
