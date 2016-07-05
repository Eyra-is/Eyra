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

# Decode wavs and info in the firebase data obtained using commands from usefulFirebaseCommands.sh.list.
# TODO make a script to insert this data into our database.

import json
import os
import base64

def run(encoded_wav_dir, output_dir='firebase_wavs'):
    os.makedirs(output_dir, exist_ok=True)

    for encoded_file in os.listdir(encoded_wav_dir):
        encoded_file = os.path.join(encoded_wav_dir, encoded_file)
        print('Processing file: {}'.format(encoded_file))
        with open(encoded_file) as f:
            encoded_data = json.load(f)

        metadata = encoded_data['metadata']
        metadata = json.loads(metadata.replace('\\"', '"'))
        data = metadata['data']
        speaker = data['speakerInfo']['name']
        recordingsInfo = data['recordingsInfo']
        recordings = encoded_data['recordings']

        if (len(recordingsInfo) != len(recordings)):
            raise ValueError('recordingsInfo ({}) and recordings ({}) not same length.'.format(len(recordingsInfo), len(recordings)))

        for rec, info in recordingsInfo.items():
            token = info['tokenText']
            for blob in recordings:
                if blob['title'] == rec:
                    wav = base64.b64decode(blob['blob64'][22:])
                    with open(os.path.join(output_dir,'{}_{}'.format(speaker, rec)), 'wb') as f:
                        f.write(wav)
                    with open(os.path.join(output_dir,'{}_{}.txt'.format(speaker, rec[:-4])), 'w') as g:
                        g.write(token)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Decode wavs and info in the firebase data obtained using commands from usefulFirebaseCommands.sh.list. 
        Output on format wav1.wav paired with wav1.txt with the prompt.""")
    parser.add_argument('encoded_wav_dir', type=str, help='Path to encoded metadata/wavs as obtained from usefulFirebaseCommands.sh.list')
    parser.add_argument('output_dir', type=str, nargs='?', help='Path to decoded wavs/txts')
    args = parser.parse_args()

    if args.output_dir:
        run(args.encoded_wav_dir, args.output_dir)
    else:
        run(args.encoded_wav_dir)