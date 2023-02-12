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

from invenio_i18n import gettext as _
from invenio_records_resources.services.files.transfer import TransferType
from invenio_records_resources.services.records.components import FilesOptionsComponent
from marshmallow import ValidationError

from .base import ServiceComponent


class DraftFilesComponent(ServiceComponent):
    """Draft files service component."""

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
        enabled = data.get("files", {}).get("enabled", True)
        record.files.enabled = enabled

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Assigns files.enabled and warns if files are missing.

        NOTE: `record` actually refers to the draft
              (this interface is used in records-resources and rdm-records)
        """
        draft = record
        enabled = data.get("files", {}).get("enabled", True)
        default_preview = data.get("files", {}).get("default_preview")

        try:
            self.files_component.assign_files_enabled(draft, enabled)
        except ValidationError as e:
            errors.append({"field": "files.enabled", "messages": e.messages})
            return  # exit early

        if draft.files.enabled and not draft.files.items():
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
            errors.append({"field": "files.default_preview", "messages": e.messages})

    def edit(self, identity, draft=None, record=None):
        """Edit callback."""
        if draft.bucket is None:
            # Happens, when a soft-deleted draft is un-deleted.
            draft["files"] = {"enabled": True}
            draft.files.create_bucket()
        draft.files.copy(record.files)

    def new_version(self, identity, draft=None, record=None):
        """New version callback."""
        # We don't copy files from the previous version, but instead allow
        # users to import the files.
        draft.files.enabled = record.files.enabled

    def _publish_new(self, identity, draft, record):
        """Action when publishing a new draft."""
        # For unpublished drafts (new and new version), we move the draft
        # bucket from the draft to the record (instead of creating a new, and
        # deleting one). For consistency, we keep a bucket for all records
        # independently of if they have files enabled or not.
        record.files.set_bucket(draft.bucket)
        record.files.copy(draft.files, copy_obj=False)

        # Lock the bucket
        # TODO: Make the locking step optional in the future (so
        # instances can potentially allow files changes if desired).
        record.files.lock()

        # Cleanup
        if draft.files.enabled:
            draft.files.delete_all(remove_obj=False)
        draft.files.unset_bucket()

    def _publish_edit(self, identity, draft, record):
        """Action when publishing a edit to an existing record."""
        # TODO: For published records, we should sync changes from the
        # draft bucket to the record bucket, so that an instance could
        # potentially allow a user to update files. For now, sync() only
        # changes the default_preview and order
        record.files.sync(draft.files)

        # Teardown the bucket and files created in edit().
        if draft.files.enabled:
            draft.files.delete_all()
        draft.files.remove_bucket(force=True)

    def publish(self, identity, draft=None, record=None):
        """Copy bucket and files to record."""
        if draft.files.enabled and draft.files.bucket:
            if not draft.files.items():
                raise ValidationError(
                    _(
                        "Missing uploaded files. To disable files for "
                        "this record please mark it as metadata-only."
                    ),
                    field_name="files.enabled",
                )
        if draft.files.enabled:
            for file_record in draft.files.values():
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
        if draft.files.enabled:
            draft.files.delete_all(draft)
        draft.files.remove_bucket(force=True)

    def import_files(self, identity, draft=None, record=None):
        """Import files handler."""
        if not draft.files.enabled:
            raise ValidationError(
                _("Files support must be enabled."), field_name="files.enabled"
            )

        if draft.files.items():
            raise ValidationError(
                _("Please remove all files first."), field_name="files.enabled"
            )

        if not record.files.enabled and not record.files.bucket:
            raise ValidationError(
                _("The record has no files."), field_name="files.enabled"
            )

        # Copy over the files
        draft.files.copy(record.files)
