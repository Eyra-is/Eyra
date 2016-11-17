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

# Analyse the output from parse_qc_dump.py used on data from analysis of prompts from 
# createWrongPrompts.py in respect to hypothesis and prompt. Test the alignment.

import os
import json
import MySQLdb
import sys
import csv
import statistics
import itertools
import numpy as np

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

def calcPhoneEditDistance(data, lexicon, isDict=True):
    """
    Similar to _calculatePhoneAccuracy from MarosijoModule

    data == (prompt, hyp)
    """ 
    accuracies = []
    if isDict:
        data = [val for key, val in data.items()]

    for pair in data:
        ref = pair[0].lower().replace('\ufeff','').split(' ')
        hyp = pair[1].replace('\ufeff','').split(' ')

        # convert all words in ref to phonemes, excluding oov
        try:
            ref_phones = [lexicon[x] for x in ref if x != '<UNK>']
        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            raise ValueError('Warning: couldn\'t find prompt words in lexicon or symbol table (grading with 0.0), prompt: {}'.format(ref))

        # convert all words in hyp to phonemes
        hyp_phones = []
        for x in hyp:
            try:
                hyp_phones.append(lexicon[x])
            except KeyError as e:
                # word in hyp not in lexicon, must be a phoneme, in which case just append it and remove the !
                hyp_phones.append(x[1:])

        ref_phones = list(itertools.chain.from_iterable(ref_phones))
        hyp_phones = list(itertools.chain.from_iterable(hyp_phones))

        N = len(ref_phones)
        ed, _ = _levenshteinDistance(hyp_phones, 
                                     ref_phones)

        try:
            ratio = 1 - min(ed / N, 1)
        except ZeroDivisionError as e:
            ratio = 0.0

        accuracies.append(ratio)

    return accuracies

def _levenshteinDistance(hyp, ref, cost_sub=1, cost_del=1, cost_ins=1):
    '''
    Returns the minimum edit distance (Levenshtein distance) between
    sequences `ref` and `hyp`, and the corresponding Levenshtein matrix.

    '''
    m, n = len(hyp)+1, len(ref)+1
    d = np.zeros((m, n))
    d[1:, 0] = range(1, m)
    d[0, 1:] = range(1, n)

    edits = []
    for j in range(1, n):
        for i in range(1, m):
            del_ = d[i-1, j] + cost_del
            ins_ = d[i, j-1] + cost_ins
            sub_ = d[i-1, j-1]
            sub_ += cost_sub if hyp[i-1] != ref[j-1] else 0
            d[i, j] = min(del_, ins_, sub_)

    return int(d[-1, -1]), d

def run(data_path, lexicon_path, prompt_col, hyp_col, wav_col):
    data = []
    with open(data_path, 'r') as f:
        csvdata = csv.reader(f, delimiter='\t')
        for row in csvdata:
            prompt = row[prompt_col - 1]
            hyp = row[hyp_col - 1]
            wav = row[wav_col - 1]
            data.append((prompt, hyp, wav))

    with open(lexicon_path, 'r') as f_:
        lexicon = {line.strip().split('\t')[0]:line.strip().split('\t')[1].split(' ')
                    for line in f_}

    print(len(data))

    original = [] # containing (prompt, hyp) pairs for the original prompts, idx here 
                  # corresponds to keys in following dicts
    substitutions = {} # for substitutions
    deletions = {} # for deletions (where the audio skipped a word)
    insertions = {} # for insertions (where the audio inserts a word)
    prevWav = 'not a wav my friend.mp3'
    originalIdx = -1
    last_action = 'not an action amigo'
    for pair in data:
        realPair = pair[0:2] # pair without wav
        currentWav = pair[2]
        if prevWav != currentWav:
            if last_action == 'original':
                # remove one-off prompts only in original and not with sub, ins versions
                original.pop()
                originalIdx -= 1
            original.append(realPair)
            originalIdx += 1
            last_action = 'original'
        elif last_action == 'original':
            substitutions[originalIdx] = realPair
            last_action = 'substitution'
        elif last_action == 'substitution':
            deletions[originalIdx] = realPair
            last_action = 'deletion'
        elif last_action == 'deletion':
            insertions[originalIdx] = realPair
            last_action = 'insertion'
        else:
            raise ValueError('Something wrong with data, you sure it originates from createWrongPrompts.py?')
        prevWav = currentWav

    # case where a one-off word was at end of original
    try:
        substitutions[len(original) - 1]
    except KeyError as e:
        original.pop()

    # make versions of sub, del and ins with the original reference prompt for reference (unchanged prompt)
    subs_orig = {}
    dels_orig = {}
    ins_orig = {}
    for i, val in enumerate(original):
        subs_orig[i] = (val[0], substitutions[i][1])
        dels_orig[i] = (val[0], deletions[i][1])
        try:
            ins_orig[i] = (val[0], insertions[i][1])
        except KeyError as e:
            # for one word prompts there should be no ins
            pass

    # output simple averages of phone error rates of analysis
    origAccs = calcPhoneEditDistance(original, lexicon, False)
    print('orig avg:', sum(origAccs) / len(origAccs))

    subAccs = calcPhoneEditDistance(subs_orig, lexicon)
    print('sub avg:', sum(subAccs) / len(subAccs))

    delAccs = calcPhoneEditDistance(dels_orig, lexicon)
    print('del avg:', sum(delAccs) / len(delAccs))

    insAccs = calcPhoneEditDistance(ins_orig, lexicon)
    print('ins avg:', sum(insAccs) / len(insAccs))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Analyse the output from parse_qc_dump.py used on data from analysis of prompts from 
        createWrongPrompts.py in respect to hypothesis and prompt. Test the alignment.""")
    parser.add_argument('data_path', type=str, help='Path to the processed dumps joined on the grades (tsv).')
    parser.add_argument('lexicon_path', type=str)
    parser.add_argument('prompt_col', type=int, help='Number of column containing the prompt.')
    parser.add_argument('hyp_col', type=int, help='Number of column containing the hypothesis.')
    parser.add_argument('wav_col', type=int, help='Number of column containing the wav filename.')

    args = parser.parse_args()

    run(args.data_path, args.lexicon_path, args.prompt_col, args.hyp_col, args.wav_col)