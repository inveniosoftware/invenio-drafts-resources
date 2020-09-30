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
    assert_expected_links(pid_value, response.json["links"])


def test_publish_draft(client, headers, input_data):
    response = client.post("/mocks", json=input_data, headers=headers)
    pid_value = response.json['id']

    # NOTE: This returns a record
    response = client.post(
        f"/mocks/{pid_value}/draft/actions/publish", headers=headers
    )

    assert response.status_code == 202
    links = response.json["links"]
    expected_links = {
        "self": f"https://localhost:5000/api/mocks/{pid_value}",
        # TODO: Add files, delete...
    }
    for key, link in expected_links.items():
        assert link == links[key]
