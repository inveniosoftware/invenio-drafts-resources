..
    Copyright (C) 2020-2023 CERN.
    Copyright (C) 2020 Northwestern University.

    Invenio-Drafts-Resources is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 1.12.0 (2023-10-09)

- versions: set the next index to the max index of all record versions

Version 1.11.2 (2023-10-02)

- components: handle disabled state on draft delete action

Version 1.11.1 (2023-10-02)

- components: replace ambiguous error on publish

Version 1.11.0 (2023-09-21)

- resources: add etag headers
- resources: add search request param to schema

Version 1.10.1 (2023-09-18)

- models: avoid flushing when getting records

Version 1.10.0 (2023-09-05)

- uow: add ParentRecordCommitOp uow

Version 1.9.0 (2023-09-05)

- service: allow passing of 'extra_filter' via kwargs to searches

Version 1.8.1 (2023-08-25)

- tasks: add margin time window for search to purge deleted documents
- services: move reindex latest records from records-resources

Version 1.8.0 (2023-08-16)

- components: conditional lock of files
- components: refactor file workflow

Version 1.7.1 (2023-08-14)

- fix an issue where the next version of the draft is incorrectly set

Version 1.7.0 (2023-08-10)

- records: read_latest method now accepts parent_id and it
  will return the latest version of a record also by parent_id
- change error message when publishing with missing files,
  depending if the record can be metadata only

Version 1.6.0 (2023-07-21)

- Add parent id resolver

Version 1.5.0 (2023-07-11)

- add media files components

Version 1.4.2 (2023-07-05)

- transifex: update config
- components: add default files enabled variable

Version 1.4.1 (2023-06-06)

- fix permission check for managing files

Version 1.4.0 (2023-04-25)

- upgrade invenio-records-resources
- ensure testing of file indexing

Version 1.3.0 (2023-04-20)

- upgrade invenio-records-resources

Version 1.2.0 (2023-03-24)

- bump invenio-records-resources to v2.0.0

Version 1.1.1 (2023-03-03)

- permissions: add can manage files permission to the draft

Version 1.1.0 (2023-03-02)

- remove deprecated flask-babelex dependency and imports
- install invenio-i18n explicitly

Version 1.0.4 (2023-02-22)

- service: allow to ignore field-level permission checks in validate_draft
- files: publishing files pending download from Fetch

Version 1.0.3 (2022-12-02)

- Fix rebuild index memory usage

Version 1.0.2 (2022-11-25)

- Add i18n translations.

Version 1.0.1 (2022-11-15)

- Use bulk indexing for service `rebuild_index` method.

Version 1.0.0 (2022-11-04)

- Bump invenio-records-resources version

Version 0.2.2 (2020-08-19)

- Fix support for Elasticsearch 6 and 7

Version 0.2.1 (2020-08-18)

- Initial public release.
