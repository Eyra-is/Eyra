## Redis layout

Here is the current layout of the Redis backend datastore (unless someone forgot to update this file... I`m looking at you Joe) used by the QC handler and modules, through Celery.

This list is in the form of a list of keys a long with references to where the descriptions of values can be found.

* `report/module/session_id` -> module specific session report
  * Where module is for example TestModule located in `modules/` and
    session_id is the id of the session this report belongs to.
  * The value description can be found in `qc_handler.getReport`

* `session/session_id/timestamp` -> a timestamp
  * Where session_id is the id of the session this last time the server was queried for a report belongs to.
  * Format of the timestamp can be found in `celery_handler.py`

* `session/session_id/recordings` -> a list of recordings + info
  * Where session_id is the id of the session this list of recordings info belongs to.
  * Format of the recordings + info can be found in `../db_handler.getRecordingsInfo`

* `session/session_id/processing` -> a simple flag, set to true if processing, deleted on a session timeout.

  