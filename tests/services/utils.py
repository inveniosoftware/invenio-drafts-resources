# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test utilities."""


def create_and_publish(service, identity_simple, input_data):
    """Creates a draft and publishes it."""
    draft = service.create(identity_simple, input_data)
    record = service.publish(identity_simple, draft.id)

    assert record.id == draft.id
    assert record._record.revision_id == 1

    return record
