# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Links Schema."""

from marshmallow import Schema
from marshmallow_utils.fields import Link
from uritemplate import URITemplate


class DraftLinksSchema(Schema):
    """Schema for a record's links."""

    self = Link(
        template=URITemplate("/api/records/{pid_value}/draft"),
        permission="read",
        params=lambda draft: {'pid_value': draft.pid.pid_value}
    )
    publish = Link(
        template=URITemplate("/api/records/{pid_value}/draft/actions/publish"),
        permission="publish",
        params=lambda draft: {'pid_value': draft.pid.pid_value}
    )
