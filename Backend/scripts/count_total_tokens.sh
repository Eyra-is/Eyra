#!/bin/bash

cd ../server-interface/recordings
ls -1 session_* | (expr $(wc -l) / 2 - $(ls . | wc -l))
