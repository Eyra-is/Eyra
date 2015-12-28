# API from Client to Server


1. submitSession
----------------

*Submit data signifying one session (session being a single sitting by one speaker) including metadata + recordings*

Current implementation:
* json format:
```
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
                    "rec1name"      : { "tokenId" : 5 },
                    "rec2name"      : { "tokenId" : 2 },
                    etc ...                            
                }
            }
        }
```
Each tokenId must match it's corresponding recording filename including extension.
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