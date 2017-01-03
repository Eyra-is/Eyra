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

# number of functions taken non-DRY-ly (WET-ly?) from MarosijoModule

import os
import json
import MySQLdb
import sys
import csv
import statistics
import itertools
import numpy as np

_warnings = 0
avgPhonemeCount = 'change me please'


def log(arg, category=None):
    """
    Logs arg to stderr. To avoid writing to stdout (used in piping this scripts output to file)

    category is 'warning' or None
    """
    global _warnings
    if category == 'warning':
        _warnings += 1
    print(arg, file=sys.stderr)

def calculateWER(data, lexicon, isDict=True):
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

        wer = _levenshteinDistance(hyp, ref)[0] / len(ref)

        accuracies.append(0.0 if 1 - wer < 0 else 1 - wer)

    return accuracies

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

def calculateHybridAccuracy(data, lexicon, isDict=True):
    """
    Accuracy is some sort of metric, attempts to locate correct words.
    E.g. ref: the dog jumped over the fence
         hyp: the /c/o/d/ ran over the tent
    would result in an accuracy of 3/6 + 1/3*1/6 = 0.555 for getting the, over, the and a 
    single phoneme from dog correct.
    Extra words are also treated as errors, e.g.
         ref: the dog jumped over the fence
         hyp: /i/n/s/e/r/t/i/o/n/ the dog jumped over the fence
    would divide insertion by the average phoneme count of words (if 5) and then
    accuracy would be 6 - 5/4 / 6 = 4.75/6 = 0.792
    TODO not make this average, but use an actual phoneme 2 grapheme and locate the words
    Words in middle, are compared to phonemes of the words from ref, and a ratio of correct
    phonemes calculated from that.

    accuracy c [0,1]

    also calculates regular WER

    also calculates percentege of correctly guessed phonemes in hyp compared to the total phoneme guesses
    """

    wer_accuracies = []

    accuracies = []

    percentagePhones = []

    if isDict:
        data = [val for key, val in data.items()]

    oov = '<UNK>'
    avgPhonemeCount = round(sum([len(key) for val, key in lexicon.items()]) / max(len(lexicon), 1))

    for pair in data:
        ref = pair[0].lower().replace('\ufeff','').split(' ')
        hyp = pair[1].replace('\ufeff','').split(' ')

        # convert all words in ref to phonemes
        try:
            ref_phones = [lexicon[x] for x in ref if x != '<UNK>']
        except KeyError as e:
            # word in ref not in lexicon, abort trying to convert it to phonemes
            raise ValueError('Warning: couldn\'t find prompt words in lexicon or symbol table (grading 0.0), prompt: {}'.format(ref))

        aligned = _alignHyp(hyp, ref)
        ali_no_oov = [x for x in aligned if x != -2] # remove oov for part of our analysis
        hyp_no_oov = [x for x in hyp if x != oov]

        # mark positions of recognized words, e.g. rec_words = [0, 3, 5]
        rec_words = []
        # mark all strings of -1's (meaning we have phonemes inserted)
        minus_ones = [] # minus_ones = [(1,3), (4,5), ..], i.e. tuples of linked sequences of -1's
        inSequence = False
        seq = [] # partial sequence
        for i, a in enumerate(ali_no_oov):
            if a == -1 and not inSequence:
                inSequence = True
                seq.append(i)
            if a != -1 and inSequence:
                inSequence = False
                seq.append(i)
                minus_ones.append(seq)
                seq = []
            # if we have -1's at the end of ali_no_oov
            if i == len(ali_no_oov) - 1 and a == -1 and inSequence:
                seq.append(len(ali_no_oov))
                minus_ones.append(seq)
            if a >= 0:
                rec_words.append(a)

        # for each sequence of -1's calculate phoneme overlap with corresponding words.
        # e.g. if ref: the cat jumped
        #         hyp: the cat j u m p
        # we would calc the overlap of 'j u m p e d' with 'j u m p'
        ratios = [] # len(ratios) == len(minus_ones) ratios of each sequence phoneme overlap (contribution to word error rate)

        #
        wer_insertions = 0
        totalPhones = 0
        correctPhones = 0 # number of phones which matched a word

        for seq in minus_ones:
            # convert seq to phoneme list, grab e.g. !h from symbolTable and remove ! to match with lexicon
            seq_phones = []
            for x in hyp_no_oov[seq[0]:seq[1]]:
                try:
                    seq_phones.append(lexicon[x])
                except KeyError as e:
                    # word in hyp not in lexicon, must be a phoneme, in which case just append it and remove the !
                    seq_phones.append(x[1:])
            ref_phones_range = () # which indices in ref_phones do we want to compare to? (which words)
            # figure out which words we should compare each phoneme sequence with
            # find out if we are a -1 sequence in the beginning, middle or end of the hyp
            if seq[0] == 0:
                # beginning, look at all words up to the first recognized word
                if rec_words:
                    ref_phones_range = (0, rec_words[0])
                else:
                    # no recognized words, compare to entire ref
                    ref_phones_range = (0, len(ref_phones))
            elif seq[-1] == len(hyp_no_oov):
                # end, look at words from last recognized word
                ref_phones_range = (rec_words[-1]+1, len(ref_phones))
            else:
                # middle, look at words between recognized words to the left&right of this sequence
                # since this is neither beginning or end, we know we have recognized words on both sides
                # e.g. aligned: [0, 1, -1, -1, -1, 4]
                # we want to look at words ref[2:4]
                ref_phones_range = (ali_no_oov[seq[0]-1]+1, ali_no_oov[seq[1]])

            hybridPenalty = 1.5
            if ref_phones_range[1] - ref_phones_range[0] > 0:
                # use formula
                # (1 - min(ed/N, hybridPenalty))*wc
                # meaning, if edit distance (levenshtein)
                # is =N (number of phonemes in our attempted words to match (from ref_phones)) 
                # we get a score of zero for this sequence.
                # If edit distance is more (e.g. our aligner inserted more phonemes than are in
                # the reference), we can get a penalty for at most (1-hybridPenalty)*ref word count
                # for the entire sequence.
                N = sum([len(ref_phones[i]) for i in range(ref_phones_range[0], ref_phones_range[1])])
                ed, _ = _levenshteinDistance(seq_phones, 
                                              list(
                                                itertools.chain.from_iterable(
                                                    ref_phones[ref_phones_range[0] : ref_phones_range[1]])
                                              ))

                ratio = 1 - min(ed / N, hybridPenalty)
                normalized_ratio = ratio*(ref_phones_range[1] - ref_phones_range[0])  
                ratios.append(normalized_ratio)

                numPhones = int(seq[1]-seq[0])
                totalPhones += numPhones
                correctPhones += max(numPhones, N) - ed
            else:
                # no words to compare to (empty interval this seq compares to)
                # attempt to attempt to give some sort of minus penalty
                # in similar ratio to the one above (if hybridPenalty=1.5 then at most -1/2*wc)
                # use average phoneme count from lexicon, and give at most
                # an error of 1/2 that. For example if avg=5 and our seq has
                # 11 phonemes we give an error of -1/2 * floor(11/5) = -1
                ratios.append((1 - hybridPenalty) * int((seq[1]-seq[0]) / avgPhonemeCount))

                wer_insertions += 1

                totalPhones += int(seq[1]-seq[0])

        # WAcc = (H - I)/N
        # https://en.wikipedia.org/wiki/Word_error_rate
        wer_accuracies.append((len([x for x in aligned if x >= 0]) - wer_insertions) / len(ref))

        accuracies.append(max((len(rec_words) + sum(ratios)) / len(ref) , 0))

        try:
            percentagePhones.append(correctPhones / totalPhones)
        except ZeroDivisionError as e:
            pass

    return (wer_accuracies, accuracies, percentagePhones)

