-- basic inserts to start with the "dummy" instructors/devices etc
start transaction;

insert into device (userAgent, imei)
values
    ('Mobile Browser Mozilla etc.', 'NOTAVALIDPHONEID');
insert into instructor (name, email, phone, address)
values
    ('Jane Doe', 'dummy@jk.is', '1-800-DONT-CALL', 'Australia');
insert into speaker (name, s_keys, s_values, deviceImei)
values
    ('John Doe', 'sex,dob,height', 'Male,1991-1995,170', 'NOTAVALIDPHONEID');
insert into session (speakerId, instructorId, deviceId, location, start, end, comments)
values 
    (1, 1, 1, 'Norway etc.', '2015/10/1 15:00:00.00', '2015/10/1 15:00:30.05', 'Much wind.');

commit;
