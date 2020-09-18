"""Example service."""

from invenio_drafts_resources.services import RecordDraftService, \
    RecordDraftServiceConfig
from invenio_records_resources.services.records.schema import RecordSchema
from invenio_search import RecordsSearchV2

from .api import Draft, Record
from .permissions import PermissionPolicy


class ServiceConfig(RecordDraftServiceConfig):
    """Mock service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Record
    draft_cls = Draft
    schema = RecordSchema
    search_cls = RecordsSearchV2


class Service(RecordDraftService):
    """Mock service."""

    default_config = ServiceConfig
