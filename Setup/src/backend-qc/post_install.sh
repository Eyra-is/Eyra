#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

report "Firing up Celery worker for QC.. log in Local/Log/celery.log"
cd ../Backend/server-interface
celery -A qc.celery_handler.celery worker --loglevel=info > ../../Local/Log/celery.log 2>&1 &
cd -

return
