"""Example of a record model."""

from invenio_db import db
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType

from invenio_drafts_resources.records import (
    DraftMetadataBase,
    ParentRecordMixin,
    ParentRecordStateMixin,
)


class MockParentRecordMetadata(db.Model, RecordMetadataBase):
    """Model for mock module metadata."""

    __tablename__ = "parent_mock_metadata"


class MockDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):
    """Model for mock module metadata."""

    __tablename__ = "draft_mock_metadata"
    __parent_record_model__ = MockParentRecordMetadata

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])


class MockRecordMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Model for mock module metadata."""

    __tablename__ = "record_mock_metadata"
    __parent_record_model__ = MockParentRecordMetadata

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])


class MockParentState(db.Model, ParentRecordStateMixin):
    """Model for mock module for parent state."""

    __parent_record_model__ = MockParentRecordMetadata
    __record_model__ = MockRecordMetadata
    __draft_model__ = MockDraftMetadata


class FileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Model for mock module record files."""

    __record_model_cls__ = MockRecordMetadata

    __tablename__ = "mock_record_files"


class MediaFileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Model for mock module record files."""

    __record_model_cls__ = MockRecordMetadata

    __tablename__ = "mock_record_media_files"


class FileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Model for mock module draft files."""

    __record_model_cls__ = MockDraftMetadata

    __tablename__ = "mock_draft_files"


class MediaFileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a draft."""

    __record_model_cls__ = MockDraftMetadata

    __tablename__ = "mock_drafts_media_files"
