-- schema for recordings_master, a database to keep info about recorded audio.

/* -------------------------------------------------------- *
   WARNING: THIS FILE DELETES ALL DATA IN recordings_master
 * -------------------------------------------------------- */

drop database if exists recordings_master;
create database recordings_master;
use recordings_master; -- set as default (current)

start transaction;

create table speaker (
    id int not null auto_increment primary key,
    birthdate varchar(25) not null
);
create table session (
    id int not null auto_increment primary key,
    speakerId int not null,
    time varchar(50) not null,
    foreign key (speakerId) references speaker(id)
);
create table recording (
    id int not null auto_increment primary key,
    sessionId int not null,
    rel_path varchar(255) not null unique,
    foreign key (sessionId) references session(id)
);

-- test inserts
insert into speaker (birthdate)
values
    ('1991/10/10'),
    ('2000/01/01');
insert into session (speakerId, time)
values 
    (1, '2015/10/1 15:00:00.00'),
    (1, '2015/10/1 16:00:00.00'),
    (2, '2015/10/1 10:00:00.00');
insert into recording (sessionId, rel_path)
values 
    (1,'b/a/12345.wav'),
    (1,'b/a/2.wav'),
    (2,'b/a/3.wav'),
    (1,'b/a/4.wav'),
    (3,'b/a/e.wav');
    /*(15,'b/a/f.wav'); --this should throw an error, since there is no session(id)
                        --that is 15 (only 3 session entries, starts count at 1) */

commit;