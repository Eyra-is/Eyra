#!/bin/bash -eu

[[ "${BASH_SOURCE[0]}" != "${0}" ]] || {
  echo "$0: This script should be sourced, not executed!"
  exit 1
}

report "Firing up Celery worker for QC.. log in Local/Log/celery.log"
cd ../Backend/server-interface
# if we have more than 1 thread, set celery to use all except 1
nproc=$(nproc)
if [ $nproc -ne 1 ]; then
    nproc=$[nproc - 1]
else
    report_err "Using QC with only 1 thread is BAD. Get more cores pls."
fi
celery multi restart 1 -A qc.celery_handler.celery -c $nproc -D -f ../../Local/Log/celery.log --loglevel=info
cd -

return