def _alignHyp(hyp, ref) -> list:
    """
    Attempts to enumerate the hypothesis in some smart manner. E.g.

    ref:    the dog jumped    across
    hyp:        dog /j/u/m/p/ across
    output:     1   -1-1-1-1  3

    Where /j/u/m/p/ represents 4 phonemes inserted instead of jumped and
    these would usually be the integer ids of the words.
    Output is the indices in ref the words in hyp correspond to.

    Parameters:
        hyp     list with the integer ids of the hyp words
        ref     same as hyp with the reference

    Pairs the hypotheses with the index of correct words in the reference. 
    -1 for hypotheses words not in ref (should only be phonemes)
    -2 if hyp word is oov <UNK>.

    Would have used align-text.cc from Kaldi, but it seemed to not perform well
    with all the inserted phonemes (on a very informal check).

    Better description of the algorithm used:
        TO DO WRITE DESC
    """

    # private functions to _alignHyp
    def _wordsBetween(aligned, idx):
        """
        Attempts to see if there are any words between
        the current idx and the last matched word in hyp, 
        and no word in between it in the ref.
        E.g.
            ref: joke about stuff
            hyp: joke and go to stuff

        With: aligned = [0, -1, -1, -1]
              idx     = 2
        Would result in False, since "and go to" could be the aligners interpretation of about.

            ref: go to France
            hyp:    to five France

        With: aligned = [1, -1]
              idx     = 2
        Would result in True, since "five" is between to and France
        """
        newAligned = [x for x in aligned if x != -1] # remove -1's
        try:
            lastMatch = newAligned[-1]
        except IndexError as e:
            return False # return false if no recognized word

        if idx - lastMatch > 1:
            return False

        # if we have some -1's after our last match, return true
        if aligned.index(lastMatch) != len(aligned) - 1:
            return True

        return False

    def _isLater(idx, ref):
        """
        Checks to see if ref[idx] is repeated in ref somewhere later,
        and in which case return the later idx.

        Returns -1 if ref[idx] is not repeated.
        """
        refSlice = ref[idx:]
        refSlice[0] = -1
        try:
            return refSlice.index(ref[idx]) + idx
        except ValueError as e:
            return -1

    def _isEarlier(idx, ref):
        """
        Checks to see if ref[idx] is repeated in ref somewhere earlier,
        and in which case return the earlier idx.

        Returns -1 if ref[idx] is not earlier.
        """
        upToIdx = ref[0:idx+1]
        isEarlier = _isLater(0, upToIdx[::-1]) # isEarlier === isLater(new idx, reversed list)
        return len(upToIdx) - isEarlier - 1 if isEarlier != -1 else -1

    oov = '<UNK>'
    refC = list(ref) # ref copy
    aligned = []
    for h in hyp:
        try:
            if h == oov:
                aligned.append(-2)
                continue

            idx = refC.index(h)
            # handle cases with multiple instances of the same word
            # in case our hypothesised index in the hyp is lower than 
            # some idx in aligned, we know that cannot be, so the only
            # chance is that it is the same word later in the hyp (or not there)
            # In addition, if we see 1 or more words (like dung in the example)
            # which could have been the interpretation of dog, we assume it is the
            # second instance of the word (if present, otherwise assume first instance).
            # e.g. 
            #    ref: the dog ate the dog
            #    hyp: the dung dog
            #    res:   0   -1   4
            refC[idx] = -1 # remove word from ref if we match, in case we have multiple of the same
            while True:
                try:
                    if any(idx < x for x in aligned) or _wordsBetween(aligned, idx):
                        idx = refC.index(h)
                        refC[idx] = -1
                    else:
                        break
                except ValueError as e:
                    break
        except ValueError as e:
            idx = -1
        aligned.append(idx)
    # do a second pass
    # if the aligned array is not strictly non-decreasing, fix it
    # e.g. if aligned = [0, -1, -1, 3, 2]
    # see if the one marked 2 isn't supposed to be the same word later in ref
    # this could be problematic if the same 2 words are repeated twice,
    # and possibly if the same word is repeated 3 times as well
    prevA = -sys.maxsize
    for i, a in enumerate(aligned):
        if a < 0:
            continue
        if a <= prevA:
            # we have decreasing
            newIdx = _isLater(a, ref)
            if newIdx != -1:
                aligned[i] = newIdx
            else:
                # now see if the 3 in the example above shouldn't be earlier
                newIdx = _isEarlier(prevA, ref)
                if newIdx != -1 and newIdx not in aligned:
                    aligned[i-1] = newIdx
                else:
                    raise MarosijoError('Error: couldn\'t align {} with hyp: {} and ref: {} and aligned: {}'
                        .format(ref[a], hyp, ref, aligned))
        prevA = a

    return aligned

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

    avgPhonemeCount = round(sum([len(key) for val, key in lexicon.items()]) / max(len(lexicon), 1)) # thanks, NPE, http://stackoverflow.com/a/7716358/5272567


    #print(len(data))

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

    print('Phone acc:')

    # output simple averages of phone error rates of analysis
    origAccs = calcPhoneEditDistance(original, lexicon, False)
    print('orig avg:', sum(origAccs) / len(origAccs))
    subAccs = calcPhoneEditDistance(subs_orig, lexicon)
    print('sub avg:', sum(subAccs) / len(subAccs))
    delAccs = calcPhoneEditDistance(dels_orig, lexicon)
    print('del avg:', sum(delAccs) / len(delAccs))
    insAccs = calcPhoneEditDistance(ins_orig, lexicon)
    print('ins avg:', sum(insAccs) / len(insAccs))

    print('WER:')

    origAccs = calculateHybridAccuracy(original, lexicon, False)
    print('orig avg:', sum(origAccs[0]) / len(origAccs[0]))
    subAccs = calculateHybridAccuracy(subs_orig, lexicon)
    print('sub avg:', sum(subAccs[0]) / len(subAccs[0]))
    delAccs = calculateHybridAccuracy(dels_orig, lexicon)
    print('del avg:', sum(delAccs[0]) / len(delAccs[0]))
    insAccs = calculateHybridAccuracy(ins_orig, lexicon)
    print('ins avg:', sum(insAccs[0]) / len(insAccs[0]))

    print('Hybrid acc:')

    print('orig avg: {} (cnt: {})'.format(sum(origAccs[1]) / len(origAccs[1]), len(origAccs[1])))
    print('sub avg: {} (cnt: {})'.format(sum(subAccs[1]) / len(subAccs[1]), len(subAccs[1])))
    print('del avg: {} (cnt: {})'.format(sum(delAccs[1]) / len(delAccs[1]), len(delAccs[1])))
    print('ins avg: {} (cnt: {})'.format(sum(insAccs[1]) / len(insAccs[1]), len(insAccs[1])))

    print('Ratio correct phones avg:')

    print('orig avg: {} (cnt: {})'.format(sum(origAccs[2]) / len(origAccs[2]), len(origAccs[2])))
    print('sub avg: {} (cnt: {})'.format(sum(subAccs[2]) / len(subAccs[2]), len(subAccs[2])))
    print('del avg: {} (cnt: {})'.format(sum(delAccs[2]) / len(delAccs[2]), len(delAccs[2])))
    print('ins avg: {} (cnt: {})'.format(sum(insAccs[2]) / len(insAccs[2]), len(insAccs[2])))

    print('Old WER:')

    origAccs = calculateWER(original, lexicon, False)
    print('orig avg:', sum(origAccs) / len(origAccs))
    subAccs = calculateWER(subs_orig, lexicon)
    print('sub avg:', sum(subAccs) / len(subAccs))
    delAccs = calculateWER(dels_orig, lexicon)
    print('del avg:', sum(delAccs) / len(delAccs))
    insAccs = calculateWER(ins_orig, lexicon)
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