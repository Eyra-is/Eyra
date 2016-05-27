# Copyright 2016 Matthias Petursson
# Apache 2.0

import sys
import os
import re

wordsToRemove = [
    'hv',
    'hæstv'
]

def process(sortedSentDir, lowerWCBound, upperWCBound, dest):
    with open(dest, 'w', encoding='utf8') as f:
        for i in range(int(lowerWCBound), int(upperWCBound)+1):
            pathToWords = os.path.join(sortedSentDir, str(i), 'sentences.words')
            if (os.path.exists(pathToWords)):
                with open(pathToWords, 'r', encoding='utf8') as tmp:
                    f.write(extractSentences(tmp.read().splitlines()))

def extractSentences(data):
    """
    Expects data on format as a list of all lines in sentences.words in the MIM prompts without \n. 
    Extracts them by returning token1\ntoken2\ntoken3 etc.. with one sentence each line.
    """
    out = ''
    # remove initial sentence tag
    data = [' '.join(y.split(' ')[1:]) for y in data]
    data = filter(filterOutNumbers, data)
    for line in data:
        words = line.split(' ')
        words = filter(filterOutPuncuation, words)
        words = filter(lambda x: x not in wordsToRemove, words)
        words = list(words)
        if len(words) >= 1 and not containsCapsAbbrev(words):
            out += ' '.join(words) + '\n'
    return out


def filterOutPuncuation(x):
    if re.match(r'^[\w\s]+$', x, re.UNICODE) is not None:
        return True
    return False

def filterOutNumbers(x):
    if re.search(r'\d', x, re.UNICODE) is not None:
        return False
    return True

def containsCapsAbbrev(x):
    '''
    Test if list x contains e.g. OECD, DNA, RNA which are abbreviations but
    not filtered out with punctuation.
    '''
    for word in x:
        upperCase = 0
        for c in word:
            if c.isupper():
                upperCase += 1
        if upperCase >= 2:
            return True
    return False

def run():
    if len(sys.argv) < 5:
        print( 
'Usage: python %s sortedSentDir lowerWCBound upperWCBound dest\n\
Description: Processes sorted MIM tokens, using the sorted/X/sentences.words files.\n' % sys.argv[0]
+
'sortedSentDir is the directory containing the folders 1,2,3,4,5,... e.g. /yourpath/MIM_prompts/sent_free/sentences/sorted\n\
lower and upper WCBound are the number of words per sentence you want. E.g. 5 and 10 would give you all sentences with\
between 5 and 10 words inclusive.\n\
dest is the destination file with the output tokens, one on each line.' 
             )
        return
    else:
        process(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == '__main__':
    run()