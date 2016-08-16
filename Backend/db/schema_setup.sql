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

-- schema for recordings_master, a database to keep info about recorded audio.

/* -------------------------------------------------------- *
   WARNING: THIS FILE DELETES ALL DATA IN recordings_master
 * -------------------------------------------------------- */

drop database if exists recordings_master;
create database recordings_master;
use recordings_master; -- set as default (current)

set collation_connection = 'utf8_general_ci';

start transaction;

alter database recordings_master character set utf8 collate utf8_general_ci;

create table token (
    id int not null auto_increment primary key,
    inputToken text not null,
    valid boolean not null default TRUE,
    promptLabel varchar(2) not null default ''
);
alter table token convert to character set utf8 collate utf8_general_ci;

create table device (
    id int not null auto_increment primary key,
    userAgent varchar(255) not null,
    imei varchar(255) not null default '' -- phone hardcoded ID, have to manually make this unique, optional
);
alter table device convert to character set utf8 collate utf8_general_ci;

create table instructor (
    id int not null auto_increment primary key,
    name varchar(255) not null,
    email varchar(255) not null,
    phone varchar(50) not null,
    address varchar(255) not null,
    unique (name, email)
);
alter table instructor convert to character set utf8 collate utf8_general_ci;

create table speaker (
    id int not null auto_increment primary key,
    name varchar(255) not null, -- just like a username
    deviceImei varchar(255) not null default '' -- optional id of device speaker was made on
);
alter table speaker convert to character set utf8 collate utf8_general_ci;

create table speaker_info (
    id int not null auto_increment primary key,
    speakerId int not null,
    s_key varchar(255) not null, -- use key/value system to allow for flexible speaker info
    s_value varchar(255) not null,
    foreign key (speakerId) references speaker(id),
    unique (speakerId, s_key)
);
alter table speaker convert to character set utf8 collate utf8_general_ci;

create table session (
    id int not null auto_increment primary key,
    speakerId int not null,
    instructorId int not null,
    deviceId int not null,
    location varchar(255) not null, -- it's possible location exceeds 255, but truncation shouldn't be catastrophic.
    start varchar(50) not null,
    end varchar(50) not null,
    comments text not null,
    foreign key (speakerId) references speaker(id),
    foreign key (deviceId) references device(id),
    unique (speakerId, instructorId, deviceId, location, start, end)
);
alter table session convert to character set utf8 collate utf8_general_ci;

create table recording (
    id int not null auto_increment primary key,
    tokenId int not null,
    speakerId int not null,
    sessionId int not null,
    filename varchar(255) not null,
    rec_method varchar(10) not null default 'eyra', -- enable labeling if recordings from other corpora are added to eyra format
    foreign key (speakerId) references speaker(id),
    foreign key (sessionId) references session(id)
);
alter table recording convert to character set utf8 collate utf8_general_ci;

create table evaluation_sets (
    id int not null auto_increment primary key,
    eval_set varchar(255) not null,
    recordingId int not null,
    foreign key (recordingId) references recording(id)
);
alter table evaluation_sets convert to character set utf8 collate utf8_general_ci;

create table evaluation (
    id int not null auto_increment primary key,
    recordingId int not null,
    eval_set varchar(255) not null,
    evaluator varchar(255) not null,
    grade int not null,
    comments varchar(255) not null default '',
    skipped boolean not null default FALSE,
    foreign key (recordingId) references recording(id),
    unique(recordingId, eval_set, evaluator)
);
alter table evaluation convert to character set utf8 collate utf8_general_ci;

commit;
