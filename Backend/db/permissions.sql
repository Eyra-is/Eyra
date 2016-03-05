-- create user 'default'@'localhost';
grant select on recordings_master.device to 'default'@'localhost';
grant select on recordings_master.instructor to 'default'@'localhost';
grant select on recordings_master.session to 'default'@'localhost';
grant select on recordings_master.speaker to 'default'@'localhost';
grant select on recordings_master.speaker_info to 'default'@'localhost';
grant select on recordings_master.token to 'default'@'localhost';
grant select on recordings_master.recording to 'default'@'localhost'

grant insert on recordings_master.device to 'default'@'localhost';
grant insert on recordings_master.instructor to 'default'@'localhost';
grant insert on recordings_master.recording to 'default'@'localhost';
grant insert on recordings_master.session to 'default'@'localhost';
grant insert on recordings_master.speaker to 'default'@'localhost';
grant insert on recordings_master.speaker_info to 'default'@'localhost';

grant update on recordings_master.session to 'default'@'localhost';



