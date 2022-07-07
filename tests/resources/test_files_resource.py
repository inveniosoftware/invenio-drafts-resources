# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test files resource integration."""

from io import BytesIO

import pytest


@pytest.fixture()
def published_id(client, location, headers):
    """A published record."""
    h = headers

    # Create a draft
    res = client.post(
        "/mocks",
        headers=h,
        json={
            "metadata": {"title": "Test"},
        },
    )
    assert res.status_code == 201
    id_ = res.json["id"]

    # Initialize files upload
    res = client.post(
        f"/mocks/{id_}/draft/files", headers=h, json=[{"key": "test.pdf"}]
    )
    assert res.status_code == 201
    assert res.json["entries"][0]["key"] == "test.pdf"
    assert res.json["entries"][0]["status"] == "pending"

    # Upload a file
    res = client.put(
        f"/mocks/{id_}/draft/files/test.pdf/content",
        headers={"content-type": "application/octet-stream"},
        data=BytesIO(b"testfile"),
    )
    assert res.status_code == 200

    # Commit the file
    res = client.post(f"/mocks/{id_}/draft/files/test.pdf/commit", headers=h)
    assert res.status_code == 200
    assert res.json["key"] == "test.pdf"
    assert res.json["status"] == "completed"

    # Publish the record
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    return id_


def test_files_publish_flow(client, search_clear, location, headers):
    """Test record creation."""
    h = headers
    # Create a draft
    res = client.post("/mocks", headers=h, json={"metadata": {"title": "Test"}})
    assert res.status_code == 201
    id_ = res.json["id"]

    # Initialize files upload
    res = client.post(
        f"/mocks/{id_}/draft/files", headers=h, json=[{"key": "test.pdf"}]
    )
    assert res.status_code == 201
    assert res.json["entries"][0]["key"] == "test.pdf"
    assert res.json["entries"][0]["status"] == "pending"

    # Upload a file
    res = client.put(
        f"/mocks/{id_}/draft/files/test.pdf/content",
        headers={"content-type": "application/octet-stream"},
        data=BytesIO(b"testfile"),
    )
    assert res.status_code == 200

    # Commit the file
    res = client.post(f"/mocks/{id_}/draft/files/test.pdf/commit", headers=h)
    assert res.status_code == 200
    assert res.json["key"] == "test.pdf"
    assert res.json["status"] == "completed"

    # Publish the record
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    # Check published files
    res = client.get(f"/mocks/{id_}/files", headers=h)
    assert res.status_code == 200
    assert res.json["entries"][0]["key"] == "test.pdf"
    assert res.json["entries"][0]["status"] == "completed"

    # Edit the record
    res = client.post(f"/mocks/{id_}/draft", headers=h)
    assert res.status_code == 201

    # Publish again
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    # Check published files
    res = client.get(f"/mocks/{id_}/files", headers=h)
    assert res.status_code == 200
    assert res.json["entries"][0]["key"] == "test.pdf"
    assert res.json["entries"][0]["status"] == "completed"


def test_metadata_only_record(client, search_clear, location, headers):
    """Test record with files disabled."""
    h = headers
    # Create a draft
    res = client.post(
        "/mocks",
        headers=h,
        json={"metadata": {"title": "Test"}, "files": {"enabled": False}},
    )
    assert res.status_code == 201
    id_ = res.json["id"]

    # Publish the record
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    # Check published files
    res = client.get(f"/mocks/{id_}/files", headers=h)
    assert res.status_code == 200
    assert res.json["enabled"] is False
    assert "entries" not in res.json

    # Edit the record
    res = client.post(f"/mocks/{id_}/draft", headers=h)
    assert res.status_code == 201

    # Publish again
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    # Check published files
    res = client.get(f"/mocks/{id_}/files", headers=h)
    assert res.status_code == 200
    assert res.json["enabled"] is False
    assert "entries" not in res.json


def test_import_files(client, search_clear, location, headers, published_id):
    """Test import files from previous version."""
    h = headers
    id_ = published_id

    # New version
    res = client.post(f"/mocks/{id_}/versions", headers=h)
    assert res.status_code == 201
    new_id = res.json["id"]

    # Check new version files
    res = client.get(f"/mocks/{new_id}/draft/files", headers=h)
    assert res.status_code == 200
    assert len(res.json["entries"]) == 0

    # Import files from previous version
    res = client.post(f"/mocks/{new_id}/draft/actions/files-import", headers=h)
    assert res.status_code == 201
    assert res.content_type == "application/json"

    # Check new version files
    res = client.get(f"/mocks/{new_id}/draft/files", headers=h)
    assert res.status_code == 200
    assert len(res.json["entries"]) == 1


def test_import_files_metadata_only(client, search_clear, location, headers):
    """Test import files from previous version."""
    h = headers

    res = client.post(
        "/mocks",
        headers=h,
        json={"metadata": {"title": "Test"}, "files": {"enabled": False}},
    )
    assert res.status_code == 201
    id_ = res.json["id"]

    # Publish
    res = client.post(f"/mocks/{id_}/draft/actions/publish", headers=h)
    assert res.status_code == 202

    # New version
    res = client.post(f"/mocks/{id_}/versions", headers=h)
    assert res.status_code == 201
    new_id = res.json["id"]

    # Check new version files
    res = client.get(f"/mocks/{new_id}/draft/files", headers=h)
    assert res.status_code == 200
    assert "entries" not in res.json

    # Import files from previous version
    res = client.post(f"/mocks/{new_id}/draft/actions/files-import", headers=h)
    assert res.status_code == 400


def test_import_files_no_version(client, search_clear, location, headers):
    """Test import files from previous version."""
    h = headers

    res = client.post(
        "/mocks",
        headers=h,
        json={"metadata": {"title": "Test"}, "files": {"enabled": True}},
    )
    assert res.status_code == 201
    id_ = res.json["id"]

    # Cannot import files from a non-existing previous version
    res = client.post(f"/mocks/{id_}/draft/actions/files-import", headers=h)
    assert res.status_code == 404
