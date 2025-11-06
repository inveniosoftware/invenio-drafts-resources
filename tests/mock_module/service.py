# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Example service."""


from invenio_records_resources.services import (
    ConditionalLink,
)
from invenio_records_resources.services import (
    FileServiceConfig as BaseFileServiceConfig,
)
from invenio_records_resources.services import (
    RecordEndpointLink,
    pagination_endpoint_links,
)
from invenio_records_resources.services.files import FileService

from invenio_drafts_resources.services import RecordService, RecordServiceConfig
from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    DraftMediaFilesComponent,
)
from invenio_drafts_resources.services.records.config import is_draft, is_record

from .api import Draft, DraftMediaFiles, Record, RecordMediaFiles
from .permissions import PermissionPolicy
from .schemas import RecordSchema


# Config
class ServiceConfig(RecordServiceConfig):
    """Mock service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Record
    draft_cls = Draft

    schema = RecordSchema

    components = RecordServiceConfig.components + [
        DraftFilesComponent,
        DraftMediaFilesComponent,
    ]

    links_item = {
        # We just keep the API links for tests since fake UI endpoints would have
        # to be created anyway
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordEndpointLink("mocks.read"),
            else_=RecordEndpointLink("mocks.read_draft"),
        ),
        "latest": RecordEndpointLink("mocks.read_latest"),
        "draft": RecordEndpointLink("mocks.read_draft", when=is_record),
        "record": RecordEndpointLink("mocks.read", when=is_draft),
        "publish": RecordEndpointLink("mocks.publish", when=is_draft),
        "versions": RecordEndpointLink("mocks.search_versions"),
    }

    links_search = pagination_endpoint_links("mocks.search")
    links_search_drafts = pagination_endpoint_links("mocks.search_user_records")
    links_search_versions = pagination_endpoint_links(
        "mocks.search_versions",
        params=["pid_value"],
    )


class MediaFilesRecordServiceConfig(RecordServiceConfig):
    """Record with media files service config."""

    service_id = "mock-record-media-files-service"
    record_cls = RecordMediaFiles
    draft_cls = DraftMediaFiles

    components = [
        DraftMediaFilesComponent,
    ]


class FileServiceConfig(BaseFileServiceConfig):
    """File service configuration."""

    allow_upload = False
    permission_policy_cls = PermissionPolicy
    record_cls = Record


class DraftFileServiceConfig(BaseFileServiceConfig):
    """File service configuration."""

    permission_policy_cls = PermissionPolicy
    permission_action_prefix = "draft_"
    record_cls = Draft


class MediaFileServiceConfig(BaseFileServiceConfig):
    """File service configuration."""

    service_id = "record-media-files-service"
    allow_upload = False
    permission_policy_cls = PermissionPolicy
    permission_action_prefix = "draft_media_"
    record_cls = RecordMediaFiles


class DraftMediaFileServiceConfig(BaseFileServiceConfig):
    """File service configuration."""

    service_id = "draft-media-files"
    permission_policy_cls = PermissionPolicy
    permission_action_prefix = "draft_media_"
    record_cls = DraftMediaFiles


# Services
file_service = FileService(FileServiceConfig)
draft_file_service = FileService(DraftFileServiceConfig)
record_service = RecordService(
    ServiceConfig,
    files_service=file_service,
    draft_files_service=draft_file_service,
)
media_file_service = FileService(MediaFileServiceConfig)
media_draft_file_service = FileService(DraftMediaFileServiceConfig)
