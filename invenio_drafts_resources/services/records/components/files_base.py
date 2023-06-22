# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Records service component base classes."""
from invenio_i18n import gettext as _
from invenio_records_resources.services.files.transfer import TransferType
from invenio_records_resources.services.records.components import (
    FilesOptionsComponent,
    BaseRecordFilesComponent,
)
from marshmallow import ValidationError

from .base import ServiceComponent


class RecordFilesComponent(ServiceComponent, BaseRecordFilesComponent):
    def __init__(self, service, *args, **kwargs):
        """Constructor."""
        super().__init__(service)
        self.files_component = FilesOptionsComponent(service)

    #
    # API
    #
    def create(self, identity, data=None, record=None, errors=None):
        """Assigns files.enabled.

        NOTE: `record` actually refers to the draft
              (this interface is used in records-resources and rdm-records)
        """
        draft = record
        files = self.get_record_files(draft)
        enabled = data.get(self.files_data_key, {}).get("enabled", True)

        if files.enabled != enabled:
            if not self.service.check_permission(
                identity, "manage_files", record=draft
            ):
                errors.append(
                    {
                        "field": f"{self.files_data_key}.enabled",
                        "messages": [
                            _("You don't have permissions to manage files options.")
                        ],
                    }
                )
                return  # exit early

        files.enabled = enabled

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Assigns files.enabled and warns if files are missing.

        NOTE: `record` actually refers to the draft
              (this interface is used in records-resources and rdm-records)
        """
        draft = record
        files = self.get_record_files(draft)
        enabled = data.get(self.files_data_key, {}).get("enabled", True)
        default_preview = data.get(self.files_data_key, {}).get("default_preview")
        if files.enabled != enabled:
            if not self.service.check_permission(
                identity, "manage_files", record=draft
            ):
                errors.append(
                    {
                        "field": f"{self.files_data_key}.enabled",
                        "messages": [
                            _("You don't have permissions to manage files options.")
                        ],
                    }
                )
                return  # exit early

        try:
            self.files_component.assign_files_enabled(draft, enabled)
        except ValidationError as e:
            errors.append(
                {"field": f"{self.files_data_key}.enabled", "messages": e.messages}
            )
            return  # exit early

        if files.enabled and not files.items():
            errors.append(
                {
                    "field": "files.enabled",
                    "messages": [
                        _(
                            "Missing uploaded files. To disable files for "
                            "this record please mark it as metadata-only."
                        )
                    ],
                }
            )

        try:
            self.files_component.assign_files_default_preview(
                draft,
                default_preview,
            )
        except ValidationError as e:
            errors.append(
                {
                    "field": f"f{self.files_data_key}.default_preview",
                    "messages": e.messages,
                }
            )

    def edit(self, identity, draft=None, record=None):
        """Edit callback."""
        files = self.get_record_files(draft)
        if draft.bucket is None:
            # Happens, when a soft-deleted draft is un-deleted.
            draft[self.files_data_key] = {"enabled": True}
            files.create_bucket()
        files.copy(record.files)

    def new_version(self, identity, draft=None, record=None):
        """New version callback."""
        # We don't copy files from the previous version, but instead allow
        # users to import the files.
        draft_files = self.get_record_files(draft)
        files = self.get_record_files(draft)
        draft_files.enabled = files.enabled

    def _publish_new(self, identity, draft, record):
        """Action when publishing a new draft."""
        # For unpublished drafts (new and new version), we move the draft
        # bucket from the draft to the record (instead of creating a new, and
        # deleting one). For consistency, we keep a bucket for all records
        # independently of if they have files enabled or not.
        files = self.get_record_files(record)
        draft_files = self.get_record_files(draft)
        files.set_bucket(draft.bucket)
        files.copy(draft_files, copy_obj=False)

        # Lock the bucket
        # TODO: Make the locking step optional in the future (so
        # instances can potentially allow files changes if desired).
        files.lock()

        # Cleanup
        if draft_files.enabled:
            draft_files.delete_all(remove_obj=False)
        draft_files.unset_bucket()

    def _publish_edit(self, identity, draft, record):
        """Action when publishing an edit to an existing record."""
        # TODO: For published records, we should sync changes from the
        # draft bucket to the record bucket, so that an instance could
        # potentially allow a user to update files. For now, sync() only
        # changes the default_preview and order
        files = self.get_record_files(record)
        draft_files = self.get_record_files(draft)
        files.sync(draft_files)

        # Teardown the bucket and files created in edit().
        if draft_files.enabled:
            draft_files.delete_all()
        draft_files.remove_bucket(force=True)

    def publish(self, identity, draft=None, record=None):
        """Copy bucket and files to record."""
        draft_files = self.get_record_files(draft)
        if draft_files.enabled and draft_files.bucket:
            if not draft_files.items():
                raise ValidationError(
                    _(
                        "Missing uploaded files. To disable files for "
                        "this record please mark it as metadata-only."
                    ),
                    field_name=f"f{self.files_data_key}.enabled",
                )
        if draft_files.enabled:
            for file_record in draft_files.values():
                if not TransferType(file_record.file.storage_class).is_completed:
                    raise ValidationError(
                        _(
                            "One or more files have not completed their transfer, please wait."
                        ),
                        field_name="files",
                    )

        if record.bucket_id:
            self._publish_edit(identity, draft, record)
        else:
            self._publish_new(identity, draft, record)

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete files associated with a draft.

        :param force: If force is True, it means that the draft is being force
            deleted instead of soft deleted (i.e. an unpublished draft).
        """
        draft_files = self.get_record_files(draft)
        if draft_files.enabled:
            draft_files.delete_all(draft)
        draft_files.remove_bucket(force=True)

    def import_files(self, identity, draft=None, record=None):
        """Import files handler."""
        record_files = self.get_record_files(record)
        draft_files = self.get_record_files(draft)
        if not draft_files.enabled:
            raise ValidationError(
                _("Files support must be enabled."), field_name="files.enabled"
            )

        if draft_files.items():
            raise ValidationError(
                _("Please remove all files first."), field_name="files.enabled"
            )

        if not files.enabled and not files.bucket:
            raise ValidationError(
                _("The record has no files."), field_name="files.enabled"
            )

        # Copy over the files
        draft_files.copy(record_files)
