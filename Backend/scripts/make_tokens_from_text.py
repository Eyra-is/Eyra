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

# Usage: python make_tokens_from_text.py src dest 
#
# Creates tokens, 1 on each line, from text
#
# THIS IS NOT USED CURRENTLY, but someone may find it useful.

import sys
import re

def process(src, dest):
    with open(src, 'r', encoding='utf8') as f:
        lines = f.read()
        # split on '. ', ', ' and '\n'
        lines = lines.replace('. ','\n').replace(', ','\n').split('\n')
        # filter out everything 10 chars or less
        lines = filter(lambda x: len(x)>10, lines)
        # capitalize
        lines = [x[0].upper()+x[1:] for x in lines]
        lines = filter(filterOutPuncuation, lines)
        # 33 is the average length of lines with 2+ words in the malromur tokens with everything
        lines = maxChar(lines, 33)
        # filter out everything that is only one word
        lines = filter(lambda x: len(x.split(' ')) > 1, lines)
        # filter out names (assume they have capitalized first and second word) among other accidental things
        lines = filter(filterOutNames, lines)
        with open(dest, 'w', encoding='utf8') as g:
            for line in lines:
                g.write(line + '\n')

# assumes x has 2 or more words split on space
def filterOutNames(x):
    words = x.split(' ')
    if (len(words[0]) > 0 and len(words[1]) > 0):
        return not (words[0][0].isupper() and words[1][0].isupper())
    return False

# returns lines filtered to contain no more than cnt chars
#   and skips the word that would go over cnt
def maxChar(lines, cnt):
    newLines = []
    for i, line in enumerate(lines):
        line = line.replace('\n','')
        words = line.split(' ')
        token = ''
        prevToken = token
        j = 0
        while len(token) < cnt and j < len(words):
            if j > 0:
                token += ' '
            token += words[j]
            if len(token) > cnt:
                token = prevToken
            prevToken = token
            j += 1
        if token != '':
            newLines.append(token)
    return newLines    

def filterOutPuncuation(x):
    if (re.match('^[\w\s]+$', x, re.UNICODE) is not None):
        return True
    return False

def run():
    if len(sys.argv) < 3:
        print( 
'Usage: python %s src dest \
\
Description: Creates tokens 1 on each line from text in src.\
' % sys.argv[0]
             )
        return
    else:
        process(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    run()