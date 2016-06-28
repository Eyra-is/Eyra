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

curl -k -X POST -F 'json=
                {    
                    "type":"session",
                    "data": 
                    {
                        "speakerInfo"    :  {
                                                "name": "jacksparrow",
                                                "gender": "female",
                                                "dob": "1991-1995",
                                                "height":"151-156"
                                                , "deviceImei":"notarealimei"
                                                , "speakerId" : 55
                                            },
                        "instructorId"   : 1,
                        "deviceInfo"     :  {
                                                "userAgent" : "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
                                                , "imei" : "notarealimei"
                                                , "deviceId" : 44
                                            },
                        "location"       : "lat:13.7467017,lon:100.5399023,acc:33.888999938964844",
                        "start"          : "2015/12/12 15:00:00",
                        "end"            : "2015/12/12 15:01:00",
                        "comments"       : "people shouting in background a lot",
                        "recordingsInfo" : 
                        {
                            "test1.wav"      : { "tokenId" : 5, "tokenText" : "the quick brown..." },
                            "test2.wav"      : { "tokenId" : 2, "tokenText" : "..." },
                            "test3.wav"      : { "tokenId" : 6, "tokenText" : "..." }                           
                        }
                    }
                }' -F 'rec0=@test/test1.wav' \
             -F 'rec1=@test/test2.wav' \
             -F 'rec2=@test/test3.wav' \
            https://localhost/backend/submit/session