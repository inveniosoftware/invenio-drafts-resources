"""Example service."""

from invenio_records_resources.services import ConditionalLink
from invenio_records_resources.services import \
    FileServiceConfig as BaseFileServiceConfig
from invenio_records_resources.services import RecordLink

from invenio_drafts_resources.services import RecordServiceConfig
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent
from invenio_drafts_resources.services.records.config import is_draft, \
    is_record

from .api import Draft, Record
from .permissions import PermissionPolicy
from .schemas import RecordSchema


class ServiceConfig(RecordServiceConfig):
    """Mock service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Record
    draft_cls = Draft

    schema = RecordSchema

    components = RecordServiceConfig.components + [
        DraftFilesComponent
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
        "publish": RecordLink(
            "{+api}/mocks/{id}/draft/actions/publish",
            when=is_draft
        ),
        "versions": RecordLink("{+api}/mocks/{id}/versions"),
    }


class FileServiceConfig(BaseFileServiceConfig):
    """File service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Draft

    # file_links_list = {
    #     "self": RecordLink("{+api}/mocks/{id}/files"),
    # }

    # file_links_item = {
    #     "self": FileLink("{+api}/mocks/{id}/files/{key}"),
    #     "content": FileLink("{+api}/mocks/{id}/files/{key}/content"),
    #     "commit": FileLink("{+api}/mocks/{id}/files/{key}/commit"),
    # }
