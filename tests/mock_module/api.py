"""Example of a record draft API."""

from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records import FileRecord as FileRecordBase
from invenio_records_resources.records.systemfields import FilesField, IndexField

from invenio_drafts_resources.records import Draft as DraftBase
from invenio_drafts_resources.records import ParentRecord as ParentRecordBase
from invenio_drafts_resources.records import Record as RecordBase
from invenio_drafts_resources.services.records.components.media_files import (
    MediaFilesAttrConfig,
)

from .models import (
    DraftMetadata,
    FileDraftMetadata,
    FileRecordMetadata,
    MediaFileDraftMetadata,
    MediaFileRecordMetadata,
    ParentRecordMetadata,
    ParentState,
    RecordMetadata,
)


class ParentRecord(ParentRecordBase):
    """Example parent record."""

    # Configuration
    model_cls = ParentRecordMetadata

    # System fields
    schema = ConstantField(
        "$schema", "http://localhost/schemas/records/parent-v1.0.0.json"
    )


class FileRecord(FileRecordBase):
    """Example record file API."""

    model_cls = FileRecordMetadata
    record_cls = None  # defined below


class MediaFileRecord(FileRecordBase):
    """Example record file API."""

    model_cls = MediaFileRecordMetadata
    record_cls = None  # defined below


class Record(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = RecordMetadata
    versions_model_cls = ParentState
    parent_record_cls = ParentRecord

    # System fields
    schema = ConstantField(
        "$schema", "http://localhost/schemas/records/record-v1.0.0.json"
    )

    index = IndexField(
        "draftsresources-records-record-v1.0.0", search_alias="draftsresources-records"
    )

    files = FilesField(
        store=False,
        dump=True,
        file_cls=FileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=MediaFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    bucket_id = ModelField(dump=False)

    bucket = ModelField(dump=False)

    media_bucket_id = ModelField(dump=False)

    media_bucket = ModelField(dump=False)


class RecordMediaFiles(Record):
    """Media file record API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=MediaFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )


FileRecord.record_cls = Record
MediaFileRecord.record_cls = RecordMediaFiles


class FileDraft(FileRecordBase):
    """Example record file API."""

    model_cls = FileDraftMetadata
    record_cls = None  # defined below


class MediaFileDraft(FileRecordBase):
    """File associated with a draft."""

    model_cls = MediaFileDraftMetadata
    record_cls = None  # defined below


class Draft(DraftBase):
    """Example record API."""

    # Configuration
    model_cls = DraftMetadata
    versions_model_cls = ParentState
    parent_record_cls = ParentRecord

    # System fields
    schema = ConstantField(
        "$schema", "http://localhost/schemas/records/record-v1.0.0.json"
    )

    index = IndexField(
        "draftsresources-drafts-draft-v1.0.0", search_alias="draftsresources-drafts"
    )

    files = FilesField(
        store=False,
        file_cls=FileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=MediaFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    bucket_id = ModelField(dump=False)

    bucket = ModelField(dump=False)

    media_bucket_id = ModelField(dump=False)

    media_bucket = ModelField(dump=False)


class DraftMediaFiles(Draft):
    """RDM Draft media file API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=MediaFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )


FileDraft.record_cls = Draft
MediaFileDraft.record_cls = DraftMediaFiles
