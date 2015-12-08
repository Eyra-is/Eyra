#!/bin/bash

touch /tmp/recording.wav

set -x

curl -X GET -F 'help=usage' http://127.0.0.1:5000/interact/
curl -X GET -F 'json={"some_request":"I want this..."}' http://127.0.0.1:5000/interact/
curl -X POST -F 'json={"speaker":"sim","time":"today"}' -F 'file=@/tmp/recording.wav' http://127.0.0.1:5000/interact/

