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

# Script to use MOS scores on a 4 point scale to compare quality of the 3 types of accuracies
# from Marosijo. (hybrid, phoneme and wer_norm)

import os
import json
import MySQLdb
import sys
import csv
import statistics

# mv out of qc/scripts/process_qc_dumps directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.pardir))
sys.path.append(newPath)
from config import dbConst
sys.path.remove(newPath)
del newPath

_db = MySQLdb.connect(**dbConst)
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

def calcAvg(data, grades, permissive):
    """
    Calculates average accuracies and stddev (hybrid, phone and wer_norm) given data
    on format as in run().

    Parameters:
        data        as format in run()
        grades      can be (1,), (2,), .., (1,2), .., (3,4)
                    or any number of configurations, meaning it will 
                    calculate the average of either
                    all who graded the specific recording 1 or 
                    all who graded either 1 or 2 etc. (if permissive is 0)
        permissive  an integer, 0 if everyone has to have the same grade,
                    1 if it is okay for one grader not to agree etc.
    """
    # keep all the numbers, to calculate stddev and avg
    hybrid_num = []
    phone_num = []
    wer_norm_num = []
    grade_num = []
    for recId, d in data.items():
        try:
            if len(d) > 4:
                log('More than 4 graders for same rec, is this right? data: { {} : [{}]}'.format(recId, d), 'warning')
            if len(d) < 4:
                log('Less than 4 graders for same rec, is this right? data: { {} : [{}]}'.format(recId, d), 'warning')
        except ValueError as e:
            print('recId:',recId)
            print('d:', d)
            raise
        valid = True
        cnt = 0
        for grade in d:
            if grade[1] not in grades:
                cnt += 1
            if cnt > permissive:
                valid = False
                break
        if valid:
            first = True
            for grade in d:
                if first:
                    hybrid_num.append(grade[2])
                    phone_num.append(grade[3])
                    wer_norm_num.append(grade[4])
                    first = False
                grade_num.append(grade[1])
    try:
        return {'hybrid_mean': statistics.mean(hybrid_num),
                'hybrid_stdev': statistics.pstdev(hybrid_num),
                'phone_mean': statistics.mean(phone_num),
                'phone_stdev': statistics.pstdev(phone_num),
                'wer_norm_mean': statistics.mean(wer_norm_num),
                'wer_norm_stdev': statistics.pstdev(wer_norm_num),
                'grade_mean': statistics.mean(grade_num),
                'grade_stdev': statistics.pstdev(grade_num),
                'count':len(hybrid_num)}
    except statistics.StatisticsError as e:
        log('Warning: {}'.format(e), 'warning')
        return {'hybrid_mean': -1,
                'hybrid_stdev': -1,
                'phone_mean': -1,
                'phone_stdev': -1,
                'wer_norm_mean': -1,
                'wer_norm_stdev': -1,
                'grade_mean': -1,
                'grade_stdev': -1,
                'count': 0}

def printRes(res):
    """
    Print results from calcAvg
    """
    print('Hybrid:\t\t{0:.5f}\t(stdev: {0:.5f})'.format(res['hybrid_mean'], res['hybrid_stdev']))
    print('Phone:\t\t{0:.5f}\t(stdev: {0:.5f})'.format(res['phone_mean'], res['phone_stdev']))
    print('Wer norm:\t{0:.5f}\t(stdev: {0:.5f})'.format(res['wer_norm_mean'], res['wer_norm_stdev']))
    print('Grade avg:\t{0:.5f}\t(stdev: {0:.5f})'.format(res['grade_mean'], res['grade_stdev']))

