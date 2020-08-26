# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test draft service links."""

import pytest


@pytest.fixture
def identified_draft(draft_service, es, fake_identity, input_draft):
    """Identified draft fixture."""
    identified_draft = draft_service.create(
        data=input_draft, identity=fake_identity
    )
    return identified_draft


def assert_expected_links(pid_value, links):
    expected_links = {
        "self": f"https://localhost:5000/api/records/{pid_value}/draft",
        "self_html": f"https://localhost:5000/deposits/{pid_value}/edit",
        "publish": f"https://localhost:5000/api/records/{pid_value}/draft/actions/publish",  # noqa
    }

    assert expected_links == links


def test_linker_links(draft_service, fake_identity, identified_draft):
    pid_value = identified_draft.id

    # NOTE: Here we test the linker links in general
    links = draft_service.linker.links(
        "draft", fake_identity, pid_value=pid_value,
        record=identified_draft.record
    )

    assert_expected_links(pid_value, links)
    # test create_draft generates links while we're at it.
    assert identified_draft.links == links


def test_read_draft_links(draft_service, fake_identity, identified_draft):
    pid_value = identified_draft.id

    read_draft = draft_service.read_draft(fake_identity, pid_value)

    assert_expected_links(pid_value, read_draft.links)


def test_update_draft_links(
        draft_service, fake_identity, identified_draft, input_draft):
    pid_value = identified_draft.id

    updated_draft = draft_service.update_draft(
        fake_identity, pid_value, input_draft
    )

    assert_expected_links(pid_value, updated_draft.links)


def test_publish_links(draft_service, fake_identity, input_draft):
    # NOTE: We have to create a new draft since we don't want to destroy
    #       the fixture one.
    identified_draft = draft_service.create(
        data=input_draft, identity=fake_identity
    )
    pid_value = identified_draft.id

    # Publish
    published_record = draft_service.publish(fake_identity, pid_value)

    expected_links = {
        "self": f"https://localhost:5000/api/records/{pid_value}",
        "self_html": f"https://localhost:5000/records/{pid_value}",
        "delete": f"https://localhost:5000/api/records/{pid_value}",
        "edit": f"https://localhost:5000/api/records/{pid_value}/draft",
        "files": f"https://localhost:5000/api/records/{pid_value}/files",
    }

    assert expected_links == published_record.links

    # TODO: Add edit links check here. We skip those because of the sleep
    #       requirement drastically slowing down the tests. It's fine for now
    #       since we know the linker is called there and the linker is tested
    #       above.


def test_new_version_links(draft_service, fake_identity, input_draft):
    # NOTE: We have to create a new draft since we don't want to destroy
    #       the fixture one.
    identified_draft = draft_service.create(
        data=input_draft, identity=fake_identity
    )
    pid_value = identified_draft.id
    published_record = draft_service.publish(fake_identity, pid_value)
    pid_value = published_record.id

    versioned_draft = draft_service.new_version(fake_identity, pid_value)

    pid_value = versioned_draft.id
    assert_expected_links(pid_value, versioned_draft.links)
