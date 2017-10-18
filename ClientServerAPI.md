# API from Client to Server


## 1. submitRecordings

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
                                        "dob": "1991-1995"
                                        [, "height":"151-156"
                                         , "deviceImei":"435763486"
                                         , "speakerId" : 55
                                         , "fullName": "Jack Sparrow"
                                         , "email": "jack@sparrow.com"
                                         , "agreementId": "2"]
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
  * Each tokenId must match its corresponding recording filename including extension.
  * Server looks at sessions with the same info (except with an updated end time), and if it is the same, it simply adds the recording to that session, and updates the end time of that session.
  * The deviceInfo 'imei' is optional.
    * Same goes for the speakerInfo 'deviceImei' and the {speaker,device}Id's.
  * The recordings in the submission (request.files) should be stored with keys 'rec0','rec1',..,'recn'
* json format of response:
```
        {
            "sessionId" : 5, "deviceId" : 6, "speakerId" : 2
        }
```
* url:
```
        /submit/session
```


## 2. getTokens

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


## 3. submitInstructor

*Submit instructor data. Server returns instructor ID.*

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


## 4. submitDevice

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


## 5. queryQC

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
                          "totalStats": {"accuracy": [0.0;1.0], "avgAcc": [0.0;1.0], 
                                         "lowerUtt": 31, "upperUtt": 36},
                          "perRecordingStats": [
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
  Where
  * `accuracy` is the cumulative average accuracy over all previous recordings
  * `avgAcc` is the average accuracy of the recordings in perRecordingStats.
  * `lowerUtt` is the number of recording processed for this session at the start of the latest batch
  * `upperUtt` is lowerUtt + recs processed in batch

  e.g. `accuracy` = 0.9, `avgAcc` = 0.8 (slightly worse this batch than overall),
       `lowerUtt` = 50, `upperUtt` = 55 (done a total of 55 recordings, batch size 5)

* url:
```
        /qc/report/session/X
```
Where X is the session id.


## 6. getFromSet

*Get a part from a certain set for evaluation.*

Current implementation:
* json format of response:
```
    [[recLinkN, promptN], .., [recLinkN+count, promptN+count]]
```
Where N is progress and recLink is the RECSURL + the relative path in the RECSROOT folder, e.g. `/recs/session_26/user_date.wav`.
* url:
```
        /evaluation/set/<string:eval_set>/progress/<int:progress>/count/<int:count>
```
Where `eval_set` is the set in question, corresponding to the entry in the `evaluation_sets` table in the database. `progress` is the first index in the set the client hasn't fetched yet (e.g. 5 if client has already fetched 5 elements already (0-4)). count is the number of elements to fetch.
* **Notes**:  
  * If the status code of the response is not 200, an error message might be supplied as `response.data`. E.g. if the set is not found, the server returns a 404.


## 7. submitEvaluation

*Submit evaluation of a part from a certain set.*

Current implementation:
* json format of submission:
```
'json': [
            {
                "evaluator": "daphne",
                "sessionId": 5,
                "recordingFilename": "asdf_2016-03-05T11:11:09.287Z.wav",
                "grade": 2,
                "comments": "Bad pronunciation",
                "skipped": false
            },
            ..
        ]
```
Where grade can be in [1-4]. If skipped is true, grade is ignored and it means the user skipped evaluating this recording.
* url:
```
        /evaluation/submit/<string:eval_set>
```
Where `eval_set` is the set in question, corresponding to the entry in the `evaluation_sets` table in the database.

## 8. getSetInfo

*Query for info about a specific set.*

Current implementation:
* json format of response:
```
    {
        "count": 52
    }
```
Currently only returns the number of elements in the set.
* url:
```
        /evaluation/setinfo/<string:eval_set>
```
Where `eval_set` is the set in question, corresponding to the entry in the `evaluation_sets` table in the database.

## 9. getUserProgress

*Query for progress into a specific set by a specific user.*

Current implementation:
* json format of response:
```
    {
        "progress": 541
    }
```
* url:
```
        /evaluation/progress/user/<string:user>/set/<string:eval_set>
```
Where `eval_set` is the set in question, corresponding to the entry in the `evaluation_sets` table in the database.

## 10. getPossibleSets

*Query for a list of all the sets available.*

Current implementation:
* json format of response:
```
    [
        "set1",
        "set2",
        ..
    ]
```
* url:
```
        /evaluation/possiblesets
```
