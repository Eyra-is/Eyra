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
    inputToken text not null
);
create table device (
    id int not null auto_increment primary key,
    hardware varchar(255) not null,
    os varchar(50) not null,
    software varchar(255) not null
);
create table instructor (
    id int not null auto_increment primary key,
    name varchar(255) not null,
    address varchar(255) not null,
    phone varchar(50) not null
);
create table speaker (
    id int not null auto_increment primary key,
    height int not null,
    birthdate varchar(25) not null
);
create table session (
    id int not null auto_increment primary key,
    speakerId int not null,
    instructorId int not null,
    deviceId int not null,
    location varchar(255) not null,
    start varchar(50) not null,
    end varchar(50) not null,
    comments text,
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
    duration int not null,
    rel_path varchar(255) not null unique,
    foreign key (tokenId) references token(id),
    foreign key (speakerId) references speaker(id),
    foreign key (sessionId) references session(id)
);

commit;