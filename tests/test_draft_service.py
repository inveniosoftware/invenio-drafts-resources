# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio Drafts Resources module to create REST APIs"""


def test_create_draft_of_new_record(app, draft_service, input_draft,
                                    fake_identity):
    """Test draft creation of a non-existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    identified_draft = draft_service.create(
        data=input_draft, identity=fake_identity
    )

    assert identified_draft.id is None

    for key, value in input_draft.items():
        assert identified_draft.record[key] == value


def test_create_draft_of_existing_record(app, draft_service, record_service,
                                         input_record, fake_identity):
    """Test draft creation of an existing record."""
    # Needs `app` context because of invenio_access/permissions.py#166
    # Create new record
    identified_record = record_service.create(
        data=input_record, identity=fake_identity
    )

    recid = identified_record.id
    assert recid

    for key, value in input_record.items():
        assert identified_record.record[key] == value

    # Create new draft of said record
    orig_title = input_record['title']
    input_record['title'] = "Edited title"
    identified_draft = draft_service.edit(
        data=input_record,
        identity=fake_identity,
        id_=recid
    )

    assert identified_draft.id == recid

    for key, value in input_record.items():
        assert identified_draft.record[key] == value

    # Check the actual record was not modified
    identified_record = record_service.read(id_=recid, identity=fake_identity)

    assert identified_record.record['title'] == orig_title
