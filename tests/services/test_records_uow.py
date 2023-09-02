# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""UOW tests."""

from unittest.mock import MagicMock

import pytest
from invenio_records_resources.services.uow import UnitOfWork

from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp

from .utils import create_and_publish


def test_parent_record_uow_params(app, db, service):
    """Test constructors params."""
    # test that it does not raise when params are passed correctly
    assert ParentRecordCommitOp({}, dict(service=service))
    assert ParentRecordCommitOp(
        {},
        indexer_context=dict(
            record_cls=service.record_cls,
            draft_cls=service.draft_cls,
            indexer=MagicMock(),
            draft_indexer=MagicMock(),
        ),
    )

    # test that it raises when one of the expected attr of the service is missing
    for missing_attr in ["record_cls", "draft_cls", "indexer", "draft_indexer"]:
        _service = type(
            "service",
            (object,),
            dict(
                record_cls=service.record_cls,
                draft_cls=service.draft_cls,
                indexer=service.indexer,
                draft_indexer=service.draft_indexer,
            ),
        )
        with pytest.raises(AttributeError):
            delattr(_service, missing_attr)
            assert ParentRecordCommitOp({}, indexer_context=dict(service=_service))

    # test that it raises when one of the expected constructor params is missing
    for missing_param in [
        "record_cls",
        "draft_cls",
        "indexer",
        "draft_indexer",
    ]:
        params = dict(
            record_cls=service.record_cls,
            draft_cls=service.draft_cls,
            indexer=service.indexer,
            draft_indexer=service.draft_indexer,
        )
        with pytest.raises(KeyError):
            params.pop(missing_param)
            assert ParentRecordCommitOp({}, indexer_context=dict(**params))


def test_parent_record_commit(app, db, service, identity_simple, input_data):
    """Test ParentRecordCommit unit of work."""
    record_v1 = create_and_publish(service, identity_simple, input_data)
    recid = record_v1.id
    draft_v1 = service.edit(identity_simple, recid)
    draft_v2 = service.new_version(identity_simple, recid)
    record_v2 = service.publish(identity_simple, draft_v2.id)

    parent = record_v1._record.parent

    indexer = MagicMock()
    draft_indexer = MagicMock()

    with UnitOfWork(db.session) as uow:
        op = ParentRecordCommitOp(
            parent,
            indexer_context=dict(
                record_cls=service.record_cls,
                draft_cls=service.draft_cls,
                indexer=indexer,
                draft_indexer=draft_indexer,
            ),
        )
        uow.register(op)
        uow.commit()

    assert indexer.bulk_index.call_count == 1
    args, _ = indexer.bulk_index.call_args
    assert list(args[0]) == [record_v1._record.id, record_v2._record.id]

    assert draft_indexer.bulk_index.call_count == 1
    args, _ = draft_indexer.bulk_index.call_args
    assert list(args[0]) == [draft_v1._record.id]
