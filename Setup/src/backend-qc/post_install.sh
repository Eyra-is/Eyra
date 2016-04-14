#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

report "Firing up Celery worker for QC.."
cd ../Backend/server-interface
gnome-terminal -x sh -c "celery -A qc.celery_handler.celery worker --loglevel=info; bash"
cd -

return
