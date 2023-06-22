# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records service component base classes."""

from .files_base import RecordFilesComponent
from invenio_records_resources.services.records.components import (
    AuxFilesOptionsComponent,
)


class DraftFilesComponent(RecordFilesComponent):
    """Draft files service component."""

    _files_attr_key = "files"
    _files_data_key = "files"
    _files_bucket_attr_key = "bucket"
    _files_bucket_id_attr_key = "bucket_id"


class DraftAuxiliaryFilesComponent(RecordFilesComponent):
    _files_attr_key = "aux_files"
    _files_data_key = "aux_files"
    _files_bucket_attr_key = "aux_bucket"
    _files_bucket_id_attr_key = "aux_bucket_id"

    def __init__(self, service, *args, **kwargs):
        """Constructor."""
        super().__init__(service)
        self.files_component = AuxFilesOptionsComponent(service)
