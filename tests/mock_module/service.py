"""Example service."""

from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services import (
    FileServiceConfig as BaseFileServiceConfig,
)
from invenio_records_resources.services import RecordLink

from invenio_drafts_resources.services import RecordServiceConfig
from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    DraftMediaFilesComponent,
)
from invenio_drafts_resources.services.records.config import is_draft, is_record

from .api import Draft, DraftMediaFiles, Record, RecordMediaFiles
from .permissions import PermissionPolicy
from .schemas import RecordSchema


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
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/mocks/{id}"),
            else_=RecordLink("{+api}/mocks/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/mocks/{id}"),
            else_=RecordLink("{+ui}/uploads/{id}"),
        ),
        "latest": RecordLink("{+api}/mocks/{id}/versions/latest"),
        "latest_html": RecordLink("{+ui}/mocks/{id}/latest"),
        "draft": RecordLink("{+api}/mocks/{id}/draft", when=is_record),
        "record": RecordLink("{+api}/mocks/{id}", when=is_draft),
        "publish": RecordLink("{+api}/mocks/{id}/draft/actions/publish", when=is_draft),
        "versions": RecordLink("{+api}/mocks/{id}/versions"),
    }


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
