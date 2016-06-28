#!/bin/bash
#
# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

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