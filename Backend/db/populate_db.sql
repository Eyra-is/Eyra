/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/*
File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

-- basic inserts to start with the "dummy" instructors/devices etc
start transaction;

insert into device (userAgent, imei)
values
    ('Mobile Browser Mozilla etc.', 'NOTAVALIDPHONEID');
insert into instructor (name, email, phone, address)
values
    ('Jane Doe', 'dummy@jk.is', '1-800-DONT-CALL', 'Australia');
insert into speaker (name, deviceImei)
values
    ('John Doe', 'NOTAVALIDPHONEID');
insert into speaker_info (speakerId, s_key, s_value)
values
    (1, 'sex', 'male'),
    (1, 'dob', '1991-1995'),
    (1, 'height', '170');
insert into session (speakerId, instructorId, deviceId, location, start, end, comments)
values 
    (1, 1, 1, 'Norway etc.', '2015/10/1 15:00:00.00', '2015/10/1 15:00:30.05', 'Much wind.');
-- add the special set Random
insert into recording (tokenId, speakerId, sessionId, filename, rec_method)
values
    (1, 1, 1, 'NOTAREALRECORDING', 'eyra');
insert into evaluation_sets (eval_set, recordingId)
values
    ('Random', 1);

commit;