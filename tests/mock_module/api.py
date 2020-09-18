"""Example of a record draft API."""

from invenio_drafts_resources.records.api import Draft as DraftBase, \
    Record as RecordBase
from invenio_records.systemfields import ConstantField

from .models import DraftMetadata, RecordMetadata


class Record(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = RecordMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/record-v1.0.0.json')


class Draft(DraftBase):
    """Example record API."""

    # Configuration
    model_cls = DraftMetadata

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/record-v1.0.0.json')