def printTsvLines(data, new_tsv):
    """
    Print recId\tnew_grade\thybrid_acc\tphone_acc\twer_norm_acc

    where new grade is 1,2,3,4 meaning 1 if <new_tsv> (all or all but one) gave grade 1, etc.

    if new_tsv is normalize new grade is grade is [0..1], i.e. ((4..16 - 4) / 12)
    """
    print('recId\tnew_grade\thybrid_acc\tphone_acc\twer_norm_acc')
    for recId, d in data.items():
        if len(d) > 4:
            log('More than 4 graders for same rec, is this right? data: { {} : [{}]}'.format(recId, d), 'warning')
        if len(d) < 4:
            log('Less than 4 graders for same rec, is this right? data: { {} : [{}]}'.format(recId, d), 'warning')
        
        new_grade = None
        if new_tsv == 'normalize':
            new_grade = (sum([grade[1] for grade in d]) - 4) / 12
        else:
            if new_tsv == 'all_agree':
                permissive = 4
            elif new_tsv == 'all_but_one':
                permissive = 3
            cnts = [-1, 0, 0, 0, 0] #counts for grade 1, 2, 3, 4
            done = False
            for grade in d:
                cnts[int(grade[1])] += 1
                for i, cnt in enumerate(cnts):
                    if cnt >= permissive:
                        new_grade = i
                        done = True
                        break
                if done:
                    break
        if new_grade:
            print('{}\t{}\t{}\t{}\t{}'.format(
                recId, new_grade, d[0][2], d[0][3], d[0][4]
            ))

def run(data_path, rec_id_col, listener_col, grade_col, hybrid_col, phone_col, wer_norm_col, new_tsv):
    # create a dict with: { recId : [(listener, grade, hybrid_acc, phone_acc, wer_norm_acc), ..], .. }
    data = {}
    with open(data_path, 'r') as f:
        csvdata = csv.reader(f, delimiter='\t')
        for row in csvdata:
            recId = row[rec_id_col - 1]
            hybrid_acc = float(row[hybrid_col - 1])
            phone_acc = float(row[phone_col - 1])
            wer_norm_acc = float(row[wer_norm_col - 1])
            listener = row[listener_col - 1]
            grade = float(row[grade_col - 1])
            listened_data = (listener, grade, hybrid_acc, phone_acc, wer_norm_acc) # the data to insert into dict
            try:
                data[recId].append(listened_data)
            except KeyError as e:
                data[recId] = [listened_data]
    # print('data:',data)

    if new_tsv == 'normal_execution':
        print('Showing results for {} graded recordings.'.format(len(data)))
        gradeCombinations = [(1,), (1,2), (2,), (3,), (3,4), (4,)]
        print('All agree:')
        for gradeC in gradeCombinations:
            res = calcAvg(data, gradeC, 0)
            print('Avg accuracies for combination: {} with count: {}'.format(gradeC, res['count']))
            printRes(res)


        print('All but one agree:')
        for gradeC in gradeCombinations:
            res = calcAvg(data, gradeC, 1)
            print('Avg accuracies for combination: {} with count: {}'.format(gradeC, res['count']))
            printRes(res)
    else:
        printTsvLines(data, new_tsv)

    print('Finished with {} warning/s.'.format(_warnings), file=sys.stderr)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Script to use MOS scores on a 4 point scale to compare quality of the 3 types of accuracies
        from Marosijo. (hybrid, phoneme and wer_norm)""")
    parser.add_argument('data_path', type=str, help='Path to the processed dumps joined on the grades (tsv).')
    parser.add_argument('rec_id_col', type=int, help='Number of column containing the recording id (start counting at 1).')
    parser.add_argument('listener_col', type=int, help='Number of column containing the listener (who graded).')
    parser.add_argument('grade_col', type=int, help='Number of column containing the grade (by a listener).')
    parser.add_argument('hybrid_col', type=int, help='Number of column containing the accuracy (by hybrid method).')
    parser.add_argument('phone_col', type=int, help='Number of column containing the accuracy (by phoneme method).')
    parser.add_argument('wer_norm_col', type=int, help='Number of column containing the accuracy (by wer norm method).')
    parser.add_argument('new_tsv', nargs='?', choices=['normal_execution', 'all_agree', 'all_but_one', 'normalize'], default='normal_execution', help='Make the script output only a new tsv with certain data and only the number of utterances lines, after deciding on a mutual grade for each.')
    args = parser.parse_args()

    run(args.data_path, args.rec_id_col, args.listener_col, args.grade_col, 
        args.hybrid_col, args.phone_col, args.wer_norm_col, args.new_tsv)