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

# Script to make ready the wrong prompts for use with Kaldi.

import os
import csv
import sh

WAVPATH = '/data/Almannaromur/audio'

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

def run(data_path, wav_path) -> None:
    with open(data_path, newline='') as data:
        datareader = csv.reader(data, delimiter='\t')
        # create dict with prompt as key and different versions of mangled prompt as values
        # { prompt : 
        #      {'ins':insprompt, 'rand':randprompt [, 'sub':subprompt, 'dele':deleprompt] }
        # }
        badPrompts = {}
        currentPrompt = ''
        for row in datareader:
            kind = row[0]
            prompt = row[1]
            if kind == 'orig':
                badPrompts[prompt] = {}
                currentPrompt = prompt
            else:
                badPrompts[currentPrompt][kind] = prompt

            if not currentPrompt:
                raise ValueError('Something wrong.')

    with open(wav_path, newline='') as wav:
        wavreader = csv.reader(wav, delimiter='\t')
        # for each record here (all unique wavs)
        # create symlinks to those wavs and output the new prompts\twav
        for row in wavreader:
            prompt = row[0]
            wavName, ext = os.path.splitext(row[2])
            origWav = row[2]
            for t in ['sub', 'ins', 'dele', 'rand']:
                try:
                    newWav = '{}_{}{}'.format(wavName, t, ext)
                    #sh.ln(os.path.join(WAVPATH, origWav), os.path.join(WAVPATH, newWav))
                    print('{}\t{}'.format(newWav, badPrompts[prompt][t]))
                except KeyError as e:
                    if t == 'sub' or t == 'dele':
                        pass
                    else:
                        raise


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Uses output of createBadData.py (and another file joined on prompt 
        containing wav name see format in help) so rec names
        can be used as unique keys for Kaldi (pairing the recordings with the bad prompts).
        Creates names like: oldwav_ins.wav, oldwav_sub.wav, oldwav_dele.wav, oldwav_rand.wav
        depending on how the prompt was modified.""")
    parser.add_argument('data_path', type=str, help='Path to output tsv of createBadData.py. Format: [orig|sub|ins|dele]\tprompt')
    parser.add_argument('wav_path', type=str, help='Path to the data file format: prompt\tthe word orig\twav name. Only prompt and wav name are used.')
    args = parser.parse_args()

    run(args.data_path, args.wav_path)