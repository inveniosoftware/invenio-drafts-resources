# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test draft service links."""

from copy import deepcopy

import pytest


@pytest.fixture()
def input_data():
    """Input data (as coming from the view layer)."""
    return {
        'metadata': {
            'title': 'Test',
        },
    }


def assert_expected_links(pid_value, links):
    expected_links = {
        "self": f"https://localhost:5000/api/mocks/{pid_value}/draft",
        "publish": f"https://localhost:5000/api/mocks/{pid_value}/draft/actions/publish",  # noqa
    }

    for key, link in expected_links.items():
        assert link == links[key]


def test_create_draft(client, headers, input_data):
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201
    pid_value = response.json["id"]
    assert_expected_links(pid_value, response.json["links"])


def test_read_draft(client, headers, input_data):
    response = client.post("/mocks", json=input_data, headers=headers)
    pid_value = response.json['id']
    response = client.get(f"/mocks/{pid_value}/draft", headers=headers)

    assert response.status_code == 200
    assert_expected_links(pid_value, response.json["links"])


def test_update_draft(client, headers, input_data):
    response = client.post("/mocks", json=input_data, headers=headers)
    pid_value = response.json["id"]
    input_data = deepcopy(input_data)
    input_data['metadata']['title'] = "Updated title"  # Shouldn't matter

    response = client.put(
        f"/mocks/{pid_value}/draft", json=input_data, headers=headers
    )
    assert response.status_code == 200
    print("response.json", response.json)
    assert_expected_links(pid_value, response.json["links"])


@pytest.mark.skip()
def test_publish_draft(client, headers, input_data):
    """Test draft publication of a non-existing record.

    It has to first create said draft.
    """
    recid = _create_and_publish(client, input_data)

    # Check draft does not exists anymore
    # FIXME: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        response = client.get(
            "/mocks/{}/draft".format(recid), headers=headers)

        assert response.status_code == 404

    # Check record exists
    response = client.get("/mocks/{}".format(recid), headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)


@pytest.mark.skip()
def test_publish_links(draft_service, headers, identity_simple, input_draft):
    # NOTE: We have to create a new draft since we don't want to destroy
    #       the fixture one.
    draft_result = draft_service.create(
        data=input_draft, identity=identity_simple
    )
    pid_value = draft_result.id

    # Publish
    published_record = draft_service.publish(identity_simple, pid_value)

    expected_links = {
        "self": f"https://localhost:5000/api/records/{pid_value}",
        "delete": f"https://localhost:5000/api/records/{pid_value}",
        "edit": f"https://localhost:5000/api/records/{pid_value}/draft",
        "files": f"https://localhost:5000/api/records/{pid_value}/files",
    }

    assert expected_links == published_record.links

    # TODO: Add edit links check here. We skip those because of the sleep
    #       requirement drastically slowing down the tests. It's fine for now
    #       since we know the linker is called there and the linker is tested
    #       above.
