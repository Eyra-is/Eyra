# API from Client to Server

1. submitRecordings
----------------

*Submit recordings, 1 or more, including metadata. Receives in return some way to ID said session.*

Current implementation:
* json format for session data:
```
'json': {    
            "type":"session",
            "data": 
            {
                "speakerInfo"    :  {
                                        "name": "jacksparrow",
                                        "gender": "female",
                                        "dob": "1991-1995",
                                        "height":"151-156"
                                        [, "deviceImei":"435763486"
                                         , "speakerId" : 55]
                                    },
                "instructorId"   : 1,
                "deviceInfo"     :  {
                                        "userAgent" : "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
                                        [, "imei" : "435763486"
                                         , "deviceId" : 44]
                                    },
                "location"       : "lat:13.7467017,lon:100.5399023,acc:33.888999938964844",
                "start"          : "2015/12/12 15:00:00",
                "end"            : "2015/12/12 15:01:00",
                "comments"       : "people shouting in background a lot",
                "recordingsInfo" : 
                {
                    "rec1name"      : { "tokenId" : 5, "tokenText" : "the quick brown..." },
                    "rec2name"      : { "tokenId" : 2, "tokenText" : "..." },
                    etc ...                            
                }
            }
        }
```
  * The 'json' key is the key in the form data itself.
  * Each tokenId must match it's corresponding recording filename including extension.
  * Server looks at sessions with the same info (minus end time of course), and if it is the same, it simply adds the recording to that session, and updates the end time of that session.
  * The deviceInfo 'imei' is optional.
    * Same goes for the speakerInfo 'deviceImei' and the {speaker,device}Id's.
  * The recordings in the submission (request.files) should be stored with keys 'rec0','rec1',..,'recn'
* json format of response:
```
        {
            "sessionId" : 5
        }
```
* url:
```
        /submit/session
```

2. getTokens
------------

*Client queries server for X number of tokens. Server returns tokens.*

Current implementation:
* json format: 
```
        [{"id":id1, "token":token1}, {"id":id2, "token":token2}, ...]
```
* url:
```
        /submit/gettokens/X
```
Where X is number of tokens.

3. submitInstructor
------------

*Submit instructor data, receives in return some way to ID said instructor.*

Current implementation:
* json format of submission:
```
'json': {
            "name" : "Jane Doe",
            "email" : "email@example.com",
            "phone" : 9999999,
            "address" : 23 Roseberry Lane
        }
```
* json format of response:
```
        {
            "instructorId" : 5
        }
```
* url:
```
        /submit/general/instructor
```

4. submitDevice
------------

*Submit device data.*

Current implementation:
* json format of submission:
```
'json': {
            "userAgent" : "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
            "imei" : "35145120840121"
        }
```
* url:
```
        /submit/general/device
```

5. queryQC
----------

*Query server for Quality Control reports.*

Current implementation:
* json format of response:
```
Returned dict if the QC report is not available, but is being
processed:

    {"sessionId": ...,
     "status": "started",
     "modules":{}}

Returned dict definition if no QC module is active:

    {"sessionId": ...,
     "status": "inactive",
     "modules":{}}

Returned dict definition:

    {"sessionId": ...,
     "status": "processing",
     "modules"  {
        "module1" :  {
                        "totalStats": {"accuracy": [0.0;1.0]"}
                        [, "perRecordingStats": [
                                {"recordingId": ...,
                                    "stats": {"accuracy": [0.0;1.0]}
                                },
                                ...]}
                        ]
                      }, 
                      ...
                }
    }
```
* url:
```
        /qc/report/session/X
```
Where X is the session id.