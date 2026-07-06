# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-FileCopyrightText: 2020-2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Service tests.

Test to add:
- Read a tombstone page
- Read with missing permissions
- Read with missing pid
"""

from datetime import datetime, timedelta, timezone

import pytest


#
# Fixtures
#
@pytest.fixture()
def input_data(input_data):
    """Enable files."""
    input_data["files"]["enabled"] = False
    return input_data


def test_hard_delete_soft_deleted(app, service, identity_simple, input_data):
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft_model = service.draft_cls.model_cls

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
    service.cleanup_drafts(timedelta(seconds=0), search_gc_deletes=0)

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 0  # noqa
    )


def test_hard_delete_soft_deleted_not_enough_time(
    app, service, identity_simple, input_data
):
    draft = service.create(identity_simple, input_data)
    service.publish(identity_simple, draft.id)
    draft_model = service.draft_cls.model_cls

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )
    service.cleanup_drafts(timedelta(seconds=10), search_gc_deletes=0)

    assert (
        len(draft_model.query.filter(draft_model.is_deleted == True).all()) == 1  # noqa
    )


def test_cleanup_drafts_batches(app, db, service, location):
    """The service loops over batches until the whole backlog is cleaned."""
    draft_model = service.draft_cls.model_cls

    # More expired soft-deleted drafts than fit in one batch.
    expired_ids = []
    for _ in range(5):
        draft = service.draft_cls.create({})
        db.session.commit()
        draft.delete(force=False)
        db.session.commit()
        expired_ids.append(draft.id)

    # Age them past the cutoff (a bulk update skips the before_update event).
    old = datetime.now(timezone.utc) - timedelta(days=1)
    draft_model.query.filter(draft_model.id.in_(expired_ids)).update(
        {draft_model.updated: old}, synchronize_session=False
    )
    db.session.commit()

    # A recent soft-deleted draft, still within the cutoff.
    recent = service.draft_cls.create({})
    db.session.commit()
    recent.delete(force=False)
    db.session.commit()

    # batch_size < number of expired drafts => several batches.
    service.cleanup_drafts(timedelta(hours=1), search_gc_deletes=0, batch_size=2)

    # All expired drafts are hard-deleted; the recent one is untouched.
    assert draft_model.query.filter(draft_model.id.in_(expired_ids)).count() == 0
    recent_row = draft_model.query.filter_by(id=recent.id).one_or_none()
    assert recent_row is not None and recent_row.is_deleted
