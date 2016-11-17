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

# Script to make "wrong" prompts from data. Intended for example, to create an evaluation set
# for QC by taking utterances known to be good, and modifying the prompt and comparing
# QC results.
#
# E.g. prompt: the quick brown fox
#     mangled: the random brown fox
#              a the quick brown fox
#              the quick fox  

import os
import sys
import random

_warnings = 0

def log(arg, category=None):
    """
    Logs arg to stderr. To avoid writing to stdout (used in piping this scripts output to file)

    category is 'warning' or None
    """
    global _warnings
    if category == 'warning':
        _warnings += 1
    print(arg, file=sys.stderr)

def modifyPrompt(prompt, wordlist) -> ['original prompt', 'substitution prompt', 'insertion prompt', 'deletion prompt']:
    """
    Modifies a prompt, e.g. "the lazy cat"
                          ->"the crazy cat"
                          ->"lazy cat"
                          ->"the really lazy cat"
    i.e. one substitution (with a random word from lexicon),
         one insertion (random position)
    and  one deletion (random word)

    Parameters:
        prompt      words as a list
        wordlist    a list of words used to choose random words for insertion/substitution      
    """
    newPrompts = [prompt]

    # substitution
    word = random.choice(wordlist)
    index = random.randint(0,len(prompt)-1)
    sub = list(prompt) # copy
    sub[index] = word
    newPrompts.append(sub)

    # insertion
    word = random.choice(wordlist)
    index = random.randint(0,len(prompt))
    ins = list(prompt)
    ins.insert(index, word)
    newPrompts.append(ins)

    # deletion (if prompt is more than one word)
    if len(prompt) > 1:
        index = random.randint(0,len(prompt)-1)
        dele = list(prompt)
        del dele[index]
        newPrompts.append(dele)

    return [' '.join(x) for x in newPrompts]

def run(data_path, lexicon_path) -> None:
    # create wordlist from lexicon
    with open(lexicon_path, 'r') as f:
        wordlist = [line.split('\t')[0] for line in f]

    modifiedPrompts = {} # format { recId: [promptOriginal, prompt2, prompt3, etc.]}
    with open(data_path, 'r') as f:
        for line in f:
            recId = line.split('\t')[0]
            prompt = line.split('\t')[1][:-1].split(' ')
            newPrompts = modifyPrompt(prompt, wordlist)
            for p in newPrompts:
                print(p)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Script to make "wrong" prompts from data. Intended for example, to create an evaluation set
        for QC by taking utterances known to be good, and modifying the prompt and comparing
        QC results.
        
        E.g. prompt: the quick brown fox
            mangled: the random brown fox
                     a the quick brown fox
                     the quick fox""")
    parser.add_argument('data_path', type=str, help='Path to the data file containing recIds paired with prompts, format "recId\tprompt\n".')
    parser.add_argument('lexicon_path', type=str, help='Path to the lexicon, format "word\tw o r d".')
    args = parser.parse_args()

    run(args.data_path, args.lexicon_path)