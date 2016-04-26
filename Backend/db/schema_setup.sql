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
    valid boolean not null default TRUE
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
    s_key varchar(255) not null, -- use key/value system to allow for flexible speaker info, comma seperated
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
    filename varchar(255) not null unique,
    foreign key (speakerId) references speaker(id),
    foreign key (sessionId) references session(id)
);
alter table recording convert to character set utf8 collate utf8_general_ci;

commit;