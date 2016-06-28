#!/bin/bash -eu
#
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
#     Robert Kjaran <robert@kjaran.com>

# Generic LVCSR built using open/freely accessible data

nj=8
stage=-100

LEXICON_PATH="../../lang_data/jv/jv_lexicon_2016-04-25.txt"
PHONEME_PATH="../../lang_data/jv/phonemes.txt"
LANGDIR="data/lang"

. ./cmd.sh
. ./path.sh
. utils/parse_options.sh

if [ $stage -le 0 ]; then
    echo "Converting corpus to datadir"
    python3 data_prep.py /data/eyra/recordings data/all

    echo "Extracting features"
    steps/make_mfcc.sh \
        --nj $nj       \
        --mfcc-config conf/mfcc.conf \
        --cmd "$train_cmd"           \
        data/all exp/make_mfcc mfcc

    steps/compute_cmvn_stats.sh \
        data/all exp/make_mfcc mfcc

    utils/fix_data_dir.sh \
        data/all

    ln -s all data/train

    # echo "Splitting into a train and dev set"
    # utils/subset_data_dir_tr_cv.sh \
    #     --cv-utt-percent 10        \
    #     data/{all,train,dev}
fi

if [ $stage -le 1 ]; then
    echo "Lang preparation"

    DICTDIR="data/local/dict"
    mkdir -p $DICTDIR
    touch $DICTDIR/extra_questions.txt
    echo "sil" > $DICTDIR/optional_silence.txt
    echo -e "sil\nspn" > $DICTDIR/silence_phones.txt
    cut -f 1 $PHONEME_PATH > $DICTDIR/nonsilence_phones.txt
    cp $LEXICON_PATH $DICTDIR/lexicon.txt
    echo -e '<UNK>\tspn' >> $DICTDIR/lexicon.txt

    utils/prepare_lang.sh \
        $DICTDIR "<UNK>" data/local/lang $LANGDIR

    utils/validate_lang.pl $LANGDIR || { echo "lang dir invalid" && exit 1; }

    # local/prep_lang_test.sh
fi

if [ $stage -le 2 ]; then
    echo "Training mono system"
    steps/train_mono.sh    \
        --nj $nj           \
        --cmd "$train_cmd" \
        --totgauss 4000    \
        data/train         \
        data/lang          \
        exp/mono
fi

if [ $stage -le 3 ]; then
    steps/align_si.sh \
        --nj $nj --cmd "$train_cmd" \
        data/train data/lang exp/mono exp/mono_ali
    steps/train_deltas.sh  \
        --cmd "$train_cmd" \
        2000 10000         \
        data/train data/lang exp/mono_ali exp/tri1b
fi
