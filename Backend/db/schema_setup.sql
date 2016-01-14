-- schema for recordings_master, a database to keep info about recorded audio.

/* -------------------------------------------------------- *
   WARNING: THIS FILE DELETES ALL DATA IN recordings_master
 * -------------------------------------------------------- */

drop database if exists recordings_master;
create database recordings_master;
use recordings_master; -- set as default (current)

start transaction;

create table token (
    id int not null auto_increment primary key,
    inputToken text not null unique
);
create table device (
    id int not null auto_increment primary key,
    userAgent varchar(255) not null,
    imei varchar(255) not null default '' -- phone hardcoded ID, have to manually make this unique, optional
);
create table instructor (
    id int not null auto_increment primary key,
    name varchar(255) not null,
    email varchar(255) not null,
    phone varchar(50) not null,
    address varchar(255) not null,
    unique (name, email)
);
create table speaker (
    id int not null auto_increment primary key,
    name varchar(255) not null, -- just like a username
    gender varchar(25) not null,
    height varchar(25) not null,
    dob varchar(25) not null, -- date of birth
    deviceImei varchar(255) not null default '' -- optional id of device speaker was made on
);
create table session (
    id int not null auto_increment primary key,
    speakerId int not null,
    instructorId int not null,
    deviceId int not null,
    location varchar(255) not null,
    start varchar(50) not null,
    end varchar(50) not null,
    comments text not null,
    foreign key (speakerId) references speaker(id),
    foreign key (instructorId) references instructor(id),
    foreign key (deviceId) references device(id),
    unique (speakerId, instructorId, deviceId, location, start, end)
);
create table recording (
    id int not null auto_increment primary key,
    tokenId int not null,
    speakerId int not null,
    sessionId int not null,
    rel_path varchar(255) not null unique,
    foreign key (tokenId) references token(id),
    foreign key (speakerId) references speaker(id),
    foreign key (sessionId) references session(id)
);

commit;