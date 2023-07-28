# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs."""

from mock_module.api import Record


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = ["id", "metadata", "created", "updated", "links"]

    for field in fields_to_check:
        assert field in response_fields


#
# Operations tests
#


def test_create_draft(client, headers, input_data, location, search_clear):
    """Test draft creation of a non-existing record."""
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201
    _assert_single_item_response(response)


def test_read_draft(client, headers, input_data, location, search_clear):
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201

    recid = response.json["id"]
    response = client.get(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)


def test_update_draft(client, headers, input_data, location, search_clear):
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201
    assert response.json["metadata"]["title"] == input_data["metadata"]["title"]

    recid = response.json["id"]

    orig_title = input_data["metadata"]["title"]
    edited_title = "Edited title"
    input_data["metadata"]["title"] = edited_title

    # Update draft content
    update_response = client.put(
        f"/mocks/{recid}/draft", json=input_data, headers=headers
    )

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == edited_title
    assert update_response.json["id"] == recid

    # Check the updates where saved
    update_response = client.get(f"/mocks/{recid}/draft", headers=headers)

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == edited_title
    assert update_response.json["id"] == recid


def test_delete_draft(client, headers, input_data, location, search_clear):
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201

    recid = response.json["id"]

    update_response = client.delete(f"/mocks/{recid}/draft", headers=headers)

    assert update_response.status_code == 204

    # Check draft deletion
    update_response = client.get(f"/mocks/{recid}/draft", headers=headers)
    assert update_response.status_code == 404


def _create_and_publish(client, headers, input_data):
    """Create a draft and publish it."""
    # Create the draft
    response = client.post("/mocks", json=input_data, headers=headers)

    assert response.status_code == 201

    recid = response.json["id"]

    # Publish it
    response = client.post(f"/mocks/{recid}/draft/actions/publish", headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)

    return recid


def test_publish_draft(client, headers, input_data, location, search_clear):
    """Test draft publication of a non-existing record.

    It has to first create said draft.
    """
    recid = _create_and_publish(client, headers, input_data)

    # Check draft does not exists anymore
    response = client.get(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 404

    # Check record exists
    response = client.get(f"/mocks/{recid}", headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)


def test_search_versions(client, headers, input_data, location, search_clear):
    """Test search for versions."""
    recid = _create_and_publish(client, headers, input_data)
    Record.index.refresh()

    # Check draft does not exists anymore
    res = client.get(f"/mocks/{recid}/versions", headers=headers)
    assert res.status_code == 200


#
# Flow tests (Note that operations are tested above
# therefore these tests do not assert their output)
#


def test_create_publish_new_revision(
    app, db, client, headers, input_data, location, search_clear
):
    """Test draft creation of an existing record and publish it."""
    recid = _create_and_publish(client, headers, input_data)

    # Create new draft of said record
    orig_title = input_data["metadata"]["title"]
    input_data["metadata"]["title"] = "Edited title"
    response = client.post(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 201
    assert response.json["revision_id"] == 5
    _assert_single_item_response(response)

    # Update that new draft
    response = client.put(f"/mocks/{recid}/draft", json=input_data, headers=headers)

    assert response.status_code == 200

    # Check the actual record was not modified
    response = client.get(f"/mocks/{recid}", headers=headers)

    assert response.status_code == 200
    _assert_single_item_response(response)
    assert response.json["metadata"]["title"] == orig_title

    # Publish it to check the increment in reversion
    response = client.post(f"/mocks/{recid}/draft/actions/publish", headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)

    assert response.json["id"] == recid
    assert response.json["revision_id"] == 2
    assert response.json["metadata"]["title"] == input_data["metadata"]["title"]

    # Check it was actually edited
    response = client.get(f"/mocks/{recid}", headers=headers)

    assert response.json["metadata"]["title"] == input_data["metadata"]["title"]


def test_multiple_edit(client, headers, input_data, location, search_clear):
    """Test the revision_id when editing record multiple times.

    This tests the `edit` service method.
    """
    recid = _create_and_publish(client, headers, input_data)

    # Create new draft of said record
    response = client.post(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 201
    assert response.json["revision_id"] == 5

    # Request a second edit. Get the same draft (revision_id)
    response = client.post(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 201
    assert response.json["revision_id"] == 5

    # Publish it to check the increment in version_id
    response = client.post(f"/mocks/{recid}/draft/actions/publish", headers=headers)

    assert response.status_code == 202

    # Edit again
    response = client.post(f"/mocks/{recid}/draft", headers=headers)

    assert response.status_code == 201
    assert response.json["revision_id"] == 8


def test_redirect_to_latest_version(client, headers, input_data, location):
    """Creates a new version of a record.

    Publishes the draft to obtain 2 versions of a record.
    """
    recid = _create_and_publish(client, headers, input_data)

    # Create new version of said record
    response = client.post(f"/mocks/{recid}/versions", headers=headers)
    recid_2 = response.json["id"]

    # This and other file related tests are flaky
    # NOTE: Assuming a new version should indeed have its files.enabled set to
    #       True automatically, we have to reset it to False for this test.
    client.put(f"/mocks/{recid_2}/draft", json=input_data, headers=headers)

    # Publish it to check the increment in version
    response = client.post(f"/mocks/{recid_2}/draft/actions/publish", headers=headers)
    latest_version_self_link = response.json["links"]["self"]

    # Read a previous versions latest
    response = client.get(f"/mocks/{recid}/versions/latest")

    assert response.status_code == 301
    assert response.headers["location"] == latest_version_self_link
