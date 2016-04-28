import requests
import json
import sys

def get_tokens(num):
  r = requests.get("https://www.dasistder.net/backend/submit/gettokens/"+str(num), verify=False)
  return r

def search_list(lst, key, value):
  for item in lst:
    if item[key] == value:
      return item

def read_metadata_file(inf):
  with open(inf,'rt') as df:
    lines = [ l.strip() for l in df.readlines() ]
  return lines
  
def subdata_string(d):
  return ('{{"speakerInfo":{{"name":"{9}","gender":"{13}","dob":"{14}","height":"unk","deviceImei":"{11}"}},'+
        '"instructorId":1,'+
        '"deviceInfo":{{"userAgent":"Frockend","imei":"{11}"}},'+
        '"location":"{15}, {16}",'+
        '"start":"{12}",'+
        '"end":"{4}",'+
        '"comments":"{3}",'+
        '"recordingsInfo":{{"{0}":{{"tokenId":{8}}}}}}}').format(*d) 

if __name__ == "__main__":
  
  # get all tokens from server
  token_resp = get_tokens('all')
  if (token_resp.status_code != 200):
    print("ERROR: ", token_resp.status_code)
    sys.exit(1)

  # Get all Tokens into a dictionary for faster lookup
  jsonData=json.loads(token_resp.text)
  ttab={}
  for t in jsonData:
    ttab[t['token']] = t['id']
  
  # read the metadata file
  promptData=read_metadata_file('data/Almannaromur/alldatacommas_clean.csv')
  
  for line in promptData:
    d = line.split(',')
    if d[8] not in ttab:
      print(None, d[8])
      continue
    d[8]=str(ttab[d[8]])
    print(subdata_string(d))

  sys.exit(0)
