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

# Script to make "wrong" prompts from data. 

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

def modifyPrompt(prompt, wordlist, randomPrompt) -> {'orig':'original prompt', 
                                                     'sub':'substitution prompt', 
                                                     'ins':'insertion prompt', 
                                                     'del':'deletion prompt', 
                                                     'rand':'another random prompt'}:
    """
    Create 4 types of wrong prompts, insertions, substitutions, deletions and another random prompt. 
    See function code for more details.     
    """
    newPrompts = {'orig': prompt}

    # substitution (if prompt is more than 4 words), substitute all but 1 words
    if len(prompt) > 4:
        sub = list(prompt) # copy
        index = random.randint(0,len(prompt)-1) # word to keep
        for i, v in enumerate(sub):
            if i != index:
                word = random.choice(wordlist)
                sub[i] = word
        newPrompts['sub'] = sub

    # insertion (insert 5 words, unless prompt is more than 5 words, then double length + 2)
    ins = list(prompt)
    cnt_ins = 5 if len(prompt) < 6 else len(prompt) + 2
    for i in range(cnt_ins):
        word = random.choice(wordlist)
        index = random.randint(0,len(ins))
        ins.insert(index, word)
    newPrompts['ins'] = ins

    # deletion (if prompt is more than 4 words), delete all but one word
    if len(prompt) > 4:
        dele = list(prompt)
        for i in range(4):
            index = random.randint(0,len(dele)-1)
            del dele[index]
        newPrompts['dele'] = dele

    newPrompts['rand'] = randomPrompt

    return { k: ' '.join(v) for k,v in newPrompts.items()}

def run(data_path, lexicon_path) -> None:
    # create wordlist from lexicon
    with open(lexicon_path, 'r') as f:
        wordlist = [line.split('\t')[0] for line in f]

    modifiedPrompts = {} # format { recId: [promptOriginal, prompt2, prompt3, etc.]}
    with open(data_path, 'r') as f:
        content = f.readlines()
        for line in content:
            recId = line.split('\t')[0]
            prompt = line.split('\t')[1][:-1].split(' ')
            randomPrompt = random.choice(content).split('\t')[1][:-1].split(' ')
            newPrompts = modifyPrompt(prompt, wordlist, randomPrompt)
            for t in ['orig', 'sub', 'ins', 'dele', 'rand']:
                try:
                    print('{}\t{}'.format(t, newPrompts[t]))
                except KeyError as e:
                    if t == 'sub' or t == 'dele':
                        pass
                    else:
                        raise

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Script to make "wrong" prompts from data.""")
    parser.add_argument('data_path', type=str, help='Path to the data file containing recIds paired with prompts, format "recId\tprompt\n".')
    parser.add_argument('lexicon_path', type=str, help='Path to the lexicon, format "word\tw o r d".')
    args = parser.parse_args()

    run(args.data_path, args.lexicon_path)