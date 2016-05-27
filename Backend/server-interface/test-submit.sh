#!/bin/bash
# Copyright 2016 Matthias Petursson
# Apache 2.0

set -x

curl -X POST -F 'json=
                {    
                    "type":"session",
                    "data": 
                    {
                        "speakerId"      : 1,
                        "instructorId"   : 1,
                        "deviceId"       : 1,
                        "location"       : "reykjavik iceland",
                        "start"          : "2015/12/12 15:00:00",
                        "end"            : "2015/12/12 15:01:00",
                        "comments"       : "people shouting in background a lot",
                        "recordingsInfo" : 
                        {
                            "test.wav"                    : { "tokenId" : 5 },
                            "test_commas_and_caps.wav"    : { "tokenId" : 2 },
                            "test_abbreviations.wav"      : { "tokenId" : 2 }                           
                        }
                    }
                }' -F 'rec0=@testData/test.wav' \
             -F 'rec1=@testData/test_abbreviations.wav' \
             -F 'rec2=@testData/test_commas_and_caps.wav' \
            http://127.0.0.1:5000/submit/session