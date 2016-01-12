# API from Client to Server


1. submitRecordings
----------------

*Submit recordings, 1 or more, including metadata.*

Current implementation:
* json format for session data:
```
'json': {    
            "type":"session",
            "data": 
            {
                "speakerInfo"    :  {
                                        'name': jacksparrow,
                                        'gender': female,
                                        'dob': '1991-1995',
                                        'height':'151-156'
                                        [, 'deviceImei':435763486]
                                    },
                "instructorId"   : 1,
                "deviceInfo"     :  {
                                        "userAgent" : "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
                                        "imei" : "35145120840121"
                                    },
                "location"       : "reykjavik iceland",
                "start"          : "2015/12/12 15:00:00",
                "end"            : "2015/12/12 15:01:00",
                "comments"       : "people shouting in background a lot",
                "recordingsInfo" : 
                {
                    "rec1name"      : { "tokenId" : 5 },
                    "rec2name"      : { "tokenId" : 2 },
                    etc ...                            
                }
            }
        }
```
  * The 'json' key is the key in the form data itself.
  * Each tokenId must match it's corresponding recording filename including extension.
  * Server looks at sessions with the same info (minus end time of course), and if it is the same, it simply adds the recording to that session, and updates the end time of that session.
  * The deviceInfo 'imei' is optional.
    * Same goes for the speakerInfo 'deviceImei'.
* The recordings in the submission (request.files) should be stored with keys 'rec0','rec1',..,'recn'
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

5. submitSpeaker
------------

*Submit speaker data.*

Current implementation:
* json format of submission:
```
'json': { 
            'name': jacksparrow,
            'gender': female,
            'dob': '1991-1995',
            'height':'151-156'
            [, 'deviceImei':435763486]
        }
```
  * The device imei is optional, and is a way to link this speaker to the device it was created on.
* url:
```
        /submit/general/speaker
```