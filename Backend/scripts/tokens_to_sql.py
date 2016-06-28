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

# Usage: python tokens_to_sql.py src dest 
#
# turns tokens in src, 1 on each line, into sql ready to be run and placed into database
#
# Example: run on 'go
#                  get
#                  some
#                  pie' 
#              -> 'insert into token (inputToken)
#                  values
#                  ('go'),
#                  ('get'),
#                  ('some'),
#                  ('pie');'

import sys

def process(src, dest):
    f = src
    text = f.read().splitlines()
    g = dest
    g.write('insert into token (inputToken)\nvalues\n')
    for i, t in enumerate(text):
        if (i == len(text) - 1):
            g.write('(\''+t+'\');')
        else:
            g.write('(\''+t+'\'),\n')

def escape(s):
    return s.replace("'", r"\'")

def processLabels(src, dest):
    lines = src.read().splitlines()
    print('insert into token (inputToken, promptLabel)', file=dest)
    print('values', file=dest)
    for i, line in enumerate(lines):
        label, prompt = line.split(maxsplit=1)
        if (i == len(lines) - 1):
            print("('{}', '{}');".format(escape(prompt), label), file=dest)
        else:
            print("('{}', '{}'),".format(escape(prompt), label), file=dest)

def run():
    import argparse
    parser = argparse.ArgumentParser(
        description='Creates sql from src ready to be put into a token')
    parser.add_argument('src', type=argparse.FileType('r'),
                        help='Tokens/prompts, newline seperated')
    parser.add_argument('dest', type=argparse.FileType('w'), default=sys.stdout,
                        nargs='?',
                        help='Destination SQL file')
    parser.add_argument('--use-labels', action='store_true', default=False,
                        help=('Use language labels. `src` must then contain'
                              ' two tab seperated columns, language label and'
                              ' the prompt'))
    args = parser.parse_args()
    if args.use_labels:
        processLabels(args.src, args.dest)
    else:
        process(args.src, args.dest)

if __name__ == '__main__':
    run()
